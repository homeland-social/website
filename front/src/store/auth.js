import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

export default {
  state: {
    user: {},
    token: JSON.parse(localStorage.getItem('token'))
  },

  getters: {
    isAutenticated (state) {
      return state.token !== null
    }
  },

  mutations: {
    updateToken (state, newToken) {
      localStorage.setItem('token', JSON.stringify(newToken))
      state.token = newToken
    },

    removeToken (state) {
      localStorage.removeItem('token')
      state.token = null
    }
  },

  actions: {
    async login ({ commit }, data) {
      return new Promise((resolve, reject) => {
        axios
          .post('/api/token/', data)
          .then((r) => {
            commit('updateToken', r.data)
            resolve(r)
          })
          .catch(reject)
      })
    },

    async register ({ state }, data) {
      return axios
        .post('/api/users/create/', data)
    },

    async confirm ({ state }, data) {
      return axios
        .post('/api/users/confirm/', data)
    }
  }
}
