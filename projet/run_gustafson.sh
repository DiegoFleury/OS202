#!/bin/bash
# Vérifie si le bon nombre d'arguments a été fourni
if [ "$#" -lt 3 ]; then
    echo "Utilisation : $0 <N_EXEC> <THREADS_LIST> <N_GUSTAFSON>"
    echo "Exemple : $0 5 \"1 2 4 8\" 50"
    exit 1
fi

# Paramètres
N_EXEC=$1
THREADS_LIST=$2
N_GUSTAFSON=$3

# Répertoire principal pour les résultats
OUTPUT_DIR="tests/gustafson_${N_GUSTAFSON}"
mkdir -p "$OUTPUT_DIR"

# Exécution selon la loi de Gustafson (n proportionnel à la racine carrée du nombre de threads)
echo "Exécution des tests selon la loi de Gustafson (n proportionnel à la racine carrée du nombre de threads)"

# Pour chaque nombre de threads
for THREADS in $THREADS_LIST; do
    # Calcul de la taille proportionnelle à la racine carrée du nombre de threads
    ADJUSTED_SIZE=$(python3 -c "import math; print(round($N_GUSTAFSON * math.sqrt($THREADS)))")
    
    echo "→ Gustafson : $THREADS threads avec n = $ADJUSTED_SIZE"
    
    # Création du sous-dossier pour cette configuration
    DIR="$OUTPUT_DIR/threads_${THREADS}_size_${ADJUSTED_SIZE}"
    mkdir -p "$DIR"
    
    # Exécuter le test N_EXEC fois
    for i in $(seq 1 $N_EXEC); do
        echo "Exécution $i/$N_EXEC pour $THREADS threads avec taille $ADJUSTED_SIZE..."
        
        # Exécuter la simulation avec le nombre de threads et la taille spécifiés
        make run OMP_NUM_THREADS=$THREADS ARGS="-n $ADJUSTED_SIZE"
        
        # Vérifier si le fichier CSV a été généré
        if [ -f "timing_results.csv" ]; then
            mv "timing_results.csv" "$DIR/timing_results_threads${THREADS}_size${ADJUSTED_SIZE}_v${i}.csv"
            echo "Fichier CSV déplacé avec succès vers $DIR"
        else
            echo "Attention : Le fichier timing_results.csv n'a pas été trouvé après l'exécution !"
        fi
        
        # Petit délai pour éviter les conflits
        sleep 1
    done
done

echo "Tests Gustafson terminés ! Résultats dans $OUTPUT_DIR"

# Analyse des résultats
echo "Analyse des résultats de Gustafson..."
echo ""
echo "Threads | Taille | Temps moyen (s) | Temps/Taille^2"
echo "--------|--------|-----------------|---------------"

# Pour chaque nombre de threads
for THREADS in $THREADS_LIST; do
    ADJUSTED_SIZE=$(python3 -c "import math; print(round($N_GUSTAFSON * math.sqrt($THREADS)))")
    DIR="$OUTPUT_DIR/threads_${THREADS}_size_${ADJUSTED_SIZE}"
    
    # Calculer la moyenne des temps d'avancement
    TOTAL_TIME=0
    COUNT=0
    
    for FILE in "$DIR"/*.csv; do
        if [ -f "$FILE" ]; then
            # Extraire la moyenne des temps d'avancement (colonne 2)
            AVG_TIME=$(tail -n +2 "$FILE" | awk -F, '{sum+=$2} END {print sum/NR}')
            TOTAL_TIME=$(echo "$TOTAL_TIME + $AVG_TIME" | bc -l)
            COUNT=$((COUNT + 1))
        fi
    done
    
    if [ $COUNT -gt 0 ]; then
        AVG_TIME=$(echo "scale=6; $TOTAL_TIME / $COUNT" | bc -l)
        # Calculer le rapport temps/taille^2 (la complexité du problème augmente en n^2)
        NORMALIZED_TIME=$(echo "scale=6; $AVG_TIME / ($ADJUSTED_SIZE * $ADJUSTED_SIZE)" | bc -l)
        
        printf "%-8s| %-8s| %-16s| %-15s\n" "$THREADS" "$ADJUSTED_SIZE" "$AVG_TIME" "$NORMALIZED_TIME"
    else
        printf "%-8s| %-8s| %-16s| %-15s\n" "$THREADS" "$ADJUSTED_SIZE" "N/A" "N/A"
    fi
done