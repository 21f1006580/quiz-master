<template>
  <div>
    <h4>All Users</h4>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>Email</th>
          <th>Full Name</th>
          <th>DOB</th>
          <th>Qualification</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.username }}</td>
          <td>{{ user.full_name }}</td>
          <td>{{ user.dob }}</td>
          <td>{{ user.qualification }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      users: []
    };
  },
  async created() {
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://127.0.0.1:5000/admin/users', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    this.users = await response.json();
  }
};
</script>
