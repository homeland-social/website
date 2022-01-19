import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

export default {
  namespaced: true,

  state: {
    user: null
  },

  getters: {
    isAuthenticated (state) {
      return state.user !== null && state.user !== false
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
    /* Called by router to check auth status. */
    whoami ({ commit, state }) {
      return new Promise((resolve) => {
        if (state.user === null) {
          axios.get('/api/users/whoami/')
            .then((r) => {
              commit('updateUser', r.data)
              resolve(true)
            })
            .catch((e) => {
              commit('updateUser', false)
              resolve(false)
            })
        } else if (state.user === false) {
          resolve(false)
        } else {
          resolve(true)
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
