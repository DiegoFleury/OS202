import pandas as pd
import matplotlib.pyplot as plt

def plot_timing_results(csv_file):
    # Charger les données depuis le fichier CSV
    df = pd.read_csv(csv_file)
    
    # Vérifier que les colonnes attendues sont bien présentes
    if not {'TimeStep', 'T_avancement', 'T_affichage', 'T_total'}.issubset(df.columns):
        raise ValueError("Le fichier CSV ne contient pas les colonnes attendues.")
    
    # Calculer la moyenne et l'écart-type pour chaque mesure
    mean_avancement = df['T_avancement'].mean()
    std_avancement = df['T_avancement'].std()
    mean_affichage = df['T_affichage'].mean()
    std_affichage = df['T_affichage'].std()
    mean_total = df['T_total'].mean()
    std_total = df['T_total'].std()
    
    # Afficher les statistiques calculées
    print(f"Moyenne et écart-type des temps mesurés:")
    print(f"T_avancement - Moyenne: {mean_avancement:.6f} s, Écart-type: {std_avancement:.6f} s")
    print(f"T_affichage - Moyenne: {mean_affichage:.6f} s, Écart-type: {std_affichage:.6f} s")
    print(f"T_total - Moyenne: {mean_total:.6f} s, Écart-type: {std_total:.6f} s")
    
    # Tracer les courbes des temps mesurés
    plt.figure(figsize=(10, 5))
    plt.plot(df['TimeStep'], df['T_avancement'], label='Temps avancement', color='blue')
    plt.plot(df['TimeStep'], df['T_affichage'], label='Temps affichage', color='green')
    plt.plot(df['TimeStep'], df['T_total'], label='Temps total', color='red')
    
    # Personnalisation du graphique
    plt.xlabel("Itérations (TimeStep)")
    plt.ylabel("Temps (secondes)")
    plt.title("Évolution des temps d'exécution au cours de la simulation")
    plt.legend()
    plt.grid()
    
    # Afficher le graphique
    plt.savefig(csv_file + ".png")
    # plt.show()

plot_timing_results("timing_results.csv")
# plot_timing_results("timing_results_1.csv")
# plot_timing_results("timing_results_2.csv")
# plot_timing_results("timing_results_3.csv")
# plot_timing_results("timing_results_4.csv")
