<template>
  <nav class="navbar">
    <div class="navbar-left">
        <img src="../assets/orca.png" alt="Logo" class="navbar-logo" />
    </div>
    <div class="navbar-center">
        <div class="navbar-brand">Dashboard</div>
    </div>
    <ul v-if="!isLoggedIn" class="navbar-links">
        <li><a @click="navigate('login')">Login</a></li>
        <li><a @click="navigate('register')">Register</a></li>
    </ul>
    <ul v-if="isLoggedIn" class="navbar-links">
       <button class="icon-button" @click="navigate('account-info')">
        <svg
          class="icon-svg"
          xmlns="http://www.w3.org/2000/svg"
          width="31"
          height="31"
          viewBox="-1 0 24 24"
          fill="none"
          stroke="white"
          stroke-width="1"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="11" cy="8" r="4" stroke="white" />
          <path d="M3 20c0-4 4-7 8-7s8 3 8 7" stroke="white" />
        </svg>
      </button>
      <button class="icon-button" @click="navigate('logout')">
        <svg
          class="icon-svg"
          xmlns="http://www.w3.org/2000/svg"
          width="31"
          height="31"
          viewBox="-1 0 24 24"
          fill="none"
          stroke="white"
          stroke-width="1"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M8 16l-4-4 4-4" />
          <path d="M4 12h12" />
          <path d="M14 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
        </svg>
      </button>
    </ul>
  </nav>
  <div v-if="!isLinked && isLoggedIn" class="link_alert">
    <p>Your cloud is not linked, please proceed to <a class="linkpage" @click="navigate('link')">Cloud Setup</a></p>
  </div>
  <div class="hub-container">
      <h1>Orca</h1>
      <p>
          Orca provides a streamlined solution by automating the linking, execution, and management of cloud resources.
      </p>
  </div>
</template>
<script>
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
        if (this.isLoggedIn && this.isLinked) {
          this.navigate('dashboard')
        }
      },
    },
      mounted() {
        this.checkStatus(); 
    },
}
    
</script>
<style scoped>       
  .hub-container {
      margin-top: 90px;
      padding: 40px 30px;
      max-width: 800px;
      margin-left: auto;
      margin-right: auto;
      background-color: white;
      border-radius: 12px;
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
      text-align: center;
  }

  h1 {
      color: #004d40;
      font-size: 2.2rem;
      font-weight: 700;
      margin-bottom: 20px;
  }

  p {
      font-size: 1.1rem;
      color: #333;
      line-height: 1.8;
      margin: 10px 0;
      text-align: justify;
  }
  
  .fa-user {
      color: white;
  }

  .link_alert {
      align-items: center;
      margin-top: 80px;
      padding: 10px 10px;
      max-width: 1000px;
      margin-left: auto;
      margin-right: auto;
      background-color: #ea6c6c;
      border-radius: 12px;
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
      text-align: center;}
  .linkpage {
      color: #FFFFFF;
      text-decoration: none;
      transition: color 0.3s ease;
      cursor: pointer; 
  }

  .linkpage:hover {
      color: #8B0000;
      text-decoration: none;
  }


  @media (max-width: 768px) {
      .navbar-links {
          display: none;
      }

      .navbar {
          padding: 10px 20px;
      }

      .hub-container {
          padding: 20px;
      }

      h1 {
          font-size: 1.8rem;
      }

      p {
          font-size: 1rem;
      }
  }

</style>
