from contextlib import closing
from pathlib import Path
import os
import sqlite3
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# SUPPLY CHAIN INTELLIGENCE - PRESENTATION VERSION
# Lavender theme | 6 focused pages
# ============================================================

st.set_page_config(
    page_title="Supply Chain Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# LAVENDER COLOR PALETTE
# ------------------------------------------------------------
LAV_1 = "#a78bfa"   # primary lavender
LAV_2 = "#c4b5fd"   # soft lavender
LAV_3 = "#7c3aed"   # deep violet (accent / totals)
LAV_4 = "#ede9fe"   # pale lavender (highlights)
LAV_5 = "#d8b4fe"   # pink-lavender
LAV_6 = "#5b21b6"   # darkest violet
LAV_WARN = "#f0abfc"  # warm pink-magenta for warnings/negatives

LAVENDER_SEQUENCE = [LAV_1, LAV_2, LAV_3, LAV_5, LAV_6, "#ddd6fe", "#8b5cf6", "#f0abfc"]
LAVENDER_CONTINUOUS = [[0, "#1e1b2e"], [0.5, LAV_3], [1, LAV_4]]

px.defaults.color_discrete_sequence = LAVENDER_SEQUENCE
px.defaults.color_continuous_scale = LAVENDER_CONTINUOUS

DB_NAME = "supply_chain_intelligence.db"


def find_db_file():
    """Locate database/supply_chain_intelligence.db wherever this file is saved.

    Order: 1) env var SUPPLY_CHAIN_DB (full path)  2) this script's folder and all
    its parents  3) the current working folder and all its parents.
    """
    env_path = os.environ.get("SUPPLY_CHAIN_DB")
    if env_path and Path(env_path).is_file():
        return Path(env_path)
    for start in (Path(__file__).resolve().parent, Path.cwd().resolve()):
        for folder in (start, *start.parents):
            candidate = folder / "database" / DB_NAME
            if candidate.is_file():
                return candidate
    return None


DB_FILE = find_db_file()

# ------------------------------------------------------------
# THEME
# ------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #150f24;
    --blue: #7c3aed;
    --blue2: #a78bfa;
    --green: #c4b5fd;
    --green2: #ede9fe;
    --text: #f3f0ff;
    --muted: #a9a0c4;
    --card: #221a38;
    --border: rgba(196, 181, 253, .20);
}
html, body, [class*="css"] { font-family: Inter, Segoe UI, sans-serif; }
.stApp {
    background: linear-gradient(180deg, #100b1c 0%, #170f29 55%, #150f24 100%);
    color: var(--text);
}
.block-container { max-width: 1500px; padding-top: 3rem; padding-bottom: 2.5rem; }
header[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #120c1f; border-right: 1px solid var(--border); }

.brand { padding: .3rem .1rem 1rem; }
.brand-title { font-weight: 800; font-size: 1.12rem; color: #fff; }
.brand-sub { color: var(--muted); font-size: .72rem; margin-top: .15rem; }

.page-title {
    font-size: 2rem; font-weight: 800; letter-spacing: -.035em;
    line-height: 1.3; margin-bottom: .15rem;
}
.page-subtitle { color: var(--muted); font-size: .85rem; margin-bottom: 1rem; }
.section-title {
    font-size: 1.08rem; font-weight: 800; color: #fff;
    margin: 1.1rem 0 .45rem 0;
}
.section-note { color: var(--muted); font-size: .73rem; margin-top: -.25rem; margin-bottom: .45rem; }

.metric-card {
    background: linear-gradient(145deg, #29204a, #1d1633);
    border: 1px solid rgba(167,139,250,.25);
    border-radius: 16px; padding: .9rem 1rem; min-height: 118px;
    box-shadow: 0 12px 30px rgba(0,0,0,.18);
}
.metric-label { color: #c3b6e6; font-size: .70rem; font-weight: 700; }
.metric-value { color: #fff; font-size: 1.55rem; font-weight: 800; margin-top: .55rem; }
.metric-help { color: #8b7fae; font-size: .64rem; margin-top: .25rem; }
.metric-accent { color: var(--green); }

.insight {
    border-left: 3px solid var(--blue2);
    background: rgba(167,139,250,.08);
    border-top: 1px solid var(--border); border-right: 1px solid var(--border); border-bottom: 1px solid var(--border);
    border-radius: 12px; padding: .75rem .9rem; margin-top: .6rem;
    color: #ece6fb; font-size: .78rem; line-height: 1.45;
}
.badge { display:inline-block; padding:.22rem .48rem; border-radius:999px; font-size:.62rem; font-weight:700; margin-right:.25rem; }
.badge-blue { background:rgba(124,58,237,.18); color:#c4b5fd; }
.badge-green { background:rgba(196,181,253,.16); color:#e9d5ff; }

.takeaway {
    background: linear-gradient(135deg, rgba(124,58,237,.20), rgba(167,139,250,.08));
    border: 1px solid rgba(196,181,253,.35);
    border-left: 4px solid #a78bfa;
    border-radius: 12px; padding: .85rem 1.1rem; margin: .3rem 0 1.1rem 0;
    color: #f3f0ff; font-size: .85rem; line-height: 1.5;
}
.takeaway b.tk-label { color: #d8b4fe; text-transform: uppercase; font-size: .68rem; letter-spacing: .06em; }

.tldr {
    background: linear-gradient(135deg, #2c2150, #1d1633 65%);
    border: 1px solid rgba(196,181,253,.4);
    border-radius: 16px; padding: 1.1rem 1.3rem; margin-bottom: 1.3rem;
    box-shadow: 0 14px 34px rgba(0,0,0,.25);
}
.tldr-title { color: #e9d5ff; font-weight: 800; font-size: .82rem; text-transform: uppercase; letter-spacing: .06em; margin-bottom: .55rem; }
.tldr ul { margin: 0; padding-left: 1.1rem; }
.tldr li { color: #f3f0ff; font-size: .88rem; line-height: 1.6; margin-bottom: .25rem; }
.tldr li b { color: #d8b4fe; }

/* Keep Streamlit dropdowns visually clean */
div[data-baseweb="select"] > div { background: #201936; border-color: rgba(196,181,253,.25); }
label { color: #e3d9f7 !important; font-weight: 600 !important; }

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# DATA
# ------------------------------------------------------------
@st.cache_data(ttl=600)
def load_view(view):
    allowed = {
        "vw_executive_summary", "vw_monthly_performance", "vw_category_performance",
        "vw_product_performance", "vw_customer_performance", "vw_warehouse_performance",
        "vw_supplier_performance", "vw_carrier_performance", "vw_revenue_quality",
        "vw_order_status_performance", "vw_quality_summary", "vw_action_center"
    }
    if view not in allowed:
        raise ValueError("Unsupported view")
    with closing(sqlite3.connect(DB_FILE)) as con:
        return pd.read_sql_query(f"SELECT * FROM {view}", con)

if DB_FILE is None:
    st.error(f"❌ Database file not found: database/{DB_NAME}")
    st.info(
        "Save this file inside your project (e.g. <project>/dashboard/) so that "
        f"<project>/database/{DB_NAME} exists, then run from the project folder:\n\n"
        "streamlit run dashboard/supply_chain_dashboard_final.py"
    )
    st.stop()

try:
    executive = load_view("vw_executive_summary")
    monthly = load_view("vw_monthly_performance")
    category = load_view("vw_category_performance")
    products = load_view("vw_product_performance")
    customers = load_view("vw_customer_performance")
    warehouses = load_view("vw_warehouse_performance")
    suppliers = load_view("vw_supplier_performance")
    carriers = load_view("vw_carrier_performance")
    quality = load_view("vw_revenue_quality")
    order_status = load_view("vw_order_status_performance")
    quality_summary = load_view("vw_quality_summary")
    actions = load_view("vw_action_center")
except Exception as e:
    st.error(f"Database could not be loaded: {e}")
    st.stop()

ex = executive.iloc[0] if not executive.empty else pd.Series(dtype=float)

# ------------------------------------------------------------
# DATA QUALITY CORRECTIONS
# A small number of stray, far-future order/shipment records skew
# three things if used as-is: the monthly trend's trailing months,
# customer recency, and carrier delivery-day averages. All three are
# corrected here directly from the raw tables — nothing is hidden,
# nothing is hard-coded to a fixed date.
# ------------------------------------------------------------
@st.cache_data(ttl=600)
def load_table(table):
    allowed = {"order_features", "fact_shipments"}
    if table not in allowed:
        raise ValueError("Unsupported table")
    with closing(sqlite3.connect(DB_FILE)) as con:
        return pd.read_sql_query(f"SELECT * FROM {table}", con)

try:
    orders_raw = load_table("order_features")
    shipments_raw = load_table("fact_shipments")
except Exception:
    orders_raw = pd.DataFrame()
    shipments_raw = pd.DataFrame()

# 1) find the true "last normal" month of activity (a month is normal
#    if it has at least a quarter of the median monthly order volume);
#    anything after that is treated as stray/incomplete data.
CUTOFF_DATE = pd.to_datetime(monthly["month"], errors="coerce").max()
if not orders_raw.empty:
    orders_raw["order_date"] = pd.to_datetime(orders_raw["order_date"], errors="coerce")
    monthly_counts = orders_raw.dropna(subset=["order_date"]).groupby(
        orders_raw["order_date"].dt.to_period("M")
    ).size()
    if len(monthly_counts):
        threshold = max(monthly_counts.median() * 0.25, 20)
        normal_months = monthly_counts[monthly_counts >= threshold]
        if len(normal_months):
            CUTOFF_DATE = normal_months.index.max().to_timestamp(how="end").normalize()

# 2) recompute customer recency against CUTOFF_DATE instead of the
#    stored analysis_date (which is pulled from a stray future order)
if not orders_raw.empty:
    valid_orders = orders_raw[orders_raw["order_date"] <= CUTOFF_DATE]
    last_order_ok = valid_orders.groupby("customer_id")["order_date"].max()
    customers["recency_adj"] = customers["customer_id"].map(last_order_ok)
    customers["recency_adj"] = (CUTOFF_DATE - customers["recency_adj"]).dt.days
else:
    customers["recency_adj"] = customers.get("days_since_last_order")

# 3) recompute carrier delivery time excluding shipments with an
#    implausible delivery window (>60 days), which otherwise pull a
#    simple mean far away from what most shipments actually experience
if not shipments_raw.empty:
    sh = shipments_raw.copy()
    sh["shipment_date"] = pd.to_datetime(sh["shipment_date"], errors="coerce")
    sh["delivery_date"] = pd.to_datetime(sh["delivery_date"], errors="coerce")
    sh["delivery_days"] = (sh["delivery_date"] - sh["shipment_date"]).dt.days
    sh_valid = sh[(sh["delivery_days"] >= 0) & (sh["delivery_days"] <= 60)]
    sh_anomaly = sh[sh["delivery_days"] > 60]
    carrier_fixed = sh_valid.groupby("carrier").agg(
        avg_delivery_days=("delivery_days", "mean"),
        median_delivery_days=("delivery_days", "median"),
        late_14d_rate=("delivery_days", lambda x: (x > 14).mean()),
    ).reset_index()
    anomaly_counts = sh_anomaly.groupby("carrier").size().rename("anomaly_count").reset_index()
    carrier_fixed = carrier_fixed.merge(anomaly_counts, on="carrier", how="left")
    carrier_fixed["anomaly_count"] = carrier_fixed["anomaly_count"].fillna(0)
    carriers = carriers.merge(carrier_fixed, on="carrier", how="left")
else:
    sh_valid = pd.DataFrame(columns=["delivery_days", "carrier"])
    carriers["avg_delivery_days"] = carriers.get("average_delivery_days")
    carriers["late_14d_rate"] = np.nan
    carriers["anomaly_count"] = 0

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def money(v):
    if pd.isna(v): return "—"
    v = float(v)
    if abs(v) >= 1e9: return f"₹{v/1e9:.2f}B"
    if abs(v) >= 1e6: return f"₹{v/1e6:.2f}M"
    if abs(v) >= 1e3: return f"₹{v/1e3:.1f}K"
    return f"₹{v:,.0f}"

def integer(v):
    if pd.isna(v): return "—"
    return f"{float(v):,.0f}"

def pct(v):
    if pd.isna(v): return "—"
    return f"{float(v)*100:.2f}%"

def heading(title, icon, subtitle=""):
    st.markdown(f'<div class="page-title"><b>{icon} {title}</b></div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def takeaway(text):
    st.markdown(f'<div class="takeaway"><b class="tk-label">🎯 Key Takeaway</b><br>{text}</div>', unsafe_allow_html=True)

def tldr(items):
    lis = "".join(f"<li>{it}</li>" for it in items)
    st.markdown(f'<div class="tldr"><div class="tldr-title">🚦 The Big Picture — 3 Things To Know</div><ul>{lis}</ul></div>', unsafe_allow_html=True)

def section(title, icon, note=""):
    st.markdown(f'<div class="section-title"><b>{icon} {title}</b></div>', unsafe_allow_html=True)
    if note:
        st.markdown(f'<div class="section-note">{note}</div>', unsafe_allow_html=True)

def kpi(col, icon, label, value, help_text=""):
    with col:
        st.markdown(f'''<div class="metric-card">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-help">{help_text}</div>
        </div>''', unsafe_allow_html=True)

def fig_style(fig, height=390, dark=False):
    paper = "#120c1f" if dark else "rgba(0,0,0,0)"
    plot = "#120c1f" if dark else "rgba(0,0,0,0)"
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=58, b=22),
        paper_bgcolor=paper,
        plot_bgcolor=plot,
        font=dict(family="Inter, Segoe UI, sans-serif", color="#ece6fb"),
        title_font=dict(size=16, color="#ffffff"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hoverlabel=dict(bgcolor="#221a38", font_color="#ffffff"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(196,181,253,.20)")
    fig.update_yaxes(gridcolor="rgba(196,181,253,.12)", zeroline=False)
    return fig

def apply_filters(df, category_filter, supplier_filter, warehouse_filter, segment_filter):
    out = df.copy()
    if category_filter != "All" and "category" in out.columns:
        out = out[out["category"].astype(str).eq(category_filter)]
    if supplier_filter != "All" and "supplier_name" in out.columns:
        out = out[out["supplier_name"].astype(str).eq(supplier_filter)]
    if warehouse_filter != "All" and "warehouse_name" in out.columns:
        out = out[out["warehouse_name"].astype(str).eq(warehouse_filter)]
    if segment_filter != "All" and "segment" in out.columns:
        out = out[out["segment"].astype(str).eq(segment_filter)]
    return out

def chart(fig, height=390):
    st.plotly_chart(fig_style(fig, height), width="stretch", config={"displayModeBar": False})

# ------------------------------------------------------------
# SIDEBAR / DROPDOWN SLICERS
# ------------------------------------------------------------
st.sidebar.markdown('<div class="brand"><div class="brand-title">📦 Supply Chain Intelligence</div><div class="brand-sub">Presentation-ready analytics dashboard</div></div>', unsafe_allow_html=True)

page = st.sidebar.selectbox("📑 Dashboard Page", [
    "Executive Overview",
    "Revenue & Product",
    "Customer Intelligence",
    "Inventory & Warehouse",
    "Supplier & Logistics",
    "Data Quality & Action",
])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Filters")

categories = ["All"] + sorted(category["category"].dropna().astype(str).unique().tolist())
suppliers_list = ["All"] + sorted(suppliers["supplier_name"].dropna().astype(str).unique().tolist())
warehouses_list = ["All"] + sorted(warehouses["warehouse_name"].dropna().astype(str).unique().tolist())
segments = ["All"] + sorted(customers["segment"].dropna().astype(str).unique().tolist())

years = sorted(pd.to_datetime(monthly["month"], errors="coerce").dt.year.dropna().astype(int).unique().tolist())
year_options = ["All"] + [str(y) for y in years]

f_category = st.sidebar.selectbox("Category", categories)
f_supplier = st.sidebar.selectbox("Supplier", suppliers_list)
f_warehouse = st.sidebar.selectbox("Warehouse", warehouses_list)
f_segment = st.sidebar.selectbox("Customer Segment", segments)
f_year = st.sidebar.selectbox("Year", year_options)

if f_year != "All":
    monthly_filtered = monthly[pd.to_datetime(monthly["month"]).dt.year.eq(int(f_year))].copy()
else:
    monthly_filtered = monthly.copy()

products_f = apply_filters(products, f_category, f_supplier, f_warehouse, f_segment)
customers_f = apply_filters(customers, f_category, f_supplier, f_warehouse, f_segment)
warehouses_f = apply_filters(warehouses, f_category, f_supplier, f_warehouse, f_segment)
suppliers_f = apply_filters(suppliers, f_category, f_supplier, f_warehouse, f_segment)
actions_f = apply_filters(actions, f_category, f_supplier, f_warehouse, f_segment)

st.sidebar.markdown("---")
st.sidebar.markdown('<span class="badge badge-blue">SQLITE</span><span class="badge badge-green">ANALYTICAL VIEWS</span>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 1. EXECUTIVE OVERVIEW
# ------------------------------------------------------------
if page == "Executive Overview":
    heading("Executive Overview", "🧠", "A compact management view of revenue, orders, customers and commercial health.")
    tldr([
        "<b>Growth is slowing</b> — new-customer sales share fell from ~40% (2025) to ~7% (2026 YTD); the growth engine is running out of new buyers, not existing demand.",
        "<b>~25% of reported revenue isn't real yet</b> — it sits in Cancelled or Returned orders, so headline sales numbers overstate what actually landed.",
        "<b>Operational risk is concentrated</b> — 43% of supplier revenue runs through suppliers rated below 3/5, and warehouse stock is measurably misaligned with where sales happen (0.74 correlation with low-stock items).",
    ])
    c = st.columns(5, gap="medium")
    kpi(c[0], "💰", "Net Sales", money(ex.get("net_sales")), "After discounts and returns")
    kpi(c[1], "📈", "Gross Sales", money(ex.get("gross_sales")), "Before discounts and returns")
    kpi(c[2], "🛒", "Orders", integer(ex.get("total_orders")), "Total recorded orders")
    kpi(c[3], "👥", "Customers", integer(ex.get("customers")), "Customer master records")
    kpi(c[4], "↩️", "Return Rate", pct(ex.get("return_rate")), "Returned units / sold units")

    mt = monthly_filtered.copy()
    mt["month"] = pd.to_datetime(mt["month"], errors="coerce")
    mt_display = mt[mt["month"] <= CUTOFF_DATE].sort_values("month")
    dropped = len(mt) - len(mt_display)
    note = "Gross sales and net sales movement over time."
    if dropped > 0:
        note += f" {dropped} trailing month(s) with too few orders to be representative were excluded from the trend line."
    section("Monthly Revenue Trend", "📈", note)
    trend_long = mt_display.melt(id_vars="month", value_vars=["gross_sales", "net_sales"],
                                   var_name="type", value_name="sales")
    trend_long["type"] = trend_long["type"].map({"gross_sales": "Gross Sales", "net_sales": "Net Sales"})
    fig = px.line(trend_long, x="month", y="sales", color="type", markers=True,
                   title="Gross vs Net Sales",
                   color_discrete_map={"Gross Sales": LAV_2, "Net Sales": LAV_3})
    fig.update_traces(line=dict(width=3))
    fig.update_layout(xaxis_title="Month", yaxis_title="Sales", legend_title="")
    chart(fig, 400)

    a, b = st.columns(2, gap="large")
    with a:
        section("Revenue Bridge", "🌉", "How gross sales become net sales after discounts and returns.")
        bridge_df = pd.DataFrame({
            "stage": ["Gross Sales", "Discounts", "Returns", "Net Sales"],
            "amount": [float(ex.get("gross_sales", 0)), float(ex.get("discount_amount", 0)), float(ex.get("return_amount", 0)), float(ex.get("net_sales", 0))],
        })
        wf = px.bar(bridge_df, x="stage", y="amount", color="stage", text="amount",
                     title="Gross Sales, Discounts, Returns & Net Sales",
                     color_discrete_map={"Gross Sales": LAV_3, "Discounts": LAV_WARN, "Returns": LAV_WARN, "Net Sales": LAV_2})
        wf.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        wf.update_layout(showlegend=False, yaxis_title="Value", xaxis_title="")
        chart(wf, 400)
    with b:
        section("Category Contribution", "🧩", "Which categories contribute the most net sales?")
        cat = category.sort_values("net_sales", ascending=False).head(10)
        fig = px.bar(cat, x="category", y="net_sales", title="Top Categories by Net Sales")
        fig.update_traces(marker_color=LAV_2)
        fig.update_layout(xaxis_title="Category", yaxis_title="Net Sales")
        chart(fig, 400)

    if not orders_raw.empty:
        section("New vs Returning Customers", "🌱", "Share of each year's net sales coming from customers placing their first-ever order that year, versus customers who had already ordered before.")
        orv = orders_raw.dropna(subset=["order_date"]).copy()
        orv["year"] = orv["order_date"].dt.year
        first_year = orv.groupby("customer_id")["year"].transform("min")
        orv["customer_type"] = np.where(orv["year"] == first_year, "New Customer", "Returning Customer")
        yr_cutoff = CUTOFF_DATE.year
        orv = orv[(orv["year"] < yr_cutoff) | ((orv["year"] == yr_cutoff) & (orv["order_date"] <= CUTOFF_DATE))]
        yearly = orv.groupby(["year", "customer_type"], as_index=False)["net_sales"].sum()
        fig = px.bar(yearly, x="year", y="net_sales", color="customer_type", barmode="stack",
                     title="Net Sales by Customer Type, by Year",
                     color_discrete_map={"New Customer": LAV_2, "Returning Customer": LAV_6})
        fig.update_layout(xaxis_title="Year", yaxis_title="Net Sales", xaxis=dict(dtick=1))
        chart(fig, 380)

# ------------------------------------------------------------
# 2. REVENUE & PRODUCT
# ------------------------------------------------------------
elif page == "Revenue & Product":
    heading("Revenue & Product", "📊", "Understand where revenue comes from and which products combine value with risk.")
    takeaway("Revenue is <b>not</b> concentrated in a handful of products — the portfolio is fairly broad. The real risk is a smaller set of high-selling products that also carry above-average return rates or have fallen below their reorder point, which the two scatter charts below surface directly.")
    p = products_f.copy()
    c = st.columns(4, gap="medium")
    kpi(c[0], "💰", "Filtered Net Sales", money(p["net_sales"].sum()), "Based on selected product filters")
    kpi(c[1], "📦", "Products", integer(p["product_id"].nunique()), "Products in current selection")
    kpi(c[2], "↩️", "Return Rate", pct(p["units_returned"].sum()/p["units_sold"].sum()) if p["units_sold"].sum() else "—", "Current selection")
    kpi(c[3], "⚠️", "Below Reorder", integer(p["below_reorder_flag"].sum()), "Products below reorder level")

    a, b = st.columns(2, gap="large")
    with a:
        section("Revenue by Category", "💰")
        cat = category.copy()
        if f_category != "All": cat = cat[cat["category"].eq(f_category)]
        fig = px.bar(cat.sort_values("net_sales", ascending=True), x="net_sales", y="category", orientation="h", title="Net Sales by Category")
        fig.update_traces(marker_color=LAV_2)
        chart(fig, 390)
    with b:
        section("Revenue Concentration", "🎯", "Top products and their cumulative revenue contribution.")
        pareto = p.sort_values("net_sales", ascending=False).head(15).copy()
        pareto["cumulative_share"] = pareto["net_sales"].cumsum() / max(p["net_sales"].sum(), 1) * 100
        fig = px.bar(pareto, x="product_name", y="net_sales", title="Top 15 Products by Net Sales")
        fig.update_traces(marker_color=LAV_1)
        fig.update_layout(xaxis_tickangle=-45, xaxis_title="", yaxis_title="Net Sales")
        chart(fig, 300)
        fig2 = px.line(pareto, x="product_name", y="cumulative_share", markers=True, title="Cumulative Revenue Share (%)")
        fig2.update_traces(line=dict(color=LAV_5, width=3))
        fig2.update_layout(xaxis_tickangle=-45, xaxis_title="", yaxis_title="Cumulative Share %", yaxis_range=[0, 100])
        chart(fig2, 300)

    a, b = st.columns(2, gap="large")
    with a:
        section("Commercial Value × Return Risk", "↩️")
        s = p[p["units_sold"] > 0].copy()
        fig = px.scatter(s, x="net_sales", y="return_rate", size="units_sold", hover_name="product_name", color="category", title="Sales vs Return Rate")
        fig.update_yaxes(tickformat=".1%")
        chart(fig, 400)
    with b:
        section("Commercial Value × Stock Position", "📦")
        s = p[p["units_sold"] > 0].copy()
        fig = px.scatter(s, x="net_sales", y="stock_to_reorder_ratio", size="units_sold", hover_name="product_name", color="below_reorder_flag", title="Sales vs Stock / Reorder Ratio")
        fig.update_yaxes(title="Stock / Reorder Ratio")
        chart(fig, 400)

# ------------------------------------------------------------
# 3. CUSTOMER INTELLIGENCE + WORLD MAP
# ------------------------------------------------------------
elif page == "Customer Intelligence":
    heading("Customer Intelligence", "👥", "Identify valuable segments, customer recency patterns and geographic revenue concentration.")
    takeaway("Nearly 90% of customers are repeat buyers and revenue is evenly split across segments (~22–24% each) — the customer base itself is healthy. The opportunity is in the scatter chart below: it identifies specific high-value customers who have gone quiet and are worth a win-back campaign.")
    c = st.columns(4, gap="medium")
    kpi(c[0], "👥", "Customers", integer(customers_f["customer_id"].nunique()), "Current selection")
    kpi(c[1], "💰", "Customer Net Sales", money(customers_f["net_sales"].sum()), "Revenue from selected customers")
    kpi(c[2], "🔁", "Repeat Customers", integer(customers_f["repeat_customer_flag"].sum()), "Customers with repeat orders")
    kpi(c[3], "⏳", "Avg Recency", integer(customers_f["recency_adj"].mean()), "Days since last order, corrected for stray future-dated records")

    a, b = st.columns(2, gap="large")
    with a:
        section("Segment Contribution", "🎯")
        seg = customers_f.groupby("segment", as_index=False)["net_sales"].sum().sort_values("net_sales", ascending=False)
        fig = px.bar(seg, x="segment", y="net_sales", title="Net Sales by Customer Segment")
        fig.update_traces(marker_color=LAV_2)
        chart(fig, 390)
    with b:
        section("Customer Value × Recency", "⏳", "Recency is measured against the true last-active month, not the raw analysis date.")
        s = customers_f[(customers_f["net_sales"] > 0) & customers_f["recency_adj"].notna()].copy()
        fig = px.scatter(s, x="recency_adj", y="net_sales", size="order_count", color="segment", hover_name="customer_name", title="Customer Value vs Days Since Last Order")
        fig.update_xaxes(title="Days Since Last Order (corrected)")
        chart(fig, 390)

    section("🌍 Customer Revenue by Country", "🌍", "Dark world map showing geographic concentration of customer net sales.")
    country = customers_f.groupby("country", as_index=False)["net_sales"].sum()
    map_fig = px.choropleth(country, locations="country", locationmode="country names", color="net_sales", hover_name="country", color_continuous_scale=LAVENDER_CONTINUOUS, title="Global Customer Revenue")
    map_fig.update_geos(bgcolor="#120c1f", showland=True, landcolor="#1d1633", showocean=True, oceancolor="#120c1f", showcountries=True, countrycolor="#3d3260", showframe=False)
    map_fig.update_layout(paper_bgcolor="#120c1f", plot_bgcolor="#120c1f", font_color="#ece6fb", margin=dict(l=0,r=0,t=55,b=0), height=470)
    st.plotly_chart(map_fig, width="stretch", config={"displayModeBar": False})

# ------------------------------------------------------------
# 4. INVENTORY & WAREHOUSE
# ------------------------------------------------------------
elif page == "Inventory & Warehouse":
    heading("Inventory & Warehouse", "🏭", "Compare inventory footprint with sales demand and highlight potential stock pressure.")
    takeaway("Stock is measurably misallocated: warehouses that are under-stocked relative to their sales also carry more low-stock items (0.74 correlation). Moving stock from over-stocked to under-stocked warehouses — rather than buying more inventory — is the fastest fix.")
    w = warehouses_f.copy()
    p = products_f.copy()
    c = st.columns(4, gap="medium")
    kpi(c[0], "📦", "Total Stock", integer(w["total_stock"].sum()), "Units across selected warehouses")
    kpi(c[1], "🏭", "Warehouses", integer(w["warehouse_id"].nunique()), "Current selection")
    kpi(c[2], "⚠️", "Low-stock Items", integer(w["low_stock_items"].sum()), "Items below stock threshold")
    kpi(c[3], "📈", "Sales Share", pct(w["sales_share"].sum()), "Share represented by selection")

    a, b = st.columns(2, gap="large")
    with a:
        section("Warehouse Balance", "⚖️", "Sales share minus stock share, per warehouse. Bars to the right hold less stock than their sales justify (stockout risk); bars to the left hold more stock than they sell (tied-up capital).")
        wb = w[["warehouse_name", "stock_share", "sales_share", "low_stock_items"]].copy()
        wb["gap"] = wb["sales_share"] - wb["stock_share"]
        wb = wb.sort_values("gap")
        fig = px.bar(wb, x="gap", y="warehouse_name", orientation="h",
                      color=wb["gap"] > 0,
                      color_discrete_map={True: LAV_WARN, False: LAV_2},
                      title="Sales Share − Stock Share, by Warehouse")
        fig.update_layout(showlegend=False, xaxis_tickformat="+.1%", xaxis_title="Sales share − Stock share", yaxis_title="")
        fig.add_vline(x=0, line_color="rgba(196,181,253,.4)")
        chart(fig, 620)
    with b:
        section("Imbalance Drives Low Stock", "🔎", "Warehouses more under-stocked relative to demand tend to carry more low-stock items.")
        wb2 = wb.copy()
        fig = px.scatter(wb2, x="gap", y="low_stock_items", size=w.loc[wb2.index, "total_stock"], hover_name="warehouse_name",
                          title="Allocation Gap vs Low-Stock Items")
        fig.update_layout(xaxis_tickformat="+.1%", xaxis_title="Sales share − Stock share", yaxis_title="Low-Stock Items")
        fig.add_vline(x=0, line_color="rgba(196,181,253,.4)")
        chart(fig, 300)
        corr = wb2["gap"].corr(wb2["low_stock_items"])
        st.markdown(f'<div class="insight">📌 Correlation between allocation gap and low-stock items: <b>{corr:.2f}</b> — the more under-stocked a warehouse is relative to its sales, the more items in it run low.</div>', unsafe_allow_html=True)

    a, b = st.columns(2, gap="large")
    with a:
        section("High-value Inventory Exposure", "🚨", "Products combining commercial value with below-reorder status.")
        risk = p[p["below_reorder_flag"] == 1].sort_values("net_sales", ascending=False).head(15)
        fig = px.bar(risk, x="net_sales", y="product_name", orientation="h", color="category", title="Top Below-Reorder Products by Net Sales")
        chart(fig, 410)
    with b:
        section("Stock vs Commercial Value", "🔎")
        s = p[p["net_sales"] > 0].copy()
        fig = px.scatter(s, x="current_stock", y="net_sales", size="units_sold", color="category", hover_name="product_name", title="Current Stock vs Net Sales")
        chart(fig, 410)

# ------------------------------------------------------------
# 5. SUPPLIER & LOGISTICS
# ------------------------------------------------------------
elif page == "Supplier & Logistics":
    heading("Supplier & Logistics", "🚚", "Review supplier contribution and carrier cost-service patterns.")
    takeaway("Supplier rating and sales volume barely correlate — <b>43% of net sales run through suppliers rated below 3/5</b>, a concentration risk if any one of them fails to deliver. Separately, about 1 in 5 shipments takes longer than 14 days to arrive, fairly evenly across carriers.")
    c = st.columns(4, gap="medium")
    kpi(c[0], "🏭", "Suppliers", integer(suppliers_f["supplier_id"].nunique()), "Current selection")
    kpi(c[1], "💰", "Supplier Net Sales", money(suppliers_f["net_sales"].sum()), "Associated commercial value")
    kpi(c[2], "🚚", "Carriers", integer(carriers["carrier"].nunique()), "Shipment carriers")
    kpi(c[3], "💸", "Shipping Cost", money(carriers["total_shipping_cost"].sum()), "Total recorded shipping cost")

    a, b = st.columns(2, gap="large")
    with a:
        section("Supplier Contribution × Rating", "⭐")
        s = suppliers_f.copy()
        fig = px.scatter(s, x="rating", y="net_sales", size="product_count", color="country", hover_name="supplier_name", title="Supplier Rating vs Net Sales")
        chart(fig, 400)
    with b:
        section("Carrier Cost × Delivery Time", "🚚", "Delivery time excludes shipments with implausible delivery windows (>60 days).")
        s = carriers.copy()
        fig = px.scatter(s, x="average_shipping_cost", y="avg_delivery_days", size="shipment_count", hover_name="carrier", title="Average Shipping Cost vs Delivery Days (corrected)")
        fig.update_yaxes(title="Avg Delivery Days (corrected)")
        chart(fig, 400)

    a, b = st.columns(2, gap="large")
    with a:
        section("Supplier Revenue Concentration", "🎯")
        top = suppliers_f.sort_values("net_sales", ascending=False).head(12)
        fig = px.bar(top.sort_values("net_sales"), x="net_sales", y="supplier_name", orientation="h", title="Top Suppliers by Net Sales")
        fig.update_traces(marker_color=LAV_2)
        chart(fig, 400)
    with b:
        section("Net Sales Share by Supplier Rating", "⭐", "Rating and revenue don't line up — a meaningful share of sales sits with lower-rated suppliers.")
        sr = suppliers_f.dropna(subset=["rating"]).copy()
        if sr.empty:
            st.info("No supplier data for the current filter selection.")
        else:
            band_labels = ["1–2 (Poor)", "2–3 (Below Avg)", "3–4 (Good)", "4–5 (Excellent)"]
            sr["rating_band"] = pd.cut(sr["rating"], [0, 2, 3, 4, 5], labels=band_labels)
            band = sr.groupby("rating_band", observed=True, as_index=False)["net_sales"].sum()
            band_colors = {"1–2 (Poor)": LAV_6, "2–3 (Below Avg)": LAV_3, "3–4 (Good)": LAV_1, "4–5 (Excellent)": "#e9d5ff"}
            fig = px.pie(band, names="rating_band", values="net_sales", hole=0.68,
                          color="rating_band", color_discrete_map=band_colors,
                          category_orders={"rating_band": band_labels},
                          title="Net Sales Share by Supplier Rating Band")
            fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#150f24", width=1)))
            chart(fig, 400)

    a, b = st.columns(2, gap="large")
    with a:
        section("Delivery Time Distribution", "⏱️", "Most shipments arrive quickly, but roughly 1 in 5 takes more than 14 days.")
        fig = px.histogram(sh_valid, x="delivery_days", nbins=30, title="Delivery Days Distribution (excl. anomalies >60 days)")
        fig.update_traces(marker_color=LAV_2)
        fig.add_vline(x=14, line_dash="dash", line_color=LAV_WARN, annotation_text="14 days")
        fig.update_layout(xaxis_title="Delivery Days", yaxis_title="Shipments")
        chart(fig, 380)
    with b:
        section("Late Shipments by Carrier", "🚨", "Share of each carrier's shipments delivered more than 14 days after dispatch.")
        cr = carriers.dropna(subset=["late_14d_rate"]).sort_values("late_14d_rate", ascending=False)
        fig = px.bar(cr, x="carrier", y="late_14d_rate", title="% Shipments Delivered Later Than 14 Days")
        fig.update_traces(marker_color=LAV_WARN)
        fig.update_yaxes(tickformat=".0%", title="% Late (>14 days)")
        chart(fig, 380)

# ------------------------------------------------------------
# 6. DATA QUALITY & ACTION
# ------------------------------------------------------------
else:
    heading("Data Quality & Action", "🎯", "Validate analytical confidence and surface evidence-based areas that deserve investigation.")
    takeaway("About a quarter of reported net sales sits in Cancelled or Returned orders, and a large share of Pending orders are over a year old and unlikely to ever convert. Treat headline revenue figures as directional until these are reconciled with order status.")
    q = quality_summary.iloc[0] if not quality_summary.empty else pd.Series(dtype=float)
    c = st.columns(4, gap="medium")
    kpi(c[0], "✅", "Complete Revenue", integer(q.get("complete_revenue_orders")), "Orders with complete revenue detail")
    kpi(c[1], "⚠️", "Partial Revenue", integer(q.get("partial_revenue_orders")), "Orders with partial detail")
    kpi(c[2], "❌", "No Detail", integer(q.get("no_detail_orders")), "Orders without usable detail")
    kpi(c[3], "🚚", "Delivery Anomalies", integer(q.get("delivery_anomaly_orders")), "Shipment timing anomalies")

    a, b = st.columns(2, gap="large")
    with a:
        section("Revenue Data Confidence", "🔎")
        qdf = quality.copy()
        fig = px.funnel(qdf, y="revenue_completeness_status", x="orders", title="Revenue Completeness")
        fig.update_traces(marker_color=LAV_2)
        chart(fig, 400)
    with b:
        section("Net Sales by Order Status", "📋", "About a quarter of reported net sales sits in Cancelled or Returned orders.")
        os = order_status.copy()
        os["is_final"] = os["order_status"].isin(["Cancelled", "Returned"])
        os = os.sort_values("net_sales", ascending=False)
        fig = px.bar(os, x="order_status", y="net_sales", color="is_final",
                      color_discrete_map={True: LAV_WARN, False: LAV_2},
                      title="Net Sales by Order Status")
        fig.update_layout(showlegend=False, yaxis_title="Net Sales")
        chart(fig, 400)

    if not orders_raw.empty:
        section("Pending Order Aging", "⏳", "How long orders have sat in Pending status, as of the last fully-recorded month. Older pending orders are less likely to ever convert.")
        pend = orders_raw[(orders_raw["order_status"] == "Pending") & (orders_raw["order_date"] <= CUTOFF_DATE)].copy()
        pend["age_days"] = (CUTOFF_DATE - pend["order_date"]).dt.days
        bins = [-1, 30, 90, 180, 365, 10_000]
        labels = ["0–30d", "31–90d", "91–180d", "181–365d", "365d+"]
        pend["bucket"] = pd.cut(pend["age_days"], bins=bins, labels=labels)
        agg = pend.groupby("bucket", observed=True, as_index=False).agg(orders=("order_id", "count"), net_sales=("net_sales", "sum"))
        fig = px.bar(agg, x="bucket", y="net_sales", text="orders", title="Pending Order Value by Age Bucket")
        fig.update_traces(marker_color=LAV_3, textposition="outside")
        fig.update_layout(xaxis_title="Time Since Order Placed", yaxis_title="Net Sales Tied Up")
        chart(fig, 380)

    section("Investigation Priorities", "🚦", "Evidence-based shortlist; these are areas to investigate, not automatic business decisions.")
    action_counts = actions_f.groupby("action_area", as_index=False).agg(net_sales=("net_sales","sum"), products=("product_id","nunique")).sort_values("net_sales", ascending=False)
    fig = px.bar(action_counts, x="action_area", y="net_sales", text="products", title="Commercial Exposure by Action Area")
    fig.update_traces(marker_color=LAV_1, textposition="outside")
    chart(fig, 390)

    section("Top Items Requiring Attention", "🚨", "Products with the strongest combination of commercial value and identified action area.")
    cols = [c for c in ["product_name","category","supplier_name","net_sales","return_rate","below_reorder_flag","action_area"] if c in actions_f.columns]
    st.dataframe(actions_f.sort_values("net_sales", ascending=False)[cols].head(20), width="stretch", hide_index=True)

st.markdown('<div style="text-align:center;color:#8b7fae;font-size:.68rem;margin-top:2rem;">Supply Chain Intelligence • Analytical database • Streamlit presentation version</div>', unsafe_allow_html=True)
