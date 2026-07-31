<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">我的食谱</h2>
      <el-button type="primary" @click="showGenerateDialog = true">
        <el-icon class="mr-2"><MagicStick /></el-icon>
        AI生成食谱
      </el-button>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="8" v-for="recipe in recipes" :key="recipe.id" class="mb-4">
        <el-card shadow="hover" class="h-full">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold">{{ recipe.name }}</span>
              <el-tag :type="recipe.status === 'active' ? 'success' : 'info'">
                {{ recipe.status === 'active' ? '进行中' : '已完成' }}
              </el-tag>
            </div>
          </template>
          <p class="text-gray-600 text-sm mb-4 line-clamp-3">{{ recipe.description }}</p>
          <div class="flex justify-between items-center text-sm text-gray-500 mb-4">
            <span>🔥 {{ recipe.total_calories }} kcal</span>
            <span>{{ formatDate(recipe.created_at) }}</span>
          </div>
          <el-button type="primary" plain class="w-full" @click="$router.push(`/recipes/${recipe.id}`)">
            查看详情
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <div class="flex justify-end mt-4" v-if="total > 0">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next"
        :total="total"
        :current-page="page"
        :page-size="pageSize"
        :page-sizes="[6, 12, 24]"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>

    <el-empty v-if="!loading && recipes.length === 0" description="暂无食谱">
      <el-button type="primary" @click="showGenerateDialog = true">生成第一个食谱</el-button>
    </el-empty>

    <el-dialog v-model="showGenerateDialog" title="AI生成个性化食谱" width="500px">
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="选择报告" required>
          <el-select v-model="generateForm.health_report_id" placeholder="请选择健康报告" class="w-full">
            <el-option v-for="report in reports" :key="report.id" :label="report.report_name" :value="report.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="handleGenerate">开始生成</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="genDialogVisible"
      title="AI 正在生成食谱"
      width="560px"
      :close-on-click-modal="false"
      :show-close="false"
    >
      <div class="flex items-center text-gray-600 mb-3">
        <el-icon class="is-loading mr-2"><Loading /></el-icon>
        {{ genStage || '准备中...' }}
      </div>
      <el-scrollbar max-height="320px">
        <div class="bg-gray-50 rounded p-4 text-sm whitespace-pre-wrap">{{ genText }}</div>
      </el-scrollbar>
      <template #footer>
        <el-button type="primary" :loading="generating">生成中...</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'
import { Loading, MagicStick } from '@element-plus/icons-vue'

const loading = ref(false)
const generating = ref(false)
const recipes = ref([])
const reports = ref([])
const page = ref(1)
const pageSize = ref(6)
const total = ref(0)
const showGenerateDialog = ref(false)
const genDialogVisible = ref(false)
const genStage = ref('')
const genText = ref('')

const generateForm = reactive({
  health_report_id: null
})

const fetchData = async () => {
  loading.value = true
  try {
    const [recipesRes, reportsRes] = await Promise.all([
      api.recipes.list(page.value, pageSize.value),
      api.healthReports.list(1, 100)
    ])
    recipes.value = recipesRes.items
    total.value = recipesRes.total
    reports.value = reportsRes.items
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (p) => {
  page.value = p
  fetchData()
}

const handleSizeChange = (s) => {
  pageSize.value = s
  page.value = 1
  fetchData()
}

const handleGenerate = async () => {
  if (!generateForm.health_report_id) {
    ElMessage.warning('请选择健康报告')
    return
  }

  generating.value = true
  showGenerateDialog.value = false
  genStage.value = ''
  genText.value = ''
  genDialogVisible.value = true
  try {
    await api.recipes.generateStream(generateForm, (event) => {
      if (event.type === 'stage') {
        genStage.value = event.message
      } else if (event.type === 'token') {
        genText.value += event.content
      } else if (event.type === 'result') {
        ElMessage.success('食谱生成成功！')
        genDialogVisible.value = false
        fetchData()
      } else if (event.type === 'error') {
        ElMessage.error(event.message || '生成失败')
        genDialogVisible.value = false
      }
    })
  } catch (error) {
    ElMessage.error(error.message || '生成失败')
    genDialogVisible.value = false
  } finally {
    generating.value = false
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(fetchData)
</script>
