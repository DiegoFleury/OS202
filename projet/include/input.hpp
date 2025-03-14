#ifndef INPUT_HPP
#define INPUT_HPP

#include <string>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <array>

#include "model.hpp"

using namespace std::string_literals;

struct ParamsType
{
    double length{1.};
    unsigned discretization{20u};
    std::array<double,2> wind{0.,0.};
    Model::LexicoIndices start{10u,10u};
};

void analyze_arg(int nargs, char* args[], ParamsType& params);
ParamsType parse_arguments(int nargs, char* args[]);
bool check_params(ParamsType& params);
void display_params(ParamsType const& params);

#endif // INPUT_HPP
