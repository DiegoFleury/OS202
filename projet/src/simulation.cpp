#include <string>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <thread>
#include <chrono>
#include <fstream> 

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

    std::string filename = "resultats_temps.csv";

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
        
        auto start_total = std::chrono::high_resolution_clock::now();

        auto start_avancement = std::chrono::high_resolution_clock::now();
        bool is_running = simu.update();  
        auto end_avancement = std::chrono::high_resolution_clock::now();

        if (!is_running) break;

        if ((simu.time_step() & 31) == 0) 
            std::cout << "Time step " << simu.time_step() << "\n===============" << std::endl;

        auto start_affichage = std::chrono::high_resolution_clock::now();
        displayer->update(simu.vegetal_map(), simu.fire_map());  
        auto end_affichage = std::chrono::high_resolution_clock::now();
        
        auto end_total = std::chrono::high_resolution_clock::now();

        double T_avancement = std::chrono::duration<double>(end_avancement - start_avancement).count();
        double T_affichage = std::chrono::duration<double>(end_affichage - start_affichage).count();
        double T_total = std::chrono::duration<double>(end_total - start_total).count();

        file << simu.time_step() << "," << T_avancement << "," << T_affichage << "," << T_total << "\n";
    }

    file.close();
    std::cout << "Résultats sauvegardés dans '" << filename << "'.\n";

    return EXIT_SUCCESS;
}