import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())

  return {
    plugins: [vue()],
    define: {
      __VUE_OPTIONS_API__: true,
      __VUE_PROD_DEVTOOLS__: false,
      __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    server: {
      port: 8080,
      host: true,
      strictPort: true,
      // 配置HTTPS
      https: {
        key: fs.readFileSync(path.resolve(__dirname, '.certs/localhost+3-key.pem')),
        cert: fs.readFileSync(path.resolve(__dirname, '.certs/localhost+3.pem'))
      },
      // 设置CSP头
      headers: {
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://challenges.cloudflare.com https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' https://challenges.cloudflare.com; frame-src https://challenges.cloudflare.com;"
      },
      // 输出开发服务器配置信息
      onListening: (server) => {
        const address = server.httpServer.address()
        const protocol = server.config.server.https ? 'https' : 'http'
        const host = address.address === '0.0.0.0' ? 'localhost' : address.address
        const port = address.port
        console.log(`用户前端开发服务器运行在: ${protocol}://${host}:${port}`)
        console.log(`API 地址: ${env.VITE_API_BASE_URL}`)
      }
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true
        }
      }
    }
  }
}) 