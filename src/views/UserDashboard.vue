<template>
  <div class="user-dashboard">
    <div class="dashboard-header">
      <h1>Welcome, {{ user.full_name || 'User' }}!</h1>
      <div class="user-stats">
        <div class="stat-card">
          <h3>{{ scoreSummary.total_quizzes_attempted || 0 }}</h3>
          <p>Quizzes Attempted</p>
        </div>
        <div class="stat-card">
          <h3>{{ scoreSummary.average_score || 0 }}%</h3>
          <p>Average Score</p>
        </div>
        <div class="stat-card">
          <h3>{{ scoreSummary.best_score || 0 }}%</h3>
          <p>Best Score</p>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading your dashboard...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Something went wrong</h3>
        <p>{{ error }}</p>
        <button @click="loadDashboard" class="btn-retry">Try Again</button>
      </div>

      <!-- Main Content -->
      <div v-else>
        <!-- Subjects Section -->
        <div class="subjects-section">
          <h2>Available Subjects</h2>
          <div v-if="subjects.length === 0" class="empty-state">
            <i class="fas fa-book fa-3x"></i>
            <h3>No Subjects Available</h3>
            <p>There are currently no subjects available for quizzes.</p>
          </div>
          <div v-else class="subjects-grid">
            <div 
              v-for="subject in subjects" 
              :key="subject.id" 
              class="subject-card"
              @click="viewQuizzes(subject.id)"
            >
              <div class="subject-header">
                <h3>{{ subject.name }}</h3>
                <div class="subject-stats">
                  <span class="stat">{{ subject.chapter_count || 0 }} chapters</span>
                  <span class="stat">{{ subject.available_quizzes || 0 }} quizzes</span>
                </div>
              </div>
              <p>{{ subject.description || 'No description available' }}</p>
              <button class="btn-view">
                <i class="fas fa-play"></i>
                View Quizzes
              </button>
            </div>
          </div>
        </div>

        <!-- Recent Scores Section -->
        <div class="recent-scores" v-if="recentScores.length > 0">
          <h2>Recent Quiz Attempts</h2>
          <div class="scores-list">
            <div v-for="score in recentScores" :key="score.score_id" class="score-item">
              <div class="score-info">
                <h4>{{ score.quiz_title }}</h4>
                <div class="score-details">
                  <span class="score-badge" :class="getScoreClass(score.total_score)">
                    {{ score.total_score }}%
                  </span>
                  <span class="questions-info">
                    {{ score.correct_answers }}/{{ score.total_questions }} correct
                  </span>
                </div>
                <div class="score-meta">
                  <span class="subject-chapter">{{ score.subject_name }} - {{ score.chapter_name }}</span>
                  <span class="attempt-date">{{ formatDate(score.attempted_on) }}</span>
                </div>
              </div>
              <button @click="viewQuizSummary(score.quiz_id)" class="btn-details">
                <i class="fas fa-chart-line"></i>
                View Details
              </button>
            </div>
          </div>
          <div class="view-all-scores">
            <router-link to="/user/scores" class="btn-link">
              <i class="fas fa-history"></i>
              View All Attempts
            </router-link>
          </div>
        </div>

        <!-- Quick Stats Section -->
        <div class="quick-stats" v-if="scoreSummary.total_quizzes_attempted > 0">
          <h2>Your Performance</h2>
          <div class="stats-grid">
            <div class="performance-card">
              <i class="fas fa-trophy"></i>
              <h4>Best Performance</h4>
              <p>{{ scoreSummary.best_score }}%</p>
            </div>
            <div class="performance-card">
              <i class="fas fa-clock"></i>
              <h4>Time Spent</h4>
              <p>{{ formatTime(scoreSummary.total_time_spent) }}</p>
            </div>
            <div class="performance-card">
              <i class="fas fa-target"></i>
              <h4>Success Rate</h4>
              <p>{{ getSuccessRate() }}%</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quiz Summary Modal -->
    <div v-if="showQuizSummary" class="modal-overlay" @click="closeQuizSummary">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Quiz Summary</h3>
          <button @click="closeQuizSummary" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body" v-if="quizSummary">
          <div class="summary-info">
            <div class="summary-header">
              <h4>{{ quizSummary.quiz_title }}</h4>
              <span class="score-badge large" :class="getScoreClass(quizSummary.percentage_score)">
                {{ quizSummary.percentage_score }}%
              </span>
            </div>
            <div class="summary-details">
              <div class="detail-row">
                <span class="label">Subject:</span>
                <span class="value">{{ quizSummary.subject }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Chapter:</span>
                <span class="value">{{ quizSummary.chapter }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Correct Answers:</span>
                <span class="value">{{ quizSummary.score }}/{{ quizSummary.total_questions }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Time Taken:</span>
                <span class="value">{{ formatTime(quizSummary.time_taken) }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Attempted:</span>
                <span class="value">{{ formatDate(quizSummary.attempted_on) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" :class="['alert', messageType === 'success' ? 'alert-success' : 'alert-error']">
      {{ message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserDashboard',
  data() {
    return {
      user: {},
      subjects: [],
      recentScores: [],
      scoreSummary: {},
      loading: true,
      error: null,
      showQuizSummary: false,
      quizSummary: null,
      message: '',
      messageType: 'success'
    }
  },
  
  async created() {
    await this.loadDashboard()
  },
  
  methods: {
    async loadDashboard() {
      try {
         console.log('Starting dashboard load...')
        this.loading = true
        this.error = null
        
        const token = localStorage.getItem('access_token')
        if (!token) {
          this.$router.push('/login')
          return
        }

        const userData = localStorage.getItem('user')
        if (userData) {
          this.user = JSON.parse(userData)
          console.log('User data loaded:', this.user)
        }

        // Load all dashboard data in parallel
        const [subjectsResponse, scoresResponse, summaryResponse] = await Promise.all([
          axios.get('/api/user/dashboard', { headers: { 'Authorization': `Bearer ${token}` } }),
          axios.get('/api/user/scores', { headers: { 'Authorization': `Bearer ${token}` } }),
          axios.get('/api/user/score-summary', { headers: { 'Authorization': `Bearer ${token}` } })
        ])

        // Handle subjects
        if (subjectsResponse.data && subjectsResponse.data.subjects) {
          this.subjects = subjectsResponse.data.subjects
        }

        // Handle recent scores (show last 5)
        if (scoresResponse.data && scoresResponse.data.scores) {
          this.recentScores = scoresResponse.data.scores.slice(0, 5)
        }

        // Handle score summary
        if (summaryResponse.data) {
          this.scoreSummary = summaryResponse.data
        }

      } catch (error) {
        console.error('Error loading dashboard:', error)
        this.error = this.getErrorMessage(error)
        
        // If authentication error, redirect to login
        if (error.response && error.response.status === 401) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          this.$router.push('/login')
        }
      } finally {
        this.loading = false
      }
    },

    viewQuizzes(subjectId) {
      this.$router.push(`/user/subjects/${subjectId}/quizzes`)
    },

    async viewQuizSummary(quizId) {
      try {
        const token = localStorage.getItem('access_token')
        const response = await axios.get(`/api/user/quiz-summary/${quizId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.data) {
          this.quizSummary = response.data
          this.showQuizSummary = true
        }
      } catch (error) {
        console.error('Error loading quiz summary:', error)
        this.showMessage('Error loading quiz summary', 'error')
      }
    },

    closeQuizSummary() {
      this.showQuizSummary = false
      this.quizSummary = null
    },

    getErrorMessage(error) {
      if (error.response && error.response.data && error.response.data.error) {
        return error.response.data.error
      }
      return error.message || 'An unexpected error occurred'
    },

    showMessage(message, type = 'success') {
      this.message = message
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 5000)
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    formatTime(seconds) {
      if (!seconds) return '0m'
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      if (minutes > 0) {
        return `${minutes}m ${remainingSeconds}s`
      }
      return `${remainingSeconds}s`
    },

    getScoreClass(score) {
      if (score >= 90) return 'excellent'
      if (score >= 75) return 'good'
      if (score >= 60) return 'average'
      return 'needs-improvement'
    },

    getSuccessRate() {
      if (!this.scoreSummary.total_quizzes_attempted) return 0
      // Consider scores >= 60% as successful
      const successfulAttempts = this.recentScores.filter(score => score.total_score >= 60).length
      return Math.round((successfulAttempts / this.scoreSummary.total_quizzes_attempted) * 100)
    }
  }
}
</script>

<style scoped>
.user-dashboard {
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
  margin-bottom: 2rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.user-stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1.5rem;
  text-align: center;
  min-width: 150px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-card h3 {
  color: white;
  font-size: 2rem;
  margin: 0 0 0.5rem 0;
}

.stat-card p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
}

.loading-state, .error-state {
  text-align: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 3rem;
  margin-bottom: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state i {
  font-size: 3rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

.btn-retry {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  margin-top: 1rem;
}

.subjects-section, .recent-scores, .quick-stats {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.subjects-section h2, .recent-scores h2, .quick-stats h2 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.empty-state i {
  color: #ddd;
  margin-bottom: 1rem;
}

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.subject-card {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.subject-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  border-color: #667eea;
}

.subject-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.subject-header h3 {
  color: #333;
  margin: 0;
  font-size: 1.3rem;
  flex: 1;
}

.subject-stats {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  text-align: right;
}

.subject-stats .stat {
  font-size: 0.8rem;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
}

.subject-card p {
  color: #666;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.btn-view {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  transition: transform 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-view:hover {
  transform: scale(1.05);
}

.scores-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.score-item:hover {
  transform: translateY(-2px);
}

.score-info {
  flex: 1;
}

.score-info h4 {
  color: #333;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.score-details {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.score-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.score-badge.large {
  padding: 0.5rem 1rem;
  font-size: 1.2rem;
}

.score-badge.excellent {
  background: #d4edda;
  color: #155724;
}

.score-badge.good {
  background: #d1ecf1;
  color: #0c5460;
}

.score-badge.average {
  background: #fff3cd;
  color: #856404;
}

.score-badge.needs-improvement {
  background: #f8d7da;
  color: #721c24;
}

.questions-info {
  color: #666;
  font-size: 0.9rem;
}

.score-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.subject-chapter {
  color: #667eea;
  font-weight: 500;
  font-size: 0.9rem;
}

.attempt-date {
  color: #999;
  font-size: 0.8rem;
}

.btn-details {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.2s ease;
}

.btn-details:hover {
  transform: scale(1.05);
}

.view-all-scores {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.btn-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: color 0.2s ease;
}

.btn-link:hover {
  color: #5a6fd8;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.performance-card {
  background: white;
  padding: 1.5rem;
  border-radius: 15px;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.performance-card i {
  font-size: 2rem;
  color: #667eea;
  margin-bottom: 1rem;
}

.performance-card h4 {
  color: #333;
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.performance-card p {
  color: #667eea;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 15px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #eee;
  background: #f8f9fa;
}

.modal-header h3 {
  color: #333;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
  padding: 0.25rem;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  background: #f0f0f0;
  color: #333;
}

.modal-body {
  padding: 2rem;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.summary-header h4 {
  color: #333;
  margin: 0;
  flex: 1;
}

.summary-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row .label {
  color: #666;
  font-weight: 500;
}

.detail-row .value {
  color: #333;
  font-weight: 600;
}

.alert {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 16px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 1001;
  min-width: 300px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.alert-success {
  background: #28a745;
}

.alert-error {
  background: #dc3545;
}

@media (max-width: 768px) {
  .user-dashboard {
    padding: 1rem;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
  
  .user-stats {
    flex-direction: column;
    align-items: center;
  }
  
  .subjects-grid, .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .score-item {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .subject-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .subject-stats {
    flex-direction: row;
    align-self: stretch;
    justify-content: space-between;
  }
  
  .score-details {
    justify-content: center;
  }
  
  .modal-content {
    margin: 1rem;
    width: calc(100% - 2rem);
  }
  
  .summary-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>