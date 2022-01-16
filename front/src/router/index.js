import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/components/Login'
import Registration from '@/components/Registration'
import Confirm from '@/components/Confirm'
import Account from '@/components/Account'

Vue.use(Router)

export default new Router({
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
      component: Account
    }
  ]
})
