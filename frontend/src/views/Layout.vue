<template>
  <el-container class="min-h-screen">
    <el-aside width="200px" class="bg-gray-800">
      <div class="text-white text-xl font-bold p-4">🍎 AI营养师</div>
      <el-menu :default-active="activeMenu" class="bg-gray-800 text-white" router>
        <el-menu-item index="/">
          <el-icon><DashboardIcon /></el-icon>
          <span>控制台</span>
        </el-menu-item>
        <el-menu-item index="/health-reports">
          <el-icon><DocumentIcon /></el-icon>
          <span>健康报告</span>
        </el-menu-item>
        <el-menu-item index="/recipes">
          <el-icon><ListIcon /></el-icon>
          <span>食谱管理</span>
        </el-menu-item>
        <el-menu-item index="/preferences">
          <el-icon><SettingIcon /></el-icon>
          <span>口味偏好</span>
        </el-menu-item>
        <el-menu-item index="/daily-menus">
          <el-icon><CalendarIcon /></el-icon>
          <span>膳食规划</span>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><BookOpenIcon /></el-icon>
          <span>知识库</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><UserIcon /></el-icon>
          <span>个人中心</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="bg-white shadow-sm">
        <div class="flex justify-between items-center">
          <span class="text-gray-800 font-bold">{{ currentTitle }}</span>
          <el-button type="text" @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="bg-gray-50 p-6">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Grid as DashboardIcon, Document as DocumentIcon, List as ListIcon, Setting as SettingIcon, User as UserIcon, Calendar as CalendarIcon, Reading as BookOpenIcon } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const currentTitle = computed(() => {
  const titles = {
    '/': '控制台',
    '/health-reports': '健康报告',
    '/recipes': '食谱管理',
    '/preferences': '口味偏好',
    '/daily-menus': '膳食规划',
    '/knowledge': '知识库',
    '/profile': '个人中心'
  }
  return titles[route.path] || 'AI营养师'
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>