<template>
    <div>
        <h1>{{ store.currentIssue.title }}</h1>
        <p>{{ store.currentIssue.text }}</p>
        <img :src="(store.image)" alt="loading" width="400" height="350">
        <p>Äänet: {{ store.currentIssue.score }} <button @click="upvote">Äänestä</button></p>
    </div>
</template>

<script setup>
import { useCounterStore } from '@/stores/counter';
    const props = defineProps(['id'])
    const store = useCounterStore()
    function upvote() {
        fetch(`http://localhost:5173/api/posts/${store.currentIssue.id}/upvote`, {
            method: "POST"
        })
        .then((res) => {
            if (res.ok) {
                store.currentIssue.score = store.currentIssue.score + 1
                store.markers.map((ele) => ele.id === store.currentIssue.id ? {...ele, 'id': ele.id + 1} : ele)
            }
        })
        .catch((e) => console.log("vituiks meni"))
    }

</script>