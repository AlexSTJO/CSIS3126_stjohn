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
  <div v-if="pipelineComplete" class="output-explorer">
    <h3 class="explorer-title">Output Explorer</h3>

    <div v-for="(taskGroup, taskName) in groupedFiles" :key="taskName" class="task-group">
      <h4 class="task-name">{{ taskName }}</h4>
      <ul>
        <li v-for="file in taskGroup" :key="file.s3_key" class="file-entry">
          <button class="preview-btn" @click="previewFile(file)">
            📄 {{ file.file }}
          </button>
          <button @click="downloadFile(file)" class="download-icon-btn" title="Download">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon-download" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </button>       
        </li>
      </ul>
    </div>

    <div v-if="previewContent" class="file-preview">
      <h4>Preview</h4>
      <pre class="preview-text">{{ previewContent }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount, onMounted, nextTick } from 'vue'
import { io } from 'socket.io-client'
import { useRoute } from 'vue-router'
import { API_ENDPOINTS } from './constants.js'
const logs = ref([])
const isRunning = ref(false)
const previewContent = ref('')
const pipelineComplete = ref(false)
const outputFiles = ref([])
const logBox = ref(null)

const route = useRoute()
const projectName = route.params.projectname
const token = sessionStorage.getItem('token')

let socket = null

const runPipeline = () => {
  logs.value = []
  isRunning.value = true
  previewContent.value = ''
  pipelineComplete.value = false

  socket = io(`${API_ENDPOINTS.BASE_URL}`, {
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
    if (message.includes('[SUCCESS')) {
      pipelineComplete.value = true
      fetchOutputs()
    }
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

const fetchOutputs = async () => {
  try {
    console.log('Calling:', getRunIdFromLogs())
    const response = await fetch(`${API_ENDPOINTS.LIST_OUTPUT_FILES}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ project_name: projectName, run_id: getRunIdFromLogs() })
    })
    const data = await response.json()
    console.log(data)
    outputFiles.value = data
  } catch (err) {
    logs.value.push(`[ERROR ${timestamp()}] Failed to fetch output files.`)
  }
}

const groupedFiles = computed(() => {
  const grouped = {}
  for (const file of outputFiles.value) {
    const match = file.s3_key.match(/outputs\/[^/]+\/([^/]+)\//)
    const taskName = match ? match[1] : 'Unknown Task'
    if (!grouped[taskName]) grouped[taskName] = []
    grouped[taskName].push(file)
  }
  return Object.keys(grouped).sort().reduce((acc, key) => {
    acc[key] = grouped[key]
    return acc
  }, {})
})


const previewFile = async (file) => {
  try {
    const response = await fetch(`${API_ENDPOINTS.GET_OUTPUT_FILE}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ project_name: projectName, s3_key: file.s3_key })
    })
    const result = await response.json()
    previewContent.value = result.content || '[No preview available]'
  } catch (err) {
    previewContent.value = '[Error loading file preview]'
  }
}

const formatLog = (line) => {
  const level = line.match(/\[(INFO|ERROR|SUCCESS)\]/)
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
  if (line.includes('[SCRIPT')) return 'log-output' 
  return 'log-default'
}

const timestamp = () => {
  const now = new Date()
  return now.toLocaleTimeString()
}

const getRunIdFromLogs = () => {
  const line = logs.value.find(l => l.includes('[PIPELINE] Run ID'))
  const match = line?.match(/Run ID:\s*(\S+)/)
  return match ? match[1] : ''
}

const downloadFile = async (file) => {
  try {
    const response = await fetch(`${API_ENDPOINTS.DOWNLOAD_FILE}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        project_name: projectName,
        s3_key: file.s3_key
      })
    });

    if (!response.ok) throw new Error('Download failed');

    const blob = await response.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = file.file;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  } catch (err) {
    console.error('Download failed:', err);
  }
};



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

.log-output {
  color: #c4b5fd; 
  font-style: italic;
}

.log-script-error {
  color: #fb7185; 
  font-weight: bold;
  font-style: italic;
}

.output-explorer {
  margin: 30px 20px 40px;
  background: #111827;
  border: 1px solid #374151;
  padding: 20px;
  border-radius: 10px;
}

.explorer-title {
  font-size: 1.4rem;
  margin-bottom: 15px;
  font-weight: bold;
  color: #f9fafb;
  border-bottom: 1px solid #374151;
  padding-bottom: 5px;
}

.task-group {
  background: #1f2937;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #374151;
}

.task-name {
  color: #fbbf24;
  margin-bottom: 10px;
  font-weight: bold;
  font-size: 1.1rem;
}

.file-entry {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #111827;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 6px;
  border: 1px solid #374151;
  transition: background 0.3s;
}

.file-entry:hover {
  background: #1e293b;
}

.preview-btn {
  background: none;
  border: none;
  color: #60a5fa;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s;
}

.preview-btn:hover {
  color: #3b82f6;
  text-decoration: underline;
}

.download-icon-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  margin-left: 8px;
  transition: transform 0.2s ease;
  color: #34d399;
}

.download-icon-btn:hover {
  transform: scale(1.15);
  color: #10b981;
}

.icon-download {
  stroke: currentColor;
  vertical-align: middle;
}
.file-preview {
  background: #1e293b;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #374151;
  color: #e5e7eb;
  margin-top: 20px;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  font-size: 0.9rem;
}

.file-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  font-size: 1.1rem;
}

.preview-text {
  text-align: left;
}
</style>

