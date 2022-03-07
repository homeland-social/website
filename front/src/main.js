import Vue from 'vue'
import axios from 'axios'
import VuePageTitle from 'vue-page-title'
import VueTimeago from 'vue-timeago'
import App from './App.vue'
import store from './store'
import router from './router'
import vuetify from './plugins/vuetify'

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
