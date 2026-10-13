import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy import signal
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Componentes do sinal simulado
V_DC = 200.0        # Componente DC (V)
F_REDE = 60.0      # Ondulação da rede (Hz)
V_REDE = 2.0       # Amplitude da ondulação (V)
F_PWM = 2000.0     # Chaveamento PWM do inversor (Hz)
V_PWM = 1.5        # Amplitude do PWM (V)
DURACAO = 0.1      # Duração da simulação (s)


class SimuladorFiltrosPV:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Filtros Elétricos - Sistemas Fotovoltaicos")
        self.root.geometry("1100x800")

        # Variáveis de estado
        self.t = None
        self.sinal_puro = None
        self.sinal_com_ruido = None
        self.sinal_filtrado = None
        self.fs = 4001.0  # Frequência de amostragem usada no último sinal gerado (Hz)

        self._criar_interface()

    def _criar_interface(self):
        frame_controles = ttk.LabelFrame(self.root, text=" Configurações e Parâmetros ", padding=10)
        frame_controles.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Linha 1: tipo de filtro, amostragem e ordem
        ttk.Label(frame_controles, text="Tipo de Filtro:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cb_filtro = ttk.Combobox(frame_controles, values=[
            "Passa-Baixa", "Passa-Alta", "Passa-Faixa", "Rejeita-Faixa"
        ], state="readonly", width=15)
        self.cb_filtro.set("Passa-Baixa")
        self.cb_filtro.grid(row=0, column=1, padx=5, pady=5)
        self.cb_filtro.bind("<<ComboboxSelected>>", self._atualizar_estado_campos)

        ttk.Label(frame_controles, text="Freq. Amostragem (Hz):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.ent_fs = ttk.Entry(frame_controles, width=10)
        self.ent_fs.insert(0, "4001")
        self.ent_fs.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_controles, text="Ordem do Filtro:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.ent_ordem = ttk.Entry(frame_controles, width=10)
        self.ent_ordem.insert(0, "4")
        self.ent_ordem.grid(row=0, column=5, padx=5, pady=5)

        # Linha 2: frequências de corte e ruído
        self.lbl_f_min = ttk.Label(frame_controles, text="Freq. Corte (Hz):")
        self.lbl_f_min.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.ent_f_min = ttk.Entry(frame_controles, width=10)
        self.ent_f_min.insert(0, "100")
        self.ent_f_min.grid(row=1, column=1, padx=5, pady=5)

        self.lbl_f_max = ttk.Label(frame_controles, text="Freq. Superior (Hz):")
        self.lbl_f_max.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.ent_f_max = ttk.Entry(frame_controles, width=10)
        self.ent_f_max.insert(0, "1000")
        self.ent_f_max.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(frame_controles, text="Nível de Ruído (V):").grid(row=1, column=4, sticky=tk.W, padx=5, pady=5)
        self.ent_ruido = ttk.Entry(frame_controles, width=10)
        self.ent_ruido.insert(0, "0.5")
        self.ent_ruido.grid(row=1, column=5, padx=5, pady=5)

        # Linha 3: botões
        frame_botoes = ttk.Frame(frame_controles)
        frame_botoes.grid(row=2, column=0, columnspan=6, pady=10)

        ttk.Button(frame_botoes, text="Gerar Sinal", command=self.gerar_sinal).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_botoes, text="Filtrar", command=self.aplicar_filtro).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_botoes, text="Limpar", command=self.limpar).pack(side=tk.LEFT, padx=10)

        # Gráficos: Figure direta (sem pyplot) para não registrar a figura no gerenciador global
        self.fig = Figure(figsize=(10, 6))
        self.axs = self.fig.subplots(2, 2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self._atualizar_estado_campos()
        self._configurar_graficos_vazios()

    def _atualizar_estado_campos(self, event=None):
        tipo = self.cb_filtro.get()
        if tipo in ("Passa-Faixa", "Rejeita-Faixa"):
            self.lbl_f_min.config(text="Freq. Inferior (Hz):")
            self.lbl_f_max.config(text="Freq. Superior (Hz):")
            self.ent_f_max.config(state="normal")
        else:
            self.lbl_f_min.config(text="Freq. Corte (Hz):")
            self.lbl_f_max.config(text="Freq. Superior (Hz):")
            self.ent_f_max.config(state="disabled")

    def _configurar_graficos_vazios(self):
        titles = [
            "Sinal Original + Ruído (Tempo)", "Sinal Filtrado (Tempo)",
            "Espectro FFT (Sinal Original)", "Espectro FFT (Sinal Filtrado)"
        ]
        x_labels = ["Tempo [s]", "Tempo [s]", "Frequência [Hz]", "Frequência [Hz]"]
        y_labels = ["Tensão [V]", "Tensão [V]", "Amplitude [V]", "Amplitude [V]"]

        for idx, ax in enumerate(self.axs.flat):
            ax.clear()  # clear() volta a escala para linear, então a escala log é definida depois
            ax.set_title(titles[idx], fontsize=10, fontweight="bold")
            ax.set_xlabel(x_labels[idx], fontsize=8)
            ax.set_ylabel(y_labels[idx], fontsize=8)
            ax.grid(True, linestyle="--", alpha=0.6)

            # Espectros em escala log: a componente DC (200 V) esconderia o resto em escala linear
            if idx >= 2:
                ax.set_yscale("log")
                ax.set_ylim(1e-4, 100)

        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()

    @staticmethod
    def _espectro_unilateral(x, fs):
        """Retorna frequências e amplitudes reais (unilateral) de cada componente."""
        n = len(x)
        freqs = np.fft.rfftfreq(n, d=1.0 / fs)
        mag = np.abs(np.fft.rfft(x)) / n
        mag[1:] *= 2.0          # dobra tudo, exceto DC
        if n % 2 == 0:
            mag[-1] /= 2.0      # componente de Nyquist também não é dobrada
        return freqs, mag

    def gerar_sinal(self):
        try:
            fs = float(self.ent_fs.get())
            nivel_ruido = float(self.ent_ruido.get())
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Insira valores numéricos válidos nos parâmetros.")
            return

        if fs <= 2 * F_PWM:
            messagebox.showerror(
                "Erro de Amostragem",
                f"A frequência de amostragem deve ser maior que {2 * F_PWM:.0f} Hz "
                f"(o PWM de {F_PWM:.0f} Hz sofreria aliasing)."
            )
            return
        if nivel_ruido < 0:
            messagebox.showerror("Erro de Entrada", "O nível de ruído não pode ser negativo.")
            return

        self.fs = fs
        n_amostras = int(self.fs * DURACAO)
        self.t = np.linspace(0, DURACAO, n_amostras, endpoint=False)

        # Sinal PV: DC + ondulação da rede (60 Hz) + chaveamento PWM do inversor (2000 Hz)
        v_rede = V_REDE * np.sin(2 * np.pi * F_REDE * self.t)
        v_pwm = V_PWM * np.sin(2 * np.pi * F_PWM * self.t)

        self.sinal_puro = V_DC + v_rede + v_pwm
        ruido_branco = np.random.normal(0, nivel_ruido, n_amostras)
        self.sinal_com_ruido = self.sinal_puro + ruido_branco

        self.sinal_filtrado = None
        self.plotar_resultados()

    def aplicar_filtro(self):
        if self.sinal_com_ruido is None:
            messagebox.showwarning("Aviso", "Gere o sinal de entrada antes de aplicar o filtro.")
            return

        tipo = self.cb_filtro.get()

        try:
            fs_atual = float(self.ent_fs.get())
            ordem = int(self.ent_ordem.get())
            f_min = float(self.ent_f_min.get())
            f_max = float(self.ent_f_max.get()) if tipo in ("Passa-Faixa", "Rejeita-Faixa") else None
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Insira valores numéricos válidos (ordem deve ser inteira).")
            return

        # O sinal foi gerado com self.fs; se o campo mudou, o filtro ficaria inconsistente
        if not np.isclose(fs_atual, self.fs):
            messagebox.showwarning(
                "Aviso",
                f"A frequência de amostragem foi alterada (sinal gerado com {self.fs:g} Hz). "
                "Gere o sinal novamente antes de filtrar."
            )
            return

        if ordem < 1:
            messagebox.showerror("Erro", "A ordem do filtro deve ser maior ou igual a 1.")
            return

        nyquist = 0.5 * self.fs

        if f_min <= 0 or f_min >= nyquist:
            messagebox.showerror("Erro", f"A frequência de corte deve estar entre 0 e Nyquist ({nyquist:g} Hz).")
            return

        try:
            if tipo == "Passa-Baixa":
                sos = signal.butter(ordem, f_min / nyquist, btype="low", output="sos")
            elif tipo == "Passa-Alta":
                sos = signal.butter(ordem, f_min / nyquist, btype="high", output="sos")
            else:
                if f_max <= f_min or f_max >= nyquist:
                    messagebox.showerror("Erro", "Verifique as frequências: 0 < f_inferior < f_superior < Nyquist.")
                    return
                btype = "bandpass" if tipo == "Passa-Faixa" else "bandstop"
                sos = signal.butter(ordem, [f_min / nyquist, f_max / nyquist], btype=btype, output="sos")

            # SOS é numericamente estável; sosfiltfilt aplica o filtro com fase zero
            self.sinal_filtrado = signal.sosfiltfilt(sos, self.sinal_com_ruido)
            self.plotar_resultados()

        except Exception as e:
            messagebox.showerror("Erro na Filtragem", str(e))

    def plotar_resultados(self):
        self._configurar_graficos_vazios()

        if self.sinal_com_ruido is not None:
            self.axs[0, 0].plot(self.t, self.sinal_com_ruido, color="tab:red", label="Sinal Bruto + Ruído")
            self.axs[0, 0].plot(self.t, self.sinal_puro, color="black", linestyle=":", label="Sinal Sem Ruído", alpha=0.7)
            self.axs[0, 0].legend(loc="upper right", fontsize=7)

            freqs, fft_orig = self._espectro_unilateral(self.sinal_com_ruido, self.fs)
            self.axs[1, 0].plot(freqs, fft_orig, color="tab:red", label="FFT Bruto")
            self.axs[1, 0].set_xlim(0, self.fs / 2)
            self.axs[1, 0].legend(loc="upper right", fontsize=7)

        if self.sinal_filtrado is not None:
            self.axs[0, 1].plot(self.t, self.sinal_filtrado, color="tab:green", label="Sinal Filtrado")
            self.axs[0, 1].legend(loc="upper right", fontsize=7)

            freqs, fft_filt = self._espectro_unilateral(self.sinal_filtrado, self.fs)
            self.axs[1, 1].plot(freqs, fft_filt, color="tab:green", label="FFT Filtrado")
            self.axs[1, 1].set_xlim(0, self.fs / 2)
            self.axs[1, 1].legend(loc="upper right", fontsize=7)

        self.canvas.draw()

    def limpar(self):
        self.t = None
        self.sinal_puro = None
        self.sinal_com_ruido = None
        self.sinal_filtrado = None
        self._configurar_graficos_vazios()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorFiltrosPV(root)
    root.mainloop()