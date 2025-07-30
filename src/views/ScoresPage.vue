<template>
  <div class="scores-page">
    <div class="header">
      <button @click="goBack" class="btn-back">
        ← Back to Dashboard
      </button>
      <h1>My Quiz Scores</h1>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading your scores...</p>
    </div>

    <div v-else class="scores-content">
      <div class="stats-overview">
        <div class="stat-card">
          <h3>{{ scoreSummary.total_quizzes_attempted || 0 }}</h3>
          <p>Total Quizzes</p>
        </div>
        <div class="stat-card">
          <h3>{{ scoreSummary.total_score || 0 }}</h3>
          <p>Total Points</p>
        </div>
        <div class="stat-card">
          <h3>{{ scoreSummary.average_score || 0 }}%</h3>
          <p>Average Score</p>
        </div>
      </div>

      <div class="scores-section">
        <h2>Quiz History</h2>
        
        <div v-if="scores.length === 0" class="no-scores">
          <h3>No Quiz Attempts Yet</h3>
          <p>You haven't taken any quizzes yet. Start by exploring subjects and taking your first quiz!</p>
          <button @click="goToDashboard" class="btn-primary">Explore Subjects</button>
        </div>

        <div v-else class="scores-list">
          <div 
            v-for="score in scores" 
            :key="score.quiz_id" 
            class="score-card"
            @click="viewQuizSummary(score.quiz_id)"
          >
            <div class="score-info">
              <h3>Quiz #{{ score.quiz_id }}</h3>
              <div class="score-details">
                <span class="score-value">{{ score.total_scored }} points</span>
                <span class="attempt-date">{{ formatDate(score.attempted_on) }}</span>
              </div>
            </div>
            <div class="score-actions">
              <button class="btn-view">View Details</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ScoresPage',
  data() {
    return {
      scores: [],
      scoreSummary: {},
      loading: true
    }
  },
  async created() {
    await this.loadScores()
  },
  methods: {
    async loadScores() {
      try {
        // Load scores
        const scoresResponse = await this.$api.get('/user/scores')
        
        if (scoresResponse.status === 200) {
          this.scores = scoresResponse.data.scores
        }

        // Load score summary
        const summaryResponse = await this.$api.get('/user/score-summary')
        
        if (summaryResponse.status === 200) {
          this.scoreSummary = summaryResponse.data
        }
      } catch (error) {
        console.error('Error loading scores:', error)
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

    viewQuizSummary(quizId) {
      this.$router.push(`/quiz-summary/${quizId}`)
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.scores-page {
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

.scores-content {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-overview {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 3rem;
  flex-wrap: wrap;
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
  font-size: 0.9rem;
}

.scores-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.scores-section h2 {
  color: #333;
  margin-bottom: 2rem;
  font-size: 1.8rem;
  text-align: center;
}

.no-scores {
  text-align: center;
  padding: 3rem;
}

.no-scores h3 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.no-scores p {
  color: #666;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.scores-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.score-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1.5rem;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.score-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #667eea;
}

.score-info h3 {
  color: #333;
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
}

.score-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.score-value {
  color: #667eea;
  font-weight: 600;
  font-size: 1.1rem;
}

.attempt-date {
  color: #999;
  font-size: 0.9rem;
}

.score-actions {
  display: flex;
  gap: 1rem;
}

.btn-view {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.btn-view:hover {
  background: #5a6fd8;
  transform: scale(1.05);
}

@media (max-width: 768px) {
  .scores-page {
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
  
  .stats-overview {
    flex-direction: column;
    align-items: center;
  }
  
  .score-card {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .score-actions {
    justify-content: center;
  }
}
</style> 