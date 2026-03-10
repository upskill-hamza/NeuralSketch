import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // Proxy API calls to FastAPI backend during development
      '/predict': 'http://localhost:8000',
      '/categories': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
})
