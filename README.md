# 📦 Supply Chain Intelligence Dashboard

An end-to-end **Supply Chain Analytics** project — from raw transactional data to a cleaned SQLite database to a fully interactive, filter-driven **Streamlit dashboard** that surfaces evidence-based business findings across sales, customers, inventory, suppliers and logistics.

### 🔗 Live Demo
**[https://supply-chain-dashboard-sdlc.streamlit.app/](https://supply-chain-dashboard-sdlc.streamlit.app/)**

---

## 📖 Overview

This project analyzes the operational and financial data of a mid-size retail/wholesale supply chain business — covering sales, customers, products, inventory, suppliers and shipping logistics. Raw transactional data is cleaned, validated and structured into a query-ready SQLite database, then presented through a 6-page interactive dashboard that lets stakeholders explore performance and identify areas that need attention — with every chart responding live to every filter.

**Scale of the dataset:**

| Metric | Value |
|---|---|
| Orders | 12,040 |
| Customers | 3,015 |
| Products | 1,510 |
| Warehouses | 40 |
| Suppliers | 306 |
| Carriers | 6 |
| Net Sales | ₹630.8M |
| Average Order Value | ₹52,393 |

---

## ✨ Key Features

- **6 dashboard pages** — Executive Overview, Revenue & Product, Customer Intelligence, Inventory & Warehouse, Supplier & Logistics, and Data Quality & Action
- **Fully cross-filtering slicers** — Category, Supplier, Warehouse, Customer Segment and Year all apply consistently to every chart on every page, computed live from order-line-level data (not static pre-aggregated summaries)
- **Interactive Plotly charts** — line, bar, scatter, donut, histogram, funnel and choropleth map charts, each with built-in zoom, pan and image-export controls
- **Data quality auditing** — the dashboard flags and corrects real data issues (stray future-dated records, delivery-time outliers, incomplete order records) rather than presenting raw numbers uncritically
- **Evidence-based recommendations** — findings are backed by specific, calculated metrics (e.g. correlation coefficients, cohort splits) rather than generic dashboard commentary
- **Custom lavender UI theme** — a consistent, presentation-ready visual design across every page

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **Python** | Data cleaning, feature engineering and analysis (pandas, numpy) |
| **SQLite** | Lightweight relational database for raw tables and analytical views |
| **SQLAlchemy** | Database interaction layer during the ETL/build stage |
| **Streamlit** | Interactive web dashboard framework |
| **Plotly Express** | Charting library used throughout the dashboard |

---

## 📁 Project Structure

```
supply-chain-dashboard/
├── dashboard/          # Streamlit dashboard app (supply_chain_dashboard_final.py)
├── data/               # Raw and intermediate data files
├── database/           # Final SQLite database (supply_chain_intelligence.db)
├── docs/               # Documentation and reference material
├── reports/            # Generated reports and exports
├── src/                # Data cleaning, ETL and feature-engineering scripts
├── requirements.txt    # Python dependencies
└── README.md
```

---

## 📊 Dashboard Pages

### 🧠 Executive Overview
A 30-second, company-wide health check — net/gross sales, orders, customers, return rate, monthly revenue trend, the revenue bridge (gross → discounts → returns → net), category contribution, and a new-vs-returning-customer breakdown by year.

### 📊 Revenue & Product
Identifies which products and categories drive value and which combine strong sales with risk — category breakdown, top-product revenue concentration (Pareto), sales-vs-return-rate risk scatter, and stock-vs-sales scatter.

### 👥 Customer Intelligence
Segments customers by value and recency, and maps revenue by country — segment contribution, customer value vs. recency scatter (win-back targeting), and a global revenue choropleth map.

### 🏭 Inventory & Warehouse
Compares stock allocation against actual sales demand across all 40 warehouses — a diverging warehouse-balance chart, an allocation-gap-vs-low-stock correlation scatter, high-value inventory exposure, and stock-vs-value analysis.

### 🚚 Supplier & Logistics
Reviews supplier reliability and carrier performance — supplier rating vs. revenue, carrier cost vs. delivery time (outlier-corrected), supplier revenue concentration, a rating-band donut chart, delivery-time distribution, and late-shipment rates by carrier.

### 🎯 Data Quality & Action
Validates how much of the reported revenue can be trusted, and prioritizes what to fix first — revenue-completeness funnel, net sales by order status (cancelled/returned highlighted), pending-order aging, and a commercial-exposure action list.

---

## 🔍 Key Findings

| # | Finding | Recommended Action |
|---|---|---|
| 1 | New-customer sales share fell from ~40% (2025) to ~7% (2026 YTD) | Run acquisition campaigns and a win-back offer for lapsed customers |
| 2 | ~25% of reported net sales sits in Cancelled or Returned orders | Reconcile revenue-reporting rules with order status before setting targets |
| 3 | Warehouse stock allocation doesn't match sales demand (gap correlates 0.74 with low-stock incidents) | Rebalance stock via inter-warehouse transfer before ordering more inventory |
| 4 | 256 high-value products combine strong sales with return or stock risk | Assign owners and deadlines to this shortlist |
| 5 | 43% of net sales run through suppliers rated below 3/5 | Qualify backup suppliers for high-revenue, low-rated partners |
| 6 | ~1 in 5 shipments takes longer than 14 days to deliver | Set distance-based delivery SLAs and alert on late-trending shipments |

---

## 🧹 Data Quality Corrections

Three real data issues were identified and corrected before finalizing the dashboard:

1. **Customer recency inflated** — a stray, far-future order was skewing the "analysis date," making every customer look less active than they really were. Fixed by detecting the true last-active month directly from order-volume patterns.
2. **Carrier delivery averages skewed** — 55 shipments had implausible 60–305 day delivery windows, distorting carrier averages. Fixed by excluding shipments outside a plausible 0–60 day range and flagging them separately.
3. **False revenue "crash" in the trend chart** — a handful of stray, sparse trailing months made the revenue trend appear to collapse. Fixed by detecting and excluding incomplete trailing months, with a note shown to the viewer.

---

## 🚀 Running Locally

```bash
# 1. Clone the repository
git clone https://github.com/Tishasamnui-24/supply-chain-dashboard.git
cd supply-chain-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run dashboard/supply_chain_dashboard_final.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 🔮 Future Improvements

- Add predictive forecasting (e.g. demand or churn prediction) on top of the current descriptive analytics
- Automate data refresh from a live source instead of a static database snapshot
- Add role-based views (e.g. a simplified view for non-technical stakeholders)

---

## 👤 Author

**Tisha Samui**
Project built as a data analytics / business intelligence portfolio piece using Python, SQL and Streamlit.
