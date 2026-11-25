"""
Agente de IA para Análise de Consumo de Energia
Integração com Ollama (local)
"""

import json
import pandas as pd
from pathlib import Path
import ollama

# ============================================
# FERRAMENTAS (Tools) - 5+ funções
# ============================================

class ConsumptionAnalyzer:
    def __init__(self, csv_path: str):
        """Carrega dataset de consumo"""
        self.df = pd.read_csv(csv_path)
        self._prepare_data()

    def _prepare_data(self):
        """Prepara dados para análise"""
        # Ajustar conforme estrutura do seu CSV
        if 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        if 'DateTime' in self.df.columns:
            self.df['DateTime'] = pd.to_datetime(self.df['DateTime'])

    def get_average_consumption(self, appliance: str) -> dict:
        """Tool 1: Consumo médio de um equipamento"""
        try:
            avg = self.df[self.df['appliance'].str.lower() == appliance.lower()]['consumption'].mean()
            return {
                "appliance": appliance,
                "average_consumption": round(avg, 2),
                "unit": "kWh"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_max_consumption_appliance(self) -> dict:
        """Tool 2: Equipamento com maior consumo"""
        try:
            max_app = self.df.groupby('appliance')['consumption'].sum().idxmax()
            max_val = self.df.groupby('appliance')['consumption'].sum().max()
            return {
                "appliance": max_app,
                "total_consumption": round(max_val, 2),
                "unit": "kWh"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_min_consumption_appliance(self) -> dict:
        """Tool 3: Equipamento com menor consumo"""
        try:
            min_app = self.df.groupby('appliance')['consumption'].sum().idxmin()
            min_val = self.df.groupby('appliance')['consumption'].sum().min()
            return {
                "appliance": min_app,
                "total_consumption": round(min_val, 2),
                "unit": "kWh"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_peak_consumption_period(self) -> dict:
        """Tool 4: Período do dia com maior consumo"""
        try:
            if 'hour' not in self.df.columns:
                self.df['hour'] = pd.to_datetime(self.df.get('timestamp') or self.df.get('DateTime')).dt.hour

            peak_hour = self.df.groupby('hour')['consumption'].sum().idxmax()
            peak_val = self.df.groupby('hour')['consumption'].sum().max()
            return {
                "peak_hour": f"{peak_hour:02d}:00",
                "consumption": round(peak_val, 2),
                "unit": "kWh"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_total_consumption(self, appliance: str = None) -> dict:
        """Tool 5: Consumo total (geral ou de um equipamento)"""
        try:
            if appliance:
                total = self.df[self.df['appliance'].str.lower() == appliance.lower()]['consumption'].sum()
                return {"appliance": appliance, "total_consumption": round(total, 2), "unit": "kWh"}
            else:
                total = self.df['consumption'].sum()
                return {"total_consumption": round(total, 2), "unit": "kWh"}
        except Exception as e:
            return {"error": str(e)}

    def analyze_consumption_variation(self, appliance: str) -> dict:
        """Tool 6: Variação de consumo de um equipamento"""
        try:
            app_data = self.df[self.df['appliance'].str.lower() == appliance.lower()]
            std = app_data['consumption'].std()
            mean = app_data['consumption'].mean()
            cv = (std / mean * 100) if mean != 0 else 0
            return {
                "appliance": appliance,
                "std_deviation": round(std, 2),
                "mean": round(mean, 2),
                "coefficient_variation": round(cv, 2)
            }
        except Exception as e:
            return {"error": str(e)}

# ============================================
# TOOLS SCHEMA para Ollama
# ============================================

TOOLS = [
    {
        "name": "get_average_consumption",
        "description": "Retorna o consumo médio de um equipamento específico",
        "parameters": {
            "type": "object",
            "properties": {
                "appliance": {
                    "type": "string",
                    "description": "Nome do equipamento (ex: 'geladeira', 'ar condicionado')"
                }
            },
            "required": ["appliance"]
        }
    },
    {
        "name": "get_max_consumption_appliance",
        "description": "Identifica o equipamento com maior consumo total",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_min_consumption_appliance",
        "description": "Identifica o equipamento com menor consumo total",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_peak_consumption_period",
        "description": "Identifica o período do dia com maior consumo de energia",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_total_consumption",
        "description": "Retorna o consumo total geral ou de um equipamento específico",
        "parameters": {
            "type": "object",
            "properties": {
                "appliance": {
                    "type": "string",
                    "description": "Nome do equipamento (opcional)"
                }
            }
        }
    },
    {
        "name": "analyze_consumption_variation",
        "description": "Analisa como o consumo de um equipamento varia ao longo do tempo",
        "parameters": {
            "type": "object",
            "properties": {
                "appliance": {
                    "type": "string",
                    "description": "Nome do equipamento"
                }
            },
            "required": ["appliance"]
        }
    }
]

# ============================================
# AGENTE IA com Ollama
# ============================================

def run_agent(question: str, analyzer: ConsumptionAnalyzer, model: str = "llama2"):
    """Executa o agente com ferramenta selecionada"""

    messages = [
        {
            "role": "system",
            "content": """Você é um assistente especializado em análise de consumo de energia.

Você tem acesso às seguintes ferramentas:
- get_average_consumption(appliance): consumo médio de um equipamento
- get_max_consumption_appliance(): equipamento com maior consumo
- get_min_consumption_appliance(): equipamento com menor consumo
- get_peak_consumption_period(): período com maior consumo
- get_total_consumption(appliance): consumo total
- analyze_consumption_variation(appliance): variação de consumo

Responda SEMPRE em português. Para cada pergunta, identifique qual ferramenta usar e retorne o resultado.
Nunca invente dados. Use apenas os resultados das ferramentas."""
        },
        {
            "role": "user",
            "content": question
        }
    ]

    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            stream=False
        )
        return response['message']['content']
    except Exception as e:
        return f"Erro ao chamar Ollama: {str(e)}\nCertifique-se de que o Ollama está rodando localmente"

if __name__ == "__main__":
    print("🔌 Agente de Consumo de Energia")
    print("=" * 50)
