# Guide d'Exécution des Tests Séquentiels

Ce document explique comment exécuter les scripts de test pour évaluer les performances de la version séquentielle du code.

## Prérequis

Assurez-vous que le script a les permissions d'exécution nécessaires :

```bash
chmod +x run_tests.sh
```

## Structure des Tests

Les tests sont organisés de façon simple :
- `run_tests.sh` est le script principal qui exécute les tests séquentiels
- Le dossier `tests` contient les résultats des tests
- Le script `plot.py` permet de visualiser les résultats

## Exécution des Tests

Le script `run_tests.sh` nécessite trois paramètres :

```bash
./run_tests.sh <N_EXEC> <TAILLE> <REPERTOIRE_SORTIE>
```

Où :
- `<N_EXEC>` : Nombre d'échantillons à exécuter
- `<TAILLE>` : Taille de la grille pour les tests
- `<REPERTOIRE_SORTIE>` : Répertoire où stocker les résultats des tests

Exemple :
```bash
./run_tests.sh 5 50 tests_50/sequentiel
```
Cette commande exécutera 5 tests pour une grille de taille 50×50, et stockera les résultats dans le répertoire `tests_50/sequentiel`.

## Analyse des Résultats

Une fois les tests exécutés, vous pouvez utiliser le script Python pour analyser les résultats. Ce script est simple à exécuter et ne nécessite aucun argument. Assurez-vous simplement que le script de test (`run_tests.sh`) a été exécuté au préalable.

Le script d'analyse est :

- `plot.py` : Génère des graphiques montrant la moyenne des `<N_EXEC>` exécutions au long des itérations

Exemple :
```bash
python3 plot.py
```

Un exemple de graphique généré est disponible dans le fichier `timing_curves_all_metrics.png`.