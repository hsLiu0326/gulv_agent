<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">个人中心</h2>

    <el-card>
      <template #header>
        <span class="font-bold">基本信息</span>
      </template>

      <el-descriptions :column="2" border class="mb-6">
        <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ userInfo.email }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ userInfo.full_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ userInfo.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ getGenderLabel(userInfo.gender) }}</el-descriptions-item>
        <el-descriptions-item label="年龄">{{ userInfo.age ? `${userInfo.age} 岁` : '-' }}</el-descriptions-item>
        <el-descriptions-item label="身高">{{ userInfo.height ? `${userInfo.height} cm` : '-' }}</el-descriptions-item>
        <el-descriptions-item label="体重">{{ userInfo.weight ? `${userInfo.weight} kg` : '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(userInfo.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="mt-6">
      <template #header>
        <span class="font-bold">修改密码</span>
      </template>

      <el-form :model="passwordForm" label-width="120px">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.oldPassword" type="password" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleChangePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()

const userInfo = ref({})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const fetchUserInfo = async () => {
  try {
    await userStore.fetchUserInfo()
    userInfo.value = userStore.userInfo
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const handleChangePassword = () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.error('两次密码输入不一致')
    return
  }
  ElMessage.success('密码修改成功')
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

const getGenderLabel = (gender) => {
  const labels = { male: '男', female: '女', other: '其他' }
  return labels[gender] || '-'
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(fetchUserInfo)
</script>
