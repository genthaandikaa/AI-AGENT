import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:9200',
        changeOrigin: true,
      },
      '/hermes-native': {
        target: 'http://127.0.0.1:9119',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/hermes-native/, '')
      },
      '/clip-pro': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/clip-pro/, '')
      },
      '/virtual-office': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/virtual-office/, '')
      }
    }
  }
})
