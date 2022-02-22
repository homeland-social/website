import axios from 'axios'

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

      axios
        .get('/api/tokens/')
        .then((r) => {
          commit('update', r.data)
        })
        .catch(console.error)
    },

    remove ({ commit, state }, uid) {
      axios
        .delete(`/api/tokens/${uid}/`)
        .then(() => {
          commit('update', state.data.filter(o => o.uid !== uid))
        })
        .catch(console.error)
    }
  }
}
