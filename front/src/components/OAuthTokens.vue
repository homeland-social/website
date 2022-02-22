<template>
  <v-flex>
    <p>OAuth tokens are used by the console to make API calls.</p>
    <v-list>
      <v-list-item
        v-for="(token, i) of items"
        :key="i"
        :data="token"
      >
        <v-list-item-icon>
        <v-icon large>mdi-server</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
        <v-list-item-title>{{ token.client.client_name }}</v-list-item-title>
        <v-list-item-subtitle>
          Issued: <timeago :datetime="token.issued_at"/>
        </v-list-item-subtitle>
        </v-list-item-content>
        <v-list-item-action>
        <v-btn
          icon
          @click="remove(token.uid)"
        ><v-icon>mdi-delete</v-icon></v-btn>
        </v-list-item-action>
      </v-list-item>
    </v-list>
  </v-flex>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'OAuthTokens',

  mounted () {
    this.fetch()
  },

  computed: {
    ...mapGetters({ items: 'oauthtokens/data' })
  },

  methods: {
    ...mapActions({
      fetch: 'oauthtokens/fetch',
      remove: 'oauthtokens/remove'
    })
  }
}
</script>

<style scoped>

</style>