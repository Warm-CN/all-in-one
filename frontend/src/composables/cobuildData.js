import { reactive } from 'vue'

/**
 * 页面 URL → 中文名称 映射
 */
export const PAGE_LABELS = {
  '/home': '首页概览',
  '/rooms': '会议室预约',
  '/recruitment': '招新面试',
  '/teams-center': '竞赛队伍',
  '/contacts': '通讯录',
  '/settings': '账号设置',
  '/users': '成员管理',
  '/admin/schedule': '日程管理',
  '/admin/rooms': '会议室管理',
  '/admin/management': '招新管理',
  '/admin/events': '赛事管理',
  '/co-build': '共建',
}

/**
 * 根据 URL 获取页面名称
 */
export function getPageLabel(url) {
  if (!url) return ''
  return PAGE_LABELS[url] || url
}

/**
 * 跨路由共享的共建数据
 * 在同一 SPA 会话中,路由切换不会丢失这些数据
 */
export const cobuildState = reactive({
  // 元素选择完成后的待处理数据(从目标页面返回 co-build 时读取)
  pendingData: null,
  // { pageUrl, pageName, screenshot: { imageSrc, width, height }, elements: [{ tag, class, text, selector, component, pageName, rect: {x,y,w,h}, description }] }

  // 进行中的数据(已有元素,正在添加更多)
  inProgress: null  // 同 pendingData 结构
})
