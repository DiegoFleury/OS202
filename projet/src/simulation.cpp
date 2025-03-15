#include <string>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <thread>
#include <chrono>
#include <fstream>
#include <atomic>
#include <signal.h>

#include <mpi.h>
#include "model.hpp"
#include "input.hpp"
#include "display.hpp"

using namespace std::chrono_literals;

std::atomic<bool> quit_signal(false);

void signal_handler(int signal) {
    // std::cout << "RECEBI O SINAL : " << signal << " AQUI !!!!" << std::endl;
    quit_signal.store(true);
}

int main(int nargs, char* args[])
{
    signal(SIGINT, signal_handler);  
    signal(SIGTERM, signal_handler); 

    int provided;
    MPI_Init_thread(&nargs, &args, MPI_THREAD_MULTIPLE, &provided);
    
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    if (size < 2 && rank == 0) {
        std::cerr << "Ce programme nécessite au moins 2 processus MPI.\n";
        MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
        return EXIT_FAILURE;
    }
    
    auto params = parse_arguments(nargs-1, &args[1]);
    
    if (!check_params(params)) {
        MPI_Finalize();
        return EXIT_FAILURE;
    }
    
    Model simu(params.length, params.discretization, params.wind, params.start);

    std::shared_ptr<Displayer> displayer = nullptr;
    SDL_Event event;
    bool is_running = true;
    bool stop_computation = false;
    
    MPI_Comm intercomm;
    MPI_Comm_dup(MPI_COMM_WORLD, &intercomm);
    
    // Processus 0 : responsable de l'affichage
    if (rank == 0) {
        displayer = Displayer::init_instance(params.discretization, params.discretization);
        
        std::string filename = "timing_results.csv";
        std::ofstream file(filename);
        file << "TimeStep,T_avancement,T_communication,T_affichage,T_total\n";
        
        std::vector<unsigned char> vegetal_buffer(params.discretization * params.discretization);
        std::vector<unsigned char> fire_buffer(params.discretization * params.discretization);
        
        bool process1_done = false;
        MPI_Request status_request = MPI_REQUEST_NULL;
        
        while (is_running) {
            bool quit_requested = false;
            
            while (SDL_PollEvent(&event)) {
                if (event.type == SDL_QUIT) {
                    // std::cout << "SDL_QUIT detectado " << std::endl;
                    quit_requested = true;
                    break;
                }
            }
            
            if (quit_requested || quit_signal.load()) {
                stop_computation = true;
                
                // Envoyer de manière non-bloquante le signal d'arrêt au processus 1
                MPI_Request stop_request;
                MPI_Isend(&stop_computation, 1, MPI_C_BOOL, 1, 999, intercomm, &stop_request);
                
                // Détacher la requête et sortir immédiatement
                MPI_Request_free(&stop_request);
                
                // std::cout << "Vou matar o processo 1 ..." << std::endl;
                break;
            }
            
            // Vérifier si le processus 1 a déjà indiqué qu'il a terminé
            if (status_request != MPI_REQUEST_NULL) {
                int flag = 0;
                MPI_Test(&status_request, &flag, MPI_STATUS_IGNORE);
                if (flag && !process1_done) {
                    // std::cout << "P1 terminou normal ..." << std::endl;
                    process1_done = true;
                    break;
                }
            }
            
            auto start_total = std::chrono::high_resolution_clock::now();
            
            MPI_Request is_running_req;
            MPI_Irecv(&is_running, 1, MPI_C_BOOL, 1, 0, intercomm, &is_running_req);
            
            int flag = 0;
            MPI_Status status;
            
            // Attendre jusqu'à 100ms = 10 (for) * 10 (SDL_DELAY)
            for (int i = 0; i < 10; ++i) {
                MPI_Test(&is_running_req, &flag, &status);
                if (flag) break;
                SDL_Delay(10);
            }
            
            if (!flag) {
                if (quit_signal.load()) {
                    // std::cout << "Deu Timeout na hora de rebecer << std::endl;
                    MPI_Cancel(&is_running_req);
                    MPI_Request_free(&is_running_req);
                    break;
                }
                
                MPI_Cancel(&is_running_req);
                MPI_Request_free(&is_running_req);
                continue;
            }
            
            if (!is_running) {
                // std::cout << "P1 terminou normal ..." << std::endl;
                break;
            }
            
            int time_step;
            MPI_Recv(&time_step, 1, MPI_INT, 1, 1, intercomm, MPI_STATUS_IGNORE);
            
            if ((time_step & 31) == 0) {
                std::cout << "Pas de temps " << time_step << "\n===============" << std::endl;
            }
            
            auto start_comm = std::chrono::high_resolution_clock::now();
            
            MPI_Recv(vegetal_buffer.data(), params.discretization * params.discretization, 
                     MPI_UNSIGNED_CHAR, 1, 2, intercomm, MPI_STATUS_IGNORE);
            MPI_Recv(fire_buffer.data(), params.discretization * params.discretization, 
                     MPI_UNSIGNED_CHAR, 1, 3, intercomm, MPI_STATUS_IGNORE);
            
            auto end_comm = std::chrono::high_resolution_clock::now();
            
            
            // -------------------------------- AFFICAHGE ---------------------------------------


            auto start_affichage = std::chrono::high_resolution_clock::now();
            displayer->update(vegetal_buffer, fire_buffer);
            auto end_affichage = std::chrono::high_resolution_clock::now();


            // -------------------------------- AFFICAHGE ---------------------------------------


            auto end_total = std::chrono::high_resolution_clock::now();
            
            // -------------------------------- AVANCEMENT ---------------------------------------

            double T_avancement;
            MPI_Recv(&T_avancement, 1, MPI_DOUBLE, 1, 4, intercomm, MPI_STATUS_IGNORE);

            // -------------------------------- AVANCEMENT ---------------------------------------
            
            double T_comm = std::chrono::duration<double>(end_comm - start_comm).count();
            double T_affichage = std::chrono::duration<double>(end_affichage - start_affichage).count();
            double T_total = std::chrono::duration<double>(end_total - start_total).count();
            
            file << time_step << "," << T_avancement << "," << T_comm << "," 
                 << T_affichage << "," << T_total << "\n";
        }
        
        file.close();
        
        stop_computation = true;
        MPI_Send(&stop_computation, 1, MPI_C_BOOL, 1, 999, intercomm);
        
        // std::cout << "Processo 0 passou pela parte de enviar sina lde parada para o P1." << std::endl;
    }
    // Processus 1 : responsable du calcul
    else if (rank == 1) {
        const int map_size = params.discretization * params.discretization;
        
        bool should_stop = false;
        
        while (is_running) {
            int flag = 0;
            MPI_Status status;
            MPI_Iprobe(0, 999, intercomm, &flag, &status);
            
            if (flag) {
                MPI_Recv(&should_stop, 1, MPI_C_BOOL, 0, 999, intercomm, MPI_STATUS_IGNORE);
                if (should_stop) {
                    // std::cout << "P1 cehgou nessa parte." << std::endl;
                    is_running = false;
                    break;
                }
            }

            // -------------------------------- SIMULATION ---------------------------------------
            
            auto start_avancement = std::chrono::high_resolution_clock::now();
            is_running = simu.update();
            auto end_avancement = std::chrono::high_resolution_clock::now();
            
            // -------------------------------- SIMULATION ---------------------------------------

            double T_avancement = std::chrono::duration<double>(end_avancement - start_avancement).count();
            
            MPI_Iprobe(0, 999, intercomm, &flag, &status);
            if (flag) {
                MPI_Recv(&should_stop, 1, MPI_C_BOOL, 0, 999, intercomm, MPI_STATUS_IGNORE);
                if (should_stop) {
                    std::cout << "Processus 1: Signal d'arrêt reçu après calcul." << std::endl;
                    is_running = false;
                    break;
                }
            }
            
            MPI_Send(&is_running, 1, MPI_C_BOOL, 0, 0, intercomm);
            
            if (!is_running) {
                // std::cout << "P1 fechou normalmzente." << std::endl;
                break;
            }
            
            int time_step = simu.time_step();
            MPI_Send(&time_step, 1, MPI_INT, 0, 1, intercomm);
            
            auto veg_map = simu.vegetal_map();
            auto fire_map = simu.fire_map();
            MPI_Send(veg_map.data(), map_size, MPI_UNSIGNED_CHAR, 0, 2, intercomm);
            MPI_Send(fire_map.data(), map_size, MPI_UNSIGNED_CHAR, 0, 3, intercomm);
            
            MPI_Send(&T_avancement, 1, MPI_DOUBLE, 0, 4, intercomm);
        }
        
        // std::cout << "Processo 1 acabou." << std::endl;
    }
    
    MPI_Comm_free(&intercomm);
    
    if (rank == 0) {
        // Bad 
        MPI_Abort(MPI_COMM_WORLD, 0);
    }
    
    MPI_Finalize();
    
    return EXIT_SUCCESS;
}