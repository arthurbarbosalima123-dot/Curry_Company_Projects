import streamlit as st

from utils import (AMBER, ORANGE, TEAL, VIOLET, fmt, hero, kpi, load_data,
                   period_label, section)

df = load_data()

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand"><h2>Curry Company</h2><p>Fastest delivery in town</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-footer">Powered by <b>Arthur Lima</b></div>',
        unsafe_allow_html=True,
    )

hero(
    "🍛 Growth Dashboard",
    "Curry Company",
    "Acompanhe em um só lugar os principais KPIs de crescimento da empresa, "
    "dos entregadores e dos restaurantes do marketplace.",
)

c1, c2, c3, c4 = st.columns(4, gap="medium")
kpi(c1, "Pedidos", fmt(len(df)), "📦", period_label(df), ORANGE)
kpi(c2, "Entregadores", fmt(df["Delivery_person_ID"].nunique()), "🛵", "entregadores únicos", TEAL)
kpi(c3, "Tempo médio", fmt(df["Time_taken(min)"].mean(), 1, " min"), "⏱️", "por entrega", VIOLET)
kpi(c4, "Avaliação média", fmt(df["Delivery_person_Ratings"].mean(), 2, " ★"), "⭐", "dos entregadores", AMBER)

section("Como utilizar este dashboard", "escolha uma visão no menu lateral")

views = [
    ("📊", "Visão Empresa", "views/empresa.py", [
        "<b>Gerencial:</b> pedidos por dia, tráfego e cidades",
        "<b>Tática:</b> evolução semanal de pedidos",
        "<b>Geográfica:</b> mapa com a localização central das entregas",
    ]),
    ("🛵", "Visão Entregadores", "views/entregadores.py", [
        "Idades e condições dos veículos",
        "Avaliações por trânsito e clima",
        "Ranking dos entregadores mais rápidos e mais lentos",
    ]),
    ("🍽️", "Visão Restaurantes", "views/restaurantes.py", [
        "Distância média das entregas",
        "Tempo de entrega com e sem festival",
        "Tempo por cidade, tráfego e tipo de pedido",
    ]),
]

cols = st.columns(3, gap="medium")
for col, (emoji, title, page, items) in zip(cols, views):
    with col:
        bullets = "".join(f"<li>{i}</li>" for i in items)
        st.markdown(
            f'<div class="view-card"><div class="emoji">{emoji}</div><h4>{title}</h4><ul>{bullets}</ul></div>',
            unsafe_allow_html=True,
        )
        st.page_link(page, label=f"Abrir {title}", icon=":material/arrow_forward:")

st.caption("Use os filtros da barra lateral em cada visão para explorar os dados por período, trânsito, clima e cidade.")
