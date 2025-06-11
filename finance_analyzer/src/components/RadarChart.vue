<template>
  <div class="flex justify-center items-center my-6">
    <!-- SVG pour le radar chart -->
    <svg
      ref="radarRef"
      v-if="hasData"
      :width="width"
      :height="height"
      viewBox="0 0 400 400"
      preserveAspectRatio="xMidYMid meet"
    ></svg>
    <p v-else class="text-gray-500 text-sm">Pas assez de données pour afficher le radar.</p>
  </div>
</template>

<script setup>
import { onMounted, watch, ref, nextTick, computed } from 'vue'
import * as d3 from 'd3'
import { sectorProfiles } from '../utils/sectorProfiles'

const props = defineProps({
  company: Object,
  allCompanies: Array
})

const radarRef = ref(null)
const width = 400
const height = 400
const radius = Math.min(width, height) / 2 - 60

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

function getAxes(company) {
  const profile = sectorProfiles[company?.sector] || sectorProfiles['default']
  return profile.metrics.map(metric => ({
    key: metric,
    ...(metricMeta[metric] || { label: metric, unit: '', min: 0, max: 100 })
  }))
}

function normalize(value, axis) {
  if (value == null || isNaN(value)) return 0
  const clipped = Math.max(axis.min, Math.min(axis.max, value))
  const norm = (clipped - axis.min) / (axis.max - axis.min)
  return axis.invert ? 1 - norm : norm
}

function formatValue(value, unit) {
  if (value == null || isNaN(value)) return '-'
  if (unit === '%') return `${value.toFixed(1)}%`
  if (unit === '€') {
    if (value >= 1e9) return `${(value / 1e9).toFixed(1)} B €`
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)} M €`
    return `${value.toFixed(1)} €`
  }
  return value >= 1e6 ? `${(value / 1e6).toFixed(1)} M` : value.toFixed(1)
}

function computeSectorAverages(company, allCompanies, axes) {
  if (!allCompanies || allCompanies.length === 0) return {}
  const sameSector = allCompanies.filter(c => {
    if (c.sector !== company?.sector) return false
    const profile = sectorProfiles[company?.sector] || sectorProfiles['default']
    return profile.metrics.some(key => typeof c[key] === 'number' && !isNaN(c[key]))
  })

  if (sameSector.length === 0) {
    console.warn(`[RadarChart] No valid peers found in sector "${company?.sector}"`)
  }

  const avg = {}
  for (const axis of axes) {
    const values = sameSector.map(c => c[axis.key]).filter(v => typeof v === 'number' && !isNaN(v))
    avg[axis.key] = values.length ? d3.mean(values) : 0
  }
  return avg
}

function renderRadar(company, allCompanies) {
  const svg = d3.select(radarRef.value)
  svg.selectAll('*').remove()
  const g = svg.append('g').attr('transform', `translate(${width / 2}, ${height / 2})`)

  const axes = getAxes(company)
  const angleSlice = (2 * Math.PI) / axes.length

  const averages = computeSectorAverages(company, allCompanies, axes)
  const sectorPoints = axes.map((axis, i) => {
    const angle = angleSlice * i - Math.PI / 2
    const norm = normalize(averages[axis.key], axis)
    const r = norm * radius
    return [r * Math.cos(angle), r * Math.sin(angle)]
  })

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

  axes.forEach((axis, i) => {
    const angle = angleSlice * i - Math.PI / 2
    const [x, y] = [Math.cos(angle) * radius, Math.sin(angle) * radius]

    g.append('line')
      .attr('x1', 0).attr('y1', 0)
      .attr('x2', x).attr('y2', y)
      .attr('stroke', '#999')

    g.append('text')
      .attr('x', x * 1.15)
      .attr('y', y * 1.15)
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .style('font-size', '11px')
      .text(axis.label)
  })

  const companyPoints = axes.map((axis, i) => {
    const angle = angleSlice * i - Math.PI / 2
    const norm = normalize(company?.[axis.key], axis)
    const r = norm * radius
    return [r * Math.cos(angle), r * Math.sin(angle)]
  })

  g.append('polygon')
    .attr('points', companyPoints.map(p => p.join(',')).join(' '))
    .attr('fill', 'rgba(79, 70, 229, 0.2)')
    .attr('stroke', '#4f46e5')
    .attr('stroke-width', 2)

  g.append('polygon')
    .attr('points', sectorPoints.map(p => p.join(',')).join(' '))
    .attr('fill', 'rgba(96, 165, 250, 0.2)')
    .attr('stroke', '#60a5fa')
    .attr('stroke-width', 2)
    .attr('stroke-dasharray', '4 2')

  companyPoints.forEach(([x, y], i) => {
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

const hasData = computed(() => {
  const axes = getAxes(props.company)
  const averages = computeSectorAverages(props.company, props.allCompanies, axes)
  return axes.some(axis => typeof averages[axis.key] === 'number' && !isNaN(averages[axis.key]))
})

watch(() => props.company, () => {
  if (props.company && props.allCompanies?.length > 0) {
    nextTick(() => renderRadar(props.company, props.allCompanies))
  }
}, { immediate: true })

onMounted(() => {
  if (props.company && props.allCompanies?.length > 0) {
    renderRadar(props.company, props.allCompanies)
  }
})
</script>

<style scoped>
div {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

svg {
  display: block;
}
</style>
