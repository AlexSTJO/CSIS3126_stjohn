<template>
    <div class="container">
      <nav class="taskbar">
        <div class="logo">
          <img src="../assets/logo.png" alt="Logo" class="logo-icon">
          <span class="logo-text">Orca</span>
          <span @click="navigate('Processes')" class="processes-link">Processes</span>
        </div>
        <div class="nav-buttons" v-if="!isLoggedIn">
          <button @click="navigate('Login')">Login</button>
        </div>
      </nav>
  
      <section class="processes-view section-box">
        <h2>Processes</h2>
        <div class="processes-section box-shadow">
          <div class="process-header">
            <h3>Active Processes</h3>
            <button class="add-process-button">+</button>
          </div>
          <ul>
            <li v-for="process in activeProcesses" :key="process.id" class="process-item">
              <span class="process-name">{{ process.name }}</span>
              <span class="process-status">{{ process.status }}</span>
              <button @click="viewProcess(process.id)" class="process-view">View</button>
            </li>
          </ul>
        </div>
  
        <div class="processes-section box-shadow">
          <h3>Cached Scripts</h3>
          <ul>
            <li v-for="script in cachedScripts" :key="script.id" class="process-item">
              <span class="script-name">{{ script.name }}</span>
              <button class="script-view">View</button>
            </li>
          </ul>
        </div>
  
        <div class="processes-section box-shadow">
          <h3>Add a Script</h3>
            <div 
                class="upload-zone" 
                @dragover.prevent
                @dragenter.prevent
                @drop="handleDrop"
                @click="openFileExplorer"
            >
                <p>Drag & Drop files here or Click to Upload</p>
                <input type="file" ref="fileInput" style="display: none;" />
            </div>
          <button class="upload-button" @click="addScript()">Upload</button>
        </div>
      </section>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        isLoggedIn: false,
        activeProcesses: [
          { id: 1, name: 'Process 1', status: 'Running' },
          { id: 2, name: 'Process 2', status: 'Queued' }
        ],
        cachedScripts: [
          { id: 1, name: 'Script 1' },
          { id: 2, name: 'Script 2' }
        ]
      };
    },
    mounted() {
      const token = sessionStorage.getItem('token');
      this.isLoggedIn = !!token;
    },
    methods: {
      navigate(page) {
        if (this.$router) {
          this.$router.push(`/${page}`);
        } else {
          console.error('Router is not available.');
        }
      },
    openFileExplorer() {
        this.$refs.fileInput.click();
  },
    handleDrop(event) {
        event.preventDefault();
        const files = event.dataTransfer.files;
        if (files.length > 0) {
        this.uploadFile(files[0]);
        }
    },
    
    async addScript(){
        const file = event.target.files[0];
        const formData = new FormData();
        const userId = sessionStorage.getItem('user_id'); 
        formData.append('user_id', userId);
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:5000/add-script', {
            method: 'POST',
            body: formData
            });

            const result = await response.json();
            if (response.ok) {
            alert('Script added successfully!');
            } else {
            alert('Failed to add script: ' + result.error);
            }
        } catch (error) {
            console.error('Error adding script:', error);
            alert('Failed to add script!');
        }
}   


    }
  };
  </script>
  
  <style>
  .taskbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 30px;
    background-color: #ffffff;
    color: #3bc442;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 1000;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }
  
  .logo {
    display: flex;
    align-items: center;
  }
  
  .logo-text {
    color: #4caf50;
    font-weight: bold;
    font-size: 1.3em;
  }
  
  .processes-link {
    color: #4caf50;
    font-size: 1.3em;
    cursor: pointer;
    text-decoration: none;
    margin-left: 20px;
  }
  
  .processes-link:hover {
    text-decoration: underline;
  }
  
  .section-box {
    background: #ffffff;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 20px;
    margin: 20px auto;
    width: 75%;
  }
  
  .box-shadow {
    background: #ffffff;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }
  
  .process-header {
    margin-left: 4%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .add-process-button {
    padding: 5px 10px;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1em;
    width: 5%;
  }
  
  .add-process-button:hover {
    background-color: #388e3c;
  }
  
  .process-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
  }
  
  .process-view, .script-view, .upload-button {
    padding: 5px 15px;
    width: 10%;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .process-view:hover, .script-view:hover, .upload-button:hover {
    background-color: #388e3c;
  }
  .upload-zone {
  border: 2px dashed #4caf50;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  color: #4caf50;
  cursor: pointer;
  margin-top: 10px;
  transition: background-color 0.2s;
  margin-bottom: 2%;
}

.upload-zone:hover {
  background-color: #f0f8f0;
}
  </style>
