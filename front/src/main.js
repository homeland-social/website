import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import VuePageTitle from 'vue-page-title'
import store from './store'
import router from './router'

Vue.config.productionTip = false
Vue.use(VuePageTitle, {
  prefix: 'shanty.social - '
})

new Vue({
  vuetify,
  store,
  router,
  render: h => h(App)
}).$mount('#app')
