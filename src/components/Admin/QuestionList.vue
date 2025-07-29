<template>
  <div class="question-management">
    <div class="header">
      <h2>Question Management</h2>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Add New Question
      </button>
    </div>

    <!-- Filters -->
    <div class="filter-section">
      <div class="filter-box">
        <select
          v-model="selectedSubjectId"
          @change="onSubjectChange"
          class="form-control"
        >
          <option value="">Select a subject</option>
          <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
            {{ subject.name }}
          </option>
        </select>
        <i class="fas fa-book filter-icon"></i>
      </div>

      <div class="filter-box" v-if="chapters.length > 0">
        <select
          v-model="selectedChapterId"
          @change="loadQuestions"
          class="form-control"
        >
          <option value="">Select a chapter to view questions</option>
          <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
            {{ chapter.name }}
          </option>
        </select>
        <i class="fas fa-book-open filter-icon"></i>
      </div>
      
      <!-- Search Box -->
      <div class="search-box" v-if="selectedChapterId">
        <input
          v-model="searchQuery"
          @input="filterQuestions"
          type="text"
          placeholder="Search questions..."
          class="form-control"
        />
        <i class="fas fa-search search-icon"></i>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading questions...
    </div>

    <!-- Selected Chapter Info -->
    <div v-else-if="selectedChapter" class="chapter-info">
      <h3>{{ selectedChapter.name }}</h3>
      <p v-if="selectedChapter.description">{{ selectedChapter.description }}</p>
      <small class="text-muted">Subject: {{ selectedSubject && selectedSubject.name }}</small>
    </div>

    <!-- Questions Table -->
    <div v-if="selectedChapterId && !loading" class="table-container">
      <table class="questions-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Question</th>
            <th>Options</th>
            <th>Correct Answer</th>
            <th>Quiz</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="question in filteredQuestions" :key="question.id">
            <td>{{ question.id }}</td>
            <td>
              <div class="question-text" :title="question.question_statement">
                {{ truncateText(question.question_statement, 50) }}
              </div>
            </td>
            <td>
              <div class="options-preview">
                <div><strong>1:</strong> {{ truncateText(question.option1, 20) }}</div>
                <div><strong>2:</strong> {{ truncateText(question.option2, 20) }}</div>
                <div v-if="question.option3"><strong>3:</strong> {{ truncateText(question.option3, 20) }}</div>
                <div v-if="question.option4"><strong>4:</strong> {{ truncateText(question.option4, 20) }}</div>
              </div>
            </td>
            <td>
              <span class="correct-answer">Option {{ question.correct_option }}</span>
            </td>
            <td>{{ question.quiz_title || 'Default Quiz' }}</td>
            <td>{{ formatDate(question.created_at) }}</td>
            <td class="actions">
              <button
                @click="viewQuestion(question)"
                class="btn btn-sm btn-info"
                title="View Details"
              >
                <i class="fas fa-eye"></i>
              </button>
              <button
                @click="editQuestion(question)"
                class="btn btn-sm btn-edit"
                title="Edit"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button
                @click="deleteQuestion(question)"
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
      <div v-if="filteredQuestions.length === 0 && !loading" class="empty-state">
        <i class="fas fa-question-circle fa-3x"></i>
        <h3>No questions found</h3>
        <p>{{ searchQuery ? 'No questions match your search.' : 'Start by creating your first question for this chapter.' }}</p>
      </div>
    </div>

    <!-- No Selection State -->
    <div v-else-if="!selectedSubjectId && !loading" class="empty-state">
      <i class="fas fa-book fa-3x"></i>
      <h3>Select a Subject and Chapter</h3>
      <p>Choose a subject and chapter from the dropdowns above to view and manage questions.</p>
    </div>

    <div v-else-if="selectedSubjectId && !selectedChapterId && !loading && chapters.length === 0" class="empty-state">
      <i class="fas fa-book-open fa-3x"></i>
      <h3>No Chapters Available</h3>
      <p>This subject doesn't have any chapters yet. Create chapters first before adding questions.</p>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal modal-large" @click.stop>
        <div class="modal-header">
          <h3>{{ editingQuestion ? 'Edit Question' : 'Create New Question' }}</h3>
          <button @click="closeModal" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveQuestion" class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label for="subject">Subject *</label>
              <select
                id="subject"
                v-model="form.subject_id"
                @change="onFormSubjectChange"
                class="form-control"
                :class="{ 'error': errors.subject_id }"
                required
              >
                <option value="">Select a subject</option>
                <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                  {{ subject.name }}
                </option>
              </select>
              <span v-if="errors.subject_id" class="error-text">{{ errors.subject_id }}</span>
            </div>
            
            <div class="form-group">
              <label for="chapter">Chapter *</label>
              <select
                id="chapter"
                v-model="form.chapter_id"
                class="form-control"
                :class="{ 'error': errors.chapter_id }"
                :disabled="!form.subject_id || formChapters.length === 0"
                required
              >
                <option value="">Select a chapter</option>
                <option v-for="chapter in formChapters" :key="chapter.id" :value="chapter.id">
                  {{ chapter.name }}
                </option>
              </select>
              <span v-if="errors.chapter_id" class="error-text">{{ errors.chapter_id }}</span>
              <small class="form-text text-muted">
                Questions will be added to a quiz automatically if none exists for this chapter.
              </small>
            </div>
          </div>
          
          <div class="form-group">
            <label for="question_statement">Question Statement *</label>
            <textarea
              id="question_statement"
              v-model="form.question_statement"
              class="form-control"
              :class="{ 'error': errors.question_statement }"
              placeholder="Enter the question statement"
              rows="4"
              required
            ></textarea>
            <span v-if="errors.question_statement" class="error-text">{{ errors.question_statement }}</span>
          </div>
          
          <!-- Answer Options -->
          <div class="options-section">
            <h4>Answer Options</h4>
            
            <div class="form-row">
              <div class="form-group">
                <label for="option1">Option 1 *</label>
                <div class="option-input">
                  <input
                    id="option1"
                    v-model="form.option1"
                    type="text"
                    class="form-control"
                    :class="{ 'error': errors.option1 }"
                    placeholder="Enter option 1"
                    required
                  />
                  <label class="radio-label">
                    <input
                      v-model="form.correct_option"
                      type="radio"
                      :value="1"
                    />
                    <span>Correct</span>
                  </label>
                </div>
                <span v-if="errors.option1" class="error-text">{{ errors.option1 }}</span>
              </div>
              
              <div class="form-group">
                <label for="option2">Option 2 *</label>
                <div class="option-input">
                  <input
                    id="option2"
                    v-model="form.option2"
                    type="text"
                    class="form-control"
                    :class="{ 'error': errors.option2 }"
                    placeholder="Enter option 2"
                    required
                  />
                  <label class="radio-label">
                    <input
                      v-model="form.correct_option"
                      type="radio"
                      :value="2"
                    />
                    <span>Correct</span>
                  </label>
                </div>
                <span v-if="errors.option2" class="error-text">{{ errors.option2 }}</span>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="option3">Option 3 (Optional)</label>
                <div class="option-input">
                  <input
                    id="option3"
                    v-model="form.option3"
                    type="text"
                    class="form-control"
                    placeholder="Enter option 3 (optional)"
                  />
                  <label class="radio-label">
                    <input
                      v-model="form.correct_option"
                      type="radio"
                      :value="3"
                      :disabled="!form.option3 || !form.option3.trim()"
                    />
                    <span>Correct</span>
                  </label>
                </div>
              </div>
              
              <div class="form-group">
                <label for="option4">Option 4 (Optional)</label>
                <div class="option-input">
                  <input
                    id="option4"
                    v-model="form.option4"
                    type="text"
                    class="form-control"
                    placeholder="Enter option 4 (optional)"
                  />
                  <label class="radio-label">
                    <input
                      v-model="form.correct_option"
                      type="radio"
                      :value="4"
                      :disabled="!form.option4 || !form.option4.trim()"
                    />
                    <span>Correct</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              {{ saving ? 'Saving...' : (editingQuestion ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Question Modal -->
    <div v-if="showViewModal" class="modal-overlay" @click="closeViewModal">
      <div class="modal modal-large" @click.stop>
        <div class="modal-header">
          <h3>Question Details</h3>
          <button @click="closeViewModal" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body" v-if="viewingQuestion">
          <div class="question-details">
            <div class="detail-row">
              <strong>Question:</strong>
              <p>{{ viewingQuestion.question_statement }}</p>
            </div>
            
            <div class="detail-row">
              <strong>Options:</strong>
              <ul class="options-list">
                <li :class="{ 'correct-option': viewingQuestion.correct_option === 1 }">
                  <strong>1.</strong> {{ viewingQuestion.option1 }}
                  <span v-if="viewingQuestion.correct_option === 1" class="correct-badge">✓ Correct</span>
                </li>
                <li :class="{ 'correct-option': viewingQuestion.correct_option === 2 }">
                  <strong>2.</strong> {{ viewingQuestion.option2 }}
                  <span v-if="viewingQuestion.correct_option === 2" class="correct-badge">✓ Correct</span>
                </li>
                <li v-if="viewingQuestion.option3" :class="{ 'correct-option': viewingQuestion.correct_option === 3 }">
                  <strong>3.</strong> {{ viewingQuestion.option3 }}
                  <span v-if="viewingQuestion.correct_option === 3" class="correct-badge">✓ Correct</span>
                </li>
                <li v-if="viewingQuestion.option4" :class="{ 'correct-option': viewingQuestion.correct_option === 4 }">
                  <strong>4.</strong> {{ viewingQuestion.option4 }}
                  <span v-if="viewingQuestion.correct_option === 4" class="correct-badge">✓ Correct</span>
                </li>
              </ul>
            </div>
            
            <div class="detail-row">
              <strong>Quiz:</strong>
              <span>{{ viewingQuestion.quiz_title || 'Default Quiz' }}</span>
            </div>
            
            <div class="detail-row">
              <strong>Chapter:</strong>
              <span>{{ viewingQuestion.chapter_name || (selectedChapter && selectedChapter.name) }}</span>
            </div>
          </div>
        </div>
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
  name: 'QuestionManagement',
  data() {
    return {
      subjects: [],
      chapters: [],
      formChapters: [],
      questions: [],
      filteredQuestions: [],
      selectedSubjectId: '',
      selectedChapterId: '',
      selectedSubject: null,
      selectedChapter: null,
      loading: false,
      saving: false,
      showModal: false,
      showViewModal: false,
      editingQuestion: null,
      viewingQuestion: null,
      searchQuery: '',
      message: '',
      messageType: 'success',
      form: {
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: 1,
        subject_id: '',
        chapter_id: '',
        quiz_id: ''
      },
      errors: {}
    }
  },
  
  mounted() {
    this.loadSubjects()
  },
  
  methods: {
    async loadSubjects() {
      try {
        console.log('Loading subjects...')
        const response = await axios.get('/api/admin/subjects', {
          headers: this.getAuthHeaders()
        })
        
        console.log('Subjects response:', response.data)
        
        // Handle both paginated and non-paginated responses
        this.subjects = response.data.subjects || response.data || []
        
        console.log('Loaded subjects:', this.subjects.length)
        
      } catch (error) {
        console.error('Error loading subjects:', error)
        this.showMessage('Error loading subjects: ' + this.getErrorMessage(error), 'error')
        this.subjects = []
      }
    },

    async onSubjectChange() {
      this.selectedChapterId = ''
      this.selectedChapter = null
      this.questions = []
      this.filteredQuestions = []
      
      if (!this.selectedSubjectId) {
        this.chapters = []
        this.selectedSubject = null
        return
      }
      
      // Find selected subject
      this.selectedSubject = this.subjects.find(s => s.id == this.selectedSubjectId)
      
      try {
        console.log('Loading chapters for subject:', this.selectedSubjectId)
        const response = await axios.get(`/api/admin/subjects/${this.selectedSubjectId}/chapters`, {
          headers: this.getAuthHeaders()
        })
        
        console.log('Chapters response:', response.data)
        this.chapters = response.data.chapters || []
        
      } catch (error) {
        console.error('Error loading chapters:', error)
        this.showMessage('Error loading chapters: ' + this.getErrorMessage(error), 'error')
        this.chapters = []
      }
    },
    
    async loadQuestions() {
      if (!this.selectedChapterId) {
        this.questions = []
        this.filteredQuestions = []
        this.selectedChapter = null
        return
      }
      
      // Find selected chapter
      this.selectedChapter = this.chapters.find(c => c.id == this.selectedChapterId)
      
      try {
        this.loading = true
        console.log('Loading questions for chapter:', this.selectedChapterId)
        
        const response = await axios.get(`/api/admin/chapters/${this.selectedChapterId}/questions`, {
          headers: this.getAuthHeaders()
        })
        
        console.log('Questions response:', response.data)
        
        this.questions = response.data.questions || response.data || []
        this.filterQuestions()
        
      } catch (error) {
        console.error('Error loading questions:', error)
        this.showMessage('Error loading questions: ' + this.getErrorMessage(error), 'error')
        this.questions = []
        this.filteredQuestions = []
      } finally {
        this.loading = false
        console.log('Loading finished, questions:', this.questions.length)
      }
    },
    
    filterQuestions() {
      if (!this.searchQuery) {
        this.filteredQuestions = this.questions
      } else {
        const query = this.searchQuery.toLowerCase()
        this.filteredQuestions = this.questions.filter(question =>
          question.question_statement.toLowerCase().includes(query) ||
          question.option1.toLowerCase().includes(query) ||
          question.option2.toLowerCase().includes(query) ||
          (question.option3 && question.option3.toLowerCase().includes(query)) ||
          (question.option4 && question.option4.toLowerCase().includes(query))
        )
      }
    },
    
    openCreateModal() {
      this.editingQuestion = null
      this.resetForm()
      this.errors = {}
      this.showModal = true
    },
    
    editQuestion(question) {
      this.editingQuestion = question
      this.form = {
        question_statement: question.question_statement || '',
        option1: question.option1 || '',
        option2: question.option2 || '',
        option3: question.option3 || '',
        option4: question.option4 || '',
        correct_option: question.correct_option || 1,
        subject_id: (this.selectedSubjectId || '').toString(),
        chapter_id: (question.chapter_id || this.selectedChapterId || '').toString(),
        quiz_id: (question.quiz_id || '').toString()
      }
      
      if (this.form.subject_id) {
        this.onFormSubjectChange()
      }
      this.errors = {}
      this.showModal = true
    },
    
    viewQuestion(question) {
      this.viewingQuestion = question
      this.showViewModal = true
    },
    
    closeModal() {
      this.showModal = false
      this.editingQuestion = null
      this.resetForm()
      this.errors = {}
    },
    
    closeViewModal() {
      this.showViewModal = false
      this.viewingQuestion = null
    },
    
    resetForm() {
      this.form = {
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: 1,
        subject_id: this.selectedSubjectId || '',
        chapter_id: this.selectedChapterId || '',
        quiz_id: ''
      }
      this.formChapters = []
      if (this.form.subject_id) {
        this.onFormSubjectChange()
      }
    },

    async onFormSubjectChange() {
      this.form.chapter_id = ''
      this.form.quiz_id = ''
      this.formChapters = []
      
      if (!this.form.subject_id) return
      
      try {
        const response = await axios.get(`/api/admin/subjects/${this.form.subject_id}/chapters`, {
          headers: this.getAuthHeaders()
        })
        
        this.formChapters = response.data.chapters || []
        
      } catch (error) {
        console.error('Error loading chapters for form:', error)
        this.formChapters = []
      }
    },
    
    async saveQuestion() {
      try {
        this.saving = true
        this.errors = {}
        
        // Basic validation
        if (!this.form.question_statement || !this.form.question_statement.trim()) {
          this.errors.question_statement = 'Question statement is required'
          return
        }
        
        if (!this.form.option1 || !this.form.option1.trim()) {
          this.errors.option1 = 'Option 1 is required'
          return
        }
        
        if (!this.form.option2 || !this.form.option2.trim()) {
          this.errors.option2 = 'Option 2 is required'
          return
        }
        
        if (!this.form.correct_option || this.form.correct_option < 1 || this.form.correct_option > 4) {
          this.errors.correct_option = 'Please select a valid correct option'
          return
        }
        
        if (!this.form.chapter_id) {
          this.errors.chapter_id = 'Chapter is required'
          return
        }
        
        const data = {
          question_statement: this.form.question_statement.trim(),
          option1: this.form.option1.trim(),
          option2: this.form.option2.trim(),
          option3: (this.form.option3 || '').trim(),
          option4: (this.form.option4 || '').trim(),
          correct_option: parseInt(this.form.correct_option),
          chapter_id: parseInt(this.form.chapter_id)
        }
        
        // If editing, include quiz_id
        if (this.editingQuestion && this.form.quiz_id) {
          data.quiz_id = parseInt(this.form.quiz_id)
        }
        
        let response
        if (this.editingQuestion) {
          response = await axios.put(
            `/api/admin/questions/${this.editingQuestion.id}`,
            data,
            { headers: this.getAuthHeaders() }
          )
        } else {
          response = await axios.post(
            '/api/admin/questions',
            data,
            { headers: this.getAuthHeaders() }
          )
        }
        
        this.showMessage(response.data.message, 'success')
        this.closeModal()
        
        // Reload questions for the selected chapter
        if (this.selectedChapterId) {
          this.loadQuestions()
        }
        
      } catch (error) {
        console.error('Error saving question:', error)
        if (error.response && error.response.status === 400) {
          this.showMessage(error.response.data.error, 'error')
        } else {
          this.showMessage('Error saving question: ' + this.getErrorMessage(error), 'error')
        }
      } finally {
        this.saving = false
      }
    },
    
    async deleteQuestion(question) {
      if (!confirm(`Are you sure you want to delete this question?`)) {
        return
      }
      
      try {
        await axios.delete(
          `/api/admin/questions/${question.id}`,
          { headers: this.getAuthHeaders() }
        )
        
        this.showMessage('Question deleted successfully', 'success')
        this.loadQuestions()
        
      } catch (error) {
        this.showMessage('Error deleting question: ' + this.getErrorMessage(error), 'error')
      }
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
    
    truncateText(text, length) {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }
  }
}
</script>

<style scoped>
.question-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #333;
}

.filter-section {
  margin-bottom: 20px;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-box,
.search-box {
  position: relative;
  flex: 1;
  min-width: 200px;
}

.filter-box {
  max-width: 250px;
}

.search-box {
  max-width: 300px;
}

.filter-box select,
.search-box input {
  padding-left: 40px;
}

.filter-icon,
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
}

.chapter-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #007bff;
}

.chapter-info h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.chapter-info p {
  margin: 0 0 4px 0;
  color: #666;
}

.text-muted {
  color: #6c757d;
  font-size: 0.9em;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.questions-table {
  width: 100%;
  border-collapse: collapse;
}

.questions-table th,
.questions-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.questions-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.questions-table tr:hover {
  background: #f8f9fa;
}

.question-text {
  max-width: 200px;
  word-wrap: break-word;
}

.options-preview {
  font-size: 12px;
  line-height: 1.3;
}

.options-preview div {
  margin-bottom: 2px;
  padding: 2px 4px;
  background: #f8f9fa;
  border-radius: 3px;
}

.correct-answer {
  background: #28a745;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 4px;
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

.form-control:disabled {
  background-color: #f8f9fa;
  color: #6c757d;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #333;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.error-text {
  color: #dc3545;
  font-size: 12px;
  margin-top: 4px;
}

.form-text {
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

.modal-large {
  width: 800px;
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

.options-section {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.options-section h4 {
  margin: 0 0 16px 0;
  color: #333;
}

.option-input {
  display: flex;
  align-items: center;
  gap: 12px;
}

.option-input input[type="text"] {
  flex: 1;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: 14px;
  white-space: nowrap;
}

.radio-label input {
  margin: 0;
}

.radio-label:has(input:disabled) {
  opacity: 0.5;
  cursor: not-allowed;
}

.question-details {
  line-height: 1.6;
}

.detail-row {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.detail-row:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.detail-row strong {
  display: block;
  margin-bottom: 4px;
  color: #333;
}

.detail-row p {
  margin: 0;
  color: #666;
}

.options-list {
  list-style: none;
  padding: 0;
  margin: 8px 0 0 0;
}

.options-list li {
  padding: 8px 12px;
  margin: 4px 0;
  background: #f8f9fa;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.options-list li.correct-option {
  background: #d4edda;
  border-left: 4px solid #28a745;
}

.correct-badge {
  color: #28a745;
  font-weight: 500;
  font-size: 12px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-state i {
  color: #ddd;
  margin-bottom: 16px;
}

.empty-state h3 {
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
  .filter-section {
    flex-direction: column;
  }
  
  .filter-box,
  .search-box {
    max-width: none;
  }
  
  .header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .questions-table {
    font-size: 12px;
  }
  
  .questions-table th,
  .questions-table td {
    padding: 8px 4px;
  }
  
  .actions {
    flex-direction: column;
    gap: 4px;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .option-input {
    flex-wrap: wrap;
  }
  
  .modal {
    width: 95vw;
    margin: 10px;
  }
  
  .modal-large {
    width: 95vw;
  }
}
</style>