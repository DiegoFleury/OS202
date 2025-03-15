#!/bin/bash

# Vérifie si le bon nombre d'arguments a été fourni
if [ "$#" -lt 3 ]; then
    echo "Utilisation : $0 <N_EXEC> <TAILLE> <REPERTOIRE_SORTIE>"
    echo "Exemple : $0 5 50 tests_50/sequentiel"
    exit 1
fi

# Paramètres
N_EXEC=$1
TAILLE=$2
REPERTOIRE_SORTIE=$3  # Répertoire cible

# Création du répertoire de sortie si nécessaire
mkdir -p "$REPERTOIRE_SORTIE"

# Exécuter le programme N_EXEC fois
for i in $(seq 1 $N_EXEC); do
    echo "Exécution $i/$N_EXEC avec taille $TAILLE..."
    
    # Exécuter le programme avec la taille spécifiée et rediriger la sortie
    ./simulation.bin -n $TAILLE > /dev/null 2>&1
    
    # Vérifier si l'exécution a réussi
    if [ $? -ne 0 ]; then
        echo "Erreur : L'exécution de ./programme a échoué à l'itération $i !"
        continue
    fi

    # Vérifier si le fichier est bien généré avec une boucle d'attente
    FICHIER_CSV="resultats_temps.csv"
    FICHIER_RENOMME="$REPERTOIRE_SORTIE/resultats_temps_v${i}.csv"
    ATTEMPTS=5
    while [ ! -f "$FICHIER_CSV" ] && [ $ATTEMPTS -gt 0 ]; do
        sleep 0.5  # Attente courte avant de vérifier à nouveau
        ATTEMPTS=$((ATTEMPTS - 1))
    done

    if [ -f "$FICHIER_CSV" ]; then
        mv "$FICHIER_CSV" "$FICHIER_RENOMME"
    else
        echo "Attention : Le fichier $FICHIER_CSV n'a pas été trouvé après l'exécution $i !"
    fi
done

echo "Tests terminés pour $REPERTOIRE_SORTIE !"