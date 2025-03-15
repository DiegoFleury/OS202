# Reimportar bibliotecas após o reset do ambiente
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob

# Configurations
BASE_DIR = "tests"
OUTPUT_DIR = "."  # Dossier racine pour sauvegarder les graphiques

# Rechercher les fichiers CSV dans le répertoire "tests"
csv_files = glob.glob(os.path.join(BASE_DIR, "resultats_temps_v*.csv"))

if not csv_files:
    print("Aucun fichier CSV trouvé dans le répertoire 'tests'!")
    exit()

# Initialisation des données
all_data = []

# Lire et stocker les données des fichiers CSV
for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file)
        if not df.empty:
            all_data.append(df)
    except Exception as e:
        print(f"Erreur lors de la lecture de {csv_file}: {e}")

if not all_data:
    print("Aucune donnée valide trouvée !")
    exit()

# Combiner toutes les données et calculer la moyenne
combined_data = pd.concat(all_data, ignore_index=True)
avg_data = combined_data.groupby('TimeStep').mean().reset_index()

# Calculer la moyenne des différentes colonnes
mean_values = avg_data.mean(numeric_only=True)

# Génération du graphique
plt.figure(figsize=(12, 8))

# Tracer toutes les colonnes sauf TimeStep
for column in avg_data.columns:
    if column != "TimeStep":
        plt.plot(avg_data["TimeStep"], avg_data[column], linewidth=2, label=f"{column} (max: {mean_values[column].max():.4f})")

plt.xlabel("Pas de temps (TimeStep)")
plt.ylabel("Valeurs mesurées")
plt.title("Courbes des mesures avec max")
plt.legend()
plt.grid(True)

# Sauvegarder la figure
output_file = os.path.join(OUTPUT_DIR, "timing_curves_all_metrics.png")
plt.savefig(output_file)
plt.show()
