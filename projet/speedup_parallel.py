import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob

BASE_DIR = "tests"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
PERF_DIR = os.path.join(RESULTS_DIR, "performance")
SPEEDUP_DIR = os.path.join(RESULTS_DIR, "speedup")
EFFICIENCY_DIR = os.path.join(RESULTS_DIR, "efficacite")

for directory in [RESULTS_DIR, PERF_DIR, SPEEDUP_DIR, EFFICIENCY_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

def calculer_speedup_et_efficacite(temps_type="T_avancement"):
    amdahl_dir = "amdahl_500"
    amdahl_path = os.path.join(BASE_DIR, amdahl_dir)
    
    thread_dirs = [d for d in os.listdir(amdahl_path) if d.startswith("threads_")]
    thread_dirs = sorted(thread_dirs, key=lambda x: int(x.split("_")[1]))
    
    ref_dir = next((d for d in thread_dirs if d.split("_")[1] == "1"), None)
    t1 = None
    
    if ref_dir:
        ref_path = os.path.join(amdahl_path, ref_dir)
        csv_files = glob.glob(os.path.join(ref_path, "*.csv"))
        
        all_times = []
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            all_times.append(df[temps_type].mean())
        
        if all_times:
            t1 = np.mean(all_times)
    
    if t1 is None:
        print(f"Impossible de trouver le temps de référence {temps_type} pour Amdahl")
        return None, None
    
    amdahl_speedups = []
    amdahl_efficiencies = []
    
    for thread_dir in thread_dirs:
        thread_count = int(thread_dir.split("_")[1])
        thread_path = os.path.join(amdahl_path, thread_dir)
        
        csv_files = glob.glob(os.path.join(thread_path, "*.csv"))
        all_times = []
        
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            all_times.append(df[temps_type].mean())
        
        if all_times:
            avg_time = np.mean(all_times)
            speedup = t1 / avg_time
            amdahl_speedups.append((thread_count, speedup))
            
            efficiency = speedup / thread_count
            amdahl_efficiencies.append((thread_count, efficiency))
    
    gustafson_dir = "gustafson_204"
    gustafson_path = os.path.join(BASE_DIR, gustafson_dir)
    
    thread_dirs = [d for d in os.listdir(gustafson_path) if d.startswith("threads_")]
    thread_dirs = sorted(thread_dirs, key=lambda x: int(x.split("_")[1]))
    
    ref_dir = next((d for d in thread_dirs if d.split("_")[1] == "1"), None)
    t1 = None
    
    if ref_dir:
        ref_path = os.path.join(gustafson_path, ref_dir)
        csv_files = glob.glob(os.path.join(ref_path, "*.csv"))
        
        all_times = []
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            all_times.append(df[temps_type].mean())
        
        if all_times:
            t1 = np.mean(all_times)
    
    if t1 is None:
        print(f"Impossible de trouver le temps de référence {temps_type} pour Gustafson")
        return amdahl_speedups, amdahl_efficiencies, None, None
    
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
            df = pd.read_csv(csv_file)
            all_times.append(df[temps_type].mean())
        
        if all_times:
            avg_time = np.mean(all_times)
            speedup = t1 / (avg_time / thread_count)
            gustafson_speedups.append((thread_count, speedup, size))
            
            efficiency = speedup / thread_count
            gustafson_efficiencies.append((thread_count, efficiency, size))
    
    return amdahl_speedups, amdahl_efficiencies, gustafson_speedups, gustafson_efficiencies

def tracer_speedup(amdahl_speedups, gustafson_speedups, temps_type):
    plt.figure(figsize=(12, 7))
    
    if amdahl_speedups:
        amdahl_threads = [x[0] for x in amdahl_speedups]
        amdahl_values = [x[1] for x in amdahl_speedups]
        
        plt.plot(amdahl_threads, amdahl_values, 'o-', linewidth=2, color='blue', 
                label='Amdahl (taille=500)')
    
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
    
    output_file = os.path.join(SPEEDUP_DIR, f"speedup_{temps_type.lower()[2:]}.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de speedup ({temps_label}) sauvegardé dans {output_file}")

def tracer_efficacite(amdahl_efficiencies, gustafson_efficiencies, temps_type):
    plt.figure(figsize=(12, 7))
    
    if amdahl_efficiencies:
        amdahl_threads = [x[0] for x in amdahl_efficiencies]
        amdahl_values = [x[1] for x in amdahl_efficiencies]
        
        plt.plot(amdahl_threads, amdahl_values, 'o-', linewidth=2, color='blue', 
                label='Amdahl (taille=500)')
    
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
    
    output_file = os.path.join(EFFICIENCY_DIR, f"efficacite_{temps_type.lower()[2:]}.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique d'efficacité ({temps_label}) sauvegardé dans {output_file}")

def tracer_comparaison_speedups(speedups_av, speedups_tot):
    plt.figure(figsize=(12, 7))
    
    amdahl_av, _, gustafson_av, _ = speedups_av
    amdahl_tot, _, gustafson_tot, _ = speedups_tot
    
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
    
    output_file = os.path.join(SPEEDUP_DIR, "speedup_comparaison.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de comparaison des speedups sauvegardé dans {output_file}")

def tracer_comparaison_efficacites(speedups_av, speedups_tot):
    plt.figure(figsize=(12, 7))
    
    _, amdahl_av_eff, _, gustafson_av_eff = speedups_av
    _, amdahl_tot_eff, _, gustafson_tot_eff = speedups_tot
    
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
    
    output_file = os.path.join(EFFICIENCY_DIR, "efficacite_comparaison.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de comparaison des efficacités sauvegardé dans {output_file}")

def tracer_performance_par_timestep():
    amdahl_dir = "amdahl_500"
    amdahl_path = os.path.join(BASE_DIR, amdahl_dir)
    
    plt.figure(figsize=(12, 7))
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown']
    
    thread_dirs = [d for d in os.listdir(amdahl_path) if d.startswith("threads_")]
    for i, thread_dir in enumerate(sorted(thread_dirs, key=lambda x: int(x.split("_")[1]))):
        thread_path = os.path.join(amdahl_path, thread_dir)
        thread_count = thread_dir.split("_")[1]
        
        csv_files = glob.glob(os.path.join(thread_path, "*.csv"))
        
        if csv_files:
            all_dfs = []
            for csv_file in csv_files:
                df = pd.read_csv(csv_file)
                all_dfs.append(df)
            
            if all_dfs:
                combined_df = pd.concat(all_dfs)
                avg_df = combined_df.groupby('TimeStep').mean().reset_index()
                
                plt.plot(avg_df['TimeStep'], avg_df['T_avancement'], 
                         linewidth=2, color=colors[i % len(colors)], 
                         label=f'{thread_count} threads')
    
    plt.xlabel('Pas de Temps (TimeStep)')
    plt.ylabel('Temps de Calcul (secondes)')
    plt.title(f'Performance par Timestep - Amdahl (Taille=500)')
    plt.grid(True)
    plt.legend()
    
    output_file = os.path.join(PERF_DIR, f"{amdahl_dir}_performance_timestep.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de performance Amdahl sauvegardé dans {output_file}")
    
    gustafson_dir = "gustafson_204"
    gustafson_path = os.path.join(BASE_DIR, gustafson_dir)
    
    plt.figure(figsize=(12, 7))
    
    thread_dirs = [d for d in os.listdir(gustafson_path) if d.startswith("threads_")]
    for i, thread_dir in enumerate(sorted(thread_dirs, key=lambda x: int(x.split("_")[1]))):
        thread_path = os.path.join(gustafson_path, thread_dir)
        parts = thread_dir.split("_")
        thread_count = parts[1]
        size = parts[3] if len(parts) > 3 else "?"
        
        csv_files = glob.glob(os.path.join(thread_path, "*.csv"))
        
        if csv_files:
            all_dfs = []
            for csv_file in csv_files:
                df = pd.read_csv(csv_file)
                all_dfs.append(df)
            
            if all_dfs:
                combined_df = pd.concat(all_dfs)
                avg_df = combined_df.groupby('TimeStep').mean().reset_index()
                
                plt.plot(avg_df['TimeStep'], avg_df['T_avancement'], 
                         linewidth=2, color=colors[i % len(colors)], 
                         label=f'{thread_count} threads (taille={size})')
    
    plt.xlabel('Pas de Temps (TimeStep)')
    plt.ylabel('Temps de Calcul (secondes)')
    plt.title(f'Performance par Timestep - Gustafson (Base=204)')
    plt.grid(True)
    plt.legend()
    
    output_file = os.path.join(PERF_DIR, f"{gustafson_dir}_performance_timestep.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de performance Gustafson sauvegardé dans {output_file}")

tracer_performance_par_timestep()

resultats_av = calculer_speedup_et_efficacite("T_avancement")

resultats_tot = calculer_speedup_et_efficacite("T_total")

tracer_speedup(resultats_av[0], resultats_av[2], "T_avancement")
tracer_speedup(resultats_tot[0], resultats_tot[2], "T_total")

tracer_efficacite(resultats_av[1], resultats_av[3], "T_avancement")
tracer_efficacite(resultats_tot[1], resultats_tot[3], "T_total")

tracer_comparaison_speedups(resultats_av, resultats_tot)
tracer_comparaison_efficacites(resultats_av, resultats_tot)

print("\nAnalyse terminée avec succès!")
print(f"Tous les graphiques ont été sauvegardés dans les sous-répertoires de {RESULTS_DIR}")