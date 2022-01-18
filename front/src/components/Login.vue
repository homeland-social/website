<template>
  <form
    v-on:submit.prevent="onLogin"
  >
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
    <button>Login</button>
    <br/>
    <p
      v-for="(error, i) in errors"
      v-bind:key="i"
      class="error"
    >{{ error }}</p>
  </form>
</template>

<script>
export default {
  name: 'Login',
  title: 'Log in',

  data () {
    return {
      form: {
        email: null,
        password: null
      },
      errors: [],
      next: this.$route.query.next || '/account'
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
