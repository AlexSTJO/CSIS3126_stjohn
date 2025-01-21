<template>
  <div class="container">
    <div class="login-form">
      <h1>Register</h1>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <form @submit.prevent="register">
        <div class="input-group">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="email" required />
        </div>

        <div class="input-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" required />
        </div>

        <button type="submit">Register</button>
      </form>

      
      <p class="signup-link">
        Already have an account? <a @click="navigate('login')">Login here</a>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      errorMessage: ''
    };
  },
  methods: {
    async register() {
      this.errorMessage = '';
      try {
        const response = await fetch('http://localhost:5000/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email: this.email, password: this.password })
        });

        const data = await response.json();
        if (response.ok) {
          this.$router.push('/');
        } else if (data.error.includes('Duplicate')) {
          this.errorMessage = 'Email is already in use.';
        } else {
          this.errorMessage = data.error;
        }
      } catch (error) {
        console.error('Error:', error);
        this.errorMessage = 'An error occurred. Please try again.';
      }
    },
    navigate(page) {
      this.$router.push(`/${page}`);
    }
  }
};
</script>

<style>
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
}

.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f9f9f9;
}

.login-form {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
  width: 300px;
  text-align: center;
  box-sizing: border-box; 
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

.error-message {
  color: red;
  margin-bottom: 15px;
}

.input-group {
  margin-bottom: 15px;
  box-sizing: border-box; 
}

.input-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.input-group input {
  width: calc(100% - 20px); 
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.signup-link {
  text-align: center;
  margin-top: 15px;
}

.signup-link a {
  color: #4caf50;
  cursor: pointer;
  text-decoration: none;
}

.signup-link a:hover {
  text-decoration: underline;
}
</style>
