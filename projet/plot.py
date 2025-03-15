import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import re

# Configurations
BASE_DIR = "tests"
OUTPUT_DIR = "."  # Dossier racine pour sauvegarder les graphiques

# Vérifier que le dossier de tests existe
if not os.path.exists(BASE_DIR):
    print(f"Le répertoire {BASE_DIR} n'existe pas!")
    exit()

# Obtenir tous les sous-répertoires correspondant aux différentes tailles de grille
# Ajusté pour correspondre au format "size_100", "size_200", etc.
size_dirs = sorted([d for d in os.listdir(BASE_DIR) if d.startswith("size_")], 
                   key=lambda x: int(x.split("_")[1]))

if not size_dirs:
    print(f"Aucun répertoire de tests trouvé dans {BASE_DIR}!")
    exit()

# Extraire juste les valeurs de taille pour l'affichage
grid_sizes = [d.split("_")[1] for d in size_dirs]
print(f"Tailles de grille trouvées: {grid_sizes}")

# Graphique 1: Temps de calcul moyen pour chaque taille de grille
plt.figure(figsize=(12, 8))

# Couleurs pour différentes tailles de grille
colors = plt.cm.viridis(np.linspace(0, 1, len(size_dirs)))

avg_times_by_size = []

for idx, size_dir in enumerate(size_dirs):
    size_path = os.path.join(BASE_DIR, size_dir)
    size = size_dir.split("_")[1]  # Extraire le nombre de "size_100"
    
    if not os.path.isdir(size_path):
        continue
    
    # Trouver tous les fichiers CSV dans ce répertoire
    # Format ajusté pour correspondre à "timing_results_size100_v1.csv"
    csv_files = glob.glob(os.path.join(size_path, f"timing_results_size{size}_v*.csv"))
    
    if not csv_files:
        print(f"Aucun fichier CSV trouvé dans {size_path}")
        continue
    
    all_data = []
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            if not df.empty:
                all_data.append(df)
        except Exception as e:
            print(f"Erreur lors de la lecture de {csv_file}: {e}")
    
    if not all_data:
        print(f"Aucune donnée valide trouvée pour la taille {size}")
        continue
    
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Calculer la moyenne des temps d'avancement pour chaque pas de temps
    avg_data = combined_data.groupby('TimeStep').mean().reset_index()
    
    # Tracer la courbe pour cette taille de grille
    plt.plot(avg_data["TimeStep"], avg_data["T_avancement"], 
             linestyle='-', color=colors[idx], linewidth=2,
             label=f"Taille {size}")
    
    # Stocker le temps moyen global pour cette taille
    avg_time = avg_data["T_avancement"].mean()
    avg_times_by_size.append((int(size), avg_time))

plt.xlabel("Pas de temps (TimeStep)")
plt.ylabel("Temps de calcul (secondes)")
plt.title(f"Temps moyen de calcul par taille de grille (MPI avec 2 processus)")
plt.legend()
plt.grid(True)

output_file = os.path.join(OUTPUT_DIR, "timing_curves_by_grid_size.png")
plt.savefig(output_file)
plt.close()

print(f"Graphique des courbes temporelles sauvegardé: {output_file}")

# Graphique 3: Évolution des proportions de temps par composante en fonction de la taille de grille
# Préparer les données pour le graphique
sizes_for_plot = []
avancement_percentages = []
communication_percentages = []
affichage_percentages = []

for size_dir in size_dirs:
    size_path = os.path.join(BASE_DIR, size_dir)
    size = size_dir.split("_")[1]  # Extraire le nombre de "size_100"
    
    if not os.path.isdir(size_path):
        continue
    
    # Format ajusté pour correspondre à "timing_results_size100_v1.csv"
    csv_files = glob.glob(os.path.join(size_path, f"timing_results_size{size}_v*.csv"))
    
    if not csv_files:
        continue
    
    all_data = []
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            if not df.empty:
                all_data.append(df)
        except Exception as e:
            print(f"Erreur lors de la lecture de {csv_file}: {e}")
    
    if not all_data:
        continue
    
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Calculer les proportions de temps pour chaque composante
    combined_data["T_proportion_avancement"] = combined_data["T_avancement"] / combined_data["T_total"] * 100
    combined_data["T_proportion_communication"] = combined_data["T_communication"] / combined_data["T_total"] * 100
    combined_data["T_proportion_affichage"] = combined_data["T_affichage"] / combined_data["T_total"] * 100
    
    # Calculer les moyennes globales
    avg_avancement = combined_data["T_proportion_avancement"].mean()
    avg_communication = combined_data["T_proportion_communication"].mean()
    avg_affichage = combined_data["T_proportion_affichage"].mean()
    
    # Ajouter les données pour le graphique
    sizes_for_plot.append(int(size))
    avancement_percentages.append(avg_avancement)
    communication_percentages.append(avg_communication)
    affichage_percentages.append(avg_affichage)

# Créer le graphique de répartition des temps
if sizes_for_plot:
    # Trier les données par taille de grille
    sorted_indices = np.argsort(sizes_for_plot)
    sorted_sizes = [sizes_for_plot[i] for i in sorted_indices]
    sorted_avancement = [avancement_percentages[i] for i in sorted_indices]
    sorted_communication = [communication_percentages[i] for i in sorted_indices]
    sorted_affichage = [affichage_percentages[i] for i in sorted_indices]
    
    # Créer le graphique avec échelle normale
    plt.figure(figsize=(12, 8))
    plt.plot(sorted_sizes, sorted_avancement, 'o-', color='#ff9999', linewidth=2, markersize=8, label='Calcul')
    plt.plot(sorted_sizes, sorted_communication, 's-', color='#66b3ff', linewidth=2, markersize=8, label='Communication')
    plt.plot(sorted_sizes, sorted_affichage, '^-', color='#99ff99', linewidth=2, markersize=8, label='Affichage')
    plt.ylim(0, 100)
    plt.xlabel("Taille de la grille (N)")
    plt.ylabel("Pourcentage du temps total (%)")
    plt.title("Répartition du temps entre calcul, communication et affichage (échelle normale)")
    plt.grid(True)
    plt.legend()
    
    output_file = os.path.join(OUTPUT_DIR, "time_distribution_linear.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de répartition des temps (échelle normale) sauvegardé: {output_file}")
    
    # Créer le graphique avec échelle logarithmique
    plt.figure(figsize=(12, 8))
    plt.plot(sorted_sizes, sorted_avancement, 'o-', color='#ff9999', linewidth=2, markersize=8, label='Calcul')
    plt.plot(sorted_sizes, sorted_communication, 's-', color='#66b3ff', linewidth=2, markersize=8, label='Communication')
    plt.plot(sorted_sizes, sorted_affichage, '^-', color='#99ff99', linewidth=2, markersize=8, label='Affichage')
    plt.yscale('log')  # Échelle logarithmique
    plt.xlabel("Taille de la grille (N)")
    plt.ylabel("Pourcentage du temps total (échelle log)")
    plt.title("Répartition du temps entre calcul, communication et affichage (échelle logarithmique)")
    plt.grid(True)
    plt.legend()
    
    output_file = os.path.join(OUTPUT_DIR, "time_distribution_log.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de répartition des temps (échelle logarithmique) sauvegardé: {output_file}")

# Tableau récapitulatif des temps moyens
if avg_times_by_size:
    print("\nRécapitulatif des temps moyens par taille de grille:")
    print("-----------------------------------------------------")
    print("Taille   | Temps moyen (s)")
    print("-----------------------------------------------------")
    
    for size, time in sorted(avg_times_by_size):
        print(f"{size:8} | {time:.6f}")
    print("-----------------------------------------------------")
    
    # Sauvegarder ce tableau dans un fichier CSV
    summary_df = pd.DataFrame(avg_times_by_size, columns=['Taille', 'Temps_moyen'])
    summary_file = os.path.join(OUTPUT_DIR, "summary_mpi_performance.csv")
    summary_df.to_csv(summary_file, index=False)
    print(f"\nRécapitulatif sauvegardé dans {summary_file}")

print("\nTraitement terminé!")