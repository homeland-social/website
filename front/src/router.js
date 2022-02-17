import Vue from 'vue'
import Router from 'vue-router'
import store from '@/store'
import Home from '@/views/Home'
import Login from '@/views/Login'
import Registration from '@/views/Registration'
import Settings from '@/views/Settings'
import Authorize from '@/views/Authorize'

Vue.use(Router)

function requiresAuth (to, from, next) {
  store
    .dispatch('auth/whoami')
    .then((r) => {
      if (r) {
        next()
      } else {
        next({
          path: '/login',
          query: {
            next: encodeURI(to.fullPath)
          }
        })
      }
    })
}

const router = new Router({
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/registration',
      name: 'Registration',
      component: Registration
    },
    {
      path: '/settings',
      name: 'Settings',
      component: Settings,
      beforeEnter: requiresAuth
    },
    {
      path: '/authorize',
      name: 'Authorize',
      component: Authorize,
      beforeEnter: requiresAuth
    }
  ]
})

export default router
