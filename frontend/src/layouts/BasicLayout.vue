<template>
  <a-layout class="layout">
    <!-- 侧边栏 -->
    <a-layout-sider
      v-model:collapsed="collapsed"
      :trigger="null"
      collapsible
      class="sider"
    >
      <div class="logo">
        <h1 v-if="!collapsed">DSP广告管理系统</h1>
        <h1 v-else>DSP</h1>
      </div>
      
      <!-- 侧边菜单 -->
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
      >
        <template v-for="item in menuItems" :key="item.key">
          <!-- 带子菜单的菜单项 -->
          <template v-if="item.children && item.children.length > 0">
            <a-sub-menu :key="item.key">
              <template #title>
                <span>
                  <component :is="item.icon" />
                  <span>{{ item.title }}</span>
                </span>
              </template>
              <a-menu-item v-for="child in item.children" :key="child.key">
                <router-link :to="child.path">
                  <span>{{ child.title }}</span>
                </router-link>
              </a-menu-item>
            </a-sub-menu>
          </template>
          
          <!-- 普通菜单项 -->
          <template v-else>
            <a-menu-item :key="item.key">
              <router-link :to="item.path">
                <span>
                  <component :is="item.icon" />
                  <span>{{ item.title }}</span>
                </span>
              </router-link>
            </a-menu-item>
          </template>
        </template>
      </a-menu>
    </a-layout-sider>
    
    <a-layout>
      <!-- 顶部栏 -->
      <a-layout-header class="header">
        <div class="header-left">
          <!-- 折叠按钮 -->
          <menu-unfold-outlined
            v-if="collapsed"
            class="trigger"
            @click="() => (collapsed = !collapsed)"
          />
          <menu-fold-outlined
            v-else
            class="trigger"
            @click="() => (collapsed = !collapsed)"
          />
          
          <!-- 面包屑 -->
          <a-breadcrumb class="breadcrumb">
            <a-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index">
              <router-link v-if="item.path" :to="item.path">{{ item.title }}</router-link>
              <span v-else>{{ item.title }}</span>
            </a-breadcrumb-item>
          </a-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- 通知图标 -->
          <a-dropdown>
            <a-badge :count="notificationCount">
              <bell-outlined class="action-icon" />
            </a-badge>
            <template #overlay>
              <a-menu>
                <a-menu-item key="1">
                  <notification-outlined />
                  系统通知 ({{ notificationCount }})
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item key="2">
                  <check-outlined />
                  全部标记为已读
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
          
          <!-- 用户菜单 -->
          <a-dropdown>
            <span class="user-dropdown">
              <a-avatar :size="32" icon="user" />
              <span class="username">{{ user?.username }}</span>
            </span>
            <template #overlay>
              <a-menu>
                <a-menu-item key="1">
                  <user-outlined />
                  个人中心
                </a-menu-item>
                <a-menu-item key="2">
                  <setting-outlined />
                  账号设置
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item key="3" @click="handleLogout">
                  <logout-outlined />
                  退出登录
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>
      
      <!-- 内容区域 -->
      <a-layout-content class="content">
        <div class="content-container">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </a-layout-content>
      
      <!-- 页脚 -->
      <a-layout-footer class="footer">
        DSP广告管理系统 ©{{ new Date().getFullYear() }} Created by Your Company
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  MenuUnfoldOutlined, 
  MenuFoldOutlined,
  DashboardOutlined,
  TeamOutlined,
  FundOutlined,
  PictureOutlined,
  BarChartOutlined,
  SettingOutlined,
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
  NotificationOutlined,
  CheckOutlined
} from '@ant-design/icons-vue'
import { useUserStore } from '@/store/user'

export default defineComponent({
  name: 'BasicLayout',
  components: {
    MenuUnfoldOutlined,
    MenuFoldOutlined,
    DashboardOutlined,
    TeamOutlined,
    FundOutlined,
    PictureOutlined,
    BarChartOutlined,
    SettingOutlined,
    BellOutlined,
    UserOutlined,
    LogoutOutlined,
    NotificationOutlined,
    CheckOutlined
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const userStore = useUserStore()
    
    // 登录状态和用户信息
    const user = computed(() => userStore.user)
    
    // 菜单折叠状态
    const collapsed = ref(false)
    
    // 当前选中的菜单项
    const selectedKeys = ref<string[]>([])
    
    // 通知数量
    const notificationCount = ref(5)
    
    // 菜单配置
    const menuItems = [
      {
        key: 'dashboard',
        title: '仪表盘',
        path: '/dashboard',
        icon: 'DashboardOutlined'
      },
      {
        key: 'advertisers',
        title: '广告主管理',
        path: '/advertisers',
        icon: 'TeamOutlined'
      },
      {
        key: 'campaigns',
        title: '广告活动',
        path: '/campaigns',
        icon: 'FundOutlined'
      },
      {
        key: 'creatives',
        title: '创意管理',
        path: '/creatives',
        icon: 'PictureOutlined'
      },
      {
        key: 'reports',
        title: '报表分析',
        path: '/reports',
        icon: 'BarChartOutlined',
        children: [
          {
            key: 'reports-performance',
            title: '效果报表',
            path: '/reports/performance'
          },
          {
            key: 'reports-custom',
            title: '自定义报表',
            path: '/reports/custom'
          }
        ]
      },
      {
        key: 'settings',
        title: '系统设置',
        path: '/settings',
        icon: 'SettingOutlined',
        children: [
          {
            key: 'settings-users',
            title: '用户管理',
            path: '/settings/users'
          },
          {
            key: 'settings-roles',
            title: '角色权限',
            path: '/settings/roles'
          }
        ]
      }
    ]
    
    // 面包屑
    const breadcrumbs = computed(() => {
      const pathArray = route.path.split('/').filter(Boolean)
      const result = [{ title: '首页', path: '/' }]
      
      if (pathArray.length > 0) {
        let currentPath = ''
        
        pathArray.forEach(path => {
          currentPath += `/${path}`
          const matchedRoute = router.getRoutes().find(route => route.path === currentPath)
          
          if (matchedRoute && matchedRoute.meta.title) {
            result.push({
              title: matchedRoute.meta.title as string,
              path: currentPath
            })
          }
        })
      }
      
      return result
    })
    
    // 根据路由更新选中的菜单项
    watch(
      () => route.path,
      (path) => {
        // 提取路径的第一级作为主菜单key
        const mainPath = path.split('/')[1]
        if (mainPath) {
          selectedKeys.value = [mainPath]
          
          // 如果是子路径，还需要选中子菜单
          if (path.split('/').length > 2) {
            const subPath = path.split('/').slice(0, 3).join('/')
            const subKey = menuItems.flatMap(item => item.children || [])
              .find(child => child.path === subPath)?.key
              
            if (subKey) {
              selectedKeys.value = [subKey]
            }
          }
        }
      },
      { immediate: true }
    )
    
    // 退出登录
    const handleLogout = () => {
      userStore.logout()
      router.push('/login')
    }
    
    // 在组件挂载时验证token
    onMounted(() => {
      if (userStore.token) {
        userStore.verifyToken().catch(() => {
          router.push('/login')
        })
      }
    })
    
    return {
      collapsed,
      selectedKeys,
      menuItems,
      breadcrumbs,
      user,
      notificationCount,
      handleLogout
    }
  }
})
</script>

<style lang="less" scoped>
.layout {
  min-height: 100vh;
}

.sider {
  .logo {
    height: 64px;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #002140;
    overflow: hidden;
    
    h1 {
      color: #fff;
      font-size: 18px;
      margin: 0;
      white-space: nowrap;
    }
  }
}

.header {
  background: #fff;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 1;
  
  .header-left {
    display: flex;
    align-items: center;
    
    .trigger {
      font-size: 18px;
      padding: 0 24px;
      cursor: pointer;
      transition: color 0.3s;
      
      &:hover {
        color: #1890ff;
      }
    }
    
    .breadcrumb {
      margin-left: 16px;
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    padding-right: 24px;
    
    .action-icon {
      padding: 0 12px;
      font-size: 18px;
      cursor: pointer;
      
      &:hover {
        color: #1890ff;
      }
    }
    
    .user-dropdown {
      display: flex;
      align-items: center;
      padding: 0 12px;
      cursor: pointer;
      
      .username {
        margin-left: 8px;
      }
      
      &:hover {
        color: #1890ff;
      }
    }
  }
}

.content {
  margin: 24px;
  
  .content-container {
    padding: 24px;
    background: #fff;
    min-height: 280px;
  }
}

.footer {
  text-align: center;
  padding: 16px 50px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 