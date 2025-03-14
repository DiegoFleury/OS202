import os
import pandas as pd
import matplotlib.pyplot as plt
import glob

# Procurar por arquivos no formato "timing_results_X_threads.csv"
csv_files = glob.glob("timing_results_*_threads.csv")

if not csv_files:
    print("Nenhum arquivo de resultado encontrado!")
    exit()

# Criar a figura
plt.figure(figsize=(10, 6))

# Cores diferentes para cada categoria
colors = {
    "T_avancement": "blue",
    "T_affichage": "red",
    "T_total": "black"
}

# Iterar sobre cada arquivo encontrado
for file in csv_files:
    # Extrair número de threads do nome do arquivo
    num_threads = file.split("_")[-2]  # Pega o número antes de "threads.csv"
    
    # Ler o arquivo CSV
    df = pd.read_csv(file)

    # Plotar as curvas para cada tipo de tempo
    plt.plot(df["TimeStep"], df["T_avancement"], linestyle='dashed', color=colors["T_avancement"], alpha=0.7, label=f"T_avancement ({num_threads} threads)")
    plt.plot(df["TimeStep"], df["T_affichage"], linestyle='dotted', color=colors["T_affichage"], alpha=0.7, label=f"T_affichage ({num_threads} threads)")
    plt.plot(df["TimeStep"], df["T_total"], linestyle='solid', color=colors["T_total"], alpha=0.7, label=f"T_total ({num_threads} threads)")

# Configurar o gráfico
plt.xlabel("Passo de Tempo (TimeStep)")
plt.ylabel("Tempo (segundos)")
plt.title("Comparação dos Tempos de Execução por Número de Threads")
plt.legend()
plt.grid(True)

# Salvar a figura
plt.savefig("timing_curves_comparison.png")

# Exibir o gráfico
plt.show()
