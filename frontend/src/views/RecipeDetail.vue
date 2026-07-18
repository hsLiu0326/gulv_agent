<template>
  <div>
    <el-breadcrumb separator="/" class="mb-4">
      <el-breadcrumb-item :to="{ path: '/recipes' }">食谱管理</el-breadcrumb-item>
      <el-breadcrumb-item>{{ recipe.name }}</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card v-loading="loading">
      <template #header>
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-bold">{{ recipe.name }}</h2>
          <el-tag :type="recipe.status === 'active' ? 'success' : 'info'">
            {{ recipe.status === 'active' ? '进行中' : '已完成' }}
          </el-tag>
        </div>
      </template>

      <el-statistic title="总热量" :value="recipe.total_calories" suffix="kcal" class="mb-6">
        <template #prefix>🔥</template>
      </el-statistic>

      <el-divider>食谱描述</el-divider>
      <p class="text-gray-600 whitespace-pre-wrap">{{ recipe.description }}</p>

      <el-divider>营养信息</el-divider>
      <el-descriptions :column="4" border>
        <el-descriptions-item label="热量">{{ recipe.nutrition_info?.calories || '-' }}</el-descriptions-item>
        <el-descriptions-item label="蛋白质">{{ recipe.nutrition_info?.protein || '-' }}g</el-descriptions-item>
        <el-descriptions-item label="碳水">{{ recipe.nutrition_info?.carbs || '-' }}g</el-descriptions-item>
        <el-descriptions-item label="脂肪">{{ recipe.nutrition_info?.fat || '-' }}g</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const loading = ref(false)
const recipe = ref({})

const fetchRecipe = async () => {
  loading.value = true
  try {
    const response = await api.recipes.get(route.params.id)
    recipe.value = response
  } catch (error) {
    console.error('获取食谱详情失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(fetchRecipe)
</script>