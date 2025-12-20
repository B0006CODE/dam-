import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue';
import { useUserStore } from '@/stores/user';
import { useAgentStore } from '@/stores/agent';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/agent',
      name: 'AgentMain',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'AgentComp',
          component: () => import('../views/AgentView.vue'),
          meta: { keepAlive: true, requiresAuth: true, requiresAdmin: false }
        }
      ]
    },
    {
      path: '/agent/:agent_id',
      name: 'AgentSinglePage',
      component: () => import('../views/AgentSingleView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/graph',
      name: 'graph',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'GraphComp',
          component: () => import('../views/GraphView.vue'),
          meta: { keepAlive: false, requiresAuth: true, requiresAdmin: false }
        }
      ]
    },
    {
      path: '/database',
      name: 'database',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'DatabaseComp',
          component: () => import('../views/DataBaseView.vue'),
          meta: { keepAlive: true, requiresAuth: true, requiresAdmin: true }
        },
        {
          path: ':database_id',
          name: 'DatabaseInfoComp',
          component: () => import('../views/DataBaseInfoView.vue'),
          meta: { keepAlive: false, requiresAuth: true, requiresAdmin: true }
        }
      ]
    },
    {
      path: '/setting',
      name: 'setting',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'SettingComp',
          component: () => import('../views/SettingView.vue'),
          meta: { keepAlive: true, requiresAuth: true, requiresAdmin: true }
        }
      ]
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'DashboardComp',
          component: () => import('../views/DashboardView.vue'),
          meta: { keepAlive: false, requiresAuth: true, requiresAdmin: true }
        }
      ]
    },
    {
      path: '/map',
      name: 'reservoirMap',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'ReservoirMapComp',
          component: () => import('../views/ReservoirMapView.vue'),
          meta: { keepAlive: false, requiresAuth: true, requiresAdmin: false }
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/EmptyView.vue'),
      meta: { requiresAuth: false }
    },
  ]
})

// 鍏ㄥ眬鍓嶇疆瀹堝崼
router.beforeEach(async (to, from, next) => {
  // 妫€鏌ヨ矾鐢辨槸鍚﹂渶瑕佽璇?
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth === true);
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin);

  const userStore = useUserStore();
  const isLoggedIn = userStore.isLoggedIn;
  const isAdmin = userStore.isAdmin;

  // 濡傛灉璺敱闇€瑕佽璇佷絾鐢ㄦ埛鏈櫥褰?
  if (requiresAuth && !isLoggedIn) {
    // 淇濆瓨灏濊瘯璁块棶鐨勮矾寰勶紝鐧诲綍鍚庤烦杞?
    sessionStorage.setItem('redirect', to.fullPath);
    next('/login');
    return;
  }

  // 濡傛灉璺敱闇€瑕佺鐞嗗憳鏉冮檺浣嗙敤鎴蜂笉鏄鐞嗗憳
  if (requiresAdmin && !isAdmin) {
    // 濡傛灉鏄櫘閫氱敤鎴凤紝璺宠浆鍒伴粯璁ゆ櫤鑳戒綋椤甸潰
    try {
      const agentStore = useAgentStore();
      if (!agentStore.isInitialized) {
        await agentStore.initialize();
      }
      next('/agent');
    } catch (error) {
      console.error('鑾峰彇鏅鸿兘浣撲俊鎭け璐?', error);
      next('/login');
    }
    return;
  }

  // 濡傛灉鐢ㄦ埛宸茬櫥褰曚絾璁块棶鐧诲綍椤碉紝璺宠浆鍒版櫤鑳戒綋椤甸潰
  if (to.path === '/login' && isLoggedIn) {
    next('/agent');
    return;
  }

  // 鍏朵粬鎯呭喌姝ｅ父瀵艰埅
  next();
});

export default router
