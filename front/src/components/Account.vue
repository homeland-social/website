<template>
  <div>
    <v-btn
      v-if="!isAuthenticated"
      to="/login"
      color="primary"
      dark
    >
      Login
      <v-icon>mdi-login-variant</v-icon>
    </v-btn>
    <v-menu
      v-else
      offset-y
      rounded="0"
    >
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          color="primary"
          class="white--text ma-5"
          dark
          v-bind="attrs"
          v-on="on"
        >
          {{ whoami.username }}
          <v-icon
            right
            dark
          >
          mdi-account
          </v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item
          to="/settings"
          link
        >
          <v-list-item-icon><v-icon>mdi-cog-outline</v-icon></v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Settings</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item
          @click.prevent="onLogout"
        >
          <v-list-item-icon><v-icon>mdi-logout-variant</v-icon></v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Logout</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Account',

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
  },

  computed: {
    ...mapGetters({ isAuthenticated: 'auth/isAuthenticated', whoami: 'auth/whoami' })
  }
}
</script>

<style scoped>

</style>
