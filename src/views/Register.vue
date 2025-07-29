<template>
  <div class="container d-flex justify-content-center align-items-center min-vh-100">
    <div class="card w-100" style="max-width: 550px;">
      <h3>Create Your Account</h3>

      <form @submit.prevent="registerUser">
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input type="email" class="form-control" v-model="form.user_name" placeholder="you@example.com" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Password</label>
          <input type="password" class="form-control" v-model="form.password" placeholder="••••••••" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Full Name</label>
          <input type="text" class="form-control" v-model="form.full_name" placeholder="Your full name" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Qualification</label>
          <input type="text" class="form-control" v-model="form.qualification" placeholder="Optional" />
        </div>

        <div class="mb-3">
          <label class="form-label">Date of Birth</label>
          <input type="date" class="form-control" v-model="form.date_of_birth" />
        </div>

        <button type="submit" class="btn btn-blue w-100 mt-3">Register</button>
      </form>

      <div class="separator"></div>

      <!-- ✅ Success and Error Messages -->
      <div class="text-success mb-2 mx-2" v-if="successMessage">{{ successMessage }}</div>
      <div class="text-danger mb-2 mx-2" v-if="errorMessage">{{ errorMessage }}</div>

      <p class="center-text mt-3">
        <router-link to="/login">Already have an account? Login</router-link>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "Register",
  data() {
    return {
      form: {
        user_name: "",
        password: "",
        full_name: "",
        qualification: "",
        date_of_birth: "",
      },
      successMessage: "",
      errorMessage: "",
    };
  },
  methods: {
    async registerUser() {
      this.errorMessage = "";
      this.successMessage = "";

      try {
        const res = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.form),
        });

        const result = await res.json();

        if (res.ok) {
          this.successMessage = "Registration successful. Redirecting to login...";
          setTimeout(() => {
            this.$router.push("/login");
          }, 2000);
        } else {
          this.errorMessage = result.message || "Registration failed.";
        }
      } catch (error) {
        console.error("Registration error:", error);
        this.errorMessage = "Something went wrong. Please try again.";
      }
    },
  },
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap");

body {
  background-color: #000;
  font-family: 'Poppins', sans-serif;
  color: #e0f7ff;
}
.card {
  background: linear-gradient(to bottom right, #1c1c1c, #0d0d0d);
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 0 20px #66ccff33;
}
.form-label {
  color: #bfeaff;
  font-weight: 500;
}
.form-control {
  background-color: #1f1f1f;
  color: #e0f7ff;
  border: 1px solid #66ccff66;
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
}
.btn-blue:hover {
  background-color: #4bb3e5;
  color: #fff;
}
h3 {
  background: linear-gradient(to right, #66ccff, #add8ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
  text-align: center;
  margin-bottom: 2rem;
}
a {
  color: #66ccff;
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}
.separator {
  border-top: 1px solid #66ccff33;
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}
.center-text {
  text-align: center;
  font-size: 0.95rem;
}
.text-success {
  color: #28a745;
  font-weight: 500;
}
.text-danger {
  color: #dc3545;
  font-weight: 500;
}
</style>
