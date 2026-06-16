# 日程管理系统 API 文档

## 概述

日程管理系统提供社团日程的查询和管理功能。普通用户可以查询日程，管理员可以创建和管理日程。

## 数据库模型

### Schedule（日程表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键ID |
| title | String(200) | 日程标题 |
| schedule_date | Date | 日程日期 |
| start_time | Time | 开始时间 |
| end_time | Time | 结束时间 |
| location | String(200) | 地点（可选） |
| color | String(20) | 颜色标记（默认 #3B82F6） |
| created_at | DateTime | 创建时间（自动） |
| updated_at | DateTime | 更新时间（自动） |

## API 接口

---

## 一、普通用户接口（所有登录用户）

### 1. 获取日程列表

**GET** `/api/v1/schedules`

获取日程列表，支持多种查询模式。

**请求头：**
```
Authorization: Bearer {access_token}
```

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | date | 否 | 查询指定日期的日程（格式：YYYY-MM-DD） |
| start_date | date | 否 | 查询日期范围的起始日期 |
| end_date | date | 否 | 查询日期范围的结束日期 |

**查询模式说明：**

1. **单日查询**：传入 `date` 参数
   ```
   GET /api/v1/schedules?date=2026-02-01
   ```

2. **日期范围查询**：传入 `start_date` 和 `end_date` 参数
   ```
   GET /api/v1/schedules?start_date=2026-02-01&end_date=2026-02-07
   ```

3. **仅起始日期**：传入 `start_date`，查询从该日期起的所有日程
   ```
   GET /api/v1/schedules?start_date=2026-02-01
   ```

4. **仅结束日期**：传入 `end_date`，查询到该日期止的所有日程
   ```
   GET /api/v1/schedules?end_date=2026-02-28
   ```

**成功响应 (200)：**
```json
{
  "code": 200,
  "msg": "查询成功",
  "data": [
    {
      "id": 1,
      "title": "技术分享会",
      "schedule_date": "2026-02-01",
      "start_time": "14:00",
      "end_time": "16:00",
      "location": "北三会议室",
      "color": "#3B82F6",
      "created_at": "2026-01-28 10:00:00",
      "updated_at": "2026-01-28 10:00:00"
    },
    {
      "id": 2,
      "title": "新成员见面会",
      "schedule_date": "2026-02-01",
      "start_time": "19:00",
      "end_time": "21:00",
      "location": "活动中心",
      "color": "#10B981",
      "created_at": "2026-01-28 11:00:00",
      "updated_at": "2026-01-28 11:00:00"
    }
  ]
}
```

**无参数响应 (200)：**
```json
{
  "code": 200,
  "msg": "请指定查询条件",
  "data": []
}
```

---

## 二、管理员接口（仅 Admin）

### 2. 创建日程

**POST** `/api/v1/admin/schedules`

创建新的日程，系统会检测时间冲突但不阻止创建。

**请求头：**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**请求体：**
```json
{
  "title": "技术分享会",
  "schedule_date": "2026-02-01",
  "start_time": "14:00",
  "end_time": "16:00",
  "location": "北三会议室",
  "color": "#3B82F6"
}
```

**字段说明：**
- `title` (必填): 日程标题，1-200 字符
- `schedule_date` (必填): 日程日期，格式 YYYY-MM-DD
- `start_time` (必填): 开始时间，格式 HH:MM (24小时制)
- `end_time` (必填): 结束时间，格式 HH:MM，必须晚于开始时间
- `location` (可选): 地点，最大 200 字符
- `color` (可选): 颜色标记，默认 #3B82F6

**核心校验逻辑：**
1. ✅ 结束时间必须晚于开始时间
2. ✅ 检测时间冲突（但不阻止创建）
3. ✅ 返回冲突日程列表（如有）

**成功响应 (200) - 无冲突：**
```json
{
  "code": 200,
  "msg": "日程创建成功",
  "data": {
    "id": 1,
    "title": "技术分享会",
    "schedule_date": "2026-02-01",
    "start_time": "14:00",
    "end_time": "16:00",
    "location": "北三会议室",
    "color": "#3B82F6",
    "created_at": "2026-01-28 14:00:00",
    "updated_at": "2026-01-28 14:00:00"
  }
}
```

**成功响应 (200) - 有冲突：**
```json
{
  "code": 200,
  "msg": "日程创建成功",
  "data": {
    "id": 2,
    "title": "项目讨论",
    "schedule_date": "2026-02-01",
    "start_time": "15:00",
    "end_time": "17:00",
    "location": "北三会议室",
    "color": "#3B82F6",
    "created_at": "2026-01-28 14:05:00",
    "updated_at": "2026-01-28 14:05:00",
    "warning": "该时间段与 1 个已有日程重叠",
    "overlapping_schedules": [
      {
        "id": 1,
        "title": "技术分享会",
        "time_range": "14:00-16:00"
      }
    ]
  }
}
```

**失败响应示例：**

**时间无效 (400)：**
```json
{
  "code": 400,
  "msg": "结束时间必须晚于开始时间",
  "data": null
}
```

---

### 3. 删除日程

**DELETE** `/api/v1/admin/schedules/{schedule_id}`

删除指定的日程。

**请求头：**
```
Authorization: Bearer {access_token}
```

**路径参数：**
- `schedule_id` (必填): 日程的ID

**成功响应 (200)：**
```json
{
  "code": 200,
  "msg": "日程删除成功",
  "data": {
    "id": 1
  }
}
```

**失败响应示例：**

**日程不存在 (404)：**
```json
{
  "code": 404,
  "msg": "日程不存在",
  "data": null
}
```

---

### 4. 检查时间冲突

**GET** `/api/v1/admin/schedules/check-overlap`

检查指定时间段是否与已有日程冲突。

**请求头：**
```
Authorization: Bearer {access_token}
```

**查询参数：**
- `schedule_date` (必填): 日程日期
- `start_time` (必填): 开始时间
- `end_time` (必填): 结束时间
- `exclude_id` (可选): 排除的日程ID（用于更新时忽略自己）

**成功响应 (200) - 无冲突：**
```json
{
  "code": 200,
  "msg": "检查完成",
  "data": {
    "has_conflict": false,
    "overlapping_schedules": []
  }
}
```

**成功响应 (200) - 有冲突：**
```json
{
  "code": 200,
  "msg": "检查完成",
  "data": {
    "has_conflict": true,
    "overlapping_schedules": [
      {
        "id": 1,
        "title": "技术分享会",
        "time_range": "14:00-16:00"
      },
      {
        "id": 2,
        "title": "项目讨论",
        "time_range": "15:30-17:00"
      }
    ]
  }
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

| 已有日程 | 新日程请求 | 是否冲突 | 原因 |
|---------|-----------|---------|------|
| 14:00-16:00 | 15:00-17:00 | ✅ 冲突 | 15:00 < 16:00 且 17:00 > 14:00 |
| 14:00-16:00 | 13:00-14:30 | ✅ 冲突 | 13:00 < 16:00 且 14:30 > 14:00 |
| 14:00-16:00 | 16:00-18:00 | ❌ 无冲突 | 16:00 不小于 16:00 |
| 14:00-16:00 | 12:00-14:00 | ❌ 无冲突 | 14:00 不大于 14:00 |
| 14:00-16:00 | 10:00-12:00 | ❌ 无冲突 | 完全不重叠 |

---

## 认证说明

所有接口都需要携带 JWT Token 进行身份验证。

**获取 Token：**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "student_id": "110",
  "password": "654321"
}
```

**使用 Token：**
```bash
GET /api/v1/schedules?date=2026-02-01
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 权限说明

| 功能 | 所需权限 |
|------|----------|
| 查询日程 | 所有登录用户 |
| 创建日程 | 仅 Admin |
| 删除日程 | 仅 Admin |
| 检查冲突 | 仅 Admin |

---

## 快速开始

### 1. 启动后端服务

```bash
cd d:\code\python\all_in_one
python main.py
```

### 2. 访问 API 文档

打开浏览器访问：http://localhost:8001/docs

在 Swagger UI 中可以直接测试所有接口。

---

## 前端集成示例

```javascript
// 1. 获取指定日期的日程
async function getSchedules(date) {
  const response = await fetch(`/api/v1/schedules?date=${date}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  const result = await response.json();
  return result.data;
}

// 2. 获取日期范围内的日程
async function getSchedulesInRange(startDate, endDate) {
  const response = await fetch(`/api/v1/schedules?start_date=${startDate}&end_date=${endDate}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  const result = await response.json();
  return result.data;
}

// 3. 创建日程（管理员）
async function createSchedule(scheduleData) {
  const response = await fetch('/api/v1/admin/schedules', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(scheduleData)
  });
  const result = await response.json();

  if (result.code === 200) {
    if (result.data.warning) {
      console.warn(result.data.warning);
      console.log('冲突日程：', result.data.overlapping_schedules);
    }
    alert('日程创建成功！');
  } else {
    alert(result.msg);
  }
}

// 4. 删除日程（管理员）
async function deleteSchedule(scheduleId) {
  const response = await fetch(`/api/v1/admin/schedules/${scheduleId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  const result = await response.json();

  if (result.code === 200) {
    alert('日程已删除');
  }
}

// 5. 检查时间冲突（管理员）
async function checkOverlap(date, startTime, endTime) {
  const response = await fetch(`/api/v1/admin/schedules/check-overlap?schedule_date=${date}&start_time=${startTime}&end_time=${endTime}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  const result = await response.json();
  return result.data;
}
```

---

## 注意事项

1. ⚠️ 所有时间使用24小时制，格式为 HH:MM
2. ⚠️ 日期格式统一为 YYYY-MM-DD（ISO 8601）
3. ⚠️ 创建日程时如果检测到时间冲突，系统会返回警告但仍会创建
4. ⚠️ 普通用户只能查询日程，只有管理员可以创建和删除日程
5. ⚠️ 日程按日期和开始时间排序返回
6. ⚠️ 颜色标记使用十六进制颜色码，如 #3B82F6（蓝色）、#10B981（绿色）、#EF4444（红色）

---

## 常用颜色代码参考

| 颜色 | 代码 | 适用场景 |
|------|------|----------|
| 蓝色 | #3B82F6 | 一般活动 |
| 绿色 | #10B981 | 成员活动 |
| 红色 | #EF4444 | 重要会议 |
| 黄色 | #F59E0B | 提醒事项 |
| 紫色 | #8B5CF6 | 培训活动 |
| 粉色 | #EC4899 | 社交活动 |
