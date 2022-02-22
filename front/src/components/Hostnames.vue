<template>
  <v-flex>
    <p>Host names are allocated for your use. They can be subdomains of a shared domain, or a domain controlled by you.</p>
    <v-simple-table>
      <tbody>
        <tr
          v-for="(hostname, i) of items"
          :key="i"
        >
          <td>
            <v-icon large>mdi-earth</v-icon>
            <p>{{ hostname.name }}</p>
          </td>
          <td></td>
          <td>{{ hostname.internal }}</td>
          <td class="text-right">
            <v-btn
              icon
              @click="remove(hostname.uid)"
            ><v-icon>mdi-delete</v-icon></v-btn>
          </td>
        </tr>
      </tbody>
    </v-simple-table>
  </v-flex>
<!--  <v-list>
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
          Created: <timeago :datetime="hostname.created"/>
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
      <v-list-item-content>Internal: {{ hostname.internal }}</v-list-item-content>
      <v-list-item-action>
        <v-btn
          icon
          @click="remove(hostname.uid)"
        ><v-icon>mdi-delete</v-icon></v-btn>
      </v-list-item-action>
    </v-list-item>
  </v-list>-->
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