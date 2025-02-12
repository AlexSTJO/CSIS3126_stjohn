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
import '@/assets/css/account-info.css'
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
