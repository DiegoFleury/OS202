#!/bin/bash
# Vérifie si le bon nombre d'arguments a été fourni
if [ "$#" -lt 3 ]; then
    echo "Utilisation : $0 <N_EXEC> <SIZE_LIST> <OUTPUT_DIR>"
    echo "Exemple : $0 5 \"50 100 200 500\" tests_mpi/"
    exit 1
fi

# Paramètres
N_EXEC=$1
SIZE_LIST=($2)  # Liste des tailles d'entrée
OUTPUT_DIR=$3   # Répertoire cible

# Nombre fixe de processus (toujours 2)
PROC=2

# Création du répertoire de sortie si nécessaire
mkdir -p "$OUTPUT_DIR"

# Variable d'environnement pour exécuter SDL sans affichage
#export SDL_VIDEODRIVER=dummy

# Boucle sur chaque taille d'entrée
for SIZE in "${SIZE_LIST[@]}"; do
    echo "Exécution des tests pour taille $SIZE avec $PROC processus..."
    
    # Création du sous-dossier correspondant à la taille
    DIR="$OUTPUT_DIR/size_$SIZE"
    mkdir -p "$DIR"
    
    # Exécuter le binaire N_EXEC fois
    for i in $(seq 1 $N_EXEC); do
        echo "Exécution $i/$N_EXEC pour taille $SIZE avec $PROC processus..."
        
        # Exécuter le binaire en utilisant make run avec les bons paramètres
        make run NPROCS=$PROC ARGS="-n $SIZE"
        
        # Vérifier si le fichier CSV a été généré
        if [ -f "timing_results.csv" ]; then
            mv "timing_results.csv" "$DIR/timing_results_size${SIZE}_v${i}.csv"
            echo "Fichier CSV déplacé avec succès vers $DIR/timing_results_size${SIZE}_v${i}.csv"
        else
            echo "Attention : Le fichier timing_results.csv n'a pas été trouvé après l'exécution !"
        fi
        
        # Petit délai pour éviter les conflits
        sleep 1
    done
done

echo "Tests terminés pour $OUTPUT_DIR !"