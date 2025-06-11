<template>
  <div class="px-4 max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-3">
      <p class="text-xs text-gray-500">
        Loaded: {{ totalCount }} | Filtered: {{ filteredCount }}
      </p>
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3">
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-0.5">Min growth (%)</label>
        <input
          type="number"
          v-model.number="filters.minGrowth"
          class="w-full border border-gray-300 px-2 py-1.5 rounded-md focus:ring-1 focus:ring-blue-500 focus:outline-none text-xs"
        />
      </div>

      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-0.5">Max Debt / EBITDA</label>
        <input
          type="number"
          v-model.number="filters.maxDebt"
          class="w-full border border-gray-300 px-2 py-1.5 rounded-md focus:ring-1 focus:ring-blue-500 focus:outline-none text-xs"
        />
      </div>

      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-0.5">Min revenue (M€)</label>
        <input
          type="number"
          v-model.number="filters.minRevenue"
          class="w-full border border-gray-300 px-2 py-1.5 rounded-md focus:ring-1 focus:ring-blue-500 focus:outline-none text-xs"
        />
      </div>

      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-0.5">Min EBITDA margin (%)</label>
        <input
          type="number"
          v-model.number="filters.minMargin"
          class="w-full border border-gray-300 px-2 py-1.5 rounded-md focus:ring-1 focus:ring-blue-500 focus:outline-none text-xs"
        />
      </div>

      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-0.5">Sector</label>
        <select
          v-model="filters.sector"
          class="w-full border border-gray-300 px-2 py-1.5 rounded-md focus:ring-1 focus:ring-blue-500 focus:outline-none text-xs"
        >
          <option value="">All</option>
          <option v-for="s in sectors" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>

      <div class="flex items-center gap-2 mt-6">
        <input type="checkbox" id="peaEligible" v-model="filters.peaEligible" class="h-4 w-4" />
        <label for="peaEligible" class="text-xs font-semibold text-gray-700">PEA Eligible</label>
      </div>

      <div class="flex items-end gap-2 mt-6">
        <button
          @click="onReset"
          class="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-xs font-medium"
        >
          Reset
        </button>
        <button
          @click="onExport"
          class="px-3 py-1.5 bg-blue-600 text-white hover:bg-blue-700 rounded-md text-xs font-medium"
        >
          Export CSV
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  filters: Object,
  sectors: Array,
  onReset: Function,
  onExport: Function,
  totalCount: Number,
  filteredCount: Number
})
</script>
