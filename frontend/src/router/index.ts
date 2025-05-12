import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/user'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

NProgress.configure({ showSpinner: false })

// 路由配置
const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/layouts/BasicLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: { title: '仪表盘', icon: 'dashboard' }
      },
      // 广告主管理
      {
        path: '/advertisers',
        name: 'Advertisers',
        component: () => import('@/views/advertiser/List.vue'),
        meta: { title: '广告主管理', icon: 'team' }
      },
      {
        path: '/advertisers/:id',
        name: 'AdvertiserDetail',
        component: () => import('@/views/advertiser/Detail.vue'),
        meta: { title: '广告主详情', hidden: true }
      },
      // 广告活动管理
      {
        path: '/campaigns',
        name: 'Campaigns',
        component: () => import('@/views/campaign/List.vue'),
        meta: { title: '广告活动', icon: 'fund' }
      },
      {
        path: '/campaigns/:id',
        name: 'CampaignDetail',
        component: () => import('@/views/campaign/Detail.vue'),
        meta: { title: '活动详情', hidden: true }
      },
      // 创意管理
      {
        path: '/creatives',
        name: 'Creatives',
        component: () => import('@/views/creative/List.vue'),
        meta: { title: '创意管理', icon: 'picture' }
      },
      {
        path: '/creatives/:id',
        name: 'CreativeDetail',
        component: () => import('@/views/creative/Detail.vue'),
        meta: { title: '创意详情', hidden: true }
      },
      // 报表分析
      {
        path: '/reports',
        name: 'Reports',
        component: () => import('@/views/report/Index.vue'),
        meta: { title: '报表分析', icon: 'bar-chart' },
        children: [
          {
            path: 'performance',
            name: 'PerformanceReport',
            component: () => import('@/views/report/Performance.vue'),
            meta: { title: '效果报表' }
          },
          {
            path: 'custom',
            name: 'CustomReport',
            component: () => import('@/views/report/Custom.vue'),
            meta: { title: '自定义报表' }
          }
        ]
      },
      // 系统设置
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/settings/Index.vue'),
        meta: { title: '系统设置', icon: 'setting' },
        children: [
          {
            path: 'users',
            name: 'Users',
            component: () => import('@/views/settings/Users.vue'),
            meta: { title: '用户管理' }
          },
          {
            path: 'roles',
            name: 'Roles',
            component: () => import('@/views/settings/Roles.vue'),
            meta: { title: '角色权限' }
          }
        ]
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { requiresAuth: false, title: '页面不存在' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 开始加载进度条
  NProgress.start()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - DSP广告管理系统`
  }
  
  // 检查是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const userStore = useUserStore()
    
    // 如果未登录，重定向到登录页
    if (!userStore.isLoggedIn) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

// 路由后置钩子
router.afterEach(() => {
  // 结束进度条
  NProgress.done()
})

export default router 