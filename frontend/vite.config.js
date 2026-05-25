import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    open: false,
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:4567/', // 
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
    },
  },
  // 添加以下 resolve 配置来设置别名
  resolve: {
    alias: {
      '@': '/src', // 设置 '@' 别名指向 'src' 目录
    },
  },

})
