import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const manualChunks = (id) => {
    if (!id.includes('node_modules')) {
      return
    }

    if (
      id.includes('@antv/g6') ||
      id.includes('sigma') ||
      id.includes('graphology') ||
      id.includes('d3') ||
      id.includes('three') ||
      id.includes('echarts')
    ) {
      return 'graph-viz'
    }

    if (id.includes('ant-design-vue') || id.includes('@ant-design/icons-vue') || id.includes('dayjs')) {
      return 'ui-vendor'
    }

    if (id.includes('md-editor-v3') || id.includes('marked') || id.includes('highlight.js')) {
      return 'editor-vendor'
    }

    return 'vendor'
  }

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    assetsInclude: ['**/*.json'],
    json: {
      stringify: false
    },
    optimizeDeps: {
      include: [
        'graphology',
        'graphology-layout',
        'graphology-layout-forceatlas2',
        'sigma'
      ]
    },
    build: {
      chunkSizeWarningLimit: 1600,
      rollupOptions: {
        output: {
          manualChunks,
        },
      },
    },
    server: {
      proxy: {
        '^/api': {
          target: env.VITE_API_URL || 'http://127.0.0.1:5050',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '/api')
        }
      },
      watch: {
        usePolling: true,
        ignored: ['**/node_modules/**', '**/dist/**'],
      },
      host: '0.0.0.0',
    }
  }
})
