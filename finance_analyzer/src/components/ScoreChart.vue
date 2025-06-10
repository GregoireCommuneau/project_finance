<template>
  <div class="bg-white rounded-2xl shadow p-4 w-full max-w-sm mx-auto">
    <!-- Header: Name + Sector -->
    <div class="flex justify-between items-center mb-2">
      <div>
        <h2 class="text-lg font-bold text-gray-800">{{ company.name }}</h2>
        <p class="text-sm text-gray-500">{{ company.sector }}</p>
      </div>
      <div class="text-right">
        <span
          :class="badgeClass"
          class="inline-block text-xs font-semibold px-2 py-1 rounded-full"
        >
          {{ badgeText }}
        </span>
        <p class="text-xs text-gray-500 mt-1 max-w-xs">
          Score based on EBITDA margin, debt, growth, revenue and valuation metrics.
        </p>
      </div>
    </div>

    <!-- Price and trend -->
    <PriceTrend :history="company.priceHistory" :price="company.price" />

    <!-- Key metrics -->
    <ul class="mt-4 space-y-1 text-sm text-gray-600">
      <li>
        <span class="font-medium text-gray-800">EBITDA Margin:</span>
        {{ fmt(company.ebitdaMargin) }}%
      </li>
      <li>
        <span class="font-medium text-gray-800">Debt / EBITDA:</span>
        {{ fmt(company.debtToEbitda) }}
      </li>
      <li>
        <span class="font-medium text-gray-800">EV / EBITDA:</span>
        {{ evToEbitdaFormatted }}
      </li>
      <li>
        <span class="font-medium text-gray-800">Growth:</span>
        {{ fmt(company.growth) }}%
      </li>
      <li>
        <span class="font-medium text-gray-800">Revenue:</span>
        {{ fmt(company.revenue) }} M€
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PriceTrend from './PriceTrend.vue'
import { fmt, computeScore, computeEVtoEbitda } from '@/utils/financeUtils'

const props = defineProps({ company: Object })

const evToEbitda = computed(() => computeEVtoEbitda(props.company))

const score = computed(() => {
  return computeScore(props.company, evToEbitda.value)
})

const evToEbitdaFormatted = computed(() => {
  return evToEbitda.value != null ? evToEbitda.value.toFixed(1) : '–'
})

const badgeText = computed(() =>
  score.value == null ? 'Incomplete Data' : `Fundamental Score: ${score.value.toFixed(1)}/100`
)

const badgeClass = computed(() => {
  const s = score.value
  if (s == null) return 'bg-gray-100 text-gray-600'
  if (s >= 80) return 'bg-green-100 text-green-800'
  if (s >= 50) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
})

</script>
