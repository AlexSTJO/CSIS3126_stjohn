<template>
  <div class="container">
    <div class="login-form">
      <h1>Login</h1>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <form @submit.prevent="login">
        <div class="input-group">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="email" required />
        </div>

        <div class="input-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" required />
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <p class="signup-link">
        Not have an account? <a @click="navigate('register')">Sign up here</a>
      </p>
    </div>
  </div>
</template>

<script>
import '@/assets/css/auth-form.css';
import {API_ENDPOINTS} from "./constants.js";

export default {
  data() {
    return {
      email: '',
      password: '',
      errorMessage: '',
      loading: false
    };
  },
  methods: {
    async login() {
      this.errorMessage = '';

      if (!this.email || !this.password) {
        this.errorMessage = 'Please fill in all fields.';
        return;
      }

      const emailPattern =
        /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      if (!emailPattern.test(this.email)) {
        this.errorMessage = 'Please enter a valid email address.';
        return;
      }

      this.loading = true;
      try {
        const response = await fetch(API_ENDPOINTS.LOGIN, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email: this.email, password: this.password })
        });

        const data = await response.json();
        if (response.ok) {
          sessionStorage.setItem('token', data.token);
          sessionStorage.setItem('user_id', data.user_id);
          if (data.link){
            this.$router.push('/');
          }
          else {
            this.$router.push('/link')
          }
          
        } else {
          this.errorMessage = data.message || 'Login unsuccessful.';
        }
      } catch (error) {
        console.error('Error:', error);
        this.errorMessage = 'Login unsuccessful.';
      } finally {
        this.loading = false;
      }
    },
    navigate(page) {
      this.$router.push(`/${page}`);
    }
  }
};
</script>


