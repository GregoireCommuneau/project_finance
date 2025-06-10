export const fmt = (val, decimals = 1) =>
  val != null && !isNaN(val) ? (+val).toFixed(decimals) : '–'

export const normalize = (val, min, max) => {
  if (val == null || isNaN(val)) return 0
  if (min === max) return val >= max ? 100 : 0
  return Math.max(0, Math.min(100, ((val - min) / (max - min)) * 100))
}

export function computeEVtoEbitda(c) {
  if (!c || !c.ebitda || !c.sharesOutstanding || !c.price) return null
  const ev = c.price * c.sharesOutstanding + (c.netDebt ?? 0)
  return ev / c.ebitda
}

export function computeTrend(history) {
  if (!Array.isArray(history) || history.length < 2) return 0
  const start = history[0]
  const end = history[history.length - 1]
  return normalize(((end - start) / start) * 100, -50, 50)
}

export function isValidNumber(val) {
  if (val === null || val === undefined || val === '') return false
  const num = Number(val)
  return !isNaN(num) && isFinite(num)
}

export const sectorProfiles = {
  'Technology': {
    metrics: ['ebitdaMargin', 'debtToEbitda', 'growth', 'revenue', 'evToEbitda', 'trend'],
    weights: [0.25, 0.2, 0.15, 0.15, 0.15, 0.1]
  },
  'Financial Services': {
    metrics: ['roe', 'revenue', 'trend'],
    weights: [0.5, 0.3, 0.2]
  },
  'Healthcare': {
    metrics: ['growth', 'ebitdaMargin', 'revenue', 'trend'],
    weights: [0.3, 0.25, 0.25, 0.2]
  },
  'Utilities': {
    metrics: ['ebitdaMargin', 'debtToEbitda', 'trend'],
    weights: [0.4, 0.4, 0.2]
  },
  'Consumer Cyclical': {
    metrics: ['growth', 'revenue', 'ebitdaMargin', 'trend'],
    weights: [0.3, 0.3, 0.2, 0.2]
  },
  'Consumer Defensive': {
    metrics: ['revenue', 'ebitdaMargin', 'trend'],
    weights: [0.4, 0.4, 0.2]
  },
  'Communication Services': {
    metrics: ['ebitdaMargin', 'growth', 'trend'],
    weights: [0.4, 0.4, 0.2]
  },
  'Industrials': {
    metrics: ['ebitdaMargin', 'debtToEbitda', 'growth', 'trend'],
    weights: [0.3, 0.3, 0.2, 0.2]
  },
  'Basic Materials': {
    metrics: ['ebitdaMargin', 'debtToEbitda', 'revenue', 'trend'],
    weights: [0.3, 0.3, 0.2, 0.2]
  },
  'default': {
    metrics: ['ebitdaMargin', 'debtToEbitda', 'growth', 'revenue', 'trend'],
    weights: [0.25, 0.25, 0.2, 0.2, 0.1]
  }
}

export function getSectorProfile(sector) {
  return sectorProfiles[sector] || sectorProfiles.default
}

export function computeDynamicScore(c, sector) {
  const profile = getSectorProfile(sector)
  const { metrics, weights } = profile

  const missing = metrics.filter(m => {
    if (m === 'evToEbitda') return !isValidNumber(computeEVtoEbitda(c))
    return !isValidNumber(c[m])
  })
  if (missing.length > 0) return { score: 'N/A', missing }

  const values = metrics.map(m => {
    if (m === 'evToEbitda') return normalize(30 - computeEVtoEbitda(c), 0, 30)
    if (m === 'trend') return computeTrend(c.priceHistory)
    if (m === 'roe') return normalize(c.roe, 0, 20)
    if (m === 'ebitdaMargin') return normalize(c.ebitdaMargin, 0, 50)
    if (m === 'debtToEbitda') return normalize(10 - Number(c.debtToEbitda), 0, 10)
    if (m === 'growth') return normalize(c.growth, -20, 50)
    if (m === 'revenue') return normalize(c.revenue, 0, 500)
    return 0
  })

  const score = values.reduce((sum, val, i) => sum + val * weights[i], 0)
  return { score: score.toFixed(2), missing: [] }
}
