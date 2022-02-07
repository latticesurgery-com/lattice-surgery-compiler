#ifndef LSQECC_SLICE_HPP
#define LSQECC_SLICE_HPP

#include <lsqecc/patches/patches.hpp>

namespace lsqecc {

struct Slice {
    int32_t distance_dependant_timesteps = 1;
    std::vector<Patch> patches;

    Slice get_copy_with_cleared_activity() const;

    bool operator==(const Slice&) const = default;
};


}

#endif //LSQECC_SLICE_HPP
