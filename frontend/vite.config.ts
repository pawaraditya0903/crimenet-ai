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
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('cytoscape')) return 'vendor-cytoscape'
            if (id.includes('mapbox-gl')) return 'vendor-mapbox'
            if (id.includes('recharts')) return 'vendor-recharts'
            if (id.includes('lucide-react')) return 'vendor-icons'
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router-dom')) return 'vendor-react'
            return 'vendor-core'
          }
        }
      }
    }
  }
})

