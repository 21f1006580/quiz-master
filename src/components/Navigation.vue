<template>
  <nav class="navigation" v-if="showNavigation">
    <div class="nav-container">
      <div class="nav-brand">
        <h2>Quiz Master</h2>
      </div>
      
      <div class="nav-menu">
        <router-link 
          v-if="isAdmin" 
          to="/admin" 
          class="nav-link"
          active-class="active"
        >
          Admin Dashboard
        </router-link>
        
        <router-link 
          to="/dashboard" 
          class="nav-link"
          active-class="active"
        >
          Dashboard
        </router-link>
        
        <router-link 
          to="/scores" 
          class="nav-link"
          active-class="active"
        >
          My Scores
        </router-link>
      </div>
      
      <div class="nav-user">
        <span class="user-name">{{ user.full_name }}</span>
        <button @click="logout" class="btn-logout">Logout</button>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navigation',
  data() {
    return {
      user: {},
      isAdmin: false
    }
  },
  computed: {
    showNavigation() {
      // Don't show navigation on login/register pages
      return !['login', 'register'].includes(this.$route.name)
    }
  },
  created() {
    this.loadUserData()
  },
  methods: {
    loadUserData() {
      const userData = localStorage.getItem('user')
      if (userData) {
        this.user = JSON.parse(userData)
        this.isAdmin = this.user.is_admin || false
      }
    },
    
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.navigation {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand h2 {
  color: #ffffff;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.nav-menu {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.nav-link {
  color: #ffffff;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 25px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  transition: left 0.3s ease;
  z-index: -1;
}

.nav-link:hover::before {
  left: 0;
}

.nav-link:hover {
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-name {
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.btn-logout {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-logout:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-logout:active {
  transform: translateY(0);
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
  }
  
  .nav-user {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  .nav-brand h2 {
    font-size: 1.3rem;
  }
}

@media (max-width: 480px) {
  .nav-container {
    padding: 0.75rem;
  }
  
  .nav-link {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .btn-logout {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
}
</style>