import axios from 'axios'

let fetching = false

export default {
  namespaced: true,

  state: {
    data: null
  },

  getters: {
    data (state) {
      return state.data
    },

    count (state) {
      return (state.data) ? state.data.length : 0
    }
  },

  mutations: {
    update (state, data) {
      state.data = data
    },
  },

  actions: {
    fetch ({ commit, state }, force=false) {
      if (!force && state.data !== null) return

      if (fetching) return
      fetching = true

      axios
        .get('/api/hosts/')
        .then((r) => {
          commit('update', r.data)
        })
        .catch((e) => {
          fetching = false
          console.error(e)
        })
    },

    remove ({ commit, state }, uid) {
      axios
        .delete(`/api/hosts/${uid}/`)
        .then(() => {
          commit('update', state.data.filter(o => o.uid !== uid))
        })
        .catch(console.error)
    }
  }
}
