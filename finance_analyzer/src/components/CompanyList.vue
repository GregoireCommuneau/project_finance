<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Filters -->
    <div class="bg-white p-6 rounded-xl shadow-md mb-8 grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-1">Minimum growth (%)</label>
        <input type="number" v-model.number="filters.minGrowth" class="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none" />
      </div>
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-1">Max Debt / EBITDA</label>
        <input type="number" v-model.number="filters.maxDebt" class="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none" />
      </div>
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-1">Minimum revenue (M€)</label>
        <input type="number" v-model.number="filters.minRevenue" class="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none" />
      </div>
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-1">Minimum EBITDA margin (%)</label>
        <input type="number" v-model.number="filters.minMargin" class="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none" />
      </div>
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-1">Sector</label>
        <select v-model="filters.sector" class="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none">
          <option value="">All</option>
          <option v-for="s in sectors" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
      <div class="flex items-end gap-2">
        <button @click="resetFilters" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition">
          Reset
        </button>
        <button @click="exportToCSV" class="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg text-sm font-medium transition">
          Export CSV
        </button>
        <button @click="loadCompanies(true)" class="px-4 py-2 bg-green-600 text-white hover:bg-green-700 rounded-lg text-sm font-medium transition">
          Reload Fresh
        </button>
      </div>
    </div>

    <!-- Sorter -->
    <div class="flex justify-end mb-6">
      <select v-model="sortBy" class="border border-gray-300 px-3 py-2 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none">
        <option value="">Sort by...</option>
        <option value="score">PE Score</option>
        <option value="revenue">Revenue</option>
        <option value="growth">Growth</option>
        <option value="debt">Debt/EBITDA</option>
      </select>
    </div>

    <!-- Global Range Control -->
    <div class="flex justify-center mb-6 gap-2">
      <button
        v-for="range in globalRanges"
        :key="range.label"
        @click="globalRange = range"
        :class="[
          'px-3 py-1 rounded text-sm font-medium border',
          globalRange.label === range.label
            ? 'bg-blue-600 text-white border-blue-600'
            : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
        ]"
          >
        {{ range.label }}
      </button>
    </div>

    <!-- Companies -->
    <CompanyModal :company="selectedCompany" @close="selectedCompany = null" />
    <div class="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      <CompanyCard
        v-for="c in sortedCompanies"
        :key="c.name"
        :company="c"
        :range="globalRange"
        @click="selectedCompany = c"
      />
    </div>

    <p v-if="!sortedCompanies.length" class="text-center text-gray-500 mt-8 text-lg">
      No companies match your filters.
    </p>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { companies, loadCompanies } from '../data/companies'
import CompanyCard from './CompanyCard.vue'
import CompanyModal from './CompanyModal.vue'

const filters = reactive({
  minGrowth: 0,
  maxDebt: Infinity,
  minRevenue: 0,
  minMargin: 0,
  sector: ''
})

const globalRanges = [
  { label: '1M', length: 21 },
  { label: '6M', length: 126 },
  { label: '1Y', length: 252 }
]
const globalRange = ref(globalRanges[0])

const selectedCompany = ref(null)
const sortBy = ref('')

onMounted(() => loadCompanies())

const sectors = computed(() => {
  const all = companies.map(c => c.sector)
  return [...new Set(all)].filter(Boolean).sort()
})

function resetFilters() {
  filters.minGrowth = 0
  filters.maxDebt = Infinity
  filters.minRevenue = 0
  filters.minMargin = 0
  filters.sector = ''
}

function normalize(val, min, max) {
  if (val == null || isNaN(val)) return 0
  return Math.max(0, Math.min(100, ((val - min) / (max - min)) * 100))
}

function computeTrend(history) {
  if (!Array.isArray(history) || history.length < 2) return 0
  const start = history[0]
  const end = history[history.length - 1]
  return normalize(((end - start) / start) * 100, -50, 50)
}

function computeScore(c) {
  const ebitdaScore = normalize(c.ebitdaMargin, 0, 50)
  const debtScore = normalize(10 - c.debtToEbitda, 0, 10)
  const growthScore = normalize(c.growth, -20, 50)
  const revenueScore = normalize(c.revenue, 0, 500)
  const evToEbitda = (c.price * c.sharesOutstanding + c.netDebt) / c.ebitda
  const evScore = normalize(30 - evToEbitda, 0, 30)
  const trendScore = computeTrend(c.priceHistory)

  return (
    0.25 * ebitdaScore +
    0.2 * debtScore +
    0.15 * growthScore +
    0.15 * revenueScore +
    0.15 * evScore +
    0.1 * trendScore
  )
}

const filteredCompanies = computed(() => {
  return companies.filter(c =>
    c.growth >= filters.minGrowth &&
    c.debtToEbitda <= filters.maxDebt &&
    c.revenue >= filters.minRevenue &&
    c.ebitdaMargin >= filters.minMargin &&
    (filters.sector === '' || c.sector === filters.sector)
  )
})

const sortedCompanies = computed(() => {
  return [...filteredCompanies.value].sort((a, b) => {
    if (sortBy.value === 'score') return computeScore(b) - computeScore(a)
    if (sortBy.value === 'revenue') return b.revenue - a.revenue
    if (sortBy.value === 'growth') return b.growth - a.growth
    if (sortBy.value === 'debt') return a.debtToEbitda - b.debtToEbitda
    return 0
  })
})

function exportToCSV() {
  const rows = [
    ['Name', 'Sector', 'Revenue', 'EBITDA Margin', 'Debt/EBITDA', 'Growth', 'PE Score', 'Price Trend']
  ]
  filteredCompanies.value.forEach(c => {
    rows.push([
      c.name,
      c.sector,
      c.revenue,
      c.ebitdaMargin,
      c.debtToEbitda,
      c.growth,
      computeScore(c),
      computeTrend(c.priceHistory).toFixed(1) + '%'
    ])
  })
  const csvContent = rows.map(e => e.join(',')).join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'filtered_companies.csv'
  link.click()
}
</script>
