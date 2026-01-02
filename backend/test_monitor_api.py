import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

def test_login():
    """测试登录"""
    print("=== 测试登录 ===")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "Admin123!"
    })
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        return response.json().get('data', {}).get('access_token')
    return None

def test_monitor_start(token):
    """测试启动监控"""
    print("\n=== 测试启动监控 ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/monitor/start", 
                           json={
                               "user": "0x7D58050D03c7B3B8812b16f2CE47774a25f77E0f",
                               "poll_seconds": 10
                           },
                           headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        return response.json().get('data', {}).get('task_id')
    return None

def test_monitor_logs(token, task_id):
    """测试获取监控日志"""
    print(f"\n=== 测试获取监控日志 (task_id: {task_id}) ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/monitor/logs", 
                          params={"task_id": task_id},
                          headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_activity_query(token):
    """测试活动查询"""
    print("\n=== 测试活动查询 ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/activity/query", 
                          params={
                              "user": "0x7D58050D03c7B3B8812b16f2CE47774a25f77E0f",
                              "limit": 20
                          },
                          headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    # 测试登录
    token = test_login()
    
    if token:
        print(f"\n成功获取token: {token[:50]}...")
        
        # 测试活动查询
        test_activity_query(token)
        
        # 测试启动监控
        task_id = test_monitor_start(token)
        
        if task_id:
            print(f"\n成功启动监控，task_id: {task_id}")
            
            # 等待几秒后获取日志
            import time
            time.sleep(3)
            
            # 测试获取监控日志
            test_monitor_logs(token, task_id)
        else:
            print("\n启动监控失败")
    else:
        print("\n登录失败")
