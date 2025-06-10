<template>
  <div class="container mx-auto px-4 py-8">
    <div class="sticky top-0 z-40 bg-white py-4 shadow-md mb-6">
      <!-- Filter panel -->
      <FilterPanel
        :filters="filters"
        :sectors="sectors"
        :onReset="resetFilters"
        :onExport="exportToCSV"
        :onReload="() => loadCompanies(true)"
        :totalCount="companies.length"
        :filteredCount="filteredCompanies.length"
      />

      <!-- Controls: Time range and sort selection -->
      <div class="flex flex-wrap md:flex-nowrap items-center justify-between mt-4 px-6 gap-4">
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
        <div>
          <select v-model="sortBy" class="border border-gray-300 px-3 py-2 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none">
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
import { ref, reactive, computed, onMounted } from 'vue'
import { companies, loadCompanies } from '../data/companies'
import CompanyCard from './CompanyCard.vue'
import CompanyModal from './CompanyModal.vue'
import FilterPanel from './FilterPanel.vue'
import { computeSectorScore } from '../utils/scoringService'
import { sectorProfiles } from '../utils/sectorProfiles'
import { normalize } from '../utils/financeUtils'

// Reactive filters object
const filters = reactive({
  minGrowth: null,
  maxDebt: null,
  minRevenue: null,
  minMargin: null,
  sector: '',
  peaEligible: false
})

// Available time ranges for trend computation
const globalRanges = [
  { label: '1M', length: 21 },
  { label: '6M', length: 126 },
  { label: '1Y', length: 252 }
]
const globalRange = ref(globalRanges[0])
const selectedCompany = ref(null)
const sortBy = ref('')

// Load companies on component mount
onMounted(() => {
  loadCompanies().then(() => {
    companies.forEach(c => {
      c.trend = computeTrend(c.priceHistory)
    })
  })
})

// List of unique sectors
const sectors = computed(() => {
  const all = companies.map(c => c.sector)
  return [...new Set(all)].filter(Boolean).sort()
})

// Countries eligible for PEA (Plan d'Épargne en Actions)
const peaEligibleCountries = [
  'France', 'Germany', 'Italy', 'Spain', 'Netherlands', 'Belgium', 'Austria',
  'Portugal', 'Greece', 'Finland', 'Ireland', 'Luxembourg', 'Denmark',
  'Sweden', 'Norway', 'Iceland', 'Liechtenstein', 'Switzerland',
  'FR', 'DE', 'IT', 'ES', 'NL', 'BE', 'AT', 'PT', 'GR', 'FI', 'IE', 'LU',
  'DK', 'SE', 'NO', 'IS', 'LI', 'CH'
]

// Reset all filters
function resetFilters() {
  filters.minGrowth = null
  filters.maxDebt = null
  filters.minRevenue = null
  filters.minMargin = null
  filters.sector = ''
  filters.peaEligible = false
}

// Check if a value is a clean, usable number
function isValidNumber(value) {
  if (value === null || value === undefined || value === '') return false
  const num = Number(value)
  return !isNaN(num) && isFinite(num)
}

// Identify which fields are missing or invalid for a company
function missingFields(company) {
  const sector = company.sector || 'default'
  const profile = sectorProfiles[sector] || sectorProfiles['default']
  const requiredMetrics = profile.metrics

  return requiredMetrics.filter(metric => {
    const value = company[metric]
    return value === undefined || value === null || isNaN(Number(value))
  })
}

// Compute the overall score for a company based on several metrics
function computeScore(c) {
  return computeSectorScore(c)
}

// Export filtered companies to CSV
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


// Apply filters to companies list
const filteredCompanies = computed(() => {
  return companies.filter(c => {
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

// Sort filtered companies based on selected field
const sortedCompanies = computed(() => {
  // Create a copy of the filtered companies
  let companiesToSort = [...filteredCompanies.value];

  // If sorting by score, exclude companies with a score of "N/A"
  if (sortBy.value === 'score') {
    companiesToSort = companiesToSort.filter(company => computeScore(company) !== 'N/A');
  }

  // Sort the remaining companies
  return companiesToSort.sort((a, b) => {
    const aScore = computeScore(a);
    const bScore = computeScore(b);

    if (aScore === 'N/A' || bScore === 'N/A') return 0;
    if (sortBy.value === 'score') return Number(bScore) - Number(aScore);
    if (sortBy.value === 'revenue') return Number(b.revenue) - Number(a.revenue);
    if (sortBy.value === 'growth') return Number(b.growth) - Number(a.growth);
    if (sortBy.value === 'debt') return Number(a.debtToEbitda) - Number(b.debtToEbitda);

    return 0;
  });
});


// Helper function to compute trend
function computeTrend(history) {
  if (!Array.isArray(history) || history.length < 2) return 0
  const start = Number(history[0])
  const end = Number(history[history.length - 1])
  if (!isFinite(start) || !isFinite(end) || start === 0) return 0
  return normalize(((end - start) / start) * 100, -50, 50)
}
</script>
