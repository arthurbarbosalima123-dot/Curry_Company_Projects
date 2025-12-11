import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon ="🎲"
)


#Image_path = 'C:\\Users\\arthu\\Downloads\\ftc_programacao_python\\Repos\\dashboards\\'
image = Image.open ('logo.png')
st.sidebar.image(image,width=120)

st.sidebar.markdown (' # Cury Company')
st.sidebar.markdown (' ## Fastest Delivery in Town')
st.sidebar.markdown ("""---""")

st.write ("# Curry Company Growth Dashboard")

st.markdown(
    """
    Este dashboard foi criado para acompanhar as principais métricas de crescimento da empresa, entregadores e restaurantes.
    ### Como utilizar este Growth Dashboard?

### Visão Empresa
• **Visão Gerencial:** Métricas gerais de comportamento.  
• **Visão Tática:** Indicadores semanais de crescimento.  
• **Visão Geográfica:** Insights de geolocalização.
                
### Visão Entregadores
• Acompanhamento dos indicadores semanais de crescimento.
        
 ### Visão Restaurantes
• Indicadores semanais de crescimento dos restaurantes.
""")
