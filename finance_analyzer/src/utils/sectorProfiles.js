export const sectorProfiles = {
  'Financial Services': {
    metrics: ['roe', 'revenue', 'trend'],
    weights: [0.5, 0.3, 0.2]
  },
  'Technology': {
    metrics: ['growth', 'ebitdaMargin', 'revenue', 'trend'],
    weights: [0.3, 0.3, 0.2, 0.2]
  },
  'Healthcare': {
    metrics: ['growth', 'ebitdaMargin', 'revenue', 'trend'],
    weights: [0.2, 0.35, 0.25, 0.2]
  },
  'Utilities': {
    metrics: ['ebitdaMargin', 'debtToEbitda', 'trend'],
    weights: [0.4, 0.4, 0.2]
  },
  'Consumer Cyclical': {
    metrics: ['growth', 'revenue', 'ebitdaMargin', 'trend'],
    weights: [0.3, 0.3, 0.2, 0.2]
  },
  'Industrials': {
    metrics: ['ebitdaMargin', 'debtToEbitda', 'growth', 'trend'],
    weights: [0.3, 0.3, 0.2, 0.2]
  },
  'default': {
    metrics: ['ebitdaMargin', 'debtToEbitda', 'growth', 'revenue', 'trend'],
    weights: [0.25, 0.25, 0.2, 0.2, 0.1]
  }
};
