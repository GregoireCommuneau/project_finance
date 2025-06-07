<template>
  <div class="mt-10">
    <h2 class="text-2xl font-semibold mb-4">My Watchlist</h2>
    <div v-if="watchlist.length" class="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      <CompanyCard
        v-for="c in watchlist"
        :key="c.name"
        :company="c"
        @click="$emit('select', c)"
      />
    </div>
    <p v-else class="text-gray-500">No companies in watchlist yet.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CompanyCard from './CompanyCard.vue'

const watchlist = ref([])

onMounted(() => {
  const list = JSON.parse(localStorage.getItem('watchlist') || '[]')
  watchlist.value = list
})
</script>
