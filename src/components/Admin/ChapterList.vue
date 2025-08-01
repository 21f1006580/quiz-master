<!-- ChapterManagement.vue -->
<template>
  <div class="chapter-management">
    <div class="header">
      <h2>Chapter Management</h2>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Add New Chapter
      </button>
    </div>

    <!-- Subject Filter -->
    <div class="filter-section">
      <div class="filter-box">
        <select
          v-model="selectedSubjectId"
          @change="loadChapters"
          class="form-control"
        >
          <option value="">Select a subject to view chapters</option>
          <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
            {{ subject.name }}
          </option>
        </select>
        <i class="fas fa-book filter-icon"></i>
      </div>
      
      <!-- Search Box -->
      <div class="search-box" v-if="selectedSubjectId">
        <input
          v-model="searchQuery"
          @input="filterChapters"
          type="text"
          placeholder="Search chapters..."
          class="form-control"
        />
        <i class="fas fa-search search-icon"></i>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading chapters...
    </div>

    <!-- Selected Subject Info -->
    <div v-else-if="selectedSubject" class="subject-info">
      <h3>{{ selectedSubject.name }}</h3>
      <p v-if="selectedSubject && selectedSubject.description">{{ selectedSubject.description }}</p>
    </div>

    <!-- Chapters Table -->
    <div v-if="selectedSubjectId && !loading" class="table-container">
      <table class="chapters-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Subject</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="chapter in filteredChapters" :key="chapter.id">
            <td>{{ chapter.id }}</td>
            <td>{{ chapter.name }}</td>
            <td>{{ chapter.description || 'No description' }}</td>
            <td>{{ selectedSubject && selectedSubject.name }}</td>
            <td>{{ formatDate(chapter.created_at) }}</td>
            <td class="actions">
              <button
                @click="editChapter(chapter)"
                class="btn btn-sm btn-edit"
                title="Edit"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button
                @click="deleteChapter(chapter)"
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
      <div v-if="filteredChapters.length === 0 && !loading" class="empty-state">
        <i class="fas fa-book-open fa-3x"></i>
        <h3>No chapters found</h3>
        <p>{{ searchQuery ? 'No chapters match your search.' : 'Start by creating your first chapter for this subject.' }}</p>
      </div>
    </div>

    <!-- No Subject Selected -->
    <div v-else-if="!selectedSubjectId && !loading" class="empty-state">
      <i class="fas fa-book fa-3x"></i>
      <h3>Select a Subject</h3>
      <p>Choose a subject from the dropdown above to view and manage its chapters.</p>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingChapter ? 'Edit Chapter' : 'Create New Chapter' }}</h3>
          <button @click="closeModal" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveChapter" class="modal-body">
          <div class="form-group">
            <label for="subject">Subject *</label>
            <select
              id="subject"
              v-model="form.subject_id"
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
            <label for="name">Chapter Name *</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              class="form-control"
              :class="{ 'error': errors.name }"
              placeholder="Enter chapter name"
              required
            />
            <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
          </div>
          
          <div class="form-group">
            <label for="description">Description</label>
            <textarea
              id="description"
              v-model="form.description"
              class="form-control"
              placeholder="Enter chapter description (optional)"
              rows="4"
            ></textarea>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              {{ saving ? 'Saving...' : (editingChapter ? 'Update' : 'Create') }}
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
  name: 'ChapterManagement',
  data() {
    return {
      subjects: [],
      chapters: [],
      filteredChapters: [],
      selectedSubjectId: '',
      selectedSubject: null,
      loading: false,
      saving: false,
      showModal: false,
      editingChapter: null,
      searchQuery: '',
      message: '',
      messageType: 'success',
      form: {
        name: '',
        description: '',
        subject_id: ''
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
    
    async loadChapters() {
      if (!this.selectedSubjectId) {
        this.chapters = []
        this.filteredChapters = []
        this.selectedSubject = null
        this.loading = false
        return
      }
      
      try {
        this.loading = true
        console.log('Loading chapters for subject:', this.selectedSubjectId)
        
        const response = await axios.get(`/api/admin/subjects/${this.selectedSubjectId}/chapters`, {
          headers: this.getAuthHeaders()
        })
        
        console.log('Chapters response:', response.data)
        
        this.selectedSubject = response.data.subject || null
        this.chapters = response.data.chapters || []
        this.filterChapters()
        
      } catch (error) {
        console.error('Error loading chapters:', error)
        this.showMessage('Error loading chapters: ' + this.getErrorMessage(error), 'error')
        this.chapters = []
        this.filteredChapters = []
      } finally {
        this.loading = false
        console.log('Loading finished, chapters:', this.chapters.length)
      }
    },
    
    filterChapters() {
      if (!this.searchQuery) {
        this.filteredChapters = this.chapters
      } else {
        const query = this.searchQuery.toLowerCase()
        this.filteredChapters = this.chapters.filter(chapter =>
          chapter.name.toLowerCase().includes(query) ||
          (chapter.description && chapter.description.toLowerCase().includes(query))
        )
      }
    },
    
    openCreateModal() {
      this.editingChapter = null
      this.form = { 
        name: '', 
        description: '', 
        subject_id: this.selectedSubjectId || '' 
      }
      this.errors = {}
      this.showModal = true
    },
    
    editChapter(chapter) {
      this.editingChapter = chapter
      this.form = {
        name: chapter.name,
        description: chapter.description || '',
        subject_id: chapter.subject_id
      }
      this.errors = {}
      this.showModal = true
    },
    
    closeModal() {
      this.showModal = false
      this.editingChapter = null
      this.form = { name: '', description: '', subject_id: '' }
      this.errors = {}
    },
    
    async saveChapter() {
      try {
        this.saving = true
        this.errors = {}
        
        // Basic validation
        if (!this.form.name.trim()) {
          this.errors.name = 'Chapter name is required'
          return
        }
        
        if (!this.form.subject_id) {
          this.errors.subject_id = 'Subject is required'
          return
        }
        
        const data = {
          name: this.form.name.trim(),
          description: this.form.description.trim(),
          subject_id: parseInt(this.form.subject_id)
        }
        
        let response
        if (this.editingChapter) {
          response = await axios.put(
            `/api/admin/chapters/${this.editingChapter.id}`,
            data,
            { headers: this.getAuthHeaders() }
          )
        } else {
          response = await axios.post(
            '/api/admin/chapters',
            data,
            { headers: this.getAuthHeaders() }
          )
        }
        
        this.showMessage(response.data.message, 'success')
        this.closeModal()
        
        // Reload chapters for the selected subject
        if (this.selectedSubjectId) {
          this.loadChapters()
        }
        
        // If we created a chapter for a different subject, switch to that subject
        if (!this.editingChapter && data.subject_id !== this.selectedSubjectId) {
          this.selectedSubjectId = data.subject_id.toString()
          this.loadChapters()
        }
        
      } catch (error) {
        if (error.response && error.response.status === 400) {
          this.showMessage(error.response.data.error, 'error')
        } else {
          this.showMessage('Error saving chapter: ' + this.getErrorMessage(error), 'error')
        }
      } finally {
        this.saving = false
      }
    },
    
    async deleteChapter(chapter) {
      if (!confirm(`Are you sure you want to delete "${chapter.name}"?`)) {
        return
      }
      
      try {
        await axios.delete(
          `/api/admin/chapters/${chapter.id}`,
          { headers: this.getAuthHeaders() }
        )
        
        this.showMessage('Chapter deleted successfully', 'success')
        this.loadChapters()
        
      } catch (error) {
        this.showMessage('Error deleting chapter: ' + this.getErrorMessage(error), 'error')
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
    }
  }
}
</script>

<style scoped>
.chapter-management {
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
  min-width: 250px;
}

.filter-box {
  max-width: 300px;
}

.search-box {
  max-width: 400px;
}

.filter-box input,
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

.subject-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #007bff;
}

.subject-info h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.subject-info p {
  margin: 0;
  color: #666;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chapters-table {
  width: 100%;
  border-collapse: collapse;
}

.chapters-table th,
.chapters-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.chapters-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.chapters-table tr:hover {
  background: #f8f9fa;
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
  width: 500px;
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
  
  .chapters-table {
    font-size: 12px;
  }
  
  .chapters-table th,
  .chapters-table td {
    padding: 8px;
  }
  
  .actions {
    flex-direction: column;
    gap: 4px;
  }
}
</style>