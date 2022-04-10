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
          Homeland social
          <v-icon class="ml-2">mdi-message-outline</v-icon>
        </v-btn>
      </div>

      <v-spacer></v-spacer>
      <account/>
    </v-app-bar>

    <v-main>
      <router-view/>
    </v-main>

    <v-footer
      padless
      color="primary lighten-1"
    >
      <v-row
        no-gutters
        justify="center"
      >
        <v-btn
          v-for="(link, i) of footerLinks"
          :key="i"
          :to="link.to"
          :href="link.href"
          :target="link.target"
          text rounded
          color="white"
          class="my-2"
        >{{ link.text }}</v-btn>
        <v-col
          class="primary lighten-2 py-4 text-center white--text"
          cols="12"
        >{{ new Date().getFullYear() }} - <strong>Homeland.social</strong></v-col>
      </v-row>
    </v-footer>
  </v-app>
</template>

<script>
import { mapActions } from 'vuex'
import Account from '@/components/Account'

export default {
  name: 'App',

  components: {
    Account
  },

  data () {
    return {
      footerLinks: [
        { text: 'About', to: '/about' },
        { text: 'How it works', to: '/how-it-works' },
        { text: 'Privacy', to: '/privacy' },
        { text: 'Github', href: 'https://github.com/shanty-social/', target: '_new' }
      ]
    }
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
