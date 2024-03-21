<template>
  <div>
    <ul>
      <ListItem v-for="issue in store.sortedMarkers" :title="issue.title" :text="issue.text" :score="issue.score"/>
    </ul>
  </div>
</template>

<script setup>
import { useCounterStore } from '@/stores/counter';
import ListItem from '../components/ListItem.vue'
const store = useCounterStore()
</script>

