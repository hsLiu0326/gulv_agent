import axios from 'axios'​
import { ElMessage } from 'element-plus'​
​
const apiClient = axios.create({​
  baseURL: '/api',​
  timeout: 30000,​
  headers: {​
    'Content-Type': 'application/json'​
  }​
})​
​
// 请求拦截器​
apiClient.interceptors.request.use(​
  (config) => {​
    const token = localStorage.getItem('token')​
    if (token) {​
      config.headers.Authorization = `Bearer ${token}`​
    }​
    return config​
  },​
  (error) => Promise.reject(error)​
)​
​
// 响应拦截器​
apiClient.interceptors.response.use(​
  (response) => response.data,​
  (error) => {​
    const message = error.response?.data?.detail || '请求失败'​
    ElMessage.error(message)​
    if (error.response?.status === 401) {​
      localStorage.removeItem('token')​
      window.location.href = '/login'​
    }​
    return Promise.reject(error)​
  }​
)​
​
const api = {​
  auth: {​
    login: (data) => apiClient.post('/auth/login', data),​
    register: (data) => apiClient.post('/auth/register', data),​
    me: () => apiClient.get('/users/me')​
  },​
  healthReports: {​
    list: () => apiClient.get('/health-reports'),​
    get: (id) => apiClient.get(`/health-reports/${id}`),​
    create: (data) => apiClient.post('/health-reports', data)​
  },​
  recipes: {​
    list: () => apiClient.get('/recipes'),​
    get: (id) => apiClient.get(`/recipes/${id}`),​
    generate: (data) => apiClient.post('/recipes/generate', data)​
  },​
  preferences: {​
    list: () => apiClient.get('/preferences'),​
    create: (data) => apiClient.post('/preferences', data),​
    delete: (id) => apiClient.delete(`/preferences/${id}`)​
  }​
}​
​
export default api