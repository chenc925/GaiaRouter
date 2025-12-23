# GaiaRouter 模块设计

## 模块划分

系统按功能划分为以下模块：

```
openrouter/
├── api/              # API 层
│   ├── controllers/  # 控制器
│   ├── middleware/   # 中间件
│   └── schemas/      # 数据模型
├── router/           # 路由层
│   ├── model_router.py
│   └── registry.py
├── adapters/         # 适配器层
│   ├── base.py       # 基础适配器接口
│   ├── openai.py     # OpenAI 适配器
│   ├── anthropic.py  # Anthropic 适配器
│   ├── google.py     # Google 适配器
│   └── openrouter.py # OpenRouter 适配器
├── providers/        # 提供商层
│   ├── base.py       # 基础提供商接口
│   ├── openai.py     # OpenAI 提供商
│   ├── anthropic.py  # Anthropic 提供商
│   ├── google.py     # Google 提供商
│   └── openrouter.py # OpenRouter 提供商
├── auth/             # 认证和授权模块
│   ├── api_key_manager.py  # API Key 管理器
│   ├── key_storage.py      # API Key 存储
│   └── permission.py        # 权限管理
├── organizations/    # 组织管理模块
│   ├── manager.py          # 组织管理器
│   ├── storage.py          # 组织存储
│   └── limits.py           # 使用限制管理
├── stats/            # 统计模块
│   ├── collector.py        # 统计收集器
│   ├── storage.py          # 统计存储
│   └── query.py            # 统计查询
├── database/         # 数据库模块
│   ├── models.py           # SQLAlchemy 模型
│   ├── connection.py        # 数据库连接（阿里云 RDS）
│   └── migrations/         # Alembic 迁移文件
├── config/           # 配置管理
│   ├── settings.py
│   └── models.yaml
├── utils/            # 工具函数
│   ├── logger.py
│   └── errors.py
└── main.py           # 应用入口
```

## 模块详细设计

### 1. API 模块（api/）

#### 1.1 Controllers

**chat_controller.py**

```python
class ChatController:
    def create_completion(request: ChatRequest) -> ChatResponse
    - 验证请求参数
    - 调用路由层
    - 处理响应
    - 错误处理
```

**models_controller.py**

```python
class ModelsController:
    def list_models() -> ModelsResponse
    - 获取模型列表
    - 格式化响应
```

**api_key_controller.py**

```python
class APIKeyController:
    def create_key(request: CreateKeyRequest) -> APIKeyResponse
    def list_keys(params: QueryParams) -> APIKeysResponse
    def get_key(key_id: str) -> APIKeyResponse
    def update_key(key_id: str, request: UpdateKeyRequest) -> APIKeyResponse
    def delete_key(key_id: str) -> DeleteResponse
    - 创建 API Key
    - 查询 API Key 列表
    - 获取单个 API Key
    - 更新 API Key
    - 删除 API Key
```

**stats_controller.py**

```python
class StatsController:
    def get_key_stats(key_id: str, params: StatsParams) -> StatsResponse
    def get_global_stats(params: StatsParams) -> GlobalStatsResponse
    def get_org_stats(org_id: str, params: StatsParams) -> StatsResponse
    - 获取 API Key 统计
    - 获取全局统计
    - 获取组织统计
```

**organization_controller.py**

```python
class OrganizationController:
    def create_org(request: CreateOrgRequest) -> OrganizationResponse
    def list_orgs(params: QueryParams) -> OrganizationsResponse
    def get_org(org_id: str) -> OrganizationResponse
    def update_org(org_id: str, request: UpdateOrgRequest) -> OrganizationResponse
    def delete_org(org_id: str) -> DeleteResponse
    def assign_api_key(org_id: str, request: CreateKeyRequest) -> APIKeyResponse
    def get_org_stats(org_id: str, params: StatsParams) -> StatsResponse
    - 创建组织
    - 查询组织列表
    - 获取单个组织
    - 更新组织
    - 删除组织
    - 为组织分配 API Key
    - 获取组织统计
```

**stream_handler.py**

```python
class StreamHandler:
    async def stream_chat_completion(request: ChatRequest) -> AsyncIterator[str]
    - 处理流式聊天完成请求
    - 使用 Server-Sent Events (SSE) 格式
    - 异步生成响应流
```

#### 1.2 Middleware

**auth_middleware.py**

```python
def verify_api_key(request) -> bool
- 验证 API Key
- 设置请求上下文
```

**error_middleware.py**

```python
def error_handler(exception) -> ErrorResponse
- 捕获异常
- 转换为统一错误格式
```

**logging_middleware.py**

```python
def log_request(request, response)
- 记录请求日志
- 记录响应日志
```

#### 1.3 Schemas

**request_schemas.py**

```python
class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float]
    max_tokens: Optional[int]
    ...
```

**response_schemas.py**

```python
class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
```

### 2. Router 模块（router/）

#### 2.1 Model Router

**model_router.py**

```python
class ModelRouter:
    def route(model_id: str) -> Provider
    - 解析模型标识符
    - 查找对应的提供商
    - 返回提供商实例

    def parse_model_id(model_id: str) -> Tuple[str, str]
    - 解析 provider 和 model_name
    - 验证格式
```

#### 2.2 Registry

**registry.py**

```python
class ModelRegistry:
    def register(provider: str, model: str, config: dict)
    - 注册模型配置

    def get_provider(model_id: str) -> Provider
    - 获取模型对应的提供商

    def list_models() -> List[ModelInfo]
    - 列出所有可用模型
```

### 3. Adapters 模块（adapters/）

#### 3.1 Base Adapter

**base.py**

```python
class RequestAdapter(ABC):
    @abstractmethod
    def adapt_request(request: ChatRequest) -> dict

class ResponseAdapter(ABC):
    @abstractmethod
    def adapt_response(response: dict) -> ChatResponse
```

#### 3.2 Provider Adapters

**openai.py**

```python
class OpenAIRequestAdapter(RequestAdapter):
    def adapt_request(request: ChatRequest) -> dict
    - 转换为 OpenAI API 格式

class OpenAIResponseAdapter(ResponseAdapter):
    def adapt_response(response: dict) -> ChatResponse
    - 转换为统一格式
```

**anthropic.py**、**google.py**、**openrouter.py** 类似实现

### 4. Providers 模块（providers/）

#### 4.1 Base Provider

**base.py**

```python
class Provider(ABC):
    @abstractmethod
    async def chat_completion(request: dict) -> dict
    - 调用外部 API
    - 处理错误
    - 重试机制
```

#### 4.2 Provider Implementations

**openai.py**

```python
class OpenAIProvider(Provider):
    def __init__(api_key: str, base_url: str)
    async def chat_completion(request: dict) -> dict
    - 调用 OpenAI API
    - 处理响应
    - 错误处理
```

**anthropic.py**、**google.py** 类似实现

### 5. Config 模块（config/）

#### 5.1 Settings

**settings.py**

```python
class Settings:
    api_keys: Dict[str, str]
    providers: Dict[str, ProviderConfig]
    timeout: int
    max_retries: int

    @classmethod
    def from_env(cls) -> Settings
    @classmethod
    def from_file(cls, path: str) -> Settings
```

#### 5.2 Models Config

**models.yaml**

```yaml
models:
  - id: openai/gpt-4
    provider: openai
    name: gpt-4
    config:
      api_key_env: OPENAI_API_KEY
  - id: anthropic/claude-3-opus
    provider: anthropic
    name: claude-3-opus
    config:
      api_key_env: ANTHROPIC_API_KEY
```

### 6. Utils 模块（utils/）

#### 6.1 Logger

**logger.py**

```python
def setup_logger(level: str) -> Logger
def log_request(model: str, status: str, duration: float)
def log_error(error: Exception, context: dict)
```

#### 6.2 Errors

**errors.py**

```python
class OpenRouterError(Exception):
    pass

class ModelNotFoundError(OpenRouterError):
    pass

class AuthenticationError(OpenRouterError):
    pass

class TimeoutError(OpenRouterError):
    pass
```

### 7. Auth 模块（auth/）

#### 7.1 API Key Manager

**api_key_manager.py**

```python
class APIKeyManager:
    def create_key(
        name: str,
        description: str = None,
        permissions: List[str] = None,
        expires_at: datetime = None
    ) -> APIKey
    - 生成唯一 API Key
    - 加密存储
    - 保存到数据库

    def get_key(key_id: str) -> APIKey
    - 从数据库查询 API Key

    def list_keys(
        page: int = 1,
        limit: int = 20,
        status: str = None,
        search: str = None
    ) -> List[APIKey]
    - 查询 API Key 列表
    - 支持分页和筛选

    def update_key(
        key_id: str,
        name: str = None,
        description: str = None,
        permissions: List[str] = None,
        status: str = None,
        expires_at: datetime = None
    ) -> APIKey
    - 更新 API Key 信息

    def delete_key(key_id: str) -> bool
    - 删除 API Key（软删除）

    def verify_key(api_key: str) -> APIKey
    - 验证 API Key 有效性
    - 检查状态和过期时间
    - 返回 API Key 信息
```

#### 7.2 Key Storage

**key_storage.py**

```python
class KeyStorage:
    def save(key: APIKey) -> bool
    - 保存 API Key 到数据库
    - 加密存储密钥

    def get(key_id: str) -> APIKey
    - 从数据库获取 API Key

    def get_by_key(api_key: str) -> APIKey
    - 通过 API Key 值查询

    def list(filters: dict) -> List[APIKey]
    - 查询 API Key 列表

    def update(key_id: str, updates: dict) -> bool
    - 更新 API Key

    def delete(key_id: str) -> bool
    - 删除 API Key
```

#### 7.3 Permission

**permission.py**

```python
class Permission:
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

    @staticmethod
    def check(api_key: APIKey, required_permission: str) -> bool
    - 检查 API Key 权限
    - 验证是否有足够权限执行操作
```

### 8. Stats 模块（stats/）

#### 8.1 Collector

**collector.py**

```python
class StatsCollector:
    def record_request(
        key_id: str,
        model: str,
        provider: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float = None
    )
    - 记录请求统计
    - 异步写入数据库
    - 聚合统计数据
```

#### 8.2 Storage

**storage.py**

```python
class StatsStorage:
    def save(stat: RequestStat) -> bool
    - 保存统计数据

    def get_key_stats(
        key_id: str,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "day"
    ) -> Dict
    - 查询 API Key 统计

    def get_global_stats(
        start_date: datetime,
        end_date: datetime,
        group_by: str = "day"
    ) -> Dict
    - 查询全局统计

    def aggregate_by_date(stats: List[RequestStat]) -> Dict
    - 按日期聚合

    def aggregate_by_model(stats: List[RequestStat]) -> Dict
    - 按模型聚合

    def aggregate_by_provider(stats: List[RequestStat]) -> Dict
    - 按提供商聚合
```

#### 8.3 Query

**query.py**

```python
class StatsQuery:
    def query_key_stats(
        key_id: str,
        params: StatsQueryParams
    ) -> StatsResponse
    - 构建查询
    - 执行统计查询
    - 格式化响应

    def query_global_stats(
        params: StatsQueryParams
    ) -> GlobalStatsResponse
    - 构建全局统计查询
    - 执行查询
    - 格式化响应
```

## 前端模块设计

### 前端项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口封装
│   │   ├── organizations.ts
│   │   ├── apiKeys.ts
│   │   ├── stats.ts
│   │   └── index.ts
│   ├── components/       # 公共组件
│   │   ├── Layout/
│   │   ├── Table/
│   │   ├── Form/
│   │   └── Chart/
│   ├── views/           # 页面组件
│   │   ├── Dashboard/
│   │   ├── Organizations/
│   │   ├── ApiKeys/
│   │   └── Stats/
│   ├── stores/          # Pinia 状态管理
│   │   ├── auth.ts
│   │   ├── organizations.ts
│   │   ├── apiKeys.ts
│   │   └── stats.ts
│   ├── router/          # 路由配置
│   │   └── index.ts
│   ├── utils/           # 工具函数
│   │   ├── request.ts   # Axios 封装
│   │   ├── format.ts    # 格式化工具
│   │   └── validate.ts  # 验证工具
│   ├── App.vue
│   └── main.ts
├── public/
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### 核心模块说明

#### 1. API 接口封装（api/）

**organizations.ts**

```typescript
// 组织管理 API
export const getOrganizations = (params) => Promise;
export const getOrganization = (id) => Promise;
export const createOrganization = (data) => Promise;
export const updateOrganization = (id, data) => Promise;
export const deleteOrganization = (id) => Promise;
export const getOrganizationStats = (id, params) => Promise;
```

**apiKeys.ts**

```typescript
// API Key 管理 API
export const getApiKeys = (params) => Promise;
export const getApiKey = (id) => Promise;
export const createApiKey = (data) => Promise;
export const updateApiKey = (id, data) => Promise;
export const deleteApiKey = (id) => Promise;
export const getApiKeyStats = (id, params) => Promise;
```

**stats.ts**

```typescript
// 统计 API
export const getGlobalStats = (params) => Promise;
export const getOrganizationStats = (id, params) => Promise;
export const getApiKeyStats = (id, params) => Promise;
```

#### 2. 状态管理（stores/）

**organizations.ts**

```typescript
export const useOrganizationStore = defineStore('organizations', {
  state: () => ({
    organizations: [],
    currentOrganization: null,
    loading: false
  }),
  actions: {
    fetchOrganizations(),
    fetchOrganization(id),
    createOrganization(data),
    updateOrganization(id, data),
    deleteOrganization(id)
  }
})
```

**apiKeys.ts**

```typescript
export const useApiKeyStore = defineStore('apiKeys', {
  state: () => ({
    apiKeys: [],
    currentApiKey: null,
    loading: false
  }),
  actions: {
    fetchApiKeys(params),
    fetchApiKey(id),
    createApiKey(data),
    updateApiKey(id, data),
    deleteApiKey(id)
  }
})
```

**stats.ts**

```typescript
export const useStatsStore = defineStore('stats', {
  state: () => ({
    globalStats: null,
    organizationStats: {},
    apiKeyStats: {},
    loading: false
  }),
  actions: {
    fetchGlobalStats(params),
    fetchOrganizationStats(id, params),
    fetchApiKeyStats(id, params)
  }
})
```

#### 3. 页面组件（views/）

**Organizations/**

- `List.vue` - 组织列表
- `Detail.vue` - 组织详情
- `Form.vue` - 组织表单（创建/编辑）

**ApiKeys/**

- `List.vue` - API Key 列表
- `Detail.vue` - API Key 详情
- `Form.vue` - API Key 表单（创建/编辑）

**Stats/**

- `Dashboard.vue` - 统计概览
- `OrganizationStats.vue` - 组织统计
- `ApiKeyStats.vue` - API Key 统计

#### 4. 公共组件（components/）

**Layout/**

- `MainLayout.vue` - 主布局（顶部导航 + 侧边栏 + 内容区）
- `Header.vue` - 顶部导航栏
- `Sidebar.vue` - 侧边栏菜单

**Chart/**

- `LineChart.vue` - 折线图（时间趋势）
- `BarChart.vue` - 柱状图（分布统计）
- `PieChart.vue` - 饼图（占比统计）

## 模块间依赖关系

```
api/controllers → router/ → adapters/ → providers/
api/controllers → auth/api_key_manager
api/controllers → stats/collector
api/controllers → utils/logger
api/controllers → utils/errors
api/middleware → auth/api_key_manager
router/ → config/
providers/ → config/
stats/collector → stats/storage

前端模块：
views/ → stores/ → api/ → 后端 API
components/ → views/
utils/ → 所有模块
```

## 接口设计

### Provider 接口

```python
class Provider(ABC):
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[dict],
        **kwargs
    ) -> dict:
        pass
```

### Adapter 接口

```python
class RequestAdapter(ABC):
    @abstractmethod
    def adapt(self, request: ChatRequest) -> dict:
        pass

class ResponseAdapter(ABC):
    @abstractmethod
    def adapt(self, response: dict) -> ChatResponse:
        pass
```

### API Key 接口

```python
class APIKey(BaseModel):
    id: str
    name: str
    description: Optional[str]
    key: str  # 只在创建时返回
    permissions: List[str]
    status: str  # active, inactive, expired
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
```

### Stats 接口

```python
class RequestStat(BaseModel):
    key_id: str
    organization_id: Optional[str]
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: Optional[float]
    timestamp: datetime
```

### Organization 接口

```python
class Organization(BaseModel):
    id: str
    name: str
    description: Optional[str]
    admin_user_id: Optional[str]
    status: str  # active, inactive
    limits: OrganizationLimits
    created_at: datetime
    updated_at: datetime

class OrganizationLimits(BaseModel):
    monthly_requests: Optional[int]
    monthly_tokens: Optional[int]
    monthly_cost: Optional[float]
```

### 数据库模型

```python
# SQLAlchemy 模型（示例）
class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    admin_user_id = Column(String)
    status = Column(String, default='active')
    monthly_requests_limit = Column(Integer)
    monthly_tokens_limit = Column(Integer)
    monthly_cost_limit = Column(Numeric)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class APIKey(Base):
    __tablename__ = 'api_keys'

    id = Column(String, primary_key=True)
    organization_id = Column(String, ForeignKey('organizations.id'))
    name = Column(String)
    key_hash = Column(String)  # 加密存储
    permissions = Column(JSON)
    status = Column(String)
    expires_at = Column(DateTime)
    created_at = Column(DateTime)
```

## 数据模型

### ChatRequest

- model: str
- messages: List[Message]
- temperature: Optional[float]
- max_tokens: Optional[int]

### ChatResponse

- id: str
- object: str
- created: int
- model: str
- choices: List[Choice]
- usage: Usage

### Message

- role: str (system/user/assistant)
- content: str

### Choice

- index: int
- message: Message
- finish_reason: str

### Usage

- prompt_tokens: int
- completion_tokens: int
- total_tokens: int
