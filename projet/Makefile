# Répertoire pour les fichiers .inc
PLATFORM_DIR= platform

# Définir la plateforme souhaitée (linux, msys2, osx)
PLATFORM ?= linux 
PLATFORM := $(strip $(PLATFORM))

# Choisir le fichier de configuration correct selon la plateforme
ifeq ($(PLATFORM), linux)
include $(PLATFORM_DIR)/Make_linux.inc
else ifeq ($(PLATFORM), msys2)
include $(PLATFORM_DIR)/Make_msys2.inc
else ifeq ($(PLATFORM), osx)
include $(PLATFORM_DIR)/Make_osx.inc
else
$(error Plateforme invalide! Utilisez PLATFORM=linux, PLATFORM=msys2 ou PLATFORM=osx)
endif

# Nombre de threads OpenMP - peut être défini en ligne de commande
OMP_NUM_THREADS ?= 6

# Utiliser uniquement MPICXX et LIB du fichier .inc
# Ajouter des flags spécifiques pour C++
CXXFLAGS += -std=c++17 -Iinclude # Ajoute le répertoire include

ifdef DEBUG
CXXFLAGS += -g -O0 -Wall -fbounds-check -pedantic -D_GLIBCXX_DEBUG
CXXFLAGS2 = $(CXXFLAGS)
else
CXXFLAGS2 = $(CXXFLAGS) -O2 -march=native -Wall
CXXFLAGS += -O3 -march=native -Wall
endif

# Paramètres de simulation - passés via ligne de commande
ARGS ?=

SRC_DIR = src
INCLUDE_DIR = include
OBJ_DIR = obj
SOURCES = $(wildcard $(SRC_DIR)/*.cpp) # Trouve tous les .cpp dans src/
OBJECTS = $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(SOURCES)) # Crée les .o dans obj/
DEPS = $(wildcard $(INCLUDE_DIR)/*.hpp) # Tous les headers
ALL = simulation.bin

default: help
all: $(ALL)

clean:
	@rm -fr $(OBJ_DIR) *.o *.exe *.bin *~

# Commande run qui permet de spécifier le nombre de threads OpenMP
run:
	export OMP_NUM_THREADS=$(OMP_NUM_THREADS) && mpiexec -n 2 --bind-to none ./$(ALL) $(ARGS)

# Compilation des .cpp -> .o dans obj/
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp $(DEPS)
	@mkdir -p $(OBJ_DIR) # Crée obj/ s'il n'existe pas
	$(MPICXX) $(CXXFLAGS2) -c $< -o $@

# Liaison finale utilisant MPICXX
simulation.bin: $(OBJECTS)
	$(MPICXX) $(CXXFLAGS2) $^ -o $@ $(LIB)

help:
	@echo "Cibles disponibles : "
	@echo " all : compile tous les exécutables avec MPI"
	@echo " run : lance la simulation MPI"
	@echo "Options :"
	@echo " NPROCS=N : définit le nombre de processus MPI (défaut: 2)"
	@echo " ARGS=\"...\" : passe des arguments à la simulation"
	@echo " Exemple: make run NPROCS=2 ARGS=\"-n 500\""
	@echo "Ajoutez DEBUG=yes pour compiler en mode debug"
	@echo "Configuration :"
	@echo " MPICXX : $(MPICXX)"
	@echo " CXXFLAGS : $(CXXFLAGS)"

%.html: %.md
	pandoc -s --toc $< --css=./github-pandoc.css --metadata pagetitle="OS202 - TD1" -o $@