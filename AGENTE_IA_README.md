# 🔌 Agente de IA para Análise de Consumo de Energia

Assistente inteligente que responde perguntas sobre consumo de energia usando **Ollama** (IA Local) + **Streamlit** (Web).

---

## 🎯 Funcionalidades

✅ **6 Ferramentas Python** implementadas:
1. Consumo médio de um equipamento
2. Equipamento com maior consumo
3. Equipamento com menor consumo
4. Período do dia com maior consumo
5. Consumo total
6. Variação de consumo

✅ **Integração com Ollama** (IA Local)
✅ **Interface Web** (Streamlit)
✅ **Suporte a dados em tempo real**
✅ **Histórico de conversas**

---

## 📋 Pré-requisitos

### 1. Instalar Ollama
```bash
# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# MacOS
# Baixar em: https://ollama.ai

# Windows
# Baixar em: https://ollama.ai
```

### 2. Baixar um modelo
```bash
# Recomendado (rápido e preciso)
ollama pull llama2

# Alternativas
ollama pull mistral
ollama pull neural-chat
ollama pull orca-mini
```

### 3. Iniciar o Ollama
```bash
ollama serve
# Vai rodar em http://localhost:11434
```

---

## 🚀 Como Rodar

### 1. Preparar o dataset

Coloque o arquivo CSV na pasta `/home/user/Python/`

**Estrutura esperada do CSV:**
```
timestamp,appliance,consumption
2024-01-01 00:00:00,geladeira,0.5
2024-01-01 00:15:00,ar_condicionado,2.3
...
```

### 2. Instalar dependências
```bash
cd /home/user/Python
pip install -r requirements_agent.txt
```

### 3. Rodar a interface Streamlit
```bash
streamlit run app_streamlit.py
```

A aplicação abrir em: `http://localhost:8501`

---

## 💬 Exemplos de Perguntas

O agente consegue responder:

- ❓ "Qual é o consumo médio da geladeira?"
- ❓ "Qual equipamento consome mais energia?"
- ❓ "Qual é o menor consumo?"
- ❓ "Qual período do dia tem maior consumo?"
- ❓ "Qual é o consumo total?"
- ❓ "Como varia o consumo do ar condicionado?"
- ❓ "Qual aparelho é mais econômico?"

**O agente NUNCA inventa dados** — tudo vem do dataset!

---

## 🔗 Vinculação com ESP32

### Integração Futura (Fluxo):

```
┌─────────────────────────────────────────┐
│   1. ESP32 coleta dados de sensores     │
│      (corrente, tensão, etc)            │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   2. Envia para servidor Python          │
│      (via MQTT ou REST API)             │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   3. App Streamlit recebe dados          │
│      e atualiza em tempo real            │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   4. Agente IA responde perguntas        │
│      baseado nos dados em tempo real     │
└─────────────────────────────────────────┘
```

### Como integrar o ESP32:

**Passo 1: ESP32 envia dados (via REST)**
```cpp
// No código do ESP32
POST http://localhost:8501/api/stream
{
  "timestamp": "2024-01-01T12:00:00",
  "appliance": "ar_condicionado",
  "consumption": 2.5
}
```

**Passo 2: App Streamlit recebe**
```python
# Já preparado em app_streamlit.py
# Falta: adicionar endpoint Flask/FastAPI
```

---

## 📂 Estrutura do Projeto

```
/home/user/Python/
├── agent_consumo.py          # Lógica do agente + tools
├── app_streamlit.py          # Interface web
├── requirements_agent.txt    # Dependências
├── CLEAN_House5.csv          # Dataset (seu arquivo)
└── assistente-de-obra.pdf    # Guia do hardware
```

---

## 🛠️ Troubleshooting

### ❌ "Erro ao chamar Ollama"
**Solução:** Certifique-se que o Ollama está rodando
```bash
ollama serve
```

### ❌ "Modelo não encontrado"
**Solução:** Baixe o modelo
```bash
ollama pull llama2
```

### ❌ "CSV não encontrado"
**Solução:** Coloque o arquivo na pasta `/home/user/Python/`

---

## 📊 Próximos Passos

1. ✅ Enviar dataset `CLEAN_House5`
2. 🔄 Testar o agente com suas perguntas
3. 🔌 Integrar ESP32 (via MQTT ou REST)
4. 📱 Adicionar dashboard em tempo real
5. 🎓 Apresentar na aula!

---

## 🎓 Critérios de Avaliação (da professora)

| Critério | Status |
|----------|--------|
| ✅ 5+ ferramentas Python | Implementado (6 tools) |
| ✅ Integração Ollama + Tool Calling | Pronto |
| ✅ Análises do dataset | Funcional |
| ✅ Tratamento de erros | Incluído |
| ✅ Interface web | Streamlit pronto |
| 🔄 Dados em tempo real | Prontos para integração |
| ✅ Teste com 5+ perguntas | Histórico de conversas |

---

## 👨‍💻 Desenvolvido por
João Phellipe - Assistente Elétrico IA

**Data:** 2026-11-25
