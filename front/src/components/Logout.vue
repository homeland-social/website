<template>
  <a
    href="#"
    class="nav-link"
    @click.prevent="onLogout"
  >Logout</a>
</template>

<script>
export default {
  name: 'Logout',

  methods: {
    onLogout () {
      this.$store.dispatch('auth/logout')
      if (this.$route.path !== '/home') {
        this.$router.push('/home')
      }
    }
  }
}
</script>

<style scoped>

</style>
