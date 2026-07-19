<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">每日膳食规划</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon class="mr-2"><Plus /></el-icon>
        添加菜单
      </el-button>
    </div>

    <el-card v-loading="loading">
      <el-table :data="menus" stripe style="width: 100%">
        <el-table-column prop="menu_date" label="日期">
          <template #default="{ row }">
            {{ formatDate(row.menu_date) }}
          </template>
        </el-table-column>
        <el-table-column label="总热量(kcal)" width="120">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.total_calories }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="营养成分" width="300">
          <template #default="{ row }">
            <div class="flex gap-4 text-sm">
              <span>蛋白质: {{ row.total_protein }}g</span>
              <span>碳水: {{ row.total_carbohydrate }}g</span>
              <span>脂肪: {{ row.total_fat }}g</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" />
        <el-table-column label="餐次" width="150">
          <template #default="{ row }">
            <el-tag size="small" v-for="meal in row.meals" :key="meal.id" class="mr-1">
              {{ getMealTypeLabel(meal.meal_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewMenu(row)">查看详情</el-button>
            <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="添加每日菜单" width="600px">
      <el-form :model="addForm" label-width="100px">
        <el-form-item label="日期">
          <el-date-picker v-model="addForm.menu_date" type="date" class="w-full" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="addForm.notes" placeholder="可选备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="adding" @click="handleAdd">添加</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="菜单详情" width="800px">
      <div v-if="currentMenu">
        <div class="mb-4">
          <h3 class="text-lg font-bold">{{ formatDate(currentMenu.menu_date) }} 的膳食安排</h3>
          <p v-if="currentMenu.notes" class="text-gray-500">{{ currentMenu.notes }}</p>
        </div>
        <div class="grid grid-cols-4 gap-4 mb-4">
          <el-card shadow="hover">
            <div class="text-2xl font-bold text-emerald-600">{{ currentMenu.total_calories }}</div>
            <div class="text-gray-500">总热量(kcal)</div>
          </el-card>
          <el-card shadow="hover">
            <div class="text-2xl font-bold text-blue-600">{{ currentMenu.total_protein }}</div>
            <div class="text-gray-500">蛋白质(g)</div>
          </el-card>
          <el-card shadow="hover">
            <div class="text-2xl font-bold text-orange-600">{{ currentMenu.total_carbohydrate }}</div>
            <div class="text-gray-500">碳水化合物(g)</div>
          </el-card>
          <el-card shadow="hover">
            <div class="text-2xl font-bold text-red-600">{{ currentMenu.total_fat }}</div>
            <div class="text-gray-500">脂肪(g)</div>
          </el-card>
        </div>
        <div v-for="meal in currentMenu.meals" :key="meal.id" class="mb-4">
          <el-card>
            <template #header>
              <span class="font-bold">{{ getMealTypeLabel(meal.meal_type) }}</span>
              <span class="text-gray-500 ml-4">目标: {{ meal.target_calories }}kcal / 实际: {{ meal.actual_calories }}kcal</span>
            </template>
            <div v-if="meal.dishes.length > 0">
              <el-table :data="meal.dishes" stripe>
                <el-table-column prop="name" label="菜品" />
                <el-table-column prop="calories" label="热量(kcal)" width="100" />
                <el-table-column prop="description" label="描述" />
              </el-table>
            </div>
            <div v-else class="text-gray-500 text-center py-4">暂无菜品</div>
          </el-card>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
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
const menus = ref([])
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const currentMenu = ref(null)

const addForm = reactive({
  menu_date: '',
  notes: ''
})

const fetchMenus = async () => {
  loading.value = true
  try {
    const response = await api.dailyMenus.list()
    menus.value = response
  } catch (error) {
    console.error('获取菜单列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleAdd = async () => {
  if (!addForm.menu_date) {
    ElMessage.warning('请选择日期')
    return
  }

  adding.value = true
  try {
    await api.dailyMenus.create({
      menu_date: addForm.menu_date,
      notes: addForm.notes,
      meals: []
    })
    ElMessage.success('添加成功')
    showAddDialog.value = false
    addForm.menu_date = ''
    addForm.notes = ''
    await fetchMenus()
  } catch (error) {
    console.error('添加失败:', error)
  } finally {
    adding.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await api.dailyMenus.delete(id)
    ElMessage.success('删除成功')
    await fetchMenus()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const viewMenu = (menu) => {
  currentMenu.value = menu
  showDetailDialog.value = true
}

const getMealTypeLabel = (type) => {
  const labels = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '加餐'
  }
  return labels[type] || type
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(fetchMenus)
</script>