<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">知识库问答</h2>
    </div>

    <el-card class="mb-6">
      <el-form :model="queryForm" inline>
        <el-form-item>
          <el-input v-model="queryForm.query" placeholder="输入您想查询的营养学问题..." class="w-96" @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="querying" @click="handleQuery">
            <el-icon class="mr-2"><Search /></el-icon>
            查询
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-loading="loading">
      <div v-if="results.length > 0">
        <h3 class="text-lg font-bold mb-4">查询结果</h3>
        <el-timeline>
          <el-timeline-item v-for="(result, index) in results" :key="index" placement="top">
            <el-card shadow="hover">
              <div class="flex justify-between items-start mb-2">
                <el-tag>{{ result.metadata?.category || '营养知识' }}</el-tag>
                <span class="text-xs text-gray-500">{{ result.metadata?.source || '' }}</span>
              </div>
              <p class="text-gray-800 whitespace-pre-wrap">{{ result.content }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
      <div v-else-if="hasQueried" class="text-center py-12">
        <el-empty description="暂无相关知识，请尝试其他关键词" />
      </div>
      <div v-else class="text-center py-12">
        <div class="text-6xl mb-4">📚</div>
        <h3 class="text-lg font-bold text-gray-600 mb-2">营养知识库</h3>
        <p class="text-gray-500">输入您关心的营养学问题，获取专业的饮食建议</p>
        <div class="mt-6 flex flex-wrap justify-center gap-2">
          <el-tag type="info" @click="quickQuery('血糖管理')">血糖管理</el-tag>
          <el-tag type="info" @click="quickQuery('血压管理')">血压管理</el-tag>
          <el-tag type="info" @click="quickQuery('尿酸管理')">尿酸管理</el-tag>
          <el-tag type="info" @click="quickQuery('减脂饮食')">减脂饮食</el-tag>
          <el-tag type="info" @click="quickQuery('膳食纤维')">膳食纤维</el-tag>
          <el-tag type="info" @click="quickQuery('膳食指南')">膳食指南</el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '@/api'
import { Search } from '@element-plus/icons-vue'

const loading = ref(false)
const querying = ref(false)
const hasQueried = ref(false)
const results = ref([])

const queryForm = reactive({
  query: ''
})

const handleQuery = async () => {
  if (!queryForm.query.trim()) {
    return
  }

  querying.value = true
  loading.value = true
  hasQueried.value = true
  try {
    const response = await api.knowledge.query({
      query: queryForm.query,
      n_results: 5
    })
    results.value = response
  } catch (error) {
    console.error('查询失败:', error)
  } finally {
    querying.value = false
    loading.value = false
  }
}

const quickQuery = (keyword) => {
  queryForm.query = keyword
  handleQuery()
}
</script>