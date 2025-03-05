#include <stdexcept>
#include <cmath>
#include <iostream>
#include <vector>
#include <omp.h>
#include "model.hpp"

namespace
{
    double pseudo_random(std::size_t index, std::size_t time_step)
    {
        std::uint_fast32_t xi = std::uint_fast32_t(index * (time_step + 1));
        std::uint_fast32_t r  = (48271 * xi) % 2147483647;
        return r / 2147483646.;
    }

    double log_factor(std::uint8_t value)
    {
        return std::log(1. + value) / std::log(256);
    }
}

Model::Model(double t_length, unsigned t_discretization, std::array<double,2> t_wind,
             LexicoIndices t_start_fire_position, double t_max_wind )
    : m_length(t_length),
      m_distance(-1),
      m_geometry(t_discretization),
      m_wind(t_wind),
      m_wind_speed(std::sqrt(t_wind[0]*t_wind[0] + t_wind[1]*t_wind[1])),
      m_max_wind(t_max_wind),
      m_vegetation_map(t_discretization * t_discretization, 255u),
      m_fire_map(t_discretization * t_discretization, 0u)
{
    if (t_discretization == 0) {
        throw std::range_error("Le nombre de cases par direction doit être plus grand que zéro.");
    }
    m_distance = m_length / double(m_geometry);

    // Position initiale du foyer
    auto index = get_index_from_lexicographic_indices(t_start_fire_position);
    m_fire_map[index] = 255u;
    m_fire_front[index] = 255u;

    // Calcul de p1
    constexpr double alpha0 = 4.52790762e-01;
    constexpr double alpha1 = 9.58264437e-04;
    constexpr double alpha2 = 3.61499382e-05;

    if (m_wind_speed < t_max_wind)
        p1 = alpha0 + alpha1*m_wind_speed + alpha2*(m_wind_speed*m_wind_speed);
    else
        p1 = alpha0 + alpha1*t_max_wind + alpha2*(t_max_wind*t_max_wind);

    // p2: probabilité que le feu commence à s'éteindre
    p2 = 0.99;

    // Ajustement de alphaEastWest / alphaWestEast selon la vitesse du vent en x
    if (m_wind[0] > 0) {
        alphaEastWest = std::abs(m_wind[0]/t_max_wind) + 1;
        alphaWestEast = 1. - std::abs(m_wind[0]/t_max_wind);
    } else {
        alphaWestEast = std::abs(m_wind[0]/t_max_wind) + 1;
        alphaEastWest = 1. - std::abs(m_wind[0]/t_max_wind);
    }

    // Ajustement de alphaSouthNorth / alphaNorthSouth selon la vitesse du vent en y
    if (m_wind[1] > 0) {
        alphaSouthNorth = std::abs(m_wind[1]/t_max_wind) + 1;
        alphaNorthSouth = 1. - std::abs(m_wind[1]/t_max_wind);
    } else {
        alphaNorthSouth = std::abs(m_wind[1]/t_max_wind) + 1;
        alphaSouthNorth = 1. - std::abs(m_wind[1]/t_max_wind);
    }
}

bool Model::update()
{
    // On copie m_fire_front dans next_front
    auto next_front = m_fire_front;

    // On récupère toutes les clés (indices) dans un vecteur pour OpenMP
    std::vector<std::size_t> fire_cells;
    fire_cells.reserve(m_fire_front.size());

    for (auto it = m_fire_front.begin(); it != m_fire_front.end(); ++it) {
        fire_cells.push_back(it->first);
    }

    // Boucle parallèle pour la propagation du feu
    #pragma omp parallel for
    for (std::size_t i = 0; i < fire_cells.size(); ++i) {
        std::size_t f = fire_cells[i]; // index global

        LexicoIndices coord = get_lexicographic_from_index(f);
        double power = log_factor(m_fire_front.at(f)); // intensité de la cellule en feu

        // Bas
        if (coord.row < m_geometry - 1) {
            std::size_t row_v = coord.row + 1;
            std::size_t col_v = coord.column;
            std::size_t neighbor_index = row_v * m_geometry + col_v;

            double tirage = pseudo_random(f + m_time_step, m_time_step);
            double green_power = m_vegetation_map[neighbor_index];
            double correction = power * log_factor(green_power);

            if (tirage < alphaSouthNorth * p1 * correction) {
                #pragma omp critical
                {
                    m_fire_map[neighbor_index] = 255;
                    next_front[neighbor_index] = 255;
                }
            }
        }

        // Haut
        if (coord.row > 0) {
            std::size_t row_v = coord.row - 1;
            std::size_t col_v = coord.column;
            std::size_t neighbor_index = row_v * m_geometry + col_v;

            double tirage = pseudo_random(f * 13427 + m_time_step, m_time_step);
            double green_power = m_vegetation_map[neighbor_index];
            double correction = power * log_factor(green_power);

            if (tirage < alphaNorthSouth * p1 * correction) {
                #pragma omp critical
                {
                    m_fire_map[neighbor_index] = 255;
                    next_front[neighbor_index] = 255;
                }
            }
        }

        // Droite
        if (coord.column < m_geometry - 1) {
            std::size_t row_v = coord.row;
            std::size_t col_v = coord.column + 1;
            std::size_t neighbor_index = row_v * m_geometry + col_v;

            double tirage = pseudo_random(f * 13427UL * 13427UL + m_time_step, m_time_step);
            double green_power = m_vegetation_map[neighbor_index];
            double correction = power * log_factor(green_power);

            if (tirage < alphaEastWest * p1 * correction) {
                #pragma omp critical
                {
                    m_fire_map[neighbor_index] = 255;
                    next_front[neighbor_index] = 255;
                }
            }
        }

        // Gauche
        if (coord.column > 0) {
            std::size_t row_v = coord.row;
            std::size_t col_v = coord.column - 1;
            std::size_t neighbor_index = row_v * m_geometry + col_v;

            double tirage = pseudo_random(f * 13427UL * 13427UL * 13427UL + m_time_step, m_time_step);
            double green_power = m_vegetation_map[neighbor_index];
            double correction = power * log_factor(green_power);

            if (tirage < alphaWestEast * p1 * correction) {
                #pragma omp critical
                {
                    m_fire_map[neighbor_index] = 255;
                    next_front[neighbor_index] = 255;
                }
            }
        }

        // Gestion de l'extinction du feu dans la cellule f
        // On regarde l'intensité actuelle dans m_fire_front[f]
        uint8_t intensite = m_fire_front.at(f);

        if (intensite == 255) {
            // Feu à son maximum
            double tirage = pseudo_random(f * 52513 + m_time_step, m_time_step);
            if (tirage < p2) {
                #pragma omp critical
                {
                    m_fire_map[f] >>= 1;
                    next_front[f] >>= 1;
                }
            }
        }
        else {
            // Feu en train de s'éteindre
            #pragma omp critical
            {
                m_fire_map[f] >>= 1;
                next_front[f] >>= 1;
                // Si la cellule tombe à zéro, on supprime du front
                if (next_front[f] == 0) {
                    next_front.erase(f);
                }
            }
        }
    }

    // Mise à jour du front
    m_fire_front = next_front;

    // Réduction de la végétation sur chaque cellule en feu
    #pragma omp parallel for
    for (std::size_t i = 0; i < fire_cells.size(); ++i) {
        std::size_t idx = fire_cells[i];
        if (m_vegetation_map[idx] > 0) {
            m_vegetation_map[idx] -= 1;
        }
    }

    // Incrément du pas de temps (protégé)
    #pragma omp critical
    {
        m_time_step += 1;
    }

    // Critère d'arrêt: s'il n'y a plus de cellules en feu
    return !m_fire_front.empty();
}

std::size_t Model::get_index_from_lexicographic_indices(LexicoIndices t_lexico_indices) const
{
    return t_lexico_indices.row * this->geometry() + t_lexico_indices.column;
}

auto Model::get_lexicographic_from_index(std::size_t t_global_index) const -> LexicoIndices
{
    LexicoIndices ind_coords;
    ind_coords.row    = t_global_index / this->geometry();
    ind_coords.column = t_global_index % this->geometry();
    return ind_coords;
}
