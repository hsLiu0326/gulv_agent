import { defineStore } from 'pinia'
import api from '@/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token
  },

  actions: {
    async login(credentials) {
      const response = await api.auth.login(credentials)
      this.token = response.access_token
      localStorage.setItem('token', this.token)
      // 登录成功后获取用户信息，失败不影响登录流程
      try {
        await this.fetchUserInfo()
      } catch (error) {
        console.warn('获取用户信息失败，将在进入控制台后重试:', error)
      }
    },

    async fetchUserInfo() {
      const response = await api.auth.me()
      this.userInfo = response
    },

    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
    }
  }
})