<template>
  <div class="container">
    <nav class="taskbar">
      <div class="logo">
        <img src="../assets/logo.png" alt="Logo" class="logo-icon">
        <span class="logo-text">Orca</span>
      </div>
      <span @click="navigate('Processes')" class="processes-link">Processes</span>
      <div class="nav-buttons" v-if="!isLoggedIn">
        <button @click="navigate('Login')">Login</button>
      </div>
    </nav>

    <section class="active-processes section-box">
      <h2>Active Processes</h2>
      <ul>
        <li v-for="process in activeProcesses" :key="process.id" class="process-item">
          <span class="process-name">{{ process.name }}</span>
          <button @click="viewProcess(process.id)" class="process-view">View</button>
          <span class="process-status">{{ process.status }}</span>
        </li>
      </ul>
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
    viewProcess(id) {
      console.log('View process:', id);
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
  max-width: 100vw;
  z-index: 1000;
  box-sizing: border-box;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.8em;
  font-weight: bold;
}

.logo-icon {
  width: 40px;
  height: 40px;
  margin-right: 10px;
}

.logo-text {
  color: #4caf50;
  font-weight: bold;
  font-size: 1.3em;
  margin-right: 10px;
}

.processes-link {
  color: #4caf50;
  font-size: 1.3em;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
}

.processes-link:hover {
  text-decoration: underline;
}

.nav-buttons button {
  padding: 10px 25px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1em;
}

.nav-buttons button:hover {
  background-color: #388e3c;
  transform: scale(1.1);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.section-box {
  background: #ffffff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  padding: 20px;
  margin: 20px auto;
  width: 75%;
}

.active-processes ul {
  list-style: none;
  padding: 0;
}

.process-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.process-name {
  flex-grow: 1;
  text-align: left;
}

.process-view {
  height: 100%;
  width: 8%;
  margin: 0 10px;
  padding: 10px 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.8em;
}

.process-view:hover {
  background-color: #388e3c;
}

.process-status {
  text-align: right;
}
</style>
