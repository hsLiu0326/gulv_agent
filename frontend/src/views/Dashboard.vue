<template>​
  <div>​
          <div class="text-4xl mb-2">❤️</div>​
          <div class="text-3xl font-bold text-blue-500">{{ stats.preferences }}</div>​
          <div class="text-gray-500">口味偏好</div>​
        </el-card>​
      </el-col>​
    </el-row>​
    ​
    <!-- 快捷操作 -->​
    <el-card>​
      <template #header>​
        <span class="font-bold">快捷操作</span>​
      </template>​
      <div class="flex gap-4">​
        <el-button type="primary" size="large" @click="$router.push('/health-reports')">​
          📤 上传体检报告​
        </el-button>​
        <el-button type="success" size="large" @click="$router.push('/recipes')">​
          🍎 生成食谱​
        </el-button>​
        <el-button type="warning" size="large" @click="$router.push('/preferences')">​
          ⚙️ 设置偏好​
        </el-button>​
      </div>​
    </el-card>​
  </div>​
</template>​
​
<script setup>​
import { ref, onMounted } from 'vue'​
import api from '@/api'​
​
const stats = ref({​
  reports: 0,​
  recipes: 0,​
  preferences: 0​
})​
​
const fetchStats = async () => {​
  try {​
    const [reports, recipes, preferences] = await Promise.all([​
      api.healthReports.list(),​
      api.recipes.list(),​
      api.preferences.list()​
    ])​
    stats.value = {​
      reports: reports.data.length,​
      recipes: recipes.data.length,​
      preferences: preferences.data.length​
    }​
  } catch (error) {​
    console.error('获取统计数据失败:', error)​
  }​
}​
​
onMounted(fetchStats)​
</script>