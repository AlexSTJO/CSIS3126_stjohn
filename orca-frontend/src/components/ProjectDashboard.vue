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
        <svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="8" r="4" stroke="white" />
          <path d="M4 20c0-4 4-7 8-7s8 3 8 7" stroke="white" />
        </svg>
      </button>

      <button class="icon-button" @click="navigate('')">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 10L12 3L21 10V20A1 1 0 0 1 20 21H4A1 1 0 0 1 3 20V10Z"></path>
            <path d="M10 21V14H14V21" stroke="white" fill="none" stroke-linecap="round"></path>   
          </svg>                    
      </button>

      <button class="icon-button" @click="navigate('logout')">
          <svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 16l-4-4 4-4" />
            <path d="M5 12h12" />
            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
          </svg>
      </button>        
    </ul>
  </nav>

  <div class="container">
    <aside class="sidebar">
      <h2>Tasks</h2>
      <ul class="project-list">
        <li v-for="task in tasks" :key="task.Name" :class="{'selected': task === selectedTask}" class="link" @click="selectTask(task)">
          {{ task.Name }}
        </li>
      </ul>
    </aside>

    <transition name="fade" mode="out-in">
      <div class="task-details" v-if="selectedTask" key="task-details">
        <div class="task-details-container">
          <div class="task-info">
            <div class="task-row">
              <strong>Name:</strong>
              <input v-if="isEditing" v-model="selectedTask.Name" class="edit-field" />
              <span v-else>{{ selectedTask.Name }}</span>
            </div>
            <div class="task-row">
              <strong>Description:</strong> 
              <textarea v-if="isEditing" v-model="selectedTask.Description" class="edit-field"></textarea>
              <span v-else>{{ selectedTask.Description }}</span>
            </div>
            <div class="task-row">
              <strong>Order:</strong> 
              <input v-if="isEditing" type="number" v-model="selectedTask.Order" class="edit-field" />
              <span v-else>{{ selectedTask.Order }}</span>
            </div>
          </div>

          <div class="task-section">
            <div class="task-label">Inputs</div>
            <ul class="task-list">
              <li v-for="input in selectedTask.Inputs" :key="input" class="task-item">
                {{ input }}
              </li>
            </ul>
          </div>

          <div class="task-section">
            <div class="task-label">Outputs</div>
            <ul class="task-list">
              <li v-for="output in selectedTask.Outputs" :key="output" class="task-item">
                {{ output }}
              </li>
            </ul>
          </div>
        </div>

        <button class="task-button" @click="toggleEditMode">{{ isEditing ? 'Save' : 'Edit' }}</button>
      </div>
    </transition>
  </div>
</template>

<script>
import { API_ENDPOINTS } from "./constants.js";
export default {
  data() {
    return {
      tasks: [],
      selectedTask: null,
      isEditing: false
    };
  },
  methods: {
    navigate(page) {
      this.$router.push(`/${page}`);
    },
    checkLogin() {
      const token = sessionStorage.getItem("token");
      const link_status = sessionStorage.getItem("link_status"); 
      if (!token || link_status !== "true") {
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

        if (this.tasks.length > 0) {
          this.selectedTask = this.tasks[0];
        }
      } catch (error) {
        console.error("Error Listing Projects", error);
      }
    },
    selectTask(task) {
      this.selectedTask = task;
      console.log("Selected Task:", task);
    },
    toggleEditMode() {
      this.isEditing = !this.isEditing;
    }
  },
  mounted() {
    this.checkLogin();
    this.listTasks();
  }
};
</script>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  padding: 20px; 
}

.sidebar {
  width: 280px;
  background: #1f2937; 
  color: white;
  padding: 20px;
  height: 100vh;
  overflow-y: auto;
  border-right: 1px solid #374151;
  transition: all 0.3s;
}

.sidebar h2 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  text-align: center;
}

.project-list {
  list-style: none;
  padding: 0;
}

.link {
  padding: 12px;
  background: #374151;
  margin: 5px 0;
  border-radius: 5px;
  cursor: pointer;
  transition: 0.3s;
}

.link:hover, .link.selected {
  background: #475569;
}

.task-details {
  flex: 1;
  padding: 20px;
  color: white;
}

.task-details-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: #1f2937;
  padding: 25px;
  border-radius: 10px;
}

.task-info {
  background: #2d3748;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-info .task-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.task-row strong {
  font-size: 1.1rem;
  font-weight: 600;
  color: #a0aec0;
}

.task-row span,
.task-row input,
.task-row textarea {
  font-size: 1rem;
  color: #ffffff;
  background: #1a202c;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #4a5568;
  transition: border 0.3s;
}

.task-row input:focus,
.task-row textarea:focus {
  border-color: #63b3ed;
  outline: none;
}

.task-row textarea {
  min-height: 80px;
  resize: vertical;
}

.task-section {
  background: #2d3748;
  padding: 20px;
  border-radius: 8px;
}

.task-label {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.task-list {
  list-style: none;
  padding: 0;
}

.task-item {
  padding: 10px;
  background: #334155;
  margin: 5px 0;
  border-radius: 5px;
  transition: 0.3s;
}

.task-item:hover {
  background: #475569;
}

.task-button {
  background: #2563eb;
  color: white;
  padding: 12px 25px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  display: block;
  margin: 20px auto;
  font-size: 1rem;
  font-weight: 600;
}

.task-button:hover {
  background: #1e40af;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease-in-out, transform 0.2s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>