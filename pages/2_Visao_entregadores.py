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

st.set_page_config( page_title = 'Visão Entregadores', page_icon='🚚',layout='wide')


# import
df = pd.read_csv('train.csv')

df = df.copy()

linhas_selecionas = (df['Delivery_person_Age'] !='NaN ')
df= df.loc[linhas_selecionas,:].copy()

linhas_selecionas = (df['Road_traffic_density'] !='NaN ')
df= df.loc[linhas_selecionas,:].copy()

linhas_selecionas = (df['City'] !='NaN ')
df= df.loc[linhas_selecionas,:].copy()

df['Delivery_person_Age'] = df['Delivery_person_Age'].astype (int)

df['Delivery_person_Ratings'] = df ['Delivery_person_Ratings'].astype (float)

df['Order_Date'] = pd.to_datetime (df['Order_Date'], format='%d-%m-%Y')

linhas_selecionas = (df['multiple_deliveries'] !='NaN ')
df= df.loc[linhas_selecionas,:].copy()
df['Time_taken(min)'] = df['Time_taken(min)'].astype(str).str.extract('(\d+)').astype(float)

df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
df.loc[:,'Road_traffic_density'] = df.loc [:,'Road_traffic_density'].str.strip()
df.loc[:,'Type_of_vehicle'] = df.loc [:,'Type_of_vehicle'].str.strip()
df.loc[:,'Type_of_order'] = df.loc [:,'Type_of_order'].str.strip()
df.loc[:,'City'] = df.loc [:,'City'].str.strip()
df.loc[:,'Festival'] = df.loc [:,'Festival'].str.strip()

#==========================================
#Streamlit Barra Lateral Visão_empresa=========================

st.header ('Marketplace - Visão Entregadores')


st.sidebar.markdown (' # Cury Company')
st.sidebar.markdown (' ## Fastest Delivery in Town')
st.sidebar.markdown ("""---""")

st.sidebar.markdown ('## Powered by Arthur Lima')   


#==========================================
#Layout no Streamlit
###########################################

tab1, = st.tabs(['Visão Gerencial'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1,col2,col3,col4 = st.columns (4, gap='Large')
        with col1:
            maior_idade = df.loc[:,'Delivery_person_Age'].max() 
            col1.metric ('Maior idade',maior_idade)
            

        with col2:
            menor_idade = df.loc[:,'Delivery_person_Age'].min() 
            col2.metric ('Menor idade',menor_idade)
        
        with col3:
            melhor_cond = df.loc[:,'Vehicle_condition'].max() 
            col3.metric ('Melhor condição', melhor_cond)

        with col4:
            pior_cond = df.loc[:,'Vehicle_condition'].min() 
            col4.metric ('Pior condição',pior_cond)
            
    with st.container():
        st.markdown ("""---""")
        st.title('Avaliações')

        col1,col2 = st.columns (2)
        with col1:
            st.markdown ('##### Avaliação média por Entregador')
            df_avg_rating = (df.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                             .groupby ('Delivery_person_ID')
                             .mean().reset_index())
            st.dataframe (df_avg_rating)
            
        with col2:
            st.markdown ('##### Avaliação média por transito')
            df_avg__std_rating_by_traffic = (df.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                                 .groupby ('Road_traffic_density')
                                                  .agg( {'Delivery_person_Ratings': ['mean','std']}))
            
            df_avg__std_rating_by_traffic.columns = ['delivery_mean','delivery_std']
            df_avg__std_rating_by_traffic = df_avg__std_rating_by_traffic.reset_index()
            st.dataframe (df_avg__std_rating_by_traffic)

            
            st.markdown ('##### Avaliação média por clima')
            df_avg__std_Weatherconditions = (df.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                                .groupby ('Weatherconditions')
                                                .agg( {'Delivery_person_Ratings': ['mean','std']}))

            df_avg__std_Weatherconditions.columns = ['delivery_mean','delivery_std']
            df_avg__std_Weatherconditions = df_avg__std_Weatherconditions.reset_index()
            st.dataframe (df_avg__std_Weatherconditions)
            
    with st.container():
        st.markdown ("""---""")
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns (2)

        with col1:
            st.markdown ('Os Entregadores mais rápidos por cidade')
            df.columns = df.columns.str.strip()
            df['Time_taken(min)'] = df['Time_taken(min)'].astype(str).str.extract('(\d+)').astype(float)
            
            df2 = (df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                    .groupby(['City', 'Delivery_person_ID'])
                    .mean()
                    .sort_values(['City', 'Time_taken(min)'], ascending=True)
                    .reset_index())

            df_aux01 = df.loc[df['City'] == 'Metropolitan', :].head(5)
            df_aux02 = df.loc[df['City'] == 'Urban', :].head(5)
            df_aux03 = df.loc[df['City'] == 'Semi-Urban', :].head(5)

            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            st.dataframe(df2)


        
#OS FILTROS NAO ESTÃO FUNCIONANDO E NAO APARECE A ULTIMA TABELA
            

