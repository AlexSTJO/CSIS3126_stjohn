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
import "@/assets/css/auth-form.css";

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

      // Input validation
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
        const response = await fetch("https://astjo.site/api/register", {
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
  },
};
</script>
