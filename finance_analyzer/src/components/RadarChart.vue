<template>
  <div class="flex justify-center items-center my-6">
    <svg ref="radarRef" :width="width" :height="height"></svg>
  </div>
</template>

<script setup>
import { onMounted, watch, ref, nextTick } from 'vue'
import * as d3 from 'd3'
import { sectorProfiles } from '../utils/sectorProfiles'


const props = defineProps({ company: Object })

const radarRef = ref(null)
const width = 400
const height = 400
const radius = Math.min(width, height) / 2 - 40

// Axis configurations by sector
const metricMeta = {
  ebitdaMargin: { label: 'EBITDA Margin (%)', unit: '%', min: 0, max: 70 },
  debtToEbitda: { label: 'Debt/EBITDA', unit: '', min: 0, max: 10, invert: true },
  revenueToEV: { label: 'Revenue / EV', unit: '', min: 0, max: 1 },
  ebitdaGrowth: { label: 'EBITDA Growth (%)', unit: '%', min: -20, max: 50 },
  growth: { label: 'Growth (%)', unit: '%', min: -20, max: 50 },
  revenue: { label: 'Revenue (M)', unit: 'M', min: 0, max: 500 },
  roe: { label: 'ROE (%)', unit: '%', min: 0, max: 25 },
  trend: { label: 'Price Trend (%)', unit: '%', min: -50, max: 50 }
}

function getAxesForCompany(company) {
  const sector = company?.sector || 'default'
  const profile = sectorProfiles[sector] || sectorProfiles['default']
  return profile.metrics.map(metric => ({
    key: metric,
    ...(metricMeta[metric] || { label: metric, unit: '', min: 0, max: 100 })
  }))
}

function normalize(value, axis) {
  if (value == null || isNaN(value)) return 0
  let clipped = Math.max(axis.min, Math.min(axis.max, value))
  let norm = (clipped - axis.min) / (axis.max - axis.min)
  return axis.invert ? 1 - norm : norm
}

function renderRadar(company) {
  const svg = d3.select(radarRef.value)
  svg.selectAll('*').remove()
  const g = svg.append('g').attr('transform', `translate(${width / 2}, ${height / 2})`)

  const sector = company?.sector || 'default'
  const axes = getAxesForCompany(company)
  const angleSlice = (Math.PI * 2) / axes.length

  // Draw grid
  const levels = 5
  for (let level = 1; level <= levels; level++) {
    const r = radius * (level / levels)
    g.append('polygon')
      .attr('points', axes.map((_, i) => {
        const angle = angleSlice * i - Math.PI / 2
        return [r * Math.cos(angle), r * Math.sin(angle)].join(',')
      }).join(' '))
      .attr('stroke', '#ccc')
      .attr('fill', 'none')
  }

  // Axis lines + labels
  axes.forEach((axis, i) => {
    const angle = angleSlice * i - Math.PI / 2
    const [x, y] = [Math.cos(angle) * radius, Math.sin(angle) * radius]

    g.append('line')
      .attr('x1', 0).attr('y1', 0)
      .attr('x2', x).attr('y2', y)
      .attr('stroke', '#999')

    g.append('text')
      .attr('x', x * 1.15).attr('y', y * 1.15)
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .style('font-size', '11px')
      .text(axis.label)
  })

  // Data points
  const points = axes.map((axis, i) => {
    const angle = angleSlice * i - Math.PI / 2
    const norm = normalize(company?.[axis.key], axis)
    const r = norm * radius
    return [r * Math.cos(angle), r * Math.sin(angle)]
  })

  g.append('polygon')
    .attr('points', points.map(p => p.join(',')).join(' '))
    .attr('fill', 'rgba(79, 70, 229, 0.2)')
    .attr('stroke', '#4f46e5')
    .attr('stroke-width', 2)

  // Points and value labels
  points.forEach(([x, y], i) => {
    const axis = axes[i]
    const raw = company?.[axis.key]
    const label = formatValue(raw, axis.unit)

    g.append('circle')
      .attr('cx', x).attr('cy', y).attr('r', 3)
      .attr('fill', '#4f46e5')

    g.append('text')
      .attr('x', x).attr('y', y - 8)
      .attr('text-anchor', 'middle')
      .attr('font-size', '10px')
      .text(label)
  })
}

watch(() => props.company, (newCompany) => {
  if (newCompany) nextTick(() => renderRadar(newCompany))
}, { immediate: true })

function formatValue(value, unit) {
  if (value == null || isNaN(value)) return '-'

  // Format pourcentages
  if (unit === '%') {
    return `${value.toFixed(1)}%`
  }

  // Money format
  if (unit === '€') {
    if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1)} B €`
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)} M €`
    if (value >= 1_000) return `${(value / 1_000).toFixed(1)} k €`
    return `${value.toFixed(1)} €`
  }

  // Number format
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1)} B`
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)} M`
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)} k`

  return `${value.toFixed(1)}`
}

onMounted(() => {
  if (props.company) renderRadar(props.company)
})
</script>

<style scoped>
div {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%; /* ou une hauteur spécifique */
}

svg {
  display: block;
}
</style>