import { sectorProfiles } from './sectorProfiles';
import { isValidNumber, normalize } from './financeUtils';


export function computeSectorScore(company) {
  const sector = company.sector || 'default'
  const profile = sectorProfiles[sector] || sectorProfiles['default']
  const { metrics, weights } = profile

  // Vérifie uniquement les champs nécessaires pour CE secteur
  const missingFields = metrics.filter(metric => !isValidNumber(company[metric]))
  if (missingFields.length > 0) {
    console.warn(`[MissingFields] ${company.name || 'Unknown'} is missing required metrics for its sector (${sector}):`, missingFields)
    return 'N/A'
  }

  const scores = metrics.map((metric, index) => {
    let score
    switch (metric) {
      case 'ebitdaMargin':
        score = normalize(company[metric], 0, 50)
        break
      case 'debtToEbitda':
        score = normalize(10 - company[metric], 0, 10)
        break
      case 'growth':
        score = normalize(company[metric], -20, 50)
        break
      case 'revenue':
        score = normalize(company[metric], 0, 500)
        break
      case 'roe':
        score = normalize(company[metric], 0, 20)
        break
      case 'trend':
        score = normalize(company[metric], -50, 50)
        break
      case 'revenuePerShare':
        score = normalize(company[metric], 0, 100)
        break
      case 'psRatio':
        score = normalize(20 - company[metric], 0, 20) // inverse du P/S : plus petit est mieux
        break
      default:
        score = 0
    }
    return score * weights[index]
  })

  const totalScore = scores.reduce((sum, score) => sum + score, 0)
  return totalScore.toFixed(2)
}