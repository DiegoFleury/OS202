import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Répertoire de base où les tests sont stockés
BASE_DIR = "tests"

# Trouver dynamiquement les répertoires d'Amdahl et de Gustafson
amdal_dirs = [d for d in os.listdir(BASE_DIR) if d.startswith("amdal_")]
gustafson_dirs = [d for d in os.listdir(BASE_DIR) if d.startswith("gustafson_")]

if not amdal_dirs or not gustafson_dirs:
    print("Erreur : Répertoires d'Amdahl ou de Gustafson non trouvés.")
    exit()

# Trier pour obtenir la version la plus récente
amdal_dirs.sort()
gustafson_dirs.sort()
AMDAL_DIR = os.path.join(BASE_DIR, amdal_dirs[-1])  # Dernière version
GUSTAFSON_DIR = os.path.join(BASE_DIR, gustafson_dirs[-1])  # Dernière version

# Extraire la taille de base de Gustafson à partir du nom du répertoire
gustafson_base_size = int(gustafson_dirs[-1].split("_")[1])

def calculer_speedup_amdahl(dossier):
    """Calcule l'accélération selon la loi d'Amdahl, en utilisant le temps de pic"""
    temps_pic = {}
    for threads in sorted(os.listdir(dossier), key=lambda x: int(x) if x.isdigit() else 0):
        thread_dir = os.path.join(dossier, threads)
        if not os.path.isdir(thread_dir):
            continue
        
        fichiers = [os.path.join(thread_dir, f) for f in os.listdir(thread_dir) if f.endswith(".csv")]
        if not fichiers:
            continue
        
        pics_executions = []
        for fichier in fichiers:
            df = pd.read_csv(fichier)
            pic = df["T_avancement"].max()
            pics_executions.append(pic)
        
        temps_pic[int(threads)] = np.mean(pics_executions)
    
    if 1 not in temps_pic:
        print(f"Erreur : pas de données pour 1 thread dans {dossier}")
        return None
    
    T1 = temps_pic[1]
    speedups = {threads: T1 / temps for threads, temps in temps_pic.items()}
    return speedups

def calculer_speedup_gustafson(dossier, taille_base):
    """
    Calcule l'accélération selon la loi de Gustafson en utilisant le temps de pic
    """
    temps_pic = {}
    tailles = {}
    
    for threads_str in sorted(os.listdir(dossier), key=lambda x: int(x) if x.isdigit() else 0):
        thread_dir = os.path.join(dossier, threads_str)
        if not os.path.isdir(thread_dir):
            continue
        
        threads = int(threads_str)
        fichiers = [os.path.join(thread_dir, f) for f in os.listdir(thread_dir) if f.endswith(".csv")]
        if not fichiers:
            continue
        
        taille_probleme = taille_base * threads
        tailles[threads] = taille_probleme
        
        pics_executions = []
        for fichier in fichiers:
            df = pd.read_csv(fichier)
            pic = df["T_avancement"].max()
            pics_executions.append(pic)
        
        temps_pic[threads] = np.mean(pics_executions)
    
    if 1 not in temps_pic:
        print(f"Erreur : pas de données pour 1 thread dans {dossier}")
        return None
    
    speedups = {}
    T1_base = temps_pic[1]
    
    for threads, temps in temps_pic.items():
        temps_normalise = temps / threads
        speedups[threads] = T1_base / temps_normalise
    
    return speedups

# Calculer les accélérations
speedup_amdahl = calculer_speedup_amdahl(AMDAL_DIR)
speedup_gustafson = calculer_speedup_gustafson(GUSTAFSON_DIR, gustafson_base_size)

if not speedup_amdahl or not speedup_gustafson:
    print("Erreur lors du calcul des accélérations. Vérifiez les répertoires et fichiers CSV.")
    exit()

# Créer un graphique
plt.figure(figsize=(10, 6))

# Tracer les résultats
plt.plot(list(speedup_amdahl.keys()), list(speedup_amdahl.values()), marker="o", linestyle="-",
         label=f"Amdahl (amdal_{amdal_dirs[-1].split('_')[1]})", color="blue")
plt.plot(list(speedup_gustafson.keys()), list(speedup_gustafson.values()), marker="s", linestyle="--",
         label=f"Gustafson (gustafson_{gustafson_base_size})", color="red")

plt.xlabel("Nombre de Threads")
plt.ylabel("Accélération")
plt.title("Comparaison de l'Accélération : Amdahl vs. Gustafson (Basé sur le Temps de Pic)")
plt.legend()
plt.grid(True)
plt.savefig(f"{BASE_DIR}/speedup_comparison_peak_{amdal_dirs[-1]}_{gustafson_dirs[-1]}.png")
plt.show()

# Afficher les valeurs pour analyse
print("Temps de pic et accélérations pour Amdahl:")
for threads, speedup in speedup_amdahl.items():
    print(f"{threads} threads : {speedup:.2f}x")

print("\nTemps de pic et accélérations pour Gustafson:")
for threads, speedup in speedup_gustafson.items():
    print(f"{threads} threads : {speedup:.2f}x")
