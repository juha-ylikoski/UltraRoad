<template>
    <GMapMap
      :center="{ lat: 61.49820944105238, lng: 23.76485334705572 }"
      :zoom="13"
      map-type-id="terrain" 
      style="width: 100vw; height: 40rem"
      ref="myMap"
      :options="{
                      zoomControl: true,
                      mapTypeControl: false,
                      scaleControl: true,
                      streetViewControl: false,
                      rotateControl: true,
                      fullscreenControl: false,
                }"
    >
      <GMapMarker
          :key="m.id"
          v-for="m in store.markers"
          :position="{'lat': m.latitude, 'lng': m.longitude}"
          :clickable="true"
          @click.self="openMarker(m.id)"
        >
        <GMapInfoWindow
        :closeclick="true"
        @click.self="openMarker(null)"
        :opened="store.openedMarkerID === m.id"
        >
        <InfoBox :id="m.id"></InfoBox>
        </GMapInfoWindow>
      </GMapMarker>
    </GMapMap>
</template>

<script setup>
import { useCounterStore } from '@/stores/counter';
import { onMounted, ref } from 'vue';
import InfoBox from './InfoBox.vue'

const store = useCounterStore()
const myMap = ref()
async function openMarker(id) {
  console.log("Marker clicked:", id)
    if (id !== store.openedMarkerID) {
      store.openedMarkerID = id
      if (id !== null) {
        store.image = null
        store.currentIssue = {}
        let response = await fetch(`http://localhost:5173/api/posts/${store.openedMarkerID}/img`)
        response = await response.blob()
        console.log(response);
        const urlCreator = window.URL || window.webkitURL
        response = urlCreator.createObjectURL(response)
        store.currentIssue = store.markers.find((ele) => ele.id === id)
        store.image = response
      }
      console.log(store.openedMarkerID);
    }
    
    
}
    onMounted(() => {
        //CALL FOR API TO GET CURRENT MARKERS
        fetch('http://localhost:5173/api/posts')
        .then((b) => b.json())
        .then((data) => {
          console.log(data)
          store.markers = data
          store.sortedMarkers = store.markers.sort((a, b) => (a.score < b.score) ? 1 : -1)
        })
        .catch((e) => console.log(e))
    })
</script>