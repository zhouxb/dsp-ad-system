import { defineStore } from 'pinia'
import { api } from '@/api'
import { message } from 'ant-design-vue'

interface UserState {
  token: string | null
  user: {
    id: number | null
    username: string
    email: string
    fullName: string
    isAdmin: boolean
    advertiserId: number | null
  } | null
  permissions: string[]
  csrfToken: string | null
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('token'),
    user: null,
    permissions: [],
    csrfToken: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    hasPermission: (state) => (permission: string) => {
      if (state.user?.isAdmin) return true
      return state.permissions.includes(permission) || state.permissions.includes('*')
    }
  },

  actions: {
    async login(username: string, password: string) {
      try {
        const response = await api.auth.login({ username, password })
        this.setUserData(response.data)
        return Promise.resolve(response.data)
      } catch (error: any) {
        const errorMsg = error.response?.data?.error || '登录失败'
        message.error(errorMsg)
        return Promise.reject(error)
      }
    },

    async verifyToken() {
      if (!this.token) return Promise.reject('未登录')

      console.log('verifyToken', this.token)

      try {
        const response = await api.auth.verify()
        this.user = response.data.user
        return Promise.resolve(response.data)
      } catch (error: any) {
        console.error('Token verification failed:', error.response?.data || error)
        this.logout()
        return Promise.reject(error)
      }
    },

    setUserData(data: any) {
      this.token = data.access_token
      this.user = data.user
      this.csrfToken = data.csrf_token

      if (data.user.is_superuser) {
        this.permissions = ['*']
      } else {
        this.permissions = data.permissions || []
      }

      // 存储token到localStorage
      localStorage.setItem('token', data.access_token)
    },

    refreshCsrfToken() {
      if (!this.token) return Promise.reject('未登录')

      return api.auth.refreshCsrfToken().then(response => {
        this.csrfToken = response.data.csrf_token
        return response.data.csrf_token
      })
    },

    logout() {
      this.token = null
      this.user = null
      this.permissions = []
      this.csrfToken = null
      localStorage.removeItem('token')
    }
  }
}) 