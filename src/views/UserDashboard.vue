<template>
  <div class="user-dashboard">
    <div class="dashboard-header">
      <h1>Welcome, {{ user.full_name }}!</h1>
      <div class="user-stats">
        <div class="stat-card">
          <h3>{{ scoreSummary.total_quizzes_attempted || 0 }}</h3>
          <p>Quizzes Attempted</p>
        </div>
        <div class="stat-card">
          <h3>{{ scoreSummary.total_score || 0 }}</h3>
          <p>Total Score</p>
        </div>
        <div class="stat-card">
          <h3>{{ scoreSummary.average_score || 0 }}%</h3>
          <p>Average Score</p>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="subjects-section">
        <h2>Available Subjects</h2>
        <div class="subjects-grid">
          <div 
            v-for="subject in subjects" 
            :key="subject.id" 
            class="subject-card"
            @click="viewQuizzes(subject.id)"
          >
            <h3>{{ subject.name }}</h3>
            <p>{{ subject.description || 'No description available' }}</p>
            <button class="btn-view">View Quizzes</button>
          </div>
        </div>
      </div>

      <div class="recent-scores" v-if="recentScores.length > 0">
        <h2>Recent Quiz Attempts</h2>
        <div class="scores-list">
          <div v-for="score in recentScores" :key="score.quiz_id" class="score-item">
            <div class="score-info">
              <h4>Quiz #{{ score.quiz_id }}</h4>
              <p>Score: {{ score.total_scored }}</p>
              <small>{{ score.attempted_on }}</small>
            </div>
            <button @click="viewQuizSummary(score.quiz_id)" class="btn-details">
              View Details
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Quiz Summary Modal -->
    <div v-if="showQuizSummary" class="modal-overlay" @click="closeQuizSummary">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Quiz Summary</h3>
          <button @click="closeQuizSummary" class="btn-close">&times;</button>
        </div>
        <div class="modal-body" v-if="quizSummary">
          <div class="summary-info">
            <p><strong>Subject:</strong> {{ quizSummary.subject }}</p>
            <p><strong>Chapter:</strong> {{ quizSummary.chapter }}</p>
            <p><strong>Date:</strong> {{ formatDate(quizSummary.date) }}</p>
            <p><strong>Duration:</strong> {{ quizSummary.duration }} minutes</p>
            <p><strong>Your Score:</strong> {{ quizSummary.score }}</p>
            <p><strong>Attempted:</strong> {{ quizSummary.attempted_on }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserDashboard',
  data() {
    return {
      user: {},
      subjects: [],
      recentScores: [],
      scoreSummary: {},
      showQuizSummary: false,
      quizSummary: null
    }
  },
  async created() {
    await this.loadDashboard()
  },
  methods: {
    async loadDashboard() {
      try {
        const token = localStorage.getItem('access_token')
        const userData = localStorage.getItem('user')
        
        if (userData) {
          this.user = JSON.parse(userData)
        }

        // Load subjects
        const subjectsResponse = await fetch('/api/user/dashboard', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (subjectsResponse.ok) {
          const data = await subjectsResponse.json()
          this.subjects = data.subjects
        }

        // Load recent scores
        const scoresResponse = await fetch('/api/user/scores', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (scoresResponse.ok) {
          const data = await scoresResponse.json()
          this.recentScores = data.scores.slice(0, 5) // Show last 5 attempts
        }

        // Load score summary
        const summaryResponse = await fetch('/api/user/score-summary', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (summaryResponse.ok) {
          const data = await summaryResponse.json()
          this.scoreSummary = data
        }
      } catch (error) {
        console.error('Error loading dashboard:', error)
      }
    },

    viewQuizzes(subjectId) {
      this.$router.push(`/user/subject/${subjectId}/quizzes`)
    },

    async viewQuizSummary(quizId) {
      try {
        const token = localStorage.getItem('access_token')
        const response = await fetch(`/api/user/quiz-summary/${quizId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.ok) {
          this.quizSummary = await response.json()
          this.showQuizSummary = true
        }
      } catch (error) {
        console.error('Error loading quiz summary:', error)
      }
    },

    closeQuizSummary() {
      this.showQuizSummary = false
      this.quizSummary = null
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
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

.subjects-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.subjects-section h2 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
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

.subject-card h3 {
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 1.3rem;
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
}

.btn-view:hover {
  transform: scale(1.05);
}

.recent-scores {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.recent-scores h2 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
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
  padding: 1rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.score-info h4 {
  color: #333;
  margin: 0 0 0.5rem 0;
}

.score-info p {
  color: #667eea;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.score-info small {
  color: #999;
}

.btn-details {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
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
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
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
}

.summary-info p {
  margin: 0.5rem 0;
  color: #333;
}

@media (max-width: 768px) {
  .user-dashboard {
    padding: 1rem;
  }
  
  .user-stats {
    flex-direction: column;
    align-items: center;
  }
  
  .subjects-grid {
    grid-template-columns: 1fr;
  }
  
  .score-item {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
}
</style> 