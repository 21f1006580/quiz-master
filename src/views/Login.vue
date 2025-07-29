<template>
  <div class="login-page">
    <h3>Login to Your Account</h3>
    <form @submit.prevent="handleLogin">
      <label class="form-label" for="identifier">Username or Email</label>
      <input
        id="identifier"
        type="text"
        class="form-control"
        v-model="identifier"
        placeholder="you@example.com"
        required
      />

      <label class="form-label" for="password">Password</label>
      <input
        id="password"
        type="password"
        class="form-control"
        v-model="password"
        placeholder="••••••••"
        required
      />

      <button type="submit" class="btn-blue" :disabled="isLoading">
        <span v-if="isLoading">Signing in...</span>
        <span v-else>Login</span>
      </button>

      <div class="separator"></div>

      <p class="center-text">
        <router-link to="/register">Don’t have an account? Register</router-link>
      </p>

      <p v-if="error" class="text-danger">{{ error }}</p>
    </form>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      identifier: '',
      password: '',
      error: '',
      isLoading: false,
    }
  },
  computed: {
    validationErrors() {
      const errors = []
      if (!this.identifier) errors.push('Username or email is required.')
      if (!this.password) errors.push('Password is required.')
      return errors
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      this.isLoading = true

      if (this.validationErrors.length === 0) {
        try {
          const response = await fetch('http://127.0.0.1:5000/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              user_name: this.identifier,
              password: this.password,
            }),
            credentials: 'include', // include cookies if backend sets refresh tokens via cookies
          })

          if (response.ok) {
            const data = await response.json()
            localStorage.setItem('access_token', data.access_token)

            const roles = data.user.role || data.user.roles || []
            localStorage.setItem('role', JSON.stringify(roles))

            if (roles.includes('sponsor')) {
              this.$router.push('/sponsor/dashboard')
            } else if (roles.includes('influencer')) {
              this.$router.push('/influencer/dashboard')
            } else if (roles.includes('admin')) {
              this.$router.push('/admin/overview')
            } else {
              this.$router.push('/explore')
            }
          } else {
            const errorData = await response.json()
            this.error = errorData.message || 'An error occurred during login.'
          }
        } catch (err) {
          this.error = 'An error occurred: ' + err.message
        } finally {
          this.isLoading = false
        }
      } else {
        this.error = this.validationErrors.join(' ')
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
html, body, #app {
  height: 100vh;
  margin: 0;
  padding: 0;
  background-color: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Poppins', sans-serif;
  color: #e0f7ff;
  box-sizing: border-box;
}

.login-page {
  background: linear-gradient(to bottom right, #1b1b1b, #111);
  border-radius: 20px;
  padding: 2rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 0 20px #66ccff33;
  box-sizing: border-box;
}

h3 {
  background: linear-gradient(to right, #66ccff, #add8ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 2rem;
}

.form-label {
  color: #bfeaff;
  font-weight: 500;
  display: block;
  margin-bottom: 0.5rem;
}

.form-control {
  background-color: #1f1f1f;
  color: #e0f7ff;
  border: 1px solid #66ccff66;
  width: 100%;
  padding: 0.5rem 0.75rem;
  margin-bottom: 1rem;
  border-radius: 4px;
}

.form-control::placeholder {
  color: #a0cbe8;
}

.btn-blue {
  background-color: #66ccff;
  color: #000;
  border: none;
  transition: all 0.3s ease;
  font-weight: 500;
  width: 100%;
  padding: 0.75rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-blue:disabled {
  background-color: #66ccff99;
  cursor: not-allowed;
}

.btn-blue:hover:not(:disabled) {
  background-color: #4bb3e5;
  color: #fff;
}

.separator {
  border-top: 1px solid #66ccff33;
  margin: 1.5rem 0;
}

.center-text {
  text-align: center;
  font-size: 0.95rem;
  color: #66ccff;
}

.center-text a {
  color: #66ccff;
  text-decoration: none;
}

.center-text a:hover {
  text-decoration: underline;
}

.text-danger {
  color: #dc3545;
  margin-top: 1rem;
  text-align: center;
}
</style>
