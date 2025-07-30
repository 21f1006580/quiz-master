<template>
  <div class="quiz-taking">
    <div class="quiz-header">
      <div class="quiz-info">
        <h1>{{ quizDetails ? quizDetails.title : `Quiz #${quizId}` }}</h1>
        <p v-if="quizDetails">
          {{ quizDetails.subjectName }} - {{ quizDetails.chapterName }}
        </p>
        <p v-if="quizDetails && timerMode === 'quiz'">
          Duration: {{ quizDetails.duration }} minutes
        </p>
      </div>
      
      <div class="timer-section">
        <!-- Quiz Timer -->
        <div v-if="timerMode === 'quiz'" class="timer" :class="{ 'timer-warning': timeLeft < 300 }">
          <span class="timer-label">Quiz Time Remaining:</span>
          <span class="timer-value">{{ formatTime(timeLeft) }}</span>
        </div>
        
        <!-- Question Timer -->
        <div v-else-if="timerMode === 'question'" class="timer" :class="{ 'timer-warning': questionTimeLeft < 10 }">
          <span class="timer-label">Question Time:</span>
          <span class="timer-value">{{ formatTime(questionTimeLeft) }}</span>
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
          <h3>Your Score: {{ finalScore }}%</h3>
          <p>{{ correctAnswersCount }} out of {{ totalQuestions }} questions correct</p>
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
        <span class="progress-text">
          Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}
          <span v-if="showInstantFeedback" class="score-preview">
            ({{ correctAnswersCount }}/{{ answeredCount }} correct)
          </span>
        </span>
      </div>

      <div class="question-container">
        <div class="question-header">
          <h2>Question {{ currentQuestionIndex + 1 }}</h2>
          <div v-if="timerMode === 'question'" class="question-timer">
            <i class="fas fa-clock"></i>
            {{ questionTimeLeft }}s
          </div>
        </div>
        
        <div class="question-content">
          <p class="question-text">{{ currentQuestion ? currentQuestion.statement : 'Loading question...' }}</p>
          
          <div class="options-list">
            <label 
            v-for="(option, index) in (currentQuestion && currentQuestion.options ? currentQuestion.options : [])" 
            :key="index"
            :class="[
              'option-item', 
              { 'selected': currentQuestion && selectedAnswers[currentQuestion.id] === index + 1 },
              getOptionClass(index)
            ]"
            >
              <input 
                type="radio" 
                :name="'question-' + (currentQuestion ? currentQuestion.id : 0)"
                :value="index + 1"
                v-model="selectedAnswers[currentQuestion ? currentQuestion.id : 0]"
                @change="saveAnswer"
                :disabled="currentQuestionFeedback && timerMode === 'question'"
                v-if="currentQuestion"
              />
              <span class="option-text">{{ option }}</span>
              <span v-if="getOptionClass(index) === 'option-correct'" class="feedback-icon correct">
                <i class="fas fa-check"></i>
              </span>
              <span v-else-if="getOptionClass(index) === 'option-incorrect'" class="feedback-icon incorrect">
                <i class="fas fa-times"></i>
              </span>
              <span v-else-if="getOptionClass(index) === 'option-show-correct'" class="feedback-icon show-correct">
                <i class="fas fa-check"></i>
              </span>
            </label>
          </div>
          
          <!-- Navigation buttons -->
          <div class="navigation-buttons">
            <button 
              @click="previousQuestion" 
              :disabled="currentQuestionIndex === 0"
              class="btn-secondary"
            >
              <i class="fas fa-arrow-left"></i> Previous
            </button>
            
            <button 
              @click="nextQuestion" 
              :disabled="currentQuestionIndex === questions.length - 1"
              class="btn-secondary"
            >
              Next <i class="fas fa-arrow-right"></i>
            </button>
            
            <button 
              @click="submitAnswers" 
              :disabled="submitting"
              class="btn-primary submit-btn"
            >
              <i class="fas fa-paper-plane"></i> Submit Quiz
            </button>
          </div>

          <!-- Instant Feedback Display -->
          <div v-if="currentQuestionFeedback" class="feedback-panel" 
               :class="currentQuestionFeedback.type">
            <div class="feedback-header">
              <i v-if="currentQuestionFeedback.isCorrect" class="fas fa-check-circle"></i>
              <i v-else-if="currentQuestionFeedback.type === 'timeout'" class="fas fa-clock"></i>
              <i v-else class="fas fa-times-circle"></i>
              <span>{{ currentQuestionFeedback.message }}</span>
            </div>
            <div v-if="currentQuestionFeedback.explanation" class="feedback-explanation">
              {{ currentQuestionFeedback.explanation }}
            </div>
          </div>
        </div>
      </div>

      <div class="navigation-buttons">
        <!-- Question Indicators - Always visible -->
        <div class="question-indicators">
          <button 
            v-for="(question, index) in questions" 
            :key="index"
            @click="goToQuestion(index)"
            class="indicator-btn"
            :class="{
              'answered': selectedAnswers[question.id],
              'current': currentQuestionIndex === index,
              'correct': questionFeedback && questionFeedback[question.id] && questionFeedback[question.id].isCorrect,
              'incorrect': questionFeedback && questionFeedback[question.id] && !questionFeedback[question.id].isCorrect
            }"
            :disabled="timerMode === 'question' && index !== currentQuestionIndex"
          >
            {{ index + 1 }}
            <i v-if="questionFeedback && questionFeedback[question.id] && questionFeedback[question.id].isCorrect" 
               class="fas fa-check indicator-icon"></i>
            <i v-else-if="questionFeedback && questionFeedback[question.id] && !questionFeedback[question.id].isCorrect" 
               class="fas fa-times indicator-icon"></i>
          </button>
        </div>
        
        <!-- Navigation Info for Question Timer Mode -->
        <div v-if="timerMode === 'question'" class="auto-progress-info">
          <p>
            <i class="fas fa-info-circle"></i>
            Questions advance automatically after 30 seconds or when answered
          </p>
        </div>
        
        <!-- Manual Navigation (only for quiz timer mode) -->
        <div v-else class="manual-navigation">
          <button 
            @click="previousQuestion" 
            class="btn-nav"
            :disabled="currentQuestionIndex === 0"
          >
            ← Previous
          </button>
          
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
          <p v-if="showInstantFeedback">
            <strong>Correct so far:</strong> {{ correctAnswersCount }} / {{ answeredCount }}
          </p>
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

// Enhanced QuizTaking.vue with auto-expiry monitoring

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
      
      // Timer management
      questionTimeLeft: 30,
      questionTimer: null,
      quizTimeLeft: 0,
      quizTimer: null,
      timerMode: 'quiz', // 'quiz' or 'question'
      
      // Auto-expiry monitoring
      quizExpiryTime: null,
      expiryCheckInterval: null,
      timeUntilExpiry: null,
      showExpiryWarning: false,
      autoExpireEnabled: false,
      
      // Quiz progress and feedback
      showInstantFeedback: false,
      currentQuestionFeedback: null,
      questionFeedback: {},
      
      // Submission state
      submitting: false,
      showConfirmModal: false,
      
      error: null
    }
  },

  computed: {
    timeUntilExpiryFormatted() {
      if (!this.timeUntilExpiry) return null
      
      const hours = Math.floor(this.timeUntilExpiry / 60)
      const minutes = this.timeUntilExpiry % 60
      
      if (hours > 0) {
        return `${hours}h ${minutes}m`
      } else {
        return `${minutes}m`
      }
    },

    shouldShowExpiryWarning() {
      return this.autoExpireEnabled && this.timeUntilExpiry && this.timeUntilExpiry <= 10
    },

    currentQuestion() {
      if (!this.questions || this.questions.length === 0 || this.currentQuestionIndex >= this.questions.length) {
        return null
      }
      return this.questions[this.currentQuestionIndex]
    },

    progressPercentage() {
      if (this.questions.length === 0) return 0
      return ((this.currentQuestionIndex + 1) / this.questions.length) * 100
    },

    answeredCount() {
      return Object.keys(this.selectedAnswers).length
    },

    correctAnswersCount() {
      let count = 0
      Object.keys(this.selectedAnswers).forEach(questionId => {
        const question = this.questions.find(q => q.id.toString() === questionId)
        if (question && this.selectedAnswers[questionId] === 1) { // Assuming correct_option is 1
          count++
        }
      })
      return count
    },

    timeLeft() {
      // Return the actual quiz time left
      return this.quizTimeLeft || 0
    }
  },

  async created() {
    this.quizId = this.$route.params.quizId
    await this.loadQuiz()
  },

  beforeDestroy() {
    this.clearAllTimers()
  },

  methods: {
    async loadQuiz() {
      try {
        console.log("Loading quiz with auto-expiry check...")
        this.loading = true
        this.error = null

        const token = localStorage.getItem('access_token')
        if (!token) {
          this.$router.push('/login')
          return
        }

        const response = await this.$api.get(`/user/quiz/${this.quizId}/take`)
        console.log('API Response:', response)
        
        if (response.status === 200) {
          const data = response.data
          console.log("Quiz data with expiry info:", data)
          
          // Ensure we have valid quiz data
          if (!data || !data.quiz_id) {
            throw new Error('Invalid quiz data received')
          }
          
          this.quizDetails = {
            id: data.quiz_id,
            title: data.title || 'Untitled Quiz',
            duration: data.duration || 30,
            totalQuestions: data.total_questions || 0,
            chapterName: data.chapter_name || 'Unknown Chapter',
            subjectName: data.subject_name || 'Unknown Subject'
          }
          
          this.questions = data.questions || []
          this.totalQuestions = this.questions.length
          console.log('Loaded questions:', this.questions)
          
          // Ensure we have at least one question
          if (this.questions.length === 0) {
            throw new Error('No questions available for this quiz')
          }
          
          // Initialize selectedAnswers object
          this.selectedAnswers = {}
          
          // Set up auto-expiry monitoring
          this.autoExpireEnabled = data.auto_expire_enabled || false
          this.timeUntilExpiry = data.time_remaining_until_expiry
          
          if (data.quiz_expires_at) {
            this.quizExpiryTime = new Date(data.quiz_expires_at)
            this.startExpiryMonitoring()
          }
          
          // Start quiz timer and question timer if we have questions
          if (this.questions.length > 0) {
            this.startQuizTimer()
            this.startQuestionTimer()
          }
          
        } else {
          this.error = (response.data && response.data.error) ? response.data.error : 'Failed to load quiz'
          console.error("Quiz loading error:", this.error)
          
          // Show specific error for expired quiz
          if (response.data && response.data.quiz_status === 'expired') {
            alert('This quiz has expired and is no longer available.')
          } else {
            alert(this.error)
          }
          
          setTimeout(() => {
            this.$router.push('/dashboard')
          }, 2000)
        }

      } catch (error) {
        console.error('Error loading quiz:', error)
        this.error = error.message || 'Failed to load quiz'
        alert('Error loading quiz: ' + this.error)
        this.$router.push('/dashboard')
      } finally {
        this.loading = false
      }
    },

    startExpiryMonitoring() {
      if (!this.autoExpireEnabled || !this.quizExpiryTime) return

      console.log("Starting quiz expiry monitoring...")
      console.log("Quiz expires at:", this.quizExpiryTime)
      
      // Check expiry every 30 seconds
      this.expiryCheckInterval = setInterval(() => {
        this.checkQuizExpiry()
      }, 30000)
      
      // Also check immediately
      this.checkQuizExpiry()
    },

    async checkQuizExpiry() {
      if (!this.autoExpireEnabled) return

      try {
        const now = new Date()
        
        // Calculate time until expiry
        if (this.quizExpiryTime) {
          const timeDiff = this.quizExpiryTime.getTime() - now.getTime()
          this.timeUntilExpiry = Math.max(0, Math.floor(timeDiff / (1000 * 60))) // minutes
          
          // Check if quiz has expired
          if (this.timeUntilExpiry <= 0) {
            console.log("Quiz has expired!")
            this.handleQuizExpired()
            return
          }
          
          // Show warning if expiring soon
          if (this.timeUntilExpiry <= 5 && !this.showExpiryWarning) {
            this.showExpiryWarning = true
            this.showExpiryAlert()
          }
        }
        
        // Double-check with server every 2 minutes
        if (Math.floor(Date.now() / 1000) % 120 === 0) {
          await this.checkQuizStatusWithServer()
        }
        
      } catch (error) {
        console.error('Error checking quiz expiry:', error)
      }
    },

    async checkQuizStatusWithServer() {
      try {
        const token = localStorage.getItem('access_token')
        const response = await this.$api.get(`/user/quiz/${this.quizId}/status`)
        
        if (response.ok) {
          const data = await response.json()
          
          if (!data.is_available) {
            console.log("Server says quiz is no longer available:", data.availability_message)
            this.handleQuizExpired(data.availability_message)
          } else {
            // Update time remaining from server
            this.timeUntilExpiry = data.time_remaining
            if (data.expires_at) {
              this.quizExpiryTime = new Date(data.expires_at)
            }
          }
        }
      } catch (error) {
        console.error('Error checking quiz status with server:', error)
      }
    },

    handleQuizExpired(message = 'This quiz has expired') {
      this.clearAllTimers()
      
      // Show expiry message
      alert(`${message}\n\nYour quiz attempt will be automatically submitted.`)
      
      // Auto-submit if user has answered any questions
      if (Object.keys(this.selectedAnswers).length > 0) {
        console.log("Auto-submitting quiz due to expiry...")
        this.submitAnswers()
      } else {
        // No answers to submit, just redirect
        this.$router.push('/dashboard')
      }
    },

    showExpiryAlert() {
      const timeLeft = this.timeUntilExpiryFormatted
      alert(`⚠️ Warning: This quiz will expire in ${timeLeft}!\n\nPlease submit your answers soon.`)
    },

    startQuizTimer() {
      if (!this.quizDetails || !this.quizDetails.duration) return
      
      this.quizTimeLeft = this.quizDetails.duration * 60 // Convert minutes to seconds
      
      this.quizTimer = setInterval(() => {
        if (this.quizTimeLeft > 0) {
          this.quizTimeLeft--
        } else {
          // Quiz time expired
          this.clearAllTimers()
          alert('Quiz time has expired! Your answers will be submitted automatically.')
          this.submitAnswers()
        }
      }, 1000)
    },

    startQuestionTimer() {
      this.questionTimeLeft = 30
      
      this.questionTimer = setInterval(() => {
        if (this.questionTimeLeft > 0) {
          this.questionTimeLeft--
        } else {
          this.moveToNextQuestionOrSubmit()
        }
      }, 1000)
    },

    moveToNextQuestionOrSubmit() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++
        this.startQuestionTimer()
      } else {
        // Last question - auto submit
        this.clearAllTimers()
        this.submitAnswers()
      }
    },

    clearAllTimers() {
      if (this.questionTimer) {
        clearInterval(this.questionTimer)
        this.questionTimer = null
      }
      if (this.quizTimer) {
        clearInterval(this.quizTimer)
        this.quizTimer = null
      }
      if (this.expiryCheckInterval) {
        clearInterval(this.expiryCheckInterval)
        this.expiryCheckInterval = null
      }
    },

    async saveAnswer() {
      console.log("Answer saved:", this.selectedAnswers)
      
      // Check if quiz is still available before allowing answer
      if (this.timeUntilExpiry && this.timeUntilExpiry <= 0) {
        alert('Quiz has expired. Your answer was not saved.')
        this.handleQuizExpired()
        return
      }
      
      // Don't auto-advance - let user control navigation
      // Only auto-advance if it's the last question and user wants to submit
    },

    async submitAnswers() {
      // Prevent multiple submissions
      if (this.submitting) {
        console.log("Submission already in progress...")
        return
      }
      
      try {
        this.submitting = true
        console.log("Submitting answers with expiry check...")
        
        const token = localStorage.getItem('access_token')
        const totalTimeSpent = this.questions.length * 30 // Approximate time
        
        const formattedAnswers = {}
        Object.keys(this.selectedAnswers).forEach(questionId => {
          formattedAnswers[questionId] = this.selectedAnswers[questionId] - 1
        })
        
        const response = await this.$api.post(`/user/quiz/${this.quizId}/submit`, {
          answers: formattedAnswers,
          time_taken: totalTimeSpent
        })
        
        if (response.status === 200) {
          const data = response.data
          console.log("Submit response:", data)
          
          this.finalScore = (data.score && data.score.percentage_score) ? data.score.percentage_score : 0
          this.quizCompleted = true
          
          // Show success message
          alert(`Quiz submitted successfully! Your score: ${this.finalScore}%`)
          
          // Show warning if quiz expired during submission
          if (data.warning) {
            setTimeout(() => {
              alert(`Note: ${data.warning}`)
            }, 1000)
          }
          
          // Redirect to dashboard after a short delay
          setTimeout(() => {
            this.$router.push('/dashboard')
          }, 2000)
          
        } else {
          console.error("Submit error:", response.data)
          
          if (response.data && response.data.error && response.data.error.includes('expired')) {
            alert('Quiz expired before submission could be completed.')
            this.$router.push('/dashboard')
          } else {
            alert('Error submitting quiz: ' + ((response.data && response.data.error) ? response.data.error : 'Unknown error'))
          }
        }
      } catch (error) {
        console.error('Error submitting quiz:', error)
        alert('Error submitting quiz. Please try again.')
      } finally {
        this.submitting = false
      }
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

    openConfirmModal() {
      this.showConfirmModal = true
    },

    closeConfirmModal() {
      this.showConfirmModal = false
    },

    confirmSubmit() {
      this.showConfirmModal = false
      this.submitAnswers()
    },

    getOptionClass(index) {
      if (!this.currentQuestionFeedback || !this.currentQuestion) return ''
      
      const userAnswer = this.selectedAnswers[this.currentQuestion.id]
      const correctOption = 1 // Assuming correct_option is 1
      
      if (userAnswer === index + 1) {
        if (userAnswer === correctOption) {
          return 'option-correct'
        } else {
          return 'option-incorrect'
        }
      } else if (index + 1 === correctOption) {
        return 'option-show-correct'
      }
      
      return ''
    },

    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    },

    viewResults() {
      // Navigate to results page or show detailed results
      this.$router.push(`/quiz/${this.quizId}/results`)
    },

    goToDashboard() {
      this.$router.push('/dashboard')
    },

    goToQuestion(index) {
      if (index >= 0 && index < this.questions.length) {
        this.currentQuestionIndex = index
      }
    }
  }
}
</script>

<style scoped>
/* Enhanced Quiz Styles with Timer and Feedback */

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
  margin: 0.25rem 0;
}

.timer-section {
  text-align: center;
}

.timer {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.timer-warning {
  border-color: #ff6b6b;
  background: rgba(255, 107, 107, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
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

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.question-timer {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-text .score-preview {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85em;
}

/* Option Feedback Styles */
.option-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  position: relative;
}

.option-item:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

.option-item.selected {
  border-color: #667eea;
  background: #f0f4ff;
}

/* Feedback-specific option styles */
.option-item.option-correct {
  border-color: #28a745;
  background: #d4edda;
  color: #155724;
}

.option-item.option-incorrect {
  border-color: #dc3545;
  background: #f8d7da;
  color: #721c24;
}

.option-item.option-show-correct {
  border-color: #28a745;
  background: #d4edda;
  color: #155724;
  animation: highlight 2s ease-in-out;
}

@keyframes highlight {
  0% { background: #d4edda; }
  50% { background: #b4d6bb; }
  100% { background: #d4edda; }
}

.feedback-icon {
  position: absolute;
  right: 1rem;
  font-size: 1.2rem;
  font-weight: bold;
}

.feedback-icon.correct {
  color: #28a745;
}

.feedback-icon.incorrect {
  color: #dc3545;
}

.feedback-icon.show-correct {
  color: #28a745;
}

/* Feedback Panel */
.feedback-panel {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 10px;
  border-left: 4px solid;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.feedback-panel.correct {
  background: #d4edda;
  border-left-color: #28a745;
  color: #155724;
}

.feedback-panel.incorrect {
  background: #f8d7da;
  border-left-color: #dc3545;
  color: #721c24;
}

.feedback-panel.timeout {
  background: #fff3cd;
  border-left-color: #ffc107;
  color: #856404;
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.feedback-explanation {
  font-style: italic;
  opacity: 0.9;
}

/* Navigation Styles */
.navigation-buttons {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
}

.question-indicators {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.auto-progress-info {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
}

.auto-progress-info p {
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.manual-navigation {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* Enhanced Question Indicators */
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
  position: relative;
}

.indicator-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.indicator-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.indicator-btn.answered {
  background: #48dbfb;
  border-color: #48dbfb;
}

.indicator-btn.current {
  background: #667eea;
  border-color: #667eea;
  transform: scale(1.1);
}

.indicator-btn.correct {
  background: #28a745;
  border-color: #28a745;
}

.indicator-btn.incorrect {
  background: #dc3545;
  border-color: #dc3545;
}

.indicator-icon {
  position: absolute;
  top: -2px;
  right: -2px;
  background: white;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
}

/* Button Styles */
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

/* Completion Card Enhancements */
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

/* Navigation Buttons */
.navigation-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.navigation-buttons button {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.navigation-buttons button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: bold;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header h3 {
  margin: 0 0 1rem 0;
  color: #333;
}

.modal-body p {
  margin: 0.5rem 0;
  color: #666;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  justify-content: flex-end;
}

.btn-cancel, .btn-confirm {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #f8f9fa;
  color: #666;
}

.btn-confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

/* Option Feedback Styles */
.option-correct {
  background: #d4edda !important;
  border-color: #c3e6cb !important;
}

.option-incorrect {
  background: #f8d7da !important;
  border-color: #f5c6cb !important;
}

.option-show-correct {
  background: #d4edda !important;
  border-color: #c3e6cb !important;
}

.feedback-icon {
  margin-left: 0.5rem;
  font-size: 0.9rem;
}

.feedback-icon.correct {
  color: #28a745;
}

.feedback-icon.incorrect {
  color: #dc3545;
}

.feedback-icon.show-correct {
  color: #28a745;
}

/* Responsive Design */
@media (max-width: 768px) {
  .quiz-taking {
    padding: 1rem;
  }
  
  .quiz-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .question-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
    text-align: center;
  }
  
  .navigation-buttons {
    gap: 1rem;
  }
  
  .manual-navigation {
    flex-direction: column;
    gap: 1rem;
  }
  
  .feedback-panel {
    margin-top: 1rem;
    padding: 0.75rem;
  }
}
  .quiz-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .question-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
    text-align: center;
  }
  
  .navigation-buttons {
    flex-direction: column;
    gap: 1rem;
  }
  
  .question-indicators {
    order: -1;
  }
  
  .feedback-panel {
    margin-top: 1rem;
    padding: 0.75rem;
  }

</style> 