<template>
  <div>
    <el-breadcrumb separator="/" class="mb-4">
      <el-breadcrumb-item :to="{ path: '/health-reports' }">健康报告</el-breadcrumb-item>
      <el-breadcrumb-item>{{ report.report_name }}</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card v-loading="loading">
      <template #header>
        <h2 class="text-xl font-bold">{{ report.report_name }}</h2>
      </template>

      <el-row :gutter="20" class="mb-6">
        <el-col :span="4">
          <el-statistic title="血糖" :value="report.blood_glucose" suffix="mmol/L">
            <template #prefix>🩸</template>
          </el-statistic>
        </el-col>
        <el-col :span="4">
          <el-statistic title="收缩压" :value="report.blood_pressure_systolic" suffix="mmHg">
            <template #prefix>❤️</template>
          </el-statistic>
        </el-col>
        <el-col :span="4">
          <el-statistic title="舒张压" :value="report.blood_pressure_diastolic" suffix="mmHg">
            <template #prefix>💓</template>
          </el-statistic>
        </el-col>
        <el-col :span="4">
          <el-statistic title="尿酸" :value="report.uric_acid" suffix="μmol/L">
            <template #prefix>🧪</template>
          </el-statistic>
        </el-col>
        <el-col :span="4">
          <el-statistic title="胆固醇" :value="report.cholesterol" suffix="mmol/L">
            <template #prefix>🫀</template>
          </el-statistic>
        </el-col>
        <el-col :span="4">
          <el-statistic title="甘油三酯" :value="report.triglycerides" suffix="mmol/L">
            <template #prefix>💉</template>
          </el-statistic>
        </el-col>
      </el-row>

      <el-divider>报告内容</el-divider>
      <p class="text-gray-600 whitespace-pre-wrap">{{ report.report_content }}</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const loading = ref(false)
const report = ref({})

const fetchReport = async () => {
  loading.value = true
  try {
    const response = await api.healthReports.get(route.params.id)
    report.value = response
  } catch (error) {
    console.error('获取报告详情失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(fetchReport)
</script>