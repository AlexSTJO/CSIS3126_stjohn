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
        <button type="submit" class="submit-button">Upload</button>
      </form>
      <p v-if="responseMessage" class="response-message">{{ responseMessage }}</p>
    </div>
</template>
<script>
import "@/assets/css/credential_upload.css";
import { API_ENDPOINTS } from './constants.js';

export default {
  data () {
    return {
      userID: sessionStorage.getItem("user_id"),
      accessKey: "",
      secretKey: "",
      responseMessage: "",
    };
  },
  methods: {
    navigate(page){
      this.$router.push(`/${page}`);
    },
    checkLogin() {
      const token = sessionStorage.getItem("token");
      if (!token){
        this.$router.push(`/`)
      }
    },
    async submitCredentials() {
      try {
        const params = new URLSearchParams({
          user_id:this.userID,
          access_key: this.accessKey,
          secret_key: this.secretKey
        })
        const response = await fetch(API_ENDPOINTS.UPLOAD_CREDENTIALS, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: params
        });
        const data = await response.json();
        if (response.ok) {
          this.responseMessage = data.message;
        } else {
          this.responseMessage = `Error: ${data.error}`;
        }
      } catch (error) {
        this.responseMessage = `Error: ${error.message}`;
      } 
    }
    },
  mounted(){
    this.checkLogin()
  }
}
</script>
