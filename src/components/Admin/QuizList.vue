<!-- QuizList.vue -->
<template>
  <div class="quiz-list">
    <div class="header">
      <h2>Quiz Management</h2>
      <div class="header-actions">
        <select v-model="selectedChapterId" @change="loadQuizzes" class="form-control chapter-select">
          <option value="">Select Chapter</option>
          <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
            {{ chapter.subject_name }} - {{ chapter.name }}
          </option>
        </select>
        <button 
          @click="openCreateModal" 
          class="btn btn-primary"
          :disabled="!selectedChapterId"
        >
          <i class="fas fa-plus"></i> Add New Quiz
        </button>
      </div>
    </div>

    <!-- Chapter Info -->
    <div v-if="selectedChapter" class="chapter-info">
      <h4>{{ selectedChapter.subject_name }} - {{ selectedChapter.name }}</h4>
      <p v-if="selectedChapter.description">{{ selectedChapter.description }}</p>
    </div>

    <!-- Search Section -->
    <div v-if="selectedChapterId" class="search-section">
      <div class="search-box">
        <input
          v-model="searchQuery"
          @input="debouncedSearch"
          type="text"
          placeholder="Search quizzes..."
          class="form-control"
        />
        <i class="fas fa-search search-icon"></i>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading quizzes...
    </div>

    <!-- Quizzes Table -->
    <div v-else-if="selectedChapterId" class="table-container">
      <table class="quizzes-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Date</th>
            <th>Duration</th>
            <th>Status</th>
            <th>Questions</th>
            <th>Remarks</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quiz in filteredQuizzes" :key="quiz.id">
            <td>{{ quiz.id }}</td>
            <td>{{ quiz.title }}</td>
            <td>{{ formatDate(quiz.date_of_quiz) }}</td>
            <td>{{ quiz.time_duration }}</td>
            <td>
              <span :class="['status-badge', quiz.is_active ? 'active' : 'inactive']">
                {{ quiz.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <span class="question-count">{{ quiz.question_count || 0 }}</span>
            </td>
            <td>{{ quiz.remarks || 'No remarks' }}</td>
            <td class="actions">
              <button
                @click="manageQuestions(quiz)"
                class="btn btn-sm btn-info"
                title="Manage Questions"
              >
                <i class="fas fa-question-circle"></i>
              </button>
              <button
                @click="editQuiz(quiz)"
                class="btn btn-sm btn-edit"
                title="Edit"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button
                @click="deleteQuiz(quiz)"
                class="btn btn-sm btn-delete"
                title="Delete"
              >
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="filteredQuizzes.length === 0 && !loading" class="empty-state">
        <i class="fas fa-clipboard-list fa-3x"></i>
        <h3>No quizzes found</h3>
        <p>{{ searchQuery ? 'No quizzes match your search.' : 'Start by creating your first quiz for this chapter.' }}</p>
      </div>
    </div>

    <!-- No Chapter Selected -->
    <div v-else class="no-selection">
      <i class="fas fa-clipboard-list fa-3x"></i>
      <h3>Select a Chapter</h3>
      <p>Choose a chapter from the dropdown to view and manage its quizzes.</p>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingQuiz ? 'Edit Quiz' : 'Create New Quiz' }}</h3>
          <button @click="closeModal" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveQuiz" class="modal-body">
          <div class="form-group">
            <label for="title">Quiz Title *</label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              class="form-control"
              :class="{ 'error': errors.title }"
              placeholder="Enter quiz title"
              required
            />
            <span v-if="errors.title" class="error-text">{{ errors.title }}</span>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="date_of_quiz">Quiz Date *</label>
              <input
                id="date_of_quiz"
                v-model="form.date_of_quiz"
                type="datetime-local"
                class="form-control"
                :class="{ 'error': errors.date_of_quiz }"
                required
              />
              <span v-if="errors.date_of_quiz" class="error-text">{{ errors.date_of_quiz }}</span>
            </div>
            
            <div class="form-group">
              <label for="time_duration">Duration (HH:MM) *</label>
              <input
                id="time_duration"
                v-model="form.time_duration"
                type="text"
                class="form-control"
                :class="{ 'error': errors.time_duration }"
                placeholder="01:30"
                pattern="^([0-9]{1,2}):([0-5][0-9])$"
                required
              />
              <span v-if="errors.time_duration" class="error-text">{{ errors.time_duration }}</span>
            </div>
          </div>
          
          <div class="form-group">
            <label for="remarks">Remarks</label>
            <textarea
              id="remarks"
              v-model="form.remarks"
              class="form-control"
              placeholder="Enter any remarks or instructions (optional)"
              rows="3"
            ></textarea>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              {{ saving ? 'Saving...' : (editingQuiz ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
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
  name: 'QuizList',
  data() {
    return {
      chapters: [],
      quizzes: [],
      selectedChapterId: '',
      selectedChapter: null,
      loading: false,
      saving: false,
      showModal: false,
      editingQuiz: null,
      searchQuery: '',
      message: '',
      messageType: 'success',
      searchTimeout: null,
      form: {
        title: '',
        date_of_quiz: '',
        time_duration: '',
        remarks: ''
      },
      errors: {}
    }
  },
  
  computed: {
    filteredQuizzes() {
      if (!this.searchQuery) return this.quizzes
      
      const query = this.searchQuery.toLowerCase()
      return this.quizzes.filter(quiz => 
        quiz.title.toLowerCase().includes(query) ||
        (quiz.remarks && quiz.remarks.toLowerCase().includes(query))
      )
    }
  },
  
  mounted() {
    this.loadChapters()
  },
  
  methods: {
    async loadChapters() {
      try {
        const response = await axios.get('/api/admin/chapters', {
          headers: this.getAuthHeaders()
        })
        this.chapters = response.data.chapters || []
      } catch (error) {
        this.showMessage('Error loading chapters: ' + this.getErrorMessage(error), 'error')
      }
    },
    
    async loadQuizzes() {
      if (!this.selectedChapterId) {
        this.quizzes = []
        this.selectedChapter = null
        return
      }
      
      try {
        this.loading = true
        const response = await axios.get(`/api/admin/chapters/${this.selectedChapterId}/quizzes`, {
          headers: this.getAuthHeaders()
        })
        
        this.quizzes = response.data.quizzes || []
        this.selectedChapter = response.data.chapter
        
      } catch (error) {
        this.showMessage('Error loading quizzes: ' + this.getErrorMessage(error), 'error')
      } finally {
        this.loading = false
      }
    },
    
    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        // Search is handled by computed property filteredQuizzes
      }, 300)
    },
    
    openCreateModal() {
      if (!this.selectedChapterId) {
        this.showMessage('Please select a chapter first', 'error')
        return
      }
      
      this.editingQuiz = null
      this.form = {
        title: '',
        date_of_quiz: '',
        time_duration: '',
        remarks: ''
      }
      this.errors = {}
      this.showModal = true
    },
    
    editQuiz(quiz) {
      this.editingQuiz = quiz
      this.form = {
        title: quiz.title,
        date_of_quiz: this.formatDateForInput(quiz.date_of_quiz),
        time_duration: quiz.time_duration,
        remarks: quiz.remarks || ''
      }
      this.errors = {}
      this.showModal = true
    },
    
    closeModal() {
      this.showModal = false
      this.editingQuiz = null
      this.form = {
        title: '',
        date_of_quiz: '',
        time_duration: '',
        remarks: ''
      }
      this.errors = {}
    },
    
    async saveQuiz() {
      try {
        this.saving = true
        this.errors = {}
        
        // Basic validation
        if (!this.form.title.trim()) {
          this.errors.title = 'Quiz title is required'
          return
        }
        
        if (!this.form.date_of_quiz) {
          this.errors.date_of_quiz = 'Quiz date is required'
          return
        }
        
        if (!this.form.time_duration) {
          this.errors.time_duration = 'Duration is required'
          return
        }
        
        // Validate time duration format
        const timePattern = /^([0-9]{1,2}):([0-5][0-9])$/
        if (!timePattern.test(this.form.time_duration)) {
          this.errors.time_duration = 'Duration must be in HH:MM format'
          return
        }
        
        const data = {
          title: this.form.title.trim(),
          chapter_id: this.selectedChapterId,
          date_of_quiz: new Date(this.form.date_of_quiz).toISOString(),
          time_duration: this.form.time_duration,
          remarks: this.form.remarks.trim()
        }
        
        let response
        if (this.editingQuiz) {
          response = await axios.put(
            `/api/admin/quizzes/${this.editingQuiz.id}`,
            data,
            { headers: this.getAuthHeaders() }
          )
        } else {
          response = await axios.post(
            '/api/admin/quizzes',
            data,
            { headers: this.getAuthHeaders() }
          )
        }
        
        this.showMessage(response.data.message, 'success')
        this.closeModal()
        this.loadQuizzes()
        
      } catch (error) {
        if (error.response && error.response.status === 400) {
          this.showMessage(error.response.data.error, 'error')
        } else {
          this.showMessage('Error saving quiz: ' + this.getErrorMessage(error), 'error')
        }
      } finally {
        this.saving = false
      }
    },
    
    async deleteQuiz(quiz) {
      if (!confirm(`Are you sure you want to delete "${quiz.title}"? This will also delete all questions associated with this quiz.`)) {
        return
      }
      
      try {
        await axios.delete(
          `/api/admin/quizzes/${quiz.id}`,
          { headers: this.getAuthHeaders() }
        )
        
        this.showMessage('Quiz deleted successfully', 'success')
        this.loadQuizzes()
        
      } catch (error) {
        this.showMessage('Error deleting quiz: ' + this.getErrorMessage(error), 'error')
      }
    },
    
    manageQuestions(quiz) {
      // Navigate to question management for this quiz
      // This would typically use Vue Router
      this.$emit('manage-questions', quiz)
      // or use this.$router.push(`/admin/quizzes/${quiz.id}/questions`)
    },
    
    getAuthHeaders() {
      const token = localStorage.getItem('access_token')
      return token ? { Authorization: `Bearer ${token}` } : {}
    },
    
    getErrorMessage(error) {
      return (error.response && error.response.data && error.response.data.error) || error.message || 'Unknown error occurred'
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
    
    formatDateForInput(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toISOString().slice(0, 16)
    }
  }
}
</script>

<style scoped>
.quiz-list {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chapter-select {
  min-width: 250px;
}

.chapter-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #007bff;
}

.chapter-info h4 {
  margin: 0 0 8px 0;
  color: #333;
}

.chapter-info p {
  margin: 0;
  color: #666;
}

.search-section {
  margin-bottom: 20px;
}

.search-box {
  position: relative;
  max-width: 400px;
}

.search-box input {
  padding-left: 40px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.quizzes-table {
  width: 100%;
  border-collapse: collapse;
}

.quizzes-table th,
.quizzes-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.quizzes-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.quizzes-table tr:hover {
  background: #f8f9fa;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.question-count {
  background: #e9ecef;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-info:hover {
  background: #138496;
}

.btn-edit {
  background: #28a745;
  color: white;
}

.btn-edit:hover {
  background: #1e7e34;
}

.btn-delete {
  background: #dc3545;
  color: white;
}

.btn-delete:hover {
  background: #c82333;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

.form-control.error {
  border-color: #dc3545;
}

.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #333;
}

.error-text {
  color: #dc3545;
  font-size: 12px;
  margin-top: 4px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 600px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  padding: 4px;
}

.btn-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.loading, .no-selection {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-state i, .no-selection i {
  color: #ddd;
  margin-bottom: 16px;
}

.empty-state h3, .no-selection h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.alert {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 16px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
  z-index: 1001;
  min-width: 300px;
}

.alert-success {
  background: #28a745;
}

.alert-error {
  background: #dc3545;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    flex-direction: column;
  }
  
  .chapter-select {
    min-width: auto;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .modal {
    width: 95vw;
  }
  
  .quizzes-table {
    font-size: 12px;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style>