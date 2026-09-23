from __future__ import annotations
from pathlib import Path

from datetime import datetime
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from equicafi.models import AnalysisResult, Metric, Observation
from equicafi.services.analysis_service import AnalysisService
from equicafi.services.scenario_service import simulate_return


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="EquiCafi",
    page_icon="dashboard/ei.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #081630;
        --panel: #0D2436;
        --panel-2: #125358;
        --panel-3: #3B8788;
        --line: #294653;
        --line-soft: rgba(59,135,136,.28);
        --gold: #3B8788;
        --gold-soft: #EBEBED;
        --ivory: #EBEBED;
        --muted: #C2C3C5;
        --green: #3B8788;
        --green-soft: rgba(59,135,136,.15);
        --red: #3B8788;
        --red-soft: rgba(59,135,136,.12);
        --blue-soft: rgba(59,135,136,.12);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 82% 4%, rgba(59,135,136,.14), transparent 30%),
            linear-gradient(180deg, #081630 0%, #0B2031 100%);
        color: var(--ivory);
    }

    section[data-testid="stSidebar"] {
        background: #081630;
        border-right: 1px solid var(--line);
    }

    section[data-testid="stSidebar"] * {
        color: var(--ivory);
    }

    .eq-brand {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 44px;
        line-height: .9;
        letter-spacing: .09em;
        color: var(--ivory);
    }

    .eq-subbrand {
        margin-top: 9px;
        color: var(--gold-soft);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .19em;
    }

    .ornament {
        margin: 16px 0 24px;
        color: var(--gold);
        letter-spacing: .45em;
        font-size: 13px;
    }

    .kicker {
        color: var(--gold);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .24em;
    }

    .hero-title {
        margin-top: 8px;
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: clamp(46px, 5.2vw, 76px);
        line-height: .92;
        font-weight: 600;
        color: var(--ivory);
        letter-spacing: -.01em;
    }

    .hero-meta {
        margin-top: 14px;
        color: var(--muted);
        font-size: 12px;
        letter-spacing: .02em;
    }

    .rule {
        margin: 20px 0 26px;
        height: 1px;
        background: linear-gradient(90deg, var(--gold), rgba(59,135,136,.18), transparent);
    }

    .section-title {
        margin-top: 28px;
        color: var(--ivory);
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 36px;
        line-height: 1;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 12px;
        margin-top: 5px;
        margin-bottom: 16px;
    }

    .signal {
        background: linear-gradient(145deg, rgba(255,255,255,.028), rgba(255,255,255,.008));
        border: 1px solid var(--line);
        min-height: 108px;
        padding: 16px 16px 14px;
        border-radius: 3px;
    }

    .signal-label {
        color: var(--muted);
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: .18em;
    }

    .signal-value {
        color: var(--ivory);
        font-size: 26px;
        font-weight: 600;
        margin-top: 8px;
    }

    .signal-note {
        color: var(--muted);
        font-size: 10px;
        line-height: 1.45;
        margin-top: 5px;
    }

    .profile-strip {
        display: grid;
        grid-template-columns: 1.4fr .8fr .8fr .8fr;
        border: 1px solid var(--line);
        margin-top: 18px;
        background: rgba(18,20,15,.72);
    }

    .profile-cell {
        padding: 15px 16px;
        border-right: 1px solid var(--line);
    }

    .profile-cell:last-child { border-right: 0; }

    .profile-label {
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: .15em;
        color: var(--muted);
    }

    .profile-value {
        margin-top: 6px;
        font-size: 13px;
        color: var(--ivory);
    }

    .notice {
        padding: 15px 17px;
        border: 1px solid var(--line-soft);
        border-left: 2px solid var(--gold);
        background: rgba(59,135,136,.045);
        color: #C2C3C5;
        font-size: 12px;
        line-height: 1.65;
        margin: 18px 0;
    }

    .metric-card {
        height: 100%;
        border: 1px solid var(--line);
        background: rgba(18,20,15,.84);
        padding: 17px 17px 16px;
        margin-bottom: 12px;
    }

    .metric-top {
        display: flex;
        justify-content: space-between;
        gap: 14px;
        align-items: start;
    }

    .metric-name {
        color: var(--gold-soft);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .16em;
    }

    .metric-value {
        color: var(--ivory);
        font-size: 27px;
        font-weight: 600;
        margin-top: 7px;
    }

    .metric-status {
        font-size: 9px;
        letter-spacing: .14em;
        text-transform: uppercase;
        color: var(--green);
        border: 1px solid rgba(113,138,115,.28);
        padding: 4px 7px;
        white-space: nowrap;
    }

    .metric-copy {
        margin-top: 12px;
        color: #b7b3a7;
        font-size: 11px;
        line-height: 1.62;
    }

    .metric-copy strong { color: var(--ivory); }

    .metric-observation {
        margin-top: 11px;
        padding-top: 10px;
        border-top: 1px solid rgba(59,135,136,.12);
        color: #C2C3C5;
        font-size: 11px;
        line-height: 1.58;
    }

    .observation-card {
        border: 1px solid var(--line);
        border-left: 2px solid var(--gold);
        padding: 18px 19px;
        margin-bottom: 11px;
        background: linear-gradient(145deg, rgba(255,255,255,.024), rgba(255,255,255,.008));
    }

    .obs-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
    }

    .obs-index {
        color: var(--gold);
        font-size: 9px;
        letter-spacing: .18em;
    }

    .obs-badge {
        padding: 4px 7px;
        border: 1px solid var(--line);
        font-size: 9px;
        letter-spacing: .14em;
    }

    .obs-badge.watch { color: var(--red); border-color: rgba(144,96,90,.35); }
    .obs-badge.risk { color: #3B8788; border-color: rgba(183,124,115,.35); }
    .obs-badge.info { color: var(--gold-soft); }

    .obs-title {
        margin-top: 11px;
        color: var(--ivory);
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 27px;
        line-height: 1.15;
    }

    .obs-body {
        margin-top: 8px;
        color: #C2C3C5;
        font-size: 12px;
        line-height: 1.7;
        max-width: 940px;
    }

    .obs-related {
        margin-top: 11px;
        color: var(--gold);
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: .12em;
    }

    .lab-hero {
        border: 1px solid var(--gold);
        background:
            radial-gradient(circle at 100% 0%, rgba(59,135,136,.12), transparent 38%),
            rgba(18,20,15,.9);
        padding: 25px 26px;
        margin: 14px 0 17px;
    }

    .lab-number {
        margin-top: 4px;
        font-family: 'Cormorant Garamond', Georgia, serif;
        color: var(--ivory);
        font-size: 53px;
        line-height: .98;
    }

    .lab-copy {
        margin-top: 10px;
        color: var(--muted);
        font-size: 12px;
        line-height: 1.6;
        max-width: 800px;
    }

    .scenario-box {
        border: 1px solid var(--line);
        padding: 18px;
        background: rgba(18,20,15,.78);
    }

    .scenario-title {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 25px;
        color: var(--ivory);
        margin-bottom: 8px;
    }

    .scenario-small {
        color: var(--muted);
        font-size: 10px;
        line-height: 1.6;
    }

    .footer {
        border-top: 1px solid var(--line);
        margin-top: 44px;
        padding: 20px 0 34px;
        color: var(--muted);
        font-size: 10px;
        line-height: 1.7;
    }

    @media (max-width: 900px) {
        .profile-strip { grid-template-columns: 1fr 1fr; }
        .profile-cell:nth-child(2) { border-right: 0; }
        .profile-cell:nth-child(-n+2) { border-bottom: 1px solid var(--line); }
    }

    
    /* EQUICAFI FINAL BRAND SYSTEM */

    [data-testid="stHeader"] {
        background: #081630 !important;
    }

    [data-testid="stToolbar"] {
        background: #081630 !important;
    }

    section[data-testid="stSidebar"] {
        background: #081630 !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 82% 4%, rgba(59,135,136,.14), transparent 30%),
            linear-gradient(180deg, #081630 0%, #0B2031 100%) !important;
        color: #EBEBED !important;
    }

    section[data-testid="stSidebar"] * {
        color: #EBEBED !important;
    }

    div.stButton > button[kind="primary"] {
        background: #3B8788 !important;
        border: 1px solid #3B8788 !important;
        color: #EBEBED !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #125358 !important;
        border-color: #3B8788 !important;
    }

    div.stButton > button:not([kind="primary"]) {
        background: #0D2436 !important;
        border: 1px solid #294653 !important;
        color: #EBEBED !important;
    }

    input,
    textarea {
        background: #0D2436 !important;
        color: #EBEBED !important;
        border-color: #294653 !important;
    }

    [data-baseweb="select"] > div {
        background: #0D2436 !important;
        color: #EBEBED !important;
        border-color: #294653 !important;
    }

    .eq-brand {
        color: #EBEBED !important;
    }

    .eq-subbrand {
        color: #3B8788 !important;
    }

    .ornament {
        color: #3B8788 !important;
    }

    .kicker {
        color: #3B8788 !important;
    }

    .rule {
        background: linear-gradient(
            90deg,
            #3B8788,
            rgba(59,135,136,.25),
            transparent
        ) !important;
    }

    .signal,
    .metric-card,
    .scenario-box {
        background: rgba(13,36,54,.82) !important;
        border-color: #294653 !important;
    }

    .profile-strip {
        background: rgba(13,36,54,.78) !important;
    }

    .notice {
        border-left-color: #3B8788 !important;
        background: rgba(59,135,136,.07) !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================


def currency_symbol(currency: str) -> str:
    symbols = {
        "INR": chr(0x20B9),
        "USD": "$",
        "EUR": chr(0x20AC),
        "GBP": chr(0x00A3),
        "JPY": chr(0x00A5),
    }
    return symbols.get(str(currency).upper(), str(currency).upper())



def money(value: float | None, currency: str = "INR") -> str:
    if value is None:
        return "?"

    value = float(value)
    symbol = currency_symbol(currency)

    if str(currency).upper() == "INR":
        negative = value < 0
        value = abs(value)

        # 1 Lakh Crore = ?1,00,000 Crore = ?1,000,000,000,000
        if value >= 1_000_000_000_000:
            result = f"{symbol}{value / 1_000_000_000_000:,.2f} Lakh Cr"
        elif value >= 10_000_000:
            result = f"{symbol}{value / 10_000_000:,.2f} Cr"
        elif value >= 100_000:
            result = f"{symbol}{value / 100_000:,.2f} Lakh"
        else:
            result = f"{symbol}{value:,.2f}"

        return f"-{result}" if negative else result

    # Non-INR fallback
    absolute = abs(value)

    if absolute >= 1_000_000_000_000:
        return f"{symbol}{value / 1_000_000_000_000:,.2f}T"
    if absolute >= 1_000_000_000:
        return f"{symbol}{value / 1_000_000_000:,.2f}B"
    if absolute >= 1_000_000:
        return f"{symbol}{value / 1_000_000:,.2f}M"

    return f"{symbol}{value:,.2f}"


def metric_value_text(metric: Metric, currency: str) -> str:
    if metric.value is None:
        return "?"

    value = float(metric.value)
    unit = str(metric.unit).strip().lower()

    if unit in {"%", "percent", "percentage"}:
        return f"{value:.2f}%"

    if unit in {"x", "times"}:
        return f"{value:.2f}?"

    if unit in {
        "/share",
        "per share",
        "inr/share",
        "usd/share",
        "eur/share",
        "gbp/share",
    }:
        return f"{currency_symbol(currency)}{value:,.2f}/share"

    if unit in {"currency", "inr", "?"} or unit == str(currency).lower():
        return money(value, currency)

    return f"{value:,.2f}{metric.unit}"


def metric_map(result: AnalysisResult) -> dict[str, Metric]:
    return {metric.name: metric for metric in result.all_metrics()}


def show_signal(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="signal">
            <div class="signal-label">{label}</div>
            <div class="signal-value">{value}</div>
            <div class="signal-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, subtitle: str | None = None) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)


def metric_card(metric: Metric, currency: str, expanded: bool = False) -> None:
    value = metric_value_text(metric, currency)
    status = "AVAILABLE" if metric.status == "available" else "UNAVAILABLE"
    status_class = "metric-status" if metric.status == "available" else "metric-status"

    observation = (
        f'<div class="metric-observation"><strong>EQUICAFI observation:</strong> {metric.observation}</div>'
        if metric.observation
        else ""
    )

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-top">
                <div>
                    <div class="metric-name">{metric.name}</div>
                    <div class="metric-value">{value}</div>
                </div>
                <div class="{status_class}">{status}</div>
            </div>
            <div class="metric-copy">
                <strong>Simple:</strong> {metric.simple_meaning}<br><br>
                <strong>Professional:</strong> {metric.professional_definition}<br><br>
                <strong>Formula:</strong> {metric.formula}<br><br>
                <strong>Why it matters:</strong> {metric.why_it_matters}<br><br>
                <strong>Caveat:</strong> {metric.caveat}
            </div>
            {observation}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_observation(obs: Observation, index: int) -> None:
    severity = obs.severity.lower()
    st.markdown(
        f"""
        <div class="observation-card">
            <div class="obs-top">
                <div class="obs-index">OBSERVATION {index:02d}</div>
                <div class="obs-badge {severity}">{severity.upper()}</div>
            </div>
            <div class="obs-title">{obs.title}</div>
            <div class="obs-body">{obs.explanation}</div>
            <div class="obs-related">
                Related metrics · {' · '.join(obs.related_metrics) if obs.related_metrics else '—'}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def series_dataframe(data: dict[str, dict[str, float]]) -> pd.DataFrame:
    if not data:
        return pd.DataFrame()

    frame = pd.DataFrame(data).T
    frame.index = frame.index.astype(str)
    return frame.sort_index()


def plot_history(frame: pd.DataFrame, column: str, title: str, y_prefix: str = "") -> None:
    series = pd.to_numeric(frame[column], errors="coerce").dropna()
    if series.empty:
        st.info("No values are available for this series.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series.values,
            mode="lines+markers",
            line=dict(color="#3B8788", width=2),
            marker=dict(size=6, color="#EBEBED"),
            hovertemplate=f"%{{x}}<br>{y_prefix}%{{y:,.2f}}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        template="plotly_dark",
        height=410,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#EBEBED", family="Inter"),
        margin=dict(l=10, r=10, t=48, b=10),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(59,135,136,.10)", zeroline=False),
        hoverlabel=dict(bgcolor="#125358", font_color="#EBEBED"),
    )
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})


def run_analysis(ticker: str) -> AnalysisResult:
    return AnalysisService().analyze(ticker)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.image("dashboard/ei.png", width=82)
    st.markdown(
        """
        <div class="eq-brand">EQUICAFI</div>
        <div class="eq-subbrand">Equity Intelligence Engine</div>
        <div class="ornament">✦ - ✦ - ✦</div>
        """,
        unsafe_allow_html=True,
    )

    ticker = st.text_input(
        "Ticker",
        value=st.session_state.get("ticker", "DEMO"),
        placeholder="RELIANCE.NS",
    ).strip().upper()

    analyse = st.button("Analyse Equity", type="primary", width="stretch")

    st.markdown("")
    page = st.radio(
        "Research Desk",
        [
            "Overview",
            "Fundamentals",
            "History",
            "Valuation",
            "Technicals & Risk",
            "Reasoning",
            "Capital Lab",
        ],
    )

    st.markdown("---")
    st.caption(
        "Analytical and educational output. Capital Lab uses hypothetical "
        "assumptions and does not determine a personal investment amount."
    )


if "result" not in st.session_state:
    st.session_state.result = None

if "ticker" not in st.session_state:
    st.session_state.ticker = "DEMO"

if analyse:
    if not ticker:
        st.error("Enter a ticker first.")
        st.stop()

    with st.spinner(f"Analysing {ticker}…"):
        try:
            st.session_state.result = run_analysis(ticker)
            st.session_state.ticker = ticker
        except Exception as exc:
            st.error(f"Analysis could not be completed: {exc}")
            st.stop()

result = st.session_state.result


# ============================================================
# LANDING
# ============================================================

if result is None:
    st.markdown('<div class="kicker">Equity research workspace</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title">Study the equity.<br>Understand the story.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-meta">Fundamentals · history · valuation · technicals · risk · reasoning · capital scenarios</div>',
        unsafe_allow_html=True,
    )

    section("Research Workflow", "Seven views built on one structured analysis engine.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        show_signal("01", "Fundamentals", "Business economics and profitability")
    with c2:
        show_signal("02", "Valuation", "Market pricing relationships")
    with c3:
        show_signal("03", "Risk", "Observed market and financial risk")
    with c4:
        show_signal("04", "Capital Lab", "Hypothetical return mathematics")

    st.markdown(
        '<div class="notice"><strong>Start here:</strong> enter a ticker in the research desk and run an analysis. Use <strong>DEMO</strong> to explore the interface with synthetic data.</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# NORMALIZED RESULT
# ============================================================

currency = result.company.currency or "INR"
metrics = metric_map(result)

company = result.company
quality = result.data_quality

st.markdown('<div class="kicker">Equity research dossier</div>', unsafe_allow_html=True)
st.markdown(f'<div class="hero-title">{company.name}</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="hero-meta">{company.ticker} · {company.exchange or "—"} · {company.sector or "Sector unavailable"} · {quality.source}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="profile-strip">
        <div class="profile-cell">
            <div class="profile-label">Data status</div>
            <div class="profile-value">{quality.status}</div>
        </div>
        <div class="profile-cell">
            <div class="profile-label">Data quality</div>
            <div class="profile-value">{quality.quality}</div>
        </div>
        <div class="profile-cell">
            <div class="profile-label">Current price</div>
            <div class="profile-value">{metric_value_text(result.current_price, currency)}</div>
        </div>
        <div class="profile-cell">
            <div class="profile-label">Updated</div>
            <div class="profile-value">{result.generated_at.astimezone().strftime('%d %b %Y · %H:%M')}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if company.ticker.upper() == "DEMO":
    st.markdown(
        '<div class="notice"><strong>DEMO MODE:</strong> Synthetic demonstration data. It is designed to show how EQUICAFI works and does not represent a live company or current market position.</div>',
        unsafe_allow_html=True,
    )

if quality.notes:
    with st.expander("Data notes", expanded=False):
        for note in quality.notes:
            st.write(f"• {note}")


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":
    section("Key Signals", "A compact view before opening the detailed research sections.")

    signal_names = [
        ("Revenue", "Revenue"),
        ("Revenue Growth", "Revenue Growth"),
        ("ROE", "ROE"),
        ("ROCE", "ROCE"),
        ("Free Cash Flow", "Free Cash Flow"),
        ("P/E", "P/E"),
    ]

    cols = st.columns(6)
    for col, (label, name) in zip(cols, signal_names):
        metric = metrics.get(name)
        with col:
            if metric:
                show_signal(label, metric_value_text(metric, currency), "Latest available value")
            else:
                show_signal(label, "—", "Unavailable")

    section("What Stands Out", "These are structured relationships between the metrics, not a single-score verdict.")

    if result.observations:
        for index, obs in enumerate(result.observations[:6], start=1):
            render_observation(obs, index)
    else:
        st.caption("No cross-metric observations are available.")

    section("Company Snapshot")

    left, right = st.columns([1.05, .95])
    with left:
        key_snapshot = [
            ("Operating Margin", "Operating Margin"),
            ("Net Margin", "Net Margin"),
            ("EPS", "EPS"),
            ("Operating Cash Flow", "Operating Cash Flow"),
            ("Debt / Equity", "Debt / Equity"),
            ("Interest Coverage", "Interest Coverage"),
        ]
        for label, name in key_snapshot:
            m = metrics.get(name)
            if m:
                st.markdown(
                    f"**{label}**  \\  {metric_value_text(m, currency)}",
                )

    with right:
        if result.price_history and len(result.price_history.close) >= 2:
            price_df = pd.DataFrame(
                {
                    "Date": [str(d) for d in result.price_history.dates],
                    "Close": result.price_history.close,
                }
            )
            price_df = price_df.tail(252)
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=price_df["Date"],
                    y=price_df["Close"],
                    mode="lines",
                    line=dict(color="#3B8788", width=2),
                    hovertemplate="%{x}<br>INR %{y:,.2f}<extra></extra>",
                )
            )
            fig.update_layout(
                title="Observed price history",
                template="plotly_dark",
                height=290,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#EBEBED", family="Inter"),
                margin=dict(l=5, r=5, t=44, b=5),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="rgba(59,135,136,.10)", zeroline=False),
            )
            st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
        else:
            st.markdown(
                '<div class="notice">No usable price-history series is available for a chart.</div>',
                unsafe_allow_html=True,
            )

    section("Method in One Line")
    st.markdown(
        "**EQUICAFI does not rely on one ratio.** It connects growth, profitability, cash conversion, valuation, leverage, liquidity and observed market behaviour so that the user can see how the pieces fit together."
    )


# ============================================================
# FUNDAMENTALS
# ============================================================

elif page == "Fundamentals":
    section("Fundamental Research", "Every metric uses a simple explanation alongside the professional finance definition.")

    preferred = [
        "Revenue", "Revenue Growth", "Gross Profit", "Gross Margin",
        "Operating Profit", "Operating Margin", "Net Profit", "Net Margin",
        "EPS", "EPS Growth", "ROE", "ROA", "ROCE",
        "Operating Cash Flow", "Capital Expenditure", "Free Cash Flow",
        "FCF / Net Income", "Operating Cash Flow / Net Income",
    ]

    shown = [metrics[name] for name in preferred if name in metrics]

    for start in range(0, len(shown), 2):
        cols = st.columns(2)
        for col, metric in zip(cols, shown[start:start + 2]):
            with col:
                metric_card(metric, currency)

    section("Balance Sheet & Coverage", "Leverage, debt servicing and liquidity provide context for the profitability figures above.")

    balance_names = [
        "Debt / Equity", "Interest Coverage", "Net Debt / Operating Cash Flow",
        "FCF / Debt", "Cash / Debt", "Liquidity Coverage", "Quick Liquidity Coverage",
    ]

    shown = [metrics[name] for name in balance_names if name in metrics]
    for start in range(0, len(shown), 2):
        cols = st.columns(2)
        for col, metric in zip(cols, shown[start:start + 2]):
            with col:
                metric_card(metric, currency)


# ============================================================
# HISTORY
# ============================================================

elif page == "History":
    section("Historical Research", "Use the history view to ask what changed over time, not just what the latest number is.")

    frame = series_dataframe(result.history)
    if frame.empty:
        st.markdown('<div class="notice">No multi-period financial history is available for this analysis.</div>', unsafe_allow_html=True)
    else:
        numeric_columns = [column for column in frame.columns if pd.api.types.is_numeric_dtype(frame[column])]
        if numeric_columns:
            choice = st.selectbox("Financial series", numeric_columns)
            plot_history(frame, choice, f"Historical {choice}")
            st.dataframe(frame[[choice]], width="stretch")

        if result.historical_observations:
            section("Historical Observations")
            for index, obs in enumerate(result.historical_observations, start=1):
                render_observation(obs, index)


# ============================================================
# VALUATION
# ============================================================

elif page == "Valuation":
    section("Valuation Observatory", "Valuation tells us how the market is pricing current fundamentals; it does not work well in isolation.")

    names = [
        "P/E", "P/B", "P/S", "EV/EBITDA", "EV/Sales",
        "Earnings Yield", "FCF Yield", "Dividend Yield",
    ]
    shown = [metrics[name] for name in names if name in metrics]

    for start in range(0, len(shown), 2):
        cols = st.columns(2)
        for col, metric in zip(cols, shown[start:start + 2]):
            with col:
                metric_card(metric, currency)

    valuation_frame = series_dataframe(result.valuation_history)
    if not valuation_frame.empty:
        section("Valuation Through Time")
        numeric_columns = [column for column in valuation_frame.columns if pd.api.types.is_numeric_dtype(valuation_frame[column])]
        if numeric_columns:
            choice = st.selectbox("Valuation series", numeric_columns)
            plot_history(valuation_frame, choice, f"Historical {choice}")
            st.dataframe(valuation_frame[[choice]], width="stretch")

    st.markdown(
        '<div class="notice"><strong>Methodology:</strong> P/E, P/B, P/S and enterprise-value multiples can answer different valuation questions. EQUICAFI therefore pairs them with growth, profitability, cash-flow and balance-sheet context instead of turning one multiple into a standalone conclusion.</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# TECHNICALS & RISK
# ============================================================

elif page == "Technicals & Risk":
    section("Technicals", "These metrics describe observed price behaviour in the selected historical window.")

    technical_names = [
        "52 Week High", "52 Week Low", "Distance from 52 Week High",
        "Distance from 52 Week Low", "SMA 20", "SMA 50", "EMA 20", "RSI 14",
    ]

    shown = [metrics[name] for name in technical_names if name in metrics]
    for start in range(0, len(shown), 2):
        cols = st.columns(2)
        for col, metric in zip(cols, shown[start:start + 2]):
            with col:
                metric_card(metric, currency)

    section("Risk Observatory", "Financial risk and observed market risk belong together when interpreting the overall picture.")

    risk_names = [
        "Maximum Drawdown", "Annualized Volatility", "Downside Volatility",
        "Worst Daily Return", "Positive Session Rate", "Debt / Equity",
        "Interest Coverage", "Net Debt / Operating Cash Flow", "FCF / Debt",
        "Cash / Debt", "Liquidity Coverage", "Quick Liquidity Coverage",
    ]

    shown = [metrics[name] for name in risk_names if name in metrics]
    for start in range(0, len(shown), 2):
        cols = st.columns(2)
        for col, metric in zip(cols, shown[start:start + 2]):
            with col:
                metric_card(metric, currency)


# ============================================================
# REASONING
# ============================================================

elif page == "Reasoning":
    section("Cross-Metric Reasoning", "This is where individual metrics become a coherent analytical story.")

    if result.observations:
        for index, obs in enumerate(result.observations, start=1):
            render_observation(obs, index)
    else:
        st.markdown('<div class="notice">No structured reasoning observations were generated for this company.</div>', unsafe_allow_html=True)

    section("How to Read the Reasoning")
    st.markdown(
        "EQUICAFI distinguishes **what the metric says** from **what might explain it**. For example, a higher ROE can coexist with higher leverage; stronger EPS growth can differ from revenue growth because of margins or share-count changes; and lower FCF than net income does not automatically prove weak earnings quality. The related metrics are shown so the reader can inspect the connection."
    )

    if result.limitations:
        with st.expander("Analytical limitations"):
            for item in result.limitations:
                st.write(f"• {item}")


# ============================================================
# CAPITAL LAB
# ============================================================

elif page == "Capital Lab":
    section(
        "Capital Lab",
        "Interactive mathematics for hypothetical capital deployment and return scenarios.",
    )

    st.markdown(
        """
        <div class="lab-hero">
            <div class="kicker">Scenario instrument</div>
            <div class="lab-number">
                Capital determines scale.<br>
                The assumption determines the path.
            </div>
            <div class="lab-copy">
                Capital Lab uses the latest available price from the current
                EQUICAFI analysis automatically. You can optionally override
                that price when testing a hypothetical entry level.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="notice">
            <strong>Scenario, not prediction:</strong>
            The Bear, Base and Bull return rates below are assumptions supplied
            by you. EQUICAFI applies them mathematically; they are not forecasts
            or guaranteed returns.
        </div>
        """,
        unsafe_allow_html=True,
    )

    controls, output = st.columns([.9, 1.4])

    market_price = result.current_price.value
    currency = result.company.currency or "INR"
    is_demo = result.company.ticker.upper() == "DEMO"

    with controls:
        capital = st.number_input(
            "Hypothetical capital (₹)",
            min_value=100.0,
            value=50000.0,
            step=5000.0,
            format="%.2f",
        )

        use_override = st.toggle(
            "Override current price",
            value=False,
            help=(
                "By default Capital Lab uses the current price returned by "
                "the EQUICAFI analysis. Enable this only to model a "
                "hypothetical entry price."
            ),
        )

        if use_override:
            default_price = float(market_price) if market_price is not None else 1000.0
            share_price = st.number_input(
                "Hypothetical entry price (₹)",
                min_value=0.01,
                value=default_price,
                step=10.0,
                format="%.2f",
            )
            st.caption("Override active · market data is unchanged.")
        else:
            share_price = float(market_price) if market_price is not None else None
            if share_price is not None:
                price_source = "Synthetic DEMO dataset" if is_demo else "Yahoo Finance / provider data"
                st.markdown(
                    f"""
                    <div class="scenario-box">
                        <div class="scenario-title">Automatic price</div>
                        <div class="scenario-small">
                            <strong>{currency} {share_price:,.2f}</strong><br>
                            Source: {price_source}<br>
                            Status: latest available price in this analysis
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No usable current price is available for this analysis.")

        years = st.slider(
            "Holding period (years)",
            min_value=1,
            max_value=20,
            value=5,
        )

        st.markdown("**User-supplied annual return assumptions**")

        bear = st.number_input("Bear (%)", value=-10.0, step=1.0)
        base = st.number_input("Base (%)", value=10.0, step=1.0)
        bull = st.number_input("Bull (%)", value=20.0, step=1.0)

    with output:
        if share_price is None or share_price <= 0:
            st.markdown(
                """
                <div class="notice">
                    Capital Lab needs a usable share price. Enable
                    <strong>Override current price</strong> and enter a
                    hypothetical price to continue.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            deployment = simulate_return(
                capital=capital,
                share_price=share_price,
                annual_return_pct=base,
                years=years,
                scenario="Base",
            )

            st.markdown(
                f"""
                <div class="scenario-box">
                    <div class="scenario-title">Capital deployment</div>
                    <div class="scenario-small">
                        <strong>{deployment.shares:,} whole shares</strong><br>
                        Capital deployed: <strong>{currency} {deployment.invested:,.2f}</strong><br>
                        Cash remaining: <strong>{currency} {deployment.cash_remaining:,.2f}</strong><br>
                        Price used: <strong>{currency} {share_price:,.2f}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            labels = [("Bear", bear), ("Base", base), ("Bull", bull)]
            scenario_rows = []
            scenario_values = []

            for name, rate in labels:
                item = simulate_return(
                    capital=capital,
                    share_price=share_price,
                    annual_return_pct=rate,
                    years=years,
                    scenario=name,
                )
                scenario_rows.append(
                    {
                        "Scenario": name,
                        "Annual Return": f"{rate:.1f}%",
                        "Final Value": f"{currency_symbol(currency)}{item.final_value:,.0f}",
                        "Profit / Loss": f"{currency_symbol(currency)}{item.profit_loss:,.0f}",
                        "Total ROI": f"{item.total_roi_pct:.1f}%",
                        "CAGR": f"{item.cagr_pct:.1f}%",
                    }
                )
                scenario_values.append(item.final_value)

            st.dataframe(
                pd.DataFrame(scenario_rows),
                width="stretch",
                hide_index=True,
            )

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=[x[0] for x in labels],
                    y=scenario_values,
                    marker_color=["#3B8788", "#3B8788", "#3B8788"],
                    text=[f"{currency_symbol(currency)}{v:,.0f}" for v in scenario_values],
                    textposition="outside",
                    hovertemplate=(
                        "%{x}<br>"
                        + currency
                        + " %{y:,.0f}<extra></extra>"
                    ),
                )
            )
            fig.update_layout(
                title=f"Modeled value after {years} year(s)",
                template="plotly_dark",
                height=360,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#EBEBED", family="Inter"),
                margin=dict(l=5, r=5, t=48, b=5),
                yaxis=dict(gridcolor="rgba(59,135,136,.10)", zeroline=False),
                xaxis=dict(showgrid=False),
                showlegend=False,
            )
            st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

            st.markdown(
                """
                <div class="notice">
                    <strong>How to read this:</strong>
                    ROI is a percentage return. Changing the capital amount
                    changes the possible rupee gain or loss at a given return
                    assumption; it does not automatically create a different
                    percentage ROI. The scenario rates are user assumptions,
                    not EQUICAFI forecasts.
                </div>
                """,
                unsafe_allow_html=True,
            )

# FOOTER
# ============================================================

st.markdown(
    f"""
    <div class="footer">
        <strong>EQUICAFI</strong> · Equity Intelligence Engine<br>
        Analysis generated {datetime.now().strftime('%d %b %Y')} ·
        Educational / analytical use · Real provider data where available · DEMO is synthetic.
    </div>
    """,
    unsafe_allow_html=True,
)
