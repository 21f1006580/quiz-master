<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">Users Management</h2>

    <!-- Search -->
    <input
      v-model="search"
      @input="fetchUsers"
      class="border p-2 rounded w-1/3 mb-4"
      placeholder="Search by name or email"
    />

    <!-- Users Table -->
    <table class="min-w-full border">
      <thead>
        <tr class="bg-gray-100">
          <th class="p-2 border">ID</th>
          <th class="p-2 border">Name</th>
          <th class="p-2 border">Email</th>
          <th class="p-2 border">Qualification</th>
          <th class="p-2 border">Date of Birth</th>
          <th class="p-2 border">Created At</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.user_id">
          <td class="p-2 border">{{ user.user_id }}</td>
          <td class="p-2 border">{{ user.full_name }}</td>
          <td class="p-2 border">{{ user.user_name }}</td>
          <td class="p-2 border">{{ user.qualification || '-' }}</td>
          <td class="p-2 border">{{ user.date_of_birth || '-' }}</td>
          <td class="p-2 border">{{ user.created_at }}</td>
        </tr>
      </tbody>
    </table>

    <!-- Pagination -->
    <div class="mt-4 flex items-center gap-2">
      <button
        class="px-3 py-1 border rounded"
        @click="changePage(currentPage - 1)"
        :disabled="currentPage === 1"
      >
        Prev
      </button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      <button
        class="px-3 py-1 border rounded"
        @click="changePage(currentPage + 1)"
        :disabled="currentPage === totalPages"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      users: [],
      search: "",
      currentPage: 1,
      totalPages: 1,
    };
  },
  methods: {
    async fetchUsers() {
      const token = localStorage.getItem("token");
      try {
        const res = await fetch(
          `/api/admin/users?page=${this.currentPage}&search=${this.search}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        const data = await res.json();
        this.users = data.users;
        this.totalPages = data.pages;
      } catch (err) {
        console.error(err);
      }
    },
    changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.currentPage = page;
      this.fetchUsers();
    },
  },
  mounted() {
    this.fetchUsers();
  },
};
</script>
