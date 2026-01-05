import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5175,
    host: true, // Allow external access
    allowedHosts: true, // Allow all hosts for LAN access
    proxy: {
      // Proxy all API requests to backend
      '/auth': {
        target: 'http://localhost:8002',
        changeOrigin: true
      },
      '/offers': {
        target: 'http://localhost:8002',
        changeOrigin: true
      },
      '/dashboard': {
        target: 'http://localhost:8002',
        changeOrigin: true
      },
      '/clients': {
        target: 'http://localhost:8002',
        changeOrigin: true
      },
      '/users': {
        target: 'http://localhost:8002',
        changeOrigin: true
      },
      '/import': {
        target: 'http://localhost:8002',
        changeOrigin: true
      },
      '/analytics': {
        target: 'http://localhost:8002',
        changeOrigin: true
      }
    }
  }
})
