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
        path: '/home',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: {
            title: '首页',
            requiresAuth: true
        }
    },
    {
        path: '/',
        redirect: '/home'
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
