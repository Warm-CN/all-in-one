# 共建模块 - 元素选择模式设计

## 背景
替代原始截图+画布批注方案,改为浏览器元素选择模式,更直观地定位问题元素。

## 核心流程
1. 用户在共建页点击"提建议" → 选择目标页面 → 同标签页跳转
2. 页面进入元素选择模式:浮动工具栏 + 悬停高亮 + 点击选中
3. 点击元素 → 内联气泡输入框 → 输入描述 → 确认 → 数字徽章
4. 可选多个元素,可编辑已有徽章
5. 点击"完成" → 自动截取全页(html-to-image) + 记录元素信息 → 返回共建页
6. 填写标题/分类/描述/署名方式(匿名或实名) → 提交
7. 管理员查看详情:页面截图 + 编号方框 + 元素清单(tag/class/文本/组件名/页面名称/描述)
8. 讨论区:可匿名或实名发表评论,支持复议

## 元素信息
- tag: 元素标签(div/button/span)
- class: class列表
- text: 文本内容(截断200字)
- selector: CSS选择器路径
- component: Vue组件名(via __vueParentComponent)
- pageName: 来源页面中文名称(如"首页概览")
- rect: {x, y, w, h} 相对页面位置
- description: 问题描述

## 匿名/实名机制
- 意见提交时可选匿名/实名,匿名时列表和详情显示"匿名用户",实名显示真实姓名
- 评论同理,匿名时显示"匿名用户",实名显示真实姓名
- 后端 Suggestion 和 Reply 模型新增 `is_anonymous` 字段(INT, 0=实名, 1=匿名)
- API 返回 `author_name`(匿名时为 null)和 `is_anonymous` 标志

## 截图方案
使用 `html-to-image` 库的 `toJpeg` 方法替代 `html2canvas`,支持现代 CSS 颜色函数(如 oklab)。
截图通过带认证头的 fetch 请求获取 Blob URL 加载,避免 `<img>` 无法携带 Authorization 的问题。

## 权限控制
- 普通用户无法访问 admin 路由(路由守卫拦截 + 菜单隐藏 + 页面选择器过滤)
- 共建页面选择器对普通用户隐藏管理工具页面选项

## 响应式适配
- 元素选择工具栏:手机端竖排半透明背景,电脑端横排(sm: 断点)
- 共建标题区域加大美化,卡片显示提出者名称

## 后端改动
| 文件 | 改动 |
|------|------|
| models/suggestion.py | Suggestion 和 Reply 新增 `is_anonymous` 字段 |
| schemas/suggestion.py | SuggestionCreate 和 ReplyCreate 新增 `is_anonymous` |
| api/v1/suggestions.py | 创建/查询时处理 is_anonymous,返回 author_name |

## 前端改动
| 文件 | 改动 |
|------|------|
| MainLayout.vue | 元素选择模式(悬停高亮+点击选中+气泡+徽章+html-to-image截图),工具栏响应式浅色风格 |
| CoBuild.vue | 接收元素数据,打开提交表单,提交时传 is_anonymous,标题美化 |
| SuggestionForm.vue (新) | 元素清单+标题/分类/描述/署名方式选择 |
| SuggestionDetail.vue | 截图+编号方框+元素信息清单(含页面名称),头部显示标题+提出者,关联页面用中文名 |
| SuggestionCard.vue | 卡片标题加大,显示提出者名称(匿名/实名) |
| DiscussionThread.vue | 评论署名选择(匿名/实名),显示真实用户名 |
| ScreenshotLauncher.vue | 页面选择器,普通用户过滤 admin 页面 |
| cobuildData.js | 共享状态结构 + PAGE_LABELS 映射 + getPageLabel() |
| router/index.js | admin 路由添加 requireAdmin meta,路由守卫权限拦截 |
| api/suggestion.js | 新增 fetchScreenshotImage(带认证获取截图 Blob) |
