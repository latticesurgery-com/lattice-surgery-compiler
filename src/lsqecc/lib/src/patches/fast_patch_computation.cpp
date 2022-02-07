#include <lsqecc/patches/patches.hpp>
#include <lsqecc/patches/fast_patch_computation.hpp>


#include <iostream>
#include <iterator>
#include <ranges>



namespace lsqecc {


class SimpleLayout : public Layout {
public:
    explicit SimpleLayout(size_t num_qubits) : num_qubits_(num_qubits) {}

    const std::vector<Patch> core_patches() const override
    {
        std::vector<Patch> core;
        core.reserve(num_qubits_);
        for(size_t i: std::views::iota(static_cast<size_t>(0),num_qubits_))
        {
            core.push_back(basic_square_patch({
                    .row=0,
                    .col=2*static_cast<Cell::CoordinateType>(i)
            }));
        }
        return core;
    }

    std::vector<Cell> magic_state_queue_locations() const override {
        std::vector<Cell> magic_state_queue;
        magic_state_queue.reserve(num_qubits_);
        for(size_t i: std::views::iota(static_cast<size_t>(0),num_qubits_))
        {
            magic_state_queue.push_back({
                    .row=0,
                    .col=2*static_cast<Cell::CoordinateType>(i)
            });
        }
        return magic_state_queue;
    }
    std::vector<Cell> distillery_locations()  const override
    {
        return {};
    };

private:
    static Patch basic_square_patch(Cell placement){
        return Patch{
                .cells=SingleCellOccupiedByPatch{
                        .top={BoundaryType::Rough,false},
                        .bottom={BoundaryType::Rough,false},
                        .left={BoundaryType::Smooth,false},
                        .right={BoundaryType::Smooth,false},
                        .cell=placement
                },
                .type=PatchType::Qubit,
                .id=std::nullopt,
        };
    }

private:
    size_t num_qubits_;

};



Slice first_slice_from_layout(const Layout& layout)
{
    Slice slice{.distance_dependant_timesteps=1, .patches={}};

    for (const Patch& p : layout.core_patches())
        slice.patches.push_back(p);

    return slice;
}


PatchComputation PatchComputation::make(const LogicalLatticeAssembly& assembly) {
    PatchComputation patch_computation;
    patch_computation.layout = std::make_unique<SimpleLayout>(assembly.core_qubits.size());
    patch_computation.slices.push_back(first_slice_from_layout(*patch_computation.layout));

    for(const LogicalLatticeOperation& instruction : assembly.instructions)
    {
        patch_computation.new_slice();

        if (const auto* s = std::get_if<SinglePatchMeasurement>(&instruction.operation))
        {

        }
        if (const auto* p = std::get_if<LogicalPauli>(&instruction.operation))
        {

        }
        else if (const auto* m = std::get_if<MultiPatchMeasurement>(&instruction.operation))
        {

        }
        else
        {
            const auto& mr = std::get<MagicStateRequest>(instruction.operation);
        }
    }


    return patch_computation;
}


size_t PatchComputation::num_slices() const
{
    return slices.size();
}


const Slice& PatchComputation::slice(size_t idx) const
{
    return slices.at(idx);
}

const Slice& PatchComputation::last_slice() const {
    return slice(num_slices()-1);
}

void PatchComputation::new_slice() {
    slices.emplace_back(last_slice().get_copy_with_cleared_activity());
}


}

