export function formatNumber(value) {
  if (value == null || isNaN(value)) return 'N/A'
  if (Math.abs(value) >= 1_000_000_000) {
    return (value / 1_000_000_000).toFixed(1) + ' B'
  }
  if (Math.abs(value) >= 1_000_000) {
    return (value / 1_000_000).toFixed(1) + ' M'
  }
  return value.toLocaleString()
}

export function formatPercent(value) {
  if (value == null || isNaN(value)) return 'N/A'
  return value.toFixed(1) + ' %'
}
