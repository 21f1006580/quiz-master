<template>
  <div class="quiz-summary">
    <div class="header">
      <button @click="goBack" class="btn-back">
        ← Back to Dashboard
      </button>
      <h1>Quiz Summary</h1>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading quiz summary...</p>
    </div>

    <div v-else-if="quizSummary" class="summary-content">
      <div class="summary-card">
        <div class="summary-header">
          <h2>Quiz #{{ quizSummary.quiz_id }}</h2>
          <div class="score-badge">
            <span class="score-value">{{ quizSummary.score }}</span>
            <span class="score-label">Points</span>
          </div>
        </div>

        <div class="summary-details">
          <div class="detail-row">
            <span class="detail-label">Subject:</span>
            <span class="detail-value">{{ quizSummary.subject }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Chapter:</span>
            <span class="detail-value">{{ quizSummary.chapter }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Quiz Date:</span>
            <span class="detail-value">{{ formatDate(quizSummary.date) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Duration:</span>
            <span class="detail-value">{{ quizSummary.duration }} minutes</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Attempted On:</span>
            <span class="detail-value">{{ quizSummary.attempted_on }}</span>
          </div>
          <div v-if="quizSummary.remarks" class="detail-row">
            <span class="detail-label">Notes:</span>
            <span class="detail-value">{{ quizSummary.remarks }}</span>
          </div>
        </div>

        <div class="performance-section">
          <h3>Performance Analysis</h3>
          <div class="performance-metrics">
            <div class="metric">
              <div class="metric-circle" :style="getScoreColor()">
                <span class="metric-value">{{ getScorePercentage() }}%</span>
              </div>
              <p class="metric-label">Success Rate</p>
            </div>
            <div class="metric">
              <div class="metric-circle secondary">
                <span class="metric-value">{{ quizSummary.score }}</span>
              </div>
              <p class="metric-label">Correct Answers</p>
            </div>
          </div>
        </div>

        <div class="actions">
          <button @click="goToDashboard" class="btn-primary">Back to Dashboard</button>
          <button @click="viewAllScores" class="btn-secondary">View All Scores</button>
        </div>
      </div>
    </div>

    <div v-else class="error-state">
      <div class="error-card">
        <h3>Quiz Summary Not Found</h3>
        <p>We couldn't find the summary for this quiz. It's possible that:</p>
        <ul>
          <li>The quiz hasn't been completed yet</li>
          <li>The quiz summary has been removed</li>
          <li>There was an error loading the data</li>
        </ul>
        <button @click="goToDashboard" class="btn-primary">Back to Dashboard</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuizSummary',
  data() {
    return {
      quizId: null,
      quizSummary: null,
      loading: true
    }
  },
  async created() {
    this.quizId = this.$route.params.quizId
    await this.loadQuizSummary()
  },
  methods: {
    async loadQuizSummary() {
      try {
        const token = localStorage.getItem('access_token')
        const response = await fetch(`/api/user/quiz-summary/${this.quizId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.ok) {
          this.quizSummary = await response.json()
        } else {
          console.error('Failed to load quiz summary')
        }
      } catch (error) {
        console.error('Error loading quiz summary:', error)
      } finally {
        this.loading = false
      }
    },

    goBack() {
      this.$router.go(-1)
    },

    goToDashboard() {
      this.$router.push('/dashboard')
    },

    viewAllScores() {
      this.$router.push('/scores')
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    getScorePercentage() {
      // Assuming total questions based on typical quiz structure
      // In a real app, you'd get this from the backend
      const totalQuestions = 10 // This should come from the backend
      return Math.round((this.quizSummary.score / totalQuestions) * 100)
    },

    getScoreColor() {
      const percentage = this.getScorePercentage()
      if (percentage >= 80) return { backgroundColor: '#48dbfb' }
      if (percentage >= 60) return { backgroundColor: '#feca57' }
      return { backgroundColor: '#ff6b6b' }
    }
  }
}
</script>

<style scoped>
.quiz-summary {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
  gap: 2rem;
}

.btn-back {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-5px);
}

.header h1 {
  color: white;
  font-size: 2.5rem;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: white;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.summary-content {
  max-width: 800px;
  margin: 0 auto;
}

.summary-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.summary-header h2 {
  color: #333;
  margin: 0;
  font-size: 2rem;
}

.score-badge {
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 15px;
  min-width: 100px;
}

.score-value {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.score-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.summary-details {
  margin-bottom: 2rem;
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

.detail-label {
  color: #666;
  font-weight: 600;
  min-width: 120px;
}

.detail-value {
  color: #333;
  text-align: right;
  flex: 1;
  margin-left: 1rem;
}

.performance-section {
  margin-bottom: 2rem;
}

.performance-section h3 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.performance-metrics {
  display: flex;
  justify-content: center;
  gap: 3rem;
  flex-wrap: wrap;
}

.metric {
  text-align: center;
}

.metric-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  background: #48dbfb;
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.metric-circle.secondary {
  background: #feca57;
  color: #333;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: bold;
}

.metric-label {
  color: #666;
  font-weight: 600;
  margin: 0;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary {
  padding: 1rem 2rem;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  border: 2px solid #667eea;
}

.btn-primary:hover, .btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.error-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.error-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  max-width: 500px;
  width: 100%;
}

.error-card h3 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}

.error-card p {
  color: #666;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.error-card ul {
  text-align: left;
  color: #666;
  margin-bottom: 2rem;
  padding-left: 2rem;
}

.error-card li {
  margin: 0.5rem 0;
}

@media (max-width: 768px) {
  .quiz-summary {
    padding: 1rem;
  }
  
  .header {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .summary-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .detail-row {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
  
  .detail-value {
    text-align: center;
    margin-left: 0;
  }
  
  .performance-metrics {
    flex-direction: column;
    gap: 2rem;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style> 