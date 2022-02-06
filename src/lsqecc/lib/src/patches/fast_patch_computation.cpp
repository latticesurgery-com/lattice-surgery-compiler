#include <lsqecc/patches/patches.hpp>
#include <lsqecc/patches/fast_patch_computation.hpp>

#include <pybind11/pybind11.h>
#include <iostream>

namespace py = pybind11;

bool lsqecc::make_computation()
{
    std::cout<<"Hello"<<std::endl;
    return true;
}



