import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob

BASE_DIR = "tests"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
SPEEDUP_SEQ_DIR = os.path.join(RESULTS_DIR, "speedup_sequentiel")
EFFICACITE_SEQ_DIR = os.path.join(RESULTS_DIR, "efficacite_sequentiel")
SEQ_DIR = os.path.join(RESULTS_DIR, "tests_sequentiel")

os.makedirs(SPEEDUP_SEQ_DIR, exist_ok=True)
os.makedirs(EFFICACITE_SEQ_DIR, exist_ok=True)

def corriger_et_obtenir_temps_sequentiels():
    temps_sequentiels = {}
    seq_files = glob.glob(os.path.join(SEQ_DIR, "resultats_temps_v*.csv"))
    
    if not seq_files:
        print(f"Aucun fichier trouvé dans {SEQ_DIR} correspondant à 'resultats_temps_v*.csv'")
        print(f"Fichiers disponibles: {os.listdir(SEQ_DIR)}")
    
    for seq_file in seq_files:
        version = os.path.basename(seq_file).split('_v')[1].split('.')[0]
        print(f"Traitement du fichier {seq_file}, version {version}")
        
        try:
            df = pd.read_csv(seq_file)
            print(f"Colonnes dans {os.path.basename(seq_file)}: {df.columns.tolist()}")
            
            if 'T_avancement' in df.columns and 'T_total' in df.columns:
                temps_sequentiels[version] = {
                    'T_avancement': df['T_avancement'].mean(),
                    'T_total': df['T_total'].mean()
                }
                print(f"Temps pour version {version}: T_avancement={temps_sequentiels[version]['T_avancement']}, T_total={temps_sequentiels[version]['T_total']}")
            elif 'T avancement' in df.columns and 'T total' in df.columns:
                temps_sequentiels[version] = {
                    'T_avancement': df['T avancement'].mean(),
                    'T_total': df['T total'].mean()
                }
                print(f"Temps pour version {version}: T_avancement={temps_sequentiels[version]['T_avancement']}, T_total={temps_sequentiels[version]['T_total']}")
            else:
                print(f"Format de colonnes non reconnu dans {seq_file}. Tentative de lecture alternative...")
                with open(seq_file, 'r') as f:
                    content = f.read()
                    print(f"Premiers caractères du fichier: {content[:100]}")
                
                if "TimeStep,T_avancement,T_affichage,T_total" in content:
                    df = pd.read_csv(seq_file, skipinitialspace=True)
                    if 'T_avancement' in df.columns and 'T_total' in df.columns:
                        temps_sequentiels[version] = {
                            'T_avancement': df['T_avancement'].mean(),
                            'T_total': df['T_total'].mean()
                        }
                        print(f"Lecture réussie! Temps pour version {version}: T_avancement={temps_sequentiels[version]['T_avancement']}, T_total={temps_sequentiels[version]['T_total']}")
                    else:
                        print(f"Colonnes après relecture: {df.columns.tolist()}")
                elif "," in content:
                    df = pd.read_csv(seq_file, skipinitialspace=True)
                    col_names = df.columns.tolist()
                    av_col = next((col for col in col_names if "avancement" in col.lower()), None)
                    tot_col = next((col for col in col_names if "total" in col.lower()), None)
                    
                    if av_col and tot_col:
                        temps_sequentiels[version] = {
                            'T_avancement': df[av_col].mean(),
                            'T_total': df[tot_col].mean()
                        }
                        print(f"Colonnes trouvées: {av_col} et {tot_col}")
                        print(f"Temps pour version {version}: T_avancement={temps_sequentiels[version]['T_avancement']}, T_total={temps_sequentiels[version]['T_total']}")
        except Exception as e:
            print(f"Erreur lors de la lecture de {seq_file}: {str(e)}")
            
    if not temps_sequentiels:
        print("ATTENTION: Aucun temps séquentiel trouvé! Utilisation de valeurs par défaut.")
        try:
            with open(os.path.join(SEQ_DIR, "resultats_temps_v1.csv"), 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    header = lines[0].strip().split(',')
                    values = []
                    for i in range(1, min(10, len(lines))):
                        values.append(lines[i].strip().split(','))
                    print(f"En-tête: {header}")
                    print(f"Quelques valeurs: {values[:3]}")
                    
                    av_idx = -1
                    tot_idx = -1
                    for i, col in enumerate(header):
                        if 'avancement' in col.lower():
                            av_idx = i
                        if 'total' in col.lower():
                            tot_idx = i
                    
                    if av_idx >= 0 and tot_idx >= 0:
                        print(f"Indices de colonnes: avancement={av_idx}, total={tot_idx}")
                        av_values = []
                        tot_values = []
                        for val_row in values:
                            if len(val_row) > max(av_idx, tot_idx):
                                try:
                                    av_values.append(float(val_row[av_idx]))
                                    tot_values.append(float(val_row[tot_idx]))
                                except ValueError:
                                    pass
                        
                        if av_values and tot_values:
                            temps_sequentiels['1'] = {
                                'T_avancement': np.mean(av_values),
                                'T_total': np.mean(tot_values)
                            }
                            print(f"Valeurs extraites manuellement: T_avancement={temps_sequentiels['1']['T_avancement']}, T_total={temps_sequentiels['1']['T_total']}")
        except Exception as e:
            print(f"Erreur lors de l'extraction manuelle: {str(e)}")
        
        if not temps_sequentiels:
            temps_sequentiels['1'] = {'T_avancement': 0.01, 'T_total': 0.02}
    
    return temps_sequentiels

def calculer_speedup_parallele(temps_type="T_avancement"):
    temps_seq = corriger_et_obtenir_temps_sequentiels()
    
    if '1' in temps_seq and temps_type in temps_seq['1']:
        t_seq = temps_seq['1'][temps_type]
    else:
        t_seq = np.mean([temps[temps_type] for temps in temps_seq.values() if temps_type in temps])
    
    print(f"Temps séquentiel de référence pour {temps_type}: {t_seq}")
    
    amdahl_dir = "amdahl_500"
    amdahl_path = os.path.join(BASE_DIR, amdahl_dir)
    
    amdahl_thread_dirs = [d for d in os.listdir(amdahl_path) if d.startswith("threads_")]
    amdahl_thread_dirs = sorted(amdahl_thread_dirs, key=lambda x: int(x.split("_")[1]))
    
    amdahl_speedups = []
    
    for thread_dir in amdahl_thread_dirs:
        thread_count = int(thread_dir.split("_")[1])
        thread_path = os.path.join(amdahl_path, thread_dir)
        
        csv_files = glob.glob(os.path.join(thread_path, "*.csv"))
        all_times = []
        
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            all_times.append(df[temps_type].mean())
        
        if all_times:
            avg_time = np.mean(all_times)
            speedup = t_seq / avg_time
            amdahl_speedups.append((thread_count, speedup))
    
    gustafson_dir = "gustafson_204"
    gustafson_path = os.path.join(BASE_DIR, gustafson_dir)
    
    gustafson_thread_dirs = [d for d in os.listdir(gustafson_path) if d.startswith("threads_")]
    gustafson_thread_dirs = sorted(gustafson_thread_dirs, key=lambda x: int(x.split("_")[1]))
    
    gustafson_speedups = []
    
    for thread_dir in gustafson_thread_dirs:
        thread_count = int(thread_dir.split("_")[1])
        thread_path = os.path.join(gustafson_path, thread_dir)
        
        csv_files = glob.glob(os.path.join(thread_path, "*.csv"))
        all_times = []
        
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            all_times.append(df[temps_type].mean())
        
        if all_times:
            avg_time = np.mean(all_times)
            speedup = t_seq / (avg_time / thread_count)
            gustafson_speedups.append((thread_count, speedup))
    
    return amdahl_speedups, gustafson_speedups

def tracer_speedup_comparaison(temps_type="T_avancement"):
    amdahl_speedups, gustafson_speedups = calculer_speedup_parallele(temps_type)
    
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
    plt.title(f'Comparaison des Speedups basés sur {temps_label} (réf: temps séquentiel)')
    plt.grid(True)
    plt.legend()
    
    output_file = os.path.join(SPEEDUP_SEQ_DIR, f"speedup_seq_comparaison_{temps_type.lower()[2:]}.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de comparaison des speedups ({temps_label}) sauvegardé dans {output_file}")

def tracer_efficacite_comparaison(temps_type="T_avancement"):
    amdahl_speedups, gustafson_speedups = calculer_speedup_parallele(temps_type)
    
    amdahl_efficiencies = [(p, s/p) for p, s in amdahl_speedups] if amdahl_speedups else []
    gustafson_efficiencies = [(p, s/p) for p, s in gustafson_speedups] if gustafson_speedups else []
    
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
    plt.title(f'Comparaison des Efficacités basées sur {temps_label} (réf: temps séquentiel)')
    plt.grid(True)
    plt.legend()
    
    output_file = os.path.join(EFFICACITE_SEQ_DIR, f"efficacite_seq_comparaison_{temps_type.lower()[2:]}.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de comparaison des efficacités ({temps_label}) sauvegardé dans {output_file}")

def tracer_speedup_combine():
    amdahl_speedups_av, gustafson_speedups_av = calculer_speedup_parallele("T_avancement")
    amdahl_speedups_tot, gustafson_speedups_tot = calculer_speedup_parallele("T_total")
    
    plt.figure(figsize=(12, 7))
    
    if amdahl_speedups_av:
        amdahl_threads_av = [x[0] for x in amdahl_speedups_av]
        amdahl_values_av = [x[1] for x in amdahl_speedups_av]
        plt.plot(amdahl_threads_av, amdahl_values_av, 'o-', linewidth=2, color='blue', 
                label='Amdahl - Temps d\'Avancement')
    
    if amdahl_speedups_tot:
        amdahl_threads_tot = [x[0] for x in amdahl_speedups_tot]
        amdahl_values_tot = [x[1] for x in amdahl_speedups_tot]
        plt.plot(amdahl_threads_tot, amdahl_values_tot, 'o-', linewidth=2, color='lightblue', 
                label='Amdahl - Temps Total')
    
    if gustafson_speedups_av:
        gustafson_threads_av = [x[0] for x in gustafson_speedups_av]
        gustafson_values_av = [x[1] for x in gustafson_speedups_av]
        plt.plot(gustafson_threads_av, gustafson_values_av, 's--', linewidth=2, color='red', 
                label='Gustafson - Temps d\'Avancement')
    
    if gustafson_speedups_tot:
        gustafson_threads_tot = [x[0] for x in gustafson_speedups_tot]
        gustafson_values_tot = [x[1] for x in gustafson_speedups_tot]
        plt.plot(gustafson_threads_tot, gustafson_values_tot, 's--', linewidth=2, color='salmon', 
                label='Gustafson - Temps Total')
    
    plt.xlabel('Nombre de threads')
    plt.ylabel('Speedup')
    plt.title('Comparaison des Speedups: Temps d\'Avancement vs. Temps Total')
    plt.grid(True)
    plt.legend()
    
    output_file = os.path.join(SPEEDUP_SEQ_DIR, "speedup_comparaison.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de comparaison des speedups combinés sauvegardé dans {output_file}")

def tracer_efficacite_combine():
    amdahl_speedups_av, gustafson_speedups_av = calculer_speedup_parallele("T_avancement")
    amdahl_speedups_tot, gustafson_speedups_tot = calculer_speedup_parallele("T_total")
    
    amdahl_efficiencies_av = [(p, s/p) for p, s in amdahl_speedups_av] if amdahl_speedups_av else []
    amdahl_efficiencies_tot = [(p, s/p) for p, s in amdahl_speedups_tot] if amdahl_speedups_tot else []
    gustafson_efficiencies_av = [(p, s/p) for p, s in gustafson_speedups_av] if gustafson_speedups_av else []
    gustafson_efficiencies_tot = [(p, s/p) for p, s in gustafson_speedups_tot] if gustafson_speedups_tot else []
    
    plt.figure(figsize=(12, 7))
    
    if amdahl_efficiencies_av:
        amdahl_threads_av = [x[0] for x in amdahl_efficiencies_av]
        amdahl_values_av = [x[1] for x in amdahl_efficiencies_av]
        plt.plot(amdahl_threads_av, amdahl_values_av, 'o-', linewidth=2, color='blue', 
                label='Amdahl - Temps d\'Avancement')
    
    if amdahl_efficiencies_tot:
        amdahl_threads_tot = [x[0] for x in amdahl_efficiencies_tot]
        amdahl_values_tot = [x[1] for x in amdahl_efficiencies_tot]
        plt.plot(amdahl_threads_tot, amdahl_values_tot, 'o-', linewidth=2, color='lightblue', 
                label='Amdahl - Temps Total')
    
    if gustafson_efficiencies_av:
        gustafson_threads_av = [x[0] for x in gustafson_efficiencies_av]
        gustafson_values_av = [x[1] for x in gustafson_efficiencies_av]
        plt.plot(gustafson_threads_av, gustafson_values_av, 's--', linewidth=2, color='red', 
                label='Gustafson - Temps d\'Avancement')
    
    if gustafson_efficiencies_tot:
        gustafson_threads_tot = [x[0] for x in gustafson_efficiencies_tot]
        gustafson_values_tot = [x[1] for x in gustafson_efficiencies_tot]
        plt.plot(gustafson_threads_tot, gustafson_values_tot, 's--', linewidth=2, color='salmon', 
                label='Gustafson - Temps Total')
    
    plt.xlabel('Nombre de threads')
    plt.ylabel('Efficacité')
    plt.title('Comparaison des Efficacités: Temps d\'Avancement vs. Temps Total')
    plt.grid(True)
    plt.legend()
    
    output_file = os.path.join(EFFICACITE_SEQ_DIR, "efficacite_comparaison.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graphique de comparaison des efficacités combinées sauvegardé dans {output_file}")

print("Analyse du speedup avec temps séquentiels...")
tracer_speedup_comparaison("T_avancement")
tracer_efficacite_comparaison("T_avancement")
tracer_speedup_comparaison("T_total")
tracer_efficacite_comparaison("T_total")
tracer_speedup_combine()
tracer_efficacite_combine()
print("\nAnalyse terminée avec succès!")
print(f"Graphiques de speedup sauvegardés dans {SPEEDUP_SEQ_DIR}")
print(f"Graphiques d'efficacité sauvegardés dans {EFFICACITE_SEQ_DIR}")