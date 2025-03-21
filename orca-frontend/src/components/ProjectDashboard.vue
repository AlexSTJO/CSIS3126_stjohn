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
          <path d="M4 20c0-4 4-7 8-7s8 3 8 7" />
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
</template>

<script>
import { API_ENDPOINTS } from "./constants.js";

export default {
  data() {
    return {
      tasks: [],
      selectedTask: null,
      isEditing: false,
      project_info: {"Project": this.$route.params.projectname}
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
    margin-top: 80px;
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
    margin-top: -300px;
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
    background: #334155;
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
    background: #475569;
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
