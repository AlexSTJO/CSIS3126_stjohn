<template>
  <nav class="navbar">
    <div class="navbar-left">
        <img src="../assets/orca.png" alt="Logo" class="navbar-logo" />
    </div>
    <div class="navbar-center">
        <div class="navbar-brand">Cloud Resource Manager</div>
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

  <div class="dashboard-container">
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
    navigate(page) {
      this.$router.push(`/${page}`);
    },
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
    
  .dashboard-container {
      color: #e0e6ed; 
      max-width: 900px;
      margin: auto;
      margin-top: 80px;
      padding: 25px;
      background: #2a3644;
      border-radius: 6px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
      border: 1px solid #3a4553;
  }


  .status-section {
      background: #1f2933;
      padding: 20px;
      border-radius: 6px;
      border: 1px solid #3a4553;
      display: flex;
      gap: 15px;
      justify-content: center;
  }


  .status-box {
      font-size: 1.1rem;
      font-weight: 600;
      padding: 14px;
      border-radius: 4px;
      background: #2a3644;
      box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
      text-align: left;
      width: 100%;
      border: 1px solid #3a4553;
  }


  .resource-section {
      background: #1f2933;
      padding: 20px;
      border-radius: 6px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
      border: 1px solid #3a4553;
      text-align: left;
  }


  .resource-section table {
      width: 100%;
      border-collapse: collapse;
  }

  .resource-section th {
      background: #37475a;
      color: white;
      text-transform: uppercase;
      font-weight: 700;
  }


  .resource-section th, .resource-section td {
      padding: 12px;
      border-bottom: 1px solid #3a4553;
      text-align: left;
      font-size: 1rem;
      color: white; 
  }

  .completed {
    color: #66bb6a !important; 
  }

  .success {
    color: #66bb6a !important;
  }
  .not-created { 
    color: #e57373 !important; 
  }

  .error {
    color: #e57373 !important;
  }

  .create-button {
      font-size: 1rem;
      padding: 12px 18px;
      background: #ff9900;
      width: 100%;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
      text-transform: uppercase;
      transition: background 0.3s ease, box-shadow 0.2s ease;
  }


  .create-button:hover {
      background: #e88e00;
      box-shadow: 0 0 10px rgba(255, 153, 0, 0.6);
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
          padding: 18px;
      }
  }
   
</style>

