<template>
  <nav class="navbar">
    <div class="navbar-left">
        <img src="../assets/orca.png" alt="Logo" class="navbar-logo" />
    </div>
    <div class="navbar-center">
        <div class="navbar-brand">Cloud Creation</div>
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
</template>
<script>
import { API_ENDPOINTS } from "./constants.js";
export default {
  data() {
    return {
      tasks: [],
      selectedTask: null
    }
  },
  methods: {
    navigate(page) {
        this.$router.push(`/${page}`);
    },
    checkLogin() {
      const token = sessionStorage.getItem("token");
      const link_status = sessionStorage.getItem("link_status"); 
      if (!token || link_status === "false") {
        this.navigate("/");
      }
    },
    async listTasks() {
      try {
        console.log(this.$route.params.projectname);
        const response = await fetch(`${API_ENDPOINTS.GET_PROJECT_TASKS}?project=${encodeURIComponent(this.$route.params.projectname)}`, {
          headers: { "Authorization" : `Bearer ${sessionStorage.getItem("token")}`}
        });
        const data = await response.json();
        if(!response.ok) throw new Error(data.error);
        this.tasks = data;

      } catch(error){
        console.error("Error Listing Projects", error);
      }
    }
  },
  mounted() {
    this.checkLogin()
    this.listTasks()
  }

}
</script>
  
