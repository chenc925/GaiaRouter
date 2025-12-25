#!/usr/bin/env python3
"""
测试模型管理 API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# 使用你的登录凭据
USERNAME = "admin"
PASSWORD = "admin123"


def login():
    """登录获取 token"""
    response = requests.post(
        f"{BASE_URL}/v1/admin/login", json={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 登录成功")
        return data.get("token")
    else:
        print(f"❌ 登录失败: {response.text}")
        return None


def test_sync_models(token):
    """测试同步模型"""
    print("\n测试同步模型...")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(f"{BASE_URL}/v1/admin/models/sync", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 同步成功: {data.get('message')}")
        print(f"   统计: {json.dumps(data.get('stats'), ensure_ascii=False)}")
        return True
    else:
        print(f"❌ 同步失败: {response.text}")
        return False


def test_list_models(token):
    """测试获取模型列表"""
    print("\n测试获取模型列表...")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BASE_URL}/v1/admin/models", headers=headers, params={"page": 1, "limit": 10}
    )

    if response.status_code == 200:
        data = response.json()
        models = data.get("data", [])
        pagination = data.get("pagination", {})
        print(f"✅ 获取成功，共 {pagination.get('total', 0)} 个模型")
        print(f"   前 {len(models)} 个模型:")
        for model in models[:5]:
            enabled = "✓" if model.get("is_enabled") else "✗"
            free = "💰免费" if model.get("is_free") else "💳付费"
            print(f"   [{enabled}] {model.get('name')} ({free})")
        return models
    else:
        print(f"❌ 获取失败: {response.text}")
        return []


def test_enable_model(token, model_id):
    """测试启用模型"""
    print(f"\n测试启用模型: {model_id}")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.patch(
        f"{BASE_URL}/v1/admin/models/{requests.utils.quote(model_id, safe='')}/enable",
        headers=headers,
    )

    if response.status_code == 200:
        print(f"✅ 启用成功")
        return True
    else:
        print(f"❌ 启用失败: {response.text}")
        return False


def test_public_models(api_key):
    """测试公开的模型列表（使用 API Key）"""
    print("\n测试公开模型列表（API Key 认证）...")
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(f"{BASE_URL}/v1/models", headers=headers)

    if response.status_code == 200:
        data = response.json()
        models = data.get("data", [])
        print(f"✅ 获取成功，共 {len(models)} 个启用的模型")
        for model in models[:5]:
            print(f"   - {model.get('id')}")
        return True
    else:
        print(f"❌ 获取失败: {response.text}")
        return False


if __name__ == "__main__":
    print("🚀 开始测试模型管理 API...\n")

    # 1. 登录
    token = login()
    if not token:
        exit(1)

    # 2. 同步模型
    sync_success = test_sync_models(token)

    # 3. 获取模型列表
    models = test_list_models(token)

    # 4. 启用第一个免费模型
    if models:
        free_models = [m for m in models if m.get("is_free") and not m.get("is_enabled")]
        if free_models:
            test_enable_model(token, free_models[0]["id"])
            # 再次获取列表验证
            test_list_models(token)

    print("\n✅ 所有测试完成!")
    print("\n💡 现在可以访问前端页面:")
    print("   - 模型管理: http://localhost:3000/models")
    print("   - 对话测试: http://localhost:3000/chat/test")
