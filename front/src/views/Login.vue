<template>
   <v-app >
      <v-main>
         <v-container fluid fill-height>
            <v-layout align-center justify-center>
               <v-flex xs12 sm8 md4>
                  <form ref="form" @submit.prevent="onLogin()">
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
                            required
                          ></v-text-field>
                          
                          <v-text-field
                            v-model="form.password"
                            name="password"
                            label="Password"
                            type="password"
                            placeholder="password"
                            required
                          ></v-text-field>
                      </v-card-text>
                      <v-card-actions>
                        <v-btn type="submit" class="mt-4" color="primary" value="log in">Login</v-btn>
                      </v-card-actions>
                    </v-card>                
                  </form>
               </v-flex>
            </v-layout>
         </v-container>
      </v-main>
   </v-app>
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

    return {
      form: {
        email: null,
        password: null
      },
      errors: [],
      next: next || '/settings'
    }
  },

  methods: {
    onLogin () {
      this.$store
        .dispatch('auth/login', this.form)
        .then(() => {
          this.$router.push(this.next)
        })
        .catch((e) => {
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
