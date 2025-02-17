<template>
    <div>
    <nav class="navbar">
            <div class="navbar-left">
                <img src="../assets/orca.png" alt="Logo" class="navbar-logo" />
            </div>
            <div class="navbar-center">
                <div class="navbar-brand">Account</div>
            </div>
            <ul class="navbar-links">
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

        <div class="hub-container">
            <p v-if="loading">Loading account information...</p>

            <div v-else>
                <p><strong>Email:</strong> {{ accountInfo.Email || 'N/A' }}</p>
                <p>
                    <strong>Cloud Linked:</strong>
                    <span :class="accountInfo.Linked === 'True' ? 'linked-true' : 'linked-false'">
                        {{ accountInfo.Linked }}
                    </span>
                </p>
                <div class="button-container">
                  <button class="reset-button" @click="resetCredentials">Reset Credentials</button>
                  <button class="resource-manager-button" @click="navigate('resource-allocation')">Resource Manager</button>
                </div>
            </div>

            <p v-if="resetMessage" class="reset-message">{{ resetMessage }}</p>
            <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        </div>
    </div>
</template>
<script>
import {API_ENDPOINTS} from './constants.js'
export default {
    data() {
        return {
            isLoggedIn: false,
            accountInfo: {},      
            loading: true,        
            errorMessage: "",     
            resetMessage: ""      
        };
    },
    methods: {
        navigate(page) {
            this.$router.push(`/${page}`);
        },
        checkLogin() {
            const token = sessionStorage.getItem("token");
            this.isLoggedIn = !!token;
            
            if (!this.isLoggedIn) {
                this.navigate('login');
            }
        },
        async fetchAccountInfo() {
            try {
                const token = sessionStorage.getItem("token")
                const response = await fetch(`${API_ENDPOINTS.GET_ACCOUNT_INFO}`, {
                    method: "GET",
                    headers: {
                      "Authorization": `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    throw new Error("Failed to fetch account information.");
                }

                const data = await response.json();
                this.accountInfo = data;
            } catch (error) {
                this.errorMessage = error.message;
            } finally {
                this.loading = false;
            }
        },
        async resetCredentials() {
            const token = sessionStorage.getItem("token");
 
            try {
                this.resetMessage = "";  
                this.errorMessage = "";

                const response = await fetch(`${API_ENDPOINTS.CREDENTIAL_RESET}`, {
                    method: "GET",
                    headers: {
                      "Authorization": `Bearer ${token}`
                    }

                });

                if (!response.ok) {
                    throw new Error(`Failed to reset credentials. HTTP Status: ${response.status}`);
                } else {
                    sessionStorage.setItem("link_status", "false")
                }
                
                const data = await response.json();
                this.resetMessage = data.message;  
                await this.fetchAccountInfo();     
            } catch (error) {
                this.errorMessage = error.message;
            }
        }
    },
    mounted() {
        this.checkLogin();       
        this.fetchAccountInfo(); 
    }
};
</script>
<style scoped>
  .hub-container {
      margin-top: 130px;
      padding: 40px 30px;
      max-width: 800px;
      margin-left: auto;
      margin-right: auto;
      background-color: white;
      border-radius: 12px;
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
      text-align: left;
  }
 
  .icon-button:hover {
    transform: scale(1.1);
  }
  .linked-true {
      color: #388e3c; 
      font-weight: 600;
  }

  .linked-false {
      color: #d32f2f; 
      font-weight: 600;
  }

  .button-container {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 80px;
  }

  .reset-button {
      background-color: #d32f2f;
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

  .resource-manager-button {
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

  .reset-button:hover {
      background-color: #b71c1c;
      transform: scale(1.02);
  }

  .resource-manager-button:hover {
    background-color: #004d40;
    transform: scale(1.02);
  }

  .reset-message {
      color: #388e3c;
      font-weight: 600;
      margin-top: 10px;
  }

  .error-message {
      color: #d32f2f;
      font-weight: 600;
      margin-top: 10px;
  }
   
</style>
