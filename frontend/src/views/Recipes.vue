<template>​
  <div>​
  try {​
    const [recipesRes, reportsRes] = await Promise.all([​
      api.recipes.list(),​
      api.healthReports.list()​
    ])​
    recipes.value = recipesRes.data​
    reports.value = reportsRes.data​
  } catch (error) {​
    console.error('获取数据失败:', error)​
  } finally {​
    loading.value = false​
  }​
}​
​
const handleGenerate = async () => {​
  if (!generateForm.health_report_id) {​
    ElMessage.warning('请选择健康报告')​
    return​
  }​
  ​
  generating.value = true​
  try {​
    await api.recipes.generate(generateForm)​
    ElMessage.success('食谱生成成功！')​
    showGenerateDialog.value = false​
    await fetchData()​
  } catch (error) {​
    console.error('生成失败:', error)​
  } finally {​
    generating.value = false​
  }​
}​
​
const formatDate = (dateStr) => {​
  return new Date(dateStr).toLocaleDateString('zh-CN')​
}​
​
onMounted(fetchData)​
</script>