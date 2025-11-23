// stores/auth.js
import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
    isLoading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    userName: (state) => state.user?.name || 'Usuario'
  },

  actions: {
    async login(credentials) {
      this.isLoading = true
      try {
        const response = await api.post('/auth/login', credentials)
        this.token = response.data.access_token
        this.user = response.data.user
        
        localStorage.setItem('token', this.token)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.detail || 'Error de conexión' 
        }
      } finally {
        this.isLoading = false
      }
    },

    async register(userData) {
      this.isLoading = true
      try {
        const response = await api.post('/auth/register', userData)
        return { success: true, data: response.data }
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Error en el registro'
        }
      } finally {
        this.isLoading = false
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    }
  }
})