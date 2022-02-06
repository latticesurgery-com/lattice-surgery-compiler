#include <gtest/gtest.h>

#include <lsqecc/patches/fast_patch_computation.hpp>


int main(int argc, char** argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


TEST(make_computation, basic_run)
{
    ASSERT_TRUE(lsqecc::make_computation());
}