<template>
  <div class="quiz-taking">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading quiz...</p>
      <div class="debug-info" v-if="showDebug">
        <p>Quiz ID: {{ quizId }}</p>
        <p>API Response: {{ debugInfo.responseReceived ? 'Yes' : 'No' }}</p>
        <p>Questions Count: {{ questions.length }}</p>
        <p>Error: {{ error || 'None' }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-card">
        <i class="fas fa-exclamation-triangle"></i>
        <h2>Unable to Load Quiz</h2>
        <p>{{ error }}</p>
        <button @click="goToDashboard" class="btn-primary">Back to Dashboard</button>
      </div>
    </div>

    <!-- Quiz Completed State -->
    <div v-else-if="quizCompleted" class="quiz-completed">
      <div class="completion-card">
        <i class="fas fa-check-circle completion-icon"></i>
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

    <!-- Main Quiz Interface -->
    <div v-else class="quiz-content">
      <!-- Header -->
      <div class="quiz-header">
        <div class="quiz-info">
          <h1>{{ quizDetails.title }}</h1>
          <p v-if="quizDetails.chapterName">
            {{ quizDetails.subjectName }} - {{ quizDetails.chapterName }}
          </p>
          <p>Duration: {{ quizDetails.duration }} minutes</p>
        </div>
        
        <div class="timer-section">
          <div v-if="showExpiryWarning" class="expiry-warning">
            <i class="fas fa-exclamation-triangle"></i>
            <span>Quiz expires in {{ timeUntilExpiryFormatted }}!</span>
          </div>
          
          <div class="timer" :class="{ 'timer-warning': questionTimeLeft <= 10 }">
            <span class="timer-label">Question Time:</span>
            <span class="timer-value">{{ questionTimeLeft }}s</span>
          </div>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        <span class="progress-text">
          Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}
          <span class="score-preview">({{ answeredCount }} answered)</span>
        </span>
      </div>

      <!-- Question Container -->
      <div class="question-container" v-if="currentQuestion">
        <div class="question-header">
          <h2>Question {{ currentQuestionIndex + 1 }}</h2>
        </div>
        
        <div class="question-content">
          <p class="question-text">{{ currentQuestion.statement }}</p>
          
          <div class="options-list">
            <label 
              v-for="(option, index) in currentQuestion.options" 
              :key="index"
              :class="[
                'option-item', 
                { 
                  'selected': selectedAnswers[currentQuestion.id] === index + 1,
                  'disabled': questionAnswered && autoAdvanceEnabled
                }
              ]"
            >
              <input 
                type="radio" 
                :name="'question-' + currentQuestion.id"
                :value="index + 1"
                v-model="selectedAnswers[currentQuestion.id]"
                @change="handleAnswerSelect"
                :disabled="questionAnswered && autoAdvanceEnabled"
              />
              <span class="option-letter">{{ String.fromCharCode(65 + index) }}.</span>
              <span class="option-text">{{ option }}</span>
              <span v-if="selectedAnswers[currentQuestion.id] === index + 1" class="selected-icon">
                <i class="fas fa-check"></i>
              </span>
            </label>
          </div>

          <!-- Answer Feedback -->
          <div v-if="questionAnswered && showInstantFeedback" class="feedback-panel">
            <p class="feedback-message">Answer recorded! Moving to next question...</p>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="navigation-section">
        <!-- Question Indicators -->
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
            :disabled="autoAdvanceEnabled && index !== currentQuestionIndex"
          >
            {{ index + 1 }}
          </button>
        </div>
        
        <!-- Progress Info -->
        <div class="progress-info">
          <p v-if="autoAdvanceEnabled">
            <i class="fas fa-info-circle"></i>
            Questions advance automatically after 30 seconds or when answered
          </p>
          <p v-else>
            Use the buttons below to navigate between questions
          </p>
        </div>
        
        <!-- Manual Navigation (when auto-advance is disabled) -->
        <div v-if="!autoAdvanceEnabled" class="manual-navigation">
          <button 
            @click="previousQuestion" 
            class="btn-nav"
            :disabled="currentQuestionIndex === 0"
          >
            <i class="fas fa-chevron-left"></i> Previous
          </button>
          
          <button 
            v-if="currentQuestionIndex < questions.length - 1"
            @click="nextQuestion" 
            class="btn-nav"
          >
            Next <i class="fas fa-chevron-right"></i>
          </button>
          
          <button 
            v-else
            @click="showSubmitConfirmation" 
            class="btn-submit"
            :disabled="answeredCount === 0"
          >
            Submit Quiz
          </button>
        </div>
      </div>
    </div>

    <!-- Submit Confirmation Modal -->
    <div v-if="showConfirmModal" class="modal-overlay" @click="closeConfirmModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Confirm Quiz Submission</h3>
          <button @click="closeConfirmModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to submit your quiz?</p>
          <div class="submission-summary">
            <div class="summary-item">
              <span class="label">Total Questions:</span>
              <span class="value">{{ questions.length }}</span>
            </div>
            <div class="summary-item">
              <span class="label">Answered:</span>
              <span class="value">{{ answeredCount }}</span>
            </div>
            <div class="summary-item">
              <span class="label">Unanswered:</span>
              <span class="value">{{ questions.length - answeredCount }}</span>
            </div>
          </div>
          <p v-if="answeredCount < questions.length" class="warning-text">
            <i class="fas fa-exclamation-triangle"></i>
            You have {{ questions.length - answeredCount }} unanswered questions.
          </p>
        </div>
        <div class="modal-actions">
          <button @click="closeConfirmModal" class="btn-cancel">Cancel</button>
          <button @click="confirmSubmit" class="btn-confirm">Submit Quiz</button>
        </div>
      </div>
    </div>

    <!-- Expiry Warning Modal -->
    <div v-if="showExpiryModal" class="modal-overlay">
      <div class="modal-content expiry-modal">
        <div class="modal-header">
          <h3>Quiz Expiring Soon!</h3>
        </div>
        <div class="modal-body">
          <p>This quiz will expire in {{ timeUntilExpiryFormatted }}.</p>
          <p>Please submit your answers soon to avoid losing your progress.</p>
        </div>
        <div class="modal-actions">
          <button @click="closeExpiryModal" class="btn-primary">I Understand</button>
          <button @click="showSubmitConfirmation" class="btn-submit">Submit Now</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuizTaking',
  data() {
    return {
      // Quiz identification
      quizId: null,
      
      // Quiz data
      quizDetails: {
        title: '',
        duration: 0,
        totalQuestions: 0,
        chapterName: '',
        subjectName: ''
      },
      questions: [],
      currentQuestionIndex: 0,
      selectedAnswers: {},
      
      // State management
      loading: true,
      error: null,
      quizCompleted: false,
      questionAnswered: false,
      
      // Results
      finalScore: 0,
      correctAnswersCount: 0,
      totalQuestions: 0,
      
      // Timers
      questionTimeLeft: 30,
      questionTimer: null,
      
      // Auto-expiry monitoring
      quizExpiryTime: null,
      expiryCheckInterval: null,
      timeUntilExpiry: null,
      showExpiryWarning: false,
      showExpiryModal: false,
      autoExpireEnabled: false,
      
      // UI controls
      showConfirmModal: false,
      showInstantFeedback: true,
      autoAdvanceEnabled: true,
      
      // Debug
      showDebug: false,
      debugInfo: {
        responseReceived: false,
        apiCalled: false
      }
    }
  },

  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || null
    },
    
    progressPercentage() {
      if (this.questions.length === 0) return 0
      return ((this.currentQuestionIndex + 1) / this.questions.length) * 100
    },
    
    answeredCount() {
      return Object.keys(this.selectedAnswers).length
    },
    
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
    }
  },

  async created() {
    this.quizId = this.$route.params.quizId
    console.log('QuizTaking component created with quizId:', this.quizId)
    
    // Enable debug mode in development
    this.showDebug = process.env.NODE_ENV === 'development'
    
    await this.loadQuiz()
  },

  beforeDestroy() {
    this.clearAllTimers()
  },

  methods: {
    async loadQuiz() {
      console.log('🚀 Starting to load quiz...')
      
      try {
        this.loading = true
        this.error = null
        this.debugInfo.apiCalled = true

        const token = localStorage.getItem('access_token')
        if (!token) {
          console.error('No access token found')
          this.$router.push('/login')
          return
        }

        console.log('Making API call to:', `http://localhost:5000/api/user/quiz/${this.quizId}/take`)
        
        const response = await fetch(`http://localhost:5000/api/user/quiz/${this.quizId}/take`, {
          method: 'GET',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        console.log('API Response status:', response.status)
        console.log('API Response ok:', response.ok)
        
        this.debugInfo.responseReceived = true
        
        if (response.ok) {
          const data = await response.json()
          console.log('✅ Quiz data received:', data)
          
          // Set quiz details
          this.quizDetails = {
            title: data.title || 'Untitled Quiz',
            duration: data.duration || data.time_duration || 30,
            totalQuestions: data.total_questions || 0,
            chapterName: data.chapter_name || '',
            subjectName: data.subject_name || ''
          }
          
          // Set questions
          this.questions = data.questions || []
          this.totalQuestions = this.questions.length
          
          console.log('Questions loaded:', this.questions.length)
          
          if (this.questions.length === 0) {
            throw new Error('No questions available for this quiz')
          }
          
          // Set up auto-expiry monitoring
          this.autoExpireEnabled = data.auto_expire_enabled || false
          this.timeUntilExpiry = data.time_remaining_until_expiry
          this.showInstantFeedback = data.show_results_immediately !== false
          
          if (data.quiz_expires_at) {
            this.quizExpiryTime = new Date(data.quiz_expires_at)
            this.startExpiryMonitoring()
          }
          
          // Start the question timer
          this.startQuestionTimer()
          
          console.log('✅ Quiz loading completed successfully')
          
        } else {
          // Handle API errors
          const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
          console.error('❌ API Error:', errorData)
          
          let errorMessage = errorData.error || 'Failed to load quiz'
          
          if (response.status === 403) {
            if (errorData.quiz_status === 'expired') {
              errorMessage = 'This quiz has expired and is no longer available.'
            } else if (errorData.quiz_status === 'upcoming') {
              errorMessage = 'This quiz has not started yet. Please try again later.'
            }
          } else if (response.status === 404) {
            errorMessage = 'Quiz not found. It may have been deleted.'
          }
          
          this.error = errorMessage
          
          setTimeout(() => {
            this.$router.push('/dashboard')
          }, 3000)
        }

      } catch (networkError) {
        console.error('❌ Network Error:', networkError)
        this.error = 'Unable to connect to the server. Please check your internet connection.'
        
        setTimeout(() => {
          this.$router.push('/dashboard')
        }, 3000)
        
      } finally {
        this.loading = false
        console.log('Loading state set to false')
      }
    },

    startQuestionTimer() {
      this.questionTimeLeft = 30
      this.questionAnswered = false
      
      if (this.questionTimer) {
        clearInterval(this.questionTimer)
      }
      
      this.questionTimer = setInterval(() => {
        if (this.questionTimeLeft > 0) {
          this.questionTimeLeft--
        } else {
          this.handleTimeUp()
        }
      }, 1000)
    },

    handleTimeUp() {
      console.log('⏰ Time up for question', this.currentQuestionIndex + 1)
      this.moveToNextQuestionOrSubmit()
    },

    handleAnswerSelect() {
      console.log('Answer selected:', this.selectedAnswers[this.currentQuestion.id])
      this.questionAnswered = true
      
      if (this.autoAdvanceEnabled) {
        // Wait 1.5 seconds before moving to next question
        setTimeout(() => {
          this.moveToNextQuestionOrSubmit()
        }, 1500)
      }
    },

    moveToNextQuestionOrSubmit() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.nextQuestion()
      } else {
        // Last question - show submit confirmation
        this.clearAllTimers()
        this.showSubmitConfirmation()
      }
    },

    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++
        this.startQuestionTimer()
      }
    },

    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
        this.startQuestionTimer()
      }
    },

    goToQuestion(index) {
      if (index >= 0 && index < this.questions.length) {
        this.currentQuestionIndex = index
        this.startQuestionTimer()
      }
    },

    showSubmitConfirmation() {
      this.showConfirmModal = true
      // Pause the timer while showing confirmation
      if (this.questionTimer) {
        clearInterval(this.questionTimer)
      }
    },

    closeConfirmModal() {
      this.showConfirmModal = false
      // Resume timer if not on last question
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.startQuestionTimer()
      }
    },

    async confirmSubmit() {
      this.closeConfirmModal()
      await this.submitQuiz()
    },

    async submitQuiz() {
      try {
        console.log('🚀 Submitting quiz...')
        this.clearAllTimers()
        
        const token = localStorage.getItem('access_token')
        const totalTimeSpent = this.questions.length * 30 // Approximate
        
        // Format answers (convert 1-based to 0-based indexing)
        const formattedAnswers = {}
        Object.keys(this.selectedAnswers).forEach(questionId => {
          formattedAnswers[questionId] = this.selectedAnswers[questionId] - 1
        })
        
        console.log('Submitting answers:', formattedAnswers)
        
        const response = await fetch(`http://localhost:5000/api/user/quiz/${this.quizId}/submit`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            answers: formattedAnswers,
            time_taken: totalTimeSpent
          })
        })
        
        if (response.ok) {
          const data = await response.json()
          console.log('✅ Quiz submitted successfully:', data)
          
          
          this.finalScore = (data.score && data.score.percentage_score) || 0
          this.correctAnswersCount = (data.score && data.score.correct_answers) || 0
          this.quizCompleted = true
          
          if (data.warning) {
            setTimeout(() => {
              alert(`Note: ${data.warning}`)
            }, 1000)
          }
          
        } else {
          const errorData = await response.json().catch(() => ({ error: 'Submission failed' }))
          console.error('❌ Submit error:', errorData)
          
          if (errorData.error && errorData.error.includes('expired')) {
            alert('Quiz expired before submission could be completed.')
            this.$router.push('/dashboard')
          } else {
            alert('Error submitting quiz: ' + (errorData.error || 'Unknown error'))
          }
        }
        
      } catch (error) {
        console.error('❌ Submit network error:', error)
        alert('Network error submitting quiz. Please try again.')
      }
    },

    startExpiryMonitoring() {
      if (!this.autoExpireEnabled || !this.quizExpiryTime) return

      console.log('🕐 Starting expiry monitoring. Quiz expires at:', this.quizExpiryTime)
      
      this.expiryCheckInterval = setInterval(() => {
        this.checkQuizExpiry()
      }, 30000) // Check every 30 seconds
      
      this.checkQuizExpiry() // Check immediately
    },

    checkQuizExpiry() {
      if (!this.autoExpireEnabled || !this.quizExpiryTime) return

      const now = new Date()
      const timeDiff = this.quizExpiryTime.getTime() - now.getTime()
      this.timeUntilExpiry = Math.max(0, Math.floor(timeDiff / (1000 * 60))) // minutes
      
      if (this.timeUntilExpiry <= 0) {
        console.log('⏰ Quiz has expired!')
        this.handleQuizExpired()
      } else if (this.timeUntilExpiry <= 5 && !this.showExpiryWarning) {
        this.showExpiryWarning = true
        this.showExpiryModal = true
      }
    },

    handleQuizExpired() {
      this.clearAllTimers()
      alert('This quiz has expired and will be automatically submitted.')
      
      if (Object.keys(this.selectedAnswers).length > 0) {
        this.submitQuiz()
      } else {
        this.$router.push('/dashboard')
      }
    },

    closeExpiryModal() {
      this.showExpiryModal = false
    },

    clearAllTimers() {
      if (this.questionTimer) {
        clearInterval(this.questionTimer)
        this.questionTimer = null
      }
      if (this.expiryCheckInterval) {
        clearInterval(this.expiryCheckInterval)
        this.expiryCheckInterval = null
      }
    },

    goToDashboard() {
      this.clearAllTimers()
      this.$router.push('/dashboard')
    },

    viewResults() {
      this.$router.push(`/quiz/${this.quizId}/results`)
    }
  }
}
</script>

<style scoped>
.quiz-taking {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  color: white;
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-left: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.debug-info {
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 0.9rem;
}

/* Error State */
.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.error-card {
  background: white;
  padding: 3rem;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  max-width: 500px;
}

.error-card i {
  font-size: 3rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

.error-card h2 {
  color: #333;
  margin-bottom: 1rem;
}

.error-card p {
  color: #666;
  margin-bottom: 2rem;
}

/* Quiz Header */
.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.quiz-info h1 {
  color: white;
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
}

.quiz-info p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0.25rem 0;
}

.timer-section {
  text-align: center;
}

.expiry-warning {
  background: rgba(255, 193, 7, 0.9);
  color: #856404;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  margin-bottom: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  animation: pulse 2s infinite;
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

/* Progress Bar */
.progress-bar {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  height: 50px;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745, #20c997);
  border-radius: 25px;
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.score-preview {
  opacity: 0.8;
  font-size: 0.9em;
}

/* Question Container */
.question-container {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.question-header h2 {
  color: #333;
  margin: 0 0 1.5rem 0;
}

.question-text {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 2rem;
  line-height: 1.6;
}

/* Options */
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
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8f9fa;
  position: relative;
}

.option-item:hover:not(.disabled) {
  border-color: #667eea;
  background: #f0f4ff;
  transform: translateY(-2px);
}

.option-item.selected {
  border-color: #667eea;
  background: #e3f2fd;
}

.option-item.disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.option-item input[type="radio"] {
  margin-right: 1rem;
  transform: scale(1.2);
}

.option-letter {
  font-weight: bold;
  color: #667eea;
  margin-right: 0.5rem;
  min-width: 20px;
}

.option-text {
  flex: 1;
  font-size: 1.1rem;
}

.selected-icon {
  color: #28a745;
  font-size: 1.2rem;
}

/* Feedback Panel */
.feedback-panel {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 10px;
  color: #155724;
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

.feedback-message {
  margin: 0;
  font-weight: 600;
}

/* Navigation */
.navigation-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
}

.question-indicators {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 1.5rem;
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.indicator-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.indicator-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.indicator-btn.answered {
  background: #28a745;
  border-color: #28a745;
}

.indicator-btn.current {
  background: #667eea;
  border-color: #667eea;
  transform: scale(1.2);
}

.progress-info {
  text-align: center;
  margin-bottom: 1.5rem;
}

.progress-info p {
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.manual-navigation {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
}

/* Buttons */
.btn-nav, .btn-submit, .btn-primary, .btn-secondary, .btn-cancel, .btn-confirm {
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
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
  font-size: 1.1rem;
  padding: 1rem 2rem;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.btn-submit:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-2px);
}

.btn-cancel {
  background: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background: #5a6268;
}

.btn-confirm {
  background: #28a745;
  color: white;
}

.btn-confirm:hover {
  background: #218838;
}

/* Quiz Completion */
.quiz-completed {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
}

.completion-card {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  max-width: 500px;
  width: 100%;
}

.completion-icon {
  font-size: 4rem;
  color: #28a745;
  margin-bottom: 1rem;
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
}

/* Modals */
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
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  margin-bottom: 2rem;
}

.modal-body p {
  color: #666;
  margin-bottom: 1rem;
}

.submission-summary {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 10px;
  margin: 1rem 0;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: #333;
}

.value {
  color: #667eea;
  font-weight: 600;
}

.warning-text {
  color: #dc3545;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.expiry-modal {
  border: 3px solid #ffc107;
}

.expiry-modal .modal-header {
  color: #856404;
}

/* Responsive Design */
@media (max-width: 768px) {
  .quiz-taking {
    padding: 0.5rem;
  }
  
  .quiz-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
    padding: 1rem;
  }
  
  .quiz-info h1 {
    font-size: 1.5rem;
  }
  
  .question-container {
    padding: 1.5rem;
  }
  
  .question-text {
    font-size: 1.1rem;
  }
  
  .option-item {
    padding: 0.75rem;
  }
  
  .option-text {
    font-size: 1rem;
  }
  
  .manual-navigation {
    flex-direction: column;
    gap: 1rem;
  }
  
  .completion-actions {
    flex-direction: column;
  }
  
  .modal-content {
    margin: 1rem;
    padding: 1.5rem;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .question-indicators {
    gap: 0.3rem;
  }
  
  .indicator-btn {
    width: 35px;
    height: 35px;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .quiz-info h1 {
    font-size: 1.3rem;
  }
  
  .completion-card {
    padding: 2rem;
  }
  
  .score-display h3 {
    font-size: 2rem;
  }
  
  .timer-value {
    font-size: 1.3rem;
  }
}