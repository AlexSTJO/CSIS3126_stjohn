<template>
  <div class="modal-overlay">
    <div class="modal">
      <h2>Create New Project</h2>
      <input v-model="projectName" class="project-input" placeholder="Enter project name" />
      <div class="modal-actions">
        <button @click="create">Create</button>
        <button @click="$emit('close')">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      projectName: ""
    };
  },
  methods: {
    async create() {
      if (!this.projectName.trim()) return alert("Please enter a project name.");
      try {
        const response = await fetch("/create-project", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${sessionStorage.getItem("token")}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ project_name: this.projectName })
        });

        const result = await response.json();
        if (!response.ok || result.error) {
          alert(result.error || "Failed to create project.");
          return;
        }

        this.$emit("created", result); // send project name back to parent
        this.$emit("close");
      } catch (err) {
        console.error("Error creating project:", err);
        alert("Something went wrong.");
      }
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex; justify-content: center; align-items: center;
}
.modal {
  background: #1f2937;
  color: white;
  padding: 25px;
  border-radius: 10px;
  width: 400px;
}
.project-input {
  width: 100%;
  padding: 10px;
  background: #2d3748;
  color: white;
  border: 1px solid #4a5568;
  border-radius: 6px;
  margin-bottom: 15px;
}
.modal-actions {
  display: flex;
  justify-content: space-between;
}
.modal-actions button {
  padding: 8px 20px;
  background: #006d5b;
  border: none;
  color: white;
  border-radius: 6px;
  cursor: pointer;
}
.modal-actions button:hover {
  background: #004d40;
}
</style>

