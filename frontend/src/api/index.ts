import axios from 'axios'
import { useUserStore } from '@/store/user'
import { message } from 'ant-design-vue'
import router from '@/router'

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    const token = userStore.token

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => response,
  async error => {
    const { response } = error

    if (response) {
      switch (response.status) {
        case 401:
          // Token 过期或无效
          const userStore = useUserStore()
          userStore.logout()
          message.error('登录已过期，请重新登录')
          window.location.href = '/login'
          break
        case 403:
          message.error('没有权限执行此操作')
          break
        case 422:
          // 验证错误
          const errorMsg = response.data.error || '请求参数错误'
          message.error(errorMsg)
          break
        default:
          message.error(response.data.error || '服务器错误')
      }
    } else {
      message.error('网络错误，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

// API模块
export const api = {
  // 认证相关API
  auth: {
    login: (data: { username: string; password: string }) => 
      request.post('/auth/login', data),
    verify: () => 
      request.get('/auth/verify'),
    refreshCsrfToken: () => 
      request.get('/auth/csrf-token')
  },
  
  // 广告主相关API
  advertisers: {
    list: (params?: any) => 
      request.get('/v1/advertisers', { params }),
    getById: (id: number) => 
      request.get(`/v1/advertisers/${id}`),
    create: (data: any) => 
      request.post('/v1/advertisers', data),
    update: (id: number, data: any) => 
      request.put(`/v1/advertisers/${id}`, data),
    changeStatus: (id: number, data: { status: string; reason?: string }) => 
      request.put(`/v1/advertisers/${id}/status`, data),
    uploadFile: (id: number, file: File, fileType: string) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('file_type', fileType)
      return request.post(`/v1/advertisers/${id}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    },
    deposit: (id: number, data: { amount: number; transaction_id: string }) => 
      request.post(`/v1/advertisers/${id}/deposit`, data),
    withdraw: (id: number, data: { amount: number; transaction_id: string }) => 
      request.post(`/v1/advertisers/${id}/withdraw`, data)
  },
  
  // 广告活动相关API
  campaigns: {
    list: (params?: any) => 
      request.get('/v1/campaigns', { params }),
    getById: (id: number) => 
      request.get(`/v1/campaigns/${id}`),
    create: (data: any) => 
      request.post('/v1/campaigns', data),
    update: (id: number, data: any) => 
      request.put(`/v1/campaigns/${id}`, data),
    changeStatus: (id: number, data: { status: string }) => 
      request.put(`/v1/campaigns/${id}/status`, data),
    getStatistics: (id: number, params: any) => 
      request.get(`/v1/campaigns/${id}/statistics`, { params })
  },
  
  // 创意相关API
  creatives: {
    list: (params?: any) => 
      request.get('/v1/creatives', { params }),
    getById: (id: number) => 
      request.get(`/v1/creatives/${id}`),
    create: (data: any) => 
      request.post('/v1/creatives', data),
    update: (id: number, data: any) => 
      request.put(`/v1/creatives/${id}`, data),
    uploadContent: (id: number, file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return request.post(`/v1/creatives/${id}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    },
    review: (id: number, data: { status: string; reason?: string }) => 
      request.put(`/v1/creatives/${id}/review`, data)
  },
  
  // 报表相关API
  reports: {
    getPerformance: (params: any) => 
      request.get('/v1/reports/performance', { params }),
    getCustom: (params: any) => 
      request.get('/v1/reports/custom', { params }),
    createJob: (data: any) => 
      request.post('/v1/reports/jobs', data),
    getJobById: (id: number) => 
      request.get(`/v1/reports/jobs/${id}`),
    listJobs: (params?: any) => 
      request.get('/v1/reports/jobs', { params })
  },
  
  // 用户管理API
  users: {
    list: (params?: any) => 
      request.get('/v1/users', { params }),
    getById: (id: number) => 
      request.get(`/v1/users/${id}`),
    create: (data: any) => 
      request.post('/v1/users', data),
    update: (id: number, data: any) => 
      request.put(`/v1/users/${id}`, data),
    changePassword: (id: number, data: { old_password: string; new_password: string }) => 
      request.put(`/v1/users/${id}/password`, data),
    getRoles: () => 
      request.get('/v1/users/roles')
  }
}

export default request 