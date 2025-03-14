#include <string>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <thread>
#include <chrono>
#include <fstream> 
#include <omp.h>  // Inclusão para obter o número de threads OMP

#include "model.hpp"
#include "input.hpp"
#include "display.hpp"

using namespace std::chrono_literals;

int main(int nargs, char* args[])
{
    auto params = parse_arguments(nargs-1, &args[1]);
    display_params(params);
    if (!check_params(params)) return EXIT_FAILURE;

    auto displayer = Displayer::init_instance(params.discretization, params.discretization);
    auto simu = Model(params.length, params.discretization, params.wind, params.start);

    SDL_Event event;

    // Obtém o número de threads do OpenMP
    int num_threads = omp_get_max_threads();
    
    // Cria o nome do arquivo com o número de threads
    std::string filename = "timing_results_" + std::to_string(num_threads) + "_threads.csv";

    // Abre o arquivo CSV para armazenar os resultados
    std::ofstream file(filename);
    if (!file) {
        std::cerr << "Erreur : Impossible de créer le fichier CSV.\n";
        return EXIT_FAILURE;
    }
    file << "TimeStep,T_avancement,T_affichage,T_total\n";  

    while (true)
    {
        while (SDL_PollEvent(&event))
            if (event.type == SDL_QUIT)
                return EXIT_SUCCESS;
        
        // Tempo total para um passo de tempo (cálculo + exibição)
        auto start_total = std::chrono::high_resolution_clock::now();

        // Início do cronômetro para o avanço no tempo
        auto start_avancement = std::chrono::high_resolution_clock::now();
        bool is_running = simu.update();  
        auto end_avancement = std::chrono::high_resolution_clock::now();

        // Se a simulação terminou, encerramos o loop
        if (!is_running) break;

        if ((simu.time_step() & 31) == 0) 
            std::cout << "Time step " << simu.time_step() << "\n===============" << std::endl;

        // Início do cronômetro para a exibição
        auto start_affichage = std::chrono::high_resolution_clock::now();
        displayer->update(simu.vegetal_map(), simu.fire_map());  
        auto end_affichage = std::chrono::high_resolution_clock::now();
        
        // Fim do cronômetro para o tempo total
        auto end_total = std::chrono::high_resolution_clock::now();

        // Cálculo dos tempos
        double T_avancement = std::chrono::duration<double>(end_avancement - start_avancement).count();
        double T_affichage = std::chrono::duration<double>(end_affichage - start_affichage).count();
        double T_total = std::chrono::duration<double>(end_total - start_total).count();

        // Salva os tempos no arquivo CSV
        file << simu.time_step() << "," << T_avancement << "," << T_affichage << "," << T_total << "\n";
    }

    // Fecha o arquivo após a simulação
    file.close();
    std::cout << "Résultats sauvegardés dans '" << filename << "'.\n";

    return EXIT_SUCCESS;
}
