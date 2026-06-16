"""
会议室预约接口测试脚本
测试简化版会议室预约系统的核心功能
"""
import requests
from datetime import date, timedelta

# 配置
BASE_URL = "http://localhost:8001"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
BOOKING_URL = f"{BASE_URL}/api/bookings"

# 测试用户凭证（请根据实际情况修改）
TEST_USER = {
    "student_id": "110",
    "password": "654321"
}


def get_auth_token():
    """获取认证 Token"""
    response = requests.post(LOGIN_URL, json=TEST_USER)
    if response.status_code == 200:
        data = response.json()
        return data["data"]["token"]["access_token"]
    else:
        print(f"登录失败: {response.json()}")
        return None


def test_create_booking(token):
    """测试创建预约"""
    print("\n=== 测试创建预约 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    tomorrow = date.today() + timedelta(days=1)
    
    booking_data = {
        "booking_date": tomorrow.isoformat(),
        "start_time": "14:00",
        "end_time": "16:00",
        "num_people": 10,
        "remarks": "技术分享会"
    }
    
    response = requests.post(BOOKING_URL, json=booking_data, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    return response.json()


def test_get_bookings(token, booking_date):
    """测试获取预约列表"""
    print("\n=== 测试获取预约列表 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"date": booking_date}
    
    response = requests.get(BOOKING_URL, params=params, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    return response.json()


def test_time_conflict(token):
    """测试时间冲突检测"""
    print("\n=== 测试时间冲突检测 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    tomorrow = date.today() + timedelta(days=1)
    
    # 尝试创建一个与已有预约重叠的预约
    booking_data = {
        "booking_date": tomorrow.isoformat(),
        "start_time": "15:00",  # 与 14:00-16:00 重叠
        "end_time": "17:00",
        "num_people": 5,
        "remarks": "这个应该失败"
    }
    
    response = requests.post(BOOKING_URL, json=booking_data, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_get_my_bookings(token):
    """测试获取我的预约"""
    print("\n=== 测试获取我的预约 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BOOKING_URL}/my", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    return response.json()


def test_delete_booking(token, booking_id):
    """测试删除预约"""
    print("\n=== 测试删除预约 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(f"{BOOKING_URL}/{booking_id}", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def main():
    """主测试流程"""
    print("开始测试会议室预约接口...")
    
    # 1. 获取 Token
    token = get_auth_token()
    if not token:
        print("无法获取 Token，测试终止")
        return
    
    print(f"✅ 成功获取 Token: {token[:20]}...")
    
    # 2. 创建预约
    create_result = test_create_booking(token)
    if create_result.get("code") == 200:
        booking_id = create_result["data"]["id"]
        booking_date = create_result["data"]["booking_date"]
        print(f"✅ 预约创建成功，ID: {booking_id}")
    else:
        print("❌ 预约创建失败")
        return
    
    # 3. 获取预约列表
    test_get_bookings(token, booking_date)
    
    # 4. 测试时间冲突
    test_time_conflict(token)
    
    # 5. 获取我的预约
    test_get_my_bookings(token)
    
    # 6. 删除预约
    test_delete_booking(token, booking_id)
    
    # 7. 验证删除
    test_get_bookings(token, booking_date)
    
    print("\n✅ 所有测试完成！")


if __name__ == "__main__":
    main()
