#Libraries
from haversine import haversine
import plotly.express as px

# bibliotecas necessarias
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import folium
import numpy as np
from streamlit_folium import folium_static

st.set_page_config( page_title = 'Visão Restaurantes', page_icon='📈',layout='wide')



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

st.header ('Marketplace - Visão Restaurantes')


st.sidebar.markdown (' # Cury Company')
st.sidebar.markdown (' ## Fastest Delivery in Town')
st.sidebar.markdown ("""---""")

st.sidebar.markdown ('## Powered by Arthur Lima')   


tab1, = st.tabs(['Visão Gerencial'])

with tab1:
    with st.container():
        st.markdown('''---''')
        st.title('Overal Metrics')
        
        col1,col2,col3,col4,col5 = st.columns (5)
        with col1:
            delivery_nunique = df.loc[:,'Delivery_person_ID'].nunique()
            col1.metric ('Entregadores únicos',delivery_nunique)
            
        with col2:
            df_aux = (df.loc[:, ['Time_taken(min)','Festival']]
                          .groupby('Festival')
                          .agg({'Time_taken(min)':['mean','std']}))

            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round (df_aux.loc[df_aux['Festival'] == 'Yes','avg_time'],2)
            col2.metric ('Tempo Médio Entregas', df_aux)
            
        with col3:
            df_aux = (df.loc[:, ['Time_taken(min)','Festival']]
                          .groupby('Festival')
                          .agg({'Time_taken(min)':['mean','std']}))

            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round (df_aux.loc[df_aux['Festival'] == 'Yes','std_time'],2)
            col3.metric ('Dvp da Entrega', df_aux)
            
        with col4:
            df_aux = (df.loc[:, ['Time_taken(min)','Festival']]
                          .groupby('Festival')
                          .agg({'Time_taken(min)':['mean','std']}))

            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round (df_aux.loc[df_aux['Festival'] == 'No','avg_time'],2)
            
            col4.metric ('Tempo Médio', df_aux)
        with col5:
            df_aux = (df.loc[:, ['Time_taken(min)','Festival']]
                          .groupby('Festival')
                          .agg({'Time_taken(min)':['mean','std']}))

            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round (df_aux.loc[df_aux['Festival'] == 'No','std_time'],2)
            col5.metric ('Dvp da Entrega', df_aux)

    with st.container():
        st.markdown('''---''')
        st.markdown('###### O TEMPO MÉDIO E O DESVIO PADRAO DE ENTREGA POR CIDADE E POR TIPO DE TRAFEGO')
         
        df_aux = (df.loc[:,['City','Time_taken(min)','Road_traffic_density']]
                    .groupby(['City','Road_traffic_density'])
                    .agg({'Time_taken(min)':['mean','std']}))
            
        df_aux.columns = ['avg_time','std_time']
        df_aux = df_aux.reset_index()

        fig = px.sunburst(df_aux, path=['City','Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time']))
        st.plotly_chart(fig)
         
 
    with st.container():
        st.markdown('''---''')
        st.markdown('### O Tempo médio e o desvio padrao de entrega por cidade')
            
        df7 = df.loc[:,['City','Time_taken(min)']].groupby ('City').agg({'Time_taken(min)':['mean','std']})
        df7.columns = ['avg_time','std_time']
        df7 = df7.reset_index()

        fig= go.Figure()
        fig.add_trace( go.Bar (name='Control', x=df7['City'], y=df7['avg_time'], error_y=dict (type='data', array=df7['std_time'])))
        fig.update_layout(barmode='group')
        st.plotly_chart(fig)
        
    with st.container():
        st.markdown('''---''')
        st.markdown('###### O TEMPO MÉDIO E O DESVIO PADRAO DE ENTREGA POR CIDADE E TIPO DE PEDIDO')
        
        df_aux = (df.loc[:,['City','Time_taken(min)','Type_of_order']]
                    .groupby(['City','Type_of_order'])
                    .agg({'Time_taken(min)':['mean','std']}))
        
        df_aux.columns = ['avg_time','std_time']
        df_aux = df_aux.reset_index()
        st.dataframe (df_aux)






































