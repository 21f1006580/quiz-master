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
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
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
  color: white;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.nav-menu {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  color: white;
  background: rgba(255, 255, 255, 0.2);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-name {
  color: white;
  font-weight: 500;
}

.btn-logout {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-logout:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
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
  }
}
</style> 