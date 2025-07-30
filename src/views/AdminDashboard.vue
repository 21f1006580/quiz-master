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

      <!-- Celery Task Management Section -->
      <div class="celery-management">
        <h2>Celery Task Management</h2>
        <div class="celery-controls">
          <div class="task-triggers">
            <h3>Trigger Tasks</h3>
            <div class="trigger-buttons">
              <button @click="triggerAllTasks" :disabled="triggering" class="btn-trigger btn-all">
                <i class="fas fa-play"></i> Trigger All Tasks
              </button>
              <button @click="triggerNotificationTasks" :disabled="triggering" class="btn-trigger btn-notification">
                <i class="fas fa-bell"></i> Notification Tasks
              </button>
              <button @click="triggerQuizTasks" :disabled="triggering" class="btn-trigger btn-quiz">
                <i class="fas fa-question-circle"></i> Quiz Tasks
              </button>
              <button @click="triggerExportTasks" :disabled="triggering" class="btn-trigger btn-export">
                <i class="fas fa-download"></i> Export Tasks
              </button>
            </div>
          </div>

          <div class="task-monitoring">
            <h3>Task Monitoring</h3>
            <div class="monitoring-controls">
              <button @click="checkWorkerStatus" :disabled="checking" class="btn-monitor">
                <i class="fas fa-server"></i> Worker Status
              </button>
              <button @click="checkActiveTasks" :disabled="checking" class="btn-monitor">
                <i class="fas fa-list"></i> Active Tasks
              </button>
            </div>
          </div>
        </div>

        <!-- Task Results Display -->
        <div v-if="taskResults" class="task-results">
          <h3>Task Results</h3>
          <div class="results-grid">
            <div v-for="(result, key) in taskResults" :key="key" class="result-card">
              <h4>{{ key.replace('_', ' ').toUpperCase() }}</h4>
              <div v-for="(task, taskKey) in result" :key="taskKey" class="task-item">
                <div class="task-info">
                  <span class="task-name">{{ taskKey.replace('_', ' ') }}</span>
                  <span class="task-status" :class="task.status">{{ task.status }}</span>
                </div>
                <div v-if="task.task_id" class="task-actions">
                  <button @click="checkTaskStatus(task.task_id)" class="btn-check">
                    Check Status
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Worker Status Display -->
        <div v-if="workerStatus" class="worker-status">
          <h3>Worker Status</h3>
          <pre>{{ JSON.stringify(workerStatus, null, 2) }}</pre>
        </div>

        <!-- Active Tasks Display -->
        <div v-if="activeTasks" class="active-tasks">
          <h3>Active Tasks</h3>
          <pre>{{ JSON.stringify(activeTasks, null, 2) }}</pre>
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
      stats: {},
      triggering: false,
      checking: false,
      taskResults: null,
      workerStatus: null,
      activeTasks: null
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
    },

    async triggerTasks(taskType) {
      try {
        this.triggering = true
        const token = localStorage.getItem('access_token')
        
        const response = await fetch('/api/admin/celery/trigger-tasks', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ task_type: taskType })
        })
        
        if (response.ok) {
          const data = await response.json()
          this.taskResults = data.results
          alert(`Successfully triggered ${taskType} tasks!`)
        } else {
          const error = await response.json()
          alert(`Error triggering tasks: ${error.error}`)
        }
      } catch (error) {
        console.error('Error triggering tasks:', error)
        alert('Error triggering tasks: ' + error.message)
      } finally {
        this.triggering = false
      }
    },

    async triggerAllTasks() {
      await this.triggerTasks('all')
    },

    async triggerNotificationTasks() {
      await this.triggerTasks('notification')
    },

    async triggerQuizTasks() {
      await this.triggerTasks('quiz')
    },

    async triggerExportTasks() {
      await this.triggerTasks('export')
    },

    async checkWorkerStatus() {
      try {
        this.checking = true
        const token = localStorage.getItem('access_token')
        
        const response = await fetch('/api/admin/celery/worker-status', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.ok) {
          const data = await response.json()
          this.workerStatus = data.worker_status
        } else {
          const error = await response.json()
          alert(`Error checking worker status: ${error.error}`)
        }
      } catch (error) {
        console.error('Error checking worker status:', error)
        alert('Error checking worker status: ' + error.message)
      } finally {
        this.checking = false
      }
    },

    async checkActiveTasks() {
      try {
        this.checking = true
        const token = localStorage.getItem('access_token')
        
        const response = await fetch('/api/admin/celery/active-tasks', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.ok) {
          const data = await response.json()
          this.activeTasks = data.active_tasks
        } else {
          const error = await response.json()
          alert(`Error checking active tasks: ${error.error}`)
        }
      } catch (error) {
        console.error('Error checking active tasks:', error)
        alert('Error checking active tasks: ' + error.message)
      } finally {
        this.checking = false
      }
    },

    async checkTaskStatus(taskId) {
      try {
        const token = localStorage.getItem('access_token')
        
        const response = await fetch(`/api/admin/celery/task-status/${taskId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.ok) {
          const data = await response.json()
          const status = data.task_status
          
          let message = `Task ${taskId}:\n`
          message += `Status: ${status.status}\n`
          message += `Ready: ${status.ready}\n`
          message += `Successful: ${status.successful}\n`
          message += `Failed: ${status.failed}`
          
          if (status.result) {
            message += `\n\nResult: ${JSON.stringify(status.result, null, 2)}`
          }
          
          if (status.error) {
            message += `\n\nError: ${status.error}`
          }
          
          alert(message)
        } else {
          const error = await response.json()
          alert(`Error checking task status: ${error.error}`)
        }
      } catch (error) {
        console.error('Error checking task status:', error)
        alert('Error checking task status: ' + error.message)
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
  margin-bottom: 2rem;
}

.celery-management {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.celery-management h2 {
  color: #333;
  margin-bottom: 1.5rem;
  text-align: center;
}

.celery-controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.task-triggers, .task-monitoring {
  background: #f8f9fa;
  border-radius: 15px;
  padding: 1.5rem;
}

.task-triggers h3, .task-monitoring h3 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.trigger-buttons, .monitoring-controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.btn-trigger, .btn-monitor {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-trigger {
  background: #007bff;
  color: white;
}

.btn-trigger:hover {
  background: #0056b3;
  transform: translateY(-2px);
}

.btn-trigger:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
}

.btn-all { background: #28a745; }
.btn-all:hover { background: #1e7e34; }
.btn-notification { background: #ffc107; color: #212529; }
.btn-notification:hover { background: #e0a800; }
.btn-quiz { background: #17a2b8; }
.btn-quiz:hover { background: #138496; }
.btn-export { background: #6f42c1; }
.btn-export:hover { background: #5a2d91; }

.btn-monitor {
  background: #6c757d;
  color: white;
}

.btn-monitor:hover {
  background: #545b62;
  transform: translateY(-2px);
}

.btn-monitor:disabled {
  background: #adb5bd;
  cursor: not-allowed;
  transform: none;
}

.task-results {
  margin-top: 2rem;
}

.task-results h3 {
  color: #333;
  margin-bottom: 1rem;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.result-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 1rem;
  border: 1px solid #dee2e6;
}

.result-card h4 {
  color: #333;
  margin-bottom: 0.75rem;
  font-size: 1rem;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e9ecef;
}

.task-item:last-child {
  border-bottom: none;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.task-name {
  font-weight: 600;
  color: #495057;
}

.task-status {
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

.task-status.queued {
  background: #fff3cd;
  color: #856404;
}

.task-status.success {
  background: #d4edda;
  color: #155724;
}

.task-status.failed {
  background: #f8d7da;
  color: #721c24;
}

.task-status.pending {
  background: #cce5ff;
  color: #004085;
}

.btn-check {
  padding: 0.25rem 0.5rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-check:hover {
  background: #0056b3;
}

.worker-status, .active-tasks {
  margin-top: 2rem;
  background: #f8f9fa;
  border-radius: 10px;
  padding: 1rem;
}

.worker-status h3, .active-tasks h3 {
  color: #333;
  margin-bottom: 1rem;
}

.worker-status pre, .active-tasks pre {
  background: #e9ecef;
  padding: 1rem;
  border-radius: 5px;
  overflow-x: auto;
  font-size: 0.8rem;
  max-height: 300px;
  overflow-y: auto;
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
