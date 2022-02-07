#ifndef LSQECC_PATCHES_HPP
#define LSQECC_PATCHES_HPP

#include <cstdint>
#include <optional>
#include <vector>
#include <variant>

#include <eigen3/Eigen/Dense>

namespace lsqecc {

enum class BoundaryType {
    None, // Used by routing
    Connected, // Used for multi patch
    Rough,
    Smooth,
};

struct Cell {
    using CoordinateType = int32_t;
    CoordinateType row;
    CoordinateType col;

    bool operator==(const Cell&) const = default;
};

enum class PatchType {
    Distillation,
    PreparedState,
    Qubit,
    Routing
};

enum class PatchActivity
{
    None,
    Measurement,
    Unitary
};


struct Boundary {
    BoundaryType boundary_type;
    bool is_active;

    bool operator==(const Boundary&) const = default;
};

struct SingleCellOccupiedByPatch : public Cell {
    Boundary top;
    Boundary bottom;
    Boundary left;
    Boundary right;

    Cell cell;

    bool operator==(const SingleCellOccupiedByPatch&) const = default;
};


struct MultipleCellsOccupiedByPatch {
    std::vector<SingleCellOccupiedByPatch> sub_cells;

    bool operator==(const MultipleCellsOccupiedByPatch&) const = default;
};

using PatchId = uint32_t;

struct Patch{
    std::variant<SingleCellOccupiedByPatch, MultipleCellsOccupiedByPatch> cells;
    PatchType type;
    PatchActivity activity;

    std::optional<PatchId> id;

    bool operator==(const Patch&) const = default;
};


PatchId make_new_patch_id();


}


#endif //LSQECC_PATCHES_HPP
