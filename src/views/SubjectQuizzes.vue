<template>
  <div class="subject-quizzes">
    <div class="header">
      <button @click="goBack" class="btn-back">
        ← Back to Dashboard
      </button>
      <h1>{{ subjectName }} Quizzes</h1>
    </div>

    <div class="quizzes-container">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading quizzes...</p>
      </div>

      <div v-else-if="quizzes.length === 0" class="no-quizzes">
        <h3>No quizzes available</h3>
        <p>There are no quizzes available for this subject at the moment.</p>
      </div>

      <div v-else class="quizzes-grid">
        <div 
          v-for="quiz in quizzes" 
          :key="quiz.quiz_id" 
          class="quiz-card"
          :class="{ 'quiz-expired': isQuizExpired(quiz.date) }"
        >
          <div class="quiz-header">
            <h3>{{ quiz.chapter_name }}</h3>
            <span class="quiz-status" :class="getQuizStatus(quiz.date)">
              {{ getQuizStatusText(quiz.date) }}
            </span>
          </div>
          
          <div class="quiz-details">
            <p><strong>Date:</strong> {{ formatDate(quiz.date) }}</p>
            <p><strong>Duration:</strong> {{ quiz.duration }} minutes</p>
            <p v-if="quiz.remarks"><strong>Notes:</strong> {{ quiz.remarks }}</p>
          </div>

          <div class="quiz-actions">
            <button 
              @click="startQuiz(quiz.quiz_id)"
              class="btn-start"
              :disabled="isQuizExpired(quiz.date) || isQuizNotStarted(quiz.date)"
            >
              {{ getActionButtonText(quiz.date) }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SubjectQuizzes',
  data() {
    return {
      subjectId: null,
      subjectName: '',
      quizzes: [],
      loading: true
    }
  },
  async created() {
    this.subjectId = this.$route.params.subjectId
    await this.loadQuizzes()
  },
  methods: {
    async loadQuizzes() {
      try {
        const token = localStorage.getItem('access_token')
        const response = await fetch(`/api/user/quizzes/${this.subjectId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.ok) {
          const data = await response.json()
          this.quizzes = data.quizzes
          // Get subject name from first quiz or set default
          if (this.quizzes.length > 0) {
            this.subjectName = this.quizzes[0].chapter_name.split(' - ')[0] || 'Subject'
          }
        } else {
          console.error('Failed to load quizzes')
        }
      } catch (error) {
        console.error('Error loading quizzes:', error)
      } finally {
        this.loading = false
      }
    },

    goBack() {
      this.$router.push('/dashboard')
    },

    startQuiz(quizId) {
      this.$router.push(`/quiz/${quizId}`)
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

    isQuizExpired(quizDate) {
      const now = new Date()
      const quizEnd = new Date(quizDate)
      quizEnd.setMinutes(quizEnd.getMinutes() + 60) // Assuming 1 hour duration
      return now > quizEnd
    },

    isQuizNotStarted(quizDate) {
      const now = new Date()
      const quizStart = new Date(quizDate)
      return now < quizStart
    },

    getQuizStatus(quizDate) {
      if (this.isQuizExpired(quizDate)) return 'expired'
      if (this.isQuizNotStarted(quizDate)) return 'upcoming'
      return 'active'
    },

    getQuizStatusText(quizDate) {
      if (this.isQuizExpired(quizDate)) return 'Expired'
      if (this.isQuizNotStarted(quizDate)) return 'Upcoming'
      return 'Active'
    },

    getActionButtonText(quizDate) {
      if (this.isQuizExpired(quizDate)) return 'Quiz Expired'
      if (this.isQuizNotStarted(quizDate)) return 'Not Started Yet'
      return 'Start Quiz'
    }
  }
}
</script>

<style scoped>
.subject-quizzes {
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

.quizzes-container {
  max-width: 1200px;
  margin: 0 auto;
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

.no-quizzes {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.no-quizzes h3 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.no-quizzes p {
  color: #666;
  font-size: 1.1rem;
}

.quizzes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.quiz-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 2px solid transparent;
}

.quiz-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0,0,0,0.15);
}

.quiz-card.quiz-expired {
  opacity: 0.7;
  border-color: #ff6b6b;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.quiz-header h3 {
  color: #333;
  margin: 0;
  font-size: 1.4rem;
}

.quiz-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.quiz-status.expired {
  background: #ff6b6b;
  color: white;
}

.quiz-status.upcoming {
  background: #feca57;
  color: #333;
}

.quiz-status.active {
  background: #48dbfb;
  color: white;
}

.quiz-details {
  margin-bottom: 1.5rem;
}

.quiz-details p {
  margin: 0.5rem 0;
  color: #555;
  line-height: 1.5;
}

.quiz-details strong {
  color: #333;
}

.quiz-actions {
  text-align: center;
}

.btn-start {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  width: 100%;
}

.btn-start:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.btn-start:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 768px) {
  .subject-quizzes {
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
  
  .quizzes-grid {
    grid-template-columns: 1fr;
  }
  
  .quiz-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
</style> 