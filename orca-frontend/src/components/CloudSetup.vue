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
                  stroke-width="1"
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
                    stroke-width="1"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="home-icon"
                  >
                    <path d="M3 10L12 3L21 10V20A1 1 0 0 1 20 21H4A1 1 0 0 1 3 20V10Z"></path>
                    <path d="M10 21V14H14V21" stroke="white" fill="none" stroke-linecap="round"></path>   
                  </svg>                    
              </button>
              <button class="icon-button" @click="navigate('logout')">
                  <svg
                    class="icon-svg"
                    xmlns="http://www.w3.org/2000/svg"
                    width="32"
                    height="32"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="white"
                    stroke-width="1"
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
      background-color: #3a4553; 
      z-index: 999; 
  }

  .progress-bar {
      height: 100%;
      background-color: #ffffff; 
      transition: width 0.3s ease;
  }

  
  .hub-container {
      margin-top: 100px; 
      padding: 40px 30px;
      max-width: 850px;
      margin-left: auto;
      margin-right: auto;
      background-color: #2a3644; 
      border-radius: 8px;
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
      border: 1px solid #3a4553;
      text-align: center;
      color: #ffffff; 
  }

  
  .main-heading {
      margin-top: -20px;
      color: #ffffff; 
      font-size: 2rem;
      margin-bottom: 20px;
      font-weight: 600;
  }

  
  .step-card {
      padding: 20px;
      background-color: #1f2933; 
      border: 1px solid #ffffff; 
      border-radius: 8px;
      margin-bottom: 15px;
      cursor: pointer;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
  }

  
  .step-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 6px 12px rgba(255, 255, 255, 0.2);
  }

  
  .step-title {
      color: #ffffff;
      font-size: 1.1rem;
      font-weight: 600;
  }

  
  .step-content {
      margin-top: 10px;
      color: #ffffff;
      font-size: 1rem;
  }

  
  pre {
      text-align: left; 
      white-space: pre-wrap;
      background: #1f2933;
      padding: 10px;
      border-radius: 6px;
      border: 1px solid #ffffff;
      color: #ffffff;
  }

  
  a {
      color: #ffffff;
      text-decoration: none;
      transition: color 0.3s ease;
  }

  a:hover {
      color: #e0e6ed;
      text-decoration: underline;
  }

  
  .button {
      background-color: #ffffff; 
      color: #2a3644; 
      font-size: 1rem;
      padding: 12px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 600;
      transition: background-color 0.3s ease, transform 0.2s ease;
      margin-top: 15px;
  }

  
  .button:hover {
      background-color: #e0e6ed;
      transform: scale(1.03);
  }

  
  @media (max-width: 768px) {
      .hub-container {
          width: 90%;
          padding: 20px;
      }

      .step-card {
          padding: 15px;
      }

      .button {
          width: 100%;
      }
  }
</style>

