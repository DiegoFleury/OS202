#include <stdexcept>
#include <cmath>
#include <iostream>
#include "model.hpp"
#include <omp.h>
#include <algorithm>

namespace
{
    double pseudo_random(std::size_t index, std::size_t time_step)
    {
        std::uint_fast32_t xi = std::uint_fast32_t(index * (10000 + time_step + 1));
        std::uint_fast32_t r = (48271 * xi) % 2147483647;
        return r / 2147483646.;
    }

    double log_factor(std::uint8_t value)
    {
        return std::log(1. + value) / std::log(256);
    }
}

Model::Model(double t_length, unsigned t_discretization, std::array<double, 2> t_wind,
             LexicoIndices t_start_fire_position, double t_max_wind)
    : m_length(t_length),
      m_distance(-1),
      m_geometry(t_discretization),
      m_wind(t_wind),
      m_wind_speed(std::sqrt(t_wind[0] * t_wind[0] + t_wind[1] * t_wind[1])),
      m_max_wind(t_max_wind),
      m_vegetation_map(t_discretization * t_discretization, 255u),
      m_fire_map(t_discretization * t_discretization, 0u)
{
    if (t_discretization == 0)
        throw std::range_error("Le nombre de cases par direction doit être plus grand que zéro.");

    m_distance = m_length / double(m_geometry);
    auto index = get_index_from_lexicographic_indices(t_start_fire_position);
    m_fire_map[index] = 255u;
    m_fire_front[index] = 255u;

    constexpr double alpha0 = 4.52790762e-01;
    constexpr double alpha1 = 9.58264437e-04;
    constexpr double alpha2 = 3.61499382e-05;

    if (m_wind_speed < m_max_wind)
        p1 = alpha0 + alpha1 * m_wind_speed + alpha2 * (m_wind_speed * m_wind_speed);
    else
        p1 = alpha0 + alpha1 * m_max_wind + alpha2 * (m_max_wind * m_max_wind);

    p2 = 0.3;

    if (m_wind[0] > 0)
    {
        alphaEastWest = std::abs(m_wind[0] / m_max_wind) + 1;
        alphaWestEast = 1. - std::abs(m_wind[0] / m_max_wind);
    }
    else
    {
        alphaWestEast = std::abs(m_wind[0] / m_max_wind) + 1;
        alphaEastWest = 1. - std::abs(m_wind[0] / m_max_wind);
    }

    if (m_wind[1] > 0)
    {
        alphaSouthNorth = std::abs(m_wind[1] / m_max_wind) + 1;
        alphaNorthSouth = 1. - std::abs(m_wind[1] / m_max_wind);
    }
    else
    {
        alphaNorthSouth = std::abs(m_wind[1] / m_max_wind) + 1;
        alphaSouthNorth = 1. - std::abs(m_wind[1] / m_max_wind);
    }
}

bool Model::check_direction(std::size_t current_index, double power, 
                           const LexicoIndices& coord, Direction dir,
                           double alpha_factor, std::size_t random_factor,
                           std::vector<FirePropagation>& propagations)
{
    // Verificar limites do grid conforme direção
    bool valid_boundary = false;
    LexicoIndices new_coord = coord;
    
    switch(dir) {
        case Direction::SOUTH:
            if (coord.row < m_geometry - 1) {
                new_coord.row += 1;
                valid_boundary = true;
            }
            break;
        case Direction::NORTH:
            if (coord.row > 0) {
                new_coord.row -= 1;
                valid_boundary = true;
            }
            break;
        case Direction::EAST:
            if (coord.column < m_geometry - 1) {
                new_coord.column += 1;
                valid_boundary = true;
            }
            break;
        case Direction::WEST:
            if (coord.column > 0) {
                new_coord.column -= 1;
                valid_boundary = true;
            }
            break;
    }
    
    if (valid_boundary) {
        std::size_t new_index = get_index_from_lexicographic_indices(new_coord);
        
        double tirage = pseudo_random(current_index * random_factor + m_time_step, m_time_step);
        double green_power = m_vegetation_map[new_index];
        double correction = power * log_factor(green_power);
        
        if (tirage < alpha_factor * p1 * correction) {
            propagations.push_back({new_index, 255, true});
            return true;
        }
    }
    
    return false;
}

bool Model::update()
{
    // Créer une copie du front de feu actuel
    auto next_front = m_fire_front;

    // Extraction de tous les indices du front de feu dans un vecteur pour parallélisation
    std::vector<decltype(m_fire_front.begin())> vecteur_idx;
    vecteur_idx.reserve(m_fire_front.size());
    
    // On remplit le vecteur d'indices
    #pragma omp parallel
    {
        #pragma omp single
        {
            for (auto it = m_fire_front.begin(); it != m_fire_front.end(); ++it) {
                vecteur_idx.push_back(it);
            }
        }
    }

    // Structure pour stocker toutes les propagations à traiter
    std::vector<std::vector<FirePropagation>> all_propagations;

    // Parallélisation de la phase de propagation du feu
    #pragma omp parallel
    {
        int num_threads = omp_get_num_threads();
        int thread_id = omp_get_thread_num();
        
        #pragma omp single
        {
            all_propagations.resize(num_threads);
        }

        auto& propagations = all_propagations[thread_id];
        propagations.reserve(vecteur_idx.size() * 4 / num_threads);

        #pragma omp for schedule(dynamic, 256)
        for (std::size_t i = 0; i < vecteur_idx.size(); i++)
        {
            const auto& fire_pair = *vecteur_idx[i];
            std::size_t current_index = fire_pair.first;
            uint8_t current_intensity = fire_pair.second;

            LexicoIndices coord = get_lexicographic_from_index(current_index);
            double power = log_factor(current_intensity);

            // Vérification de la propagation dans les 4 directions
            check_direction(current_index, power, coord, Direction::SOUTH, alphaSouthNorth, 1, propagations);
            check_direction(current_index, power, coord, Direction::NORTH, alphaNorthSouth, 13427, propagations);
            check_direction(current_index, power, coord, Direction::EAST, alphaEastWest, 179284929ULL, propagations);
            check_direction(current_index, power, coord, Direction::WEST, alphaWestEast, 2418104973ULL, propagations);

            uint8_t new_intensity = current_intensity >> 1;

            if (current_intensity == 255)
            {
                double tirage = pseudo_random(current_index * 52513 + m_time_step, m_time_step);
                if (tirage >= p2)
                {
                    new_intensity = current_intensity; 
                }
            }

            propagations.push_back({current_index, new_intensity});
        }
    }

    // Application des propagations sur le front de feu (section critique)
    // Cette étape pourrait être parallélisée avec des sections critiques ou des structures concurrentes
    // mais nous maintenons la version séquentielle pour éviter les conflits d'accès
    for (const auto& thread_propagations : all_propagations)
    {
        for (const auto& propagation : thread_propagations)
        {
            if (propagation.is_new_fire)
            {
                m_fire_map[propagation.cell_position] = propagation.fire_intensity;
                next_front[propagation.cell_position] = propagation.fire_intensity;
            }
            else{
                m_fire_map[propagation.cell_position] = propagation.fire_intensity;
                if (propagation.fire_intensity == 0)
                    next_front.erase(propagation.cell_position);
                else
                    next_front[propagation.cell_position] = propagation.fire_intensity;
            }
        }
    }

    // Mise à jour du front de feu
    m_fire_front = next_front;

    // Mise à jour de la végétation
    std::vector<std::size_t> veg_indices;
    veg_indices.reserve(m_fire_front.size());
    
    #pragma omp parallel
    {
        #pragma omp single
        {
            for (const auto &f : m_fire_front)
                veg_indices.push_back(f.first);
        }
    }

    #pragma omp parallel for schedule(dynamic, 256)
    for (std::size_t i = 0; i < veg_indices.size(); i++)
    {
        std::size_t index = veg_indices[i];
        if (m_vegetation_map[index] > 0)
            m_vegetation_map[index] -= 1;
    }

    m_time_step += 1;
    return !m_fire_front.empty();
}

std::size_t Model::get_index_from_lexicographic_indices(LexicoIndices t_lexico_indices) const
{
    return t_lexico_indices.row * this->geometry() + t_lexico_indices.column;
}

Model::LexicoIndices Model::get_lexicographic_from_index(std::size_t t_global_index) const
{
    LexicoIndices ind_coords;
    ind_coords.row = t_global_index / this->geometry();
    ind_coords.column = t_global_index % this->geometry();
    return ind_coords;
}