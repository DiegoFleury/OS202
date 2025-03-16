# Guide d'Exécution des Tests

Ce document explique comment exécuter les scripts de test pour évaluer les performances du code selon les lois d'Amdahl et de Gustafson.

## Prérequis

Assurez-vous que tous les scripts ont les permissions d'exécution nécessaires :

```bash
chmod +x run_tests.sh run_amdahl.sh run_gustafson.sh
```

## Structure des Tests

Les tests sont organisés de la façon suivante :
- `run_tests.sh` est le script de base utilisé par les autres scripts
- `run_amdahl.sh` exécute les tests selon la loi d'Amdahl
- `run_gustafson.sh` exécute les tests selon la loi de Gustafson

## Exécution des Tests d'Amdahl

Le script `run_amdahl.sh` nécessite trois paramètres :

```bash
./run_amdahl.sh <N_EXEC> <THREADS_LIST> <N_AMDAHL>
```

Où :
- `<N_EXEC>` : Nombre d'échantillons à exécuter pour chaque test
- `<THREADS_LIST>` : Liste des nombres de threads à tester (entre guillemets, séparés par des espaces)
- `<N_AMDAHL>` : Taille du problème à résoudre (fixe quelle que soit la parallélisation)

Exemple :
```bash
./run_amdahl.sh 5 "1 2 4 8" 500
```
Cette commande exécutera 5 tests pour chaque configuration de threads (1, 2, 4 et 8), avec une taille de problème fixe de 500.

## Exécution des Tests de Gustafson

Le script `run_gustafson.sh` nécessite également trois paramètres :

```bash
./run_gustafson.sh <N_EXEC> <THREADS_LIST> <N_GUSTAFSON>
```

Où :
- `<N_EXEC>` : Nombre d'échantillons à exécuter pour chaque test
- `<THREADS_LIST>` : Liste des nombres de threads à tester (entre guillemets, séparés par des espaces)
- `<N_GUSTAFSON>` : Côté de la grille pour `<N_THREADS> = 1`

**Important :** Dans les tests de Gustafson, la taille du problème augmente avec la racine carrée du nombre de threads.

Exemple :
```bash
./run_gustafson.sh 5 "1 2 4 8" 50
```
Cette commande exécutera 5 tests pour chaque configuration de threads, en commençant avec une grille de taille 50×50 pour 1 thread, puis en augmentant la taille proportionnellement à la racine carrée du nombre de threads.

## Analyse des Résultats

Une fois les tests exécutés, vous pouvez utiliser les scripts Python pour analyser les résultats. Ces scripts sont simples à exécuter et ne nécessitent aucun argument. Assurez-vous simplement que les scripts de test (`run_amdahl.sh` et/ou `run_gustafson.sh`) ont été exécutés au préalable.

Les scripts d'analyse sont :

- `plot.py` : Génère des graphiques montrant la moyenne des `<N_EXEC>` exécutions au long des itérations
- `speedup.py` : Calcule et affiche les graphiques des accélérations (speedups) obtenues lors des tests

Exemple :
```bash
python3 plot.py
python3 speedup.py
```

## Remarque

Le dossier `tests_sequentiel` a été ajouté manuellement à partir de la branche `sequentiel`. Il contient des données de référence pour comparer les performances.