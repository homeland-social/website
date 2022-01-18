<template>
  <form
    v-on:submit.prevent="onRegister"
  >
    <label for="username">Username</label>
    <input
      v-model="form.username"
    />
    <br/>
    <label for="email">Email</label>
    <input
      v-model="form.email"
    />
    <br/>
    <label for="password">Password</label>
    <input
      type="password"
      v-model="form.password"
    />
    <br/>
    <label for="password-repeat">Password (confirm)</label>
    <input
      type="password"
      v-model="form.confirm"
    />
    <br/>
    <button>Register</button>
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
  name: 'Registration',
  title: 'Register a new account',

  data () {
    return {
      form: {
        username: null,
        email: null,
        password: null,
        confirm: null
      },
      next: this.$route.params.next || '/confirm',
      errors: []
    }
  },

  methods: {
    onRegister () {
      const data = {
        username: this.form.username,
        email: this.form.email,
        password: this.form.password
      }

      axios
        .post('/api/users/create/', data)
        .then((r) => {
          this.$router.push({
            path: this.next,
            query: { email: r.data.email }
          })
        })
        .catch((e) => {
          console.log(e.response.data)
          this.errors.push(e.message)
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
