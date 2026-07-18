<template>​
  <el-container class="min-h-screen">​
        </el-menu-item>​
        <el-menu-item index="/health-reports" class="text-white hover:bg-emerald-600">​
          <el-icon><Document /></el-icon>​
          <span>健康报告</span>​
        </el-menu-item>​
        <el-menu-item index="/recipes" class="text-white hover:bg-emerald-600">​
          <el-icon><Food /></el-icon>​
          <span>我的食谱</span>​
        </el-menu-item>​
        <el-menu-item index="/preferences" class="text-white hover:bg-emerald-600">​
          <el-icon><Setting /></el-icon>​
          <span>口味偏好</span>​
        </el-menu-item>​
      </el-menu>​
    </el-aside>​
    ​
    <!-- 主内容区 -->​
    <el-container>​
      <el-header class="bg-white border-b flex items-center justify-between px-6">​
        <div></div>​
        <div class="flex items-center gap-4">​
          <span class="text-gray-600">{{ userStore.userInfo?.username }}</span>​
          <el-button text @click="handleLogout">退出登录</el-button>​
        </div>​
      </el-header>​
      <el-main class="bg-gray-50 p-6">​
        <router-view />​
      </el-main>​
    </el-container>​
  </el-container>​
</template>​
​
<script setup>​
import { computed } from 'vue'​
import { useRoute, useRouter } from 'vue-router'​
import { useUserStore } from '@/stores/user'​
import { HomeFilled, Document, Food, Setting } from '@element-plus/icons-vue'​
​
const route = useRoute()​
const router = useRouter()​
const userStore = useUserStore()​
​
const activeMenu = computed(() => route.path)​
​
const handleLogout = () => {​
  userStore.logout()​
  router.push('/login')​
}​
</script>