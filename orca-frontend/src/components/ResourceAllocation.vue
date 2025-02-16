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
<style scoped>
  body {
    font-family: "Inter", sans-serif;
    background: #f4f6f8;
    margin: 0;
  }

  .dashboard-container {
    max-width: 850px;
    margin-right: auto;
    margin-left: auto;
    margin-top: 0px;
    padding: 30px;
    padding-top:10px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
  }

  .header h1 {
    font-size: 2rem;
    text-align: center;
    color: #004d40;
    margin-bottom: 25px;
    font-weight: bold;
  }

  .status-section {
    background: #ffffff;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #d1d5db;
    display: flex;
    gap: 15px;
    justify-content: center;
  }

  .status-box {
    font-size: 1.2rem;
    font-weight: bold;
    padding: 15px;
    border-radius: 8px;
    background: #f9fafb;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    text-align: left;
    width: 100%;
  }

  .status-box .checking {
    color: orange;
  }

  .status-box .success {
    color: green;
  }

  .status-box .error {
    color: red;
  }

  .resource-section {
    background: #ffffff;
    padding: 25px;
    padding-top: 0px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #d1d5db;
    text-align: center;
  }

  .resource-section h2 {
    color: #004d40;
    font-size: 1.5rem;
    margin-bottom: 15px;
    font-weight: bold;
  }

  .resource-section table {
    width: 100%;
    border-collapse: collapse;
  }

  .resource-section th, .resource-section td {
    padding: 14px;
    border-bottom: 1px solid #ddd;
    text-align: left;
  }
  .resource {
    border-radius: 4px 0 0 4px;
  }
  .status {
    border-radius: 0px 4px 4px 0px;
  }
  .completed {
    color: green;
  }
  .not-created {
    color: red;
  }

  .resource-section th {
    background: #004d40;
    color: white;
    text-transform: uppercase;
    font-size: 1rem;
  }

  .button-section {
    text-align: center;
    margin-top: 25px;
    background: white;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #d1d5db;
  }

  .create-button {
    font-size: 1.1rem;
    padding: 12px 18px;
    background: #004d40;
    width: 100%;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
    transition: background 0.3s ease, transform 0.2s ease;
  }

  .create-button:hover {
    background: #00796b;
    transform: translateY(-2px);
  }

  .create-button:disabled {
    background: gray;
    cursor: not-allowed;
    opacity: 0.6;
  }

  @media (max-width: 768px) {
    .dashboard-container {
      width: 90%;
      padding: 20px;
    }

    .status-section {
      flex-direction: column;
      align-items: center;
    }

    .status-box {
      width: 100%;
    }

    .resource-section {
      padding: 20px;
    }
  }
 
</style>

