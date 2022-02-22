<template>
  <v-flex>
    <p>SSH keys are used by the console to establish an SSH tunnel.</p>
    <v-list>
      <v-list-item
        v-for="(sshkey, i) of items"
        :key="i"
      >
        <v-list-item-icon>
          <v-icon large>mdi-key-outline</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>{{ sshkey.name }}</v-list-item-title>
          <v-list-item-subtitle>
            Created: <timeago :datetime="sshkey.created"/>
          </v-list-item-subtitle>
        </v-list-item-content>
        <v-list-item-action>
          <v-btn
            icon
            @click="remove(sshkey.uid)"
          ><v-icon>mdi-delete</v-icon></v-btn>
        </v-list-item-action>
      </v-list-item>
    </v-list>
  </v-flex>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'SSHKeys',

  mounted () {
    this.fetch()
  },

  computed: {
    ...mapGetters({ items: 'sshkeys/data' })
  },

  methods: {
    ...mapActions({
      fetch: 'sshkeys/fetch',
      remove: 'sshkeys/remove'
    }),
  }
}
</script>

<style scoped>

</style>