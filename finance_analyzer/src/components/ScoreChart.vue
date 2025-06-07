<template>
  <div class="bg-white rounded-2xl shadow p-4 w-full max-w-sm mx-auto">
    <!-- Header: Nom + secteur -->
    <div class="flex justify-between items-center mb-2">
      <div>
        <h2 class="text-lg font-bold text-gray-800">{{ company.name }}</h2>
        <p class="text-sm text-gray-500">{{ company.sector }}</p>
      </div>
      <div class="text-right">
        <span
          class="inline-block text-xs font-semibold bg-blue-100 text-blue-800 px-2 py-1 rounded-full"
        >
          PE Score: {{ score.toFixed(1) }}/100
        </span>
      </div>
    </div>

    <!-- Prix et tendance -->
    <PriceTrend :history="company.priceHistory" :price="company.price" />

    <!-- Indicateurs clés -->
    <ul class="mt-4 space-y-1 text-sm text-gray-600">
      <li><span class="font-medium text-gray-800">EBITDA Margin:</span> {{ company.ebitdaMargin }}%</li>
      <li><span class="font-medium text-gray-800">Debt / EBITDA:</span> {{ company.debtToEbitda }}</li>
      <li><span class="font-medium text-gray-800">EV / EBITDA:</span> {{ evToEbitda.toFixed(1) }}</li>
      <li><span class="font-medium text-gray-800">Growth:</span> {{ company.growth }}%</li>
      <li><span class="font-medium text-gray-800">Revenue:</span> {{ company.revenue }} M€</li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PriceTrend from './PriceTrend.vue'

const props = defineProps({
  company: Object
})

const normalize = (val, min, max) => {
  if (val == null || isNaN(val)) return 0
  return Math.max(0, Math.min(100, ((val - min) / (max - min)) * 100))
}

const evToEbitda = computed(() => {
  const c = props.company
  return (c.price * c.sharesOutstanding + c.netDebt) / c.ebitda
})

const score = computed(() => {
  const c = props.company

  const ebitdaScore = normalize(c.ebitdaMargin, 0, 50)
  const debtScore = normalize(10 - c.debtToEbitda, 0, 10)
  const growthScore = normalize(c.growth, -20, 50)
  const revenueScore = normalize(c.revenue, 0, 500)
  const evScore = normalize(30 - evToEbitda.value, 0, 30)

  return (
    0.25 * ebitdaScore +
    0.2 * debtScore +
    0.15 * growthScore +
    0.15 * revenueScore +
    0.25 * evScore
  )
})
</script>
