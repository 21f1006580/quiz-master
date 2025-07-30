<!-- QuizList.vue - Clean Implementation -->
<template>
  <div class="quiz-list">
    <div class="header">
      <h2>Quiz Management</h2>
      <div class="header-actions">
        <select v-model="selectedChapterId" @change="loadQuizzes" class="form-control">
          <option value="">Select Chapter</option>
          <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
            {{ chapter.subject_name }} - {{ chapter.name }}
          </option>
        </select>
        <button @click="openCreateModal" class="btn btn-primary" :disabled="!selectedChapterId">
          <i class="fas fa-plus"></i> Add New Quiz
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading...
    </div>

    <!-- Quiz Table -->
    <div v-else-if="selectedChapterId" class="table-container">
      <table class="quizzes-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Start Date/Time</th>
            <th>Duration</th>
            <th>Status</th>
            <th>Questions</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quiz in quizzes" :key="quiz.id">
            <td>
              <strong>{{ quiz.title }}</strong>
              <div v-if="quiz.remarks" class="quiz-remarks">{{ quiz.remarks }}</div>
            </td>
            <td>{{ formatDate(quiz.date_of_quiz) }}</td>
            <td>{{ quiz.time_duration }} minutes</td>
            <td>
              <span :class="['status-badge', getStatusClass(quiz)]">
                {{ getStatus(quiz) }}
              </span>
            </td>
            <td>{{ quiz.question_count || 0 }}</td>
            <td class="actions">
              <button @click="editQuiz(quiz)" class="btn btn-sm btn-primary">Edit</button>
              <button @click="deleteQuiz(quiz)" class="btn btn-sm btn-danger">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="quizzes.length === 0" class="empty-state">
        <p>No quizzes found for this chapter.</p>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingQuiz ? 'Edit Quiz' : 'Create New Quiz' }}</h3>
          <button @click="closeModal" class="btn-close">&times;</button>
        </div>
        
        <form @submit.prevent="saveQuiz" class="modal-body">
          <div class="form-group">
            <label>Quiz Title *</label>
            <input v-model="form.title" type="text" class="form-control" required />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Start Date *</label>
              <input v-model="form.start_date" type="date" class="form-control" :min="today" required />
            </div>
            <div class="form-group">
              <label>Start Time *</label>
              <input v-model="form.start_time" type="time" class="form-control" required />
            </div>
          </div>

          <div class="form-group">
            <label>Duration (minutes) *</label>
            <input v-model.number="form.time_duration" type="number" class="form-control" min="1" required />
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="form.remarks" class="form-control" rows="3"></textarea>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.is_active" />
              Active (visible to students)
            </label>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingQuiz ? 'Update' : 'Create') }}
            </button>
          </div>
          <div class="form-section">
  <h4>Auto-Expiry Settings</h4>
  
  <div class="form-group">
    <label class="checkbox-label">
      <input type="checkbox" v-model="form.auto_expire" />
      <span>Enable automatic expiry</span>
    </label>
    <small class="form-help">Quiz will automatically lock when end time is reached</small>
  </div>

  <div v-if="form.auto_expire" class="expiry-settings">
    <div class="form-row">
      <div class="form-group">
        <label>End Date</label>
        <input 
          v-model="form.end_date" 
          type="date" 
          class="form-control"
          :min="form.start_date || today"
        />
        <small class="form-help">When should this quiz expire?</small>
      </div>
      
      <div class="form-group">
        <label>End Time</label>
        <input 
          v-model="form.end_time" 
          type="time" 
          class="form-control"
          :disabled="!form.end_date"
        />
        <small class="form-help">Time when quiz becomes unavailable</small>
      </div>
    </div>

    <div class="form-group">
      <label>Grace Period (minutes)</label>
      <input 
        v-model.number="form.grace_period" 
        type="number" 
        class="form-control"
        min="0" 
        max="60"
        placeholder="0"
      />
      <small class="form-help">Extra time after end time for ongoing attempts (0-60 minutes)</small>
    </div>

    <!-- Expiry Preview -->
    <div v-if="form.end_date && form.end_time" class="expiry-preview">
      <h5>Expiry Schedule</h5>
      <div class="preview-items">
        <div class="preview-item">
          <i class="fas fa-calendar-alt"></i>
          <span>Expires: {{ formatDateTime(form.end_date, form.end_time) }}</span>
        </div>
        <div v-if="form.grace_period > 0" class="preview-item">
          <i class="fas fa-clock"></i>
          <span>Final deadline: {{ formatDateTimeWithGrace(form.end_date, form.end_time, form.grace_period) }}</span>
        </div>
        <div class="preview-item">
          <i class="fas fa-info-circle"></i>
          <span class="expiry-status">{{ getExpiryStatus(form.end_date, form.end_time) }}</span>
        </div>
      </div>
    </div>
  </div>
</div>
        </form>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" :class="['alert', messageType === 'success' ? 'alert-success' : 'alert-error']">
      {{ message }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuizList',
  data() {
    return {
      chapters: [],
      quizzes: [],
      selectedChapterId: '',
      loading: false,
      saving: false,
      showModal: false,
      editingQuiz: null,
      message: '',
      messageType: 'success',
      form: {
        title: '',
        start_date: '',
        start_time: '',
        end_date: '',
        end_time: '',
        time_duration: 30,
        remarks: '',
        is_active: true,
        auto_expire: true,  // Enable by default
        grace_period: 5     // 5 minute grace period by default
      }
    }
  },
  
  computed: {
    today() {
      return new Date().toISOString().split('T')[0]
    }
  },
  
  mounted() {
    this.loadChapters()
  },
  
  methods: {
    async loadChapters() {
      try {
        const token = localStorage.getItem('access_token')
        const response = await fetch('/api/admin/chapters', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.ok) {
          const data = await response.json()
          this.chapters = data.chapters || []
        }
      } catch (error) {
        console.error('Error loading chapters:', error)
        this.showMessage('Error loading chapters', 'error')
      }
    },
    
    async loadQuizzes() {
      if (!this.selectedChapterId) return
      
      try {
        this.loading = true
        const token = localStorage.getItem('access_token')
        const response = await fetch(`/api/admin/chapters/${this.selectedChapterId}/quizzes`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.ok) {
          const data = await response.json()
          this.quizzes = data.quizzes || []
        }
      } catch (error) {
        console.error('Error loading quizzes:', error)
        this.showMessage('Error loading quizzes', 'error')
      } finally {
        this.loading = false
      }
    },    
    openCreateModal() {
      if (!this.selectedChapterId) {
        this.showMessage('Please select a chapter first', 'error')
        return
      }
      
      this.editingQuiz = null
      const now = new Date()
      const nextHour = new Date(now.getTime() + 60 * 60 * 1000)
      
      this.form = {
        title: '',
        start_date: now.toISOString().split('T')[0],
        start_time: nextHour.toTimeString().slice(0, 5),
        time_duration: 30,
        remarks: '',
        is_active: true
      }
      this.showModal = true
    },
    
    editQuiz(quiz) {
      this.editingQuiz = quiz
      const startDate = new Date(quiz.date_of_quiz)
      
      this.form = {
        title: quiz.title,
        start_date: startDate.toISOString().split('T')[0],
        start_time: startDate.toTimeString().slice(0, 5),
        time_duration: quiz.time_duration,
        remarks: quiz.remarks || '',
        is_active: quiz.is_active !== false
      }
      this.showModal = true
    },
    
    closeModal() {
      this.showModal = false
      this.editingQuiz = null
    },
    
    async saveQuiz() {
      try {
        this.saving = true
        
        const data = {
          title: this.form.title,
          chapter_id: this.selectedChapterId,
          start_date: this.form.start_date,
          start_time: this.form.start_time,
          time_duration: this.form.time_duration,
          remarks: this.form.remarks,
          is_active: this.form.is_active
        }
        
        const token = localStorage.getItem('access_token')
        let response
        
        if (this.editingQuiz) {
          response = await fetch(`/api/admin/quizzes/${this.editingQuiz.id}`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
          })
        } else {
          response = await fetch('/api/admin/quizzes', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
          })
        }
        
        if (response.ok) {
          const result = await response.json()
          this.showMessage(result.message, 'success')
          this.closeModal()
          this.loadQuizzes()
        } else {
          const error = await response.json()
          this.showMessage(error.error || 'Error saving quiz', 'error')
        }
        
      } catch (error) {
        console.error('Error saving quiz:', error)
        this.showMessage('Error saving quiz', 'error')
      } finally {
        this.saving = false
      }
    },
    
    async deleteQuiz(quiz) {
      if (!confirm(`Delete "${quiz.title}"?`)) return
      
      try {
        const token = localStorage.getItem('access_token')
        const response = await fetch(`/api/admin/quizzes/${quiz.id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.ok) {
          this.showMessage('Quiz deleted successfully', 'success')
          this.loadQuizzes()
        }
      } catch (error) {
        console.error('Error deleting quiz:', error)
        this.showMessage('Error deleting quiz', 'error')
      }
    },
    
    getStatus(quiz) {
      const now = new Date()
      const startDate = new Date(quiz.date_of_quiz)
      
      if (!quiz.is_active) return 'Inactive'
      if (now < startDate) return 'Upcoming'
      if (quiz.end_date_time && now > new Date(quiz.end_date_time)) return 'Expired'
      return 'Active'
    },
    
    getStatusClass(quiz) {
      const status = this.getStatus(quiz)
      return status.toLowerCase()
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    },
    
    showMessage(message, type = 'success') {
      this.message = message
      this.messageType = type
      setTimeout(() => { this.message = '' }, 5000)
    },

    async saveQuiz() {
      try {
        this.saving = true
        
        // Enhanced validation for auto-expiry
        if (this.form.auto_expire) {
          if (!this.form.end_date || !this.form.end_time) {
            this.showMessage('End date and time are required when auto-expiry is enabled', 'error')
            return
          }
          
          const startDateTime = new Date(`${this.form.start_date}T${this.form.start_time}`)
          const endDateTime = new Date(`${this.form.end_date}T${this.form.end_time}`)
          
          if (endDateTime <= startDateTime) {
            this.showMessage('End time must be after start time', 'error')
            return
          }
          
          // Minimum quiz duration check
          const durationHours = (endDateTime - startDateTime) / (1000 * 60 * 60)
          if (durationHours < 0.5) {
            this.showMessage('Quiz must be available for at least 30 minutes', 'error')
            return
          }
        }
        
        const data = {
          title: this.form.title,
          chapter_id: this.selectedChapterId,
          start_date: this.form.start_date,
          start_time: this.form.start_time,
          end_date: this.form.auto_expire ? this.form.end_date : null,
          end_time: this.form.auto_expire ? this.form.end_time : null,
          time_duration: this.form.time_duration,
          remarks: this.form.remarks,
          is_active: this.form.is_active,
          auto_expire: this.form.auto_expire,
          grace_period: this.form.auto_expire ? this.form.grace_period : 0
        }
        
        // ... rest of save logic
        
      } catch (error) {
        // ... error handling
      } finally {
        this.saving = false
      }
    },

    formatDateTime(date, time) {
      if (!date || !time) return 'Not set'
      const dateTime = new Date(`${date}T${time}`)
      return dateTime.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    formatDateTimeWithGrace(date, time, graceMinutes) {
      if (!date || !time || !graceMinutes) return this.formatDateTime(date, time)
      const dateTime = new Date(`${date}T${time}`)
      const withGrace = new Date(dateTime.getTime() + graceMinutes * 60 * 1000)
      return withGrace.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    getExpiryStatus(date, time) {
      if (!date || !time) return ''
      const endDateTime = new Date(`${date}T${time}`)
      const now = new Date()
      
      if (endDateTime < now) {
        return 'Would be expired'
      } else {
        const hoursUntil = Math.round((endDateTime - now) / (1000 * 60 * 60))
        return `Will expire in ${hoursUntil} hours`
      }
    },

    // Add method to check quiz status in real-time
    getStatus(quiz) {
      const now = new Date()
      const startDate = new Date(quiz.date_of_quiz)
      
      if (!quiz.is_active) return 'Inactive'
      if (now < startDate) return 'Upcoming'
      
      // Check auto-expiry
      if (quiz.auto_expire && quiz.end_date_time) {
        const endDate = new Date(quiz.end_date_time)
        const graceEnd = quiz.grace_period ? 
          new Date(endDate.getTime() + quiz.grace_period * 60 * 1000) : endDate
        
        if (now > graceEnd) return 'Expired'
        if (now > endDate) return 'Grace Period'
        
        // Check if ending soon (within 30 minutes)
        const minutesUntilEnd = (endDate - now) / (1000 * 60)
        if (minutesUntilEnd <= 30 && minutesUntilEnd > 0) return 'Ending Soon'
      }
      
      return 'Active'
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
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.form-control {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-danger { background: #dc3545; color: white; }
.btn-sm { padding: 4px 8px; font-size: 12px; }

.btn:hover { opacity: 0.9; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }

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
}

.quiz-remarks {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active { background: #d4edda; color: #155724; }
.status-badge.upcoming { background: #fff3cd; color: #856404; }
.status-badge.expired { background: #f8d7da; color: #721c24; }
.status-badge.inactive { background: #e9ecef; color: #6c757d; }

.actions {
  display: flex;
  gap: 8px;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
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

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.loading, .empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.alert {
  position: fixed;
  top: 20px; right: 20px;
  padding: 12px 16px;
  border-radius: 4px;
  color: white;
  z-index: 1001;
}

.alert-success { background: #28a745; }
.alert-error { background: #dc3545; }

@media (max-width: 768px) {
  .header { flex-direction: column; gap: 16px; }
  .header-actions { flex-direction: column; width: 100%; }
  .form-row { flex-direction: column; }
  .actions { flex-direction: column; }
}


.expiry-settings {
  background: #fff8f0;
  border: 1px solid #ffd09b;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

.expiry-preview {
  background: #f0f8ff;
  border: 1px solid #b3d9ff;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

.expiry-preview h5 {
  margin: 0 0 0.75rem 0;
  color: #0066cc;
  font-size: 0.9rem;
}

.preview-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.preview-item i {
  width: 16px;
  color: #666;
}

.expiry-status {
  font-weight: 500;
  color: #333;
}

/* Enhanced status badges */
.status-badge.ending-soon {
  background: #ff9800;
  color: white;
  animation: blink 2s infinite;
}

.status-badge.grace-period {
  background: #ff5722;
  color: white;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.7; }
}

.form-help {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6c757d;
  font-style: italic;
}
</style>