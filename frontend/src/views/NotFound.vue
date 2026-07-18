<template>
  <div class="flex flex-col items-center justify-center min-h-screen">
    <div class="text-8xl mb-4">404</div>
    <h1 class="text-2xl font-bold text-gray-800 mb-2">页面未找到</h1>
    <p class="text-gray-500 mb-6">您访问的页面不存在</p>
    <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
  </div>
</template>

<script setup>
</script>