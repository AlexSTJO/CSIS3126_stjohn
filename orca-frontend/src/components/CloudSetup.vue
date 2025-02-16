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
                <li v-if="isLoggedIn">
                    <a class="dropdown-toggle" @click="toggleDropdown">Account</a>
                    <ul v-if="showDropdown" class="dropdown-menu">
                        <li><a @click="navigate('profile')">Profile</a></li>
                        <li><a @click="navigate('logout')">Logout</a></li>
                    </ul>
                </li>
            </ul>
        </nav>

        <div class="progress-bar-container">
            <div class="progress-bar" :style="{ width: progress + '%' }"></div>
        </div>

        <div class="hub-container">
            <h1 class="main-heading">Setting Up an AWS Cloud User</h1>

            <div v-for="(step, index) in steps" :key="index" class="step-card" @click="toggleStep(index)">
                <h2 class="step-title">{{ step.title }}</h2>
                <div v-if="activeStep === index" class="step-content">
                    <p v-html="step.content"></p>
                    <pre v-if="step.policy">{{ JSON.stringify(step.policy, null, 2) }}</pre>
                    <button v-if="step.policy" class="copy-button" @click.stop="copyToClipboard(step.policy, index)">
                        {{ copiedIndex === index ? 'Copied!' : 'Copy JSON' }}
                    </button>
                    <button
                        v-if="step.requiresUpload"
                        class="upload-button"
                        @click.stop="navigateToUpload"
                    >
                        Upload Cloud Credentials
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { steps } from "@/assets/steps";
export default {
    data() {
        return {
            isLoggedIn: false,
            activeStep: null,
            steps: steps,
            progress: 0,
            showDropdown: false,
            copiedIndex: null
        };
    },
    methods: {
        navigate(page) {
            this.$router.push(`/${page}`);
        },
        checkLogin() {
            const token = sessionStorage.getItem("token");
            this.isLoggedIn = !!token;
        },
        toggleStep(index) {
            this.activeStep = this.activeStep === index ? null : index;
            this.updateProgress();
        },
        updateProgress() {
            const completedSteps = this.steps.filter((_, index) => index <= this.activeStep).length;
            this.progress = (completedSteps / this.steps.length) * 100;
        },
        navigateToUpload() {
            this.$router.push('/link');  
        },
        toggleDropdown() {
            this.showDropdown = !this.showDropdown;
        },
        async copyToClipboard(jsonData, index) {
            try {
                await navigator.clipboard.writeText(JSON.stringify(jsonData, null, 2));
                this.copiedIndex = index;
                setTimeout(() => { this.copiedIndex = null; }, 2000);
            } catch (error) {
                console.error("Failed to copy: ", error);
            }
        }
    },
    mounted() {
        this.checkLogin();
    }
};
</script>
<style scoped>

  .navbar {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 20px;
      background-color: #004d40;
      color: white;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      z-index: 1000;
      font-size: 0.95rem;
      height: 50px; 
  }


  .navbar-logo {
      height: 70px; 
      width: auto;
      position: relative;
      top: 0px; 
      transition: transform 0.3s ease;
      margin: 0 10px;
  }

  .navbar-left {
      display: flex;
      align-items: center;
  }

  .navbar-logo:hover {
      transform: scale(1.1);
  }

  .navbar-brand {
      font-size: 1.4rem;
      font-weight: 700;
  }


  .navbar-links {
      display: flex;
      list-style: none;
      margin: 0;
      padding: 0;
  }

  .navbar-links li {
      position: relative;
      margin-left: 20px;
  }

  .navbar-links a {
      color: white;
      padding: 8px 12px;
      border-radius: 4px;
      transition: background-color 0.3s ease;
  }

  .navbar-links a:hover {
      background-color: white;
      color: #004d40;
  }


  .dropdown-menu {
      position: absolute;
      top: 100%;
      left: 0;
      display: none;
      background-color: white;
      min-width: 180px;
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
      border-radius: 6px;
      overflow: hidden;
      z-index: 999;
  }

  .navbar-links li:hover .dropdown-menu {
      display: block;
      animation: dropdown-slide 0.3s ease forwards;
  }

  .dropdown-item {
      padding: 10px 15px;
      color: #004d40;
      transition: background-color 0.3s ease;
  }

  .dropdown-item:hover {
      background-color: #004d40;
      color: white;
  }


  @keyframes dropdown-slide {
      from {
          opacity: 0;
          transform: translateY(-10px);
      }
      to {
          opacity: 1;
          transform: translateY(0);
      }
  }


  .progress-bar-container {
      position: fixed;
      top: 70px; 
      left: 0;
      width: 100%;
      height: 8px;
      background-color: #ddd;
      z-index: 999; 
  }

  .progress-bar {
      height: 100%;
      background-color: #00796b;
      transition: width 0.3s ease;
  }


  .hub-container {
      margin-top: 100px; 
      padding: 40px 30px;
      max-width: 850px;
      margin-left: auto;
      margin-right: auto;
      background-color: white;
      border-radius: 12px;
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
      text-align: center;
  }
  .main-heading {
      margin-top: -20px;
      color: #004d40;
      font-size: 2.0rem;
      margin-bottom: 20px;
      font-weight: 400;
  }


  .step-card {
      padding: 20px;
      background-color: #e0f2f1;
      border: 1px solid #00796b;
      border-radius: 10px;
      margin-bottom: 15px;
      cursor: pointer;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
  }

  .step-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  }

  .step-title {
      color: #00796b;
      font-size: 1.0rem;
  }

  .step-content {
      margin-top: 10px;
      color: #333;
      font-size: 1rem;
  }

  .upload-button {
      background-color: #00796b;
      color: white;
      font-size: 1rem;
      padding: 12px 20px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      transition: background-color 0.3s ease, transform 0.2s ease;
      margin-top: 15px;
  }

  .upload-button:hover {
      background-color: #004d40;
      transform: scale(1.02);
  }
    
</style>

