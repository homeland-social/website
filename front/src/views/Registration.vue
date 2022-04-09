<template>
  <v-main>
    <v-container fluid>
      <v-layout align-center justify-center>
        <v-flex xs12 sm8 md4>
          <v-form
            ref="form"
            @submit.prevent="onRegister()"
          >
            <v-card class="elevation-12">
              <v-toolbar dark color="primary">
                <v-toolbar-title>Register</v-toolbar-title>
              </v-toolbar>
              <v-card-text>
                <p class="text-h4">Create an account</p>
                <p>An account is required to set up domains for use with the <a target="new" href="https://github.com/shanty-social/console/">Homeland social console</a>.</p>
              </v-card-text>
              <v-card-text>
                <v-text-field
                  v-model="form.username"
                  name="username"
                  label="Username"
                  type="text"
                  placeholder="username"
                  :rules="rules.username"
                ></v-text-field>
                <v-text-field
                  v-model="form.email"
                  name="email"
                  label="Email"
                  type="text"
                  placeholder="email"
                  :rules="rules.email"
                ></v-text-field>
                <v-text-field
                  v-model="form.password"
                  name="password"
                  label="Password"
                  type="password"
                  placeholder="password"
                  :rules="rules.password"
                ></v-text-field>
                <v-text-field
                  v-model="confirm"
                  name="confirm"
                  label="Confirm password"
                  type="password"
                  placeholder="Confirm password"
                  :rules="rules.confirm"
                ></v-text-field>
                <vue-recaptcha
                  :sitekey="recaptchaSiteKey"
                  @verify="onVerify"
                />
                <v-alert
                  v-if="error"
                  dense outlined
                  type="error"
                  class="mt-4"
                >{{ error }}</v-alert>
              </v-card-text>
              <v-card-actions>
                <v-btn
                  type="submit"
                  color="primary"
                  value="log in"
                >Register</v-btn>
              </v-card-actions>
            </v-card>                
          </v-form>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
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
      rules: {
        username: [
          v => (v || '').length > 0 || 'Is required'
        ],
        email: [
          v => (v || '').length > 0 || 'Is required',
          v => (v || '').match(/^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/) !== null || 'Not a valid email address'
        ],
        password: [
          v => (v || '').length > 0 || 'Is required'
        ],
        confirm: [
          v => (v || '').length > 0 || 'Is required',
          v => (v === this.form.password) || 'Must match password'
        ]
      },
      confirm: null,
      next: this.$route.params.next || '/login',
      recaptchaSiteKey: config.RECAPTCHA_SITE_KEY,
      error: null
    }
  },

  methods: {
    onVerify (response) {
      this.form.recaptcha = response
    },

    onRegister () {
      if (!this.$refs.form.validate()) return
      if (!this.form.recaptcha) {
        this.error = 'Please complete captcha'
        return
      }

      axios
        .post('/api/users/', this.form)
        .then((r) => {
          this.$router.push({
            path: this.next,
            query: { email: r.data.email }
          })
        })
        .catch((e) => {
          this.error = (e.response && e.response.data && e.response.data.detail || e.message)
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
