<template>
  <div class="mx-auto max-w-[1440px] px-2 py-4">
    <!-- Sticky header wrapper -->
    <div class="sticky top-0 z-40 bg-white shadow-md border-b border-gray-200 overflow-hidden transition-all duration-300"
         :class="showHeader ? 'max-h-[1000px]' : 'max-h-[40px]'">
      <div v-if="showHeader" class="px-4 py-2">
        <!-- Contenu visible uniquement quand le header est ouvert -->
        <div class="flex flex-col sm:flex-row flex-wrap gap-4 items-center justify-between">
          <FilterPanel
            :filters="filters"
            :sectors="sectors"
            :onReset="resetFilters"
            :onExport="exportToCSV"
            :totalCount="companies.length"
            :filteredCount="filteredCompanies.length"
          />
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

      <!-- Toggle arrow -->
      <div class="flex justify-center items-center bg-white border-t border-gray-200">
        <button
          @click="showHeader = !showHeader"
          class="p-1 hover:bg-gray-100 transition rounded"
          aria-label="Toggle header"
        >
          <svg
            v-if="!showHeader"
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.24 4.24a.75.75 0 01-1.06 0L5.21 8.27a.75.75 0 01.02-1.06z"
              clip-rule="evenodd"
            />
          </svg>

          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              d="M14.77 12.79a.75.75 0 01-1.06-.02L10 9.06 6.29 12.77a.75.75 0 11-1.06-1.06l4.24-4.24a.75.75 0 011.06 0l4.24 4.24a.75.75 0 01-.02 1.06z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Pagination controls (top) -->
    <div v-if="totalPages > 1" class="flex justify-center items-center mb-4 gap-2 text-sm">
      <button
        @click="currentPage--"
        :disabled="currentPage === 1"
        class="px-3 py-1 rounded border border-gray-300 bg-white hover:bg-gray-100 disabled:opacity-50"
      >
        Prev
      </button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      <button
        @click="currentPage++"
        :disabled="currentPage === totalPages"
        class="px-3 py-1 rounded border border-gray-300 bg-white hover:bg-gray-100 disabled:opacity-50"
      >
        Next
      </button>
    </div>

    <!-- Company list -->
    <CompanyModal :company="selectedCompany" :range="globalRange" @close="selectedCompany = null" :allCompanies="companies" />
    <div class="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 mt-6">
      <CompanyCard
        v-for="c in paginatedCompanies"
        :key="c.name"
        :company="c"
        :score="computeScore(c)"
        :missingFields="missingFields(c)"
        :scoreTooltip="missingFields(c).length ? 'Missing: ' + missingFields(c).join(', ') : ''"
        :range="globalRange"
        @click="selectedCompany = c"
      />
    </div>

    <p v-if="!sortedCompanies.length" class="text-center text-gray-500 mt-8 text-lg">
      No companies match your filters.
    </p>

    <!-- Pagination controls (bottom) -->
    <div v-if="totalPages > 1" class="flex justify-center items-center mt-8 gap-2 text-sm">
      <button
        @click="currentPage--"
        :disabled="currentPage === 1"
        class="px-3 py-1 rounded border border-gray-300 bg-white hover:bg-gray-100 disabled:opacity-50"
      >
        Prev
      </button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      <button
        @click="currentPage++"
        :disabled="currentPage === totalPages"
        class="px-3 py-1 rounded border border-gray-300 bg-white hover:bg-gray-100 disabled:opacity-50"
      >
        Next
      </button>
    </div>
  </div>
</template>


<script setup>
import { ref, reactive, computed, watch} from 'vue'
import { useCachedData } from '../composables/useCachedData'
import CompanyCard from './CompanyCard.vue'
import CompanyModal from './CompanyModal.vue'
import FilterPanel from './FilterPanel.vue'
import { computeSectorScore } from '../utils/scoringService'
import { sectorProfiles } from '../utils/sectorProfiles'
import { normalize } from '../utils/financeUtils'

const { data: companies } = useCachedData()

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

const currentPage = ref(1)
const itemsPerPage = 51

const totalPages = computed(() => {
  return Math.ceil(sortedCompanies.value.length / itemsPerPage)
})

const paginatedCompanies = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return sortedCompanies.value.slice(start, start + itemsPerPage)
})

function goToPreviousPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function goToNextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

watch([filteredCompanies, sortBy], () => {
  currentPage.value = 1
})

</script>
