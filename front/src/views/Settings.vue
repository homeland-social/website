<template>
  <v-main>
    <v-container fluid fill-height>
      <v-layout justify-center>
        <v-flex xs3 sm1 md2>
          <v-card class="elevation-12">
            <v-toolbar dark color="primary">
              <v-toolbar-title>Menu</v-toolbar-title>
            </v-toolbar>
            <v-list>
              <v-list-item-group
                v-model="selected"
              >
                <v-list-item
                  v-for="(item, i) in items"
                  :key="i"
                >
                  <v-list-item-icon>
                    <v-icon v-text="item.icon"></v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title v-text="item.name"></v-list-item-title>
                  </v-list-item-content>
                  <v-list-item-action>
                    <v-chip
                      small
                      color="light-green"
                      text-color="white"
                    >{{ item.count }}</v-chip>
                  </v-list-item-action>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-flex>
        <v-flex
          xs8 sm3 md8 ml-4
        >
          <v-card
            v-if="selected !== null"
            class="elevation-12"
          >
            <v-toolbar dark color="primary">
              <v-toolbar-title v-text="items[selected].name"></v-toolbar-title>
            </v-toolbar>
            <v-card-text><component :is="items[selected].component"/>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>
import { mapGetters } from 'vuex'
import Hostnames from '@/components/Hostnames'
import SSHKeys from '@/components/SSHKeys'
import OAuthTokens from '@/components/OAuthTokens'

export default {
  name: 'Settings',
  title: 'Settings',

  components: {
    Hostnames,
    SSHKeys,
    OAuthTokens
  },

  data () {
    return {
      selected: 0
    }
  },

  mounted () {
    this.$store.dispatch('hostnames/fetch')
    this.$store.dispatch('sshkeys/fetch')
    this.$store.dispatch('oauthtokens/fetch')
  },

  computed: {
    items () {
      return [
        { icon: 'mdi-dns-outline', name: 'Hostnames', count: this.hostnames, component: Hostnames },
        { icon: 'mdi-key-outline', name: 'SSH keys' , count: this.sshkeys, component: SSHKeys },
        { icon: 'mdi-server', name: 'OAuth tokens', count: this.oauthtokens, component: OAuthTokens }
      ]
    },

    ...mapGetters({
        hostnames: 'hostnames/count',
        sshkeys: 'sshkeys/count',
        oauthtokens: 'oauthtokens/count'
      })
  },
}
</script>

<style scoped>

</style>
