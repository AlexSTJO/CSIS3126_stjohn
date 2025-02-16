<template>
    <div>
    <nav class="navbar">
            <div class="navbar-left">
                <img src="../assets/orca.png" alt="Logo" class="navbar-logo" />
            </div>
            <div class="navbar-center">
                <div class="navbar-brand">Orca</div>
            </div>
            <ul class="navbar-links">
                <li><a @click="navigate('')">Home</a></li>
            </ul>
        </nav>

        <div class="hub-container">
            <h1>Account Information</h1>

            <p v-if="loading">Loading account information...</p>

            <div v-else>
                <p><strong>Email:</strong> {{ accountInfo.Email || 'N/A' }}</p>
                <p>
                    <strong>Cloud Linked:</strong>
                    <span :class="accountInfo.Linked === 'True' ? 'linked-true' : 'linked-false'">
                        {{ accountInfo.Linked }}
                    </span>
                </p>

                <button class="reset-button" @click="resetCredentials">Reset Credentials</button>
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
  .linked-true {
      color: #388e3c; 
      font-weight: 600;
  }

  .linked-false {
      color: #d32f2f; 
      font-weight: 600;
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

  .reset-button:hover {
      background-color: #b71c1c;
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
