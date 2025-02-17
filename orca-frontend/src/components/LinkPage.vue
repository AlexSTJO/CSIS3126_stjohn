<template>
    <nav class="navbar">
      <div class="navbar-left">
        <img src="../assets/orca.png" alt="Logo" class="navbar-logo" />
      </div>
      <div class="navbar-center">
          <div class="navbar-brand">Link</div>
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

    <div class="upload-container">
      <h1>Link Your Cloud</h1>
      <form @submit.prevent="submitCredentials">
        <div class="form-group">
          <label for="access_key">Access Key</label>
          <input type="text"
                 id="access_key"
                 v-model="accessKey"
                 placeholder="Enter your Access Key"
                 required />
        </div>
        <div class="form-group">
          <label for="secret_key">Secret Key</label>
          <input type="password"
                 id="secret_key"
                 v-model="secretKey"
                 placeholder="Enter your Secret Key"
                 required />
        </div>
        <div class="form-group">
          <label for="region">Select AWS Region</label>
          <select id="region" v-model="region" required>
            <option value="us-east-1">US East (N. Virginia)</option>
            <option value="us-east-2">US East 2 (Ohio)</option>
            <option value="us-west-1">US West (N. California)</option>
            <option value="eu-central-1">EU (Frankfurt)</option>
            <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
          </select>
        </div>
        <button type="submit" class="submit-button">Upload</button>
      </form>
      <p v-if="responseMessage" class="response-message">{{ responseMessage }}</p>
    </div>
</template>

<script>
import { API_ENDPOINTS } from './constants.js';

export default {
  data() {
    return {
      userID: sessionStorage.getItem("user_id"),
      accessKey: "",
      secretKey: "",
      region: "us-east-2",  
      responseMessage: "",
    };
  },
  methods: {
    navigate(page) {
      this.$router.push(`/${page}`);
    },
    checkLogin() {
      const token = sessionStorage.getItem("token");
      const link_status = sessionStorage.getItem("link_status")
      if (!token || !link_status) {
        this.$router.push(`/`);
      }
    },
    async submitCredentials() {
      try {
        const token = sessionStorage.getItem("token")
        const params = new URLSearchParams({
          user_id: this.userID,
          access_key: this.accessKey,
          secret_key: this.secretKey,
          region: this.region
        });

        const response = await fetch(API_ENDPOINTS.UPLOAD_CREDENTIALS, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": `Bearer ${token}`
          },
          body: params,
        });

        const data = await response.json();
        if (response.ok) {
          sessionStorage.setItem("link_status", "true")
          this.$router.push('/resource-allocation')
        } else {
          this.responseMessage = `Error: ${data.error}`;
        }
      } catch (error) {
        this.responseMessage = `Error: ${error.message}`;
      }
    },
  },
  mounted() {
    this.checkLogin();
  },
};
</script>
<style scoped> 

  .upload-container {
      padding: 30px 40px;
      max-width: 800px;
      margin: 180px auto 20px auto; 
      background-color: white;
      border-radius: 10px;
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
      text-align: center;
      margin-top: 90px;
  }

  .upload-container h1 {
      font-size: 2rem;
      color: #006d5b;
      margin-bottom: 20px;
  }


  .form-group {
      margin: 20px 0;
      text-align: left;
  }

  label {
      font-size: 1rem;
      font-weight: 600;
      color: #004d40;
      display: block;
      margin-bottom: 8px;
  }

  input, select {
      width: 100%;
      padding: 10px 12px;
      font-size: 1rem;
      border: 1px solid #ccc;
      border-radius: 6px;
      box-sizing: border-box;
      transition: border-color 0.3s ease, box-shadow 0.3s ease;
  }

  input:focus, select:focus {
      border-color: #00796b;
      box-shadow: 0 0 6px rgba(0, 121, 107, 0.4);
      outline: none;
  }

  button.submit-button {
      background-color: #00796b;
      color: white;
      font-size: 1rem;
      padding: 12px 20px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      transition: background-color 0.3s ease, transform 0.2s ease;
  }

  button.submit-button:hover {
      background-color: #004d40;
      transform: scale(1.02);
  }


  .response-message {
      margin-top: 20px;
      font-size: 1rem;
      color: #d32f2f;
  }


  pre {
      background-color: #f4f4f4;
      padding: 12px;
      border-left: 4px solid #00796b;
      font-family: 'Consolas', monospace;
      color: #333;
      margin: 20px 0;
      overflow-x: auto;
      border-radius: 6px;
      text-align: left; 
      white-space: pre-wrap; 
  }



  h2 {
      color: #004d40;
      font-size: 1.6rem;
      margin-top: 25px;
      margin-bottom: 10px;
  }
   
</style>
