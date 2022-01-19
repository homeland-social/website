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

  props: {
    next: {
      type: String,
      default: '/home'
    }
  },

  methods: {
    onLogout () {
      this.$store.dispatch('auth/logout')
      if (this.$route.path !== this.next) {
        this.$router.push(this.next)
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
