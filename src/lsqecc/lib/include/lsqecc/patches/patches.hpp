#ifndef LSQECC_PATCHES_HPP
#define LSQECC_PATCHES_HPP

#include <cstdint>
#include <optional>

namespace lsqecc {

enum class BoundaryType {
    None, // Used by routing
    Rough,
    Smooth,
};

struct cell {
    using CoordinateType = int32_t;
    CoordinateType row;
    CoordinateType col;
};

enum class PatchType {
    Distillation,
    PreparedState,
    Qubit,
    Routing
};

struct Boundary {
    BoundaryType boundary_type;
    bool is_active;
};

using PatchID = uint32_t;

struct SingleBlockPatch {
    Boundary Top;
    Boundary Bottom;
    Boundary Left;
    Boundary Right;

    PatchID patch_id;

};


}


#endif //LSQECC_PATCHES_HPP
