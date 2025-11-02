import axios from 'axios'

const API_BASE_URL = '/api'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Services API
export const servicesAPI = {
  getAll: () => api.get('/services'),
  getById: (id) => api.get(`/services/${id}`),
}

// Contact API
export const contactAPI = {
  submit: (data) => api.post('/contact', data),
  getMessages: () => api.get('/contact/messages'),
}

// Health check
export const healthCheck = () => api.get('/health')

export default api
