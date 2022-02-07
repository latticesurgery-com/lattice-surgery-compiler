#include <lsqecc/patches/patches.hpp>

namespace lsqecc {

PatchId global_patch_id_counter = 0;

PatchId make_new_patch_id(){
    return global_patch_id_counter++;
}

}