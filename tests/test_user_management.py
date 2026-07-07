"""
成员管理系统功能测试
测试入社审批、成员维护的完整流程
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def print_response(title, response):
    """打印响应"""
    print(f"\n{'='*60}")
    print(f"【{title}】")
    print(f"状态码: {response.status_code}")
    if response.status_code < 500:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print('='*60)


def test_user_management():
    """测试成员管理功能"""
    
    # 1. 管理员登录
    print("\n>>> 管理员登录")
    login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "student_id": "110",
        "password": "654321"
    })
    print_response("管理员登录", login_res)
    
    if login_res.status_code != 200:
        print("❌ 登录失败")
        return
    
    admin_token = login_res.json()["data"]["token"]["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 2. 注册测试用户
    print("\n>>> 注册测试用户")
    for i in range(3):
        register_res = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
            "full_name": f"测试用户{i+1}",
            "student_id": f"test{i+1:03d}",
            "password": "123456",
            "phone": f"1380013800{i}",
            "email": f"test{i+1}@example.com",
            "department": ["技术部", "运营部", "市场部"][i]
        })
        if i == 0:
            print_response(f"注册用户{i+1}", register_res)
    
    # 3. 获取待审核用户
    print("\n>>> 获取待审核用户列表")
    pending_res = requests.get(f"{BASE_URL}/api/admin/users/pending", headers=headers)
    print_response("待审核用户列表", pending_res)
    
    pending_users = pending_res.json()["data"]
    if len(pending_users) < 2:
        print("⚠️ 待审核用户不足")
        return
    
    # 4. 批量通过审核
    print("\n>>> 批量通过前2个用户")
    user_ids = [pending_users[0]["id"], pending_users[1]["id"]]
    batch_res = requests.post(
        f"{BASE_URL}/api/admin/users/approve",
        headers=headers,
        json=user_ids
    )
    print_response("批量审核", batch_res)
    
    # 5. 单个拒绝
    print("\n>>> 拒绝第3个用户")
    if len(pending_users) > 2:
        reject_res = requests.post(
            f"{BASE_URL}/api/admin/users/reject/{pending_users[2]['id']}",
            headers=headers
        )
        print_response("拒绝用户", reject_res)
    
    # 6. 获取成员列表（带搜索）
    print("\n>>> 获取成员列表（搜索'测试'）")
    members_res = requests.get(
        f"{BASE_URL}/api/admin/users",
        headers=headers,
        params={"status": "active", "keyword": "测试"}
    )
    print_response("成员列表", members_res)
    
    members = members_res.json()["data"]
    if not members:
        print("⚠️ 没有激活的成员")
        return
    
    test_user = members[0]
    
    # 7. 重置密码
    print(f"\n>>> 重置用户 {test_user['full_name']} 的密码")
    reset_res = requests.post(
        f"{BASE_URL}/api/admin/users/reset-password",
        headers=headers,
        params={"user_id": test_user["id"]}
    )
    print_response("重置密码", reset_res)
    
    # 8. 提升为管理员
    print(f"\n>>> 提升用户 {test_user['full_name']} 为管理员")
    promote_res = requests.post(
        f"{BASE_URL}/api/admin/users/promote",
        headers=headers,
        params={"user_id": test_user["id"]}
    )
    print_response("提升为管理员", promote_res)
    
    # 9. 部门筛选
    print("\n>>> 按部门筛选（技术部）")
    dept_res = requests.get(
        f"{BASE_URL}/api/admin/users",
        headers=headers,
        params={"status": "active", "department": "技术部"}
    )
    print_response("部门筛选", dept_res)
    
    # 10. 移出成员
    if len(members) > 1:
        print(f"\n>>> 移出成员 {members[1]['full_name']}")
        remove_res = requests.delete(
            f"{BASE_URL}/api/admin/users/{members[1]['id']}",
            headers=headers
        )
        print_response("移出成员", remove_res)
    
    print("\n" + "="*60)
    print("✅ 成员管理系统测试完成")
    print("="*60)


if __name__ == "__main__":
    try:
        test_user_management()
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保后端已启动")
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
