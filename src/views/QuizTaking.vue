<template>
  <div class="quiz-taking">
    <div class="quiz-header">
      <div class="quiz-info">
        <h1>Quiz #{{ quizId }}</h1>
        <p v-if="quizDetails">Duration: {{ quizDetails.duration }} minutes</p>
      </div>
      
      <div class="timer-section">
        <div class="timer" :class="{ 'timer-warning': timeLeft < 300 }">
          <span class="timer-label">Time Remaining:</span>
          <span class="timer-value">{{ formatTime(timeLeft) }}</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading quiz...</p>
    </div>

    <div v-else-if="quizCompleted" class="quiz-completed">
      <div class="completion-card">
        <h2>Quiz Completed!</h2>
        <div class="score-display">
          <h3>Your Score: {{ finalScore }}</h3>
          <p>Out of {{ totalQuestions }} questions</p>
        </div>
        <div class="completion-actions">
          <button @click="goToDashboard" class="btn-primary">Back to Dashboard</button>
          <button @click="viewResults" class="btn-secondary">View Detailed Results</button>
        </div>
      </div>
    </div>

    <div v-else class="quiz-content">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        <span class="progress-text">Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}</span>
      </div>

      <div class="question-container">
        <div class="question-header">
          <h2>Question {{ currentQuestionIndex + 1 }}</h2>
        </div>
        
        <div class="question-content">
          <p class="question-text">{{ currentQuestion.statement }}</p>
          
          <div class="options-list">
            <label 
              v-for="(option, index) in currentQuestion.options" 
              :key="index"
              :class="['option-item', { 'selected': selectedAnswers[currentQuestion.id] === index + 1 }]"
            >
              <input 
                type="radio" 
                :name="'question-' + currentQuestion.id"
                :value="index + 1"
                v-model="selectedAnswers[currentQuestion.id]"
                @change="saveAnswer"
              />
              <span class="option-text">{{ option }}</span>
            </label>
          </div>
        </div>
      </div>

      <div class="navigation-buttons">
        <button 
          @click="previousQuestion" 
          class="btn-nav"
          :disabled="currentQuestionIndex === 0"
        >
          ← Previous
        </button>
        
        <div class="question-indicators">
          <button 
            v-for="(question, index) in questions" 
            :key="index"
            @click="goToQuestion(index)"
            class="indicator-btn"
            :class="{
              'answered': selectedAnswers[question.id],
              'current': currentQuestionIndex === index
            }"
          >
            {{ index + 1 }}
          </button>
        </div>
        
        <button 
          v-if="currentQuestionIndex < questions.length - 1"
          @click="nextQuestion" 
          class="btn-nav"
        >
          Next →
        </button>
        
        <button 
          v-else
          @click="submitQuiz" 
          class="btn-submit"
          :disabled="!canSubmit"
        >
          Submit Quiz
        </button>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmModal" class="modal-overlay" @click="closeConfirmModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Confirm Submission</h3>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to submit your quiz?</p>
          <p><strong>Answered:</strong> {{ answeredCount }} / {{ questions.length }} questions</p>
          <p><strong>Unanswered:</strong> {{ questions.length - answeredCount }} questions</p>
        </div>
        <div class="modal-actions">
          <button @click="closeConfirmModal" class="btn-cancel">Cancel</button>
          <button @click="confirmSubmit" class="btn-confirm">Submit Quiz</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// Fixed QuizTaking.vue component
export default {
  name: 'QuizTaking',
  data() {
    return {
      quizId: null,
      quizDetails: null,
      questions: [],
      currentQuestionIndex: 0,
      selectedAnswers: {},
      loading: true,
      quizCompleted: false,
      finalScore: 0,
      totalQuestions: 0,
      timeLeft: 0,
      timer: null,
      showConfirmModal: false,
      error: null
    }
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || {}
    },
    progressPercentage() {
      return this.questions.length > 0 ? ((this.currentQuestionIndex + 1) / this.questions.length) * 100 : 0
    },
    answeredCount() {
      return Object.keys(this.selectedAnswers).length
    },
    canSubmit() {
      return this.answeredCount > 0
    }
  },
  async created() {
    this.quizId = this.$route.params.quizId
    console.log("Quiz ID from route:", this.quizId)
    await this.loadQuiz()
  },
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  methods: {
    async loadQuiz() {
      try {
        console.log("Loading quiz with ID:", this.quizId)
        this.loading = true
        this.error = null

        const token = localStorage.getItem('access_token')
        if (!token) {
          console.log("No token found, redirecting to login")
          this.$router.push('/login')
          return
        }

        // FIXED: Use the correct endpoint that matches your Flask route
        const response = await fetch(`http://localhost:5000/api/user/quiz/${this.quizId}/take`, {
          method: 'GET',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        console.log("Quiz API response status:", response.status)
        
        if (response.ok) {
          const data = await response.json()
          console.log("Quiz data received:", data)
          
          // Store the full quiz details
          this.quizDetails = {
            id: data.quiz_id,
            title: data.title,
            duration: data.duration,
            totalQuestions: data.total_questions,
            chapterName: data.chapter_name,
            subjectName: data.subject_name
          }
          
          this.questions = data.questions || []
          this.totalQuestions = this.questions.length
          
          // FIXED: Only start timer if we have valid duration
          if (data.duration && data.duration > 0) {
            this.timeLeft = data.duration * 60 // Convert to seconds
            this.startTimer()
          }
          
          console.log("Questions loaded:", this.questions.length)
          console.log("Quiz details:", this.quizDetails)
          
        } else {
          const errorData = await response.json()
          this.error = errorData.error || 'Failed to load quiz'
          console.error("Quiz loading error:", this.error)
          
          // Show error message and redirect after delay
          alert(this.error)
          setTimeout(() => {
            this.$router.push('/user/dashboard')
          }, 2000)
        }

      } catch (error) {
        console.error('Error loading quiz:', error)
        this.error = error.message || 'Failed to load quiz'
        alert('Error loading quiz: ' + this.error)
        this.$router.push('/user/dashboard')
      } finally {
        this.loading = false
      }
    },

    startTimer() {
      if (this.timeLeft <= 0) return
      
      this.timer = setInterval(() => {
        if (this.timeLeft > 0) {
          this.timeLeft--
        } else {
          console.log("Time's up! Auto-submitting quiz")
          this.submitQuiz()
        }
      }, 1000)
    },

    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
    },

    saveAnswer() {
      console.log("Answer saved:", this.selectedAnswers)
    },

    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
      }
    },

    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++
      }
    },

    goToQuestion(index) {
      this.currentQuestionIndex = index
    },

    submitQuiz() {
      console.log("Submit quiz called, answered count:", this.answeredCount)
      
      if (this.answeredCount === 0) {
        alert('Please answer at least one question before submitting.')
        return
      }
      this.showConfirmModal = true
    },

    async confirmSubmit() {
      this.showConfirmModal = false
      await this.submitAnswers()
    },

    closeConfirmModal() {
      this.showConfirmModal = false
    },

    async submitAnswers() {
      try {
        console.log("Submitting answers:", this.selectedAnswers)
        
        const token = localStorage.getItem('access_token')
        const startTime = Date.now()
        
        // FIXED: Convert selectedAnswers to the format expected by backend
        const formattedAnswers = {}
        Object.keys(this.selectedAnswers).forEach(questionId => {
          // Convert to 0-based index for backend
          formattedAnswers[questionId] = this.selectedAnswers[questionId] - 1
        })
        
        const response = await fetch(`http://localhost:5000/api/user/quiz/${this.quizId}/submit`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            answers: formattedAnswers,
            time_taken: Math.floor((Date.now() - startTime) / 1000)
          })
        })
        
        console.log("Submit response status:", response.status)
        
        if (response.ok) {
          const data = await response.json()
          console.log("Submit response data:", data)
          
          this.finalScore = (data.score && data.score.percentage_score) ? data.score.percentage_score : 0
          this.quizCompleted = true
          
          if (this.timer) {
            clearInterval(this.timer)
          }
        } else {
          const errorData = await response.json()
          console.error("Submit error:", errorData)
          alert('Error submitting quiz: ' + (errorData.error || 'Unknown error'))
        }
      } catch (error) {
        console.error('Error submitting quiz:', error)
        alert('Error submitting quiz. Please try again.')
      }
    },

    goToDashboard() {
      this.$router.push('/user/dashboard')
    },

    viewResults() {
      this.$router.push(`/user/quiz/${this.quizId}/results`)
    }
  }
}
</script>

<style scoped>
.quiz-taking {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.quiz-info h1 {
  color: white;
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
}

.quiz-info p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.timer-section {
  text-align: center;
}

.timer {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.timer-warning {
  border-color: #ff6b6b;
  background: rgba(255, 107, 107, 0.2);
}

.timer-label {
  display: block;
  color: white;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.timer-value {
  display: block;
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
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

.quiz-completed {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.completion-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  max-width: 500px;
  width: 100%;
}

.completion-card h2 {
  color: #333;
  margin-bottom: 2rem;
  font-size: 2rem;
}

.score-display {
  margin-bottom: 2rem;
}

.score-display h3 {
  color: #667eea;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.score-display p {
  color: #666;
  font-size: 1.1rem;
}

.completion-actions {
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

.quiz-content {
  max-width: 800px;
  margin: 0 auto;
}

.progress-bar {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  height: 20px;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.progress-fill {
  background: linear-gradient(90deg, #48dbfb 0%, #0abde3 100%);
  height: 100%;
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.question-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.question-header h2 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.question-text {
  color: #333;
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.option-item:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

.option-item.selected {
  border-color: #667eea;
  background: #f0f4ff;
}

.option-item input[type="radio"] {
  margin-right: 1rem;
  transform: scale(1.2);
}

.option-text {
  color: #333;
  font-size: 1rem;
  line-height: 1.4;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-nav, .btn-submit {
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-nav {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-nav:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.btn-nav:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-submit {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.btn-submit:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.question-indicators {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.indicator-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.indicator-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.indicator-btn.answered {
  background: #48dbfb;
  border-color: #48dbfb;
}

.indicator-btn.current {
  background: #667eea;
  border-color: #667eea;
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
  max-width: 400px;
  width: 90%;
}

.modal-header h3 {
  color: #333;
  margin-bottom: 1rem;
}

.modal-body p {
  color: #666;
  margin: 0.5rem 0;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-cancel, .btn-confirm {
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  font-weight: 600;
}

.btn-cancel {
  background: #f8f9fa;
  color: #666;
}

.btn-confirm {
  background: #ff6b6b;
  color: white;
}

@media (max-width: 768px) {
  .quiz-taking {
    padding: 1rem;
  }
  
  .quiz-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .navigation-buttons {
    flex-direction: column;
    gap: 1rem;
  }
  
  .question-indicators {
    order: -1;
  }
  
  .completion-actions {
    flex-direction: column;
  }
}
</style> 