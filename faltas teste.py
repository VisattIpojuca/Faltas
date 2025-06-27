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
            background-color: #f2f2f2;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .login-title {
            text-align: center;
            font-size: 24px;
            color: #003366;
            margin-bottom: 1.5rem;
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
COR_PRINCIPAL = "#003366"
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
datas = st.sidebar.multiselect("Data", options=sorted(df["Cargo/Função"].dropna().unique()))
tipos = st.sidebar.multiselect("Tipo de Ausência", options=sorted(df["Tipo de Ausência"].dropna().unique()))

# Filtro por período com calendário (seguro)
data_validas = df["Data da Falta Formatada"].dropna()
if not data_validas.empty:
    data_min = data_validas.min()
    data_max = data_validas.max()
else:
    data_min = date.today()
    data_max = date.today()

periodo = st.sidebar.date_input("Período", [data_min, data_max])

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
if isinstance(periodo, list) and len(periodo) == 2:
    inicio, fim = periodo
    df_filtrado = df_filtrado[df_filtrado["Data da Falta Formatada"].between(inicio, fim)]

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
                        title="Faltas por Tipo", labels={"Nome do Profissional": "Unidade de Saúde"})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.histogram(df_filtrado, x="Cargo/Função", color="Tipo de Ausência",
                        title="Faltas por Dia", labels={"Cargo/Função": "Datas"})
    st.plotly_chart(fig2, use_container_width=True)

# Rank por Unidade
st.subheader("📊 Faltas por Unidade")
rank = df_filtrado["Nome do Profissional"].value_counts().reset_index()
rank.columns = ["Unidade de Saúde", "Total de Faltas"]
fig3 = px.bar(rank, x="Unidade de Saúde", y="Total de Faltas", title="Faltas por Unidade",
              text_auto=True, color="Total de Faltas")
fig3.update_traces(marker_color=COR_PRINCIPAL)
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
