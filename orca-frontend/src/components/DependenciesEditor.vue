<template>
  <div class="modal-overlay">
    <div class="modal">
      <h2>Edit Dependencies</h2>

      <ul class="dependency-list">
        <li v-for="(dep, index) in dependencies" :key="index" class="dep-row">
          <input v-model="dependencies[index]" class="dep-input" />
          <button class="remove-btn" @click="removeDependency(index)">X</button>
        </li>
      </ul>

      <button class="add-btn" @click="addDependency">+ Add Dependency</button>

      <div class="modal-actions">
        <button class="save-btn" @click="save">Save</button>
        <button class="cancel-btn" @click="$emit('close')">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
import { API_ENDPOINTS } from "./constants.js";
export default {
  props: ["project"],
  data() {
    return {
      dependencies: []
    };
  },
  async mounted() {
     try {
      const response = await fetch(`${API_ENDPOINTS.GET_DEPENDENCIES}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${sessionStorage.getItem("token")}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          project_info: { Project: this.project }
        })
      });

      const result = await response.json();
      if (!response.ok || result.error) {
        throw new Error(result.error || "Failed to fetch dependencies.");
      }

      this.dependencies = result.message
    } catch (err) {
      console.error("Failed to load dependencies:", err);
    }
  },
  methods: {
    addDependency() {
      this.dependencies.push("");
    },
    removeDependency(index) {
      this.dependencies.splice(index, 1);
    },
    async save() {
      const cleanDeps = this.dependencies.map(dep => dep.trim()).filter(dep => dep.length > 0);
      await fetch(`${API_ENDPOINTS.UPLOAD_DEPENDENCIES}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${sessionStorage.getItem("token")}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          project_info: { Project: this.project },
          dependencies: cleanDeps.join("\n")
        })
      });
      this.$emit("close");
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal {
  background: #1f2937;
  padding: 25px;
  border-radius: 10px;
  color: white;
  width: 500px;
}
.dependency-list {
  list-style: none;
  padding: 0;
}
.dep-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.dep-input {
  flex: 1;
  background: #2d3748;
  color: white;
  border: 1px solid #4a5568;
  border-radius: 6px;
  padding: 8px;
}
.remove-btn {
  background: #e53e3e;
  border: none;
  color: white;
  margin-left: 10px;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
}
.add-btn,
.save-btn,
.cancel-btn {
  margin-top: 15px;
  margin-right: 10px;
  padding: 10px 20px;
  background: #006d5b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.cancel-btn {
  background: #4b5563;
}

.add-btn:hover,
.save-btn:hover {
  background: #004d40;
}

.cancel-btn:hover {
  background: #374151;
}

.remove-btn:hover {
  background: #c53030;
}
</style>

