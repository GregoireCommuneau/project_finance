<template>
  <div class="bg-white p-4 rounded-lg shadow mb-6 grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
    <div class="mb-6 p-4 border rounded-xl">
      <h2 class="text-lg font-semibold mb-2">Filters</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label>
          Minimum growth (%):
          <input type="number" v-model.number="filters.minGrowth" class="border p-1 rounded w-full" />
        </label>
        <label>
          Max Debt / EBITDA:
          <input type="number" v-model.number="filters.maxDebt" class="border p-1 rounded w-full" />
        </label>
        <label>
          Minimum revenue (M€):
          <input type="number" v-model.number="filters.minRevenue" class="border p-1 rounded w-full" />
        </label>
        <label>
          Minimum EBITDA margin (%):
          <input type="number" v-model.number="filters.minMargin" class="border p-1 rounded w-full" />
        </label>
        <label>
          Sector:
          <select v-model="filters.sector" class="border p-1 rounded w-full">
            <option value="">All</option>
            <option value="Cybersecurity">Cybersecurity</option>
            <option value="SaaS">SaaS</option>
          </select>
        </label>
      </div>
    </div>
  </div>

  
</template>

<script setup>
import { defineProps } from 'vue'
const props = defineProps({
  filters: Object
})
</script>