"""
ChargeGrid Intelligence - Analise dos dados das sessoes de recarga.

Le data/dados_sessoes.csv (saida CSV do monitor serial do protótipo no Wokwi),
imprime estatisticas e salva os graficos em docs/.

Uso (a partir da raiz do repositorio):
    pip install pandas matplotlib
    python analysis/analise_sessoes.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # salva PNG sem precisar abrir janela
import matplotlib.pyplot as plt
import pandas as pd

# ----------------------------------------------------------
# Caminhos e parametros (iguais aos do firmware)
# ----------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "data" / "dados_sessoes.csv"
SAIDA = RAIZ / "docs"
SAIDA.mkdir(exist_ok=True)

ENERGIA_MINIMA_KW = 3.0     # ENERGIA_MINIMA no firmware
POTENCIA_RECARGA_KW = 3.3   # POTENCIA_RECARGA no firmware

TEMPERATURA_MAXIMA_C = 40.0  # TEMPERATURA_MAXIMA no firmware

# uma cor por resultado (mesma ordem em todos os graficos)
CORES_RESULTADO = {
    "RECARGA NORMAL": "#2a78d6",    # azul
    "ENERGIA BAIXA": "#eb6834",     # laranja
    "TEMPERATURA ALTA": "#1baf7a",  # verde-agua
}
NOMES_RESULTADO = {
    "RECARGA NORMAL": "Recarga normal",
    "ENERGIA BAIXA": "Bloqueada: energia baixa",
    "TEMPERATURA ALTA": "Bloqueada: temperatura alta",
}
TEXTO = "#0b0b0b"
TEXTO_SEC = "#52514e"
GRADE = "#e3e2dd"

# ----------------------------------------------------------
# Leitura dos dados
# ----------------------------------------------------------
df = pd.read_csv(CSV)

# Tempo de recarga estimado a partir da energia (E = P * t  ->  t = E / P)
df["Tempo_recarga_est_s"] = df["Energia_utilizada_kWh"] * 3600 / POTENCIA_RECARGA_KW
df["Recarga_sobre_duracao"] = df["Tempo_recarga_est_s"] / df["Duracao_s"]

print("===== DADOS DAS SESSOES =====")
print(df.round(4).to_string(index=False))

# ----------------------------------------------------------
# Estatisticas
# ----------------------------------------------------------
normais = df[df["Resultado"] == "RECARGA NORMAL"]

print("\n===== ESTATISTICAS =====")
print(f"Sessoes registradas:       {len(df)}")
print(f"Duracao media:             {df['Duracao_s'].mean():.2f} s")
print(f"Temperatura media:         {df['Temperatura_C'].mean():.1f} C")
print(f"Energia solar media:       {df['Energia_solar_kW'].mean():.2f} kW")
print(f"Energia utilizada total:   {df['Energia_utilizada_kWh'].sum():.4f} kWh")
print(f"Energia media (normais):   {normais['Energia_utilizada_kWh'].mean():.4f} kWh")

maior_dur = df.loc[df["Duracao_s"].idxmax()]
maior_en = df.loc[df["Energia_utilizada_kWh"].idxmax()]
print(f"Maior duracao:             sessao {int(maior_dur['Sessao'])} ({maior_dur['Duracao_s']:.1f} s)")
print(f"Maior energia utilizada:   sessao {int(maior_en['Sessao'])} ({maior_en['Energia_utilizada_kWh']:.4f} kWh)")

print("\n===== RESULTADOS DAS SESSOES =====")
print(df["Resultado"].value_counts().to_string())
bloqueadas = (df["Resultado"] != "RECARGA NORMAL").sum()
print(f"Sessoes bloqueadas pela automacao: {bloqueadas} de {len(df)} ({bloqueadas / len(df):.0%})")

print("\n===== TEMPO DE RECARGA x DURACAO (sessoes com recarga) =====")
print(normais[["Sessao", "Duracao_s", "Tempo_recarga_est_s", "Recarga_sobre_duracao"]]
      .round(2).to_string(index=False))


# ----------------------------------------------------------
# Graficos
# ----------------------------------------------------------
def cores(resultados):
    return [CORES_RESULTADO[r] for r in resultados]


def grafico_barras(coluna, titulo, rotulo_y, arquivo, casas, linha_ref=None):
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=150)
    barras = ax.bar(df["Sessao"], df[coluna], width=0.5, color=cores(df["Resultado"]))

    # valor em cima de cada barra (poucas barras: rotulo em todas e legivel)
    for barra, valor in zip(barras, df[coluna]):
        ax.text(barra.get_x() + barra.get_width() / 2, valor,
                f"{valor:.{casas}f}", ha="center", va="bottom",
                fontsize=9, color=TEXTO)

    if linha_ref is not None:
        ax.axhline(linha_ref[0], color=TEXTO_SEC, linestyle="--", linewidth=1.2)
        # rotulo em uma sessao com barra baixa, onde ha espaco livre acima da linha
        ax.text(linha_ref[2], linha_ref[0] + df[coluna].max() * 0.015, linha_ref[1],
                ha="center", va="bottom", fontsize=9, color=TEXTO_SEC)

    ax.set_xticks(df["Sessao"])
    ax.set_xlabel("Sessão", color=TEXTO_SEC)
    ax.set_ylabel(rotulo_y, color=TEXTO_SEC)
    ax.set_title(titulo, color=TEXTO, loc="left", fontsize=12, fontweight="bold")
    ax.set_ylim(0, df[coluna].max() * 1.18)
    ax.yaxis.grid(True, color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(colors=TEXTO_SEC, length=0)

    # legenda so com os resultados que existem nos dados
    legenda = [
        plt.Rectangle((0, 0), 1, 1, color=cor, label=NOMES_RESULTADO[res])
        for res, cor in CORES_RESULTADO.items() if res in set(df["Resultado"])
    ]
    ax.legend(handles=legenda, frameon=False, loc="upper left",
              bbox_to_anchor=(0, -0.16), ncol=3, fontsize=9, labelcolor=TEXTO_SEC)

    fig.tight_layout()
    fig.savefig(SAIDA / arquivo, facecolor="white")
    plt.close(fig)
    print(f"Grafico salvo: docs/{arquivo}")


print("\n===== GRAFICOS =====")
grafico_barras("Energia_solar_kW", "Energia solar disponível por sessão",
               "Energia solar (kW)", "grafico_energia_solar.png", 1,
               linha_ref=(ENERGIA_MINIMA_KW, "mínimo para recarregar: 3,0 kW", 3))
grafico_barras("Temperatura_C", "Temperatura por sessão",
               "Temperatura (°C)", "grafico_temperatura.png", 1,
               linha_ref=(TEMPERATURA_MAXIMA_C, "limite de segurança: 40 °C", 2))
grafico_barras("Energia_utilizada_kWh", "Energia utilizada por sessão",
               "Energia utilizada (kWh)", "grafico_energia_utilizada.png", 4)
grafico_barras("Duracao_s", "Duração das sessões",
               "Duração (s)", "grafico_duracao.png", 1)
