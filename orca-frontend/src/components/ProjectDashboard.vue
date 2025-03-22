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

  <div class="container">
    <aside class="sidebar">
      <div class="sidebar-content">
        <!-- Scrollable Task List -->
        <ul class="project-list">
          <li 
            v-for="task in tasks" 
            :key="task.Name" 
            :class="{ 'selected': task === selectedTask }" 
            class="link" 
            @click="selectTask(task)">
            {{ task.Name }}
          </li>
        </ul>

        <!-- Fixed Actions -->
        <div class="sidebar-actions">
          <button class="action-btn" @click="addTask">Add Task</button>
          <button class="action-btn" @click="removeTask" :disabled="!selectedTask">Remove Task</button>
          <button class="action-btn" @click="runPipeline">Run Pipeline</button>
        </div>
      </div>
    </aside>
    <transition name="fade" mode="out-in">
      <div class="task-details" v-if="selectedTask" key="task-details">
        <div class="task-details-container">
          <div class="task-info">
            <div class="task-row">
              <strong>Name:</strong>
              <span>{{ selectedTask.Name }}</span>
            </div>          
            <div class="task-row">
              <strong>Description:</strong> 
              <textarea v-if="isEditing" v-model="selectedTask.Description" class="edit-field"></textarea>
              <span v-else>{{ selectedTask.Description }}</span>
            </div>
          </div>
        <div class="task-sections">
          <div class="task-section">
            <div class="task-label">Inputs</div>
            <ul class="task-list">
              <li v-for="(input, index) in selectedTask.Inputs" :key="index" class="task-item">
                <input v-if="isEditing" v-model="selectedTask.Inputs[index]" class="edit-field" />
                <span v-else>{{ input }}</span>
                <button v-if="isEditing" @click="removeInput(index)" class="remove-btn">X</button>
              </li>
            </ul>
            <button v-if="isEditing" @click="addInput" class="task-button">Add Input</button>
          </div>

          <div class="task-section">
            <div class="task-label">Outputs</div>
            <ul class="task-list">
              <li v-for="(output, index) in selectedTask.Outputs" :key="index" class="task-item">
                <input v-if="isEditing" v-model="selectedTask.Outputs[index]" class="edit-field" />
                <span v-else>{{ output }}</span>
                <button v-if="isEditing" @click="removeOutput(index)" class="remove-btn">X</button>
              </li>
            </ul>
            <button v-if="isEditing" @click="addOutput" class="task-button">Add Output</button>
          </div>
        </div>
      
        <button class="task-button" @click="toggleEditMode">{{ isEditing ? 'Save' : 'Edit' }}</button>
      </div>
    </div>
  </transition>
  </div>
  <AddTaskModal
      v-if="showAddTaskModal"
      @close="showAddTaskModal = false"
      @create="handleTaskCreate"
  />

</template>

<script>
import { API_ENDPOINTS } from "./constants.js";
import AddTaskModal from './AddTaskModal.vue';
export default {
  components: {
    AddTaskModal
  },
  data() {
    return {
      tasks: [],
      selectedTask: null,
      isEditing: false,
      project_info: {"Project": this.$route.params.projectname},
      showAddTaskModal: false,
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
          headers: { "Authorization" : `Bearer ${sessionStorage.getItem("token")}` }
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
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
      if (this.isEditing) {
        console.log(this.project_info)
        try {
            const response = fetch(`${API_ENDPOINTS.EDIT_TASK}`,{
            method: 'POST',
            headers: { "Authorization" : `Bearer ${sessionStorage.getItem("token")}`,
            'Content-Type': 'application/json',},
            body: JSON.stringify({selectedTask: this.selectedTask,project_info: this.project_info,})
          });
          if (!response.ok) {
            console.error("error")
          } else {
            console.log("success")
          }
        } catch {
          console.log("An Error")
        }
      }
      this.isEditing = !this.isEditing;
    },
    addInput() {
      if (this.selectedTask) {
        this.selectedTask.Inputs.push("");
      }
    },
    removeInput(index) {
      if (this.selectedTask) {
        this.selectedTask.Inputs.splice(index, 1);
      }
    },
    addOutput() {
      if (this.selectedTask) {
        this.selectedTask.Outputs.push("");
  }
    },
    removeOutput(index) {
      if (this.selectedTask) {
        this.selectedTask.Outputs.splice(index, 1);
      }
    },
    addTask() {
    this.showAddTaskModal = true;
    },
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
    height: 90vh;
    padding: 20px; 
  }

   .sidebar {
    display: flex;
    flex-direction: column;
    margin-top: 80px;
    height: 90vh;
    width: 280px;
    background: #1f2937;
    color: white;
    padding: 20px;
    border-right: 1px solid #374151;
  }

  .sidebar-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .project-list {
    flex: 1;
    overflow-y: auto;
    margin: 0;
    padding: 0;
  }

  .sidebar-actions {
    padding-top: 10px;
    border-top: 1px solid #374151;
    background: #1f2937;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .action-btn {
    background: #334155;
    color: white;
    padding: 10px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.3s;
  }

  .action-btn:hover {
    background: #475569;
  }
  .action-btn {
    background: #334155;
    color: white;
    padding: 10px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.3s;
  }

  .action-btn:disabled {
    background: #4b5563;
    cursor: not-allowed;
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
    color: #ffffff;
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
  .task-sections {
    display: flex;
    gap: 20px;
  }
  .task-section {
    flex: 1;
    background: #2d3748;
    padding: 20px;
    border-radius: 8px;
  }

  .task-label {
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 10px;
  }

  .task-list {
    list-style: none;
    padding: 0;
  }

  .task-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #1a202c;
    border: 1px solid #4a5568;
    transition: border 0.3s;
    padding: 8px 12px;
    border-radius: 6px;
    padding: 8px;
    margin: 5px 0;
  }
 
  .task-button {
    background: #006d5b;
    width: 100%;
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

  .edit-field {
    font-size: 1rem;
    color: #ffffff;
    background: #1a202c;
    padding: 8px 12px;
    border-radius: 6px;
    border: none; 
    width: 100%;

  }

  .task-button:hover {
    background: #004d40;
  }
  .remove-btn {
    background: #e53e3e;
    color: white;
    border: none;
    padding: 5px 10px;
    margin-left: 10px;
    cursor: pointer;
    border-radius: 4px;
  }

  .remove-btn:hover {
    background: #c53030;
  }

  .fade-enter-active, .fade-leave-active {
    transition: opacity 0.3s ease-in-out, transform 0.2s;
  }

  .fade-enter, .fade-leave-to {
    opacity: 0;
    transform: translateY(10px);
  }

</style>
