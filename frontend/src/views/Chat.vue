<template>
  <div class="flex flex-col" style="height: calc(100vh - 120px)">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">AI 营养助手</h2>
    <el-card class="flex-1 flex flex-col min-h-0">
      <div ref="msgListRef" class="flex-1 overflow-y-auto pr-2 space-y-4" style="min-height: 0">
        <div v-if="messages.length === 0" class="text-center text-gray-400 py-16">
          输入问题，向 AI 营养师咨询饮食与健康建议
        </div>
        <div
          v-for="(msg, i) in messages"
          :key="i"
          :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'"
        >
          <div
            :class="msg.role === 'user' ? 'bg-emerald-500 text-white' : 'bg-gray-100 text-gray-800'"
            class="max-w-[75%] rounded-lg px-4 py-2 whitespace-pre-wrap text-sm"
          >
            <div v-if="msg.toolInfo" class="text-xs mb-1 text-gray-500">
              🔍 {{ msg.toolInfo }}
            </div>
            {{ msg.content }}
          </div>
        </div>
        <div v-if="streaming" class="flex justify-start">
          <div class="bg-gray-100 text-gray-500 rounded-lg px-4 py-2 text-sm">
            <el-icon class="is-loading"><Loading /></el-icon> 正在回答...
          </div>
        </div>
      </div>
      <div class="pt-3 border-t border-gray-100 mt-3">
        <el-input
          v-model="question"
          type="textarea"
          :rows="2"
          placeholder="例如：高血压饮食要注意什么？"
          @keydown.enter.exact.prevent="handleSend"
        />
        <div class="flex justify-end mt-2">
          <el-button type="primary" :loading="streaming" @click="handleSend">发送</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import api from '@/api'
import { Loading } from '@element-plus/icons-vue'

const messages = ref([])
const question = ref('')
const streaming = ref(false)
const msgListRef = ref(null)

const scrollToBottom = () => {
  nextTick(() => {
    msgListRef.value?.scrollTo({ top: msgListRef.value.scrollHeight, behavior: 'smooth' })
  })
}

const handleSend = async () => {
  const q = question.value.trim()
  if (!q || streaming.value) return

  const history = messages.value.map((m) => ({ role: m.role, content: m.content }))
  messages.value.push({ role: 'user', content: q })
  messages.value.push({ role: 'assistant', content: '', toolInfo: null })
  question.value = ''
  streaming.value = true
  scrollToBottom()

  try {
    await api.chat.stream({ question: q, history }, (event) => {
      const last = messages.value[messages.value.length - 1]
      if (event.type === 'tool') {
        last.toolInfo = `已检索营养知识库：${event.query}`
        scrollToBottom()
      } else if (event.type === 'token') {
        last.content += event.content
        scrollToBottom()
      } else if (event.type === 'error') {
        last.content = (last.content || '') + (event.message || '出错了')
      }
    })
  } catch (error) {
    const last = messages.value[messages.value.length - 1]
    last.content = error.message || '请求失败'
  } finally {
    streaming.value = false
    scrollToBottom()
  }
}
</script>
