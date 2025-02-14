<template>
  <div class="dashboard-container">

    <header class="header">
      <h1>Cloud Resource Manager</h1>
    </header>

    <div class="status-section">
      <div class="status-box">
        <p><strong>Permissions Check:</strong></p>
        <span :class="{'checking': isCheckingPermissions, 'success': permissionsValid, 'error': permissionsError}">
          {{ isCheckingPermissions ? '⏳ Checking...' : permissionsError ? '❌ Failed' : '✔ Passed' }}
        </span>
      </div>
      
      <div class="status-box" v-if="permissionsValid">
        <p><strong>Resource Check:</strong></p>
        <span :class="{'checking': isCheckingResources, 'success': resourcesExist, 'error': !resourcesExist}">
          {{ isCheckingResources ? '⏳ Checking...' : resourcesExist ? '✔ All Resources Exist' : '❌ Some Resources Missing' }}
        </span>
      </div>
    </div>

    
    <section class="resource-section">
      <h2>Cloud Resources</h2>
      <table>
        <thead>
          <tr>
            <th class="resource">Resource</th>
            <th class= "status">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(status, resource) in resourceStatus" :key="resource">
            <td>{{ resource }}</td>
            <td :class="{ 'completed': status, 'not-created': !status }">
              {{ status ? '✔ Available' : '❌ Missing' }}
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <div class="button-section">
      <button 
      @click="handleButtonClick" 
      :disabled="isCreating || !permissionsValid" 
      class="create-button">
      {{ resourcesExist ? 'Go to Home' : isCreating ? 'Creating Resources...' : 'Create Missing Resources' }}
      </button>
    </div>

  </div>
</template>


<script>
import { API_ENDPOINTS } from "./constants.js";
import '@/assets/css/resource-manager.css'
export default {
  data() {
    return {
      resourceStatus: {
        Vpc: false,
        RouteTable: false,
        Subnet: false,
        InternetGateway: false,
        KeyPair: false,
        SecurityGroup: false,
        Ec2: false,
        S3: false
      },
      isCreating: false,
      isCheckingPermissions: true,
      isCheckingResources: false,
      resourcesExist: false,
      permissionsValid: false,
      permissionsError: "",
      responseMessage: ""
    };
  },
  methods: {
    checkLogin() {
      const token = sessionStorage.getItem("token");
      if (!token) {
        this.$router.push(`/`);
      }
    },
    handleButtonClick() {
        if (this.resourcesExist) {
          this.$router.push('/'); 
        } else {
          this.startResourceCreation();
        }
    },
    async validatePermissionsAndCheckResources() {
      this.isCheckingPermissions = true;
      this.permissionsError = "";

      try {
        const response = await fetch(API_ENDPOINTS.PERMISSIONS_CHECK, {
          headers: { "Authorization": `Bearer ${sessionStorage.getItem("token")}` }
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        if (data.permissions && Object.keys(data.permissions).length > 0) {
          this.permissionsError = "Missing permissions: " + Object.keys(data.permissions).join(", ");
          this.isCheckingPermissions = false;
          return;
        }

        this.permissionsValid = true;
        this.isCheckingPermissions = false;
        await this.checkResourceExistence();
      } catch (error) {
        this.permissionsError = `Error checking permissions: ${error.message}`;
        this.isCheckingPermissions = false;
        console.error("Permission check failed:", error);
      }
    },
    async checkResourceExistence() {
      if (!this.permissionsValid) return;

      this.isCheckingResources = true;
      try {
        const response = await fetch(API_ENDPOINTS.RESOURCE_STATUS, {
          headers: { "Authorization": `Bearer ${sessionStorage.getItem("token")}` }
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        Object.keys(this.resourceStatus).forEach(resource => {
          this.resourceStatus[resource] = data[resource] && data[resource] !== "" ? true : false;
        });

        this.resourcesExist = Object.values(this.resourceStatus).every(status => status);
      } catch (error) {
        this.permissionsError = `Error checking resources: ${error.message}`;
        console.error("Error checking resource existence:", error);
      } finally {
        this.isCheckingResources = false;
      }
    },
    async startResourceCreation() {
      this.isCreating = true;
      try {
        const response = await fetch(API_ENDPOINTS.RESOURCE_CREATE, {
          method: "GET",
          headers: { "Authorization": `Bearer ${sessionStorage.getItem("token")}` }
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        await this.checkResourceExistence();
      } catch (error) {
        console.error("Error creating resources:", error);
      } finally {
        this.isCreating = false;
      }
    }
  },
  mounted() {
    this.checkLogin();
    this.validatePermissionsAndCheckResources();
  }
};
</script>

