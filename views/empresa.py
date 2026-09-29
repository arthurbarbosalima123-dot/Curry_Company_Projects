import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (AMBER, CITY_ORDER, ORANGE, TEAL, TRAFFIC_ORDER,
                   VIOLET, card_header, fmt, hero, kpi, load_data,
                   period_label, show_chart, sidebar_filters)

df = sidebar_filters(load_data())

hero(
    "📊 Marketplace",
    "Visão Empresa",
    f"Volume de pedidos, distribuição por trânsito e cidade e evolução semanal · {period_label(df)}",
)

orders_per_day = df.groupby("Order_Date")["ID"].count()
c1, c2, c3, c4 = st.columns(4, gap="medium")
kpi(c1, "Total de pedidos", fmt(len(df)), "📦", "no período filtrado", ORANGE)
kpi(c2, "Média por dia", fmt(orders_per_day.mean()), "📅", f"pico de {fmt(orders_per_day.max())} pedidos", TEAL)
kpi(c3, "Entregadores", fmt(df["Delivery_person_ID"].nunique()), "🛵", "IDs únicos", VIOLET)
kpi(c4, "Pedidos/entregador", fmt(len(df) / df["Delivery_person_ID"].nunique(), 1), "🔁",
    "média no período", AMBER)

st.write("")
tab1, tab2, tab3 = st.tabs(["📈 Visão Gerencial", "🗓️ Visão Tática", "🗺️ Visão Geográfica"])

# ----------------------------------------------------------
with tab1:
    with st.container(border=True):
        card_header("Pedidos por dia", "Quantidade de pedidos realizados em cada dia")
        daily = orders_per_day.reset_index(name="pedidos")
        fig = go.Figure(go.Bar(
            x=daily["Order_Date"], y=daily["pedidos"],
            marker=dict(color=daily["pedidos"], colorscale=[[0, "#8E2F1C"], [0.5, ORANGE], [1, AMBER]],
                        line=dict(width=0)),
            hovertemplate="%{x|%d/%m/%Y}<br><b>%{y} pedidos</b><extra></extra>",
        ))
        fig.update_layout(bargap=0.25)
        show_chart(fig, 360)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        with st.container(border=True):
            card_header("Pedidos por tipo de trânsito", "Participação de cada condição de tráfego")
            traffic = (df.groupby("Road_traffic_density")["ID"].count()
                       .reindex(TRAFFIC_ORDER).dropna().reset_index(name="pedidos"))
            fig = px.pie(traffic, values="pedidos", names="Road_traffic_density", hole=0.6,
                         color_discrete_sequence=[TEAL, AMBER, ORANGE, "#E0592A"])
            fig.update_traces(textinfo="percent+label", textposition="outside",
                              marker=dict(line=dict(color="#151826", width=3)),
                              hovertemplate="%{label}<br><b>%{value} pedidos</b> (%{percent})<extra></extra>")
            fig.update_layout(showlegend=False, annotations=[dict(
                text=f"<b>{fmt(traffic['pedidos'].sum())}</b><br><span style='font-size:12px'>pedidos</span>",
                x=0.5, y=0.5, showarrow=False, font=dict(size=20))])
            show_chart(fig, 400)

    with col2:
        with st.container(border=True):
            card_header("Pedidos por cidade e trânsito", "Volume de pedidos em cada combinação")
            city_traffic = (df.groupby(["City", "Road_traffic_density"])["ID"].count()
                            .reset_index(name="pedidos"))
            fig = px.bar(city_traffic, x="City", y="pedidos", color="Road_traffic_density",
                         barmode="group",
                         category_orders={"City": CITY_ORDER, "Road_traffic_density": TRAFFIC_ORDER},
                         color_discrete_sequence=[TEAL, AMBER, ORANGE, "#E0592A"],
                         labels={"City": "", "pedidos": "Pedidos", "Road_traffic_density": "Trânsito"})
            fig.update_traces(marker_line_width=0)
            fig.update_layout(legend=dict(orientation="h", y=1.12, x=0), bargap=0.2)
            show_chart(fig, 400)

# ----------------------------------------------------------
with tab2:
    weekly = df.groupby("week_of_year").agg(
        pedidos=("ID", "count"), entregadores=("Delivery_person_ID", "nunique")).reset_index()
    weekly["pedidos_por_entregador"] = weekly["pedidos"] / weekly["entregadores"]
    weekly["semana"] = "Sem " + weekly["week_of_year"].astype(str).str.zfill(2)

    with st.container(border=True):
        card_header("Pedidos por semana", "Evolução semanal do volume de pedidos")
        fig = go.Figure(go.Scatter(
            x=weekly["semana"], y=weekly["pedidos"], mode="lines+markers",
            line=dict(color=ORANGE, width=3, shape="spline"),
            marker=dict(size=9, color="#0E1117", line=dict(color=ORANGE, width=2.5)),
            fill="tozeroy", fillcolor="rgba(255,140,58,0.15)",
            hovertemplate="%{x}<br><b>%{y} pedidos</b><extra></extra>",
        ))
        show_chart(fig, 360)

    with st.container(border=True):
        card_header("Pedidos por entregador por semana", "Quantos pedidos, em média, cada entregador realizou")
        fig = go.Figure(go.Scatter(
            x=weekly["semana"], y=weekly["pedidos_por_entregador"], mode="lines+markers",
            line=dict(color=TEAL, width=3, shape="spline"),
            marker=dict(size=9, color="#0E1117", line=dict(color=TEAL, width=2.5)),
            fill="tozeroy", fillcolor="rgba(46,196,182,0.12)",
            hovertemplate="%{x}<br><b>%{y:.2f} pedidos/entregador</b><extra></extra>",
        ))
        show_chart(fig, 360)

# ----------------------------------------------------------
with tab3:
    valid = df.dropna(subset=["Delivery_location_latitude", "Delivery_location_longitude"])
    geo = (valid.groupby("city_name")
           .agg(lat=("Delivery_location_latitude", "median"),
                lon=("Delivery_location_longitude", "median"),
                pedidos=("ID", "count"),
                tempo=("Time_taken(min)", "mean"))
           .reset_index())
    mix = (valid.pivot_table(index="city_name", columns="Road_traffic_density", values="ID",
                             aggfunc="count", fill_value=0)
           .reindex(columns=TRAFFIC_ORDER, fill_value=0))
    geo["transito"] = geo["city_name"].map(
        lambda c: "<br>".join(f"{t}: {mix.loc[c, t]}" for t in TRAFFIC_ORDER))

    with st.container(border=True):
        card_header("Localização central das entregas",
                    "Mediana da localização por cidade · tamanho = nº de pedidos · cor = tempo médio")
        fig = go.Figure(go.Scattermapbox(
            lat=geo["lat"], lon=geo["lon"], mode="markers",
            marker=dict(size=geo["pedidos"], sizemode="area",
                        sizeref=2.0 * geo["pedidos"].max() / 45 ** 2, sizemin=6,
                        color=geo["tempo"], colorscale=[[0, TEAL], [0.5, AMBER], [1, ORANGE]],
                        opacity=0.85, colorbar=dict(title="Tempo (min)", thickness=12)),
            customdata=geo[["city_name", "pedidos", "tempo", "transito"]],
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} pedidos"
                          "<br>Tempo médio: %{customdata[2]:.1f} min"
                          "<br><br><b>Pedidos por trânsito</b><br>%{customdata[3]}<extra></extra>",
        ))
        fig.update_layout(mapbox=dict(style="carto-darkmatter", zoom=3.8,
                                      center=dict(lat=geo["lat"].mean(), lon=geo["lon"].mean())),
                          margin=dict(l=0, r=0, t=0, b=0))
        show_chart(fig, 600)

    with st.container(border=True):
        card_header("Pedidos por cidade e trânsito", "Distribuição do volume de pedidos em cada cidade")
        heat = mix.loc[geo.sort_values("pedidos", ascending=False)["city_name"]]
        fig = px.imshow(heat.T, aspect="auto", text_auto=True,
                        color_continuous_scale=[[0, "#151826"], [0.5, "#E0592A"], [1, AMBER]],
                        labels=dict(x="", y="", color="Pedidos"))
        fig.update_xaxes(tickangle=-40)
        show_chart(fig, 340)
