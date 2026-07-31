import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'health-reports', name: 'HealthReports', component: () => import('@/views/HealthReports.vue') },
      { path: 'health-reports/:id', name: 'HealthReportDetail', component: () => import('@/views/HealthReportDetail.vue') },
      { path: 'preferences', name: 'Preferences', component: () => import('@/views/Preferences.vue') },
      { path: 'daily-menus', name: 'DailyMenus', component: () => import('@/views/DailyMenus.vue') },
      { path: 'knowledge', name: 'KnowledgeBase', component: () => import('@/views/KnowledgeBase.vue') },
      { path: 'chat', name: 'Chat', component: () => import('@/views/Chat.vue') },
      { path: 'recipes', name: 'Recipes', component: () => import('@/views/Recipes.vue') },
      { path: 'recipes/:id', name: 'RecipeDetail', component: () => import('@/views/RecipeDetail.vue') },
      { path: 'profile', name: 'Profile', component: () => import('@/views/Profile.vue') }
    ]
  },
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('@/views/Register.vue') },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFound.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!token && !['Login', 'Register'].includes(to.name)) {
    next('/login')
  } else {
    next()
  }
})

export default router
