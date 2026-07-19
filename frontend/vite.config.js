import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes, req) => {
            // 把后端返回的重定向地址改回代理地址，避免跨域丢 Authorization
            const location = proxyRes.headers['location']
            if (location && proxyRes.statusCode >= 300 && proxyRes.statusCode < 400) {
              proxyRes.headers['location'] = location.replace('http://localhost:8000', '')
            }
          })
        }
      }
    }
  }
})