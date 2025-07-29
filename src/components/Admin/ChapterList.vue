<template>
  <div>
    <h4>Chapters</h4>
    <form @submit.prevent="createChapter">
      <input v-model="newChapter.name" placeholder="Chapter Name" required />
      <input v-model="newChapter.description" placeholder="Description" required />
      <input v-model="newChapter.subject_id" placeholder="Subject ID" required />
      <button class="btn btn-success btn-sm ml-2">Add</button>
    </form>

    <ul class="list-group mt-3">
      <li v-for="chapter in chapters" :key="chapter.id" class="list-group-item d-flex justify-content-between">
        {{ chapter.name }} - {{ chapter.description }} (Subject ID: {{ chapter.subject_id }})
        <button class="btn btn-danger btn-sm" @click="deleteChapter(chapter.id)">Delete</button>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      chapters: [],
      newChapter: { name: '', description: '', subject_id: '' }
    };
  },
  created() {
    this.loadChapters();
  },
  methods: {
    async loadChapters() {
      const token = localStorage.getItem('access_token');
      const res = await fetch('http://127.0.0.1:5000/admin/chapters', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      this.chapters = await res.json();
    },
    async createChapter() {
      const token = localStorage.getItem('access_token');
      await fetch('http://127.0.0.1:5000/admin/chapters', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(this.newChapter)
      });
      this.newChapter = { name: '', description: '', subject_id: '' };
      this.loadChapters();
    },
