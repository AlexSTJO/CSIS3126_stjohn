<template>
  <div class="resource-manager-container">
    <h1>Cloud Resource Manager</h1>
    
    <div v-if="resourcesExist" class="resource-exists">
      <p>All required cloud resources already exist.</p>
    </div>
    
    <div v-else>
      <div class="resource-status">
        <div class="resource-step" v-for="(status, resource) in resourceStatus" :key="resource">
          <span class="step-name">{{ resource }}</span>
          <span class="step-status" :class="{ 'completed': status }">{{ status ? '✔' : '⏳' }}</span>
        </div>
      </div>

      <p v-if="permissionsError" class="error-message">{{ permissionsError }}</p>

      <button @click="validatePermissionsAndStart" :disabled="isCreating" class="create-button">
        {{ isCreating ? 'Creating Resources...' : 'Start Resource Check' }}
      </button>
    </div>
  </div>
</template>

<script>
import "@/assets/css/resource-manager.css";
import { API_ENDPOINTS } from "./constants.js";

export default {
  data() {
    return {
      resourceStatus: {},
      isCreating: false,
      resourcesExist: false,
      permissionsError: "",
      responseMessage: ""
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
    async checkResourceExistence() {
      try {
        const response = await fetch(API_ENDPOINTS.RESOURCE_STATUS, {
          headers: {
            "Authorization": `Bearer ${sessionStorage.getItem("token")}`
          }
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        
        this.resourceStatus = data || {};
        this.resourcesExist = Object.values(this.resourceStatus).every(status => status);
      } catch (error) {
        this.responseMessage = `Error: ${error.message}`;
        console.error("Error checking resource existence:", error);
      }
    },
    async validatePermissionsAndStart() {
      this.permissionsError = "";
      try {
        const response = await fetch(API_ENDPOINTS.PERMISSIONS_CHECK, {
          headers: {
            "Authorization": `Bearer ${sessionStorage.getItem("token")}`
          }
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        
        if (data.permissions && Object.keys(data.permissions).length > 0) {
          this.permissionsError = "Missing permissions: " + Object.keys(data.permissions).join(", ");
          return;
        }

        this.startResourceCreation();
      } catch (error) {
        this.permissionsError = `Error checking permissions: ${error.message}`;
        console.error("Permission check failed:", error);
      }
    },
    async startResourceCreation() {
      this.isCreating = true;
      try {
        const response = await fetch(API_ENDPOINTS.START_RESOURCE_CREATION, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${sessionStorage.getItem("token")}`
          }
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        
        this.pollResourceStatus();
      } catch (error) {
        this.responseMessage = `Error: ${error.message}`;
        console.error("Error starting resource creation:", error);
        this.isCreating = false;
      }
    },
    pollResourceStatus() {
      const interval = setInterval(async () => {
        await this.checkResourceExistence();
        if (this.resourcesExist) {
          clearInterval(interval);
          this.isCreating = false;
        }
      }, 3000);
    }
  },
  mounted() {
    this.checkLogin();
    this.checkResourceExistence();
  }
};
</script>


