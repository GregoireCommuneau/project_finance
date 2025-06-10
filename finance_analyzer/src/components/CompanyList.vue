<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Sticky header with filters, sort, and range -->
    <div
      class="sticky top-0 z-40 bg-white shadow-md border-b border-gray-200 mb-6 transition-transform duration-300"
      :class="{ '-translate-y-full': !showHeader, 'translate-y-0': showHeader }"
    >
      <div class="flex flex-col sm:flex-row flex-wrap gap-4 px-4 py-2 items-center justify-between">
        <!-- Filter panel -->
        <FilterPanel
          :filters="filters"
          :sectors="sectors"
          :onReset="resetFilters"
          :onExport="exportToCSV"
          :totalCount="companies.length"
          :filteredCount="filteredCompanies.length"
        />

        <!-- Controls: Time range and sort selection -->
        <div class="flex flex-wrap sm:flex-nowrap items-center gap-3">
          <div class="flex gap-2">
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
          <select
            v-model="sortBy"
            class="border border-gray-300 px-3 py-2 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
          >
            <option value="">Sort by...</option>
            <option value="score">PE Score</option>
            <option value="revenue">Revenue</option>
            <option value="growth">Growth</option>
            <option value="debt">Debt/EBITDA</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Company modal and cards -->
    <CompanyModal :company="selectedCompany" :range="globalRange" @close="selectedCompany = null" />
    <div class="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 mt-6">
      <CompanyCard
        v-for="c in sortedCompanies"
        :key="c.name"
        :company="c"
        :score="computeScore(c)"
        :missingFields="missingFields(c)"
        :scoreTooltip="missingFields(c).length ? 'Missing: ' + missingFields(c).join(', ') : ''"
        :range="globalRange"
        @click="selectedCompany = c"
      />
    </div>

    <!-- Empty state -->
    <p v-if="!sortedCompanies.length" class="text-center text-gray-500 mt-8 text-lg">
      No companies match your filters.
    </p>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useCachedData } from '../composables/useCachedData'
import CompanyCard from './CompanyCard.vue'
import CompanyModal from './CompanyModal.vue'
import FilterPanel from './FilterPanel.vue'
import { computeSectorScore } from '../utils/scoringService'
import { sectorProfiles } from '../utils/sectorProfiles'
import { normalize } from '../utils/financeUtils'

const { data: companies, loading } = useCachedData()

const filters = reactive({
  minGrowth: null,
  maxDebt: null,
  minRevenue: null,
  minMargin: null,
  sector: '',
  peaEligible: false
})

const globalRanges = [
  { label: '1M', length: 21 },
  { label: '6M', length: 126 },
  { label: '1Y', length: 252 }
]
const globalRange = ref(globalRanges[0])
const selectedCompany = ref(null)
const sortBy = ref('')
const showHeader = ref(true)
let lastScroll = 0

function handleScroll() {
  const current = window.scrollY
  showHeader.value = current < lastScroll || current < 50
  lastScroll = current
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const sectors = computed(() => {
  const all = companies.value.map(c => c.sector)
  return [...new Set(all)].filter(Boolean).sort()
})

const peaEligibleCountries = [
  'France', 'Germany', 'Italy', 'Spain', 'Netherlands', 'Belgium', 'Austria',
  'Portugal', 'Greece', 'Finland', 'Ireland', 'Luxembourg', 'Denmark',
  'Sweden', 'Norway', 'Iceland', 'Liechtenstein', 'Switzerland',
  'FR', 'DE', 'IT', 'ES', 'NL', 'BE', 'AT', 'PT', 'GR', 'FI', 'IE', 'LU',
  'DK', 'SE', 'NO', 'IS', 'LI', 'CH'
]

function resetFilters() {
  filters.minGrowth = null
  filters.maxDebt = null
  filters.minRevenue = null
  filters.minMargin = null
  filters.sector = ''
  filters.peaEligible = false
}

function isValidNumber(value) {
  if (value === null || value === undefined || value === '') return false
  const num = Number(value)
  return !isNaN(num) && isFinite(num)
}

function missingFields(company) {
  const sector = company.sector || 'default'
  const profile = sectorProfiles[sector] || sectorProfiles['default']
  const requiredMetrics = profile.metrics
  return requiredMetrics.filter(metric => {
    const value = company[metric]
    return value === undefined || value === null || isNaN(Number(value))
  })
}

function computeScore(c) {
  return computeSectorScore(c)
}

function exportToCSV() {
  const rows = [
    ['Name', 'Sector', 'Country', 'Revenue', 'EBITDA Margin (%)', 'Debt/EBITDA', 'Growth (%)', 'PE Score', 'Price Trend (%)']
  ]
  filteredCompanies.value.forEach(c => {
    const score = computeScore(c)
    const trend = computeTrend(c.priceHistory)
    rows.push([
      `"${c.name}"`,
      `"${c.sector}"`,
      `"${c.country || 'Unknown'}"`,
      isValidNumber(c.revenue) ? c.revenue.toFixed(0) : '',
      isValidNumber(c.ebitdaMargin) ? c.ebitdaMargin.toFixed(2) : '',
      isValidNumber(c.debtToEbitda) ? c.debtToEbitda.toFixed(2) : '',
      isValidNumber(c.growth) ? c.growth.toFixed(2) : '',
      typeof score === 'number' || !isNaN(parseFloat(score)) ? score : 'N/A',
      isValidNumber(trend) ? trend.toFixed(1) : 'N/A'
    ])
  })
  const csvContent = '\uFEFF' + rows.map(row => row.join(',')).join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'filtered_companies.csv'
  link.click()
}

const filteredCompanies = computed(() => {
  return companies.value.filter(c => {
    const passesFilters =
      (filters.minGrowth === null || Number(c.growth) >= filters.minGrowth) &&
      (filters.maxDebt === null || Number(c.debtToEbitda) <= filters.maxDebt) &&
      (filters.minRevenue === null || Number(c.revenue) >= filters.minRevenue) &&
      (filters.minMargin === null || Number(c.ebitdaMargin) >= filters.minMargin) &&
      (filters.sector === '' || c.sector === filters.sector)
    const raw = (c.country || c.exchangeCountry || '').trim().toUpperCase()
    if (filters.peaEligible) {
      return passesFilters && peaEligibleCountries.includes(raw)
    }
    return passesFilters
  })
})

const sortedCompanies = computed(() => {
  let companiesToSort = [...filteredCompanies.value]
  if (sortBy.value === 'score') {
    companiesToSort = companiesToSort.filter(company => computeScore(company) !== 'N/A')
  }
  return companiesToSort.sort((a, b) => {
    const aScore = computeScore(a)
    const bScore = computeScore(b)
    if (aScore === 'N/A' || bScore === 'N/A') return 0
    if (sortBy.value === 'score') return Number(bScore) - Number(aScore)
    if (sortBy.value === 'revenue') return Number(b.revenue) - Number(a.revenue)
    if (sortBy.value === 'growth') return Number(b.growth) - Number(a.growth)
    if (sortBy.value === 'debt') return Number(a.debtToEbitda) - Number(b.debtToEbitda)
    return 0
  })
})

function computeTrend(history) {
  if (!Array.isArray(history) || history.length < 2) return 0
  const start = Number(history[0])
  const end = Number(history[history.length - 1])
  if (!isFinite(start) || !isFinite(end) || start === 0) return 0
  return normalize(((end - start) / start) * 100, -50, 50)
}
</script>
