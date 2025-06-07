<template>
  <main class="p-6">
    <h1 class="text-3xl font-bold mb-4">PE Target Screener</h1>
    <CompanyList />
  </main>

  <div class="bg-red-500 text-white p-4 rounded">
    If this is NOT red with white text, Tailwind is broken.
  </div>
</template>

<script setup>
import CompanyList from './components/CompanyList.vue'
</script>