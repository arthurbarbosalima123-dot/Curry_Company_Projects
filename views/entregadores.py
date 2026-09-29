import plotly.graph_objects as go
import streamlit as st

from utils import (CITY_ORDER, ORANGE, PINK, TEAL, TRAFFIC_ORDER,
                   VIOLET, card_header, hero, kpi, load_data,
                   period_label, section, show_chart, sidebar_filters)

df = sidebar_filters(load_data())

hero(
    "🛵 Marketplace",
    "Visão Entregadores",
    f"Perfil, avaliações e velocidade de entrega dos entregadores · {period_label(df)}",
)

c1, c2, c3, c4 = st.columns(4, gap="medium")
kpi(c1, "Maior idade", f"{df['Delivery_person_Age'].max()} anos", "👴", "entregador mais velho", ORANGE)
kpi(c2, "Menor idade", f"{df['Delivery_person_Age'].min()} anos", "🧑", "entregador mais novo", TEAL)
kpi(c3, "Melhor condição", str(df["Vehicle_condition"].max()), "🏍️", "condição do veículo (0 a 3)", VIOLET)
kpi(c4, "Pior condição", str(df["Vehicle_condition"].min()), "🔧", "condição do veículo (0 a 3)", PINK)


def rating_bar(data, category, order, color):
    agg = (data.groupby(category)["Delivery_person_Ratings"].agg(["mean", "std"])
           .reindex(order).dropna(how="all").reset_index())
    fig = go.Figure(go.Bar(
        x=agg[category], y=agg["mean"],
        error_y=dict(type="data", array=agg["std"], color="rgba(255,255,255,0.35)", thickness=1.5, width=6),
        marker=dict(color=color, line=dict(width=0)),
        text=agg["mean"].map(lambda v: f"{v:.2f}"), textposition="inside",
        insidetextanchor="end", textfont=dict(color="#0E1117", size=13),
        hovertemplate="%{x}<br>Média: <b>%{y:.2f}</b><br>Desvio: %{error_y.array:.2f}<extra></extra>",
    ))
    fig.update_yaxes(range=[3, 5.2], title="Avaliação")
    fig.update_layout(bargap=0.35)
    return fig


section("Avaliações", "média e desvio padrão")
col1, col2 = st.columns(2, gap="medium")
with col1:
    with st.container(border=True):
        card_header("Avaliação por tipo de trânsito", "Barras = média · linhas = desvio padrão")
        show_chart(rating_bar(df, "Road_traffic_density", TRAFFIC_ORDER, TEAL), 340)
with col2:
    with st.container(border=True):
        card_header("Avaliação por condição climática", "Barras = média · linhas = desvio padrão")
        weather_order = (df.groupby("Weatherconditions")["Delivery_person_Ratings"].mean()
                         .sort_values(ascending=False).index.tolist())
        show_chart(rating_bar(df, "Weatherconditions", weather_order, VIOLET), 340)

with st.container(border=True):
    card_header("Avaliação média por entregador", "Pesquise ou ordene clicando no cabeçalho das colunas")
    by_person = (df.groupby("Delivery_person_ID")
                 .agg(avaliacao=("Delivery_person_Ratings", "mean"),
                      entregas=("ID", "count"),
                      tempo=("Time_taken(min)", "mean"))
                 .sort_values("avaliacao", ascending=False).reset_index())
    st.dataframe(
        by_person, use_container_width=True, hide_index=True, height=320,
        column_config={
            "Delivery_person_ID": st.column_config.TextColumn("Entregador"),
            "avaliacao": st.column_config.ProgressColumn("Avaliação média", format="%.2f ★",
                                                         min_value=0, max_value=5),
            "entregas": st.column_config.NumberColumn("Entregas"),
            "tempo": st.column_config.NumberColumn("Tempo médio", format="%.1f min"),
        },
    )

section("Velocidade de entrega", "top 10 entregadores por cidade")
city = st.radio("Cidade", [c for c in CITY_ORDER if c in df["City"].unique()],
                horizontal=True, label_visibility="collapsed")
df_city = df[df["City"] == city]
times = (df_city.groupby("Delivery_person_ID")["Time_taken(min)"].mean()
         .reset_index(name="tempo"))


def ranking_chart(data, color):
    data = data.iloc[::-1]
    fig = go.Figure(go.Bar(
        x=data["tempo"], y=data["Delivery_person_ID"], orientation="h",
        marker=dict(color=color, line=dict(width=0)),
        text=data["tempo"].map(lambda v: f"{v:.1f} min"), textposition="outside",
        textfont=dict(color="#E6E8EF"),
        hovertemplate="%{y}<br><b>%{x:.1f} min</b><extra></extra>",
    ))
    fig.update_xaxes(title="Tempo médio (min)", range=[0, data["tempo"].max() * 1.25])
    fig.update_layout(bargap=0.3)
    return fig


col1, col2 = st.columns(2, gap="medium")
with col1:
    with st.container(border=True):
        card_header(f"⚡ 10 mais rápidos · {city}", "Menor tempo médio de entrega")
        show_chart(ranking_chart(times.nsmallest(10, "tempo"), TEAL), 420)
with col2:
    with st.container(border=True):
        card_header(f"🐢 10 mais lentos · {city}", "Maior tempo médio de entrega")
        show_chart(ranking_chart(times.nlargest(10, "tempo"), ORANGE), 420)
