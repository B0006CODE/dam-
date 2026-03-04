import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css';
import '@/assets/css/main.css'
import '@/assets/css/antd-dark-override.css'

function isModuleLoadError (error) {
  const msg = String(error?.message || error || '')
  return (
    msg.includes('Failed to fetch dynamically imported module') ||
    msg.includes('Importing a module script failed') ||
    msg.includes('Load failed') ||
    msg.includes('ERR_CONNECTION') ||
    msg.includes('ERR_NETWORK')
  )
}

async function bootstrap () {
  const reloadKey = '__app_bootstrap_reload__'
  const readSession = (key) => {
    try { return window.sessionStorage.getItem(key) } catch (_e) { return null }
  }
  const writeSession = (key, value) => {
    try { window.sessionStorage.setItem(key, value) } catch (_e) {}
  }
  const removeSession = (key) => {
    try { window.sessionStorage.removeItem(key) } catch (_e) {}
  }
  const hasRetried = readSession(reloadKey) === '1'

  try {
    const [{ default: App }, { default: router }, { useInfoStore }] = await Promise.all([
      import('./App.vue'),
      import('./router'),
      import('./stores/info')
    ])

    const app = createApp(App)
    const pinia = createPinia()

    app.use(pinia)
    app.use(router)
    app.use(Antd)

    const infoStore = useInfoStore()
    void infoStore.loadInfoConfig()

    removeSession(reloadKey)
    app.mount('#app')
  } catch (error) {
    if (!hasRetried && isModuleLoadError(error)) {
      writeSession(reloadKey, '1')
      window.location.reload()
      return
    }
    removeSession(reloadKey)
    console.error('应用启动失败:', error)
  }
}

void bootstrap()
