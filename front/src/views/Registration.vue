<template>
  <div>
    <label for="username">Username</label>
    <input
      type="text"
      v-model="form.username"
      required
    />
    <br/>
    <label for="email">Email</label>
    <input
      type="email"
      v-model="form.email"
      required
    />
    <br/>
    <label for="password">Password</label>
    <input
      type="password"
      v-model="form.password"
      required
    />
    <br/>
    <label for="password-repeat">Password (confirm)</label>
    <input
      type="password"
      v-model="confirm"
    />
    <br/>
    <vue-recaptcha
      :sitekey="recaptchaSiteKey"
      @verify="onVerify"
    />
    <br/>
    <button
      @click.prevent="onRegister"
    >Register</button>
    <br/>
    <p
      v-for="(error, i) in errors"
      v-bind:key="i"
      class="error"
    >{{ error }}</p>
  </div>
</template>

<script>
import axios from 'axios'
import { VueRecaptcha } from 'vue-recaptcha'
import config from '@/config'

export default {
  name: 'Registration',
  title: 'Register a new account',

  components: {
    VueRecaptcha
  },

  data () {
    return {
      form: {
        username: null,
        email: null,
        password: null,
        recaptcha: null
      },
      confirm: null,
      next: this.$route.params.next || '/login',
      recaptchaSiteKey: config.RECAPTCHA_SITE_KEY,
      errors: []
    }
  },

  methods: {
    onVerify (response) {
      this.form.recaptcha = response
    },

    onRegister () {
      if (!this.form.recaptcha) {
        this.errors[0] = 'Complete captcha'
        return
      }

      axios
        .post('/api/users/create/', this.form)
        .then((r) => {
          this.$router.push({
            path: this.next,
            query: { email: r.data.email }
          })
        })
        .catch((e) => {
          console.log(e.response.data)
          this.errors[0] = e.message
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
