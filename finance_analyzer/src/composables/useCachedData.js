import { ref } from 'vue'

const CACHE_KEY = 'cachedCompanyData'
const TIMESTAMP_KEY = 'cachedCompanyTimestamp'
const MAX_AGE = 6 * 60 * 60 * 1000 // 6 heures

export function useCachedData() {
  const data = ref([])
  const loading = ref(true)

  async function fetchData() {
    const cached = localStorage.getItem(CACHE_KEY)
    const timestamp = localStorage.getItem(TIMESTAMP_KEY)
    const now = Date.now()

    if (cached && timestamp && now - parseInt(timestamp) < MAX_AGE) {
      data.value = JSON.parse(cached)
    } else {
      const res = await fetch('/data/data.json')
      const freshData = await res.json()
      localStorage.setItem(CACHE_KEY, JSON.stringify(freshData))
      localStorage.setItem(TIMESTAMP_KEY, now.toString())
      data.value = freshData
    }

    loading.value = false
  }

  fetchData()

  return { data, loading }
}
