import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router/index.js'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import * as Icons from '@element-plus/icons-vue'
import commonJs from './assets/js/common'



const app = createApp(App)

// 注册 Element Plus 图标组件
for (let i in Icons) {
    app.component(i, Icons[i])
}

// 使用 Element Plus 并设置中文语言
app.use(ElementPlus, {
  locale: zhCn,
})

// 将 commonJs 挂载到全局属性
app.config.globalProperties.$commonJs = commonJs

// 使用路由器
app.use(router)

// 挂载应用
app.mount('#app')
