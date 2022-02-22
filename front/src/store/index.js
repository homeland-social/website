import Vue from 'vue'
import Vuex from 'vuex'
import Auth from './auth'
import Hostnames from './hostnames'
import Sshkeys from './sshkeys'
import Oauthtokens from './oauthtokens'

Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    auth: Auth,
    hostnames: Hostnames,
    sshkeys: Sshkeys,
    oauthtokens: Oauthtokens
  }
})

export default store
