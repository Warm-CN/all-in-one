# 会议室预约系统 API 文档

## 概述

简化版会议室预约系统，提供会议室的日常预约管理功能，无需审批流程。包含完整的时间冲突检测机制。

## 数据库模型

### RoomBooking（会议室预约表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键ID |
| user_id | Integer | 预约用户ID（外键关联 users 表） |
| booking_date | Date | 预约日期 |
| start_time | Time | 开始时间 |
| end_time | Time | 结束时间 |
| num_people | Integer | 人数（1-50） |
| remarks | Text | 备注（可选，最大500字符） |
| created_at | DateTime | 创建时间（自动） |
| updated_at | DateTime | 更新时间（自动） |

## API 接口

### 1. 获取预约列表

**GET** `/api/bookings?date=YYYY-MM-DD`

获取指定日期的所有预约记录，按时间先后排序。

**请求头：**
```
Authorization: Bearer {access_token}
```

**查询参数：**
- `date` (必填): 查询日期，格式为 YYYY-MM-DD，例如 `2026-01-28`

**成功响应 (200)：**
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "id": 1,
      "user_id": 5,
      "booking_date": "2026-01-28",
      "start_time": "09:00",
      "end_time": "11:00",
      "num_people": 15,
      "remarks": "部门周会",
      "user_name": "张三",
      "user_dept": "技术部",
      "created_at": "2026-01-27T10:30:00"
    },
    {
      "id": 2,
      "user_id": 8,
      "booking_date": "2026-01-28",
      "start_time": "14:00",
      "end_time": "16:00",
      "num_people": 10,
      "remarks": "项目讨论",
      "user_name": "李四",
      "user_dept": "产品部",
      "created_at": "2026-01-27T11:00:00"
    }
  ]
}
```

---

### 2. 提交预约

**POST** `/api/bookings`

提交会议室预约，系统会自动检查时间冲突并关联当前用户。

**请求头：**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**请求体：**
```json
{
  "booking_date": "2026-01-28",
  "start_time": "09:00",
  "end_time": "11:00",
  "num_people": 15,
  "remarks": "部门周会"
}
```

**字段说明：**
- `booking_date` (必填): 预约日期，格式 YYYY-MM-DD
- `start_time` (必填): 开始时间，格式 HH:MM (24小时制)
- `end_time` (必填): 结束时间，格式 HH:MM，必须晚于开始时间
- `num_people` (必填): 人数，范围 1-50
- `remarks` (可选): 备注信息，最大500字符

**核心校验逻辑：**
1. ✅ 预约日期不能是过去的日期
2. ✅ 预约日期不能超过未来7天
3. ✅ 结束时间必须晚于开始时间
4. ✅ 检查时间段是否与已有预约重叠（冲突检测算法）
5. ✅ 自动通过 JWT Token 关联当前登录用户的 user_id

**成功响应 (200)：**
```json
{
  "code": 200,
  "msg": "预约成功",
  "data": {
    "id": 3,
    "booking_date": "2026-01-28",
    "start_time": "09:00",
    "end_time": "11:00"
  }
}
```

**失败响应示例：**

**时间冲突 (400)：**
```json
{
  "code": 400,
  "msg": "该时段已被占用，请选择其他时间",
  "data": null
}
```

**日期无效 (400)：**
```json
{
  "code": 400,
  "msg": "不能预约过去的日期",
  "data": null
}
```

**超出预约范围 (400)：**
```json
{
  "code": 400,
  "msg": "只能预约未来7天内的日期",
  "data": null
}
```

---

### 3. 取消预约

**DELETE** `/api/bookings/{id}`

取消指定的会议室预约。

**请求头：**
```
Authorization: Bearer {access_token}
```

**路径参数：**
- `id` (必填): 预约记录的ID

**权限控制：**
- 普通用户只能删除自己的预约
- 管理员 (role=admin) 可以删除任何预约

**成功响应 (200)：**
```json
{
  "code": 200,
  "msg": "预约已取消",
  "data": null
}
```

**失败响应示例：**

**预约不存在 (404)：**
```json
{
  "code": 404,
  "msg": "预约不存在",
  "data": null
}
```

**无权删除 (403)：**
```json
{
  "code": 403,
  "msg": "无权删除此预约",
  "data": null
}
```

---

### 4. 获取我的预约

**GET** `/api/bookings/my?upcoming=false`

获取当前登录用户的所有预约记录。

**请求头：**
```
Authorization: Bearer {access_token}
```

**查询参数：**
- `upcoming` (可选): 是否仅获取未来（含今天）的预约，默认 `false`
  - `upcoming=true`: 仅获取未来（含今天）的预约，按时间正序排列（最近的在前面）
  - `upcoming=false`: 获取所有预约，按时间倒序排列（最新的在前面）

**成功响应 (200) - 获取所有预约（默认）：**
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "id": 5,
      "booking_date": "2026-02-01",
      "start_time": "10:00",
      "end_time": "12:00",
      "num_people": 8,
      "remarks": "培训课程",
      "created_at": "2026-01-27T14:20:00"
    },
    {
      "id": 3,
      "booking_date": "2026-01-28",
      "start_time": "09:00",
      "end_time": "11:00",
      "num_people": 15,
      "remarks": "部门周会",
      "created_at": "2026-01-27T10:30:00"
    }
  ]
}
```

**成功响应 (200) - 仅获取未来预约：**

请求：`GET /api/bookings/my?upcoming=true`

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "id": 3,
      "booking_date": "2026-02-05",
      "start_time": "09:00",
      "end_time": "11:00",
      "num_people": 15,
      "remarks": "部门周会",
      "created_at": "2026-01-27T10:30:00"
    },
    {
      "id": 7,
      "booking_date": "2026-02-08",
      "start_time": "14:00",
      "end_time": "16:00",
      "num_people": 10,
      "remarks": "项目讨论",
      "created_at": "2026-02-01T09:00:00"
    }
  ]
}
```

---

## 时间冲突检测算法

系统使用以下逻辑检测时间段是否重叠：

```
如果满足以下条件，则两个时间段重叠：
  start_time < existing.end_time AND end_time > existing.start_time
```

**示例：**

| 已有预约 | 新预约请求 | 是否冲突 | 原因 |
|---------|-----------|---------|------|
| 09:00-11:00 | 10:00-12:00 | ✅ 冲突 | 10:00 < 11:00 且 12:00 > 09:00 |
| 09:00-11:00 | 08:00-09:30 | ✅ 冲突 | 08:00 < 11:00 且 09:30 > 09:00 |
| 09:00-11:00 | 11:00-13:00 | ❌ 无冲突 | 11:00 不小于 11:00 |
| 09:00-11:00 | 07:00-09:00 | ❌ 无冲突 | 09:00 不大于 09:00 |
| 09:00-11:00 | 14:00-16:00 | ❌ 无冲突 | 完全不重叠 |

---

## 认证说明

所有接口都需要携带 JWT Token 进行身份验证。

**获取 Token：**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "student_id": "2021001",
  "password": "password123"
}
```

**使用 Token：**
```bash
GET /api/bookings?date=2026-01-28
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 快速开始

### 1. 启动后端服务

```bash
cd d:\code\python\all_in_one
python main.py
```

### 2. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

在 Swagger UI 中可以直接测试所有接口。

### 3. 使用测试脚本

```bash
cd d:\code\python\all_in_one
python tests/test_room_bookings.py
```

---

## 前端集成示例

```javascript
// 1. 获取指定日期的预约列表
async function getBookings(date) {
  const response = await fetch(`/api/bookings?date=${date}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  const data = await response.json();
  return data.data;
}

// 2. 提交预约
async function createBooking(bookingData) {
  const response = await fetch('/api/bookings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(bookingData)
  });
  const result = await response.json();
  
  if (result.code === 200) {
    alert('预约成功！');
  } else {
    alert(result.msg); // 显示错误信息，如"该时段已被占用"
  }
}

// 3. 取消预约
async function cancelBooking(bookingId) {
  const response = await fetch(`/api/bookings/${bookingId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  const result = await response.json();

  if (result.code === 200) {
    alert('预约已取消');
  }
}

// 4. 获取我的所有预约
async function getMyBookings() {
  const response = await fetch('/api/bookings/my', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  const result = await response.json();
  return result.data;
}

// 5. 获取我的未来预约（含今天）
async function getMyUpcomingBookings() {
  const response = await fetch('/api/bookings/my?upcoming=true', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  const result = await response.json();
  return result.data;
}
```

---

## 数据库迁移

首次使用时，需要创建数据库表：

```bash
# 启动应用时会自动创建表
python main.py
```

表 `room_bookings` 将自动创建。

---

## 注意事项

1. ⚠️ 所有时间使用24小时制，格式为 HH:MM
2. ⚠️ 日期格式统一为 YYYY-MM-DD（ISO 8601）
3. ⚠️ 普通用户只能删除自己的预约，管理员可删除任意预约
4. ⚠️ 时间冲突检测仅针对同一日期，不同日期的预约不会冲突
5. ⚠️ 系统会自动记录预约的创建时间和更新时间
6. ⚠️ 只能预约未来7天内的日期（含今天）
7. ⚠️ 获取预约列表时会包含预约者的姓名和部门信息
