import axios from 'axios'

const baseURL =
  import.meta.env.VITE_API_BASE_URL?.toString() ?? 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

