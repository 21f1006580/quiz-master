<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h1>Admin Dashboard</h1>
      <p>Manage your quiz application</p>
    </div>

    <div class="dashboard-content">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <div class="stat-info">
            <h3>{{ stats.total_subjects || 0 }}</h3>
            <p>Subjects</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">📖</div>
          <div class="stat-info">
            <h3>{{ stats.total_chapters || 0 }}</h3>
            <p>Chapters</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">📝</div>
          <div class="stat-info">
            <h3>{{ stats.total_quizzes || 0 }}</h3>
            <p>Quizzes</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">❓</div>
          <div class="stat-info">
            <h3>{{ stats.total_questions || 0 }}</h3>
            <p>Questions</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-info">
            <h3>{{ stats.total_users || 0 }}</h3>
            <p>Users</p>
          </div>
        </div>
      </div>

      <div class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="actions-grid">
          <router-link to="/admin/subjects" class="action-card">
            <div class="action-icon">📚</div>
            <h3>Manage Subjects</h3>
            <p>Add, edit, or remove subjects</p>
          </router-link>
          
          <router-link to="/admin/chapters" class="action-card">
            <div class="action-icon">📖</div>
            <h3>Manage Chapters</h3>
            <p>Organize chapters by subject</p>
          </router-link>
          
          <router-link to="/admin/quizzes" class="action-card">
            <div class="action-icon">📝</div>
            <h3>Manage Quizzes</h3>
            <p>Create and schedule quizzes</p>
          </router-link>
          
          <router-link to="/admin/questions" class="action-card">
            <div class="action-icon">❓</div>
            <h3>Manage Questions</h3>
            <p>Add questions to quizzes</p>
          </router-link>
          
          <router-link to="/admin/users" class="action-card">
            <div class="action-icon">👥</div>
            <h3>Manage Users</h3>
            <p>View and manage user accounts</p>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: {}
    }
  },
  async created() {
    await this.loadStats()
  },
  methods: {
    async loadStats() {
      try {
        const token = localStorage.getItem('access_token')
        const response = await fetch('/api/admin/dashboard/stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.ok) {
          this.stats = await response.json()
        }
      } catch (error) {
        console.error('Error loading stats:', error)
      }
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 3rem;
}

.dashboard-header h1 {
  color: white;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.dashboard-header p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.stat-info h3 {
  color: white;
  font-size: 1.8rem;
  margin: 0 0 0.25rem 0;
}

.stat-info p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 0.9rem;
}

.quick-actions {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.quick-actions h2 {
  color: #333;
  margin-bottom: 2rem;
  font-size: 1.8rem;
  text-align: center;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  text-align: center;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 2px solid transparent;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  border-color: #667eea;
}

.action-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.action-card h3 {
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 1.3rem;
}

.action-card p {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .admin-dashboard {
    padding: 1rem;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
