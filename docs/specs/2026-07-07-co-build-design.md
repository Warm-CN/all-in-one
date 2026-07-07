# 共建页面设计文档

> **日期**: 2026-07-07
> **状态**: 设计待审核
> **分支**: ZHM

## 1. 概述

### 1.1 目标

为社团管理系统新增"共建"模块,允许所有内部成员对系统页面提出建设性意见(布局美化、功能优化、Bug 反馈等),并通过截图 + 任意形状框选 + 文字批注的方式精确描述问题位置。管理员可查看所有意见、直接阅读框选区域对应的文字说明、管理状态流转,成员可针对同一问题反复追加意见并互相复议。

### 1.2 用户角色

| 角色 | 权限 |
|------|------|
| 普通成员 | 提交意见、查看所有意见、参与讨论、复议 |
| 管理员 | 上述全部 + 修改状态、回复、查看 OCR 文字提取 |

### 1.3 性能硬指标

- 截图模式触发到可框选 < 500ms
- 批注绘制(框选/拖动/删除)全程无卡顿,60fps
- 单张截图压缩后 < 200KB
- 列表页首屏加载 < 1s(缩略图懒加载)
- OCR 不阻塞前端提交

## 2. 截图入口

共建页顶部设置一个下拉选择器,列出系统所有可反馈页面:

```
可选页面:
- 首页概览 /home
- 会议室预约 /rooms
- 招新面试 /recruitment
- 竞赛队伍 /teams-center
- 通讯录 /contacts
- 账号设置 /settings
- 成员管理 /users
- 日程管理 /admin/schedule
- 会议室管理 /admin/rooms
- 招新管理 /admin/recruitment
- 赛事管理 /admin/events
```

用户选择目标页面 → 点击"前往截图" → 系统在新标签页打开该页面,并自动进入截图模式(整页变暗 + 十字光标)。截图完成后,批注编辑器在共建页主流程中打开。

多张截图时,可切换下拉选择不同页面分别截图,汇总到一个意见中。

## 3. 批注编辑器

### 3.1 画布交互

截完一张图后进入批注编辑器(全屏遮罩浮层):

- **左侧**:刚截的图作为背景 + Canvas 2D 画布叠加(所有批注绘制在 Canvas 上,零 DOM 重排)
- **工具栏**:矩形框选、任意形状(freehand)框选、文字标注、撤销、清除、添加下一张截图
- **框选操作**:鼠标拖拽画矩形或自由路径,松开后自动选中该区域并弹出输入框,用户必须输入该框选区域的文字说明(必填),可删除/改颜色
- **文字标注**:点击画布任意位置,弹出输入框,输入后文字渲染在 Canvas 上
- **多张截图**:一个意见可关联多张截图,每张独立编辑

### 3.2 右侧表单

- 标题(必填)
- 分类:布局美化 / 功能优化 / Bug 反馈 / 其他
- 描述(必填)
- 关联页面 URL(自动从下拉选择填充)
- 截图列表(缩略图,可切换编辑)

### 3.3 性能保障

- html2canvas 仅在"前往截图"时执行一次,按框选区域裁剪
- 所有批注(矩形/任意形状/文字)绘制在单个 `<canvas>` 上,拖动重绘只清画布重画,不创建/删除 DOM 元素
- 截图存储前压缩:PNG → JPEG quality 0.7,最大宽度 1920px
- 列表页缩略图用 IntersectionObserver 懒加载

## 4. 批注文字提取

### 4.1 方案

不使用 OCR。用户每次框选(矩形/任意形状)或添加文字标注时,即弹出输入框要求输入该批注的内容说明,随截图一起提交。

### 4.2 管理员视图

意见详情页中,管理员看到:
- 框选文字清单:"框 1: xxx / 框 2: xxx"(直接可读,不必看图)
- 下方配缩略图(可选查看)
- 文字批注也一并列出

### 4.3 优势

- 零 OCR 依赖,无环境配置成本
- 文字由用户亲自输入,准确率 100%
- 提交即保存,无异步等待

## 5. 状态机

### 5.1 状态定义

| 状态 | 中文名 | 说明 |
|------|--------|------|
| received | 已收到 | 提交后默认 |
| pending_fix | 等待修改 | 管理员确认需处理 |
| fixing | 修改中 | 管理员开始处理 |
| wont_fix | 不予修改 | 必填原因 |
| done | 修改成功 | 自动记录完成时间 + 修改人 |

### 5.2 流转规则

```
received → pending_fix → fixing → done
                 └→ wont_fix (必填原因)
```

- 仅管理员可改状态
- 每次状态变更可选填说明
- "不予修改"必填原因
- "修改成功"自动记录 `done_at`(完成时间)和 `done_by`(当前管理员)
- 所有状态变更记入 `status_history`

## 6. 讨论与复议

### 6.1 讨论区

每条意见下方有讨论区:
- **作者追加**:意见作者可多次追加后续意见,作为该意见的 reply(带时间戳)
- **其他用户评论**:所有登录用户可在讨论区发评论
- **管理员回复**:管理员在讨论区回复,形成双方对话
- **所有交流文字对所有用户可见**

### 6.2 复议

- 每条 reply 有"支持/复议"按钮
- 点击后 `endorse_count + 1`
- 同一用户对同一 reply 只能复议一次(取消可撤回)
- 按 `endorse_count` 排序展示高赞回复

## 7. 数据模型

### Suggestion(意见)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK | 自增主键 |
| title | varchar(200) | 标题 |
| description | text | 描述 |
| category | enum | layout / feature / bug / other |
| status | enum | received / pending_fix / fixing / wont_fix / done |
| page_url | varchar(500) | 关联页面 URL |
| author_id | int FK | 提出者 |
| created_at | datetime | 创建时间 |
| done_at | datetime | 完成时间(仅 done) |
| done_by | int FK | 修改人(仅 done) |

### Screenshot(截图)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK | 自增主键 |
| suggestion_id | int FK | 关联意见 |
| image_data | longblob | JPEG 压缩数据 |
| width | int | 原图宽度 |
| height | int | 原图高度 |
| created_at | datetime | 创建时间 |

### Annotation(批注)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK | 自增主键 |
| screenshot_id | int FK | 关联截图 |
| type | enum | rect / freehand / text |
| coords | json | rect: {x,y,w,h}; freehand: {points:[[x,y],...]}; text: {x,y} |
| text | varchar(500) | 文字批注内容(用户输入,必填) |
| color | varchar(20) | 颜色 |
| created_at | datetime | 创建时间 |

### StatusChange(状态变更记录)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK | 自增主键 |
| suggestion_id | int FK | 关联意见 |
| from_status | enum | 原状态 |
| to_status | enum | 新状态 |
| reason | text | 说明/不予修改原因 |
| operator_id | int FK | 操作人 |
| created_at | datetime | 操作时间 |

### Reply(讨论回复)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK | 自增主键 |
| suggestion_id | int FK | 关联意见 |
| parent_id | int FK | 父回复(支持嵌套),可为空 |
| author_id | int FK | 作者 |
| content | text | 内容 |
| endorse_count | int | 复议数,默认 0 |
| created_at | datetime | 创建时间 |

### Endorsement(复议记录)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK | 自增主键 |
| reply_id | int FK | 关联回复 |
| user_id | int FK | 复议用户 |
| created_at | datetime | 复议时间 |
| | UNIQUE(reply_id, user_id) | 防重复 |

## 8. API 设计

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/v1/suggestions` | GET | 列表(分页,可按状态/作者筛选) | 登录用户 |
| `/api/v1/suggestions` | POST | 提交意见(含多截图+批注) | 登录用户 |
| `/api/v1/suggestions/{id}` | GET | 详情(含截图、批注、OCR、讨论) | 登录用户 |
| `/api/v1/suggestions/{id}/status` | PATCH | 改状态 | 管理员 |
| `/api/v1/suggestions/{id}/replies` | POST | 追加意见/评论 | 登录用户 |
| `/api/v1/replies/{id}/endorse` | POST | 复议/支持(取消再点撤回) | 登录用户 |

### 提交数据格式

```json
{
  "title": "首页卡片间距过小",
  "description": "首页欢迎区下方卡片间距太小,建议加大",
  "category": "layout",
  "page_url": "/home",
  "screenshots": [
    {
      "image_data": "base64...",
      "width": 1920,
      "height": 1080,
      "annotations": [
        {
          "type": "rect",
          "coords": {"x": 100, "y": 200, "w": 300, "h": 150},
          "text": "这里间距太小",
          "color": "#EF4444"
        },
        {
          "type": "freehand",
          "coords": {"points": [[50,50],[60,52],[70,55],...]},
          "text": "这个区域的布局需要调整",
          "color": "#3B82F6"
        },
        {
          "type": "text",
          "coords": {"x": 500, "y": 300},
          "text": "建议改为 24px 间距",
          "color": "#10B981"
        }
      ]
    }
  ]
}
```

## 9. 前端结构

```
frontend/src/
├── views/
│   └── CoBuild.vue                  # 共建主页(意见列表+页面选择+提建议)
├── components/cobuild/
│   ├── ScreenshotLauncher.vue       # 页面下拉选择+前往截图按钮
│   ├── AnnotationEditor.vue         # 批注编辑器(截图+Canvas+工具栏+表单)
│   ├── ScreenshotCanvas.vue         # Canvas 画布(矩形/任意形状/文字绘制)
│   ├── SuggestionCard.vue           # 意见列表卡片
│   ├── SuggestionDetail.vue         # 意见详情(含OCR清单+讨论区)
│   └── DiscussionThread.vue         # 讨论区(回复+复议)
├── api/
│   └── suggestion.js                # API 封装
└── router/index.js                  # 新增 /co-build 路由
```

### 路由

```js
{
    path: 'co-build',
    name: 'CoBuild',
    component: () => import('@/views/CoBuild.vue'),
    meta: { title: '共建', requiresAuth: true }
}
```

### 菜单

在 MainLayout.vue 的侧边栏"协会资源"分组中新增"共建"菜单项,所有登录用户可见。

## 10. 后端结构

```
app/
├── api/v1/
│   └── suggestions.py               # 路由
├── models/
│   └── suggestion.py                # SQLAlchemy 模型
└── schemas/
    └── suggestion.py                # Pydantic schema
```

## 11. 依赖

### 前端

- html2canvas(截图)
- 无新增(Canvas 2D 原生,Element Plus 已有)

### 后端

- pillow(图片处理)

## 12. 错误处理

| 场景 | 处理 |
|------|------|
| html2canvas 截图失败 | 提示重试,允许跳过截图直接提交文字意见 |
| 图片过大(>5MB) | 前端压缩后再提交,超出限制提示 |
| 状态非法流转 | 后端校验 from→to 合法性,拒绝非法跳转 |
| 未登录访问 | 路由守卫拦截,重定向登录 |

## 13. 测试要点

- 截图模式框选(矩形+任意形状)不卡顿
- 多张截图切换编辑正常
- 每次框选强制输入文字说明
- 状态流转合法性校验
- 讨论嵌套回复 + 复议计数
- 权限隔离(普通成员不能改状态)
