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
    // FormData 交由浏览器自动设置 multipart boundary，避免默认 JSON 头导致 422
    if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
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
  (response) => {
    if (response.config.rawResponse) {
      return response
    }
    return response.data
  },
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

// 分页列表请求：携带 skip/limit，并从响应头读取总数
const paginatedList = (url, page = 1, pageSize = 20) =>
  apiClient.get(url, {
    params: { skip: (page - 1) * pageSize, limit: pageSize },
    rawResponse: true
  }).then((res) => ({
    items: res.data,
    total: Number(res.headers['x-total-count'] ?? res.data.length)
  }))

// SSE 流式请求：fetch 读取事件流，onEvent 回调收到已解析的事件对象
const ssePost = (url, data, onEvent) => {
  const token = localStorage.getItem('token')
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify(data)
  }).then(async (res) => {
    if (!res.ok) {
      let detail = '请求失败'
      try {
        const err = await res.json()
        detail = err.detail || detail
      } catch (e) { /* ignore */ }
      if (res.status === 401) {
        localStorage.removeItem('token')
        router.push('/login')
      }
      throw new Error(detail)
    }
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''
      for (const line of lines) {
        const trimmed = line.trim()
        if (trimmed.startsWith('data:')) {
          const payload = trimmed.slice(5).trim()
          if (payload) {
            try {
              onEvent(JSON.parse(payload))
            } catch (e) { /* 忽略无法解析的事件 */ }
          }
        }
      }
    }
  })
}

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
    list: (page, pageSize) => paginatedList('/health-reports/', page, pageSize),
    get: (id) => apiClient.get(`/health-reports/${id}`),
    create: (data) => apiClient.post('/health-reports/', data),
    upload: (formData) => apiClient.post('/health-reports/upload', formData)
  },
  recipes: {
    list: (page, pageSize) => paginatedList('/recipes/', page, pageSize),
    get: (id) => apiClient.get(`/recipes/${id}`),
    generate: (data) => apiClient.post('/recipes/generate', data),
    // SSE 流式生成：通过 fetch 读取事件流，onEvent 回调收到 {type: stage/token/result/error}
    generateStream: (data, onEvent) => ssePost('/api/recipes/generate-stream', data, onEvent)
  },
  chat: {
    stream: (data, onEvent) => ssePost('/api/chat/stream', data, onEvent)
  },
  preferences: {
    list: (page, pageSize) => paginatedList('/preferences/', page, pageSize),
    create: (data) => apiClient.post('/preferences/', data),
    delete: (id) => apiClient.delete(`/preferences/${id}`)
  },
  dailyMenus: {
    list: (page, pageSize) => paginatedList('/daily-menus/', page, pageSize),
    get: (id) => apiClient.get(`/daily-menus/${id}`),
    create: (data) => apiClient.post('/daily-menus/', data),
    delete: (id) => apiClient.delete(`/daily-menus/${id}`)
  },
  knowledge: {
    query: (data) => apiClient.post('/knowledge/query', data)
  }
}

export default api
