/**
 * 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

// 路由配置
const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Login.vue'),
        meta: {
            title: '登录',
            requiresAuth: false
        }
    },
    {
        path: '/',
        component: () => import('@/layout/MainLayout.vue'),
        redirect: '/home',
        children: [
            {
                path: 'home',
                name: 'Home',
                component: () => import('@/views/Home.vue'),
                meta: {
                    title: '首页概览',
                    requiresAuth: true
                }
            },
            {
                path: 'rooms',
                name: 'Rooms',
                component: () => import('@/views/MeetingRoom.vue'),
                meta: { title: '会议室预约', requiresAuth: true }
            },
            {
                path: 'recruitment',
                name: 'Recruitment',
                component: () => import('@/views/Placeholder.vue'),
                meta: { title: '招新面试', requiresAuth: true }
            },
            {
                path: 'wireless-cup',
                name: 'WirelessCup',
                component: () => import('@/views/Placeholder.vue'),
                meta: { title: '无线杯', requiresAuth: true }
            },
            {
                path: 'telecom-cup',
                name: 'TelecomCup',
                component: () => import('@/views/Placeholder.vue'),
                meta: { title: '电信杯', requiresAuth: true }
            },
            {
                path: 'settings',
                name: 'AccountSettings',
                component: () => import('@/views/AccountSettings.vue'),
                meta: { title: '账号设置', requiresAuth: true }
            },
            {
                path: 'contacts',
                name: 'Contacts',
                component: () => import('@/views/Contacts.vue'),
                meta: { title: '通讯录', requiresAuth: true }
            },
            {
                path: 'users',
                name: 'Users',
                component: () => import('@/views/UserManagement.vue'),
                meta: { title: '成员管理', requiresAuth: true }
            },
            {
                path: 'admin/rooms',
                name: 'AdminRooms',
                component: () => import('@/views/MeetingRoomAdmin.vue'),
                meta: { title: '会议室管理', requiresAuth: true }
            },
            {
                path: 'admin/schedule',
                name: 'AdminSchedule',
                component: () => import('@/views/AdminSchedule.vue'),
                meta: { title: '日程管理', requiresAuth: true }
            },
            {
                path: 'admin/recruitment',
                name: 'AdminRecruitment',
                component: () => import('@/views/Placeholder.vue'),
                meta: { title: '招新数据管理', requiresAuth: true }
            },
            {
                path: 'admin/contest',
                name: 'AdminContest',
                component: () => import('@/views/Placeholder.vue'),
                meta: { title: '比赛后台管理', requiresAuth: true }
            }
        ]
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        redirect: '/home'
    }
]

// 创建路由实例
const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

// 全局前置守卫 - 路由权限控制
router.beforeEach((to, from, next) => {
    const userStore = useUserStore()

    // 设置页面标题
    document.title = to.meta.title ? `${to.meta.title} - 社团管理系统` : '社团管理系统'

    // 判断是否需要登录
    if (to.meta.requiresAuth) {
        // 检查是否已登录
        if (userStore.isLoggedIn) {
            next()
        } else {
            ElMessage.warning('请先登录')
            next({
                path: '/login',
                query: { redirect: to.fullPath } // 保存目标路由，登录后跳转
            })
        }
    } else {
        // 如果已登录，访问登录页时自动跳转到首页
        if (to.path === '/login' && userStore.isLoggedIn) {
            next('/home')
        } else {
            next()
        }
    }
})

export default router
