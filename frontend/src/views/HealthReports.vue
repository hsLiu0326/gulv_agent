<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">健康报告</h2>
      <el-button type="primary" @click="showUploadDialog = true">
        <el-icon class="mr-2"><Upload /></el-icon>
        上传报告
      </el-button>
    </div>

    <el-card v-loading="loading">
      <el-table :data="reports" stripe style="width: 100%">
        <el-table-column prop="report_name" label="报告名称" />
        <el-table-column label="血糖(mmol/L)" width="120">
          <template #default="{ row }">
            <el-tag :type="getGlucoseType(row.blood_glucose)">
              {{ row.blood_glucose || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="血压(mmHg)" width="140">
          <template #default="{ row }">
            {{ row.blood_pressure_systolic }}/{{ row.blood_pressure_diastolic }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="$router.push(`/health-reports/${row.id}`)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showUploadDialog" title="上传体检报告" width="600px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="报告名称">
          <el-input v-model="uploadForm.report_name" placeholder="请输入报告名称" />
        </el-form-item>
        <el-form-item label="报告内容">
          <el-input v-model="uploadForm.report_content" type="textarea" :rows="10" placeholder="请粘贴体检报告内容..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传分析</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'

const loading = ref(false)
const uploading = ref(false)
const reports = ref([])
const showUploadDialog = ref(false)

const uploadForm = reactive({
  report_name: '',
  report_content: ''
})

const fetchReports = async () => {
  loading.value = true
  try {
    const response = await api.healthReports.list()
    reports.value = response
  } catch (error) {
    console.error('获取报告列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleUpload = async () => {
  if (!uploadForm.report_name || !uploadForm.report_content) {
    ElMessage.warning('请填写完整信息')
    return
  }

  uploading.value = true
  try {
    await api.healthReports.create(uploadForm)
    ElMessage.success('报告上传成功，正在分析...')
    showUploadDialog.value = false
    uploadForm.report_name = ''
    uploadForm.report_content = ''
    await fetchReports()
  } catch (error) {
    console.error('上传失败:', error)
  } finally {
    uploading.value = false
  }
}

const getGlucoseType = (value) => {
  if (!value) return 'info'
  if (value < 6.1) return 'success'
  if (value < 7.0) return 'warning'
  return 'danger'
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(fetchReports)
</script>