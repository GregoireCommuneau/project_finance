import { reactive } from 'vue'

export const companies = reactive([])

const CACHE_KEY = 'fetchedFrenchCompanies'
const EXPIRATION_DAYS = 6
const API_KEY = 'pjaMA7esuOuKWDQkPIKqUB009g0BsMFF'

import { FRENCH_SYMBOLS } from './stockSymbols.js';

function isExpired(timestamp) {
  return Date.now() - timestamp > EXPIRATION_DAYS * 24 * 60 * 60 * 1000
}

function isValidNumber(n) {
  return typeof n === 'number' && !isNaN(n)
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function fetchCompanyDetails(symbol) {
  let profile = null
  let priceHistory = []
  let income = null
  let balance = null
  let enterpriseValue = null

  try {
    const profileRes = await fetch(`https://financialmodelingprep.com/api/v3/profile/${symbol}?apikey=${API_KEY}`)
    const profileData = await profileRes.json()
    profile = Array.isArray(profileData) ? profileData[0] : null
  } catch (e) {
    console.warn(`Profile fetch failed for ${symbol}:`, e.message)
  }

  try {
    const priceRes = await fetch(`https://financialmodelingprep.com/api/v3/historical-price-full/${symbol}?serietype=line&timeseries=252&apikey=${API_KEY}`)
    const priceData = await priceRes.json()
    priceHistory = priceData?.historical?.map(p => p.close).reverse() || []
  } catch (e) {
    console.warn(`Price data fetch failed for ${symbol}:`, e.message)
  }

  try {
    const incomeRes = await fetch(`https://financialmodelingprep.com/api/v3/income-statement/${symbol}?limit=2&apikey=${API_KEY}`)
    income = await incomeRes.json()
  } catch (e) {
    console.warn(`Income statement fetch failed for ${symbol}:`, e.message)
  }

  try {
    const balanceRes = await fetch(`https://financialmodelingprep.com/api/v3/balance-sheet-statement/${symbol}?limit=1&apikey=${API_KEY}`)
    const [balanceData] = await balanceRes.json()
    balance = balanceData
  } catch (e) {
    console.warn(`Balance sheet fetch failed for ${symbol}:`, e.message)
  }

  try {
    const evRes = await fetch(`https://financialmodelingprep.com/api/v3/enterprise-values/${symbol}?limit=1&apikey=${API_KEY}`)
    const evData = await evRes.json()
    enterpriseValue = evData?.[0]?.enterpriseValue ?? null
  } catch (e) {
    console.warn(`Enterprise value fetch failed for ${symbol}:`, e.message)
  }

  const latest = income?.[0]
  const previous = income?.[1]

  const currentEbitda = latest?.ebitda ?? null
  const previousEbitda = previous?.ebitda ?? null

  const ebitdaGrowth = (currentEbitda && previousEbitda)
    ? ((currentEbitda - previousEbitda) / previousEbitda) * 100
    : null

  const revenue = latest?.revenue ?? null
  const sharesOutstanding = latest?.weightedAverageShsOut ?? null
  const ebitdaMargin = (currentEbitda && revenue)
    ? (currentEbitda / revenue) * 100
    : null
  const growth = (latest?.revenue && previous?.revenue)
    ? ((latest.revenue - previous.revenue) / previous.revenue) * 100
    : null

  const totalDebt = balance?.totalDebt ?? null
  const cash = balance?.cashAndShortTermInvestments ?? 0
  const netDebt = (totalDebt != null) ? totalDebt - cash : null
  const debtToEbitda = (netDebt != null && currentEbitda > 0)
    ? netDebt / currentEbitda
    : null
  const revenueToEV = (enterpriseValue && revenue != null) ? revenue / enterpriseValue : 0

  const netIncome = latest?.netIncome ?? null;
  const totalEquity = balance?.totalStockholdersEquity ?? null;

  const roe = (netIncome != null && totalEquity > 0)
    ? (netIncome / totalEquity) * 100
    : null;

  // Compute trend (percentage change over priceHistory)
  let trend = null;
  if (Array.isArray(priceHistory) && priceHistory.length > 1) {
    const start = priceHistory[0];
    const end = priceHistory[priceHistory.length - 1];
    if (isValidNumber(start) && isValidNumber(end) && start !== 0) {
      trend = ((end - start) / start) * 100;
    }
  }

  return {
    name: profile?.companyName ?? symbol,
    sector: profile?.sector ?? 'Unknown',
    symbol,
    price: profile?.price ?? null,
    priceHistory,
    revenue,
    ebitdaMargin,
    debtToEbitda,
    growth,
    sharesOutstanding,
    netDebt,
    ebitda: currentEbitda,
    ebitdaGrowth,
    enterpriseValue,
    revenueToEV,
    trend,
    roe,
    country: profile?.country ?? 'FR'
  }
}

export async function loadCompanies(force = false) {
  console.info('[loadCompanies] Triggered')

  const cached = JSON.parse(localStorage.getItem(CACHE_KEY))
  if (cached && !isExpired(cached.timestamp) && !force) {
    console.info('[loadCompanies] Using cached data')
    companies.splice(0, companies.length, ...cached.data)
    return
  }

  const enriched = []

  for (const symbol of FRENCH_SYMBOLS) {
    const company = await fetchCompanyDetails(symbol)
    await sleep(1500)

    const requiredFields = [
      'revenue',
      'price',
      'ebitda',
      'ebitdaMargin',
      'debtToEbitda',
      'growth',
      'sharesOutstanding',
      'netDebt',
      'trend',
      'roe'
    ]

    const missingFields = requiredFields.filter(field => !isValidNumber(company[field]))

    if (missingFields.length === 0) {
      console.log(`[✓] ${symbol} OK – all data present`)
    } else {
      console.warn(`[⚠️] ${symbol} incomplete – missing fields : ${missingFields.join(', ')}`)
      console.debug(company)
    }

    enriched.push(company)
  }

  companies.splice(0, companies.length, ...enriched)
  localStorage.setItem(CACHE_KEY, JSON.stringify({
    data: enriched,
    timestamp: Date.now()
  }))

  console.info(`[loadCompanies] Completed. Total companies loaded: ${enriched.length}`)
}
