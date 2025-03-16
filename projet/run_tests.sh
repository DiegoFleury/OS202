#!/bin/bash
# Vérifie si le bon nombre d'arguments a été fourni
if [ "$#" -lt 3 ]; then
    echo "Utilisation : $0 <N_EXEC> <THREAD_LIST> <SIZE_LIST> <OUTPUT_DIR>"
    echo "Exemple : $0 5 \"1 2 4 8\" \"50 100 200 500\" tests_openmp/"
    exit 1
fi

# Paramètres
N_EXEC=$1
THREAD_LIST=($2)  # Liste des nombres de threads
SIZE_LIST=($3)    # Liste des tailles d'entrée
OUTPUT_DIR=$4     # Répertoire cible

# Création du répertoire de sortie si nécessaire
mkdir -p "$OUTPUT_DIR"

# Variable d'environnement pour exécuter SDL sans affichage (optionnel, décommenter si nécessaire)
# export SDL_VIDEODRIVER=dummy

# Boucle sur chaque taille d'entrée et chaque nombre de threads
for SIZE in "${SIZE_LIST[@]}"; do
    for THREADS in "${THREAD_LIST[@]}"; do
        echo "Exécution des tests pour taille $SIZE avec $THREADS thread(s)..."
        
        # Création du sous-dossier correspondant à la taille et au nombre de threads
        DIR="$OUTPUT_DIR/size_${SIZE}_threads_${THREADS}"
        mkdir -p "$DIR"
        
        # Exécuter le binaire N_EXEC fois
        for i in $(seq 1 $N_EXEC); do
            echo "Exécution $i/$N_EXEC pour taille $SIZE avec $THREADS thread(s)..."
            
            # Exécuter le binaire avec les bons paramètres et --bind-to none
            make run OMP_NUM_THREADS=$THREADS ARGS="-n $SIZE"
            
            # Vérifier si le fichier CSV a été généré
            if [ -f "timing_results.csv" ]; then
                mv "timing_results.csv" "$DIR/timing_results_size${SIZE}_threads${THREADS}_v${i}.csv"
                echo "Fichier CSV déplacé avec succès vers $DIR/timing_results_size${SIZE}_threads${THREADS}_v${i}.csv"
            else
                echo "Attention : Le fichier timing_results.csv n'a pas été trouvé après l'exécution !"
            fi
            
            # Petit délai pour éviter les conflits
            sleep 1
        done
    done
done

echo "Tests terminés pour $OUTPUT_DIR !"

