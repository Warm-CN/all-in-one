import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import pinia from './store'

// 引入全局样式（Tailwind CSS + 自定义样式）
import './assets/styles/global.css'
// 引入 animate.css 动画库
import 'animate.css'

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.use(pinia)

app.mount('#app')
