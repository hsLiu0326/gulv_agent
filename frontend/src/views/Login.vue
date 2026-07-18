<template>​
  <div class="min-h-screen bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">​
            size="large"​
            class="w-full"​
            :loading="loading"​
            @click="handleLogin"​
          >​
            登录​
          </el-button>​
        </el-form-item>​
      </el-form>​
      ​
      <div class="text-center text-gray-500">​
        还没有账号？​
        <router-link to="/register" class="text-emerald-600 hover:underline">​
          立即注册​
        </router-link>​
      </div>​
    </el-card>​
  </div>​
</template>​
​
<script setup>​
import { ref, reactive } from 'vue'​
import { useRouter } from 'vue-router'​
import { useUserStore } from '@/stores/user'​
import { ElMessage } from 'element-plus'​
​
const router = useRouter()​
const userStore = useUserStore()​
const formRef = ref(null)​
const loading = ref(false)​
​
const loginForm = reactive({​
  username: '',​
  password: ''​
})​
​
const rules = {​
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],​
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]​
}​
​
const handleLogin = async () => {​
  await formRef.value.validate()​
  loading.value = true​
  try {​
    await userStore.login(loginForm)​
    ElMessage.success('登录成功')​
    router.push('/')​
  } catch (error) {​
    console.error('登录失败:', error)​
  } finally {​
    loading.value = false​
  }​
}​
</script>