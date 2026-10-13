# Simulador de Filtros Elétricos – Sistemas Fotovoltaicos

Aplicação desktop em Python (Tkinter) para simular e visualizar o efeito de filtros digitais sobre um sinal de tensão típico de um sistema fotovoltaico (PV). O programa gera um sinal sintético com ondulação da rede e chaveamento PWM do inversor, adiciona ruído branco, aplica um filtro Butterworth configurável e mostra os resultados no domínio do tempo e da frequência (FFT).

## Funcionalidades

- Geração de um sinal PV simulado com ruído gaussiano de nível ajustável
- Quatro tipos de filtro Butterworth: **passa-baixa**, **passa-alta**, **passa-faixa** e **rejeita-faixa**
- Ordem do filtro, frequências de corte e frequência de amostragem configuráveis
- Filtragem de **fase zero** (`sosfiltfilt`), sem atraso de fase no sinal filtrado
- Filtros implementados em seções de segunda ordem (SOS), numericamente estáveis
- Painel com 4 gráficos: sinal original + ruído, sinal filtrado, FFT do original e FFT do filtrado
- Espectros unilaterais com amplitude real (em volts) e eixo vertical em escala logarítmica
- Validação das entradas com mensagens de erro e aviso

## Modelo do sinal

O sinal simulado é composto por:

| Componente | Frequência | Amplitude |
|---|---|---|
| Nível DC do arranjo PV | 0 Hz | 200 V |
| Ondulação da rede | 60 Hz | 2 V |
| Chaveamento PWM do inversor | 2000 Hz | 1,5 V |
| Ruído branco gaussiano | banda larga | σ ajustável (padrão 0,5 V) |

A duração da simulação é de 0,1 s. Essas constantes ficam no início do código (`V_DC`, `F_REDE`, `V_REDE`, `F_PWM`, `V_PWM`, `DURACAO`) e podem ser alteradas livremente.

## Requisitos

- Python 3.8 ou superior
- [NumPy](https://numpy.org/)
- [SciPy](https://scipy.org/)
- [Matplotlib](https://matplotlib.org/)
- Tkinter (já incluído na instalação padrão do Python em Windows e macOS)

Instalação das dependências:

```bash
pip install numpy scipy matplotlib
```

No Linux (Debian/Ubuntu), caso o Tkinter não esteja instalado:

```bash
sudo apt install python3-tk
```

## Como executar

```bash
python simulador_filtros_pv.py
```

> Substitua `simulador_filtros_pv.py` pelo nome real do arquivo.

## Como usar

1. Defina a **frequência de amostragem**, o **nível de ruído** e clique em **Gerar Sinal**.
2. Escolha o **tipo de filtro**, a **ordem** e a(s) **frequência(s) de corte**.
3. Clique em **Filtrar** para ver o resultado.
4. Use **Limpar** para zerar os dados e os gráficos.

### Parâmetros da interface

| Campo | Descrição | Padrão |
|---|---|---|
| Tipo de Filtro | Passa-Baixa, Passa-Alta, Passa-Faixa ou Rejeita-Faixa | Passa-Baixa |
| Freq. Amostragem (Hz) | Taxa de amostragem do sinal gerado | 4001 |
| Ordem do Filtro | Ordem do filtro Butterworth (inteiro ≥ 1) | 4 |
| Freq. Corte / Inferior (Hz) | Frequência de corte (ou limite inferior da faixa) | 100 |
| Freq. Superior (Hz) | Limite superior da faixa (habilitado só em passa-faixa e rejeita-faixa) | 1000 |
| Nível de Ruído (V) | Desvio padrão do ruído branco | 0,5 |

### Exemplos de uso

- **Remover o PWM de 2 kHz:** passa-baixa com corte em 100 Hz e ordem 4. Preserva o nível DC e a ondulação de 60 Hz.
- **Isolar a ondulação da rede:** passa-faixa com limites de 40 a 80 Hz.
- **Eliminar o nível DC e a rede:** passa-alta com corte em 500 Hz, mantendo apenas o PWM e o ruído.
- **Suprimir a ondulação de 60 Hz:** rejeita-faixa de 50 a 70 Hz.

## Validações e restrições

- A frequência de amostragem deve ser maior que **2 × 2000 Hz = 4000 Hz** (critério de Nyquist para o PWM); caso contrário, o programa recusa a geração do sinal.
- O nível de ruído não pode ser negativo.
- As frequências de corte devem estar entre 0 e a frequência de Nyquist (`fs / 2`). Para filtros de faixa, é necessário `0 < f_inferior < f_superior < Nyquist`.
- Se a frequência de amostragem for alterada depois de gerado o sinal, é preciso gerar o sinal novamente antes de filtrar, para manter o filtro consistente com os dados.
- É necessário gerar o sinal antes de aplicar o filtro.

## Detalhes de implementação

- **Filtro:** `scipy.signal.butter(..., output="sos")` para projeto e `scipy.signal.sosfiltfilt` para aplicação. A filtragem direta e reversa dobra a ordem efetiva e elimina a distorção de fase.
- **Espectro:** a função `_espectro_unilateral` usa `numpy.fft.rfft`, normaliza por `N` e dobra as componentes (exceto DC e Nyquist), de modo que as amplitudes lidas no gráfico correspondem às amplitudes reais em volts.
- **Escala logarítmica:** os espectros usam eixo Y logarítmico (limites de 10⁻⁴ a 10²), pois a componente DC de 200 V esconderia as demais em escala linear.
- **Gráficos:** usa `matplotlib.figure.Figure` diretamente (sem `pyplot`), embutido na janela Tkinter via `FigureCanvasTkAgg`.

## Observações

- Com a frequência padrão de 4001 Hz, o PWM de 2000 Hz fica muito próximo da frequência de Nyquist. Para uma visualização mais fiel dessa componente no espectro, use uma frequência de amostragem maior, como 20000 Hz.
- O ruído é gerado com `numpy.random.normal` sem semente fixa, portanto cada geração produz um resultado ligeiramente diferente.

## Estrutura do código

```
SimuladorFiltrosPV
├── _criar_interface()             # Monta controles e área de gráficos
├── _atualizar_estado_campos()     # Habilita/desabilita a freq. superior conforme o filtro
├── _configurar_graficos_vazios()  # Títulos, rótulos, grade e escalas
├── _espectro_unilateral()         # FFT unilateral com amplitudes reais
├── gerar_sinal()                  # Gera o sinal PV com ruído
├── aplicar_filtro()               # Projeta e aplica o filtro Butterworth
├── plotar_resultados()            # Atualiza os 4 gráficos
└── limpar()                       # Reinicia o estado
```

## Licença

Defina aqui a licença do projeto (por exemplo, MIT).
