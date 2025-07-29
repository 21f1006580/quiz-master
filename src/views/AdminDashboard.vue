<template>
  <div class="container mt-4">
    <h2>Admin Dashboard</h2>
    <ul class="nav nav-tabs">
      <li class="nav-item" v-for="tab in tabs" :key="tab">
        <a class="nav-link" :class="{active: currentTab === tab}" @click="currentTab = tab">{{ tab }}</a>
      </li>
    </ul>
    <div class="mt-3">
      <component :is="getTabComponent(currentTab)" />
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tabs: ['Users', 'Subjects', 'Chapters', 'Quizzes', 'Questions'],
      currentTab: 'Users'
    };
  },
  methods: {
    getTabComponent(tab) {
      return {
        'Users': 'UserList',
        'Subjects': 'SubjectList',
        'Chapters': 'ChapterList',
        'Quizzes': 'QuizList',
        'Questions': 'QuestionList'
      }[tab];
    }
  }
};
</script>
