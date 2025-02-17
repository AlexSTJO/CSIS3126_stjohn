<template>
    <div>
        <nav class="navbar">
            <div class="navbar-left">
                <img src="../assets/orca.png" alt="Logo" class="navbar-logo" />
            </div>
            <div class="navbar-center">
                <div class="navbar-brand">Cloud Creation</div>
            </div>
            <ul class="navbar-links">
              <button class="icon-button" @click="navigate('account-info')">
                <svg
                  class="icon-svg"
                  xmlns="http://www.w3.org/2000/svg"
                  width="32"
                  height="32"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="white"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="12" cy="8" r="4" stroke="white" />
                  <path d="M4 20c0-4 4-7 8-7s8 3 8 7" stroke="white" />
                </svg>
              </button>

              <button class="icon-button" @click="navigate('')">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="32"
                    height="32"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="white"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="home-icon"
                  >
                    <path d="M3 10L12 3L21 10V20A1 1 0 0 1 20 21H4A1 1 0 0 1 3 20V10Z"></path>
                    <path d="M10 21V14H14V21" stroke="white" fill="none" stroke-linecap="round"></path>   
                  </svg>                    
              </button>
              <button class="icon-button" @click="logout">
                  <svg
                    class="icon-svg"
                    xmlns="http://www.w3.org/2000/svg"
                    width="32"
                    height="32"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="white"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M9 16l-4-4 4-4" />
                    <path d="M5 12h12" />
                    <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                  </svg>
                </button>
                    
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
                    <button v-if="step.policy" class="button" @click.stop="copyToClipboard(step.policy, index)">
                        {{ copiedIndex === index ? 'Copied!' : 'Copy JSON' }}
                    </button>
                    <button
                        v-if="step.requiresUpload"
                        class="button"
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
  
  pre {
    text-align: left; 
    white-space: pre-wrap; 
  }

  a {
      color: #00796b;
      text-decoration: none;
      transition: color 0.3s ease;
  }

   a:hover {
      color: #004d40;
      text-decoration: underline;
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

  .button {
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

  .button:hover {
      background-color: #004d40;
      transform: scale(1.02);
  }
    
</style>

