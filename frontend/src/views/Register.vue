<template>
  <div class="min-h-screen bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">
    <el-card class="w-96" shadow="always">
      <template #header>
        <div class="text-center">
          <h1 class="text-2xl font-bold text-gray-800">🍎 AI营养师</h1>
          <p class="text-gray-500 mt-2">创建新账户</p>
        </div>
      </template>

      <el-form ref="formRef" :model="registerForm" :rules="rules" size="large">
        <el-form-item prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" prefix-icon="Message" />
        </el-form-item>
        <el-form-item prop="phone">
          <el-input v-model="registerForm.phone" placeholder="手机号（选填）" prefix-icon="Phone" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-divider content-position="left" class="!my-3 text-xs text-gray-400">
          身体数据（选填，用于更精准的营养方案）
        </el-divider>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item prop="gender">
              <el-select v-model="registerForm.gender" placeholder="性别" class="w-full">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="age">
              <el-input-number
                v-model="registerForm.age"
                :min="1"
                :max="150"
                placeholder="年龄"
                class="w-full"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item prop="height">
              <el-input-number
                v-model="registerForm.height"
                :min="50"
                :max="300"
                placeholder="身高(cm)"
                class="w-full"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="weight">
              <el-input-number
                v-model="registerForm.weight"
                :min="20"
                :max="500"
                placeholder="体重(kg)"
                class="w-full"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" size="large" class="w-full" :loading="loading" @click="handleRegister">
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="text-center text-gray-500">
        已有账号？
        <router-link to="/login" class="text-emerald-600 hover:underline">立即登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  gender: '',
  age: null,
  height: null,
  weight: null
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次密码输入不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
  confirmPassword: [{ required: true, message: '请确认密码', trigger: 'blur' }, { validator: validateConfirmPassword, trigger: 'blur' }]
}

const handleRegister = async () => {
  const isValid = await formRef.value.validate().catch(() => false)
  if (!isValid) {
    return
  }

  loading.value = true
  try {
    await api.auth.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      phone: registerForm.phone || null,
      gender: registerForm.gender || null,
      age: registerForm.age,
      height: registerForm.height,
      weight: registerForm.weight
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    const detail = error.response?.data?.detail
    if (detail === '用户名已存在') {
      ElMessage.error('该用户名已被注册，请选择其他用户名')
    } else if (detail === '邮箱已被注册') {
      ElMessage.error('该邮箱已被注册，请使用其他邮箱')
    } else {
      ElMessage.error('注册失败，请重试')
    }
  } finally {
    loading.value = false
  }
}
</script>
