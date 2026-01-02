import requests
import json

# 配置
BASE_URL = "http://localhost:5000"

# 登录信息
login_data = {
    "username": "admin",
    "password": "Admin123!"
}

# 测试数据
test_config = {
    "target_user": "0x7D58050D03c7B3B8812b16f2CE47774a25f77E0f",
    "wallet_address": "0x594739Cb523211BF5c013f60557fa39E37686903",
    "private_key": "test_private_key"
}

def test_copy_trade():
    print("=== 登录 ===")
    # 登录获取token
    login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    print(f"状态码: {login_response.status_code}")
    print(f"响应: {json.dumps(login_response.json(), indent=2, ensure_ascii=False)}")
    
    if login_response.status_code != 200:
        print("登录失败，测试结束")
        return
    
    # 提取token
    access_token = login_response.json().get("data", {}).get("access_token")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print("\n=== 保存跟单配置 ===")
    # 保存配置
    config_response = requests.post(f"{BASE_URL}/api/v1/copy-trade/config", json=test_config, headers=headers)
    print(f"状态码: {config_response.status_code}")
    print(f"响应: {json.dumps(config_response.json(), indent=2, ensure_ascii=False)}")
    
    if config_response.status_code != 200:
        print("保存配置失败，测试结束")
        return
    
    print("\n=== 启动跟单 ===")
    # 启动跟单
    start_response = requests.post(f"{BASE_URL}/api/v1/copy-trade/start", json={}, headers=headers)
    print(f"状态码: {start_response.status_code}")
    print(f"响应: {json.dumps(start_response.json(), indent=2, ensure_ascii=False)}")
    
    if start_response.status_code == 200:
        task_id = start_response.json().get("data", {}).get("task_id")
        print(f"成功启动跟单，task_id: {task_id}")
    
    print("\n=== 获取跟单统计 ===")
    # 获取统计信息
    stat_response = requests.get(f"{BASE_URL}/api/v1/copy-trade/stat", headers=headers)
    print(f"状态码: {stat_response.status_code}")
    print(f"响应: {json.dumps(stat_response.json(), indent=2, ensure_ascii=False)}")
    
    print("\n=== 获取跟单据 ===")
    # 获取跟单据
    records_response = requests.get(f"{BASE_URL}/api/v1/copy-trade/records?limit=10", headers=headers)
    print(f"状态码: {records_response.status_code}")
    print(f"响应: {json.dumps(records_response.json(), indent=2, ensure_ascii=False)}")
    
    print("\n=== 停止跟单 ===")
    # 停止跟单
    stop_response = requests.post(f"{BASE_URL}/api/v1/copy-trade/stop", json={}, headers=headers)
    print(f"状态码: {stop_response.status_code}")
    print(f"响应: {json.dumps(stop_response.json(), indent=2, ensure_ascii=False)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_copy_trade()