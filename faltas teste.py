import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import date

# ========== LOGIN ==========
def login_page():
    st.markdown(
        """
        <style>
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
        """,
        unsafe_allow_html=True
    )

    # Exibir imagem institucional com link
    st.markdown(
        """
        <div style='text-align: center; margin-top: 5vh; margin-bottom: 2rem;'>
            <a href='https://www.ipojuca.pe.gov.br/' target='_blank'>
                <st.image("1.png", width=400/>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🔐 Acesso Restrito")

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
PALETA_CORES = ["#5cb13b", "#276db3", "#fdcd2f", "#ffffff"]

st.set_page_config(page_title="Painel de Faltas - APS Ipojuca", layout="wide")

st.title("📊 Painel de Faltas - Atenção Primária à Saúde de Ipojuca")
st.image("images.png", width=150)

sheet_id = "1vf27HR8Pk-CiS_zT-1-0oskfsMlR6DPM63OX61SJzU0"
sheet_name = "respostas1"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

df = pd.read_csv(url)
df.columns = [col.strip() for col in df.columns]
df.rename(columns={
    df.columns[0]: "Data de Envio",
    df.columns[1]: "Nome do Profissional",
    df.columns[2]: "Unidade de Saúde",
    df.columns[3]: "Data da Falta",
    df.columns[4]: "Tipo de Ausência",
    df.columns[5]: "Cargo/Função",
    df.columns[6]: "Observações"
}, inplace=True)

df["Data da Falta Formatada"] = pd.to_datetime(df["Data da Falta"], errors="coerce")

# Filtros
st.sidebar.header("🔍 Seleções")
df.sort_values("Unidade de Saúde", inplace=True)

unidades = st.sidebar.multiselect("Nome do Profissional", options=sorted(df["Unidade de Saúde"].dropna().unique()))
profissionais = st.sidebar.multiselect("Unidade de Saúde", options=sorted(df["Nome do Profissional"].dropna().unique()))

datas_opcoes = sorted(df["Cargo/Função"].dropna().unique())
hoje = date.today().strftime("%d/%m/%Y")
datas = st.sidebar.multiselect("Data", options=datas_opcoes, default=[hoje] if hoje in datas_opcoes else None)

tipos = st.sidebar.multiselect("Tipo de Ausência", options=sorted(df["Tipo de Ausência"].dropna().unique()))

# Aplicando filtros
df_filtrado = df.copy()
if unidades:
    df_filtrado = df_filtrado[df_filtrado["Unidade de Saúde"].isin(unidades)]
if profissionais:
    df_filtrado = df_filtrado[df_filtrado["Nome do Profissional"].isin(profissionais)]
if datas:
    df_filtrado = df_filtrado[df_filtrado["Cargo/Função"].isin(datas)]
if tipos:
    df_filtrado = df_filtrado[df_filtrado["Tipo de Ausência"].isin(tipos)]

# Resumo individual
if len(profissionais) == 1:
    st.subheader(f"📌 Resumo de {profissionais[0]}")
    dados_prof = df_filtrado[df_filtrado["Nome do Profissional"] == profissionais[0]]
    for _, row in dados_prof.iterrows():
        data_falta = str(row['Data da Falta']) if pd.notnull(row['Data da Falta']) else 'Sem Data'
        st.markdown(f"- 🗓️ {data_falta} | 🏥 {row['Unidade de Saúde']} | 📌 *{row['Tipo de Ausência']}* — {row['Observações']}")

# Gráficos
st.subheader("📊 Visualização de Dados")
col1, col2 = st.columns(2)

with col1:
    fig1 = px.histogram(df_filtrado, x="Tipo de Ausência", color="Nome do Profissional",
                        title="Faltas por Tipo", labels={"Nome do Profissional": "Unidade de Saúde"},
                        color_discrete_sequence=PALETA_CORES)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.histogram(df_filtrado, x="Cargo/Função", color="Tipo de Ausência",
                        title="Faltas por Dia", labels={"Cargo/Função": "Datas"},
                        color_discrete_sequence=PALETA_CORES)
    st.plotly_chart(fig2, use_container_width=True)

# Rank por Unidade
st.subheader("📊 Faltas por Unidade")
rank = df_filtrado["Nome do Profissional"].value_counts().reset_index()
rank.columns = ["Unidade de Saúde", "Total de Faltas"]
fig3 = px.bar(rank, x="Unidade de Saúde", y="Total de Faltas", title="Faltas por Unidade",
              text_auto=True, color="Total de Faltas", color_continuous_scale=["#fdcd2f", "#5cb13b"])
st.plotly_chart(fig3, use_container_width=True)

# Tabela Detalhada
st.subheader("📋 Tabela Detalhada")
df_tabela = df_filtrado.rename(columns={
    "Nome do Profissional": "Unidade de Saúde",
    "Unidade de Saúde": "Nome do Profissional",
    "Data da Falta": "Cargo/Função",
    "Cargo/Função": "Data da Falta"
})
st.dataframe(df_tabela, use_container_width=True)

# Exportar Excel
xlsx_data = BytesIO()
df_tabela.to_excel(xlsx_data, index=False, engine='openpyxl')
xlsx_data.seek(0)
st.download_button("📥 Baixar Excel", data=xlsx_data, file_name="faltas_aps_ipojuca.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
