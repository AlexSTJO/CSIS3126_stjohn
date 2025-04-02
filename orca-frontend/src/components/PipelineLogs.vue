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
  <div class="pipeline-runner"> 
    <div class="log-box" ref="logBox">
      <div
        v-for="(line, index) in logs"
        :key="index"
        :class="getLogClass(line)"
      >
        {{ line }}
      </div>
    </div>     
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount, onMounted, nextTick } from 'vue'
import { io } from 'socket.io-client'
import { useRoute } from 'vue-router'

const logs = ref([])
const isRunning = ref(false)
const logBox = ref(null)

const route = useRoute()
const projectName = route.params.projectname
const token = sessionStorage.getItem('token')

let socket = null

const runPipeline = () => {
  logs.value = []
  isRunning.value = true

  socket = io('http://localhost:5000', {
    transports: ['websocket']
  })

  socket.on('connect', () => {
    logs.value.push(`[INFO ${timestamp()}] Connected to server`)
    socket.emit('run_pipeline', {
      token: token,
      project: projectName
    })
  })

  socket.on('log', (message) => {
    logs.value.push(formatLog(message))
    nextTick(() => {
      if (logBox.value) {
        logBox.value.scrollTop = logBox.value.scrollHeight
      }
    })
  })

  socket.on('disconnect', () => {
    logs.value.push(`[INFO ${timestamp()}] Disconnected from server`)
    isRunning.value = false
  })

  socket.on('connect_error', (err) => {
    logs.value.push(`[ERROR ${timestamp()}] Connection failed: ${err.message}`)
    isRunning.value = false
  })
}

const formatLog = (line) => {
  const level = line.match(/^\[(INFO|ERROR|SUCCESS)\]/)
  const ts = timestamp()
  return level ? `[${level[1]} ${ts}] ${line.replace(level[0], '').trim()}` : `[LOG ${ts}] ${line}`
}

const getLogClass = (line) => {
  if (line.includes('[ERROR')) return 'log-error'
  if (line.includes('[SUCCESS')) return 'log-success'
  if (line.includes('[STATUS] Success')) return 'log-success'
  if (line.includes('[INFO')) return 'log-info'
  if (line.includes('[TASK')) return 'log-task'
  if (line.includes('[LOG')) return 'log-default'
  return 'log-default'
}

const timestamp = () => {
  const now = new Date()
  return now.toLocaleTimeString()
}

onMounted(() => {
  runPipeline()
})

onBeforeUnmount(() => {
  if (socket) socket.disconnect()
})


</script>

<style scoped>
.pipeline-runner {
  background: #1f2937;
  color: #e5e7eb;
  padding: 20px;
  border-radius: 10px;
  border: 1px solid #374151;
  margin: 20px;
  margin-top: 80px;
}

.log-box {
  background: #111827;
  border: 1px solid #374151;
  padding: 15px;
  border-radius: 6px;
  height: 350px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  white-space: pre-wrap;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 20px;
  text-align: left;
}

.log-info {
  color: #60a5fa; 
}

.log-default {
  color: #e5e7eb;
}

.log-success {
  color: #34d399; 
  font-weight: bold;
}

.log-error {
  color: #f87171; 
  font-weight: bold;
}

.log-task {
  color: #fbbf24; 
  font-style: italic;
  font-weight: bold;
}
.run-btn {
  margin-top: 15px;
  padding: 10px 20px;
  background: #006d5b;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}

.run-btn:hover {
  background: #004d40;
}

.run-btn:disabled {
  background: #4b5563;
  cursor: not-allowed;
}
</style>

