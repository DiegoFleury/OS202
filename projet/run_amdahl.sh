#!/bin/bash
# Vérifie si le bon nombre d'arguments a été fourni
if [ "$#" -lt 3 ]; then
    echo "Utilisation : $0 <N_EXEC> <THREADS_LIST> <N_AMDAHL>"
    echo "Exemple : $0 5 \"1 2 4 8\" 500"
    exit 1
fi

# Paramètres
N_EXEC=$1
THREADS_LIST=$2
N_AMDAHL=$3

# Répertoire principal pour les résultats
OUTPUT_DIR="tests/amdahl_${N_AMDAHL}"
mkdir -p "$OUTPUT_DIR"

# Exécution selon la loi d'Amdahl (n constant)
echo "Exécution des tests selon la loi d'Amdahl (n = $N_AMDAHL constant)"

# Pour chaque nombre de threads
for THREADS in $THREADS_LIST; do
    echo "→ Amdahl : $THREADS threads avec n = $N_AMDAHL"
    
    # Création du sous-dossier pour cette configuration
    DIR="$OUTPUT_DIR/threads_${THREADS}"
    mkdir -p "$DIR"
    
    # Exécuter le test N_EXEC fois
    for i in $(seq 1 $N_EXEC); do
        echo "Exécution $i/$N_EXEC pour $THREADS threads avec taille $N_AMDAHL..."
        
        # Exécuter la simulation avec le nombre de threads et la taille spécifiés
        make run OMP_NUM_THREADS=$THREADS ARGS="-n $N_AMDAHL"
        
        # Vérifier si le fichier CSV a été généré
        if [ -f "timing_results.csv" ]; then
            mv "timing_results.csv" "$DIR/timing_results_threads${THREADS}_v${i}.csv"
            echo "Fichier CSV déplacé avec succès vers $DIR"
        else
            echo "Attention : Le fichier timing_results.csv n'a pas été trouvé après l'exécution !"
        fi
        
        # Petit délai pour éviter les conflits
        sleep 1
    done
done

echo "Tests Amdahl terminés ! Résultats dans $OUTPUT_DIR"

# Analyse des résultats
echo "Analyse des résultats d'Amdahl..."
echo ""
echo "Threads | Temps moyen (s) | Accélération"
echo "--------|-----------------|-------------"

# Calculer le temps avec 1 thread (référence)
BASE_DIR="$OUTPUT_DIR/threads_1"
BASE_TIME=0
BASE_COUNT=0

for FILE in "$BASE_DIR"/*.csv; do
    if [ -f "$FILE" ]; then
        # Extraire la moyenne des temps d'avancement (colonne 2)
        AVG_TIME=$(tail -n +2 "$FILE" | awk -F, '{sum+=$2} END {print sum/NR}')
        BASE_TIME=$(echo "$BASE_TIME + $AVG_TIME" | bc -l)
        BASE_COUNT=$((BASE_COUNT + 1))
    fi
done

if [ $BASE_COUNT -gt 0 ]; then
    BASE_TIME=$(echo "scale=6; $BASE_TIME / $BASE_COUNT" | bc -l)
    printf "%-8s| %-16s| %-12s\n" "1" "$BASE_TIME" "1.00"
    
    # Pour chaque nombre de threads (sauf 1)
    for THREADS in $THREADS_LIST; do
        if [ "$THREADS" != "1" ]; then
            DIR="$OUTPUT_DIR/threads_${THREADS}"
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
                SPEEDUP=$(echo "scale=2; $BASE_TIME / $AVG_TIME" | bc -l)
                printf "%-8s| %-16s| %-12s\n" "$THREADS" "$AVG_TIME" "$SPEEDUP"
            else
                printf "%-8s| %-16s| %-12s\n" "$THREADS" "N/A" "N/A"
            fi
        fi
    done
else
    echo "Aucune donnée valide pour 1 thread. Impossible de calculer les accélérations."
fi