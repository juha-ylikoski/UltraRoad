<template>
    <li>
        <p>{{ props.title }}</p>
        <p>{{ props.text }}</p>
        <p>{{ props.score }}</p>
    </li>
</template>

<script setup>
const props = defineProps(['title', 'text', 'score'])
</script>

<style scoped>
li {
  padding: 8px 16px;
  border-bottom: 1px solid #ddd;
  list-style-type: none;
}

li:last-child {
  border-bottom: none
  
}
</style>