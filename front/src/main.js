import Vue from 'vue'
import axios from 'axios'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import VuePageTitle from 'vue-page-title'
import VueTimeago from 'vue-timeago'
import store from './store'
import router from './router'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

Vue.config.productionTip = false
Vue.use(VuePageTitle, {
  prefix: 'shanty.social - '
})
Vue.use(VueTimeago, {
  name: 'Timeago',
  locale: 'en'
})

new Vue({
  vuetify,
  store,
  router,
  render: h => h(App)
}).$mount('#app')
