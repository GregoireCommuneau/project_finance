<template>
  <div class="my-6 max-w-md mx-auto">
    <canvas ref="radarRef"></canvas>
  </div>
</template>

<script setup>
import { onMounted, watch, ref } from 'vue'
import { Chart, RadarController, RadialLinearScale, PointElement, LineElement, Filler, Tooltip } from 'chart.js'
Chart.register(RadarController, RadialLinearScale, PointElement, LineElement, Filler, Tooltip)

const props = defineProps({ company: Object })
const radarRef = ref(null)
let radarChart = null

const normalize = (value, min, max) => {
  if (value == null || isNaN(value)) return 0
  return Math.max(0, Math.min(100, ((value - min) / (max - min)) * 100))
}

function renderRadar(company) {
  if (!radarRef.value) return

  if (radarChart) {
    radarChart.destroy()
  }

  const revenueScore = normalize(company.revenue, 0, 500)
  const ebitdaScore = normalize(company.ebitdaMargin, 0, 100)
  const debtScore = normalize(10 - company.debtToEbitda, 0, 10)
  const growthScore = normalize(company.growth, -20, 50)

  radarChart = new Chart(radarRef.value.getContext('2d'), {
    type: 'radar',
    data: {
      labels: ['Revenue', 'EBITDA Margin', 'Debt/EBITDA (inverted)', 'Growth'],
      datasets: [{
        label: company.name,
        data: [revenueScore, ebitdaScore, debtScore, growthScore],
        backgroundColor: 'rgba(79, 70, 229, 0.2)',
        borderColor: '#4f46e5'
      }]
    },
    options: {
      scales: {
        r: { beginAtZero: true, max: 100 }
      }
    }
  })
}

watch(() => props.company, (newCompany) => {
  if (newCompany) {
    renderRadar(newCompany)
  }
}, { immediate: true })

onMounted(() => {
  if (props.company) {
    renderRadar(props.company)
  }
})
</script>
