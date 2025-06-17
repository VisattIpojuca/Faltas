import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# CORES INSTITUCIONAIS
COR_PRINCIPAL = "#003366"
COR_SECUNDARIA = "#00ADEF"
COR_DESTAQUE = "#F8B133"

# CONFIGURAÇÃO
st.set_page_config(page_title="Painel de Faltas - APS Ipojuca", layout="wide")
st.markdown(f"""
    <style>
        h1 {{ color: {COR_PRINCIPAL}; }}
        .stButton>button {{ background-color: {COR_PRINCIPAL}; color: white; }}
    </style>
""", unsafe_allow_html=True)

st.title("📊 Painel de Faltas - Atenção Primária à Saúde de Ipojuca")

# Dados do Google Sheets
sheet_id = "1vf27HR8Pk-CiS_zT-1-0oskfsMlR6DPM63OX61SJzU0"
sheet_name = "respostas1"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Leitura
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

# Filtros
st.sidebar.header("🔍 Seleções")
df.sort_values("Unidade de Saúde", inplace=True)
unidades = st.sidebar.multiselect("Nome do Profissional", options=sorted(df["Unidade de Saúde"].dropna().unique()))
profissionais = st.sidebar.multiselect("Unidade de Saúde", options=sorted(df["Nome do Profissional"].dropna().unique()))
cargos = st.sidebar.multiselect("Cargo/Função", options=sorted(df["Cargo/Função"].dropna().unique()))
tipos = st.sidebar.multiselect("Tipo de Ausência", options=sorted(df["Tipo de Ausência"].dropna().unique()))

# Aplicando filtros
df_filtrado = df.copy()
if unidades:
    df_filtrado = df_filtrado[df_filtrado["Unidade de Saúde"].isin(unidades)]
if profissionais:
    df_filtrado = df_filtrado[df_filtrado["Nome do Profissional"].isin(profissionais)]
if cargos:
    df_filtrado = df_filtrado[df_filtrado["Cargo/Função"].isin(cargos)]
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

# Gráfico Faltas por Tipo (trocando legenda)
with col1:
    fig1 = px.histogram(
        df_filtrado,
        x="Tipo de Ausência",
        color="Nome do Profissional",  # Aqui trocamos de "Unidade de Saúde" para "Nome do Profissional"
        title="Faltas por Tipo"
    )
    st.plotly_chart(fig1, use_container_width=True)

# Gráfico Faltas por Dia
with col2:
    fig2 = px.histogram(
        df_filtrado,
        x="Cargo/Função",  # Aqui, na tabela visual, virou "Cargo/Função", que é na verdade a Data da Falta
        color="Tipo de Ausência",
        title="Faltas por Dia"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ➕ Gráfico Rank de Faltas por Nome do Profissional
st.subheader("📈 Rank de Faltas por Nome do Profissional")
rank = df_filtrado["Nome do Profissional"].value_counts().reset_index()
rank.columns = ["Nome do Profissional", "Total de Faltas"]

fig3 = px.line(
    rank,
    x="Nome do Profissional",
    y="Total de Faltas",
    markers=True,
    title="Rank de Faltas por Nome do Profissional"
)
fig3.update_traces(line_color=COR_PRINCIPAL)
st.plotly_chart(fig3, use_container_width=True)

# 🔥 Tabela Detalhada com nomes das colunas trocados
st.subheader("📋 Tabela Detalhada")
df_tabela = df_filtrado.rename(columns={
    "Nome do Profissional": "Unidade de Saúde",
    "Unidade de Saúde": "Nome do Profissional",
    "Data da Falta": "Cargo/Função",
    "Cargo/Função": "Data da Falta"
})
st.dataframe(df_tabela, use_container_width=True)

# Download XLSX da Tabela
xlsx_data = BytesIO()
df_tabela.to_excel(xlsx_data, index=False, engine='openpyxl')
xlsx_data.seek(0)
st.download_button(
    "📥 Baixar Excel",
    data=xlsx_data,
    file_name="faltas_aps_ipojuca.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
