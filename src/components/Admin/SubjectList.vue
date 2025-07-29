<template>
  <div>
    <h4>Subjects</h4>
    <form @submit.prevent="createSubject">
      <input v-model="newSubject.name" placeholder="Subject Name" required />
      <input v-model="newSubject.description" placeholder="Description" required />
      <button class="btn btn-success btn-sm ml-2">Add</button>
    </form>

    <ul class="list-group mt-3">
      <li v-for="subject in subjects" :key="subject.id" class="list-group-item d-flex justify-content-between">
        {{ subject.name }} - {{ subject.description }}
        <button class="btn btn-danger btn-sm" @click="deleteSubject(subject.id)">Delete</button>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      subjects: [],
      newSubject: { name: '', description: '' }
    };
  },
  created() {
    this.loadSubjects();
  },
  methods: {
    async loadSubjects() {
      const token = localStorage.getItem('access_token');
      const res = await fetch('http://127.0.0.1:5000/admin/subjects', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      this.subjects = await res.json();
    },
    async createSubject() {
      const token = localStorage.getItem('access_token');
      await fetch('http://127.0.0.1:5000/admin/subjects', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(this.newSubject)
      });
      this.newSubject = { name: '', description: '' };
      this.loadSubjects();
    },
    async deleteSubject(id) {
      const token = localStorage.getItem('access_token');
      await fetch(`http://127.0.0.1:5000/admin/subjects/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      this.loadSubjects();
    }
  }
};
</script>
