<template>
  <div
    class="relative bg-white rounded-xl shadow-md p-5 transition hover:shadow-lg border hover:border-blue-500 cursor-pointer"
    @click="$emit('click')"
  >
    <!-- PE Score badge (top-right corner) -->
    <div
      :class="[
        'absolute top-3 right-3 text-xs px-2 py-1 rounded font-semibold',
        score.value >= 80 ? 'bg-green-500 text-white'
        : score.value >= 60 ? 'bg-yellow-500 text-white'
        : 'bg-red-500 text-white'
      ]"
    >
      Score: {{ score }}
    </div>

    <!-- Company header -->
    <div class="mb-4">
      <h3 class="text-lg font-bold text-gray-800">{{ company.name }}</h3>
      <p class="text-sm text-gray-500">{{ company.sector }}</p>
    </div>

    <!-- Metrics in 2-column layout -->
    <div class="grid grid-cols-2 gap-y-3 gap-x-4 text-sm text-gray-700">
      <!-- Revenue -->
      <div>
        <span class="block font-medium text-gray-500">Revenue</span>
        <span class="text-gray-900">${{ company.revenue.toFixed(1) }}M</span>
      </div>

      <!-- EBITDA Margin -->
      <div>
        <span class="block font-medium text-gray-500">EBITDA Margin</span>
        <span class="text-gray-900">{{ company.ebitdaMargin.toFixed(1) }}%</span>
      </div>

      <!-- Debt/EBITDA -->
      <div>
        <span class="block font-medium text-gray-500">Debt/EBITDA</span>
        <span class="text-gray-900">{{ company.debtToEbitda.toFixed(2) }}</span>
      </div>

      <!-- Growth with conditional color -->
      <div>
        <span class="block font-medium text-gray-500">Growth</span>
        <span
          :class="{
            'text-green-600': company.growth > 10,
            'text-yellow-600': company.growth > 5 && company.growth <= 10,
            'text-red-600': company.growth <= 5
          }"
        >
          {{ company.growth.toFixed(1) }}%
        </span>
      </div>
    </div>
    <!-- Price trend (graph + % + prix brut) -->
    <PriceTrend :price="company.price" :history="company.priceHistory" :range="range" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PriceTrend from './PriceTrend.vue'

const props = defineProps({
  company: Object,
  range: Object
})

const normalize = (val, min, max) => {
  if (val == null || isNaN(val)) return 0
  return Math.max(0, Math.min(100, ((val - min) / (max - min)) * 100))
}

const score = computed(() => {
  const c = props.company

  const ebitdaScore = normalize(c.ebitdaMargin, 0, 50)
  const debtScore = normalize(10 - c.debtToEbitda, 0, 10)
  const growthScore = normalize(c.growth, -20, 50)
  const revenueScore = normalize(c.revenue, 0, 500)
  const evToEbitda = (c.price * c.sharesOutstanding + c.netDebt) / c.ebitda
  const evScore = normalize(30 - evToEbitda, 0, 30)

  return (
    0.25 * ebitdaScore +
    0.2 * debtScore +
    0.15 * growthScore +
    0.15 * revenueScore +
    0.25 * evScore
  )
})
</script>
