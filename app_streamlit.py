"""
Interface Web - Streamlit
Agente IA para Análise de Consumo de Energia
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from agent_consumo import ConsumptionAnalyzer, run_agent
import json

st.set_page_config(
    page_title="🔌 Assistente de Energia",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main { max-width: 900px; }
    .stButton > button {
        background-color: #FF6B35;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================

st.title("⚡ Assistente de Análise de Consumo de Energia")
st.markdown("*Faça perguntas sobre seu consumo de energia usando IA*")

# ============================================
# SIDEBAR - CONFIGURAÇÕES
# ============================================

with st.sidebar:
    st.header("⚙️ Configuração")

    # Seleção do modelo Ollama
    model = st.selectbox(
        "Modelo Ollama:",
        ["llama2", "mistral", "neural-chat", "orca-mini"],
        help="Certifique-se de que o modelo está instalado no Ollama"
    )

    # Upload ou seleção de dataset
    st.subheader("📊 Dataset")

    dataset_option = st.radio(
        "Selecione o dataset:",
        ["Usar arquivo local", "Upload novo"]
    )

    dataset_path = None

    if dataset_option == "Usar arquivo local":
        # Procura por CSVs no diretório
        csv_files = list(Path("/home/user/Python").glob("*.csv"))

        if csv_files:
            selected_file = st.selectbox(
                "Arquivos disponíveis:",
                csv_files,
                format_func=lambda x: x.name
            )
            dataset_path = str(selected_file)
        else:
            st.warning("❌ Nenhum arquivo CSV encontrado no diretório")

    else:
        uploaded_file = st.file_uploader(
            "Envie um CSV com consumo de energia",
            type=["csv"]
        )
        if uploaded_file:
            dataset_path = uploaded_file

# ============================================
# MAIN CONTENT
# ============================================

if dataset_path:
    # Carrega o dataset
    if isinstance(dataset_path, str):
        df = pd.read_csv(dataset_path)
    else:
        df = pd.read_csv(dataset_path)

    # Inicializa o analisador
    analyzer = ConsumptionAnalyzer(dataset_path if isinstance(dataset_path, str) else dataset_path.name)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat com IA", "📈 Análise Rápida", "📊 Dados"])

    # ============================================
    # TAB 1: CHAT COM IA
    # ============================================

    with tab1:
        st.subheader("Faça suas perguntas sobre consumo de energia")

        # Exemplos de perguntas
        with st.expander("💡 Exemplos de perguntas"):
            st.markdown("""
            - Qual é o consumo médio da geladeira?
            - Qual equipamento consome mais energia?
            - Qual equipamento consome menos?
            - Qual é o período do dia com maior consumo?
            - Qual é o consumo total?
            - Como varia o consumo do ar condicionado?
            """)

        # Input de pergunta
        question = st.text_area(
            "Sua pergunta:",
            placeholder="Ex: Qual equipamento consome mais energia?",
            height=100
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            if st.button("🔍 Buscar Resposta", use_container_width=True):
                if question.strip():
                    with st.spinner("⏳ Processando com IA..."):
                        try:
                            answer = run_agent(question, analyzer, model)

                            # Exibe resposta
                            st.success("✅ Resposta recebida")
                            st.info(answer)

                            # Histórico
                            if "chat_history" not in st.session_state:
                                st.session_state.chat_history = []

                            st.session_state.chat_history.append({
                                "pergunta": question,
                                "resposta": answer
                            })

                        except Exception as e:
                            st.error(f"❌ Erro: {str(e)}")
                            st.warning("💡 Dica: Certifique-se de que o Ollama está rodando localmente\n`ollama serve`")
                else:
                    st.warning("⚠️ Digite uma pergunta!")

        # Histórico de conversas
        if "chat_history" in st.session_state and st.session_state.chat_history:
            with st.expander("📝 Histórico"):
                for i, item in enumerate(st.session_state.chat_history[-5:], 1):
                    st.write(f"**{i}. Pergunta:** {item['pergunta']}")
                    st.write(f"**Resposta:** {item['resposta']}")
                    st.divider()

    # ============================================
    # TAB 2: ANÁLISE RÁPIDA
    # ============================================

    with tab2:
        st.subheader("Análises Rápidas")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Maior Consumo"):
                result = analyzer.get_max_consumption_appliance()
                st.json(result)

        with col2:
            if st.button("📉 Menor Consumo"):
                result = analyzer.get_min_consumption_appliance()
                st.json(result)

        with col3:
            if st.button("⏰ Pico do Dia"):
                result = analyzer.get_peak_consumption_period()
                st.json(result)

        st.divider()

        # Consumo por equipamento
        st.subheader("🔌 Consumo por Equipamento")

        col1, col2 = st.columns([2, 1])

        with col1:
            if 'appliance' in df.columns:
                appliances = df['appliance'].unique()
                selected_appliance = st.selectbox("Selecione um equipamento:", appliances)

                if st.button("Analisar"):
                    result = analyzer.get_average_consumption(selected_appliance)
                    st.metric(
                        f"Consumo médio - {selected_appliance}",
                        f"{result.get('average_consumption', 'N/A')} kWh"
                    )

    # ============================================
    # TAB 3: DADOS BRUTOS
    # ============================================

    with tab3:
        st.subheader("📊 Prévia dos Dados")

        st.dataframe(df.head(20), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de registros", len(df))
        with col2:
            st.metric("Colunas", len(df.columns))

        st.subheader("Informações do Dataset")
        st.write(df.info())

else:
    st.warning("⚠️ Selecione um dataset para começar")
    st.info("👈 Use a barra lateral para configurar o dataset")
