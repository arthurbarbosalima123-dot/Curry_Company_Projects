import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (AMBER, BLUE, CITY_ORDER, ORANGE, TEAL,
                   VIOLET, card_header, fmt, hero, kpi,
                   load_data, period_label, section, show_chart,
                   sidebar_filters)

df = sidebar_filters(load_data())

hero(
    "🍽️ Marketplace",
    "Visão Restaurantes",
    f"Distâncias e tempos de entrega por cidade, trânsito, tipo de pedido e festivais · {period_label(df)}",
)

festival = df.groupby("Festival")["Time_taken(min)"].agg(["mean", "std"])


def fest(flag, stat):
    return fmt(festival.loc[flag, stat], 1, " min") if flag in festival.index else "—"


c1, c2, c3 = st.columns(3, gap="medium")
kpi(c1, "Entregadores", fmt(df["Delivery_person_ID"].nunique()), "🛵", "únicos", ORANGE)
kpi(c2, "Distância média", fmt(df["distance_km"].mean(), 1, " km"), "📍", "restaurante → cliente", TEAL)
kpi(c3, "Tipos de pedido", str(df["Type_of_order"].nunique()), "🧾", ", ".join(sorted(df["Type_of_order"].unique())), BLUE)
st.write("")
c1, c2, c3, c4 = st.columns(4, gap="medium")
kpi(c1, "Tempo c/ festival", fest("Yes", "mean"), "🎉", "tempo médio de entrega", VIOLET)
kpi(c2, "Desvio c/ festival", fest("Yes", "std"), "📊", "desvio padrão", VIOLET)
kpi(c3, "Tempo s/ festival", fest("No", "mean"), "🍛", "tempo médio de entrega", AMBER)
kpi(c4, "Desvio s/ festival", fest("No", "std"), "📊", "desvio padrão", AMBER)

section("Distância e tempo por cidade")
col1, col2 = st.columns(2, gap="medium")
with col1:
    with st.container(border=True):
        card_header("Distância média por cidade", "Km entre restaurante e local de entrega")
        dist = (df.groupby("City")["distance_km"].mean()
                .reindex(CITY_ORDER).dropna().reset_index())
        fig = go.Figure(go.Pie(
            labels=dist["City"], values=dist["distance_km"], hole=0.6,
            pull=[0.04] * len(dist), marker=dict(colors=[TEAL, ORANGE, VIOLET],
                                                 line=dict(color="#151826", width=3)),
            texttemplate="%{label}<br><b>%{value:.1f} km</b>", textposition="outside",
            hovertemplate="%{label}<br><b>%{value:.2f} km</b><extra></extra>",
        ))
        fig.update_layout(showlegend=False)
        show_chart(fig, 380)

with col2:
    with st.container(border=True):
        card_header("Tempo médio de entrega por cidade", "Barras = média · linhas = desvio padrão")
        by_city = (df.groupby("City")["Time_taken(min)"].agg(["mean", "std"])
                   .reindex(CITY_ORDER).dropna().reset_index())
        fig = go.Figure(go.Bar(
            x=by_city["City"], y=by_city["mean"],
            error_y=dict(type="data", array=by_city["std"], color="rgba(255,255,255,0.35)", thickness=1.5, width=8),
            marker=dict(color=[TEAL, ORANGE, VIOLET][:len(by_city)], line=dict(width=0)),
            text=by_city["mean"].map(lambda v: f"{v:.1f} min"), textposition="inside",
            insidetextanchor="end", textfont=dict(color="#0E1117", size=13),
            hovertemplate="%{x}<br>Média: <b>%{y:.1f} min</b><extra></extra>",
        ))
        fig.update_yaxes(title="Minutos")
        fig.update_layout(bargap=0.45)
        show_chart(fig, 380)

section("Tempo por cidade e tipo de trânsito")
with st.container(border=True):
    card_header("Tempo médio por cidade e trânsito",
                "Tamanho = tempo médio · cor = desvio padrão · clique para expandir")
    sun = (df.groupby(["City", "Road_traffic_density"])["Time_taken(min)"]
           .agg(avg_time="mean", std_time="std").reset_index())
    fig = px.sunburst(
        sun, path=["City", "Road_traffic_density"], values="avg_time", color="std_time",
        color_continuous_scale=[[0, "#1F3B4D"], [0.5, TEAL], [1, AMBER]],
        labels={"avg_time": "Tempo médio", "std_time": "Desvio padrão"},
    )
    fig.update_traces(marker=dict(line=dict(color="#151826", width=2)),
                      hovertemplate="<b>%{label}</b><br>Tempo médio: %{value:.1f} min"
                                    "<br>Desvio: %{color:.2f}<extra></extra>")
    fig.update_layout(coloraxis_colorbar=dict(title="Desvio", thickness=12))
    show_chart(fig, 520)

section("Tempo por cidade e tipo de pedido")
by_order = (df.groupby(["City", "Type_of_order"])["Time_taken(min)"]
            .agg(avg_time="mean", std_time="std").reset_index())
col1, col2 = st.columns([3, 2], gap="medium")
with col1:
    with st.container(border=True):
        card_header("Tempo médio por tipo de pedido", "Comparação entre cidades")
        fig = px.bar(by_order, x="City", y="avg_time", color="Type_of_order", barmode="group",
                     error_y="std_time", category_orders={"City": CITY_ORDER},
                     color_discrete_sequence=[ORANGE, TEAL, VIOLET, BLUE],
                     labels={"City": "", "avg_time": "Minutos", "Type_of_order": "Pedido"})
        fig.update_traces(marker_line_width=0, error_y=dict(color="rgba(255,255,255,0.3)", thickness=1))
        fig.update_layout(legend=dict(orientation="h", y=1.12, x=0), bargap=0.2)
        show_chart(fig, 400)
with col2:
    with st.container(border=True):
        card_header("Tabela detalhada", "Média e desvio padrão em minutos")
        st.dataframe(
            by_order, use_container_width=True, hide_index=True, height=400,
            column_config={
                "City": st.column_config.TextColumn("Cidade"),
                "Type_of_order": st.column_config.TextColumn("Pedido"),
                "avg_time": st.column_config.ProgressColumn(
                    "Tempo médio", format="%.1f min", min_value=0,
                    max_value=float(by_order["avg_time"].max())),
                "std_time": st.column_config.NumberColumn("Desvio", format="%.2f"),
            },
        )
