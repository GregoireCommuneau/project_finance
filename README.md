# Project in Finance

A personal project combining exploratory financial data analysis with an interactive web application for company screening and visualization.

## 1. Overview

This project consists of two main parts:

- **v0 – Small Python Project**: Basic exploratory analysis to visualize correlations between stock prices using a local database.
- **Finance Analyzer (Web App)**: A Vue.js-based application to search, filter, and visualize key financial data of listed companies.

## 2. v0 – Small Python Project

An initial prototype developed in Python to:

- Load historical stock price data (e.g., CAC 40, major tech companies)
- Compute correlations
- Visualize relationships using simple plotting libraries (matplotlib, seaborn, etc.)

**Directory structure**

v0/   
├─ connectPostGre_template.py   
├─ correlation_avg.py   
├─ correaltion_dispersion.py   
├─ correlation_graph.py   
├─ correlation_table.py   
├─ correlation_window.py   
├─ data_utils.py   
├─ db_utils.py   
├─ fetch_data.py   
├─ main.py   
├─ plot_utils.py   
├─ query.py   
├─ streamlit_app.py   
└─ test_query.py   



Purpose: serve as a foundation for designing more advanced features in the web app.

## 3. Finance Analyzer (Vue.js Web App)

A modern single-page application that enables users to:

- Search for companies by name or ticker symbol
- Display key financial ratios (e.g., EV/EBITDA, ROE)
- Visualize historical stock prices
- Generate sector-weighted scores
- Cache API responses for performance optimization

### File Structure

src/   
├─ assets/   
├─ components/   
│   ├─ CompanyCard.vue   
│   ├─ CompanyList.vue   
│   ├─ CompanyModal.vue   
│   ├─ FilterPanel.vue   
│   ├─ PriceTrend.vue   
│   ├─ RadarChart.vue   
│   ├─ ScoreChart.vue   
|   └─ Watchlist.vue   
├─ composables/   
│   └─ useCachedData.js   
├─ data/   
│   ├─ companies.js   
│   └─ stockSymbols.js   
├─ router/   
│   └─ index.js   
├─ views/   
│   ├─ About.js   
│   └─ HomeView.js   
├─ App.vue   
├─ main.js   
└─ index.css   

## 4. Getting Started

### Prerequisites

- Node.js v18+
- npm

### Installation

```bash
git clone https://github.com/your-username/finance-analyzer.git
cd finance-analyzer
npm install
npm run dev
```

## 5. Tech Stack

- Vue 3 + Vite
- Tailwind CSS
- Chart.js (vizualisation)
- Financial Modeling Prep API (financial data)

## 6. Roadmap

- Add sector-level dashboards
- User authentification & management
- More complete multi-criteria scoring
- ESG and technical indicators integration
- Also try to apply

## 7. About

This project was built as part of my personal learning in data science and finance, with a focus on combining data analysis, UX design, and modern frontend development.

---

This project uses FMP data under the Starter plan, for educational purposes only. No redistribution or commercial use intended.