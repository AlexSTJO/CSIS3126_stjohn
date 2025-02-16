<template>
    <nav class="navbar">
      <div class="navbar-left">
        <img src="../assets/orca.png" alt="Logo" class="navbar-logo" />
      </div>
      <div class="navbar-center">
          <div class="navbar-brand">Orca</div>
      </div>
      <ul class="navbar-links">
         <li ><a @click="navigate('')">Home</a></li>
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
      if (!token) {
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
          this.$router.push('/')
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
 
  
  a {
      color: #00796b;
      text-decoration: none;
      transition: color 0.3s ease;
  }

  a:hover {
      color: #004d40;
      text-decoration: underline;
  }

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
