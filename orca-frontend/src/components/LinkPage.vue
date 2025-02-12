<template>
    <nav class="navbar">
        <div class="navbar-brand">Orca</div>
        <ul class="navbar-links">
          <li><a @click="navigate('')">Home</a></li>
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
import "@/assets/css/credential_upload.css";
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
