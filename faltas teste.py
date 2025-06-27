import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import date

# ========== LOGIN ==========
def login_page():
    st.markdown(
        '''
        <style>
        .login-box {
            max-width: 400px;
            margin: 10vh auto;
            padding: 2rem;
            border-radius: 10px;
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border: 2px solid #276db3;
        }
        .login-title {
            text-align: center;
            font-size: 24px;
            color: #276db3;
            margin-bottom: 1.5rem;
        }
        .stTextInput > div > input,
        .stPassword > div > input {
            border: 1px solid #5cb13b;
        }
        .stButton button {
            background-color: #5cb13b;
            color: white;
            font-weight: bold;
            border-radius: 5px;
        }
        </style>
        ''',
        unsafe_allow_html=True
    )

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.image("1.png", width=150)
    st.markdown('<div class="login-title">Painel de faltas APS - Acesso Restrito</div>', unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    username = st.text_input("Login")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if username == "apsipojuca" and password == "Ipojuca@2025*":
            st.session_state["autenticado"] = True
        else:
            st.error("Credenciais inválidas. Tente novamente.")

    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.get("autenticado"):
    login_page()
    st.stop()

# ========== PAINEL ==========
COR_PRINCIPAL = "#276db3"
st.set_page_config(page_title="Painel de Faltas - APS Ipojuca", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        background-color: #ffffff;
    }
    h1, h2, h3, h4, h5 {
        color: #276db3;
    }
    .stApp {
        background-color: #ffffff;
    }
    .css-1aumxhk, .st-bb, .st-at {
        background-color: #fdcd2f !important;
    }
    .stSidebar {
        background-color: #f0f0f0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Painel de Faltas - Atenção Primária à Saúde de Ipojuca")
st.image("images.png", width=150)

sheet_id = "1vf27HR8Pk-CiS_zT-1-0oskfsMlR6DPM63OX61SJzU0"
sheet_name = "respostas1"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

...
