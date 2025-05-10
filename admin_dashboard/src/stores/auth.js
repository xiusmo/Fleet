import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const isLoggedIn = ref(!!token.value)

  // 登录
  const login = async (credentials) => {
    try {
      const response = await api.auth.login(credentials)
      token.value = response.data.access_token
      isLoggedIn.value = true
      
      // 保存到本地存储
      localStorage.setItem('token', token.value)
      
      // 获取用户信息
      await fetchUserInfo()
      
      return { success: true }
    } catch (error) {
      console.error('登录失败:', error)
      return { 
        success: false, 
        message: error.response?.data?.detail || '登录失败，请检查用户名和密码'
      }
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    user.value = null
    isLoggedIn.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    if (!token.value) return
    
    try {
      const response = await api.auth.getMe()
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取失败可能是token无效，执行登出
      if (error.response && error.response.status === 401) {
        logout()
      }
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    logout,
    fetchUserInfo
  }
}) 