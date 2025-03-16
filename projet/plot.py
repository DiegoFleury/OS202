import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob

# Répertoires
BASE_DIR = "tests"

# Tracer les graphiques pour Amdahl
amdahl_dir = "amdahl_500"  # Nom exact du dossier Amdahl
amdahl_path = os.path.join(BASE_DIR, amdahl_dir)

# Créer un graphique pour Amdahl
plt.figure(figsize=(12, 7))
colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown']  # Couleurs fixes

# Parcourir les dossiers de threads pour Amdahl
thread_dirs = [d for d in os.listdir(amdahl_path) if d.startswith("threads_")]
for i, thread_dir in enumerate(sorted(thread_dirs, key=lambda x: int(x.split("_")[1]))):
    thread_path = os.path.join(amdahl_path, thread_dir)
    thread_count = thread_dir.split("_")[1]
    
    # Chercher les fichiers CSV
    csv_files = glob.glob(os.path.join(thread_path, "*.csv"))
    
    if csv_files:
        all_dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                all_dfs.append(df)
            except:
                pass
        
        if all_dfs:
            # Combiner les données
            combined_df = pd.concat(all_dfs)
            # Calculer la moyenne par TimeStep
            avg_df = combined_df.groupby('TimeStep').mean().reset_index()
            
            # Tracer la courbe
            plt.plot(avg_df['TimeStep'], avg_df['T_avancement'], 
                     linewidth=2, color=colors[i % len(colors)], 
                     label=f'{thread_count} threads')

# Finaliser le graphique Amdahl
plt.xlabel('Pas de Temps (TimeStep)')
plt.ylabel('Temps de Calcul (secondes)')
plt.title(f'Performance par Timestep - Amdahl (Taille=500)')
plt.grid(True)
plt.legend()
plt.savefig(f"{amdahl_dir}_performance_timestep.png")
plt.close()

# Tracer les graphiques pour Gustafson
gustafson_dir = "gustafson_204"  # Nom exact du dossier Gustafson
gustafson_path = os.path.join(BASE_DIR, gustafson_dir)

# Créer un graphique pour Gustafson
plt.figure(figsize=(12, 7))

# Parcourir les dossiers de threads pour Gustafson
thread_dirs = [d for d in os.listdir(gustafson_path) if d.startswith("threads_")]
for i, thread_dir in enumerate(sorted(thread_dirs, key=lambda x: int(x.split("_")[1]))):
    thread_path = os.path.join(gustafson_path, thread_dir)
    parts = thread_dir.split("_")
    thread_count = parts[1]
    size = parts[3] if len(parts) > 3 else "?"
    
    # Chercher les fichiers CSV
    csv_files = glob.glob(os.path.join(thread_path, "*.csv"))
    
    if csv_files:
        all_dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                all_dfs.append(df)
            except:
                pass
        
        if all_dfs:
            # Combiner les données
            combined_df = pd.concat(all_dfs)
            # Calculer la moyenne par TimeStep
            avg_df = combined_df.groupby('TimeStep').mean().reset_index()
            
            # Tracer la courbe
            plt.plot(avg_df['TimeStep'], avg_df['T_avancement'], 
                     linewidth=2, color=colors[i % len(colors)], 
                     label=f'{thread_count} threads (taille={size})')

# Finaliser le graphique Gustafson
plt.xlabel('Pas de Temps (TimeStep)')
plt.ylabel('Temps de Calcul (secondes)')
plt.title(f'Performance par Timestep - Gustafson (Base=204)')
plt.grid(True)
plt.legend()
plt.savefig(f"{gustafson_dir}_performance_timestep.png")

print("Graphiques générés avec succès!")