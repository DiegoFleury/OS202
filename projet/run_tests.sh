#!/bin/bash

# Vérifie si le bon nombre d'arguments a été fourni
if [ "$#" -lt 4 ]; then
    echo "Utilisation : $0 <N_EXEC> <THREADS_LIST> <SIZE> <OUTPUT_DIR>"
    echo "Exemple : $0 5 \"1 2 4 8\" 50 tests_50/amdal"
    exit 1
fi

# Paramètres
N_EXEC=$1
THREADS_LIST=($2)
SIZE=$3
OUTPUT_DIR=$4  # Nouveau paramètre pour spécifier le répertoire cible

# Nom du binaire (modifiez si nécessaire)
BINARIO="./simulation.bin"

# Création du répertoire de sortie si nécessaire
mkdir -p "$OUTPUT_DIR"

# Boucle sur chaque configuration de threads
for THREADS in "${THREADS_LIST[@]}"; do
    echo "Exécution des tests pour $THREADS threads avec taille $SIZE..."
    
    # Création du sous-dossier correspondant au nombre de threads
    DIR="$OUTPUT_DIR/$THREADS"
    mkdir -p "$DIR"

    # Exécuter le binaire N_EXEC fois
    for i in $(seq 1 $N_EXEC); do
        echo "Exécution $i/$N_EXEC pour $THREADS threads avec taille $SIZE..."
        
        # Définir le nombre de threads dans OpenMP
        export OMP_NUM_THREADS=$THREADS

        # Exécuter le binaire avec la taille spécifiée et rediriger la sortie
        $BINARIO -n $SIZE > /dev/null 2>&1

        # Renommer et déplacer le fichier généré
        CSV_FILE="timing_results_${THREADS}_threads.csv"
        if [ -f "$CSV_FILE" ]; then
            mv "$CSV_FILE" "$DIR/timing_results_${THREADS}_threads_v${i}.csv"
        else
            echo "Attention : Le fichier $CSV_FILE n'a pas été trouvé après l'exécution !"
        fi
    done
done

echo "Tests terminés pour $OUTPUT_DIR !"
