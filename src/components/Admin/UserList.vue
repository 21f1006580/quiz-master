<!-- UserList.vue -->
<template>
  <div class="user-list">
    <div class="header">
      <h2>User Management</h2>
      <div class="header-stats">
        <span class="stat-badge">
          <i class="fas fa-users"></i>
          {{ totalUsers }} Total Users
        </span>
      </div>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <div class="search-box">
        <input
          v-model="searchQuery"
          @input="debouncedSearch"
          type="text"
          placeholder="Search users by email or name..."
          class="form-control"
        />
        <i class="fas fa-search search-icon"></i>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading users...
    </div>

    <!-- Users Table -->
    <div v-else class="table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Email</th>
            <th>Full Name</th>
            <th>Date of Birth</th>
            <th>Qualification</th>
            <th>Registered</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username || user.email }}</td>
            <td>{{ user.full_name }}</td>
            <td>{{ formatDate(user.dob) }}</td>
            <td>{{ user.qualification || 'Not specified' }}</td>
            <td>{{ formatDate(user.created_at) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="users.length === 0 && !loading" class="empty-state">
        <i class="fas fa-users fa-3x"></i>
        <h3>No users found</h3>
        <p>{{ searchQuery ? 'No users match your search criteria.' : 'No users have registered yet.' }}</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="changePage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="btn btn-sm"
      >
        <i class="fas fa-chevron-left"></i> Previous
      </button>
      
      <span class="page-info">
        Page {{ currentPage }} of {{ totalPages }} ({{ totalUsers }} total users)
      </span>
      
      <button
        @click="changePage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="btn btn-sm"
      >
        Next <i class="fas fa-chevron-right"></i>
      </button>
    </div>

    <!-- Error Messages -->
    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserList',
  data() {
    return {
      users: [],
      loading: false,
      searchQuery: '',
      currentPage: 1,
      totalPages: 1,
      totalUsers: 0,
      perPage: 10,
      error: '',
      searchTimeout: null
    }
  },
  
  mounted() {
    this.loadUsers()
  },
  
  methods: {
    async loadUsers() {
      try {
        this.loading = true
        this.error = ''
        
        const params = {
          page: this.currentPage,
          per_page: this.perPage,
          search: this.searchQuery
        }
        
        const response = await axios.get('/api/admin/users', {
          params,
          headers: this.getAuthHeaders()
        })
        
        // Handle the API response structure
        if (response.data && response.data.users) {
          this.users = response.data.users
          this.totalPages = response.data.pages || 1
          this.currentPage = response.data.current_page || 1
          this.totalUsers = response.data.total || 0
        } else {
          // Fallback for direct array response
          this.users = Array.isArray(response.data) ? response.data : []
          this.totalUsers = this.users.length
          this.totalPages = 1
          this.currentPage = 1
        }
        
      } catch (error) {
        console.error('Error loading users:', error)
        this.error = 'Error loading users: ' + this.getErrorMessage(error)
        this.users = []
      } finally {
        this.loading = false
      }
    },
    
    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1
        this.loadUsers()
      }, 500)
    },
    
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.loadUsers()
      }
    },
    
    getAuthHeaders() {
      const token = localStorage.getItem('access_token')
      return token ? { Authorization: `Bearer ${token}` } : {}
    },
    
    getErrorMessage(error) {
      if (error.response) {
        const data = error.response.data || {}
        return data.error || data.message || `HTTP ${error.response.status}`
      }
      return error.message || 'Unknown error occurred'
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Not provided'
      
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        })
      } catch (e) {
        return dateString
      }
    }
  }
}
</script>

<style scoped>
.user-list {
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

.header-stats {
  display: flex;
  gap: 12px;
}

.stat-badge {
  background: #007bff;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
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

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.users-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.users-table tr:hover {
  background: #f8f9fa;
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
  background: #007bff;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn:hover:not(:disabled) {
  background: #0056b3;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
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

.alert-error {
  background: #dc3545;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .users-table {
    font-size: 12px;
  }
  
  .users-table th,
  .users-table td {
    padding: 8px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 8px;
  }
}
</style>