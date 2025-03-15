#!/bin/bash
# Vérifie si le bon nombre d'arguments a été fourni
if [ "$#" -lt 3 ]; then
    echo "Utilisation : $0 <N_EXEC> <THREADS_LIST> <N_GUSTAFSON>"
    echo "Exemple : $0 5 \"1 2 4 8\" 50"
    exit 1
fi

# Paramètres
N_EXEC=$1
THREADS_LIST=($2) # Convertit en tableau
N_GUSTAFSON=$3

# Nom du script à appeler
TEST_SCRIPT="./run_tests.sh"

# Répertoire principal
TEST_DIR="tests"
GUSTAFSON_DIR="$TEST_DIR/gustafson_${N_GUSTAFSON}"

# Création du répertoire pour Gustafson
mkdir -p "$GUSTAFSON_DIR"

# Exécution selon la loi de Gustafson (n proportionnel à la racine carrée du nombre de threads)
echo "Exécution des tests selon la loi de Gustafson (n proportionnel à la racine carrée du nombre de threads)"

for THREADS in "${THREADS_LIST[@]}"; do
    # Calcul de la racine carrée avec Python (très précis)
    ADJUSTED_SIZE=$(python3.10 -c "import math; print(round($N_GUSTAFSON * math.sqrt($THREADS)))")
    
    echo "→ Gustafson : $THREADS threads avec n = $ADJUSTED_SIZE (racine carrée de $THREADS = $SQRT_THREADS_PRECISE, arrondi à $SQRT_THREADS)"
    $TEST_SCRIPT $N_EXEC "$THREADS" $ADJUSTED_SIZE "$GUSTAFSON_DIR"
done

echo "Tests Gustafson terminés !"