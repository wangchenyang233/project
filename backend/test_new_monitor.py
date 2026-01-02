import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_new_monitor():
    """测试新的监控任务"""
    
    # 1. 登录
    print("=== 登录 ===")
    login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin123!"
    })
    print(f"状态码: {login_response.status_code}")
    print(f"响应: {json.dumps(login_response.json(), indent=2, ensure_ascii=False)}")
    
    if login_response.status_code != 200:
        print("登录失败")
        return
    
    token = login_response.json()['data']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 启动监控
    print("\n=== 启动监控 ===")
    start_response = requests.post(f"{BASE_URL}/api/v1/monitor/start", 
                                   json={"user": "0x204f72f35326db932158cba6adff0b9a1da95e14", "poll_seconds": 10},
                                   headers=headers)
    print(f"状态码: {start_response.status_code}")
    print(f"响应: {json.dumps(start_response.json(), indent=2, ensure_ascii=False)}")
    
    if start_response.status_code == 200:
        task_id = start_response.json()['data']['task_id']
        print(f"成功启动监控，task_id: {task_id}")
        
        # 等待一段时间让监控任务运行
        print("\n等待30秒让监控任务运行...")
        time.sleep(30)
        
        # 3. 获取监控日志
        print(f"\n=== 获取监控日志 (task_id: {task_id}) ===")
        logs_response = requests.get(f"{BASE_URL}/api/v1/monitor/logs", 
                                    params={"task_id": task_id},
                                    headers=headers)
        print(f"状态码: {logs_response.status_code}")
        print(f"响应: {json.dumps(logs_response.json(), indent=2, ensure_ascii=False)}")
        
        # 4. 停止监控
        print(f"\n=== 停止监控 ===")
        stop_response = requests.post(f"{BASE_URL}/api/v1/monitor/stop",
                                     json={"task_id": task_id},
                                     headers=headers)
        print(f"状态码: {stop_response.status_code}")
        print(f"响应: {json.dumps(stop_response.json(), indent=2, ensure_ascii=False)}")
    else:
        print("启动监控失败")

if __name__ == "__main__":
    test_new_monitor()
