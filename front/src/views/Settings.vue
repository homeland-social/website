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
                      v-if="item.count !== null"
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
          <component :is="items[selected].component"/>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import Account from '@/components/Account'
import Consoles from '@/components/Consoles'

export default {
  name: 'Settings',
  title: 'Settings',

  components: {
    Account,
    Consoles,
  },

  data () {
    return {
      selected: 0
    }
  },

  mounted () {
    this.fetchConsoles()
  },

  computed: {
    ...mapGetters({
      consoles: 'consoles/data'
    }),

    consoleCount () {
      return (this.consoles) ? this.consoles.length : 0;
    },

    items () {
      return [
        { icon: 'mdi-account', name: 'Account', count: null, component: Account },
        { icon: 'mdi-dns-outline', name: 'consoles', count: this.consoleCount, component: Consoles },
      ]
    }
  },

  methods: {
    ...mapActions({ fetchConsoles: 'consoles/fetch' }),
  },
}
</script>

<style scoped>

</style>
