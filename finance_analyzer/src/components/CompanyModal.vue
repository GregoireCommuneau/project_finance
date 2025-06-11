<template>
  <div
    v-if="company"
    class="fixed inset-0 z-50 bg-black bg-opacity-40 backdrop-blur-sm flex items-center justify-center"
  >
    <div
      class="bg-white rounded-lg p-6 shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto relative animate-fade-in"
    >
      <button
        @click="$emit('close')"
        class="absolute top-2 right-3 text-gray-500 hover:text-black text-2xl font-bold"
      >
        &times;
      </button>

      <h2 class="text-2xl font-semibold mb-1">{{ company.name }}</h2>
      <p class="text-gray-600 mb-4">{{ company.sector }}</p>

      <div class="grid grid-cols-2 gap-4 text-sm text-gray-800">
        <p><strong>Revenue:</strong> {{ formatNumber(company.revenue) }}</p>
        <p><strong>EBITDA:</strong> {{ formatNumber(company.ebitda) }}</p>
        <p><strong>EBITDA Margin:</strong> {{ formatPercent(company.ebitdaMargin) }}</p>
        <p><strong>EBITDA Growth:</strong> {{ formatPercent(company.ebitdaGrowth) }}</p>
        <p><strong>Debt/EBITDA:</strong> {{ formatNumber(company.debtToEbitda, '', 2) }}</p>
        <p><strong>Net Debt:</strong> {{ formatNumber(company.netDebt, '€') }}</p>
        <p><strong>ROE:</strong> {{ formatPercent(company.roe) }}</p>
        <p><strong>Revenue / EV:</strong> {{ formatNumber(company.revenueToEV, '', 3) }}</p>
        <p><strong>Growth:</strong> {{ formatPercent(company.growth) }}</p>
      </div>

      <div class="mt-6">
        <RadarChart
          :company="company"
          :allCompanies="effectiveAllCompanies"
        />
      </div>
      <div class="mt-2 text-sm text-gray-600 flex justify-center gap-4">
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 inline-block rounded-full bg-indigo-600"></span>
          <span>Entreprise</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 inline-block rounded-full border-2 border-blue-400"></span>
          <span>Moyenne sectorielle</span>
        </div>
      </div>

      <div class="mt-6">
        <PriceTrend
          :price="company.price"
          :history="company.priceHistory"
          :range="range"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject, computed } from 'vue'
import RadarChart from './RadarChart.vue'
import PriceTrend from './PriceTrend.vue'
import { formatNumber, formatPercent } from '@/utils/formatting'

const props = defineProps({
  company: Object,
  range: Object,
  allCompanies: Array
})

const injectedCompanies = inject('allCompanies')
const effectiveAllCompanies = computed(() => props.allCompanies || injectedCompanies)
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
