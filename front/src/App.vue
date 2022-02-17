<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
    >
      <div class="d-flex align-center">
        <v-btn
          to="/"
          light
        >
          Shanty social
          <v-icon>mdi-earth</v-icon>
        </v-btn>
      </div>

      <v-spacer></v-spacer>
      <account/>
    </v-app-bar>

    <v-main>
      <router-view/>
    </v-main>
  </v-app>
</template>

<script>
import { mapActions } from 'vuex'
import Account from '@/components/Account'

export default {
  components: {
    Account
  },

  methods: {
    ...mapActions({ whoami: 'auth/whoami'})
  },

  created () {
    this.whoami()
  }
}
</script>

<style>
</style>
