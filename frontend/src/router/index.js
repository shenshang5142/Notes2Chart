import { createRouter, createWebHashHistory } from 'vue-router'
import SentenceDetail from '@/components/SentenceDetail.vue';


const routes = [
    {
        path: '/',
        redirect: '/login'
    },
    {
        path: '/login',
        name: 'login',
        meta: {
            title: '登录'
        },
        component: () => import('../view/Login.vue')
    },
    {
        path: '/home',
        name: '主页',
        meta: {
            title: '主页'
        },
        component: () => import('../view/Home.vue'),
        redirect: '/index',
        children: [
            {
                path: '/index',
                meta: {
                    title: '首页'
                },
                component: () => import('../view/Welcome.vue')
            },
            {
                path: '/menus/menu1',
                meta: {
                    title: '图表生成'
                },
                component: () => import('../view/menus/menu1.vue'),
            },
            {
                path: '/menus/menu2',
                meta: {
                    title: '学习笔记'
                },
                component: () => import('../view/menus/menu2.vue'),
            },
            {
                path: '/menus/menu3',
                meta: {
                    title: '学习成长雷达图'
                },
                component: () => import('../view/menus/menu3.vue'),
            },
            {
                path: '/user/detail',
                meta: {
                    title: '用户中心'
                },
                component: () => import('../view/user/detail.vue'),
            },
            {
                path: '/aboutp/aboutp',
                meta: {
                    title: '关于项目'
                },
                component: () => import('../view/aboutp/aboutp.vue'),
            },
            {
                path: '/sentence/:id',
                name: 'SentenceDetail',
                component: SentenceDetail
              }
            
        ]
    },
]
const router = createRouter({
    history: createWebHashHistory(),
    routes
})
// 挂载路由导航守卫：to表示将要访问的路径，from表示从哪里来，next是下一个要做的操作
router.beforeEach((to, from, next) => {
    // 修改页面 title
    if (to.meta.title) {
      document.title = '学习笔记图表生成系统 - ' + to.meta.title
    }
    // 放行登录页面
    if (to.path === '/login') {
      return next()
    }
    // 获取token
    // const token= sessionStorage.getItem('token')
    // if (!token) {
    //   return next('/login')
    // } else {
    //   next()
    // }
    return next()
  })
  
// 导出路由
export default router