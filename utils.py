"""Funções compartilhadas: carga/limpeza dos dados, estilo visual e componentes."""
from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ==========================================================
# Paleta
# ==========================================================
ORANGE = "#FF8C3A"
AMBER = "#FFC857"
TEAL = "#2EC4B6"
VIOLET = "#8B7CF6"
PINK = "#EF476F"
BLUE = "#4EA8DE"
PALETTE = [ORANGE, TEAL, VIOLET, AMBER, PINK, BLUE]

TEXT = "#E6E8EF"
MUTED = "#9AA0B4"
GRID = "rgba(255,255,255,0.06)"

TRAFFIC_ORDER = ["Low", "Medium", "High", "Jam"]
CITY_ORDER = ["Semi-Urban", "Urban", "Metropolitan"]

# prefixo do ID do entregador -> cidade real
CITY_NAMES = {
    "JAP": "Jaipur", "RANCHI": "Ranchi", "BANG": "Bangalore", "SUR": "Surat", "HYD": "Hyderabad",
    "MUM": "Mumbai", "MYS": "Mysore", "COIMB": "Coimbatore", "VAD": "Vadodara", "INDO": "Indore",
    "CHEN": "Chennai", "PUNE": "Pune", "AGR": "Agra", "LUDH": "Ludhiana", "ALH": "Allahabad",
    "KNP": "Kanpur", "DEH": "Dehradun", "GOA": "Goa", "AURG": "Aurangabad", "KOC": "Kochi",
    "KOL": "Kolkata", "BHP": "Bhopal",
}

pio.templates["curry"] = go.layout.Template(
    layout=dict(
        font=dict(family="Inter, sans-serif", color=TEXT, size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=PALETTE,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor=GRID, zeroline=False, linecolor=GRID, tickfont=dict(color=MUTED)),
        yaxis=dict(gridcolor=GRID, zeroline=False, linecolor=GRID, tickfont=dict(color=MUTED)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED)),
        hoverlabel=dict(bgcolor="#1E2233", bordercolor=ORANGE, font=dict(color=TEXT)),
    )
)
pio.templates.default = "plotly_dark+curry"


# ==========================================================
# Dados
# ==========================================================
@st.cache_data(show_spinner="Carregando dados...")
def load_data(path: str = "train.csv") -> pd.DataFrame:
    df = pd.read_csv(path)

    # remove espaços extras de todas as colunas de texto
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    df["Weatherconditions"] = df["Weatherconditions"].str.replace("conditions ", "", regex=False)
    df["City"] = df["City"].replace("Metropolitian", "Metropolitan")

    cols_nan = [
        "Delivery_person_Age", "Delivery_person_Ratings", "Road_traffic_density",
        "City", "Festival", "multiple_deliveries", "Weatherconditions",
    ]
    for col in cols_nan:
        df = df[df[col] != "NaN"]
    df = df.dropna(subset=["Delivery_person_Ratings"])

    df["Delivery_person_Age"] = df["Delivery_person_Age"].astype(int)
    df["Delivery_person_Ratings"] = df["Delivery_person_Ratings"].astype(float)
    df["multiple_deliveries"] = df["multiple_deliveries"].astype(int)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="%d-%m-%Y")
    df["Time_taken(min)"] = df["Time_taken(min)"].str.extract(r"(\d+)").astype(float)
    prefix = df["Delivery_person_ID"].str.extract(r"^([A-Z]+)RES")[0]
    df["city_name"] = prefix.map(CITY_NAMES).fillna(prefix)
    df["week_of_year"] = df["Order_Date"].dt.strftime("%U").astype(int)

    # algumas coordenadas vêm com sinal trocado ou zeradas (erro de cadastro)
    coords = ["Restaurant_latitude", "Restaurant_longitude",
              "Delivery_location_latitude", "Delivery_location_longitude"]
    df[coords] = df[coords].abs().where(df[coords].abs() > 1)

    # distância restaurante -> cliente (haversine vetorizado, em km)
    lat1, lon1, lat2, lon2 = (
        np.radians(df[c]) for c in [
            "Restaurant_latitude", "Restaurant_longitude",
            "Delivery_location_latitude", "Delivery_location_longitude",
        ]
    )
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    df["distance_km"] = 6371 * 2 * np.arcsin(np.sqrt(a))

    return df.reset_index(drop=True)


# ==========================================================
# Estilo
# ==========================================================
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, button, input {{
    font-family: 'Inter', sans-serif !important;
}}

#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #151826 0%, #0E1117 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}}
.sidebar-brand {{ text-align: center; margin: .2rem 0 1rem 0; }}
.sidebar-brand h2 {{ margin: 0; font-weight: 800; font-size: 1.35rem; color: {TEXT}; }}
.sidebar-brand p {{ margin: 0; color: {ORANGE}; font-size: .8rem; letter-spacing: .12em; text-transform: uppercase; }}
.sidebar-footer {{
    margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.07);
    color: {MUTED}; font-size: .8rem; text-align: center;
}}
.sidebar-footer b {{ color: {ORANGE}; }}

/* ---------- Hero ---------- */
.hero {{
    position: relative; overflow: hidden;
    background: radial-gradient(circle at 85% 20%, rgba(255,200,87,.35), transparent 40%),
                linear-gradient(120deg, #FF8C3A 0%, #E0592A 55%, #8E2F1C 100%);
    border-radius: 20px; padding: 2rem 2.2rem; margin-bottom: 1.6rem;
    box-shadow: 0 12px 40px rgba(255,140,58,.18);
}}
.hero .eyebrow {{
    display: inline-block; background: rgba(0,0,0,.2); color: #FFF4EA;
    padding: .25rem .75rem; border-radius: 999px; font-size: .75rem;
    font-weight: 600; letter-spacing: .08em; text-transform: uppercase;
}}
.hero h1 {{ color: #FFFFFF; font-size: 2.2rem; font-weight: 800; margin: .6rem 0 .3rem 0; padding: 0; }}
.hero p {{ color: rgba(255,255,255,.88); font-size: 1.02rem; margin: 0; max-width: 780px; }}

/* ---------- KPI cards ---------- */
.kpi-card {{
    position: relative; overflow: hidden;
    background: linear-gradient(145deg, #1B1F2E 0%, #141722 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 1.1rem 1.2rem; height: 100%;
    box-shadow: 0 6px 24px rgba(0,0,0,.25);
    transition: transform .15s ease, border-color .15s ease;
}}
.kpi-card:hover {{ transform: translateY(-3px); border-color: rgba(255,140,58,.45); }}
.kpi-card::before {{
    content: ""; position: absolute; left: 0; top: 0; height: 100%; width: 4px;
    background: var(--accent);
}}
.kpi-top {{ display: flex; align-items: center; justify-content: space-between; }}
.kpi-label {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: {MUTED}; font-size: .78rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; }}
.kpi-icon {{
    flex-shrink: 0; font-size: 1.15rem; width: 2.2rem; height: 2.2rem; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    background: color-mix(in srgb, var(--accent) 18%, transparent);
}}
.kpi-value {{ color: {TEXT}; font-size: 1.9rem; font-weight: 800; margin-top: .35rem; line-height: 1.1; }}
.kpi-sub {{ color: {MUTED}; font-size: .8rem; margin-top: .25rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

/* ---------- Section title ---------- */
.section-title {{ display: flex; align-items: center; gap: .6rem; margin: 1.8rem 0 .8rem 0; }}
.section-title .bar {{ width: 6px; height: 1.6rem; border-radius: 4px; background: linear-gradient({ORANGE}, {AMBER}); }}
.section-title h3 {{ margin: 0; padding: 0; font-size: 1.3rem; font-weight: 700; color: {TEXT}; }}
.section-title span {{ color: {MUTED}; font-size: .9rem; }}

/* ---------- Chart cards (st.container(border=True)) ---------- */
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > .stVerticalBlock > .stElementContainer > .stMarkdown .card-title) {{
    background: #151826; border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    box-shadow: 0 6px 24px rgba(0,0,0,.25);
}}
.card-title {{ font-weight: 700; font-size: 1rem; color: {TEXT}; margin-bottom: .1rem; }}
.card-sub {{ color: {MUTED}; font-size: .82rem; margin-bottom: .4rem; }}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {{
    gap: .4rem; background: #151826; padding: .35rem; border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.06);
}}
.stTabs [data-baseweb="tab"] {{
    height: 2.6rem; padding: 0 1.2rem; border-radius: 9px; color: {MUTED}; font-weight: 600;
}}
.stTabs [aria-selected="true"] {{ background: {ORANGE} !important; color: #FFFFFF !important; }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none; }}

/* ---------- Home: cards de navegação ---------- */
.view-card {{
    background: linear-gradient(145deg, #1B1F2E 0%, #141722 100%);
    border: 1px solid rgba(255,255,255,0.06); border-radius: 18px;
    padding: 1.4rem; min-height: 290px; margin-bottom: .6rem;
}}
.view-card .emoji {{ font-size: 2rem; }}
.view-card h4 {{ margin: .5rem 0 .4rem 0; padding: 0; font-weight: 700; color: {TEXT}; }}
.view-card ul {{ color: {MUTED}; padding-left: 1.1rem; margin: 0; font-size: .92rem; }}
.view-card li {{ margin-bottom: .25rem; }}
</style>
"""


def apply_style() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


# ==========================================================
# Componentes
# ==========================================================
def hero(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""<div class="hero">
            <span class="eyebrow">{eyebrow}</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>""",
        unsafe_allow_html=True,
    )


def kpi(col, label: str, value: str, icon: str, sub: str = "", accent: str = ORANGE) -> None:
    col.markdown(
        f"""<div class="kpi-card" style="--accent:{accent}">
            <div class="kpi-top"><span class="kpi-label">{label}</span><span class="kpi-icon">{icon}</span></div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def section(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""<div class="section-title"><div class="bar"></div><h3>{title}</h3><span>{subtitle}</span></div>""",
        unsafe_allow_html=True,
    )


def card_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="card-title">{title}</div><div class="card-sub">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def show_chart(fig, height: int = 380) -> None:
    fig.update_layout(template="plotly_dark+curry", height=height,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True, theme=None, config={"displayModeBar": False})


def fmt(value: float, decimals: int = 0, suffix: str = "") -> str:
    text = f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text}{suffix}"


# ==========================================================
# Sidebar com filtros
# ==========================================================
def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><h2>Curry Company</h2><p>Fastest delivery in town</p></div>',
            unsafe_allow_html=True,
        )

        st.markdown("#### 🎛️ Filtros")
        min_d, max_d = df["Order_Date"].min().date(), df["Order_Date"].max().date()
        date_range = st.slider(
            "Período dos pedidos",
            min_value=min_d, max_value=max_d, value=(min_d, max_d), format="DD/MM/YY",
        )
        traffic = st.multiselect(
            "Condição de trânsito", TRAFFIC_ORDER, default=TRAFFIC_ORDER,
        )
        weather_opts = sorted(df["Weatherconditions"].unique())
        weather = st.multiselect("Condição climática", weather_opts, default=weather_opts)
        cities = st.multiselect("Tipo de cidade", CITY_ORDER, default=CITY_ORDER)

        st.markdown(
            '<div class="sidebar-footer">Powered by <b>Arthur Lima</b></div>',
            unsafe_allow_html=True,
        )

    start, end = (pd.Timestamp(d) for d in date_range)
    mask = (
        df["Order_Date"].between(start, end)
        & df["Road_traffic_density"].isin(traffic)
        & df["Weatherconditions"].isin(weather)
        & df["City"].isin(cities)
    )
    filtered = df[mask]
    if filtered.empty:
        st.warning("Nenhum pedido encontrado para os filtros selecionados. Ajuste os filtros na barra lateral.")
        st.stop()
    return filtered


def period_label(df: pd.DataFrame) -> str:
    d0: date = df["Order_Date"].min()
    d1: date = df["Order_Date"].max()
    return f"{d0:%d/%m/%Y} a {d1:%d/%m/%Y}"
