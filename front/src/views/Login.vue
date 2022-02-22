<template>
  <v-main>
    <v-container fluid>
      <v-layout align-center justify-center>
        <v-flex xs12 sm8 md4>
          <v-form
            ref="form"
            @submit.prevent="onLogin()"
          >
            <v-card class="elevation-12">
              <v-toolbar dark color="primary">
                <v-toolbar-title>Login</v-toolbar-title>
              </v-toolbar>
              <v-card-text>
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
                <v-alert
                  v-if="error"
                  dense outlined
                  type="error"
                >{{ error }}</v-alert>
              </v-card-text>
              <v-card-actions>
                <v-btn
                  type="submit" color="primary" value="log in"
                >Login</v-btn>
                <v-btn
                  text
                  color="accent-4"
                  to="/registration"
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
export default {
  name: 'Login',
  title: 'Log in',

  data () {
    let next = this.$route.query.next
    if (next) {
      next = decodeURI(next)
    }
    let email = this.$route.query.email

    return {
      form: {
        email,
        password: null
      },
      rules: {
        email: [
          v => (v || '').length > 0 || 'Is required',
          v => (v || '').match(/^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/) !== null || 'Not a valid email address'
        ],
        password: [
          v => (v || '').length > 0 || 'Is required'
        ]
      },
      error: null,
      next: next || '/settings'
    }
  },

  methods: {
    onLogin () {
      if (!this.$refs.form.validate()) return

      this.$store
        .dispatch('auth/login', this.form)
        .then(() => {
          this.$router.push(this.next)
        })
        .catch((e) => {
          this.error = e.message
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
