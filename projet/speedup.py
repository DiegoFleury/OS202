import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob

# Répertoires
BASE_DIR = "tests"

def calculer_speedup_et_efficacite(temps_type="T_avancement"):
    """
    Calcule les speedups et efficacités basés sur le type de temps spécifié
    
    Args:
        temps_type: Colonne de temps à utiliser ('T_avancement' ou 'T_total')
    
    Returns:
        Tuple contenant les speedups et efficacités d'Amdahl et Gustafson
    """
    # 1. Calculer le speedup pour Amdahl (taille constante)
    amdahl_dir = "amdahl_500"
    amdahl_path = os.path.join(BASE_DIR, amdahl_dir)
    
    # Trouver tous les dossiers de threads pour Amdahl
    thread_dirs = [d for d in os.listdir(amdahl_path) if d.startswith("threads_")]
    thread_dirs = sorted(thread_dirs, key=lambda x: int(x.split("_")[1]))
    
    # Trouver d'abord le temps de référence (1 thread)
    ref_dir = next((d for d in thread_dirs if d.split("_")[1] == "1"), None)
    t1 = None
    
    if ref_dir:
        ref_path = os.path.join(amdahl_path, ref_dir)
        csv_files = glob.glob(os.path.join(ref_path, "*.csv"))
        
        all_times = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                all_times.append(df[temps_type].mean())
            except Exception as e:
                print(f"Erreur avec {csv_file}: {e}")
                pass
        
        if all_times:
            t1 = np.mean(all_times)
    
    if t1 is None:
        print(f"Impossible de trouver le temps de référence {temps_type} pour Amdahl")
        return None, None
    
    # Calculer les speedups et efficacités pour chaque nombre de threads
    amdahl_speedups = []
    amdahl_efficiencies = []
    
    for thread_dir in thread_dirs:
        thread_count = int(thread_dir.split("_")[1])
        thread_path = os.path.join(amdahl_path, thread_dir)
        
        csv_files = glob.glob(os.path.join(thread_path, "*.csv"))
        all_times = []
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                all_times.append(df[temps_type].mean())
            except:
                pass
        
        if all_times:
            avg_time = np.mean(all_times)
            # Speedup Amdahl: T1/Tp
            speedup = t1 / avg_time
            amdahl_speedups.append((thread_count, speedup))
            
            # Efficacité: Speedup/nombre de threads
            efficiency = speedup / thread_count
            amdahl_efficiencies.append((thread_count, efficiency))
    
    # 2. Calculer le speedup pour Gustafson (taille variable)
    gustafson_dir = "gustafson_204"
    gustafson_path = os.path.join(BASE_DIR, gustafson_dir)
    
    # Trouver tous les dossiers de threads pour Gustafson
    thread_dirs = [d for d in os.listdir(gustafson_path) if d.startswith("threads_")]
    thread_dirs = sorted(thread_dirs, key=lambda x: int(x.split("_")[1]))
    
    # Trouver d'abord le temps de référence (1 thread)
    ref_dir = next((d for d in thread_dirs if d.split("_")[1] == "1"), None)
    t1 = None
    
    if ref_dir:
        ref_path = os.path.join(gustafson_path, ref_dir)
        csv_files = glob.glob(os.path.join(ref_path, "*.csv"))
        
        all_times = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                all_times.append(df[temps_type].mean())
            except:
                pass
        
        if all_times:
            t1 = np.mean(all_times)
    
    if t1 is None:
        print(f"Impossible de trouver le temps de référence {temps_type} pour Gustafson")
        return amdahl_speedups, amdahl_efficiencies, None, None
    
    # Calculer les speedups pour chaque nombre de threads (Gustafson)
    gustafson_speedups = []
    gustafson_efficiencies = []
    
    for thread_dir in thread_dirs:
        parts = thread_dir.split("_")
        thread_count = int(parts[1])
        size = int(parts[3]) if len(parts) > 3 else None
        
        thread_path = os.path.join(gustafson_path, thread_dir)
        
        csv_files = glob.glob(os.path.join(thread_path, "*.csv"))
        all_times = []
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                all_times.append(df[temps_type].mean())
            except:
                pass
        
        if all_times:
            avg_time = np.mean(all_times)
            # Speedup Gustafson: t1 / (tp / p) où p est le nombre de threads
            speedup = t1 / (avg_time / thread_count)
            gustafson_speedups.append((thread_count, speedup, size))
            
            # Efficacité: Speedup/nombre de threads
            efficiency = speedup / thread_count
            gustafson_efficiencies.append((thread_count, efficiency, size))
    
    return amdahl_speedups, amdahl_efficiencies, gustafson_speedups, gustafson_efficiencies

def tracer_speedup(amdahl_speedups, gustafson_speedups, temps_type):
    """
    Trace le graphique de speedup pour un type de temps spécifique
    """
    plt.figure(figsize=(12, 7))
    
    # Amdahl
    if amdahl_speedups:
        amdahl_threads = [x[0] for x in amdahl_speedups]
        amdahl_values = [x[1] for x in amdahl_speedups]
        
        plt.plot(amdahl_threads, amdahl_values, 'o-', linewidth=2, color='blue', 
                label='Amdahl (taille=500)')
    
    # Gustafson
    if gustafson_speedups:
        gustafson_threads = [x[0] for x in gustafson_speedups]
        gustafson_values = [x[1] for x in gustafson_speedups]
        
        plt.plot(gustafson_threads, gustafson_values, 's--', linewidth=2, color='red', 
                label='Gustafson (base=204)')
    
    plt.xlabel('Nombre de threads')
    plt.ylabel('Speedup')
    temps_label = "Temps d'Avancement" if temps_type == "T_avancement" else "Temps Total"
    plt.title(f'Speedup basé sur {temps_label}: Amdahl vs. Gustafson')
    plt.grid(True)
    plt.legend()
    
    # Sauvegarder le graphique spécifique
    output_file = f"speedup_{temps_type.lower()[2:]}.png"
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de speedup ({temps_label}) sauvegardé dans {output_file}")

def tracer_efficacite(amdahl_efficiencies, gustafson_efficiencies, temps_type):
    """
    Trace le graphique d'efficacité pour un type de temps spécifique
    """
    plt.figure(figsize=(12, 7))
    
    # Amdahl
    if amdahl_efficiencies:
        amdahl_threads = [x[0] for x in amdahl_efficiencies]
        amdahl_values = [x[1] for x in amdahl_efficiencies]
        
        plt.plot(amdahl_threads, amdahl_values, 'o-', linewidth=2, color='blue', 
                label='Amdahl (taille=500)')
    
    # Gustafson
    if gustafson_efficiencies:
        gustafson_threads = [x[0] for x in gustafson_efficiencies]
        gustafson_values = [x[1] for x in gustafson_efficiencies]
        
        plt.plot(gustafson_threads, gustafson_values, 's--', linewidth=2, color='red', 
                label='Gustafson (base=204)')
    
    plt.xlabel('Nombre de threads')
    plt.ylabel('Efficacité')
    temps_label = "Temps d'Avancement" if temps_type == "T_avancement" else "Temps Total"
    plt.title(f'Efficacité basée sur {temps_label}: Amdahl vs. Gustafson')
    plt.grid(True)
    plt.legend()
    
    # Sauvegarder le graphique spécifique
    output_file = f"efficacite_{temps_type.lower()[2:]}.png"
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique d'efficacité ({temps_label}) sauvegardé dans {output_file}")

def tracer_comparaison_speedups(speedups_av, speedups_tot):
    """
    Trace un graphique comparant les speedups basés sur différents temps
    """
    plt.figure(figsize=(12, 7))
    
    # Extraire les données
    amdahl_av, _, gustafson_av, _ = speedups_av
    amdahl_tot, _, gustafson_tot, _ = speedups_tot
    
    # Tracer les courbes d'Amdahl
    if amdahl_av:
        amdahl_av_threads = [x[0] for x in amdahl_av]
        amdahl_av_values = [x[1] for x in amdahl_av]
        plt.plot(amdahl_av_threads, amdahl_av_values, 'o-', linewidth=2, color='blue', 
                label='Amdahl - Temps d\'Avancement')
    
    if amdahl_tot:
        amdahl_tot_threads = [x[0] for x in amdahl_tot]
        amdahl_tot_values = [x[1] for x in amdahl_tot]
        plt.plot(amdahl_tot_threads, amdahl_tot_values, '^-', linewidth=2, color='skyblue', 
                label='Amdahl - Temps Total')
    
    # Tracer les courbes de Gustafson
    if gustafson_av:
        gustafson_av_threads = [x[0] for x in gustafson_av]
        gustafson_av_values = [x[1] for x in gustafson_av]
        plt.plot(gustafson_av_threads, gustafson_av_values, 's--', linewidth=2, color='red', 
                label='Gustafson - Temps d\'Avancement')
    
    if gustafson_tot:
        gustafson_tot_threads = [x[0] for x in gustafson_tot]
        gustafson_tot_values = [x[1] for x in gustafson_tot]
        plt.plot(gustafson_tot_threads, gustafson_tot_values, 'd--', linewidth=2, color='salmon', 
                label='Gustafson - Temps Total')
    
    plt.xlabel('Nombre de threads')
    plt.ylabel('Speedup')
    plt.title('Comparaison des Speedups: Temps d\'Avancement vs. Temps Total')
    plt.grid(True)
    plt.legend()
    
    # Sauvegarder le graphique de comparaison
    plt.savefig("speedup_comparaison.png")
    plt.close()
    
    print("Graphique de comparaison des speedups sauvegardé dans speedup_comparaison.png")

def tracer_comparaison_efficacites(speedups_av, speedups_tot):
    """
    Trace un graphique comparant les efficacités basées sur différents temps
    """
    plt.figure(figsize=(12, 7))
    
    # Extraire les données
    _, amdahl_av_eff, _, gustafson_av_eff = speedups_av
    _, amdahl_tot_eff, _, gustafson_tot_eff = speedups_tot
    
    # Tracer les courbes d'Amdahl
    if amdahl_av_eff:
        amdahl_av_threads = [x[0] for x in amdahl_av_eff]
        amdahl_av_values = [x[1] for x in amdahl_av_eff]
        plt.plot(amdahl_av_threads, amdahl_av_values, 'o-', linewidth=2, color='blue', 
                label='Amdahl - Temps d\'Avancement')
    
    if amdahl_tot_eff:
        amdahl_tot_threads = [x[0] for x in amdahl_tot_eff]
        amdahl_tot_values = [x[1] for x in amdahl_tot_eff]
        plt.plot(amdahl_tot_threads, amdahl_tot_values, '^-', linewidth=2, color='skyblue', 
                label='Amdahl - Temps Total')
    
    # Tracer les courbes de Gustafson
    if gustafson_av_eff:
        gustafson_av_threads = [x[0] for x in gustafson_av_eff]
        gustafson_av_values = [x[1] for x in gustafson_av_eff]
        plt.plot(gustafson_av_threads, gustafson_av_values, 's--', linewidth=2, color='red', 
                label='Gustafson - Temps d\'Avancement')
    
    if gustafson_tot_eff:
        gustafson_tot_threads = [x[0] for x in gustafson_tot_eff]
        gustafson_tot_values = [x[1] for x in gustafson_tot_eff]
        plt.plot(gustafson_tot_threads, gustafson_tot_values, 'd--', linewidth=2, color='salmon', 
                label='Gustafson - Temps Total')
    
    plt.xlabel('Nombre de threads')
    plt.ylabel('Efficacité')
    plt.title('Comparaison des Efficacités: Temps d\'Avancement vs. Temps Total')
    plt.grid(True)
    plt.legend()
    
    # Sauvegarder le graphique de comparaison
    plt.savefig("efficacite_comparaison.png")
    plt.close()
    
    print("Graphique de comparaison des efficacités sauvegardé dans efficacite_comparaison.png")

# Exécuter les analyses
try:
    # Calculer les métriques basées sur le temps d'avancement
    resultats_av = calculer_speedup_et_efficacite("T_avancement")
    
    # Calculer les métriques basées sur le temps total
    resultats_tot = calculer_speedup_et_efficacite("T_total")
    
    # Tracer les graphiques de speedup
    tracer_speedup(resultats_av[0], resultats_av[2], "T_avancement")
    tracer_speedup(resultats_tot[0], resultats_tot[2], "T_total")
    
    # Tracer les graphiques d'efficacité
    tracer_efficacite(resultats_av[1], resultats_av[3], "T_avancement")
    tracer_efficacite(resultats_tot[1], resultats_tot[3], "T_total")
    
    # Tracer les graphiques de comparaison
    tracer_comparaison_speedups(resultats_av, resultats_tot)
    tracer_comparaison_efficacites(resultats_av, resultats_tot)
    
    print("Analyse terminée!")
except Exception as e:
    print(f"Erreur lors de l'analyse: {e}")