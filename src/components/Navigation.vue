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
        <span class="user-name">{{ userFullName }}</span>
        <button @click="handleLogout" class="btn-logout">Logout</button>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navigation',
  computed: {
    showNavigation() {
      // Don't show navigation on login/register pages
      return !['login', 'register'].includes(this.$route.name)
    },
    user() {
      return this.$store.getters['auth/user']
    },
    isAdmin() {
      return this.$store.getters['auth/isAdmin']
    },
    userFullName() {
      return this.$store.getters['auth/userFullName']
    }
  },
  methods: {
    async handleLogout() {
      try {
        // Dispatch logout action to Vuex store
        this.$store.dispatch('auth/logout')
        
        // Redirect to login page
        this.$router.push('/login')
        
        console.log('Logout successful')
      } catch (error) {
        console.error('Logout error:', error)
        // Even if there's an error, clear local storage and redirect
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        this.$router.push('/login')
      }
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
}

.nav-menu {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 5px;
}

.nav-link:hover,
.nav-link.active {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-name {
  color: #ffffff;
  font-weight: 500;
}

.btn-logout {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 5px;
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
  }
  
  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .nav-user {
    justify-content: center;
  }
}
</style>