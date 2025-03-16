import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob

# Répertoire de base où les tests sont stockés
BASE_DIR = "tests"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
SPEEDUP_DIR = os.path.join(RESULTS_DIR, "speedup")

# Créer les répertoires s'ils n'existent pas
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(SPEEDUP_DIR, exist_ok=True)

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
    return speedups, temps_pic

def calculer_speedup_gustafson(dossier, taille_base):
    """
    Calcule l'accélération selon la loi de Gustafson en utilisant le temps de pic.
    Pour Gustafson, nous devons tenir compte de la taille du problème qui grandit
    proportionnellement au nombre de processeurs.
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
    
    # Correction: Pour Gustafson, on divise T1 par Tp/p (où p est le nombre de threads)
    for threads, temps in temps_pic.items():
        # Le temps séquentiel équivalent serait T1 * threads (car problème plus grand)
        temps_equivalent_sequentiel = T1_base * threads
        # Le speedup correct pour Gustafson: temps séquentiel équivalent / temps parallèle
        speedups[threads] = temps_equivalent_sequentiel / temps_pic[threads]
    
    return speedups, temps_pic

def obtenir_temps_sequentiel():
    """
    Obtient le temps d'exécution séquentiel à partir des fichiers dans tests_sequentiel
    """
    seq_dir = os.path.join(BASE_DIR, "tests_sequentiel")
    if not os.path.exists(seq_dir):
        print(f"Erreur : Répertoire {seq_dir} non trouvé.")
        return None
    
    # Chercher tous les fichiers CSV dans le répertoire séquentiel
    csv_files = glob.glob(os.path.join(seq_dir, "resultats_temps_*.csv"))
    if not csv_files:
        print(f"Erreur : Aucun fichier CSV trouvé dans {seq_dir}")
        return None
    
    # Calculer le temps moyen pour tous les fichiers
    temps_total_moyen = 0
    count = 0
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            # Pour l'analyse de speedup, nous utilisons le temps maximal de chaque exécution
            temps_max = df["T_avancement"].max()
            temps_total_moyen += temps_max
            count += 1
        except Exception as e:
            print(f"Erreur lors de la lecture de {csv_file}: {e}")
    
    if count == 0:
        return None
    
    return temps_total_moyen / count

def calculer_speedup_vrai_sequentiel(temps_pic, temps_sequentiel, est_gustafson=False, base_size=None):
    """
    Calcule le speedup en utilisant le temps séquentiel véritable comme référence
    
    Pour Gustafson, nous ajustons le calcul en tenant compte de la taille croissante du problème.
    """
    if not temps_sequentiel:
        return None
    
    speedups = {}
    
    for threads, temps in temps_pic.items():
        if est_gustafson:
            # Pour Gustafson, le temps séquentiel équivalent pour un problème de taille N*p
            # serait approximativement le temps séquentiel de base * p
            temps_sequentiel_equivalent = temps_sequentiel * threads
            speedups[threads] = temps_sequentiel_equivalent / temps
        else:
            # Pour Amdahl, c'est simplement le rapport entre temps séquentiel et temps parallèle
            speedups[threads] = temps_sequentiel / temps
    
    return speedups

# Calculer les accélérations avec la méthode actuelle (même programme, 1 thread)
speedup_amdahl, temps_pic_amdahl = calculer_speedup_amdahl(AMDAL_DIR)
speedup_gustafson, temps_pic_gustafson = calculer_speedup_gustafson(GUSTAFSON_DIR, gustafson_base_size)

if not speedup_amdahl or not speedup_gustafson:
    print("Erreur lors du calcul des accélérations. Vérifiez les répertoires et fichiers CSV.")
    exit()

# Créer un graphique pour la méthode actuelle
plt.figure(figsize=(10, 6))

# Tracer les résultats
plt.plot(list(speedup_amdahl.keys()), list(speedup_amdahl.values()), marker="o", linestyle="-",
         label=f"Amdahl (amdal_{amdal_dirs[-1].split('_')[1]})", color="blue")
plt.plot(list(speedup_gustafson.keys()), list(speedup_gustafson.values()), marker="s", linestyle="--",
         label=f"Gustafson (gustafson_{gustafson_base_size})", color="red")

plt.xlabel("Nombre de Threads")
plt.ylabel("Accélération")
plt.title("Comparaison de l'Accélération : Amdahl vs. Gustafson (Basé sur le Programme Parallèle)")
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(SPEEDUP_DIR, f"speedup_comparison_same_program_{amdal_dirs[-1]}_{gustafson_dirs[-1]}.png"))
plt.close()

# Obtenir le temps séquentiel à partir des fichiers de la version séquentielle
temps_sequentiel = obtenir_temps_sequentiel()

if temps_sequentiel:
    # Calculer les nouveaux speedups basés sur le vrai temps séquentiel
    true_speedup_amdahl = calculer_speedup_vrai_sequentiel(temps_pic_amdahl, temps_sequentiel, est_gustafson=False)
    true_speedup_gustafson = calculer_speedup_vrai_sequentiel(temps_pic_gustafson, temps_sequentiel, est_gustafson=True, base_size=gustafson_base_size)
    
    # Créer un graphique pour la nouvelle méthode
    plt.figure(figsize=(10, 6))
    
    # Tracer les résultats
    plt.plot(list(true_speedup_amdahl.keys()), list(true_speedup_amdahl.values()), marker="o", linestyle="-",
             label=f"Amdahl (amdal_{amdal_dirs[-1].split('_')[1]})", color="blue")
    plt.plot(list(true_speedup_gustafson.keys()), list(true_speedup_gustafson.values()), marker="s", linestyle="--",
             label=f"Gustafson (gustafson_{gustafson_base_size})", color="red")
    
    plt.xlabel("Nombre de Threads")
    plt.ylabel("Accélération")
    plt.title("Comparaison de l'Accélération : Amdahl vs. Gustafson (Basé sur Version Séquentielle)")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(SPEEDUP_DIR, f"speedup_comparison_true_sequential_{amdal_dirs[-1]}_{gustafson_dirs[-1]}.png"))
    plt.close()
    
    # Afficher les valeurs pour analyse
    print("Temps de pic et accélérations pour Amdahl (par rapport au programme parallèle avec 1 thread):")
    for threads, speedup in speedup_amdahl.items():
        print(f"{threads} threads : {speedup:.2f}x")
    
    print("\nTemps de pic et accélérations pour Gustafson (par rapport au programme parallèle avec 1 thread):")
    for threads, speedup in speedup_gustafson.items():
        print(f"{threads} threads : {speedup:.2f}x")
    
    print("\nTemps séquentiel véritable :", temps_sequentiel)
    
    print("\nTemps de pic et accélérations pour Amdahl (par rapport au programme séquentiel):")
    for threads, speedup in true_speedup_amdahl.items():
        print(f"{threads} threads : {speedup:.2f}x")
    
    print("\nTemps de pic et accélérations pour Gustafson (par rapport au programme séquentiel):")
    for threads, speedup in true_speedup_gustafson.items():
        print(f"{threads} threads : {speedup:.2f}x")
else:
    print("Impossible de calculer le speedup basé sur le vrai programme séquentiel.")
    
    # Afficher les valeurs pour analyse
    print("Temps de pic et accélérations pour Amdahl (par rapport au programme parallèle avec 1 thread):")
    for threads, speedup in speedup_amdahl.items():
        print(f"{threads} threads : {speedup:.2f}x")
    
    print("\nTemps de pic et accélérations pour Gustafson (par rapport au programme parallèle avec 1 thread):")
    for threads, speedup in speedup_gustafson.items():
        print(f"{threads} threads : {speedup:.2f}x")

print("\nTraitement terminé!")