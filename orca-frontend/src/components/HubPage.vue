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
                <li v-if="isLoggedIn">
                    <button class="user-icon-button" @click="navigate('account-info')">
                        <svg class="user-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="white">
                            <circle cx="12" cy="8" r="4" stroke="white" stroke-width="1.5" fill="none" />
                            <path d="M4 20c0-4 4-7 8-7s8 3 8 7" stroke="white" stroke-width="1.5" fill="none" />
                        </svg>
                    </button>
                </li>
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
      },
    },
      mounted() {
        this.checkStatus(); 
    },
}
    
</script>
<style scoped>      
  a {
      color: #00796b;
      text-decoration: none;
      transition: color 0.3s ease;
  }

  a:hover {
      color: #004d40;
  }


  .navbar {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 20px;
      background-color: #004d40;
      color: white;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      z-index: 1000;
      height: 60px;
      box-sizing: border-box;
  }


  .navbar-left, .navbar-center, .navbar-links {
      flex: 1;
      display: flex;
      align-items: center;
  }

  .navbar-center {
      justify-content: center;
  }


  .navbar-logo {
      height: 80px;
      width: auto;
      transition: transform 0.3s ease;
      margin-right: 12px;
  }

  .navbar-logo:hover {
      transform: scale(1.1);
  }


  .navbar-brand {
      font-size: 1.5rem;
      font-weight: 700;
      white-space: nowrap;
  }


  .navbar-links {
      justify-content: flex-end;
      list-style: none;
      margin: 0;
      padding: 0;
  }

  .navbar-links li {
      margin-left: 20px;
  }

  .navbar-links a {
      color: white;
      font-size: 1.1rem;
      padding: 8px 14px;
      border-radius: 6px;
      font-weight: 800;
      text-decoration: none;
      transition: transform 0.2s ease, background-color 0.3s ease;
      white-space: nowrap;
  }

  .navbar-links a:hover {
      background-color: white;
      text-decoration: none;
      color: #004d40;
      transform: scale(1.05);
  }


  .hub-container {
      margin-top: 130px;
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
  .user-icon-button {
      background-color: transparent;
      border: none;
      cursor: pointer;
      padding: 8px;
      border-radius: 50%;
      transition: background-color 0.3s ease, transform 0.2s ease;
  }

  .user-icon-button:hover {
      background-color: rgba(255, 255, 255, 0.2);
      transform: scale(1.05);
  }

  .user-icon {
      width: 28px;
      height: 20px;
      fill: white;
      max-width: 800px;
  }

  .fa-user {
      color: white;
  }

  .link_alert {
      align-items: center;
      margin-top: 20px;
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
