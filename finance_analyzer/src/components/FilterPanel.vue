<template>
  <div class="flex justify-between items-center px-6 mb-4">
    <p class="text-sm text-gray-500">
      Loaded: {{ totalCount }} | Filtered: {{ filteredCount }}
    </p>
  </div>
  <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-7 gap-4 px-6">
    <div>
      <label class="block text-sm font-semibold text-gray-700 mb-1">Minimum growth (%)</label>
      <input
        type="number"
        v-model.number="filters.minGrowth"
        class="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
      />
    </div>
    <div>
      <label class="block text-sm font-semibold text-gray-700 mb-1">Max Debt / EBITDA</label>
      <input
        type="number"
        v-model.number="filters.maxDebt"
        class="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
      />
    </div>
    <div>
      <label class="block text-sm font-semibold text-gray-700 mb-1">Minimum revenue (M€)</label>
      <input
        type="number"
        v-model.number="filters.minRevenue"
        class="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
      />
    </div>
    <div>
      <label class="block text-sm font-semibold text-gray-700 mb-1">Minimum EBITDA margin (%)</label>
      <input
        type="number"
        v-model.number="filters.minMargin"
        class="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
      />
    </div>
    <div>
      <label class="block text-sm font-semibold text-gray-700 mb-1">Sector</label>
      <select
        v-model="filters.sector"
        class="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
      >
        <option value="">All</option>
        <option v-for="s in sectors" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>
    <div class="flex items-center gap-2">
      <input type="checkbox" id="peaEligible" v-model="filters.peaEligible" />
      <label for="peaEligible" class="text-sm font-semibold text-gray-700">PEA Eligible</label>
    </div>
    <div class="flex items-end gap-2">
      <button
        @click="onReset"
        class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition"
      >
        Reset
      </button>
      <button
        @click="onExport"
        class="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg text-sm font-medium transition"
      >
        Export CSV
      </button>
      <button
        @click="onReload"
        class="px-4 py-2 bg-green-600 text-white hover:bg-green-700 rounded-lg text-sm font-medium transition"
      >
        Reload Fresh
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  filters: Object,
  sectors: Array,
  onReset: Function,
  onExport: Function,
  onReload: Function,
  totalCount: Number,
  filteredCount: Number
})
</script>
