<template>
  <form
    v-on:submit.prevent="onConfirm"
  >
    <label for="email">Email</label>
    <input
      name="email"
      v-model="form.email"
    />
    <br/>
    <label for="ts">Timestamp</label>
    <input
      name="ts"
      v-model="form.ts"
    />
    <br/>
    <label for="signature">Signature</label>
    <input
      name="signature"
      v-model="form.signature"
    />
    <br/>
    <button>Confirm</button>
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
  name: 'Confirm',
  title: 'Confirm your email address',

  data () {
    return {
      form: {
        email: this.$route.query.email,
        ts: this.$route.query.ts,
        signature: this.$route.query.signature
      },
      next: this.$route.query.next || '/login',
      errors: []
    }
  },

  mounted () {
    if (this.form.email && this.form.ts && this.form.signature) {
      this.onConfirm()
    }
  },

  methods: {
    onConfirm () {
      this.$store
        .dispatch('confirm', this.form)
        .then((r) => {
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
