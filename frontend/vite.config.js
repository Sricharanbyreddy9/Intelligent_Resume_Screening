import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // CORS is handled in FastAPI, so direct fetch to localhost:8000 works fine
  }
})