#!/bin/bash

# Vérifie si le bon nombre d'arguments a été fourni
if [ "$#" -lt 3 ]; then
    echo "Utilisation : $0 <N_EXEC> <THREADS_LIST> <SIZE>"
    echo "Exemple : $0 5 \"1 2 4 8\" 50"
    exit 1
fi

# Paramètres
N_EXEC=$1
THREADS_LIST=($2)  # Convertit en tableau
BASE_SIZE=$3

# Nom du script à appeler
TEST_SCRIPT="./run_tests.sh"

# Répertoires principaux
TEST_DIR="tests_${BASE_SIZE}"
AMDAL_DIR="$TEST_DIR/amdal"
GUSTAFSON_DIR="$TEST_DIR/gustafson"

# Création des répertoires pour Amdahl et Gustafson
mkdir -p "$AMDAL_DIR"
mkdir -p "$GUSTAFSON_DIR"

# Exécution selon la loi d'Amdahl (n constant)
echo "Exécution des tests selon la loi d'Amdahl (n = $BASE_SIZE constant)"
for THREADS in "${THREADS_LIST[@]}"; do
    echo "→ Amdahl : $THREADS threads avec n = $BASE_SIZE"
    $TEST_SCRIPT $N_EXEC "$THREADS" $BASE_SIZE "$AMDAL_DIR"
done

# Exécution selon la loi de Gustafson (n proportionnel aux threads)
echo "Exécution des tests selon la loi de Gustafson (n proportionnel aux threads)"
for THREADS in "${THREADS_LIST[@]}"; do
    ADJUSTED_SIZE=$(( BASE_SIZE * THREADS ))
    echo "→ Gustafson : $THREADS threads avec n = $ADJUSTED_SIZE"
    $TEST_SCRIPT $N_EXEC "$THREADS" $ADJUSTED_SIZE "$GUSTAFSON_DIR"
done

echo "Tous les tests de scaling ont été effectués !"
