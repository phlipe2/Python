"""
Script para gerar dataset de EXEMPLO
Use isso para testar o agente antes do dataset real
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def gerar_dataset_exemplo():
    """Gera dataset fictício de consumo de energia"""

    # Data base
    data_inicio = datetime(2024, 1, 1)

    dados = []

    # Equipamentos e seus padrões de consumo
    equipamentos = {
        'geladeira': {'consumo_base': 0.4, 'variacao': 0.1},
        'ar_condicionado': {'consumo_base': 2.5, 'variacao': 0.8},
        'chuveiro': {'consumo_base': 4.5, 'variacao': 1.2},
        'microondas': {'consumo_base': 1.2, 'variacao': 0.3},
        'tv': {'consumo_base': 0.15, 'variacao': 0.05},
        'iluminacao': {'consumo_base': 0.3, 'variacao': 0.1},
        'maquina_lavar': {'consumo_base': 1.8, 'variacao': 0.5},
    }

    # Gera 7 dias de dados (15 minutos)
    for dia in range(7):
        for hora in range(24):
            for minuto in [0, 15, 30, 45]:
                timestamp = data_inicio + timedelta(days=dia, hours=hora, minutes=minuto)

                for equipamento, params in equipamentos.items():
                    # Variação de consumo por período do dia
                    if 6 <= hora < 12:  # Manhã (maior uso)
                        fator_hora = 1.2
                    elif 12 <= hora < 18:  # Tarde
                        fator_hora = 1.0
                    elif 18 <= hora < 22:  # Noite (pico)
                        fator_hora = 1.5
                    else:  # Madrugada (menor)
                        fator_hora = 0.6

                    # Consumo com variação
                    consumo = params['consumo_base'] * fator_hora
                    consumo += np.random.normal(0, params['variacao'])
                    consumo = max(0, consumo)  # Não negativo

                    dados.append({
                        'timestamp': timestamp,
                        'appliance': equipamento,
                        'consumption': round(consumo, 3),
                        'hour': hora
                    })

    # Cria DataFrame
    df = pd.DataFrame(dados)

    # Salva (funciona em Windows/Linux/Mac)
    output_path = 'CLEAN_House5_EXEMPLO.csv'
    df.to_csv(output_path, index=False)

    print(f"✅ Dataset gerado: {output_path}")
    print(f"📊 Total de registros: {len(df)}")
    print(f"📋 Equipamentos: {df['appliance'].unique()}")
    print(f"\n📌 Primeiras linhas:")
    print(df.head(10))

    return df

if __name__ == "__main__":
    gerar_dataset_exemplo()
