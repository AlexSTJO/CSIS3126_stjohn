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
  <div class="task-container">
    <ul class="task-list">
      <li v-for="task in tasks" :key="task.Name" @click="selectTask(task)">
        <strong>{{ task.Name }}</strong>
      </li>
    </ul>

    <div v-if="selectedTask" class="task-details">
      <h3>Selected Task</h3>
      <p><strong>Name:</strong> {{ selectedTask.Name }}</p>
      <p><strong>Description:</strong> {{ selectedTask.Description }}</p>
      <p><strong>Order:</strong> {{ selectedTask.Order }}</p>
      <p><strong>Inputs:</strong> {{ selectedTask.Inputs.length }} items</p>
      <p><strong>Outputs:</strong> {{ selectedTask.Outputs.length }} items</p>
    </div>
  </div>
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
        const response = await fetch(`${API_ENDPOINTS.GET_PROJECT_TASKS}?project=${encodeURIComponent(this.$route.params.projectname)}`, {
          headers: { "Authorization" : `Bearer ${sessionStorage.getItem("token")}`}
        });
        const data = await response.json();
        if(!response.ok) throw new Error(data.error);
        this.tasks = data;

      } catch(error){
        console.error("Error Listing Projects", error);
      }
    },
    selectTask(task) {
      this.selectedTask = task;
      console.log("Selected Task:", task);
    }
  },
  mounted() {
    this.checkLogin()
    this.listTasks()
  }

}
</script>
<style scoped> 
  .task-container {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;  
  margin-top: 100px;
  }
 
  .task-list {
  list-style: none;
  padding: 0;
  margin-top: 20px;
  }

  .task-list li {
  padding: 10px 15px;
  background: white;
  border: 1px solid #ddd;
  margin: 5px 0;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s, transform 0.1s;
  }

  .task-list li:hover {
  background: #e3e3e3;
  transform: scale(1.02);
  }

  
  .task-details {
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  border: 1px solid #ddd;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  }

  .task-details h3 {
  margin-bottom: 10px;
  color: #333;
  }

  .task-details p {
  margin: 5px 0;
  color: #555;
  }

  .task-details strong {
  color: #000;
  }

  
  .navbar + .task-container {
  margin-top: 20px;
  }
</style> 
