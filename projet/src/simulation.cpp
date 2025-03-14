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

    // Ouvrir un fichier CSV pour enregistrer les résultats
    std::ofstream file("timing_results.csv");
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
        
        // Temps total pour un pas de temps (calcul + affichage)
        auto start_total = std::chrono::high_resolution_clock::now();

        // Début du chronomètre pour l'avancement en temps
        auto start_avancement = std::chrono::high_resolution_clock::now();
        bool is_running = simu.update();  
        auto end_avancement = std::chrono::high_resolution_clock::now();

        // Si la simulation est terminée, on arrête la boucle
        if (!is_running) break;

        if ((simu.time_step() & 31) == 0) 
            std::cout << "Time step " << simu.time_step() << "\n===============" << std::endl;

        // Début du chronomètre pour l'affichage
        auto start_affichage = std::chrono::high_resolution_clock::now();
        displayer->update(simu.vegetal_map(), simu.fire_map());  
        auto end_affichage = std::chrono::high_resolution_clock::now();
        
        // Fin du chronomètre pour le temps total
        auto end_total = std::chrono::high_resolution_clock::now();

        // Calcul des temps
        double T_avancement = std::chrono::duration<double>(end_avancement - start_avancement).count();
        double T_affichage = std::chrono::duration<double>(end_affichage - start_affichage).count();
        double T_total = std::chrono::duration<double>(end_total - start_total).count();

        // Sauvegarde des temps dans le fichier CSV
        file << simu.time_step() << "," << T_avancement << "," << T_affichage << "," << T_total << "\n";
        
        // std::this_thread::sleep_for(0.1s);
    }

    // Fermeture du fichier après la simulation
    file.close();
    std::cout << "Résultats sauvegardés dans 'timing_results.csv'.\n";

    return EXIT_SUCCESS;
}