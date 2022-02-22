<template>
  <v-main>
    <v-container fluid fill-height>
      <v-layout align-center justify-center>
        <v-flex xs12 sm8 md4>
          <form
            method="POST"
            :action="formAction"
            v-if="client"
          >
            <input
              type="hidden"
              name="csrfmiddlewaretoken"
              :value="csrfToken"
            />
            <input
              v-if="confirm"
              type="hidden"
              name="confirm"
              value="true"
            />
            <v-card class="elevation-12">
              <v-toolbar dark color="primary">
                <v-toolbar-title>Authorize application</v-toolbar-title>
              </v-toolbar>
              <v-card-text>
                <p class="text-h4 text--primary">{{ client.client_name }}</p>
                <div>Brought to you by</div>
                <p class="text-h6 text--primary">{{ client.user.username }}</p>
                <a
                  :href="client.website_uri"
                  target="_blank"
                >{{ client.website_uri }}</a>
                <p>{{ client.description }}</p>
                <p class="text-h8 text--primary">Requested scope(s):</p>
                <ul>
                  <li
                    v-for="(scope, i) of client.scope"
                    :key="i"
                  >{{ scope }}</li>
                </ul>
              </v-card-text>
              <v-card-actions>
                <v-btn
                  @click="confirm=true"
                  type="submit"
                  class="mt-4"
                  color="primary"
                >Confirm access</v-btn>
                <v-btn
                  @click="confirm=false"
                  type="submit"
                  class="mt-4"
                  color="red"
                >Cancel</v-btn>
              </v-card-actions>
            </v-card>                
          </form>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>
import Cookies from 'js-cookie'
import axios from 'axios'

export default {
  name: 'Authorize',
  title: 'Grant application access to your account',

  data () {
    return {
      params: this.$route.query,
      client: null,
      confirm: false
    }
  },

  mounted () {
    axios
      .get('/api/oauth2/authorize/', { params: this.params })
      .then((r) => {
        this.client = r.data.client
      })
  },

  computed: {
    formAction () {
      return `/api/oauth2/authorize/?client_id=${this.params.client_id}&response_type=${this.params.response_type}&redirect_uri=${this.params.redirect_uri}&state=${this.params.state}`
    },

    csrfToken () {
      return Cookies.get('csrftoken')
    }
  }
}
</script>

<style scoped>
</style>
