import streamlit as st

from utils import apply_style

st.set_page_config(
    page_title="Curry Company | Growth Dashboard",
    page_icon="🍛",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_style()
st.logo("assets/logo.png")

pages = {
    "Início": [
        st.Page("views/home.py", title="Home", icon=":material/home:", default=True),
    ],
    "Visões do negócio": [
        st.Page("views/empresa.py", title="Visão Empresa", icon=":material/monitoring:"),
        st.Page("views/entregadores.py", title="Visão Entregadores", icon=":material/two_wheeler:"),
        st.Page("views/restaurantes.py", title="Visão Restaurantes", icon=":material/restaurant:"),
    ],
}

st.navigation(pages).run()
