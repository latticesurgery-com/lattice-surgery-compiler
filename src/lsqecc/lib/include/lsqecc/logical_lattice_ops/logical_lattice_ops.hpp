#ifndef LSQECC_LOGICAL_LATTICE_OPS_HPP
#define LSQECC_LOGICAL_LATTICE_OPS_HPP

#include <variant>

#include <lsqecc/patches/patches.hpp>

#include <tsl/ordered_map.h>


namespace lsqecc {

enum class PauliOperator {
    I,
    X,
    Y,
    Z,
};

enum class MagicState {
    S,
    T,
};

struct SinglePatchMeasurement {
    PatchId target;
    PauliOperator observable;
    bool is_negative;
};

struct MultiPatchMeasurement {
    tsl::ordered_map<PatchId, PauliOperator> targetted_observable;
    bool is_negative;
};

struct MagicStateRequest {
    PatchId target;
    MagicState request;
};

struct LogicalPauli {
    PatchId target;
    PauliOperator op;
};

struct LogicalLatticeOperation {
    std::variant<SinglePatchMeasurement, MultiPatchMeasurement, MagicStateRequest, LogicalPauli> operation;

    std::vector<PatchId> get_operating_patches() const;
};

struct LogicalLatticeAssembly
{
    std::vector<PatchId> core_qubits;
    std::vector<LogicalLatticeOperation> instructions;
};


}


#endif //LSQECC_LOGICAL_LATTICE_OPS_HPP
