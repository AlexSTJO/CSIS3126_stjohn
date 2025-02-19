<template>
  <div class="container">
    <div class="logout-form">
      <h1>Are you sure you want to log out?</h1>
      <div class="button-container">
        <button class="logout-button" @click="performLogout()">Yes</button>
        <button class="stay-button" @click="navigate('')">No</button>
      </div>
    </div>
  </div>
</template>
<script>
  export default {
    methods: {
      navigate (page) {
        this.$router.push(`/${page}`)
      },
      checkLogin () {
        const token = sessionStorage.getItem("token");

        if (!token) {
          this.navigate("")
        }
      },
      performLogout() {
        sessionStorage.clear()
        this.navigate("")
      } 
    },
    mounted () {
      this.checkLogin()
    }
  } 
</script>
<style>
  .container {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .logout-form {
      margin-top: 250px;
      background-color: #2a3644; 
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3); 
      max-width: 500px;
      width: 90%; 
      text-align: center;
      box-sizing: border-box;
      color: #FFFFFF; 
  }

  .button-container {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 40px;
  }
    
  .logout-button {
      background-color: #e57373; 
      color: white;
      font-size: 1rem;
      padding: 12px 30px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      transition: background-color 0.3s ease, transform 0.2s ease;
      margin-top: 15px;
  }

  .stay-button {
      background-color: #66bb6a; 
      color: white;
      font-size: 1rem;
      padding: 12px 30px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      transition: background-color 0.3s ease, transform 0.2s ease;
      margin-top: 15px;
  }

  .logout-button:hover {
      background-color: #C0392B; 
      transform: scale(1.05);
  }

  .stay-button:hover {
      background-color: #1E8449; 
      transform: scale(1.05);
  }

</style>
