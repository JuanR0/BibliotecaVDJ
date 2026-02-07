import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

const buildUrl = (endpoint) => {
  // Si el endpoint ya empieza con /api/, usarlo como está
  if (endpoint.startsWith('/api/')) {
    return endpoint
  }
  // Si no, agregar /api/
  return `/api${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`
}

// Interceptor para modificar URLs antes de enviar
api.interceptors.request.use(
  (config) => {
    // Construir URL consistente
    config.url = buildUrl(config.url)
    
    // Agregar token si existe
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    console.log('🔗 Request URL:', config.url) // Para debug
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)


// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => {
    console.log('✅ Response from:', response.config.url) // Para debug
    return response
  },
  (error) => {
    console.error('❌ API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data
    })
    
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

// Interceptor para agregar token automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export { api }
export { buildUrl }

export default api