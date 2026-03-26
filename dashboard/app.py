import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Diamond Barbers",
    page_icon="💈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Neumorphism palette ────────────────────────────────────────────────────────
BG           = "#1E1E1E"   # page + card background — must be identical
SD           = "#0F0F0F"   # shadow dark  (deeper than BG)
SL           = "#2D2D2D"   # shadow light (lighter than BG)
NEU          = f"8px 8px 18px {SD}, -8px -8px 18px {SL}"
NEU_INSET    = f"inset 5px 5px 10px {SD}, inset -5px -5px 10px {SL}"
GOLD         = "#FFB800"
BLUE         = "#3B82F6"
ORANGE       = "#F97316"
RED          = "#EF4444"
GRID         = "#272727"

st.markdown(f"""
<style>
.stApp {{ background-color: {BG} !important; }}
.main .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}
section[data-testid="stSidebar"] {{ display: none; }}
#MainMenu, footer {{ visibility: hidden; }}

body, p, span, div, label {{ color: #FFFFFF !important; }}

h1 {{ color: {GOLD} !important; font-size: 1.8rem !important; font-weight: 700 !important; }}
h2 {{ color: {GOLD} !important; font-size: 0.85rem !important; font-weight: 600 !important;
     text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.5rem !important; }}

/* Subtle gradient divider instead of hard line */
hr {{
  border: none !important;
  height: 1px !important;
  background: linear-gradient(to right, transparent, #333, transparent) !important;
  margin: 1.5rem 0 !important;
}}

/* Selectbox — inset/concave (pressed-in) neumorphism */
.stSelectbox label {{ color: #888 !important; font-size: 0.75rem !important;
                     text-transform: uppercase; letter-spacing: 0.08em; }}
.stSelectbox [data-baseweb="select"] {{
    background: {BG} !important;
    box-shadow: {NEU_INSET} !important;
    border: none !important;
    border-radius: 12px !important;
}}
.stSelectbox [data-baseweb="select"] * {{ color: #FFFFFF !important; }}

/* Metric cards */
[data-testid="stMetric"] {{
    background: {BG} !important;
    box-shadow: {NEU} !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}}
[data-testid="stMetricLabel"] p {{ color: #888 !important; font-size: 0.72rem !important;
                                   text-transform: uppercase; letter-spacing: 0.1em; }}
[data-testid="stMetricValue"] {{ color: #FFFFFF !important; font-size: 1.5rem !important;
                                   font-weight: 700 !important; }}

/* Dataframe */
.stDataFrame {{ border-radius: 16px !important; overflow: hidden;
                box-shadow: {NEU} !important; }}
.stDataFrame thead tr th {{ background-color: #252525 !important; color: {GOLD} !important;
                             border-bottom: 1px solid #2A2A2A !important; }}
.stDataFrame tbody tr:nth-child(even) td {{ background-color: #1a1a1a !important; }}
.stDataFrame tbody tr:nth-child(odd) td  {{ background-color: {BG} !important; }}
.stDataFrame tbody tr td {{ color: #FFFFFF !important; border-color: #252525 !important; }}

/* Logo — screen blend removes white background on dark surface */
[data-testid="stImage"] img {{
    mix-blend-mode: screen;
    filter: brightness(1.1) contrast(1.05);
}}

[data-testid="stCaptionContainer"] p {{ color: #666 !important; }}
</style>
""", unsafe_allow_html=True)

DATA_FILE = Path(__file__).parent.parent / "data" / "performance_summary.json"
LOGO_FILE  = Path(__file__).parent / "logo.png"


# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    records = data if isinstance(data, list) else [data]
    return [r for r in records if "sales_summary" in r]


def card(label, value, color=GOLD, size="normal"):
    fs = "2.6rem" if size == "large" else "1.6rem"
    return f"""
    <div style="background:{BG};border-radius:16px;
                box-shadow:{NEU};padding:1.4rem;
                text-align:center;height:100%;">
        <div style="color:#888;font-size:0.68rem;text-transform:uppercase;
                    letter-spacing:0.12em;margin-bottom:0.7rem;">{label}</div>
        <div style="color:{color};font-size:{fs};font-weight:700;line-height:1.1;">{value}</div>
    </div>"""


def occ_color_for(val):
    if val is None: return "#555"
    if val >= 80:   return BLUE
    if val >= 65:   return ORANGE
    return RED


def c(val):
    try:    return f"${float(val):,.0f}"
    except: return "$0"

def pct(val):
    try:    return f"{float(val):.1f}%"
    except: return "—"

def n(val):
    try:    return int(val)
    except: return 0

def fmt_date(d):
    try:
        from datetime import datetime
        dt = datetime.strptime(d, "%Y-%m-%d")
        return f"{dt.day} {dt.strftime('%B')} {dt.year}"
    except:
        return d or "—"


# ── Load ──────────────────────────────────────────────────────────────────────
history = load_data()

if not history:
    st.title("💈 Diamond Barbers")
    st.info("No data yet. The report runs every Monday at 6:00 AM Darwin time.")
    st.stop()

reversed_history = list(reversed(history))

# ── Header ────────────────────────────────────────────────────────────────────
col_t, col_sel = st.columns([2, 2])
with col_t:
    if LOGO_FILE.exists():
        st.image(str(LOGO_FILE), width=210)
    else:
        st.title("💈 Diamond Barbers")
with col_sel:
    selected_idx = st.selectbox(
        "week",
        options=range(len(reversed_history)),
        format_func=lambda i: (
            f"{fmt_date(reversed_history[i].get('period_start','?'))}  →  "
            f"{fmt_date(reversed_history[i].get('period_end','?'))}"
        ),
        index=0,
        label_visibility="collapsed",
    )

latest     = reversed_history[selected_idx]
sales      = latest.get("sales_summary", {})
appts      = latest.get("appointments", {})
perf       = latest.get("sales_performance", {})
staff_list = latest.get("staff", [])

st.caption(
    f"Week: **{fmt_date(latest.get('period_start','—'))}** to "
    f"**{fmt_date(latest.get('period_end','—'))}**"
    f"  ·  Fetched: {fmt_date(latest.get('report_date','—'))}"
)

st.divider()

# ── Row 1: Three big KPIs ─────────────────────────────────────────────────────
occ_values  = [float(s.get("occupancy_pct", 0) or 0) for s in staff_list if s.get("occupancy_pct")]
overall_occ = sum(occ_values) / len(occ_values) if occ_values else None
occ_display = pct(overall_occ) if overall_occ is not None else "No data yet"

k1, k2, k3 = st.columns(3)
k1.markdown(card("Net Service Sales",  c(sales.get("services")),  GOLD, "large"), unsafe_allow_html=True)
k2.markdown(card("Net Product Sales",  c(sales.get("products")),  GOLD, "large"), unsafe_allow_html=True)
k3.markdown(card("Overall Occupancy",  occ_display, occ_color_for(overall_occ), "large"), unsafe_allow_html=True)

st.divider()

# ── Occupancy Chart ───────────────────────────────────────────────────────────
st.subheader("Staff Occupancy")

if occ_values:
    occ_df = pd.DataFrame(staff_list)
    occ_df["occupancy_pct"] = pd.to_numeric(occ_df["occupancy_pct"], errors="coerce").fillna(0)
    occ_df = occ_df[occ_df["occupancy_pct"] > 0].sort_values("occupancy_pct", ascending=True).reset_index(drop=True)

    total           = len(occ_df)
    occ_df["rank"]  = [total - i for i in range(total)]
    occ_df["label"] = occ_df.apply(lambda r: f"#{int(r['rank'])}  {r['name']}", axis=1)
    bar_colors      = [occ_color_for(v) for v in occ_df["occupancy_pct"]]

    fig_occ = go.Figure(go.Bar(
        x=occ_df["occupancy_pct"], y=occ_df["label"],
        orientation="h", marker_color=bar_colors, marker_line_width=0,
        text=[f"{v:.1f}%" for v in occ_df["occupancy_pct"]],
        textposition="inside", textfont=dict(color="#FFFFFF", size=11),
        cliponaxis=False,
    ))
    fig_occ.add_vline(x=80, line_dash="dot", line_color=BLUE,   line_width=1,
                      annotation_text="80%", annotation_font_color=BLUE,
                      annotation_font_size=10, annotation_position="top")
    fig_occ.add_vline(x=65, line_dash="dot", line_color=ORANGE, line_width=1,
                      annotation_text="65%", annotation_font_color=ORANGE,
                      annotation_font_size=10, annotation_position="top")
    fig_occ.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=BG,
        font=dict(color="#FFFFFF"),
        height=max(300, len(occ_df) * 28),
        xaxis=dict(range=[0, 100], showgrid=True, gridcolor=GRID,
                   ticksuffix="%", color="#888", zeroline=False),
        yaxis=dict(color="#FFFFFF"),
        margin=dict(l=10, r=20, t=30, b=20),
        bargap=0.18,
    )
    st.plotly_chart(fig_occ, use_container_width=True)

    st.markdown(
        f"<div style='display:flex;gap:2rem;margin-top:-0.8rem;'>"
        f"<span style='color:{BLUE};font-size:0.78rem;'>● ≥80% &nbsp;On Target</span>"
        f"<span style='color:{ORANGE};font-size:0.78rem;'>● 65–79% &nbsp;Needs Attention</span>"
        f"<span style='color:{RED};font-size:0.78rem;'>● &lt;65% &nbsp;Below Target</span>"
        f"</div>", unsafe_allow_html=True
    )
else:
    st.markdown(
        f"<div style='background:{BG};border-radius:12px;box-shadow:{NEU};"
        "padding:2rem;text-align:center;color:#555;'>"
        "Occupancy data will appear after the next weekly run</div>",
        unsafe_allow_html=True
    )

st.divider()

# ── Sales Breakdown + Appointments ───────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("Sales Breakdown")
    items = {
        "Services":          float(sales.get("services", 0) or 0),
        "Service Add-ons":   float(sales.get("service_addons", 0) or 0),
        "Products":          float(sales.get("products", 0) or 0),
        "Service Charges":   float(sales.get("service_charges", 0) or 0),
        "Tips":              float(sales.get("tips", 0) or 0),
        "Late Cancel. Fees": float(sales.get("late_cancellation_fees", 0) or 0),
        "No-Show Fees":      float(sales.get("no_show_fees", 0) or 0),
    }
    s_df = pd.DataFrame(
        [(k, v) for k, v in items.items() if v > 0],
        columns=["Category", "Amount"]
    ).sort_values("Amount")

    fig_s = go.Figure(go.Bar(
        x=s_df["Amount"], y=s_df["Category"], orientation="h",
        marker_color=GOLD, marker_line_width=0,
        text=[f"${v:,.0f}" for v in s_df["Amount"]],
        textposition="inside", textfont=dict(color="#000000"),
    ))
    fig_s.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=BG,
        font=dict(color="#FFFFFF"), height=280,
        xaxis=dict(showgrid=True, gridcolor=GRID, color="#888", zeroline=False),
        yaxis=dict(color="#FFFFFF"),
        margin=dict(l=10, r=20, t=10, b=20), bargap=0.3,
    )
    st.plotly_chart(fig_s, use_container_width=True)

with right:
    st.subheader("Appointments")
    a1, a2 = st.columns(2)
    a1.markdown(card("Total", str(n(appts.get("total")))), unsafe_allow_html=True)
    a2.markdown(card("Online",
        f"{n(appts.get('online'))}<br>"
        f"<span style='font-size:0.9rem;color:#888'>{pct(appts.get('pct_online'))}</span>"),
        unsafe_allow_html=True)
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    a3, a4 = st.columns(2)
    a3.markdown(card("Cancelled",
        f"{n(appts.get('cancelled'))}<br>"
        f"<span style='font-size:0.9rem;color:#888'>{pct(appts.get('pct_cancelled'))}</span>"),
        unsafe_allow_html=True)
    a4.markdown(card("No-Shows",
        f"{n(appts.get('no_shows'))}<br>"
        f"<span style='font-size:0.9rem;color:#888'>{pct(appts.get('pct_no_show'))}</span>"),
        unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    st.subheader("Sales Performance")
    p1, p2 = st.columns(2)
    p1.markdown(card("Services Sold", str(n(perf.get("services_sold")))), unsafe_allow_html=True)
    p2.markdown(card("Avg Service",   c(perf.get("avg_service_value"))),  unsafe_allow_html=True)
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    p3, p4 = st.columns(2)
    p3.markdown(card("Products Sold", str(n(perf.get("products_sold")))), unsafe_allow_html=True)
    p4.markdown(card("Avg Product",   c(perf.get("avg_product_value"))),  unsafe_allow_html=True)

st.divider()

# ── Weekly Summary Strip ──────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;background:{BG};border-radius:16px;
            box-shadow:{NEU};overflow:hidden;margin-bottom:0.5rem;">
    <div style="flex:1;padding:0.9rem 1rem;text-align:center;border-right:1px solid #272727;">
        <div style="color:#888;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem;">Total Sales</div>
        <div style="color:{GOLD};font-size:1.1rem;font-weight:700;">{c(sales.get("total_sales"))}</div>
    </div>
    <div style="flex:1;padding:0.9rem 1rem;text-align:center;border-right:1px solid #272727;">
        <div style="color:#888;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem;">Inc. Tips &amp; Charges</div>
        <div style="color:{GOLD};font-size:1.1rem;font-weight:700;">{c(sales.get("total_sales_and_other"))}</div>
    </div>
    <div style="flex:1;padding:0.9rem 1rem;text-align:center;border-right:1px solid #272727;">
        <div style="color:#888;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem;">Appointments</div>
        <div style="color:{GOLD};font-size:1.1rem;font-weight:700;">{n(appts.get("total"))}</div>
    </div>
    <div style="flex:1;padding:0.9rem 1rem;text-align:center;border-right:1px solid #272727;">
        <div style="color:#888;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem;">Tips</div>
        <div style="color:{GOLD};font-size:1.1rem;font-weight:700;">{c(sales.get("tips"))}</div>
    </div>
    <div style="flex:1;padding:0.9rem 1rem;text-align:center;">
        <div style="color:#888;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem;">Avg Service Value</div>
        <div style="color:{GOLD};font-size:1.1rem;font-weight:700;">{c(perf.get("avg_service_value"))}</div>
    </div>
</div>""", unsafe_allow_html=True)

st.divider()

# ── Staff Table ───────────────────────────────────────────────────────────────
st.subheader("Staff Performance")
if staff_list:
    t_df = pd.DataFrame(staff_list)
    t_df["total_sales"] = pd.to_numeric(t_df["total_sales"], errors="coerce").fillna(0)
    t_df = t_df.sort_values("total_sales", ascending=False).reset_index(drop=True)

    cols = ["name", "total_sales", "services", "products", "tips",
            "total_appts", "cancelled_appts", "no_show_appts", "services_sold"]
    if "occupancy_pct" in t_df.columns:
        cols.append("occupancy_pct")

    t_df = t_df[cols].copy()
    t_df.columns = (["Staff", "Total Sales", "Services", "Products", "Tips",
                      "Appts", "Cancelled", "No-Shows", "Svcs Sold"] +
                     (["Occupancy %"] if "occupancy_pct" in cols else []))

    for col in ["Total Sales", "Services", "Products", "Tips"]:
        t_df[col] = pd.to_numeric(t_df[col], errors="coerce").fillna(0).apply(lambda x: f"${x:,.2f}")
    if "Occupancy %" in t_df.columns:
        t_df["Occupancy %"] = pd.to_numeric(t_df["Occupancy %"], errors="coerce").fillna(0).apply(lambda x: f"{x:.1f}%")

    st.dataframe(t_df, hide_index=True, use_container_width=True)

# ── Weekly Trend ──────────────────────────────────────────────────────────────
valid_trend = [r for r in history if "sales_summary" in r]
if len(valid_trend) > 1:
    st.divider()
    st.subheader("Weekly Trend — Total Sales")
    trend_data = [{
        "Week": fmt_date(r.get("period_end", r.get("report_date", ""))),
        "Total Sales": float(r.get("sales_summary", {}).get("total_sales", 0) or 0),
    } for r in valid_trend]
    t_df2 = pd.DataFrame(trend_data).sort_values("Week")

    fig_t = go.Figure(go.Scatter(
        x=t_df2["Week"], y=t_df2["Total Sales"],
        mode="lines+markers",
        line=dict(color=GOLD, width=2),
        marker=dict(color=GOLD, size=7),
        fill="tozeroy", fillcolor="rgba(255,184,0,0.07)",
    ))
    fig_t.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=BG,
        font=dict(color="#FFFFFF"), height=180,
        xaxis=dict(showgrid=False, color="#888"),
        yaxis=dict(showgrid=True, gridcolor=GRID, color="#888", tickprefix="$"),
        margin=dict(l=10, r=10, t=10, b=20),
    )
    st.plotly_chart(fig_t, use_container_width=True)

st.markdown(
    f"<div style='text-align:center;color:#333;font-size:0.7rem;padding:1.5rem 0 0.5rem;'>"
    "Diamond Barbers · Auto-refreshes every 5 minutes · Updated every Monday 6:00 AM Darwin time"
    "</div>", unsafe_allow_html=True
)
