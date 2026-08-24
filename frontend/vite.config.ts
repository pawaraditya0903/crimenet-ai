import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    host: true,
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'https://crimenet-ai.onrender.com',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
