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
      <div class="flex justify-end mt-4" v-if="total > 0">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :total="total"
          :current-page="page"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="showUploadDialog" title="上传体检报告" width="600px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="上传方式">
          <el-radio-group v-model="uploadMode">
            <el-radio-button value="text">粘贴文本</el-radio-button>
            <el-radio-button value="file">上传文件 (.docx/.pdf)</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="报告名称">
          <el-input v-model="uploadForm.report_name" placeholder="选填，默认使用文件名" />
        </el-form-item>
        <el-form-item v-if="uploadMode === 'text'" label="报告内容">
          <el-input v-model="uploadForm.report_content" type="textarea" :rows="10" placeholder="请粘贴体检报告内容..." />
        </el-form-item>
        <el-form-item v-else label="文件">
          <el-upload
            ref="uploadRef"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".docx,.pdf"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :on-exceed="handleFileExceed"
          >
            <div class="el-upload__text">
              将 .docx / .pdf 文件拖到此处，或<em>点击选择</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">仅支持 .docx / .pdf，文件不超过 10MB</div>
            </template>
          </el-upload>
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
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showUploadDialog = ref(false)
const uploadMode = ref('text')
const uploadRef = ref(null)
const uploadFile = ref(null)

const uploadForm = reactive({
  report_name: '',
  report_content: ''
})

const MAX_FILE_SIZE = 10 * 1024 * 1024

const fetchReports = async () => {
  loading.value = true
  try {
    const response = await api.healthReports.list(page.value, pageSize.value)
    reports.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('获取报告列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (p) => {
  page.value = p
  fetchReports()
}

const handleSizeChange = (s) => {
  pageSize.value = s
  page.value = 1
  fetchReports()
}

const handleUpload = async () => {
  if (uploadMode.value === 'file') {
    if (!uploadFile.value) {
      ElMessage.warning('请先选择 .docx 或 .pdf 文件')
      return
    }
  } else if (!uploadForm.report_name || !uploadForm.report_content) {
    ElMessage.warning('请填写完整信息')
    return
  }

  uploading.value = true
  try {
    if (uploadMode.value === 'file') {
      const formData = new FormData()
      formData.append('file', uploadFile.value)
      if (uploadForm.report_name) {
        formData.append('report_name', uploadForm.report_name)
      }
      await api.healthReports.upload(formData)
    } else {
      await api.healthReports.create(uploadForm)
    }
    ElMessage.success('报告上传成功，正在分析...')
    showUploadDialog.value = false
    uploadForm.report_name = ''
    uploadForm.report_content = ''
    uploadFile.value = null
    uploadRef.value?.clearFiles()
    await fetchReports()
  } catch (error) {
    console.error('上传失败:', error)
  } finally {
    uploading.value = false
  }
}

const handleFileChange = (file) => {
  if (file.raw && file.raw.size > MAX_FILE_SIZE) {
    ElMessage.warning('文件不能超过 10MB')
    uploadRef.value?.clearFiles()
    uploadFile.value = null
    return
  }
  uploadFile.value = file.raw
}

const handleFileRemove = () => {
  uploadFile.value = null
}

const handleFileExceed = () => {
  ElMessage.warning('只能上传一个文件')
  uploadRef.value?.clearFiles()
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
