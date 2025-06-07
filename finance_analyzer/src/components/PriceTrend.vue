<template>
  <div class="mt-4 bg-gray-50 rounded p-3">
    <div class="flex justify-between items-center text-sm text-gray-700 mb-2">
      <span class="font-medium">Price</span>
      <span class="font-bold text-gray-900">
        {{ price.toFixed(2) }} €
        <span
          :class="trend >= 0 ? 'text-green-600' : 'text-red-600'"
          class="ml-1 text-xs"
        >
          ({{ trend >= 0 ? '+' : '' }}{{ trend.toFixed(1) }}%)
        </span>
      </span>
    </div>

    <!-- Duration Selector -->
    <div class="flex space-x-2 mb-2">
      <button
        type="button"
        v-for="range in ranges"
        :key="range.label"
        @click.stop="selectedRange = range"
        :class="[
          'px-2 py-1 text-xs rounded border',
          selectedRange.label === range.label
            ? 'bg-blue-500 text-white border-blue-500'
            : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-100'
        ]"
      >
        {{ range.label }}
      </button>
    </div>

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
  price: Number,
  history: Array,
  range: Object
})
const canvas = ref(null)
let chart = null

const ranges = [
  { label: '1M', length: 21 },
  { label: '6M', length: 126 },
  { label: '1Y', length: 252 }
]

const selectedRange = ref(ranges[0])

const slicedHistory = computed(() => {
  if (!props.history) return []
  return props.history.slice(-selectedRange.value.length)
})

const trend = computed(() => {
  const data = slicedHistory.value
  if (!data.length) return 0
  const start = data[0]
  const end = data.at(-1)
  return ((end - start) / start) * 100
})

function drawChart() {
  if (!canvas.value || !slicedHistory.value.length) return
  if (chart) chart.destroy()

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

watch(() => slicedHistory.value, () => {
  console.log('Sliced data (length:', slicedHistory.value.length, '):', slicedHistory.value)
  drawChart()
}, { immediate: true })
onMounted(() => {
  console.log('Full price history:', props.history)
  drawChart()
})
</script>
