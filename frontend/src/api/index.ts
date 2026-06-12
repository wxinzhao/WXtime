import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

api.interceptors.response.use(
  response => response,
  error => {
    const detail = error.response?.data?.error || error.response?.data?.errors?.join('; ') || error.message
    console.error('API错误:', error.response?.status, detail)
    return Promise.reject(new Error(detail))
  }
)

export const messageApi = {
  send: (receiver: string, content: string) => api.post('/messages', { receiver, content }),
  list: () => api.get('/messages'),
  delete: (id: number) => api.delete(`/messages/${id}`)
}

export const taskApi = {
  create: (task: any) => api.post('/tasks', task),
  list: () => api.get('/tasks'),
  update: (id: number, task: any) => api.put(`/tasks/${id}`, task),
  delete: (id: number) => api.delete(`/tasks/${id}`)
}

export const statusApi = {
  get: () => api.get('/status')
}