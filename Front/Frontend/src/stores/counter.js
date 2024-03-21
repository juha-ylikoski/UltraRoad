import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  const markers = ref([])
  const openedMarkerID = ref(null)
  const image = ref()
  const currentIssue = ref({})
  const sortedMarkers = ref([])
  watch(markers.value, () => {
    console.log("has changed")
    sortedMarkers.value = markers.value.sort((a, b) => (a.score > b.score) ? 1 : -1)
  })
  return { markers, openedMarkerID, image, currentIssue, sortedMarkers }
})
