<template>
  <div class="font-sans text-gray-800">
    <main class="p-6">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { provide } from 'vue'
import { companies } from './data/companies' 

provide('allCompanies', companies)
</script>
