import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use(
  (config) => {
    if (config.headers?.skipAuth) {
      delete config.headers.skipAuth
      return config
    }
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

let redirectingToLogin = false

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || '请求失败'
    if (error.response?.status === 401) {
      const currentRoute = router.currentRoute?.value
      const isAuthPage = currentRoute?.name === 'Login' || currentRoute?.name === 'Register'
      if (!isAuthPage && !redirectingToLogin) {
        redirectingToLogin = true
        localStorage.removeItem('token')
        ElMessage.error('登录已过期，请重新登录')
        router.push('/login').finally(() => {
          redirectingToLogin = false
        })
      }
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

const api = {
  auth: {
    login: (data) => apiClient.post('/auth/login', new URLSearchParams(data), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', skipAuth: true }
    }),
    register: (data) => apiClient.post('/auth/register', data, {
      headers: { skipAuth: true }
    }),
    me: () => apiClient.get('/users/me')
  },
  healthReports: {
    list: () => apiClient.get('/health-reports'),
    get: (id) => apiClient.get(`/health-reports/${id}`),
    create: (data) => apiClient.post('/health-reports', data)
  },
  recipes: {
    list: () => apiClient.get('/recipes'),
    get: (id) => apiClient.get(`/recipes/${id}`),
    generate: (data) => apiClient.post('/recipes/generate', data)
  },
  preferences: {
    list: () => apiClient.get('/preferences'),
    create: (data) => apiClient.post('/preferences', data),
    delete: (id) => apiClient.delete(`/preferences/${id}`)
  },
  dailyMenus: {
    list: () => apiClient.get('/daily-menus'),
    get: (id) => apiClient.get(`/daily-menus/${id}`),
    create: (data) => apiClient.post('/daily-menus', data),
    delete: (id) => apiClient.delete(`/daily-menus/${id}`)
  },
  knowledge: {
    query: (data) => apiClient.post('/knowledge/query', data)
  }
}

export default api