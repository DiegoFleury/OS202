#!/bin/bash

# Vérifie si le bon nombre d'arguments a été fourni
if [ "$#" -lt 3 ]; then
    echo "Utilisation : $0 <N_EXEC> <THREADS_LIST> <N_AMDAL>"
    echo "Exemple : $0 5 \"1 2 4 8\" 500"
    exit 1
fi

# Paramètres
N_EXEC=$1
THREADS_LIST=($2)  # Convertit en tableau
N_AMDAL=$3

# Nom du script à appeler
TEST_SCRIPT="./run_tests.sh"

# Répertoire principal
TEST_DIR="tests"
AMDAL_DIR="$TEST_DIR/amdal_${N_AMDAL}"

# Création du répertoire pour Amdahl
mkdir -p "$AMDAL_DIR"

# Exécution selon la loi d'Amdahl (n constant)
echo "Exécution des tests selon la loi d'Amdahl (n = $N_AMDAL constant)"
for THREADS in "${THREADS_LIST[@]}"; do
    echo "→ Amdahl : $THREADS threads avec n = $N_AMDAL"
    $TEST_SCRIPT $N_EXEC "$THREADS" $N_AMDAL "$AMDAL_DIR"
done

echo "Tests Amdahl terminés !"
