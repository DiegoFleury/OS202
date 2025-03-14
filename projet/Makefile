# Diretório para os arquivos .inc
PLATFORM_DIR= platform

# Definir a plataforma desejada (linux, msys2, osx)
PLATFORM ?= linux  # Padrão: linux (pode ser sobrescrito na linha de comando)
PLATFORM := $(strip $(PLATFORM))

# Escolher o arquivo de configuração correto com base na plataforma
ifeq ($(PLATFORM), linux)
    include $(PLATFORM_DIR)/Make_linux.inc
else ifeq ($(PLATFORM), msys2)
    include $(PLATFORM_DIR)/Make_msys2.inc
else ifeq ($(PLATFORM), osx)
    include $(PLATFORM_DIR)/Make_osx.inc
else
    $(error Platform invalide! Utilisez PLATFORM=linux, PLATFORM=msys2 ou PLATFORM=osx)
endif

CXXFLAGS = -std=c++17 -Iinclude  # Adiciona o diretório include
ifdef DEBUG
CXXFLAGS += -g -O0 -Wall -fbounds-check -pedantic -D_GLIBCXX_DEBUG
CXXFLAGS2 = $(CXXFLAGS)
else
CXXFLAGS2 = $(CXXFLAGS) -O2 -march=native -Wall
CXXFLAGS += -O3 -march=native -Wall
endif

SRC_DIR = src
INCLUDE_DIR = include
OBJ_DIR = obj

SOURCES = $(wildcard $(SRC_DIR)/*.cpp)  # Encontra todos os .cpp em src/
OBJECTS = $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(SOURCES))  # Cria os .o em obj/
DEPS = $(wildcard $(INCLUDE_DIR)/*.hpp)  # Todos os headers

ALL = simulation.bin

default: help

all: $(ALL)

clean:
	@rm -fr $(OBJ_DIR) *.o *.exe *.bin *~

run:
	./$(ALL)

# Compilação dos .cpp -> .o dentro de obj/
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp $(DEPS)
	@mkdir -p $(OBJ_DIR)  # Cria obj/ se não existir
	$(CXX) $(CXXFLAGS2) -c $< -o $@

# Linkagem final
simulation.bin: $(OBJECTS)
	$(CXX) $(CXXFLAGS2) $^ -o $@ $(LIB)

help:
	@echo "Available targets : "
	@echo "    all            : compile all executables"
	@echo "Add DEBUG=yes to compile in debug"
	@echo "Configuration :"
	@echo "    CXX      :    $(CXX)"
	@echo "    CXXFLAGS :    $(CXXFLAGS)"

%.html: %.md
	pandoc -s --toc $< --css=./github-pandoc.css --metadata pagetitle="OS202 - TD1" -o $@
