#include <lsqecc/patches/slice.hpp>
#include <iterator>

namespace lsqecc{

Slice Slice::get_copy_with_cleared_activity() const {
    Slice new_slice;

    // Remove patches that were measured in the previous timestep
    std::ranges::copy_if(patches,
            std::back_inserter(new_slice.patches),
            [](const Patch& p){return p.activity!=PatchActivity::Measurement;});
    for (auto& e : new_slice.patches) {
        // Clear Unitary Operator activity
        if(e.activity == PatchActivity::Unitary)
            e.activity = PatchActivity::None;
    }

    return new_slice;
}

}
