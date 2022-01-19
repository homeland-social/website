<template>
  <div>
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
      <h4>{{ client.client_name }}</h4>
      <p><em>By:</em>{{ client.user.username }}</p>
      <a
        :href="client.website_uri"
        target="_blank"
      >{{ client.website_uri }}</a>
      <p>{{ client.description }}</p>
      <p><em>Requested scope(s):</em></p>
      <ul>
        <li
          v-for="(scope, i) of client.scope"
          :key="i"
        >{{ scope }}</li>
      </ul>
      <label for="email">Email</label>
      <input
        name="confirm"
        type="checkbox"
        value="true"
      />
      <br/>
      <button>Grant access</button>
    </form>
    <p
      v-else
    >Fetching application info</p>
  </div>
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
      client: null
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
      return `/api/oauth2/authorize/?client_id=${this.params.client_id}&response_type=${this.params.response_type}&redirect_uri=${this.params.redirect_uri}`
    },

    csrfToken () {
      return Cookies.get('csrftoken')
    }
  }
}
</script>

<style scoped>
</style>
