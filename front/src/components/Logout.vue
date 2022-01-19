<template>
  <a
    href="#"
    :class="{ 'nav-link': true, 'disabled': !isAuthenticated }"
    @click.prevent="onLogout"
  >Logout</a>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Logout',

  methods: {
    onLogout () {
      this.$store.dispatch('auth/logout')
      if (this.$route.path !== '/home') {
        this.$router.push('/home')
      }
    }
  },

  computed: {
    ...mapGetters({ isAuthenticated: 'auth/isAuthenticated' })
  }
}
</script>

<style scoped>

</style>
