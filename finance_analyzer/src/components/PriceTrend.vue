<template>
  <div class="mt-4 bg-gray-50 rounded p-3">
    <div class="flex justify-between items-center text-sm text-gray-700 mb-2">
      <span class="font-medium">Price</span>
      <span v-if="price !== null" class="font-bold text-gray-900">
        {{ price.toFixed(2) }} €
        <span
          :class="trend >= 0 ? 'text-green-600' : 'text-red-600'"
          class="ml-1 text-xs"
        >
          ({{ trend >= 0 ? '+' : '' }}{{ trend.toFixed(1) }}%)
        </span>
      </span>
      <span v-else class="font-bold text-gray-500">
        Price data not available
      </span>
    </div>

    <!-- Pas de boutons ici : ce composant est synchronisé via `range` -->
    <div class="h-10">
      <canvas ref="canvas" class="w-full h-full" />
    </div>
  </div>
</template>

<script setup>
import { computed, watch, ref, onMounted } from 'vue'
import {
  Chart,
  LineController,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
} from 'chart.js'

Chart.register(LineController, LineElement, CategoryScale, LinearScale, PointElement)

const props = defineProps({
  price: {
    type: Number,
    default: null
  },
  history: {
    type: Array,
    default: () => []
  },
  range: {
    type: Object,
    default: () => ({ length: 0 })
  }
})

const canvas = ref(null)
let chart = null

const slicedHistory = computed(() => {
  if (!props.history || !props.range?.length) return []
  return props.history.slice(-props.range.length)
})

const trend = computed(() => {
  const data = slicedHistory.value
  if (!data.length || data.length < 2) return 0
  const start = data[0]
  const end = data[data.length - 1]
  return ((end - start) / start) * 100
})

function drawChart() {
  if (!canvas.value || !slicedHistory.value.length) {
    return
  }

  if (chart) {
    chart.destroy()
  }

  chart = new Chart(canvas.value.getContext('2d'), {
    type: 'line',
    data: {
      labels: slicedHistory.value.map((_, i) => i),
      datasets: [{
        data: slicedHistory.value,
        borderColor: '#4f46e5',
        tension: 0.3,
        pointRadius: 0,
        fill: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { display: false },
        y: { display: false }
      },
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      }
    }
  })
}

watch(() => props.range, drawChart, { immediate: true })
onMounted(drawChart)
</script>
