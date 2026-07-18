<template>​
  <div>​
    loading.value = false​
  }​
}​
​
const handleUpload = async () => {​
  if (!uploadForm.report_name || !uploadForm.report_content) {​
    ElMessage.warning('请填写完整信息')​
    return​
  }​
  ​
  uploading.value = true​
  try {​
    await api.healthReports.create(uploadForm)​
    ElMessage.success('报告上传成功，正在分析...')​
    showUploadDialog.value = false​
    uploadForm.report_name = ''​
    uploadForm.report_content = ''​
    await fetchReports()​
  } catch (error) {​
    console.error('上传失败:', error)​
  } finally {​
    uploading.value = false​
  }​
}​
​
const getGlucoseType = (value) => {​
  if (!value) return 'info'​
  if (value < 6.1) return 'success'​
  if (value < 7.0) return 'warning'​
  return 'danger'​
}​
​
const formatDate = (dateStr) => {​
  return new Date(dateStr).toLocaleString('zh-CN')​
}​
​
onMounted(fetchReports)​
</script>