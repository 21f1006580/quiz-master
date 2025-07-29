<!-- SubjectManagement.vue -->
<template>
  <div class="subject-management">
    <div class="header">
      <h2>Subject Management</h2>
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Add New Subject
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="search-section">
      <div class="search-box">
        <input
          v-model="searchQuery"
          @input="debouncedSearch"
          type="text"
          placeholder="Search subjects..."
          class="form-control"
        />
        <i class="fas fa-search search-icon"></i>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading subjects...
    </div>

    <!-- Subjects Table -->
    <div v-else class="table-container">
      <table class="subjects-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="subject in subjects" :key="subject.id">
            <td>{{ subject.id }}</td>
            <td>{{ subject.name }}</td>
            <td>{{ subject.description || 'No description' }}</td>
            <td>{{ formatDate(subject.created_at) }}</td>
            <td class="actions">
              <button
                @click="editSubject(subject)"
                class="btn btn-sm btn-edit"
                title="Edit"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button
                @click="deleteSubject(subject)"
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
      <div v-if="subjects.length === 0 && !loading" class="empty-state">
        <i class="fas fa-book fa-3x"></i>
        <h3>No subjects found</h3>
        <p>{{ searchQuery ? 'No subjects match your search.' : 'Start by creating your first subject.' }}</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="changePage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="btn btn-sm"
      >
        Previous
      </button>
      
      <span class="page-info">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      
      <button
        @click="changePage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="btn btn-sm"
      >
        Next
      </button>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingSubject ? 'Edit Subject' : 'Create New Subject' }}</h3>
          <button @click="closeModal" class="btn-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveSubject" class="modal-body">
          <div class="form-group">
            <label for="name">Subject Name *</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              class="form-control"
              :class="{ 'error': errors.name }"
              placeholder="Enter subject name"
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
              placeholder="Enter subject description (optional)"
              rows="4"
            ></textarea>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              <i v-if="saving" class="fas fa-spinner fa-spin"></i>
              {{ saving ? 'Saving...' : (editingSubject ? 'Update' : 'Create') }}
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
  name: 'SubjectManagement',
  data() {
    return {
      subjects: [],
      loading: false,
      saving: false,
      showModal: false,
      editingSubject: null,
      searchQuery: '',
      currentPage: 1,
      totalPages: 1,
      perPage: 10,
      message: '',
      messageType: 'success',
      searchTimeout: null,
      form: {
        name: '',
        description: ''
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
        this.loading = true
        const params = {
          page: this.currentPage,
          per_page: this.perPage,
          search: this.searchQuery
        }
        
        const response = await axios.get('/api/admin/subjects', {
          params,
          headers: this.getAuthHeaders()
        })
        
        this.subjects = response.data.subjects
        this.totalPages = response.data.pages
        this.currentPage = response.data.current_page
        
      } catch (error) {
        this.showMessage('Error loading subjects: ' + this.getErrorMessage(error), 'error')
      } finally {
        this.loading = false
      }
    },
    
    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1
        this.loadSubjects()
      }, 500)
    },
    
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.loadSubjects()
      }
    },
    
    openCreateModal() {
      this.editingSubject = null
      this.form = { name: '', description: '' }
      this.errors = {}
      this.showModal = true
    },
    
    editSubject(subject) {
      this.editingSubject = subject
      this.form = {
        name: subject.name,
        description: subject.description || ''
      }
      this.errors = {}
      this.showModal = true
    },
    
    closeModal() {
      this.showModal = false
      this.editingSubject = null
      this.form = { name: '', description: '' }
      this.errors = {}
    },
    
    async saveSubject() {
      try {
        this.saving = true
        this.errors = {}
        
        // Basic validation
        if (!this.form.name.trim()) {
          this.errors.name = 'Subject name is required'
          return
        }
        
        const data = {
          name: this.form.name.trim(),
          description: this.form.description.trim()
        }
        
        let response
        if (this.editingSubject) {
          response = await axios.put(
            `/api/admin/subjects/${this.editingSubject.id}`,
            data,
            { headers: this.getAuthHeaders() }
          )
        } else {
          response = await axios.post(
            '/api/admin/subjects',
            data,
            { headers: this.getAuthHeaders() }
          )
        }
        
        this.showMessage(response.data.message, 'success')
        this.closeModal()
        this.loadSubjects()
        
      } catch (error) {
        if (error.response && error.response.status === 400) {
          this.showMessage(error.response.data.error, 'error')
        } else {
          this.showMessage('Error saving subject: ' + this.getErrorMessage(error), 'error')
        }
      } finally {
        this.saving = false
      }
    },
    
    async deleteSubject(subject) {
      if (!confirm(`Are you sure you want to delete "${subject.name}"?`)) {
        return
      }
      
      try {
        await axios.delete(
          `/api/admin/subjects/${subject.id}`,
          { headers: this.getAuthHeaders() }
        )
        
        this.showMessage('Subject deleted successfully', 'success')
        this.loadSubjects()
        
      } catch (error) {
        this.showMessage('Error deleting subject: ' + this.getErrorMessage(error), 'error')
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
.subject-management {
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

.subjects-table {
  width: 100%;
  border-collapse: collapse;
}

.subjects-table th,
.subjects-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.subjects-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.subjects-table tr:hover {
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
}

.page-info {
  color: #666;
  font-size: 14px;
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
</style>