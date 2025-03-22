<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal">
      <h2>Add New Task</h2>

      <!-- File Drop Zone -->
      <div 
        class="drop-zone" 
        @dragover.prevent 
        @drop.prevent="handleFileDrop"
        @click="triggerFileSelect"
      >
        <span v-if="!file">Drop a .py file here or click to upload</span>
        <span v-else>{{ file.name }}</span>
        <input type="file" ref="fileInput" @change="handleFileChange" accept=".py" hidden />
      </div>
      <div v-if="fileError" class="error-msg">{{ fileError }}</div>

      <!-- Description -->
      <label>Description:</label>
      <textarea v-model="task.Description" class="modal-input" />

      <div class="io-container">
        <!-- Inputs Column -->
        <div class="io-column">
          <label>Inputs:</label>
          <ul class="list-group">
            <li v-for="(input, index) in task.Inputs" :key="'in' + index" class="list-item">
              <input v-model="task.Inputs[index]" class="modal-input" />
              <button @click="removeInput(index)" class="remove-btn">X</button>
            </li>
          </ul>
          <button @click="addInput" class="small-btn">Add Input</button>
        </div>

        <!-- Outputs Column -->
        <div class="io-column">
          <label>Outputs:</label>
          <ul class="list-group">
            <li v-for="(output, index) in task.Outputs" :key="'out' + index" class="list-item">
              <input v-model="task.Outputs[index]" class="modal-input" />
              <button @click="removeOutput(index)" class="remove-btn">X</button>
            </li>
          </ul>
          <button @click="addOutput" class="small-btn">Add Output</button>
        </div>
      </div>
      <div class="modal-actions">
        <button @click="submit" class="modal-btn">Create</button>
        <button @click="close" class="modal-btn cancel">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  emits: ['close', 'create'],
  data() {
    return {
      task: {
        Name: '',
        Description: '',
        Inputs: [],
        Outputs: [],
      },
      file: null,
      fileError: null,
    };
  },
  methods: {
    triggerFileSelect() {
    this.$refs.fileInput?.click();
    },
    handleFileDrop(e) {
      const dropped = e.dataTransfer.files[0];
      this.processFile(dropped);
    },
    handleFileChange(e) {
      const selected = e.target.files[0];
      this.processFile(selected);
    },
    processFile(file) {
      if (file && file.name.endsWith('.py')) {
        this.file = file;
        this.task.Name = file.name;
        this.fileError = null;
      } else {
        this.fileError = "Only .py files are allowed";
      }
    },
    addInput() {
      this.task.Inputs.push('');
    },
    removeInput(index) {
      this.task.Inputs.splice(index, 1);
    },
    addOutput() {
      this.task.Outputs.push('');
    },
    removeOutput(index) {
      this.task.Outputs.splice(index, 1);
    },
    submit() {
      if (!this.file || !this.task.Name.trim()) {
        this.fileError = "Please upload a valid .py file";
        return;
      }
      this.$emit('create', { ...this.task, File: this.file });
      this.close();
    },
    close() {
      this.$emit('close');
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal {
  background: #1f2937;
  padding: 30px;
  border-radius: 10px;
  width: 500px;
  color: white;
}
.drop-zone {
  border: 2px dashed #4a5568;
  border-radius: 6px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  margin-bottom: 10px;
  background: #2d3748;
}

.io-container {
  display: flex;
  justify-content: center; 
  width: 100%;
  gap: 40px;
}
.io-column {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.modal-input {
  flex: 1;
  width: 100%;
  padding: 10px;
  background: #374151;
  border: 1px solid #4a5568;
  border-radius: 6px;
  margin: 8px 0;
  color: white;
}
.list-group {
  list-style: none;
  padding: 0;
  margin: 0 0 10px;
}
.list-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.small-btn {
  background: #334155;
  border: none;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 10px;
}
.small-btn:hover {
  background: #475569;
}
.remove-btn {
  background: #e53e3e;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}
.remove-btn:hover {
  background: #c53030;
}
.error-msg {
  color: #f87171;
  margin-bottom: 10px;
}
.modal-actions {
  display: flex;
  justify-content: center;
  margin-top: 15px; 
  gap: 40px;
}
.modal-btn {
  padding: 10px 20px;
  background: #006d5b;
  width: 100%;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
}
.modal-btn.cancel {
  background: #e53e3e;
}

.modal-btn:hover {
 background: #004d40; 
}
.modal-btn.cancel:hover {
  background: #c53030;
}
</style>
