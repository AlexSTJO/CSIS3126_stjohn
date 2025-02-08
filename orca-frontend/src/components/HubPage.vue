<template>
    <div>
        <!-- Navbar -->
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
                <!-- User Icon Button -->
                <li v-if="isLoggedIn">
                    <button class="user-icon-button" @click="navigate('account-info')">
                        <!-- SVG Icon -->
                        <svg class="user-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="white">
                            <circle cx="12" cy="8" r="4" stroke="white" stroke-width="1.5" fill="none" />
                            <path d="M4 20c0-4 4-7 8-7s8 3 8 7" stroke="white" stroke-width="1.5" fill="none" />
                        </svg>
                    </button>
                </li>
            </ul>
        </nav>

        <!-- Hub Content -->
        <div class="hub-container">
            <h1>Orca</h1>
            <p>
                Orca provides a streamlined solution by automating the linking, execution, and management of cloud resources.
            </p>
        </div>
    </div>
</template>
  
<script>
  import "@/assets/css/theme.css";
  export default {
    data() {
        return {
            isLoggedIn: false,
            isLinked: false
        };
    },
    methods: {
      navigate(page) {
        this.$router.push(`/${page}`);
      },
      checkStatus() {
        const token = sessionStorage.getItem("token");
        this.isLoggedIn = !!token;  
        const linkStatus = sessionStorage.getItem("link_status");
        this.isLinked = linkStatus === "true";
      },
    },
      mounted() {
        this.checkStatus(); 
    },
}
    
</script>
  
