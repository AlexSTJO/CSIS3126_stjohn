<template>
  <nav class="navbar">
    <div class="navbar-left">
        <img src="../assets/orca.png" alt="Logo" class="navbar-logo" />
    </div>
    <div class="navbar-center">
        <div class="navbar-brand">Dashboard</div>
    </div>
    <ul class="navbar-links">
       <button class="icon-button" @click="navigate('account-info')">
        <svg
          class="icon-svg"
          xmlns="http://www.w3.org/2000/svg"
          width="31"
          height="31"
          viewBox="-1 0 24 24"
          fill="none"
          stroke="white"
          stroke-width="1"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="11" cy="8" r="4" stroke="white" />
          <path d="M3 20c0-4 4-7 8-7s8 3 8 7" stroke="white" />
        </svg>
      </button>
      <button class="icon-button" @click="navigate('logout')">
        <svg
          class="icon-svg"
          xmlns="http://www.w3.org/2000/svg"
          width="31"
          height="31"
          viewBox="-1 0 24 24"
          fill="none"
          stroke="white"
          stroke-width="1"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M8 16l-4-4 4-4" />
          <path d="M4 12h12" />
          <path d="M14 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
        </svg>
      </button>
    </ul>
  </nav>
  <div class="container">
    <div class="sidebar-container">
      <aside class="sidebar">
        <h2>Projects</h2>
        <ul class="project-list">
          <li v-for="(project, index) in projectList" :key="index" class="project-item">
            <router-link class="link" :to="`/project/${project}`">
              {{ project }}
            </router-link>         
          </li>
        </ul>
        <button class="create-btn" @click="showCreateModal = true">+ New Project</button>
      </aside>
    </div>
  </div>
  <CreateProjectModal
  v-if="showCreateModal"
  @close="showCreateModal = false"
  @created="handleProjectCreated"
  />
</template>
<script>
import { API_ENDPOINTS } from  "./constants.js";
import CreateProjectModal from "./CreateProjectModal.vue";
  export default {
    components: {
      CreateProjectModal,
    },
    data() {
      return {
        projectList: [],
        showCreateModal: false
      }
    },
    methods: {
      navigate(page) {
        this.$router.push(`/${page}`);
      },
      checkLogin() {
        const token = sessionStorage.getItem("token");
        const link_status = sessionStorage.getItem("link_status");
        console.log(link_status)
        if (!token || link_status === false) {
          this.navigate('')
        }
      },
      async listProjects() {
        try {
          const response = await fetch(API_ENDPOINTS.LIST_PROJECTS, {
            headers: { "Authorization" : `Bearer ${sessionStorage.getItem("token")}`}
          });

          const data = await response.json();
          if(!response.ok) throw new Error(data.error);
          this.projectList = data;
          console.log(this.projectList)
        } catch (error){
          console.error("Error Listing Projects", error);
        }
      },
      handleProjectCreated(newProjectName) {
        this.projectList.push(newProjectName);
        this.$router.push(`/project/${newProjectName}`);
      }
    
    },
    mounted() {
      this.checkLogin();
      this.listProjects();
    }
  }
</script>

<style scoped>
  .container {
    display: flex; 
    height: calc(100vh - 80px);
    margin-top: 80px;
  }

  .sidebar {
  width: 300px;
  background: #232f3e; 
  color: #ffffff;
  padding: 20px;
  height: calc(100vh - 80px);
  overflow-y: auto;
  border-right: 1px solid #3a4553; 
  padding-top: 0px;
}

.sidebar h2 {
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #3a4553; 
  padding-bottom: 5px;
}

.project-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.link {
  padding: 10px 12px;
  margin: 5px 0;
  background: #37475a; 
  border: 1px solid #4a5b6a; 
  color: white;
  text-decoration: none;
  border-radius: 2px; 
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: background 0.2s ease-in-out, border-color 0.2s;
}

.project-item:hover {
  background: #485769; 
  border-color: #596775;
}

.project-item:active {
  background: #3a4553; 
}

.create-btn {
  width: 100%;
  margin-bottom: 15px;
  background: #006d5b;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}
.create-btn:hover {
  background: #004d40;
}



</style>
