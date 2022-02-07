#include <gtest/gtest.h>

#include <lsqecc/patches/fast_patch_computation.hpp>

using namespace lsqecc;


TEST(PatchComputation, make)
{
    LogicalLatticeAssembly assembly{
        .core_qubits = {0},
        .instructions = {
        }
    };

    auto p = PatchComputation::make(assembly);

    ASSERT_EQ(1,p.num_slices());

    Slice expected{
            .distance_dependant_timesteps=1,
            .patches=std::vector<Patch>{
                    Patch{
                            .cells=SingleCellOccupiedByPatch{
                                    .top={BoundaryType::Rough, false},
                                    .bottom={BoundaryType::Rough, false},
                                    .left={BoundaryType::Smooth, false},
                                    .right={BoundaryType::Smooth, false},
                                    .cell=Cell{0, 0}
                            },
                            .type=PatchType::Qubit,
                            .id=std::nullopt,
                    }
            }
    };
    ASSERT_EQ(expected, p.last_slice());
}


TEST(MultiPatchMeasurement, get_operating_patches)
{
    MultiPatchMeasurement m{ .targetted_observable=tsl::ordered_map<PatchId, PauliOperator>{
            {0,PauliOperator::X},
            {10,PauliOperator::Y},
            {20,PauliOperator::Z}
    },
            .is_negative=false
    };

    auto op_patches = LogicalLatticeOperation{m}.get_operating_patches();
    ASSERT_EQ(0,op_patches[0]);
    ASSERT_EQ(10,op_patches[1]);
    ASSERT_EQ(20,op_patches[2]);

}