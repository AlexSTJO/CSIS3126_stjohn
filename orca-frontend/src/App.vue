<template>
  <div id="app">
    <MainMenu />
    <router-view></router-view> 
  </div>
</template>

<script>

export default {
  name: 'App',
  
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  margin: 0;
  padding: 0;
}
 html, body{
  background: #1e272e;
}
 .navbar {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 20px;
      background-color: #232f3e;
      color: white;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      z-index: 1000;
      height: 60px;
      box-sizing: border-box;
  }


  .navbar-left, .navbar-center, .navbar-links {
      flex: 1;
      display: flex;
      align-items: center;
  }

  .navbar-center {
      justify-content: center;
  }


  .navbar-logo {
      height: 80px;
      width: auto;
      transition: transform 0.3s ease;
      margin-right: 12px;
  }

  .navbar-logo:hover {
      transform: scale(1.1);
  }


  .navbar-brand {
      font-size: 1.5rem;
      font-weight: 700;
      white-space: nowrap;
  }


  .navbar-links {
      justify-content: flex-end;
      list-style: none;
      margin: 0;
      padding: 0;
  }

  .navbar-links li {
      margin-left: 20px;
  }

  .navbar-links a {
      color: white;
      font-size: 1.1rem;
      padding: 8px 14px;
      border-radius: 6px;
      text-decoration: none;
      transition: transform 0.2s ease, background-color 0.3s ease;
      white-space: nowrap;
  }

  .navbar-links a:hover {
      background-color: white;
      text-decoration: none;
      color: #004d40;
      transform: scale(1.05);
  }

  .icon-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease-in-out;
  }

  .icon-svg {
    width: 32px;
    height: 32px;
    stroke: white;
  }

  .icon-button:hover {
    transform: scale(1.1);
  }

</style>
