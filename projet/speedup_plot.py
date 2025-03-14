import pandas as pd
import matplotlib.pyplot as plt
import glob
import re

def compute_speedup():
    # Buscar arquivos timing_results_NUMERO.csv
    files = glob.glob("timing_results_*.csv")

    # Dicionário para armazenar os tempos totais de T_avancement
    timing_data = {}

    for file in files:
        # Extrair número de threads do nome do arquivo
        match = re.search(r"timing_results_(\d+).csv", file)
        if match:
            num_threads = int(match.group(1))
            
            # Carregar o CSV
            df = pd.read_csv(file)
            
            # Verificar se a coluna necessária existe
            if 'T_avancement' not in df.columns:
                raise ValueError(f"Le fichier {file} ne contient pas la colonne T_avancement.")
            
            # Calcular o tempo total como a soma de T_avancement
            total_time = df['T_avancement'].sum()
            timing_data[num_threads] = total_time

    # Ordenar por número de threads
    timing_data = dict(sorted(timing_data.items()))

    # Separar os valores para plotagem
    threads = list(timing_data.keys())
    times = list(timing_data.values())

    # Definir T1 (tempo total com 1 thread)
    T1 = times[0]  # O primeiro valor (threads=1)

    # Calcular speedup
    speedups = [T1 / T for T in times]

    # Plotar gráfico de speedup
    plt.figure(figsize=(10, 5))
    plt.plot(threads, speedups, marker='o', linestyle='-', label="Speedup réel")
    plt.plot(threads, threads, linestyle="dashed", color="gray", label="Speedup idéal (N_threads)")

    plt.xlabel("Nombre de threads")
    plt.ylabel("Speedup")
    plt.title("Speedup en fonction du nombre de threads")
    plt.legend()
    plt.grid(True)

    # Salvar e exibir gráfico
    plt.savefig("speedup_plot.png")
    plt.show()

    print("Données de speedup enregistrées dans 'speedup_plot.png'.")

# Executar análise de speedup
compute_speedup()
