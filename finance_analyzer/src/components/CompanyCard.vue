<template>
  <div
    class="relative bg-white rounded-xl shadow-md p-5 transition hover:shadow-lg border hover:border-blue-500 cursor-pointer"
    @click="$emit('click')"
  >
    <!-- Score badge (top-right corner) with tooltip -->
    <div
      :class="scoreBadgeClass"
      class="absolute top-3 right-3 text-xs px-2 py-1 rounded font-semibold group"
      @click.stop
    >
      <span>{{ scoreLabel }}</span>
      <div
        v-if="scoreTooltip"
        class="absolute z-10 hidden group-hover:block bg-black text-white text-xs rounded px-2 py-1 mt-1 right-0 max-w-[240px] w-max whitespace-pre-line"
      >
        {{ scoreTooltip }}
      </div>
    </div>

    <!-- Company header -->
    <div class="mb-4">
      <h3 class="text-lg font-bold text-gray-800">{{ company.name || 'Unknown' }}</h3>
      <p class="text-sm text-gray-500">{{ company.sector || 'Unknown sector' }}</p>
    </div>

    <!-- Metrics in 2-column layout -->
    <div class="grid grid-cols-2 gap-y-3 gap-x-4 text-sm text-gray-700">
      <div>
        <span class="block font-medium text-gray-500">Revenue</span>
        <span :class="valueColor(company.revenue)">
          {{ formatNumber(company.revenue) }}
        </span>
      </div>

      <div>
        <span class="block font-medium text-gray-500">EBITDA Margin</span>
        <span :class="valueColor(company.ebitdaMargin)">
          {{ formatPercent(company.ebitdaMargin) }}
        </span>
      </div>

      <div>
        <span class="block font-medium text-gray-500">Debt / EBITDA</span>
        <span :class="valueColor(company.debtToEbitda)">
          {{ debtToEbitdaFormatted }}
        </span>
      </div>

      <div>
        <span class="block font-medium text-gray-500">Growth</span>
        <span :class="growthColor(company.growth)">
          {{ formatPercent(company.growth) }}
        </span>
      </div>
    </div>

    <!-- Price trend -->
    <PriceTrend v-if="company.price !== null" :price="company.price" :history="company.priceHistory" :range="range" />
    <div v-else>
      <p class="text-center text-gray-500 mt-2">Price trend data not available</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PriceTrend from './PriceTrend.vue'

const props = defineProps({
  company: Object,
  range: Object,
  score: [Number, String],
  missingFields: Array
})

// Helper function to check if a value is a valid number
const isValidNumber = (value) => {
  if (value === null || value === undefined || value === '') return false
  const num = Number(value)
  return !isNaN(num) && isFinite(num)
}

// Helper function to format numbers
function formatNumber(value, unit = '', decimals = 1) {
  if (value == null || isNaN(value)) return '-'

  const abs = Math.abs(value)

  if (abs >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(decimals)} B ${unit}`
  if (abs >= 1_000_000) return `${(value / 1_000_000).toFixed(decimals)} M ${unit}`
  if (abs >= 1_000) return `${(value / 1_000).toFixed(decimals)} k ${unit}`

  return `${value.toFixed(decimals)} ${unit}`
}

// Helper function to format percentages
const formatPercent = (value) => {
  return isValidNumber(value) ? `${Number(value).toFixed(2)}%` : 'N/A'
}

// Whether score is valid (all fields present)
const hasValidScore = computed(() => {
  const s = Number(props.score)
  return isValidNumber(s) && s >= 0 && s <= 100 && (!props.missingFields || props.missingFields.length === 0)
})

// Score value to display
const scoreLabel = computed(() => {
  if (!hasValidScore.value) return 'Score: N/A'
  return 'Score: ' + Math.round(props.score)
})

// Tooltip content
const scoreTooltip = computed(() => {
  if (hasValidScore.value) return 'Score based on financial and price trend metrics'
  if (props.missingFields?.length) {
    return 'Missing fields:\n' + props.missingFields.map(f => `• ${f}`).join('\n')
  }
  return 'Missing data for score computation'
})

// Score badge class depending on value or missing fields
const scoreBadgeClass = computed(() => {
  if (!hasValidScore.value) return 'bg-gray-300 text-gray-600'
  const s = Number(props.score)
  if (s >= 80) return 'bg-green-500 text-white'
  if (s >= 60) return 'bg-yellow-500 text-white'
  return 'bg-red-500 text-white'
})

// Format Debt/EBITDA safely
const debtToEbitdaFormatted = computed(() => {
  const val = Number(props.company?.debtToEbitda)
  return isValidNumber(val) ? val.toFixed(2) : 'N/A'
})

// Growth color based on thresholds
const growthColor = (growth) => {
  if (!isValidNumber(growth)) return 'text-gray-500'
  if (growth > 10) return 'text-green-600'
  if (growth > 5) return 'text-yellow-600'
  return 'text-red-600'
}

// Generic color fallback
const valueColor = (val) => {
  return isValidNumber(val) ? 'text-gray-900' : 'text-gray-500'
}

</script>
