<template>
  <form
    v-on:submit.prevent="onLogin"
  >
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
      type="checkbox"
      value="true"
      v-model="form.confirm"
    />
    <br/>
    <button>Grant access</button>
    <br/>
    <p
      v-for="(error, i) in errors"
      v-bind:key="i"
      class="error"
    >{{ error }}</p>
  </form>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Authorize',
  title: 'Grant application access to your account',

  data () {
    return {
      form: {
        confirm: null
      },
      client: null,
      errors: []
    }
  },

  mounted () {
    axios
      .get('/api/oauth2/authorize/', {
        params: {
          client_id: 'foobar',
          response_type: 'code',
          redirect_uri: 'http://localhost:5000/oauth/'
        }
      })
      .then((r) => {
        this.client = r.data.client
      })
  },

  methods: {
    onLogin () {
      axios
        .post('/api/oauth2/authorize/', this.form, {
          params: {
            client_id: 'foobar',
            response_type: 'code',
            redirect_uri: 'http://localhost:5000/oauth/'
          }
        })
        .then((r) => {
          if (r.statusCode === 302) {
            window.location = r.headers['Location']
          }
        })
    }
  }
}
</script>

<style scoped>
.error {
  color: red;
}
</style>
