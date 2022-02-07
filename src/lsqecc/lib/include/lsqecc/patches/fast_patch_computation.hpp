#ifndef LSQECC_FAST_PATCH_COMPUTATION_HPP
#define LSQECC_FAST_PATCH_COMPUTATION_HPP


#include <lsqecc/logical_lattice_ops/logical_lattice_ops.hpp>
#include <lsqecc/patches/slice.hpp>
#include <lsqecc/patches/patches.hpp>


namespace lsqecc {


struct Layout
{
    virtual const std::vector<Patch> core_patches() const = 0;
    virtual std::vector<Cell> magic_state_queue_locations() const = 0;
    virtual std::vector<Cell> distillery_locations()  const = 0;
};


class PatchComputation
{
public:
    // Abstract away the slices so wen don't have to rely on having a vector
    // TODO make iterator
    size_t num_slices() const;
    const Slice& slice(size_t idx) const;
    const Slice& last_slice() const;

    static PatchComputation make(const LogicalLatticeAssembly& assembly);

private:

    void new_slice();

    std::unique_ptr<Layout> layout = nullptr;
    std::vector<Slice> slices;


public:
    using ConstIer = decltype(slices)::const_iterator;
    ConstIer begin() const {return slices.begin();};
    ConstIer end() const {return slices.end();};

};


}

#endif //LSQECC_FAST_PATCH_COMPUTATION_HPP
