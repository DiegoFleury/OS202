import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import re

# Configurations
BASE_DIR = "tests"
OUTPUT_DIR = "."  # Dossier racine pour sauvegarder les graphiques

# Rechercher les répertoires Amdahl et Gustafson
amdal_dirs = [d for d in os.listdir(BASE_DIR) if d.startswith("amdal_")]
gustafson_dirs = [d for d in os.listdir(BASE_DIR) if d.startswith("gustafson_")]

if not amdal_dirs and not gustafson_dirs:
    print("Aucun répertoire de tests trouvé!")
    exit()

# Fonction pour traiter un répertoire de test spécifique (Amdahl ou Gustafson)
def traiter_repertoire_test(test_dir, test_type):
    full_path = os.path.join(BASE_DIR, test_dir)
    
    # Obtenir tous les répertoires de threads (1, 2, 4, 6, etc.)
    thread_dirs = sorted([d for d in os.listdir(full_path) if d.isdigit()], 
                         key=lambda x: int(x))
    
    if not thread_dirs:
        print(f"Aucun répertoire de threads trouvé dans {full_path}")
        return
    
    # Configurer le graphique
    plt.figure(figsize=(12, 8))
    
    # Couleurs pour différents nombres de threads
    colors = plt.cm.viridis(np.linspace(0, 1, len(thread_dirs)))
    
    for idx, thread_dir in enumerate(thread_dirs):
        thread_path = os.path.join(full_path, thread_dir)
        
        if not os.path.isdir(thread_path):
            continue
        
        csv_files = glob.glob(os.path.join(thread_path, "timing_results_*_threads*.csv"))
        
        if not csv_files:
            print(f"Aucun fichier CSV trouvé dans {thread_path}")
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
            print(f"Aucune donnée valide trouvée pour {thread_dir} threads")
            continue
        
        combined_data = pd.concat(all_data, ignore_index=True)
        
        avg_data = combined_data.groupby('TimeStep').mean().reset_index()
        
        plt.plot(avg_data["TimeStep"], avg_data["T_avancement"], 
                 linestyle='-', color=colors[idx], linewidth=2,
                 label=f"{thread_dir} threads")
    
    plt.xlabel("Pas de temps (TimeStep)")
    plt.ylabel("Temps de calcul (secondes)")
    plt.title(f"Temps moyen de calcul - {test_type} ({test_dir})")
    plt.legend()
    plt.grid(True)
    
    output_file = os.path.join(OUTPUT_DIR, f"timing_curves_{test_dir}.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique sauvegardé: {output_file}")

for amdal_dir in amdal_dirs:
    traiter_repertoire_test(amdal_dir, "Amdahl")

for gustafson_dir in gustafson_dirs:
    traiter_repertoire_test(gustafson_dir, "Gustafson")

if amdal_dirs and gustafson_dirs:
    latest_amdal = sorted(amdal_dirs)[-1]
    latest_gustafson = sorted(gustafson_dirs)[-1]
    
    amdal_threads = set([d for d in os.listdir(os.path.join(BASE_DIR, latest_amdal)) if d.isdigit()])
    gustafson_threads = set([d for d in os.listdir(os.path.join(BASE_DIR, latest_gustafson)) if d.isdigit()])
    common_threads = sorted(amdal_threads.intersection(gustafson_threads), key=int)
    
    if common_threads:
        for thread_count in common_threads:
            plt.figure(figsize=(12, 8))
            
            amdal_path = os.path.join(BASE_DIR, latest_amdal, thread_count)
            amdal_csv_files = glob.glob(os.path.join(amdal_path, "timing_results_*_threads*.csv"))
            
            if amdal_csv_files:
                amdal_data = []
                for csv_file in amdal_csv_files:
                    try:
                        df = pd.read_csv(csv_file)
                        if not df.empty:
                            amdal_data.append(df)
                    except Exception as e:
                        print(f"Erreur lors de la lecture de {csv_file}: {e}")
                
                if amdal_data:
                    combined_amdal = pd.concat(amdal_data, ignore_index=True)
                    avg_amdal = combined_amdal.groupby('TimeStep').mean().reset_index()
                    plt.plot(avg_amdal["TimeStep"], avg_amdal["T_avancement"], 
                             linestyle='-', color='blue', linewidth=2,
                             label=f"Amdahl ({latest_amdal})")
            
            gustafson_path = os.path.join(BASE_DIR, latest_gustafson, thread_count)
            gustafson_csv_files = glob.glob(os.path.join(gustafson_path, "timing_results_*_threads*.csv"))
            
            if gustafson_csv_files:
                gustafson_data = []
                for csv_file in gustafson_csv_files:
                    try:
                        df = pd.read_csv(csv_file)
                        if not df.empty:
                            gustafson_data.append(df)
                    except Exception as e:
                        print(f"Erreur lors de la lecture de {csv_file}: {e}")
                
                if gustafson_data:
                    combined_gustafson = pd.concat(gustafson_data, ignore_index=True)
                    avg_gustafson = combined_gustafson.groupby('TimeStep').mean().reset_index()
                    plt.plot(avg_gustafson["TimeStep"], avg_gustafson["T_avancement"], 
                             linestyle='--', color='red', linewidth=2,
                             label=f"Gustafson ({latest_gustafson})")
            
            plt.xlabel("Pas de temps (TimeStep)")
            plt.ylabel("Temps de calcul (secondes)")
            plt.title(f"Comparaison Amdahl vs Gustafson - {thread_count} threads")
            plt.legend()
            plt.grid(True)
            
            output_file = os.path.join(OUTPUT_DIR, f"comparison_{thread_count}_threads.png")
            plt.savefig(output_file)
            plt.close()
            
            print(f"Comparaison sauvegardée: {output_file}")

print("Traitement terminé!")
