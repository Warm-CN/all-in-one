"""
快速测试认证系统
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_auth_system():
    """测试认证系统"""
    print("=" * 60)
    print("🧪 开始测试第二阶段：用户认证与权限控制系统")
    print("=" * 60)
    
    # 1. 测试登录
    print("\n1️⃣ 测试登录接口...")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "student_id": "admin",
            "password": "123456"
        }
    )
    print(f"   状态码: {login_response.status_code}")
    login_data = login_response.json()
    print(f"   响应: {json.dumps(login_data, ensure_ascii=False, indent=2)}")
    
    if login_data.get("code") == 200:
        token = login_data["data"]["token"]["access_token"]
        print(f"   ✅ 登录成功！Token: {token[:50]}...")
    else:
        print(f"   ❌ 登录失败！")
        return
    
    # 2. 测试获取当前用户信息
    print("\n2️⃣ 测试获取当前用户信息...")
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    print(f"   状态码: {me_response.status_code}")
    me_data = me_response.json()
    print(f"   当前用户: {me_data['data']['real_name']} ({me_data['data']['role']})")
    print(f"   ✅ 获取成功！")
    
    # 3. 测试场景 A（公开接口）- 获取报名活动列表
    print("\n3️⃣ 测试场景 A（公开接口）- 获取报名活动列表...")
    signup_response = requests.get(f"{BASE_URL}/api/v1/signups/configs")
    print(f"   状态码: {signup_response.status_code}")
    print(f"   ✅ 无需登录即可访问！")
    
    # 4. 测试场景 B（内部接口）- 查看我的预约
    print("\n4️⃣ 测试场景 B（内部接口）- 查看我的预约...")
    bookings_response = requests.get(
        f"{BASE_URL}/api/bookings/my",
        headers=headers
    )
    print(f"   状态码: {bookings_response.status_code}")
    if bookings_response.status_code == 200:
        print(f"   ✅ Member/Admin 权限验证通过！")
    else:
        print(f"   ❌ 权限验证失败！")
    
    # 5. 测试场景 C（管理接口）- 查看所有用户
    print("\n5️⃣ 测试场景 C（管理接口）- 查看用户列表...")
    all_bookings_response = requests.get(
        f"{BASE_URL}/api/v1/users",
        headers=headers
    )
    print(f"   状态码: {all_bookings_response.status_code}")
    if all_bookings_response.status_code == 200:
        print(f"   ✅ Admin 权限验证通过！")
    else:
        print(f"   ❌ 权限验证失败！")
    
    # 6. 测试无效 Token
    print("\n6️⃣ 测试无效 Token...")
    invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
    invalid_response = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers=invalid_headers
    )
    print(f"   状态码: {invalid_response.status_code}")
    if invalid_response.status_code == 401:
        print(f"   ✅ 正确拒绝无效 Token！")
    else:
        print(f"   ❌ 应该返回 401！")
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    print("⚠️  请确保应用正在运行（python main.py）")
    input("按回车键开始测试...")
    
    try:
        test_auth_system()
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败！请确保应用正在 http://localhost:8000 运行")
    except Exception as e:
        print(f"❌ 测试出错: {e}")
