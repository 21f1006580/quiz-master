<template>
  <div class="subject-quizzes">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <button @click="$router.go(-1)" class="btn-back">
          <i class="fas fa-arrow-left"></i>
          Back to Dashboard
        </button>
        <div class="subject-info" v-if="subject">
          <h1>{{ subject.name }}</h1>
          <p v-if="subject.description">{{ subject.description }}</p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading quizzes...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      <h3>Something went wrong</h3>
      <p>{{ error }}</p>
      <button @click="loadQuizzes" class="btn btn-primary">Try Again</button>
    </div>

    <!-- Main Content -->
    <div v-else class="content-container">
      <!-- Stats Section -->
      <div class="stats-section" v-if="quizzes.length > 0">
        <div class="stat-card">
          <h3>{{ totalQuizzes }}</h3>
          <p>Total Quizzes</p>
        </div>
        <div class="stat-card">
          <h3>{{ attemptedQuizzes }}</h3>
          <p>Attempted</p>
        </div>
        <div class="stat-card">
          <h3>{{ availableQuizzes }}</h3>
          <p>Available</p>
        </div>
        <div class="stat-card">
          <h3>{{ averageScore }}%</h3>
          <p>Average Score</p>
        </div>
      </div>

      <!-- Filter Section -->
      <div class="filter-section" v-if="quizzes.length > 0">
        <div class="filter-controls">
          <div class="filter-group">
            <label>Filter by Status:</label>
            <select v-model="statusFilter" class="form-control">
              <option value="all">All Quizzes</option>
              <option value="available">Available</option>
              <option value="attempted">Attempted</option>
              <option value="pending">Not Attempted</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Sort by:</label>
            <select v-model="sortBy" class="form-control">
              <option value="date_asc">Date (Oldest First)</option>
              <option value="date_desc">Date (Newest First)</option>
              <option value="chapter">Chapter</option>
              <option value="score">Score (High to Low)</option>
            </select>
          </div>
        </div>
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search quizzes..."
            class="form-control"
          />
          <i class="fas fa-search search-icon"></i>
        </div>
      </div>

      <!-- Quizzes Grid -->
      <div v-if="filteredQuizzes.length > 0" class="quizzes-grid">
        <div
          v-for="quiz in filteredQuizzes"
          :key="quiz.quiz_id"
          class="quiz-card"
          :class="{
            'attempted': quiz.attempted,
            'available': !quiz.attempted && isQuizAvailable(quiz),
            'upcoming': !isQuizAvailable(quiz)
          }"
        >
          <div class="quiz-header">
            <h3>{{ quiz.title }}</h3>
            <div class="quiz-status">
              <span v-if="quiz.attempted" class="status-badge attempted">
                <i class="fas fa-check"></i>
                Completed
              </span>
              <span v-else-if="isQuizAvailable(quiz)" class="status-badge available">
                <i class="fas fa-play"></i>
                Available
              </span>
              <span v-else class="status-badge upcoming">
                <i class="fas fa-clock"></i>
                Upcoming
              </span>
            </div>
          </div>

          <div class="quiz-details">
            <div class="detail-row">
              <i class="fas fa-book-open"></i>
              <span>{{ quiz.chapter_name }}</span>
            </div>
            <div class="detail-row">
              <i class="fas fa-calendar"></i>
              <span>{{ formatDate(quiz.date_of_quiz) }}</span>
            </div>
            <div class="detail-row">
              <i class="fas fa-clock"></i>
              <span>{{ quiz.time_duration }} minutes</span>
            </div>
            <div class="detail-row">
              <i class="fas fa-question-circle"></i>
              <span>{{ quiz.question_count }} questions</span>
            </div>
          </div>

          <div v-if="quiz.remarks" class="quiz-remarks">
            <p>{{ quiz.remarks }}</p>
          </div>

          <!-- Quiz Score (if attempted) -->
          <div v-if="quiz.attempted" class="quiz-score">
            <div class="score-display" :class="getScoreClass(quiz.user_score)">
              <span class="score-value">{{ quiz.user_score }}%</span>
              <span class="score-label">Your Score</span>
            </div>
            <div class="attempt-info">
              <small>Attempted on {{ formatDate(quiz.attempt_date) }}</small>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="quiz-actions">
            <button
              v-if="!quiz.attempted && isQuizAvailable(quiz)"
              @click="startQuiz(quiz.quiz_id)"
              class="btn btn-primary btn-full"
            >
              <i class="fas fa-play"></i>
              Start Quiz
            </button>
            
            <button
              v-else-if="quiz.attempted"
              @click="viewResults(quiz.quiz_id)"
              class="btn btn-secondary btn-full"
            >
              <i class="fas fa-chart-line"></i>
              View Results
            </button>
            
            <button
              v-else
              disabled
              class="btn btn-disabled btn-full"
            >
              <i class="fas fa-lock"></i>
              Not Available Yet
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="quizzes.length === 0" class="empty-state">
        <i class="fas fa-clipboard-list fa-3x"></i>
        <h3>No Quizzes Available</h3>
        <p>There are currently no quizzes available for this subject.</p>
        <button @click="$router.push('/user/dashboard')" class="btn btn-primary">
          <i class="fas fa-arrow-left"></i>
          Back to Dashboard
        </button>
      </div>

      <!-- No Results State -->
      <div v-else class="empty-state">
        <i class="fas fa-search fa-3x"></i>
        <h3>No Quizzes Found</h3>
        <p>No quizzes match your current filters.</p>
        <button @click="clearFilters" class="btn btn-secondary">
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" :class="['alert', messageType === 'success' ? 'alert-success' : 'alert-error']">
      {{ message }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'SubjectQuizzes',
  data() {
    return {
      subject: null,
      quizzes: [],
      loading: true,
      error: null,
      message: '',
      messageType: 'success',
      statusFilter: 'all',
      sortBy: 'date_asc',
      searchQuery: ''
    }
  },

  computed: {
    subjectId() {
      return this.$route.params.subjectId
    },

    totalQuizzes() {
      return this.quizzes.length
    },

    attemptedQuizzes() {
      return this.quizzes.filter(quiz => quiz.attempted).length
    },

    availableQuizzes() {
      return this.quizzes.filter(quiz => !quiz.attempted && this.isQuizAvailable(quiz)).length
    },

    averageScore() {
      const attemptedQuizzes = this.quizzes.filter(quiz => quiz.attempted)
      if (attemptedQuizzes.length === 0) return 0
      const totalScore = attemptedQuizzes.reduce((sum, quiz) => sum + (quiz.user_score || 0), 0)
      return Math.round(totalScore / attemptedQuizzes.length)
    },

    filteredQuizzes() {
      let filtered = [...this.quizzes]

      // Apply status filter
      if (this.statusFilter !== 'all') {
        filtered = filtered.filter(quiz => {
          switch (this.statusFilter) {
            case 'available':
              return !quiz.attempted && this.isQuizAvailable(quiz)
            case 'attempted':
              return quiz.attempted
            case 'pending':
              return !quiz.attempted
            default:
              return true
          }
        })
      }

      // Apply search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(quiz =>
          quiz.title.toLowerCase().includes(query) ||
          quiz.chapter_name.toLowerCase().includes(query) ||
          (quiz.remarks && quiz.remarks.toLowerCase().includes(query))
        )
      }

      // Apply sorting
      filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'date_desc':
            return new Date(b.date_of_quiz) - new Date(a.date_of_quiz)
          case 'date_asc':
            return new Date(a.date_of_quiz) - new Date(b.date_of_quiz)
          case 'chapter':
            return a.chapter_name.localeCompare(b.chapter_name)
          case 'score':
            return (b.user_score || 0) - (a.user_score || 0)
          default:
            return 0
        }
      })

      return filtered
    }
  },

  async created() {
    await this.loadQuizzes()
  },

  methods: {
    async loadQuizzes() {
      try {
        console.log("Initializing quiz loading for subject:", this.subjectId)
        this.loading = true
        this.error = null

        const token = localStorage.getItem('access_token')
        if (!token) {
          this.$router.push('/login')
          return
        }

        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }

        console.log('Loading quizzes for subject:', this.subjectId)

        const response = await this.$api.get(`/user/subjects/${this.subjectId}/quizzes`)

        console.log('Response status:', response.status)

        if (response.status === 200) {
          const data = response.data
          console.log('Quizzes data:', data)
          
          this.subject = data.subject
          this.quizzes = data.quizzes || []
        } else {
          this.error = response.data?.error || 'Failed to load quizzes'
        }

      } catch (error) {
        console.error('Error loading quizzes:', error)
        this.error = error.message || 'Failed to load quizzes'
      } finally {
        this.loading = false
      }
    },

    isQuizAvailable(quiz) {
      if (!quiz.date_of_quiz) return false
      const quizDate = new Date(quiz.date_of_quiz)
      const now = new Date()
      return quizDate <= now
    },

    startQuiz(quizId) {
      this.$router.push(`/user/quiz/${quizId}/take`)
    },

    viewResults(quizId) {
      this.$router.push(`/user/quiz/${quizId}/results`)
    },

    clearFilters() {
      this.statusFilter = 'all'
      this.sortBy = 'date_asc'
      this.searchQuery = ''
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

    getScoreClass(score) {
      if (score >= 90) return 'excellent'
      if (score >= 75) return 'good'
      if (score >= 60) return 'average'
      return 'needs-improvement'
    },

    showMessage(message, type = 'success') {
      this.message = message
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 5000)
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

.page-header {
  margin-bottom: 2rem;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.btn-back {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  margin-bottom: 1.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.subject-info h1 {
  color: white;
  font-size: 2.5rem;
  margin: 0 0 0.5rem 0;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.subject-info p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  margin: 0;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
}

.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  margin-bottom: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.stats-section {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  justify-content: center;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1.5rem;
  text-align: center;
  min-width: 120px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-card h3 {
  color: white;
  font-size: 1.8rem;
  margin: 0 0 0.5rem 0;
}

.stat-card p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 0.9rem;
}

.filter-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 2rem;
}

.filter-controls {
  display: flex;
  gap: 1.5rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #333;
  font-size: 0.9rem;
}

.search-box {
  position: relative;
  min-width: 250px;
}

.search-box input {
  padding-left: 2.5rem;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
}

.form-control {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
  min-width: 150px;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.25);
}

.quizzes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.quiz-card {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  border-left: 4px solid #e9ecef;
}

.quiz-card.available {
  border-left-color: #28a745;
}

.quiz-card.attempted {
  border-left-color: #667eea;
}

.quiz-card.upcoming {
  border-left-color: #ffc107;
}

.quiz-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.quiz-header h3 {
  color: #333;
  margin: 0;
  font-size: 1.2rem;
  flex: 1;
  line-height: 1.3;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.status-badge.available {
  background: #d4edda;
  color: #155724;
}

.status-badge.attempted {
  background: #cce5ff;
  color: #004085;
}

.status-badge.upcoming {
  background: #fff3cd;
  color: #856404;
}

.quiz-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.detail-row i {
  color: #667eea;
  width: 16px;
}

.quiz-remarks {
  background: #f8f9fa;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.quiz-remarks p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  font-style: italic;
}

.quiz-score {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 1rem;
}

.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  border-radius: 8px;
}

.score-display.excellent {
  background: #d4edda;
  color: #155724;
}

.score-display.good {
  background: #d1ecf1;
  color: #0c5460;
}

.score-display.average {
  background: #fff3cd;
  color: #856404;
}

.score-display.needs-improvement {
  background: #f8d7da;
  color: #721c24;
}

.score-value {
  font-size: 1.2rem;
  font-weight: 700;
}

.score-label {
  font-size: 0.7rem;
  opacity: 0.8;
}

.attempt-info {
  display: flex;
  flex-direction: column;
  align-items: end;
  color: #666;
}

.quiz-actions {
  margin-top: auto;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.btn-full {
  width: 100%;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5a6fd8;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-disabled {
  background: #e9ecef;
  color: #6c757d;
  cursor: not-allowed;
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
  .subject-quizzes {
    padding: 1rem;
  }

  .subject-info h1 {
    font-size: 2rem;
  }

  .stats-section {
    flex-wrap: wrap;
    justify-content: center;
  }

  .filter-section {
    flex-direction: column;
    gap: 1rem;
  }

  .filter-controls {
    flex-direction: column;
    gap: 1rem;
  }

  .search-box {
    min-width: auto;
  }

  .quizzes-grid {
    grid-template-columns: 1fr;
  }

  .quiz-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
  }

  .quiz-score {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
}
</style>