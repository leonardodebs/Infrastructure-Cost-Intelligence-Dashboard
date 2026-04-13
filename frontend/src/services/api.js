import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const login = async (username, password) => {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)
  const response = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return response.data
}

export const getDashboard = () => api.get('/costs/dashboard')
export const getDailyTrend = (days) => api.get(`/costs/daily-trend?days=${days}`)
export const getCostsByService = (startDate, endDate) =>
  api.get(`/costs/by-service?start_date=${startDate}&end_date=${endDate}`)
export const getAnomalies = (days) => api.get(`/costs/anomalies?days=${days}`)
export const getForecast = () => api.get('/costs/forecast')
export const getTagCompliance = () => api.get('/costs/tag-compliance')
export const exportCsv = () => api.get('/costs/export-csv', { responseType: 'blob' })

export default api
