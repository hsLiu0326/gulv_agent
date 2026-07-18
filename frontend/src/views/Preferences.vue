<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">口味偏好</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon class="mr-2"><Plus /></el-icon>
        添加偏好
      </el-button>
    </div>

    <el-card v-loading="loading">
      <el-table :data="preferences" stripe style="width: 100%">
        <el-table-column prop="preference_type" label="类型">
          <template #default="{ row }">
            <el-tag>{{ getTypeLabel(row.preference_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="preference_value" label="内容" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="添加偏好" width="400px">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="类型" required>
          <el-select v-model="addForm.preference_type" class="w-full">
            <el-option label="喜欢的食物" value="favorite_food" />
            <el-option label="不喜欢的食物" value="disliked_food" />
            <el-option label="菜系偏好" value="cuisine" />
            <el-option label="过敏食物" value="allergy" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="addForm.preference_value" placeholder="请输入偏好内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="adding" @click="handleAdd">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const loading = ref(false)
const adding = ref(false)
const preferences = ref([])
const showAddDialog = ref(false)

const addForm = reactive({
  preference_type: '',
  preference_value: ''
})

const fetchPreferences = async () => {
  loading.value = true
  try {
    const response = await api.preferences.list()
    preferences.value = response
  } catch (error) {
    console.error('获取偏好列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleAdd = async () => {
  if (!addForm.preference_type || !addForm.preference_value) {
    ElMessage.warning('请填写完整信息')
    return
  }

  adding.value = true
  try {
    await api.preferences.create(addForm)
    ElMessage.success('添加成功')
    showAddDialog.value = false
    addForm.preference_type = ''
    addForm.preference_value = ''
    await fetchPreferences()
  } catch (error) {
    console.error('添加失败:', error)
  } finally {
    adding.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await api.preferences.delete(id)
    ElMessage.success('删除成功')
    await fetchPreferences()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const getTypeLabel = (type) => {
  const labels = {
    favorite_food: '喜欢的食物',
    disliked_food: '不喜欢的食物',
    cuisine: '菜系偏好',
    allergy: '过敏食物'
  }
  return labels[type] || type
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(fetchPreferences)
</script>