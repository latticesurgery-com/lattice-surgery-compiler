#include <pybind11/pybind11.h>

#include <lsqecc/patches/fast_patch_computation.hpp>

int fast_make_computation(int i)
{
    return 10*i;
}


PYBIND11_MODULE(lsqecclib_bybind, m) {
    m.doc() = "Fast patch computation";
    m.def("fast_make_computation", &fast_make_computation, "Fast patch computation");
}