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

# ── Exact palette from reference image ────────────────────────────────────────
BG     = "#0D0F14"
CARD   = "#141720"
CARD2  = "#0F1218"
BORDER = "#1E2235"
MUTED  = "#7B8091"
GOLD   = "#FFB800"
BLUE   = "#4F8EF7"
ORANGE = "#F97316"
RED    = "#EF4444"
GRID   = "#1A1E2E"

DATA_FILE = Path(__file__).parent.parent / "data" / "performance_summary.json"
LOGO_FILE = Path(__file__).parent / "logo.png"

# ── SVG icons ─────────────────────────────────────────────────────────────────
ICON_HOME = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
ICON_CHART= '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
ICON_USERS= '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
ICON_STAR = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'
ICON_GRID = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'
ICON_COG  = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
ICON_BELL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>'
ICON_CHEV= '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>'
ICON_ARR = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>'
ICON_ARR2= '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>'
ICON_SCH = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── Reset ── */
.stApp {{ background-color: {BG} !important; }}
section[data-testid="stSidebar"] {{ display: none !important; }}
#MainMenu, footer, header {{ visibility: hidden !important; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body, p, span, div, label, td, th {{ color: #FFFFFF; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}

/* ── Push main content to make room for fixed sidebar + topbar ── */
.main .block-container {{
    margin-left: 64px !important;
    padding-top: 68px !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 100% !important;
}}

/* ── Fixed left sidebar ── */
.db-sidebar {{
    position: fixed;
    left: 0; top: 0;
    width: 64px;
    height: 100vh;
    background: {BG};
    border-right: 1px solid {BORDER};
    z-index: 1000;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem 0 1.2rem;
    gap: 0;
}}
.db-sidebar-logo {{
    width: 36px; height: 36px;
    background: {GOLD};
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; font-weight: 700; color: #000;
    margin-bottom: 1.8rem;
    flex-shrink: 0;
}}
.db-sidebar-nav {{
    display: flex; flex-direction: column;
    align-items: center; gap: 0.25rem;
    flex: 1;
}}
.db-nav-icon {{
    width: 40px; height: 40px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    color: {MUTED};
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
}}
.db-nav-icon:hover {{ background: {BORDER}; color: #FFFFFF; }}
.db-nav-icon.active {{ background: {BORDER}; color: #FFFFFF; }}
.db-sidebar-bottom {{
    display: flex; flex-direction: column;
    align-items: center; gap: 0.25rem;
}}

/* ── Fixed top bar ── */
.db-topbar {{
    position: fixed;
    top: 0; left: 64px; right: 0;
    height: 56px;
    background: {BG};
    border-bottom: 1px solid {BORDER};
    z-index: 999;
    display: flex;
    align-items: center;
    padding: 0 1.5rem;
    gap: 1rem;
}}
.db-topbar-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: #FFFFFF;
    display: flex; align-items: center; gap: 0.35rem;
    white-space: nowrap;
}}
.db-topbar-title svg {{ color: {MUTED}; }}
.db-topbar-center {{
    flex: 1;
    display: flex;
    justify-content: center;
}}
.db-search {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 0.35rem 0.9rem;
    color: {MUTED};
    font-size: 0.8rem;
    width: 240px;
    display: flex; align-items: center; gap: 0.5rem;
}}
.db-topbar-right {{
    display: flex; align-items: center; gap: 0.6rem;
}}
.db-topbar-btn {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 0.3rem 0.7rem;
    font-size: 0.78rem;
    color: #FFFFFF;
    display: flex; align-items: center; gap: 0.35rem;
    white-space: nowrap;
}}
.db-notif-dot {{
    width: 7px; height: 7px;
    background: {BLUE};
    border-radius: 50%;
    display: inline-block;
}}
.db-icon-btn {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    color: {MUTED};
    cursor: pointer;
}}

/* ── Card base ── */
.db-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 1.3rem 1.4rem;
    height: 100%;
}}
.db-card-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: #FFFFFF;
    margin-bottom: 0.2rem;
}}
.db-card-sub {{
    font-size: 0.78rem;
    color: {MUTED};
    margin-bottom: 1rem;
}}
.db-card-header {{
    display: flex; justify-content: space-between; align-items: flex-start;
    margin-bottom: 0.9rem;
}}
.db-badge {{
    background: {CARD2};
    border: 1px solid {BORDER};
    border-radius: 7px;
    padding: 0.22rem 0.6rem;
    font-size: 0.72rem;
    color: #FFFFFF;
    display: flex; align-items: center; gap: 0.3rem;
    white-space: nowrap;
}}

/* ── Stat rows inside card ── */
.db-stat-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid {BORDER};
    font-size: 0.82rem;
}}
.db-stat-row:last-child {{ border-bottom: none; }}
.db-stat-label {{ color: {MUTED}; font-size: 0.78rem; }}
.db-stat-value {{ color: #FFFFFF; font-weight: 500; font-size: 0.82rem; }}
.db-stat-value.pos {{ color: #22C55E; }}
.db-stat-value.neg {{ color: {RED}; }}

/* ── Tab toggle (decorative) ── */
.db-tabs {{
    display: flex;
    background: {CARD2};
    border-radius: 8px;
    padding: 3px;
    gap: 2px;
    margin-bottom: 0.75rem;
    width: fit-content;
}}
.db-tab {{
    padding: 0.3rem 0.7rem;
    border-radius: 6px;
    font-size: 0.75rem;
    color: {MUTED};
    cursor: pointer;
}}
.db-tab.active {{
    background: {BORDER};
    color: #FFFFFF;
    font-weight: 500;
}}

/* ── Big number (Total Balance style) ── */
.db-big-num {{
    font-size: 2.6rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 0.5rem;
}}
.db-big-num span {{ color: {MUTED}; font-size: 2rem; }}

/* ── Compare pill ── */
.db-compare {{
    display: flex; flex-direction: column; align-items: flex-end;
    font-size: 0.75rem;
}}
.db-compare-label {{ color: {MUTED}; margin-bottom: 0.15rem; }}
.db-compare-val {{ font-weight: 600; }}
.db-compare-val.pos {{ color: #22C55E; }}
.db-compare-val.neg {{ color: {RED}; }}

/* ── Inner card (dark nested card like reference) ── */
.db-inner-card {{
    background: {CARD2};
    border-radius: 12px;
    padding: 1.2rem;
    margin-top: 0.75rem;
    border: 1px solid {BORDER};
}}

/* ── Staff table ── */
.table-wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 0.75rem; }}
.staff-table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; }}
.staff-table thead tr {{ border-bottom: 1px solid {BORDER}; }}
.staff-table thead th {{
    color: {MUTED}; font-size: 0.68rem; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.07em;
    padding: 0.55rem 0.8rem; text-align: left; white-space: nowrap;
}}
.staff-table thead th.r {{ text-align: right; }}
.staff-table tbody tr {{ border-bottom: 1px solid {BORDER}; transition: background 0.1s; }}
.staff-table tbody tr:last-child {{ border-bottom: none; }}
.staff-table tbody tr:hover {{ background: rgba(255,255,255,0.02); }}
.staff-table tbody td {{ padding: 0.7rem 0.8rem; color: #FFFFFF; white-space: nowrap; }}
.staff-table tbody td.r {{ text-align: right; font-variant-numeric: tabular-nums; }}
.rank-pill {{
    display: inline-flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.07); border-radius: 6px;
    padding: 0.15rem 0.5rem; font-size: 0.72rem; font-weight: 600;
    color: {MUTED}; min-width: 2.2rem;
}}
.join-btn {{
    background: transparent; border: 1px solid {BORDER};
    border-radius: 7px; padding: 0.22rem 0.75rem;
    font-size: 0.75rem; color: #FFFFFF; cursor: pointer;
    white-space: nowrap;
}}

/* ── Mini top-staff cards ── */
.mini-staff-grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem;
    margin-top: 0.75rem;
}}
.mini-staff-card {{
    background: {CARD2};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 0.9rem 1rem;
}}
.mini-staff-name {{ font-size: 0.82rem; font-weight: 600; color: #FFFFFF; margin-bottom: 0.15rem; }}
.mini-staff-sales {{ font-size: 0.72rem; color: {MUTED}; margin-bottom: 0.5rem; }}
.mini-staff-bottom {{ display: flex; align-items: center; justify-content: space-between; }}

/* ── Occupancy badge ── */
.occ-pill {{
    display: inline-block; border-radius: 6px;
    padding: 0.18rem 0.6rem; font-size: 0.72rem; font-weight: 600;
    white-space: nowrap;
}}

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] {{
    background: {CARD} !important; border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
}}
.stSelectbox [data-baseweb="select"] * {{ color: #FFFFFF !important; }}
.stSelectbox label {{ color: {MUTED} !important; font-size: 0.72rem !important; }}

/* ── Chart containers — no extra card chrome since they go inside db-card ── */
[data-testid="stPlotlyChart"] > div {{
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
}}
[data-testid="stCaptionContainer"] p {{ color: {MUTED} !important; font-size: 0.75rem !important; }}

/* ── Column spacing ── */
[data-testid="column"] {{ padding: 0 0.4rem !important; }}
[data-testid="column"]:first-child {{ padding-left: 0 !important; }}
[data-testid="column"]:last-child {{ padding-right: 0 !important; }}

/* ── Logo image ── */
[data-testid="stImage"] img {{ mix-blend-mode: screen; filter: brightness(1.1); }}

/* ── Streamlit removes top padding on image ── */
[data-testid="stImage"] {{ margin: 0 !important; padding: 0 !important; }}

/* ── Divider ── */
hr {{ border: none !important; border-top: 1px solid {BORDER} !important; margin: 0.75rem 0 !important; }}

/* ── Responsive ── */
@media (max-width: 900px) {{
    .db-sidebar {{ display: none; }}
    .main .block-container {{ margin-left: 0 !important; padding-top: 68px !important; }}
    .db-topbar {{ left: 0; }}
    .mini-staff-grid {{ grid-template-columns: 1fr; }}
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

def c2(val):
    """With cents."""
    try:    return f"${float(val):,.2f}"
    except: return "$0.00"

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
        return f"{dt.day} {dt.strftime('%b')} {dt.year}"
    except:
        return d or "—"

def fmt_date_long(d):
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

def occ_badge_html(val):
    try:
        v   = float(val)
        col = occ_color(v)
        bg  = col.replace("#","")
        r,g,b = int(bg[0:2],16), int(bg[2:4],16), int(bg[4:6],16)
        return (f"<span class='occ-pill' style='background:rgba({r},{g},{b},0.15);"
                f"color:{col};'>{v:.1f}%</span>")
    except:
        return "—"


# ── Load ──────────────────────────────────────────────────────────────────────
history = load_data()

if not history:
    st.markdown(
        f"<div class='db-sidebar'>"
        f"<div class='db-sidebar-logo'>💎</div></div>",
        unsafe_allow_html=True,
    )
    st.title("💈 Diamond Barbers")
    st.info("No data yet. The report runs every Monday at 6:00 AM Darwin time.")
    st.stop()

reversed_history = list(reversed(history))

# ── Fixed sidebar ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="db-sidebar">
    <div class="db-sidebar-logo">💎</div>
    <nav class="db-sidebar-nav">
        <div class="db-nav-icon active" title="Dashboard">{ICON_HOME}</div>
        <div class="db-nav-icon" title="Analytics">{ICON_CHART}</div>
        <div class="db-nav-icon" title="Staff">{ICON_USERS}</div>
        <div class="db-nav-icon" title="Performance">{ICON_STAR}</div>
        <div class="db-nav-icon" title="Reports">{ICON_GRID}</div>
    </nav>
    <div class="db-sidebar-bottom">
        <div class="db-nav-icon" title="Settings">{ICON_COG}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Fixed top bar ─────────────────────────────────────────────────────────────
period_start = fmt_date(reversed_history[0].get('period_start',''))
period_end   = fmt_date(reversed_history[0].get('period_end',''))

st.markdown(f"""
<div class="db-topbar">
    <div class="db-topbar-title">
        Diamond Barbers &nbsp;{ICON_CHEV}
    </div>
    <div class="db-topbar-center">
        <div class="db-search">
            {ICON_SCH} &nbsp; {period_start} → {period_end}
        </div>
    </div>
    <div class="db-topbar-right">
        <div class="db-topbar-btn">
            <span class="db-notif-dot"></span> Weekly Report
        </div>
        <div class="db-icon-btn">{ICON_ARR}</div>
        <div class="db-icon-btn">{ICON_ARR2}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Week selector ─────────────────────────────────────────────────────────────
sel_col, _ = st.columns([2, 5])
with sel_col:
    selected_idx = st.selectbox(
        "Select week",
        options=range(len(reversed_history)),
        format_func=lambda i: (
            f"{fmt_date_long(reversed_history[i].get('period_start','?'))}  →  "
            f"{fmt_date_long(reversed_history[i].get('period_end','?'))}"
        ),
        index=0,
        label_visibility="collapsed",
    )

latest     = reversed_history[selected_idx]
sales      = latest.get("sales_summary", {})
appts      = latest.get("appointments", {})
perf       = latest.get("sales_performance", {})
staff_list = latest.get("staff", [])

ps = fmt_date_long(latest.get('period_start','—'))
pe = fmt_date_long(latest.get('period_end','—'))
period_label = f"{ps}  →  {pe}"

# ── Computed values ───────────────────────────────────────────────────────────
occ_vals    = [float(s.get("occupancy_pct",0) or 0) for s in staff_list if s.get("occupancy_pct")]
overall_occ = sum(occ_vals)/len(occ_vals) if occ_vals else None
top_staff   = sorted(staff_list, key=lambda s: float(s.get("total_sales",0) or 0), reverse=True)
valid_trend = [r for r in history if "sales_summary" in r]

# ── 3-column layout (matching reference proportions) ─────────────────────────
col_left, col_center, col_right = st.columns([3, 4, 3])

# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN — Overview card + Top Staff card
# ══════════════════════════════════════════════════════════════════════════════
with col_left:

    # ── Overview card ─────────────────────────────────────────────────────────
    total_s  = float(sales.get("total_sales", 0) or 0)
    net_svc  = float(sales.get("services", 0) or 0)
    net_prod = float(sales.get("products", 0) or 0)
    tips_val = float(sales.get("tips", 0) or 0)

    st.markdown(f"""
    <div class="db-card">
        <div class="db-card-header">
            <div>
                <div class="db-card-title">Weekly Overview</div>
                <div class="db-card-sub">{period_label}</div>
            </div>
            <div class="db-badge">Last Week &nbsp;{ICON_CHEV}</div>
        </div>
        <div class="db-stat-row">
            <span class="db-stat-label">Net Service Sales</span>
            <span class="db-stat-value">{c(net_svc)}</span>
        </div>
        <div class="db-stat-row">
            <span class="db-stat-label">Net Product Sales</span>
            <span class="db-stat-value">{c(net_prod)}</span>
        </div>
        <div class="db-stat-row">
            <span class="db-stat-label">Tips</span>
            <span class="db-stat-value">{c(tips_val)}</span>
        </div>
        <div class="db-stat-row">
            <span class="db-stat-label">Appointments</span>
            <span class="db-stat-value">{n(appts.get("total"))}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Trend line chart (inside its own card below the stats)
    if len(valid_trend) > 1:
        trend_df = pd.DataFrame([{
            "Week": r.get("period_end",""),
            "Sales": float(r.get("sales_summary",{}).get("total_sales",0) or 0),
        } for r in valid_trend]).sort_values("Week")

        fig_trend = go.Figure(go.Scatter(
            x=trend_df["Week"],
            y=trend_df["Sales"],
            mode="lines",
            line=dict(color=BLUE, width=2.5),
            fill="tozeroy",
            fillcolor=f"rgba(79,142,247,0.12)",
        ))
        fig_trend.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=CARD,
            font=dict(color="#FFFFFF", size=10),
            height=130,
            margin=dict(l=0, r=0, t=4, b=0),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            showlegend=False,
        )
        st.markdown(
            f"<div style='background:{CARD};border:1px solid {BORDER};"
            f"border-radius:0 0 14px 14px;margin-top:-2px;padding:0.5rem 0.5rem 0.7rem;'>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
        inc_tips = float(sales.get("total_sales_and_other", 0) or 0)
        st.markdown(
            f"<div style='padding:0 0.4rem 0.2rem;display:flex;justify-content:space-between;align-items:center;'>"
            f"<span style='color:{GOLD};font-size:1.5rem;font-weight:700;'>+ {c(total_s)}</span>"
            f"<span style='font-size:0.72rem;color:{MUTED};text-align:right;'>Inc. tips &amp; charges<br>"
            f"<span style='color:#FFFFFF;font-weight:600;'>{c(inc_tips)}</span></span>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background:{CARD};border:1px solid {BORDER};"
            f"border-radius:0 0 14px 14px;margin-top:-2px;padding:1rem 1rem;'>"
            f"<span style='color:{GOLD};font-size:1.5rem;font-weight:700;'>+ {c(total_s)}</span>"
            f"<span style='color:{MUTED};font-size:0.75rem;margin-left:0.75rem;'>Total Sales</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── Top Staff card ─────────────────────────────────────────────────────────
    top2 = top_staff[:4]
    mini_cards = ""
    for s in top2:
        occ_val = s.get("occupancy_pct", 0) or 0
        mini_cards += f"""
        <div class="mini-staff-card">
            <div class="mini-staff-name">{s.get('name','—').split()[0]}</div>
            <div class="mini-staff-sales">{c(s.get('total_sales'))} sales</div>
            <div class="mini-staff-bottom">
                <span style="color:{MUTED};font-size:0.7rem;">{n(s.get('total_appts'))} appts</span>
                {occ_badge_html(occ_val) if occ_val else ""}
            </div>
        </div>"""

    total_staff = len(top_staff)
    st.markdown(f"""
    <div class="db-card">
        <div class="db-card-header">
            <div>
                <div class="db-card-title">Top Performers</div>
                <div class="db-card-sub">Ranked by total sales</div>
            </div>
            <div class="db-badge">1 of {(total_staff+3)//4} pages</div>
        </div>
        <div class="mini-staff-grid">{mini_cards}</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CENTRE COLUMN — Total Sales card + Staff table
# ══════════════════════════════════════════════════════════════════════════════
with col_center:

    # ── Total Sales (big balance card) ────────────────────────────────────────
    inc_tips_big = float(sales.get("total_sales_and_other", 0) or 0)
    avg_svc      = float(perf.get("avg_service_value", 0) or 0)

    st.markdown(f"""
    <div class="db-card">
        <div class="db-card-header">
            <div>
                <div class="db-card-title">Total Sales</div>
                <div class="db-card-sub">The sum of all sales for this week</div>
            </div>
            <div class="db-badge">AUD {ICON_CHEV}</div>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div class="db-big-num"><span>$</span> {f"{float(sales.get('total_sales',0) or 0):,.2f}"}</div>
            <div class="db-compare">
                <div class="db-compare-label">Inc. tips &amp; charges</div>
                <div class="db-compare-val pos">+ {c(inc_tips_big)}</div>
            </div>
        </div>
        <div style="display:flex;gap:0.4rem;align-items:center;margin-top:0.5rem;margin-bottom:0.75rem;">
            <span style="color:{MUTED};font-size:0.8rem;">Avg service value</span>
            <span style="color:{GOLD};font-size:0.8rem;font-weight:600;">{c(avg_svc)} ↗</span>
        </div>
        <div class="db-inner-card" style="display:flex;align-items:center;justify-content:center;gap:1rem;padding:1rem;">
            <div style="text-align:center;">
                <div style="color:{MUTED};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">Services Sold</div>
                <div style="color:#FFFFFF;font-size:1.1rem;font-weight:700;">{n(perf.get("services_sold"))}</div>
            </div>
            <div style="width:1px;height:32px;background:{BORDER};"></div>
            <div style="text-align:center;">
                <div style="color:{MUTED};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">Products Sold</div>
                <div style="color:#FFFFFF;font-size:1.1rem;font-weight:700;">{n(perf.get("products_sold"))}</div>
            </div>
            <div style="width:1px;height:32px;background:{BORDER};"></div>
            <div style="text-align:center;">
                <div style="color:{MUTED};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">Appointments</div>
                <div style="color:#FFFFFF;font-size:1.1rem;font-weight:700;">{n(appts.get("total"))}</div>
            </div>
            <div style="width:1px;height:32px;background:{BORDER};"></div>
            <div style="text-align:center;">
                <div style="color:{MUTED};font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">Tips</div>
                <div style="color:{GOLD};font-size:1.1rem;font-weight:700;">{c(sales.get("tips"))}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── Staff performance table (Popular Campaigns style) ─────────────────────
    has_occ     = any(s.get("occupancy_pct") for s in staff_list)
    occ_th      = '<th class="r">Occupancy</th>' if has_occ else ""
    sorted_staff = sorted(staff_list, key=lambda s: float(s.get("total_sales",0) or 0), reverse=True)

    rows = ""
    for i, s in enumerate(sorted_staff, 1):
        occ_td = f"<td class='r'>{occ_badge_html(s.get('occupancy_pct',0))}</td>" if has_occ else ""
        rows += (
            f"<tr>"
            f"<td><span class='rank-pill'>#{i}</span></td>"
            f"<td style='font-weight:500;'>{s.get('name','—')}</td>"
            f"<td class='r' style='color:{GOLD};font-weight:600;'>{c(s.get('total_sales'))}</td>"
            f"<td class='r'>{c(s.get('services'))}</td>"
            f"<td class='r'>{c(s.get('products'))}</td>"
            f"<td class='r'>{n(s.get('total_appts'))}</td>"
            f"<td class='r'>{n(s.get('cancelled_appts'))}</td>"
            f"{occ_td}"
            f"<td><span class='join-btn'>View</span></td>"
            f"</tr>"
        )

    st.markdown(f"""
    <div class="db-card">
        <div class="db-card-header">
            <div>
                <div class="db-card-title">Staff Performance</div>
                <div class="db-card-sub">{period_label}</div>
            </div>
            <div style="display:flex;gap:0.5rem;align-items:center;">
                <div class="db-badge">{ICON_GRID} &nbsp;as List</div>
            </div>
        </div>
        <div class="table-wrap">
        <table class="staff-table">
            <thead><tr>
                <th>Rank</th><th>Name</th>
                <th class="r">Total</th>
                <th class="r">Services</th>
                <th class="r">Products</th>
                <th class="r">Appts</th>
                <th class="r">Cancel</th>
                {occ_th}
                <th></th>
            </tr></thead>
            <tbody>{rows}</tbody>
        </table>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN — Occupancy card (tall, like "Ads" panel in reference)
# ══════════════════════════════════════════════════════════════════════════════
with col_right:

    occ_display  = pct(overall_occ) if overall_occ is not None else "No data"
    top_occ_col  = occ_color(overall_occ) if overall_occ is not None else MUTED
    bg_hex       = top_occ_col.replace("#","")
    r0,g0,b0     = int(bg_hex[0:2],16), int(bg_hex[2:4],16), int(bg_hex[4:6],16)

    st.markdown(f"""
    <div class="db-card">
        <div class="db-card-header">
            <div>
                <div class="db-card-title">Occupancy</div>
                <div class="db-card-sub">Staff booked hours vs available</div>
            </div>
        </div>
        <div style="text-align:center;padding:0.5rem 0 1rem;">
            <div style="color:{top_occ_col};font-size:3rem;font-weight:700;
                        line-height:1;letter-spacing:-0.03em;">{occ_display}</div>
            <div style="color:{MUTED};font-size:0.78rem;margin-top:0.35rem;">Overall average</div>
        </div>
        <div style="display:flex;flex-direction:column;gap:0.4rem;margin-bottom:0.9rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;
                        background:{CARD2};border-radius:8px;padding:0.5rem 0.75rem;
                        border:1px solid {BORDER};">
                <div style="display:flex;align-items:center;gap:0.5rem;">
                    <span style="width:8px;height:8px;border-radius:50%;
                                 background:{BLUE};display:inline-block;"></span>
                    <span style="color:{MUTED};font-size:0.75rem;">On Target</span>
                </div>
                <span style="color:{BLUE};font-size:0.75rem;font-weight:600;">≥ 80%</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                        background:{CARD2};border-radius:8px;padding:0.5rem 0.75rem;
                        border:1px solid {BORDER};">
                <div style="display:flex;align-items:center;gap:0.5rem;">
                    <span style="width:8px;height:8px;border-radius:50%;
                                 background:{ORANGE};display:inline-block;"></span>
                    <span style="color:{MUTED};font-size:0.75rem;">Needs Attention</span>
                </div>
                <span style="color:{ORANGE};font-size:0.75rem;font-weight:600;">65–79%</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;
                        background:{CARD2};border-radius:8px;padding:0.5rem 0.75rem;
                        border:1px solid {BORDER};">
                <div style="display:flex;align-items:center;gap:0.5rem;">
                    <span style="width:8px;height:8px;border-radius:50%;
                                 background:{RED};display:inline-block;"></span>
                    <span style="color:{MUTED};font-size:0.75rem;">Below Target</span>
                </div>
                <span style="color:{RED};font-size:0.75rem;font-weight:600;">&lt; 65%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Occupancy bar chart as its own card below
    if occ_vals:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        occ_df = pd.DataFrame(staff_list)
        occ_df["occupancy_pct"] = pd.to_numeric(occ_df["occupancy_pct"], errors="coerce").fillna(0)
        occ_df = (occ_df[occ_df["occupancy_pct"] > 0]
                  .sort_values("occupancy_pct", ascending=True)
                  .reset_index(drop=True))
        total_o         = len(occ_df)
        occ_df["rank"]  = [total_o - i for i in range(total_o)]
        occ_df["label"] = occ_df.apply(lambda r: f"#{int(r['rank'])} {r['name'].split()[0]}", axis=1)
        bar_colors      = [occ_color(v) for v in occ_df["occupancy_pct"]]

        fig_occ = go.Figure(go.Bar(
            x=occ_df["occupancy_pct"], y=occ_df["label"],
            orientation="h", marker_color=bar_colors, marker_line_width=0,
            text=[f"{v:.0f}%" for v in occ_df["occupancy_pct"]],
            textposition="inside", textfont=dict(color="#FFFFFF", size=9),
            cliponaxis=False,
        ))
        fig_occ.add_vline(x=80, line_dash="dot", line_color=BLUE,   line_width=1)
        fig_occ.add_vline(x=65, line_dash="dot", line_color=ORANGE, line_width=1)
        fig_occ.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=CARD,
            font=dict(color="#FFFFFF", size=10),
            height=max(260, len(occ_df) * 22),
            xaxis=dict(range=[0,100], showgrid=True, gridcolor=GRID,
                       ticksuffix="%", color=MUTED, zeroline=False, tickfont=dict(size=9)),
            yaxis=dict(color="#FFFFFF", tickfont=dict(size=9)),
            margin=dict(l=5, r=10, t=8, b=8),
            bargap=0.2,
        )
        st.markdown(
            f"<div style='background:{CARD};border:1px solid {BORDER};"
            f"border-radius:14px;padding:0.9rem 0.6rem 0.5rem;'>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig_occ, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # Appointments mini stats
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="db-card">
        <div class="db-card-title" style="margin-bottom:0.8rem;">Appointments</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
            <div style="background:{CARD2};border:1px solid {BORDER};border-radius:10px;padding:0.8rem;text-align:center;">
                <div style="color:{MUTED};font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">Total</div>
                <div style="color:#FFFFFF;font-size:1.2rem;font-weight:700;">{n(appts.get("total"))}</div>
            </div>
            <div style="background:{CARD2};border:1px solid {BORDER};border-radius:10px;padding:0.8rem;text-align:center;">
                <div style="color:{MUTED};font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">Online</div>
                <div style="color:#FFFFFF;font-size:1.2rem;font-weight:700;">{n(appts.get("online"))}</div>
                <div style="color:{MUTED};font-size:0.7rem;">{pct(appts.get("pct_online"))}</div>
            </div>
            <div style="background:{CARD2};border:1px solid {BORDER};border-radius:10px;padding:0.8rem;text-align:center;">
                <div style="color:{MUTED};font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">Cancelled</div>
                <div style="color:{RED};font-size:1.2rem;font-weight:700;">{n(appts.get("cancelled"))}</div>
                <div style="color:{MUTED};font-size:0.7rem;">{pct(appts.get("pct_cancelled"))}</div>
            </div>
            <div style="background:{CARD2};border:1px solid {BORDER};border-radius:10px;padding:0.8rem;text-align:center;">
                <div style="color:{MUTED};font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">No-Shows</div>
                <div style="color:{ORANGE};font-size:1.2rem;font-weight:700;">{n(appts.get("no_shows"))}</div>
                <div style="color:{MUTED};font-size:0.7rem;">{pct(appts.get("pct_no_show"))}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    f"<div style='text-align:center;color:{BORDER};font-size:0.68rem;"
    "padding:1.5rem 0 0.5rem;'>"
    "Diamond Barbers  ·  Auto-refreshes every 5 min  ·  Updated every Monday 6:00 AM Darwin time"
    "</div>",
    unsafe_allow_html=True,
)
