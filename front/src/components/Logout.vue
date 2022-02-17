<template>
  <v-btn
    text
    @click.prevent="onLogout"
  >
    <span class="mr-2">Logout</span>
    <v-icon>mdi-logout-variant</v-icon>
  </v-btn>
</template>

<script>
export default {
  name: 'Logout',

  props: {
    next: {
      type: String,
      default: '/'
    }
  },

  methods: {
    onLogout () {
      this.$store.dispatch('auth/logout')
      if (this.$route.path !== this.next) {
        this.$router.push(this.next)
      }
    }
  }
}
</script>

<style scoped>

</style>
