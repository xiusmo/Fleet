import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import SignConfigs from '../views/SignConfigs.vue'
import ActivityDetail from '../views/ActivityDetail.vue'
import UserProfile from '../views/UserProfile.vue'
import QrScanner from '../views/QrScanner.vue'
import NotFound from '../views/NotFound.vue'
import Terms from '../views/Terms.vue'
import LeaveNoteEditor from '../views/LeaveNoteEditor.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/sign-configs',
    name: 'SignConfigs',
    component: SignConfigs,
    meta: { requiresAuth: true }
  },
  {
    path: '/activities/:uuid',
    name: 'ActivityDetail',
    component: ActivityDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { requiresAuth: true }
  },
  {
    path: '/qr-scanner',
    name: 'QrScanner',
    component: QrScanner,
    // 无需验证，任何人都可访问
  },
  {
    path: '/terms',
    name: 'Terms',
    component: Terms,
    // 无需验证，任何人都可访问
  },
  {
    path: '/leave-note-editor',
    name: 'LeaveNoteEditor',
    component: LeaveNoteEditor,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    // 始终滚动到顶部
    return { top: 0 }
  }
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 