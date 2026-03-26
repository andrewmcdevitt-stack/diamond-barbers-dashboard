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

# ── Palette — matches reference dark-navy dashboard ────────────────────────────
BG     = "#0F1117"   # page background
CARD   = "#1A1D27"   # card / panel background
BORDER = "#252A3A"   # subtle card border
MUTED  = "#7B7F93"   # secondary / label text
GOLD   = "#FFB800"   # brand accent
BLUE   = "#4F8EF7"   # ≥ 80 % occupancy
ORANGE = "#F97316"   # 65–79 %
RED    = "#EF4444"   # < 65 %
GRID   = "#1E2235"   # chart grid lines

DATA_FILE = Path(__file__).parent.parent / "data" / "performance_summary.json"
LOGO_FILE = Path(__file__).parent / "logo.png"

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── Base ── */
.stApp {{ background-color: {BG} !important; }}
.main .block-container {{
    padding: 1.5rem 2rem 2rem 2rem !important;
    max-width: 1400px !important;
}}
section[data-testid="stSidebar"] {{ display: none !important; }}
#MainMenu, footer {{ visibility: hidden !important; }}
* {{ box-sizing: border-box; }}
body, p, span, div, label {{ color: #FFFFFF; }}

/* ── Typography ── */
h1 {{
    color: {GOLD} !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}}
h2 {{
    color: {MUTED} !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0 0 0.75rem 0 !important;
}}
hr {{
    border: none !important;
    border-top: 1px solid {BORDER} !important;
    margin: 1.25rem 0 !important;
}}

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
}}
.stSelectbox [data-baseweb="select"] * {{ color: #FFFFFF !important; }}
.stSelectbox label {{ color: {MUTED} !important; font-size: 0.72rem !important; }}

/* ── Plotly chart containers → card look ── */
[data-testid="stPlotlyChart"] > div {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
    overflow: hidden;
    padding: 0.75rem !important;
}}
.modebar-container {{ opacity: 0.25; transition: opacity 0.2s; }}
.modebar-container:hover {{ opacity: 1; }}

/* ── Caption ── */
[data-testid="stCaptionContainer"] p {{
    color: {MUTED} !important;
    font-size: 0.78rem !important;
}}

/* ── Logo blend (removes white background) ── */
[data-testid="stImage"] img {{
    mix-blend-mode: screen;
    filter: brightness(1.1) contrast(1.05);
}}

/* ── KPI grid — 3 equal cards ── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
}}

/* ── Stats strip ── */
.stats-row {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 1rem;
}}
.stat-cell {{
    padding: 1rem 1.2rem;
    border-right: 1px solid {BORDER};
    text-align: center;
}}
.stat-cell:last-child {{ border-right: none; }}

/* ── Staff table ── */
.table-wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
.staff-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
}}
.staff-table thead tr {{ border-bottom: 1px solid {BORDER}; }}
.staff-table thead th {{
    color: {MUTED};
    font-size: 0.7rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.65rem 1rem;
    text-align: left;
    white-space: nowrap;
}}
.staff-table thead th.r {{ text-align: right; }}
.staff-table tbody tr {{ border-bottom: 1px solid {BORDER}; transition: background 0.1s; }}
.staff-table tbody tr:last-child {{ border-bottom: none; }}
.staff-table tbody tr:hover {{ background: rgba(255,255,255,0.025); }}
.staff-table tbody td {{
    padding: 0.8rem 1rem;
    color: #FFFFFF;
    white-space: nowrap;
    font-size: 0.875rem;
}}
.staff-table tbody td.r {{
    text-align: right;
    font-variant-numeric: tabular-nums;
}}
.rank-pill {{
    display: inline-block;
    background: rgba(255,255,255,0.07);
    border-radius: 6px;
    padding: 0.18rem 0.55rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: {MUTED};
    min-width: 2.4rem;
    text-align: center;
}}

/* ── Section card header helper ── */
.section-hd {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.9rem;
}}
.section-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: #FFFFFF;
}}
.section-sub {{
    font-size: 0.75rem;
    color: {MUTED};
}}

/* ── Responsive: tablet ── */
@media (max-width: 900px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr) !important; }}
    .stats-row {{ grid-template-columns: repeat(2, 1fr) !important; }}
    .stat-cell:nth-child(2n)   {{ border-right: none !important; }}
    .stat-cell:nth-child(n+3)  {{ border-top: 1px solid {BORDER} !important; }}
    .stat-cell:last-child      {{ grid-column: span 2 !important; border-right: none !important; }}
    .main .block-container     {{ padding: 1rem !important; }}
    [data-testid="column"]     {{ min-width: 100% !important; flex: 0 0 100% !important; }}
}}

/* ── Responsive: mobile ── */
@media (max-width: 600px) {{
    .kpi-grid  {{ grid-template-columns: 1fr !important; }}
    .stats-row {{ grid-template-columns: 1fr 1fr !important; }}
}}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    records = data if isinstance(data, list) else [data]
    return [r for r in records if "sales_summary" in r]


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

def occ_color(val):
    try:
        v = float(val)
        if v >= 80: return BLUE
        if v >= 65: return ORANGE
        return RED
    except:
        return MUTED

def occ_badge(val):
    try:
        v = float(val)
        col = occ_color(v)
        bg  = col.replace("#", "")
        r = int(bg[0:2], 16); g = int(bg[2:4], 16); b = int(bg[4:6], 16)
        return (
            f"<span style='background:rgba({r},{g},{b},0.15);color:{col};"
            f"border-radius:6px;padding:0.18rem 0.6rem;font-size:0.75rem;"
            f"font-weight:600;white-space:nowrap;'>{v:.1f}%</span>"
        )
    except:
        return "—"

def kpi_card(label, value, color="#FFFFFF", sub_label=None, sub_value=None):
    sub = ""
    if sub_label and sub_value:
        sub = (
            f"<div style='margin-top:0.9rem;padding-top:0.9rem;"
            f"border-top:1px solid {BORDER};display:flex;"
            f"justify-content:space-between;align-items:center;'>"
            f"<span style='color:{MUTED};font-size:0.72rem;'>{sub_label}</span>"
            f"<span style='color:#FFFFFF;font-size:0.72rem;font-weight:600;'>{sub_value}</span>"
            f"</div>"
        )
    return (
        f"<div style='background:{CARD};border:1px solid {BORDER};"
        f"border-radius:14px;padding:1.5rem;height:100%;'>"
        f"<div style='color:{MUTED};font-size:0.7rem;text-transform:uppercase;"
        f"letter-spacing:0.1em;margin-bottom:0.6rem;'>{label}</div>"
        f"<div style='color:{color};font-size:2.2rem;font-weight:700;"
        f"line-height:1.1;letter-spacing:-0.02em;'>{value}</div>"
        f"{sub}</div>"
    )

def card_wrap(content, extra_style=""):
    return (
        f"<div style='background:{CARD};border:1px solid {BORDER};"
        f"border-radius:14px;padding:1.5rem;{extra_style}'>{content}</div>"
    )

def section_header(title, right_content=""):
    return (
        f"<div class='section-hd'>"
        f"<span class='section-title'>{title}</span>"
        f"<span class='section-sub'>{right_content}</span>"
        f"</div>"
    )


# ── Load data ──────────────────────────────────────────────────────────────────
history = load_data()

if not history:
    st.title("💈 Diamond Barbers")
    st.info("No data yet. The report runs every Monday at 6:00 AM Darwin time.")
    st.stop()

reversed_history = list(reversed(history))

# ── Header row ────────────────────────────────────────────────────────────────
col_logo, col_sel = st.columns([3, 2])

with col_logo:
    if LOGO_FILE.exists():
        st.image(str(LOGO_FILE), width=200)
    else:
        st.title("💈 Diamond Barbers")

with col_sel:
    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    selected_idx = st.selectbox(
        "Select week",
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

period_label = (
    f"{fmt_date(latest.get('period_start','—'))}  →  "
    f"{fmt_date(latest.get('period_end','—'))}"
)

st.caption(f"Week  ·  {period_label}  ·  Fetched {fmt_date(latest.get('report_date','—'))}")

st.divider()

# ── KPI grid (3 cards) ────────────────────────────────────────────────────────
occ_values  = [float(s.get("occupancy_pct", 0) or 0) for s in staff_list if s.get("occupancy_pct")]
overall_occ = sum(occ_values) / len(occ_values) if occ_values else None
top_color   = occ_color(overall_occ) if overall_occ is not None else MUTED
occ_display = pct(overall_occ) if overall_occ is not None else "No data"

st.markdown(
    f"""<div class="kpi-grid">
        {kpi_card("Net Service Sales",  c(sales.get("services")),  GOLD,
                  "Total Sales", c(sales.get("total_sales")))}
        {kpi_card("Net Product Sales",  c(sales.get("products")),  GOLD,
                  "Inc. Tips & Charges", c(sales.get("total_sales_and_other")))}
        {kpi_card("Overall Occupancy",  occ_display, top_color,
                  "Avg across all staff", "")}
    </div>""",
    unsafe_allow_html=True,
)

# ── Occupancy chart ───────────────────────────────────────────────────────────
legend_html = (
    f"<div style='display:flex;gap:1.5rem;'>"
    f"<span style='color:{BLUE};font-size:0.75rem;'>● ≥ 80 %  On Target</span>"
    f"<span style='color:{ORANGE};font-size:0.75rem;'>● 65–79 %  Watch</span>"
    f"<span style='color:{RED};font-size:0.75rem;'>● &lt; 65 %  Below</span>"
    f"</div>"
)
st.markdown(
    card_wrap(section_header("Staff Occupancy", legend_html)),
    unsafe_allow_html=True,
)

if occ_values:
    occ_df = pd.DataFrame(staff_list)
    occ_df["occupancy_pct"] = pd.to_numeric(occ_df["occupancy_pct"], errors="coerce").fillna(0)
    occ_df = (
        occ_df[occ_df["occupancy_pct"] > 0]
        .sort_values("occupancy_pct", ascending=True)
        .reset_index(drop=True)
    )
    total           = len(occ_df)
    occ_df["rank"]  = [total - i for i in range(total)]
    occ_df["label"] = occ_df.apply(lambda r: f"#{int(r['rank'])}  {r['name']}", axis=1)
    bar_colors      = [occ_color(v) for v in occ_df["occupancy_pct"]]

    fig_occ = go.Figure(go.Bar(
        x=occ_df["occupancy_pct"],
        y=occ_df["label"],
        orientation="h",
        marker_color=bar_colors,
        marker_line_width=0,
        text=[f"{v:.1f}%" for v in occ_df["occupancy_pct"]],
        textposition="inside",
        textfont=dict(color="#FFFFFF", size=11),
        cliponaxis=False,
    ))
    fig_occ.add_vline(x=80, line_dash="dot", line_color=BLUE,   line_width=1,
                      annotation_text="80 %", annotation_font_color=BLUE,
                      annotation_font_size=10, annotation_position="top")
    fig_occ.add_vline(x=65, line_dash="dot", line_color=ORANGE, line_width=1,
                      annotation_text="65 %", annotation_font_color=ORANGE,
                      annotation_font_size=10, annotation_position="top")
    fig_occ.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CARD,
        font=dict(color="#FFFFFF"),
        height=max(300, len(occ_df) * 28),
        xaxis=dict(range=[0, 100], showgrid=True, gridcolor=GRID,
                   ticksuffix="%", color=MUTED, zeroline=False),
        yaxis=dict(color="#FFFFFF", tickfont=dict(size=12)),
        margin=dict(l=10, r=20, t=10, b=20),
        bargap=0.18,
    )
    st.plotly_chart(fig_occ, use_container_width=True)
else:
    st.markdown(
        card_wrap(
            f"<div style='text-align:center;color:{MUTED};padding:2rem 0;'>"
            "Occupancy data will appear after the next weekly run.</div>"
        ),
        unsafe_allow_html=True,
    )

st.divider()

# ── Sales Breakdown  +  Appointments & Performance ───────────────────────────
left, right = st.columns(2)

with left:
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
        columns=["Category", "Amount"],
    ).sort_values("Amount")

    st.markdown(
        card_wrap(section_header("Sales Breakdown", c(sales.get("total_sales")) + " total")),
        unsafe_allow_html=True,
    )
    fig_s = go.Figure(go.Bar(
        x=s_df["Amount"], y=s_df["Category"], orientation="h",
        marker_color=GOLD, marker_line_width=0,
        text=[f"${v:,.0f}" for v in s_df["Amount"]],
        textposition="inside", textfont=dict(color="#000000", size=11),
    ))
    fig_s.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=CARD,
        font=dict(color="#FFFFFF"), height=260,
        xaxis=dict(showgrid=True, gridcolor=GRID, color=MUTED, zeroline=False),
        yaxis=dict(color="#FFFFFF"),
        margin=dict(l=10, r=20, t=10, b=20),
        bargap=0.28,
    )
    st.plotly_chart(fig_s, use_container_width=True)

with right:
    def mini_card(label, main, sub=""):
        s = f"<div style='color:{MUTED};font-size:0.72rem;margin-top:0.2rem;'>{sub}</div>" if sub else ""
        return (
            f"<div style='background:rgba(255,255,255,0.04);border-radius:10px;"
            f"padding:0.9rem 1rem;text-align:center;'>"
            f"<div style='color:{MUTED};font-size:0.65rem;text-transform:uppercase;"
            f"letter-spacing:0.1em;margin-bottom:0.3rem;'>{label}</div>"
            f"<div style='color:#FFFFFF;font-size:1.35rem;font-weight:700;'>{main}</div>"
            f"{s}</div>"
        )

    appt_grid = (
        f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;'>"
        f"{mini_card('Total Appts', n(appts.get('total')))}"
        f"{mini_card('Online', n(appts.get('online')), pct(appts.get('pct_online')))}"
        f"{mini_card('Cancelled', n(appts.get('cancelled')), pct(appts.get('pct_cancelled')))}"
        f"{mini_card('No-Shows', n(appts.get('no_shows')), pct(appts.get('pct_no_show')))}"
        f"</div>"
    )
    perf_grid = (
        f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;margin-top:0.6rem;'>"
        f"{mini_card('Services Sold', n(perf.get('services_sold')))}"
        f"{mini_card('Avg Service', c(perf.get('avg_service_value')))}"
        f"{mini_card('Products Sold', n(perf.get('products_sold')))}"
        f"{mini_card('Avg Product', c(perf.get('avg_product_value')))}"
        f"</div>"
    )
    st.markdown(
        card_wrap(
            section_header("Appointments & Performance") +
            appt_grid + perf_grid
        ),
        unsafe_allow_html=True,
    )

st.divider()

# ── Stats strip ───────────────────────────────────────────────────────────────
def stat_cell(label, value):
    return (
        f"<div class='stat-cell'>"
        f"<div style='color:{MUTED};font-size:0.65rem;text-transform:uppercase;"
        f"letter-spacing:0.1em;margin-bottom:0.35rem;'>{label}</div>"
        f"<div style='color:{GOLD};font-size:1.1rem;font-weight:700;'>{value}</div>"
        f"</div>"
    )

st.markdown(
    f"""<div class="stats-row">
        {stat_cell("Total Sales",             c(sales.get("total_sales")))}
        {stat_cell("Inc. Tips &amp; Charges", c(sales.get("total_sales_and_other")))}
        {stat_cell("Appointments",            str(n(appts.get("total"))))}
        {stat_cell("Tips",                    c(sales.get("tips")))}
        {stat_cell("Avg Service Value",       c(perf.get("avg_service_value")))}
    </div>""",
    unsafe_allow_html=True,
)

# ── Staff performance table ───────────────────────────────────────────────────
has_occ = any(s.get("occupancy_pct") for s in staff_list)
occ_th  = '<th class="r">Occupancy</th>' if has_occ else ""

sorted_staff = sorted(
    staff_list,
    key=lambda s: float(s.get("total_sales", 0) or 0),
    reverse=True,
)

rows_html = ""
for i, s in enumerate(sorted_staff, 1):
    occ_td = (
        f"<td class='r'>{occ_badge(s.get('occupancy_pct', 0))}</td>"
        if has_occ else ""
    )
    rows_html += (
        f"<tr>"
        f"<td><span class='rank-pill'>#{i}</span></td>"
        f"<td style='font-weight:500;'>{s.get('name','—')}</td>"
        f"<td class='r' style='color:{GOLD};font-weight:600;'>{c(s.get('total_sales'))}</td>"
        f"<td class='r'>{c(s.get('services'))}</td>"
        f"<td class='r'>{c(s.get('products'))}</td>"
        f"<td class='r'>{c(s.get('tips'))}</td>"
        f"<td class='r'>{n(s.get('total_appts'))}</td>"
        f"<td class='r'>{n(s.get('cancelled_appts'))}</td>"
        f"<td class='r'>{n(s.get('no_show_appts'))}</td>"
        f"<td class='r'>{n(s.get('services_sold'))}</td>"
        f"{occ_td}"
        f"</tr>"
    )

st.markdown(
    f"<div style='background:{CARD};border:1px solid {BORDER};"
    f"border-radius:14px;padding:1.5rem;'>"
    f"{section_header('Staff Performance', period_label)}"
    f"<div class='table-wrap'>"
    f"<table class='staff-table'>"
    f"<thead><tr>"
    f"<th>Rank</th><th>Name</th>"
    f"<th class='r'>Total</th>"
    f"<th class='r'>Services</th>"
    f"<th class='r'>Products</th>"
    f"<th class='r'>Tips</th>"
    f"<th class='r'>Appts</th>"
    f"<th class='r'>Cancel</th>"
    f"<th class='r'>No-Show</th>"
    f"<th class='r'>Svcs Sold</th>"
    f"{occ_th}"
    f"</tr></thead>"
    f"<tbody>{rows_html}</tbody>"
    f"</table></div></div>",
    unsafe_allow_html=True,
)

# ── Weekly trend ──────────────────────────────────────────────────────────────
valid_trend = [r for r in history if "sales_summary" in r]
if len(valid_trend) > 1:
    st.divider()
    trend_data = [{
        "Week": fmt_date(r.get("period_end", r.get("report_date", ""))),
        "Total Sales": float(r.get("sales_summary", {}).get("total_sales", 0) or 0),
    } for r in valid_trend]
    t_df = pd.DataFrame(trend_data).sort_values("Week")

    st.markdown(
        card_wrap(section_header("Weekly Trend — Total Sales")),
        unsafe_allow_html=True,
    )
    fig_t = go.Figure(go.Scatter(
        x=t_df["Week"], y=t_df["Total Sales"],
        mode="lines+markers",
        line=dict(color=GOLD, width=2),
        marker=dict(color=GOLD, size=7),
        fill="tozeroy",
        fillcolor="rgba(255,184,0,0.07)",
    ))
    fig_t.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=CARD,
        font=dict(color="#FFFFFF"), height=180,
        xaxis=dict(showgrid=False, color=MUTED),
        yaxis=dict(showgrid=True, gridcolor=GRID, color=MUTED, tickprefix="$"),
        margin=dict(l=10, r=10, t=10, b=20),
    )
    st.plotly_chart(fig_t, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    f"<div style='text-align:center;color:{BORDER};font-size:0.7rem;"
    "padding:1.5rem 0 0.5rem;'>"
    "Diamond Barbers  ·  Auto-refreshes every 5 min  ·  Updated every Monday 6:00 AM Darwin time"
    "</div>",
    unsafe_allow_html=True,
)
