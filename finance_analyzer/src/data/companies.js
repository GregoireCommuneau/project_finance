import { reactive } from 'vue'

export const companies = reactive([])

const CACHE_KEY = 'fetchedCompanies'
const EXPIRATION_DAYS = 6

function isExpired(timestamp) {
  const now = Date.now()
  return now - timestamp > EXPIRATION_DAYS * 24 * 60 * 60 * 1000
}

export async function loadCompanies(force = false) {
  const cached = JSON.parse(localStorage.getItem(CACHE_KEY))

  if (cached && !isExpired(cached.timestamp) && !force) {
    console.log('Using cached data')
    companies.length = 0
    companies.push(...cached.data)
    return
  }

  try {
    console.log('Fetching fresh data...')
    const res = await fetch('https://financialmodelingprep.com/api/v3/stock-screener?marketCapMoreThan=1000000000&limit=10&apikey=pjaMA7esuOuKWDQkPIKqUB009g0BsMFF')
    const apiData = await res.json()

    const enriched = await Promise.all(apiData.map(async c => {
      const symbol = c.symbol
      let priceHistory = []

      try {
        const priceRes = await fetch(`https://financialmodelingprep.com/api/v3/historical-price-full/${symbol}?serietype=line&timeseries=252&apikey=pjaMA7esuOuKWDQkPIKqUB009g0BsMFF`)
        const priceData = await priceRes.json()
        priceHistory = priceData?.historical?.map(p => p.close).reverse() || []
      } catch (e) {
        console.warn(`Failed to load history for ${symbol}`, e)
      }

      return {
        name: c.companyName,
        sector: c.sector || 'Unknown',
        symbol: c.symbol,
        price: c.price,
        priceHistory,
        revenue: Math.random() * 100,
        ebitdaMargin: Math.random() * 30,
        debtToEbitda: Math.random() * 5,
        growth: Math.random() * 20,
        ebitda: Math.random() * 100_000_000,
        sharesOutstanding: Math.random() * 100_000_000,
        netDebt: Math.random() * 1_000_000_000
      }
    }))

    companies.length = 0
    companies.push(...enriched)

    localStorage.setItem(CACHE_KEY, JSON.stringify({
      data: enriched,
      timestamp: Date.now()
    }))

    console.log('Fresh data loaded:', enriched.length)
  } catch (e) {
    console.error('Failed to fetch companies:', e)
  }
}
