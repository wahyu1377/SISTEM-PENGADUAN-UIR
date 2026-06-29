import { defineStore } from 'pinia'
import { authService } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin'
  },

  actions: {
    async login(credentials) {
      const response = await authService.login(credentials)
      this.token = response.data.access_token
      this.user = response.data.user
      localStorage.setItem('token', this.token)
      return response
    },

    async register(data) {
      const response = await authService.register(data)
      this.token = response.data.access_token
      this.user = response.data.user
      localStorage.setItem('token', this.token)
      return response
    },

    logout() {
      // Clear state synchronously
      this.user = null
      this.token = null
      localStorage.removeItem('token')
    },

    async checkAuth() {
      if (!this.token) {
        return false
      }
      try {
        const response = await authService.getMe()
        this.user = response.data
        return true
      } catch (e) {
        // Token invalid or expired - clear auth
        this.logout()
        return false
      }
    }
  }
})
