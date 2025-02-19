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

        <div class="input-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="confirmPassword"
            required
          />
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? "Registering..." : "Register" }}
        </button>
      </form>

      <p class="signup-link">
        Already have an account? <a @click="navigate('login')">Login here</a>
      </p>
    </div>
  </div>
</template>
<script>
import {API_ENDPOINTS} from './constants.js';

export default {
  data() {
    return {
      email: "",
      password: "",
      confirmPassword: "",
      errorMessage: "",
      loading: false,
    };
  },
  methods: {
    async register() {
      this.errorMessage = "";

      if (!this.email || !this.password || !this.confirmPassword) {
        this.errorMessage = "Please fill in all fields.";
        return;
      }

      const emailPattern =
        /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      if (!emailPattern.test(this.email)) {
        this.errorMessage = "Please enter a valid email address.";
        return;
      }

      if (this.password.length < 6) {
        this.errorMessage = "Password must be at least 6 characters.";
        return;
      }

      if (this.password !== this.confirmPassword) {
        this.errorMessage = "Passwords do not match.";
        return;
      }

      try {
        this.loading = true;
        const response = await fetch(API_ENDPOINTS.REGISTER, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: this.email,
            password: this.password,
          }),
        });

        const data = await response.json();
        if (response.ok) {
          this.$router.push("/login");
        } else if (data.error && data.error.includes("Duplicate")) {
          this.errorMessage = "Email is already in use.";
        } else {
          this.errorMessage = data.error || "Registration unsuccessful.";
        }
      } catch (error) {
        console.error("Error:", error);
        this.errorMessage = "An error occurred. Please try again.";
      } finally {
        this.loading = false;
      }
    },
    navigate(page) {
      this.$router.push(`/${page}`);
    },
    checkLogin() {
      const token = sessionStorage.getItem("token");
      if (token) {
        this.navigate("");
      }
    }
  },
  mounted() {
    this.checkLogin();
  }
};
</script>
<style scoped> 
  .container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    color: white;
  }

  .login-form {
    margin-top: -250px;
    background-color: #3a4553; 
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1); 
    max-width: 500px;
    width: 90%; 
    text-align: center;
    box-sizing: border-box;
  }


  .login-form h1 {
    font-size: 2em;
    margin-bottom: 20px;
  }


  .input-group {
    margin-bottom: 15px;
    text-align: left; 
  }

  .input-group label {
    font-weight: bold;
    margin-bottom: 5px;
    display: block;
  }

  .input-group input {
    width: 100%;
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 5px;
    box-sizing: border-box;
    font-size: 1em;
  }


  button {
    width: 100%;
    padding: 12px;
    font-size: 1.1em;
    background-color: #006d5b; 
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  button:hover {
    background-color: #004d40; 
  }


  .error-message {
    color: red;
    margin-bottom: 15px;
    font-weight: bold;
  }


  .login-form .signup-link {
    margin-top: 15px;
    font-size: 0.9em;
  }

  .login-form .signup-link a {
    color: #33a08b;;
    text-decoration: none;
    font-weight: bold;
  }

  .login-form .signup-link a:hover {
    text-decoration: underline;
  }
</style>
