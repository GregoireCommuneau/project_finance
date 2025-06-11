export const sectorProfiles = {
  'Financial Services': {
    metrics: ['roe', 'revenueToEV', 'trend'],
    weights: [0.5, 0.3, 0.2]
  },
  'Technology': {
    metrics: ['growth', 'ebitdaMargin', 'roe', 'trend'],
    weights: [0.3, 0.3, 0.2, 0.2]
  },
  'Healthcare': {
    metrics: ['growth', 'ebitdaMargin', 'roe', 'trend'],
    weights: [0.2, 0.35, 0.25, 0.2]
  },
  'Utilities': {
    metrics: ['ebitdaMargin', 'debtToEbitda', 'trend'],
    weights: [0.4, 0.4, 0.2]
  },
  'Consumer Cyclical': {
    metrics: ['growth', 'roe', 'ebitdaMargin', 'trend'],
    weights: [0.3, 0.3, 0.2, 0.2]
  },
  'Industrials': {
    metrics: ['ebitdaMargin', 'debtToEbitda', 'growth', 'trend'],
    weights: [0.3, 0.3, 0.2, 0.2]
  },
  'default': {
    metrics: ['ebitdaMargin', 'debtToEbitda', 'growth', 'roe', 'trend'],
    weights: [0.25, 0.25, 0.2, 0.2, 0.1]
  }
};
