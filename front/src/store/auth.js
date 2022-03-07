import axios from 'axios'

export default {
  namespaced: true,

  state: {
    auth: null
  },

  getters: {
    isAuthenticated (state) {
      // TODO: may also need to inspect the cookie.
      return state.auth !== null && state.auth !== false
    },

    whoami (state) {
      return state.auth
    }
  },

  mutations: {
    updateAuth (state, user) {
      state.auth = user
    },
  },

  actions: {
    whoami ({ state, commit }) {
      return new Promise((resolve) => {
        if (state.auth === false) {
          resolve(null)
          return
        } else if (state.auth) {
          resolve(state.auth)
          return
        }
        axios
          .get('/api/users/whoami/')
          .then((r) => {
            commit('updateAuth', r.data)
            resolve(state.auth)
          })
          .catch(() => {
            commit('updateAuth', false)
            resolve(null)
          })
      })
    },

    async login ({ commit }, data) {
      const r = await axios.post('/api/users/login/', data)
      commit('updateAuth', r.data)
    },

    logout ({ commit }) {
      axios
        .post('/api/users/logout/')
        .then(() => {
          commit('updateAuth', null)
        })
        .catch(console.error)
    }
  }
}
