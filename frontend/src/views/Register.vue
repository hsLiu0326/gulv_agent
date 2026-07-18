<template>​
  <div class="min-h-screen bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">​
import { ElMessage } from 'element-plus'​
​
const router = useRouter()​
const formRef = ref(null)​
const loading = ref(false)​
​
const registerForm = reactive({​
  username: '',​
  email: '',​
  password: '',​
  confirmPassword: ''​
})​
​
const validateConfirmPassword = (rule, value, callback) => {​
  if (value !== registerForm.password) {​
    callback(new Error('两次密码输入不一致'))​
  } else {​
    callback()​
  }​
}​
​
const rules = {​
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],​
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],​
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],​
  confirmPassword: [{ required: true, message: '请确认密码', trigger: 'blur' }, { validator: validateConfirmPassword, trigger: 'blur' }]​
}​
​
const handleRegister = async () => {​
  await formRef.value.validate()​
  loading.value = true​
  try {​
    await api.auth.register({​
      username: registerForm.username,​
      email: registerForm.email,​
      password: registerForm.password​
    })​
    ElMessage.success('注册成功，请登录')​
    router.push('/login')​
  } catch (error) {​
    console.error('注册失败:', error)​
  } finally {​
    loading.value = false​
  }​
}​
</script>