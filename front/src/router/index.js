import Vue from 'vue'
import Router from 'vue-router'
import store from '@/store'
import Login from '@/components/Login'
import Registration from '@/components/Registration'
import Confirm from '@/components/Confirm'
import Account from '@/components/Account'
import Authorize from '@/components/Authorize'

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
            next: to.path
          }
        })
      }
    })
}

const router = new Router({
  routes: [
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
      path: '/confirm',
      name: 'Confirm',
      component: Confirm
    },
    {
      path: '/account',
      name: 'Account',
      component: Account,
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
