<template>
  <div>
    <h4>Questions</h4>
    <form @submit.prevent="createQuestion">
      <input v-model="newQuestion.quiz_id" placeholder="Quiz ID" required />
      <input v-model="newQuestion.question_statement" placeholder="Question" required />
      <input v-model="newQuestion.option1" placeholder="Option 1" required />
      <input v-model="newQuestion.option2" placeholder="Option 2" required />
      <input v-model="newQuestion.option3" placeholder="Option 3" required />
      <input v-model="newQuestion.option4" placeholder="Option 4" required />
      <input v-model="newQuestion.correct_option" placeholder="Correct Option (1-4)" required />
      <button class="btn btn-success btn-sm ml-2">Add</button>
    </form>

    <ul class="list-group mt-3">
      <li v-for="q in questions" :key="q.id" class="list-group-item">
        [Q{{ q.id }}] {{ q.question_statement }} (Correct: Option {{ q.correct_option }})
        <button class="btn btn-danger btn-sm float-right" @click="deleteQuestion(q.id)">Delete</button>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      questions: [],
      newQuestion: {
        quiz_id: '',
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: ''
      }
    };
  },
  created() {
    this.loadQuestions();
  },
  methods: {
    async loadQuestions() {
      const token = localStorage.getItem('access_token');
      const res = await fetch('http://127.0.0.1:5000/admin/questions', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      this.questions = await res.json();
    },
    async createQuestion() {
      const token = localStorage.getItem('access_token');
      await fetch('http://127.0.0.1:5000/admin/questions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(this.newQuestion)
      });
      this.newQuestion = {
        quiz_id: '',
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: ''
      };
      this.loadQuestions();
    },
    async deleteQuestion(id) {
      const token = localStorage.getItem('access_token');
      await fetch(`http://127.0.0.1:5000/admin/questions/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      this.loadQuestions();
    }
  }
};
</script>
