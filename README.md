# 📊 Painel de Faltas - APS Ipojuca

Este painel foi desenvolvido para monitoramento e análise das ausências justificadas dos profissionais da Atenção Primária de Ipojuca.

## 🔐 Acesso Restrito

Este painel possui tela de login protegida com usuário e senha padrão:

- **Login:** apsipojuca  
- **Senha:** Ipojuca@2025*

## 🚀 Funcionalidades

- Filtros por:
  - Unidade de Saúde
  - Nome do Profissional
  - Tipo de Ausência
  - Data
- Resumo individual por profissional
- Visualização por gráficos:
  - Faltas por Tipo
  - Faltas por Dia
  - Faltas por Unidade
- Tabela com possibilidade de download em Excel (.xlsx)

## 🛠️ Como executar localmente

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o painel:
```bash
streamlit run faltas.py
```

---

Desenvolvido com carinho pela Diretoria de Atenção Primária de Ipojuca 💙