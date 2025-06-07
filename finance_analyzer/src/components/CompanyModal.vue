<template>
  <div
    v-if="company"
    class="fixed inset-0 z-50 bg-black bg-opacity-40 backdrop-blur-sm flex items-center justify-center"
  >
    <div class="bg-white rounded-lg p-6 shadow-xl max-w-2xl w-full relative animate-fade-in">
      <button
        @click="$emit('close')"
        class="absolute top-2 right-3 text-gray-500 hover:text-black text-2xl font-bold"
      >
        &times;
      </button>

      <h2 class="text-2xl font-semibold mb-1">{{ company.name }}</h2>
      <p class="text-gray-600 mb-4">{{ company.sector }}</p>

      <div class="grid grid-cols-2 gap-4 text-sm">
        <p><strong>Revenue:</strong> ${{ company.revenue.toFixed(1) }}M</p>
        <p><strong>EBITDA Margin:</strong> {{ company.ebitdaMargin.toFixed(1) }}%</p>
        <p><strong>Debt/EBITDA:</strong> {{ company.debtToEbitda.toFixed(2) }}</p>
        <p><strong>Growth:</strong> {{ company.growth.toFixed(1) }}%</p>
      </div>

      <div class="mt-6">
        <RadarChart :company="company" />
      </div>

      <div class="mt-6 text-right">
        <button class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Add to Watchlist
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import RadarChart from './RadarChart.vue'
const props = defineProps({ company: Object })
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>
