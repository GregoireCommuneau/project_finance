// dataFetcher.js
import fs from 'fs/promises'
import fetch from 'node-fetch'
import { FRENCH_SYMBOLS } from './src/data/stockSymbols.js'

const API_KEY = '...to replace...' // put your API_KEY
const OUTPUT_PATH = './public/data/data.json'

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
    const profileRes = await fetch(https://financialmodelingprep.com/api/v3/profile/${symbol}?apikey=${API_KEY})
    const profileData = await profileRes.json()
    profile = Array.isArray(profileData) ? profileData[0] : null
  } catch {}

  try {
    const priceRes = await fetch(https://financialmodelingprep.com/api/v3/historical-price-full/${symbol}?serietype=line&timeseries=252&apikey=${API_KEY})
    const priceData = await priceRes.json()
    priceHistory = priceData?.historical?.map(p => p.close).reverse() || []
  } catch {}

  try {
    const incomeRes = await fetch(https://financialmodelingprep.com/api/v3/income-statement/${symbol}?limit=2&apikey=${API_KEY})
    income = await incomeRes.json()
  } catch {}

  try {
    const balanceRes = await fetch(https://financialmodelingprep.com/api/v3/balance-sheet-statement/${symbol}?limit=1&apikey=${API_KEY})
    const [balanceData] = await balanceRes.json()
    balance = balanceData
  } catch {}

  try {
    const evRes = await fetch(https://financialmodelingprep.com/api/v3/enterprise-values/${symbol}?limit=1&apikey=${API_KEY})
    const evData = await evRes.json()
    enterpriseValue = evData?.[0]?.enterpriseValue ?? null
  } catch {}

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

  const netIncome = latest?.netIncome ?? null;
  const totalEquity = balance?.totalStockholdersEquity ?? null;
  const roe = (netIncome != null && totalEquity > 0)
    ? (netIncome / totalEquity) * 100
    : null;

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
    revenueToEV: (enterpriseValue && revenue != null) ? revenue / enterpriseValue : 0,
    trend,
    roe,
    country: profile?.country ?? 'FR'
  }
}

export async function generateStaticData() {
  const results = []

  for (const symbol of FRENCH_SYMBOLS) {
    console.log([fetch] ${symbol})
    const company = await fetchCompanyDetails(symbol)
    await sleep(1500)
    results.push(company)
  }

  await fs.writeFile(OUTPUT_PATH, JSON.stringify(results, null, 2), 'utf-8')
  console.log([done] Data saved to ${OUTPUT_PATH})
}

// Usage example:
// node dataFetcher.js

if (import.meta.url === file://${process.argv[1]}) {
  generateStaticData()
}