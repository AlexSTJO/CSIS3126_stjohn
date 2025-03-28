<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal">
      <h2>Confirm Task Deletion</h2>
      <p class="warning-text">
        This action <strong>cannot</strong> be undone. Please type the task name
        <span class="task-name">{{ taskName }}</span> to confirm deletion.
      </p>

      <input
        v-model="confirmName"
        class="modal-input"
        placeholder="Enter task name to confirm"
      />

      <div class="modal-actions">
        <button 
          @click="confirmDelete" 
          class="modal-btn delete"
          :disabled="confirmName !== taskName || loading"
        >
          <span v-if="!loading">Delete</span>
          <span v-else class="spinner"></span>
        </button>       
        <button class="modal-btn cancel" @click="close">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    taskName: {
      type: String,
      required: true
    }
  },
  emits: ['confirm', 'close'],
  data() {
    return {
      confirmName: '',
      loading: false
    };
  },
  methods: {
    close() {
      this.$emit('close');
    },
    async confirmDelete() {
    this.loading = true;
    try {
      await this.$emit('confirm', this.confirmName);
    } finally {
      this.loading = false;
    }
}  }
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
  width: 450px;
  color: white;
  text-align: center;
}
.warning-text {
  margin: 15px 0;
  color: #fbbf24;
}
.task-name {
  font-weight: bold;
  color: #f87171;
}
.modal-input {
  width: 100%;
  padding: 10px;
  background: #374151;
  border: 1px solid #4a5568;
  border-radius: 6px;
  margin-top: 10px;
  color: white;
}
.modal-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 20px;
}
.modal-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
}
.modal-btn.delete {
  background: #e53e3e;
}
.modal-btn.delete:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
.modal-btn.cancel {
  background: #006d5b;
}
.modal-btn:hover:not(:disabled) {
  transform: scale(1.05);
  transition: transform 0.2s ease, background-color 0.2s ease;
}

.modal-btn.delete:hover:not(:disabled) {
  background: #c53030;
}

.modal-btn.cancel:hover {
  background: #004d40;
}
.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

