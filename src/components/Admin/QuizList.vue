<template>
  <div>
    <h4>Quizzes</h4>
    <form @submit.prevent="createQuiz">
      <input v-model="newQuiz.chapter_id" placeholder="Chapter ID" required />
      <input v-model="newQuiz.date_of_quiz" type="date" required />
      <input v-model="newQuiz.time_duration" placeholder="Time (HH:MM)" required />
      <input v-model="newQuiz.remarks" placeholder="Remarks" />
      <button class="btn btn-success btn-sm ml-2">Add</button>
    </form>

    <ul class="list-group mt-3">
      <li v-for="quiz in quizzes" :key="quiz.id" class="list-group-item d-flex justify-content-between">
        Quiz {{ quiz.id }} | Chapter {{ quiz.chapter_id }} | {{ quiz.date_of_quiz }} | {{ quiz.time_duration }}
        <button class="btn btn-danger btn-sm" @click="deleteQuiz(quiz.id)">Delete</button>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      quizzes: [],
      newQuiz: { chapter_id: '', date_of_quiz: '', time_duration: '', remarks: '' }
    };
  },
  created() {
    this.loadQuizzes();
  },
  methods: {
    async loadQuizzes() {
      const token = localStorage.getItem('access_token');
      const res = await fetch('http://127.0.0.1:5000/admin/quizzes', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      this.quizzes = await res.json();
    },
    async createQuiz() {
      const token = localStorage.getItem('access_token');
      await fetch('http://127.0.0.1:5000/admin/quizzes', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(this.newQuiz)
      });
      this.newQuiz = { chapter_id: '', date_of_quiz: '', time_duration: '', remarks: '' };
      this.loadQuizzes();
    },
    async deleteQuiz(id) {
      const token = localStorage.getItem('access_token');
      await fetch(`http://127.0.0.1:5000/admin/quizzes/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      this.loadQuizzes();
    }
  }
};
</script>
