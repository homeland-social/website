import axios from 'axios'

export default {
  namespaced: true,

  state: {
    user: null
  },

  getters: {
    isAuthenticated (state) {
      // TODO: may also need to inspect the cookie.
      return state.user !== null && state.user !== false
    },

    whoami (state) {
      return state.user
    }
  },

  mutations: {
    updateUser (state, newUser) {
      state.user = newUser
    },

    removeUser (state) {
      state.user = null
    }
  },

  actions: {
    whoami ({ state, commit }) {
      return new Promise((resolve) => {
        if (state.user === null) {
          axios.get('/api/users/whoami/')
            .then((r) => {
              commit('updateUser', r.data)
              resolve(state.user)
            })
            .catch(() => {
              commit('updateUser', false)
              resolve(null)
            })
        } else if (state.user === false) {
          resolve(null);
        } else if (state.user) {
          resolve(state.user)
          return
        }
      })
    },

    async login ({ commit }, data) {
      const r = await axios.post('/api/users/login/', data)
      commit('updateUser', r.data)
    },

    logout ({ commit }) {
      axios
        .post('/api/users/logout/')
        .then(console.log)
      commit('removeUser')
    }
  }
}
