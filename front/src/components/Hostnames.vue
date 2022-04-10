<template>
  <v-card class="elevation-12">
    <v-toolbar dark color="primary">
      <v-toolbar-title>Hostnames</v-toolbar-title>
    </v-toolbar>
    <v-card-text>
      <p>Host names are allocated for your use. They can be subdomains of a shared domain, or a domain controlled by you.</p>
      <v-list>
        <v-list-item
          v-for="(hostname, i) of items"
          :key="i"
          :data="hostname"
        >
          <v-list-item-icon>
            <v-icon large>mdi-earth</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>{{ hostname.name }}</v-list-item-title>
            <v-list-item-subtitle>
              <span class="text--primary">Created</span> &mdash; <timeago :datetime="hostname.created"/>
            </v-list-item-subtitle>
            <v-list-item-subtitle>
              <span v-if="dig">
                <p
                  v-for="(addr, i) of dig"
                  :key="i"
                >{{ addr }}</p>
              </span>
            </v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-content>
            <v-list-item-title>Type</v-list-item-title>
            <v-list-item-subtitle>{{ (hostname.internal) ? 'Internal' : 'External' }}</v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-action>
            <v-btn
              icon
              @click="remove(hostname.uid)"
            ><v-icon>mdi-delete</v-icon></v-btn>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Hostnames',

  mounted () {
    this.fetch()
  },

  computed: {
    ...mapGetters({ items: 'hostnames/data' })
  },

  methods: {
    ...mapActions({
      fetch: 'hostnames/fetch',
      remove: 'hostnames/remove'
    }),
  }
}
</script>

<style scoped>

</style>