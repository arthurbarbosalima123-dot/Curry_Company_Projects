    
#Libraries
from haversine import haversine
import plotly.express as px

# bibliotecas necessarias
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
import plotly.express as px
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title = 'Visão Restaurantes', page_icon='🍽',layout='wide')


# import
df = pd.read_csv('train.csv')

df = df.copy()

linhas_selecionas = (df['Delivery_person_Age'] !='NaN ')
df= df.loc[linhas_selecionas,:].copy()

linhas_selecionas = (df['Road_traffic_density'] !='NaN ')
df= df.loc[linhas_selecionas,:].copy()

linhas_selecionas = (df['City'] !='NaN ')
df= df.loc[linhas_selecionas,:].copy()

linhas_selecionas = (df['Festival'] !='NaN ')
df= df.loc[linhas_selecionas,:].copy()

df['Delivery_person_Age'] = df['Delivery_person_Age'].astype (int)

df['Delivery_person_Ratings'] = df ['Delivery_person_Ratings'].astype (float)

df['Order_Date'] = pd.to_datetime (df['Order_Date'], format='%d-%m-%Y')

linhas_selecionas = (df['multiple_deliveries'] !='NaN ')
df= df.loc[linhas_selecionas,:].copy()
df['multiple_deliveries'] = df['multiple_deliveries'].astype (int)
df['Time_taken(min)'] = df['Time_taken(min)'].astype(str).str.extract('(\d+)').astype(float)

df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
df.loc[:,'Road_traffic_density'] = df.loc [:,'Road_traffic_density'].str.strip()
df.loc[:,'Type_of_vehicle'] = df.loc [:,'Type_of_vehicle'].str.strip()
df.loc[:,'Type_of_order'] = df.loc [:,'Type_of_order'].str.strip()
df.loc[:,'City'] = df.loc [:,'City'].str.strip()
df.loc[:,'Festival'] = df.loc [:,'Festival'].str.strip()


#==========================================
#Streamlit Barra Lateral Visão_empresa=========================

st.header ('Marketplace - Visão Empresa')


st.sidebar.markdown (' # Cury Company')
st.sidebar.markdown (' ## Fastest Delivery in Town')
st.sidebar.markdown ("""---""")

st.sidebar.markdown ('## Powered by Arthur Lima')   
st.dataframe (df)
#==========================================
#Layout no Streamlit
###########################################

tab1, tab2, tab3 = st.tabs ( ['Visão Gerencial','Visão Tática','Visão Geográfica'] )

with tab1:
    with st.container():
        st.markdown('# Pedidos por dia')
        cols = ('ID','Order_Date')
        df_aux = df.loc[:,cols].groupby (['Order_Date']).count().reset_index()
        df_aux.head()
    
        fig = px.bar (df_aux, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.header(' Traffic Order Share')
            df_aux = df.loc[:,['ID','Road_traffic_density']].groupby ('Road_traffic_density').count().reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] !='NaN',:]
            df_aux  ['entregas_perc'] = df_aux ['ID']/df_aux['ID'].sum()

            fig =px.pie (df_aux, values = 'entregas_perc', names ='Road_traffic_density')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.header(' Traffic Order City')
            df_aux = df.loc[:,['ID', 'City','Road_traffic_density']].groupby (['City', 'Road_traffic_density']) .count().reset_index()
            df_aux = df_aux.loc[df_aux['City'] !='NaN',:]
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] !='NaN',:]

            fig = px.scatter (df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart (fig, use_container_width=True)
with tab2:
    with st.container():
        st.markdown('# Pedidos por Semana')
        df['week_of_year'] = df['Order_Date'].dt.strftime ('%U')
        df.head()
        df_aux = df.loc[:,['ID','week_of_year']].groupby (['week_of_year']).count().reset_index()
        df_aux.head()
        fig = px.line(df_aux, x='week_of_year', y='ID')
        st.plotly_chart (fig, use_container_width=True)
    with st.container():
        st.markdown('# Order Share by Week')
        df_aux01 = df.loc[:,['ID','week_of_year']].groupby(['week_of_year']).count().reset_index()
        df_aux02 = df.loc[:,['Delivery_person_ID','week_of_year']].groupby ('week_of_year').nunique().reset_index()
        df_aux = pd.merge (df_aux01, df_aux02, how='inner')
        df_aux ['order_by_deliver'] = df_aux ['ID']/df_aux['Delivery_person_ID']
        fig = px.line (df_aux, x='week_of_year', y='order_by_deliver')
        st.plotly_chart (fig, use_container_width=True)

with tab3:
    st.header(' Country Maps')
    df_aux = df.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] !='NaN',:]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] !='NaN',:]

    map = folium.Map()
    folium_static (map, width=1024 , height=600)



print (df.head())


## Os filtros nao estao funcionandooo