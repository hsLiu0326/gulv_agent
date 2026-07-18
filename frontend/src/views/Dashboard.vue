<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">控制台</h2>

    <el-row :gutter="20" class="mb-6">
      <el-col :span="8">
        <el-card shadow="hover" class="text-center">
          <div class="text-4xl mb-2">📊</div>
          <div class="text-3xl font-bold text-emerald-600">{{ stats.reports }}</div>
          <div class="text-gray-500">健康报告</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="text-center">
          <div class="text-4xl mb-2">🍽️</div>
          <div class="text-3xl font-bold text-orange-500">{{ stats.recipes }}</div>
          <div class="text-gray-500">个性化食谱</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="text-center">
          <div class="text-4xl mb-2">❤️</div>
          <div class="text-3xl font-bold text-blue-500">{{ stats.preferences }}</div>
          <div class="text-gray-500">口味偏好</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>
        <span class="font-bold">快捷操作</span>
      </template>
      <div class="flex gap-4">
        <el-button type="primary" size="large" @click="$router.push('/health-reports')">
          📤 上传体检报告
        </el-button>
        <el-button type="success" size="large" @click="$router.push('/recipes')">
          🍎 生成食谱
        </el-button>
        <el-button type="warning" size="large" @click="$router.push('/preferences')">
          ⚙️ 设置偏好
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const stats = ref({
  reports: 0,
  recipes: 0,
  preferences: 0
})

const fetchStats = async () => {
  try {
    const [reports, recipes, preferences] = await Promise.all([
      api.healthReports.list(),
      api.recipes.list(),
      api.preferences.list()
    ])
    stats.value = {
      reports: reports.length,
      recipes: recipes.length,
      preferences: preferences.length
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

onMounted(fetchStats)
</script>