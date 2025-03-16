# Guide d'Exécution des Tests

Ce document explique comment exécuter les scripts de test pour évaluer les performances du code avec différentes tailles de grille.

## Prérequis

Assurez-vous que tous les scripts ont les permissions d'exécution nécessaires :

```bash
chmod +x run_tests.sh
```

## Structure des Tests

Les tests sont organisés de la façon suivante :
- `run_tests.sh` est le script principal qui exécute les tests avec différentes tailles de grille
- Le dossier `tests` contient les résultats organisés par taille (size_100, size_200, etc.)

## Exécution des Tests

Le script `run_tests.sh` nécessite trois paramètres :

```bash
./run_tests.sh <N_EXEC> <SIZE_LIST> <OUTPUT_DIR>
```

Où :
- `<N_EXEC>` : Nombre d'échantillons à exécuter pour chaque taille
- `<SIZE_LIST>` : Liste des tailles de grille à tester (entre guillemets, séparées par des espaces)
- `<OUTPUT_DIR>` : Répertoire où stocker les résultats des tests

Exemple :
```bash
./run_tests.sh 5 "50 100 200 500" tests_mpi/
```
Cette commande exécutera 5 tests pour chaque taille de grille (50×50, 100×100, 200×200 et 500×500), et stockera les résultats dans le répertoire `tests_mpi/`.

## Analyse des Résultats

Une fois les tests exécutés, vous pouvez utiliser le script Python pour analyser les résultats. Ce script est simple à exécuter et ne nécessite aucun argument. Assurez-vous simplement que le script de test (`run_tests.sh`) a été exécuté au préalable.

Le script d'analyse est :

- `plot.py` : Génère des graphiques montrant la moyenne des `<N_EXEC>` exécutions au long des itérations pour chaque taille de grille

Exemple :
```bash
python3 plot.py
```