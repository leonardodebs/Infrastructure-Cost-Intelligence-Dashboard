import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist'
  },
  server: {
    port: 3000,
    host: true,
    allowedHosts: ['d2qlmhctjhcymb.cloudfront.net', 'cloudcostiq-alb-327235121.us-east-1.elb.amazonaws.com']
  },
  preview: {
    port: 3000,
    host: true,
    allowedHosts: true
  }
})
