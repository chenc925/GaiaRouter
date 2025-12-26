"""
聊天完成控制器

处理聊天完成请求（普通模式和流式模式）
"""

import json
import time
from typing import AsyncIterator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from starlette.responses import Response

from ...database.connection import get_db
from ...database.models import Organization
from ...models.manager import get_model_manager
from ...organizations.limits import get_limit_checker
from ...router import get_model_router
from ...stats.collector import get_stats_collector
from ...utils.errors import ModelNotFoundError
from ...utils.logger import get_logger
from ..middleware.auth import verify_api_key
from ..schemas.request import ChatRequest
from ..schemas.response import ChatResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat/completions")
async def create_completion(request: ChatRequest, api_key=Depends(verify_api_key)) -> Response:
    """
    创建聊天完成请求

    支持普通模式和流式模式

    Args:
      request: 聊天请求
      api_key: API Key（通过中间件验证）

    Returns:
      聊天响应（普通模式）或流式响应（流式模式）
    """
    start_time = time.time()

    try:
        # 验证模型是否启用
        model_manager = get_model_manager()
        db_model = model_manager.get_model(request.model)

        if not db_model:
            raise ModelNotFoundError(f"Model not found: {request.model}")

        if not db_model.is_enabled:
            raise ModelNotFoundError(f"Model is not enabled: {request.model}")

        # 检查组织使用限制
        if api_key.organization_id:
            db = next(get_db())
            try:
                org = (
                    db.query(Organization)
                    .filter(Organization.id == api_key.organization_id)
                    .first()
                )
                if org:
                    limit_checker = get_limit_checker()
                    # 预检查（使用估算值）
                    limit_checker.check_limits(org, additional_requests=1, additional_tokens=100)
            finally:
                db.close()

        # 路由到对应的提供商
        model_router = get_model_router()
        route_result = model_router.route(request.model)
        provider = route_result[0]
        request_adapter = route_result[1]
        response_adapter = route_result[2]
        model_name = route_result[3]

        # 提取提供商名称
        provider_name = request.model.split("/")[0] if "/" in request.model else "unknown"

        # 转换请求格式
        request_dict = request.dict(exclude_none=True)
        adapted_request = request_adapter.adapt(request_dict)

        # 如果是流式模式
        if request.stream:
            return StreamingResponse(
                _stream_chat_completion(
                    provider, response_adapter, adapted_request, model_name, request.model
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )

        # 普通模式
        provider_response = await provider.chat_completion(
            messages=adapted_request["messages"],
            model=model_name,
            temperature=adapted_request.get("temperature"),
            max_tokens=adapted_request.get("max_tokens"),
            top_p=adapted_request.get("top_p"),
            frequency_penalty=adapted_request.get("frequency_penalty"),
            presence_penalty=adapted_request.get("presence_penalty"),
            stream=False,
        )

        # 转换响应格式
        response_data = response_adapter.adapt(provider_response)

        # 确保响应ID和时间戳存在
        if "id" not in response_data or not response_data["id"]:
            response_data["id"] = f"chatcmpl-{int(time.time())}"
        if "created" not in response_data or not response_data["created"]:
            response_data["created"] = int(time.time())

        process_time = time.time() - start_time

        # 记录统计数据
        try:
            stats_collector = get_stats_collector()
            # 计算费用（如果有的话，这里简化处理）
            cost = None  # TODO: 根据模型和token数计算费用

            stats_collector.record_request_sync(
                api_key_id=api_key.id,
                organization_id=api_key.organization_id,
                model=request.model,
                provider=provider_name,
                prompt_tokens=provider_response.prompt_tokens,
                completion_tokens=provider_response.completion_tokens,
                total_tokens=provider_response.total_tokens,
                cost=cost,
            )
        except Exception as e:
            logger.warning(f"Failed to record stats: {e}", exc_info=e)

        logger.info(
            "Chat completion completed",
            model=request.model,
            process_time=f"{process_time:.3f}s",
            tokens=provider_response.total_tokens,
        )

        return ChatResponse(**response_data)

    except ModelNotFoundError as e:
        logger.error(f"Model not found: {request.model}")
        raise
    except Exception as e:
        logger.exception("Chat completion error", exc_info=e)
        raise


async def _stream_chat_completion(
    provider, response_adapter, adapted_request: dict, model_name: str, model_id: str
) -> AsyncIterator[str]:
    """
    流式聊天完成处理

    Args:
      provider: 提供商实例
      response_adapter: 响应适配器
      adapted_request: 适配后的请求
      model_name: 模型名称
      model_id: 完整模型ID

    Yields:
      SSE格式的响应块
    """
    import time

    stream_id = f"chatcmpl-{int(time.time())}"
    created_time = int(time.time())

    try:
        async for chunk in provider.stream_chat_completion(
            messages=adapted_request["messages"],
            model=model_name,
            temperature=adapted_request.get("temperature"),
            max_tokens=adapted_request.get("max_tokens"),
            top_p=adapted_request.get("top_p"),
            frequency_penalty=adapted_request.get("frequency_penalty"),
            presence_penalty=adapted_request.get("presence_penalty"),
        ):
            # 转换响应块格式
            adapted_chunk = response_adapter.adapt_stream_chunk(chunk)

            # 确保必需的字段存在
            if "id" not in adapted_chunk:
                adapted_chunk["id"] = stream_id
            if "object" not in adapted_chunk:
                adapted_chunk["object"] = "chat.completion.chunk"
            if "created" not in adapted_chunk:
                adapted_chunk["created"] = created_time
            if "model" not in adapted_chunk:
                adapted_chunk["model"] = model_id

            # 格式化为SSE格式
            chunk_json = json.dumps(adapted_chunk, ensure_ascii=False)
            yield f"data: {chunk_json}\n\n"

        # 发送结束标记
        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.exception("Stream chat completion error", exc_info=e)
        # 发送错误信息（SSE格式）
        error_chunk = {
            "id": stream_id,
            "object": "chat.completion.chunk",
            "created": created_time,
            "model": model_id,
            "error": {"message": str(e), "type": "stream_error"},
        }
        yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
