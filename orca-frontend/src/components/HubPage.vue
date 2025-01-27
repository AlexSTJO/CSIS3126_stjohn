<template>
    <div>
      <nav class="navbar">
        <div class="navbar-left">
            <img src="../assets/orca.png" alt="Logo" class="navbar-logo" />
        </div>
        <div class="navbar-center">
            <div class="navbar-brand">Orca</div>
        </div>
        <ul class="navbar-links">
          <li v-if="!isLoggedIn"><a @click="navigate('login')">Login</a></li>
          <li v-if="!isLoggedIn"><a @click="navigate('register')">Register</a></li>
          <li v-if="isLoggedIn"><a @click="navigate('link')">Link Cloud Account</a></li>
        </ul>

      </nav>
  
      <div class="hub-container">
        <h1>Orca</h1>
        <p>
            Orca provides a streamlined solution by automating the linking, execution, and management of cloud resources. It eliminates manual overhead, prevents bottlenecks, and ensures reliable task execution through features like SQS-driven order enforcement. By saving time, reducing costs, and simplifying cloud workflows, Orca empowers users to focus on their core objectives.
        </p>
      </div>
    </div>
</template>
  
<script>
  import "@/assets/css/theme.css";
  export default {
    data() {
        return {
            isLoggedIn: false
        };
    },
    methods: {
      navigate(page) {
        this.$router.push(`/${page}`);
      },
      checkLogin() {
        const token = sessionStorage.getItem("token");
        if (token) {
            this.isLoggedIn = true;
        } else {
            this.isLoggedIn = false;
        }
      }
    },
      mounted() {
        this.checkLogin(); 
    },
  }
    
</script>
  