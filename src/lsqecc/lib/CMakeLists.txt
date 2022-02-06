cmake_minimum_required(VERSION 3.5)


project(lsqecc)


####################################################
# General configuration

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -Wfatal-errors -Wall -pedantic")
set(CMAKE_CXX_STANDARD 20)


find_package(Boost REQUIRED COMPONENTS filesystem)

# set(PYTHON_VERSION 3.9)
# set(Python_ROOT_DIR /usr/lib/python3.9)
# set(PYTHON_LIBRARIES /usr/lib/libpython3.10.so)
find_package(PythonLibs)
include_directories(/usr/include/python3.10)

add_subdirectory(external/pybind11)

###################################################
# Library setup

message(STATUS ${PYTHON_LIBRARIES})

add_library(
        lsqecclib
        "${PROJECT_SOURCE_DIR}/src/patches/fast_patch_computation.cpp"
)

set(INCLUDE_DIRS
        "${PROJECT_SOURCE_DIR}/include"
        "${PROJECT_SOURCE_DIR}/external/pybind11/include")

target_include_directories(
        lsqecclib
        PUBLIC
        ${INCLUDE_DIRS}
)

set_property(TARGET lsqecclib PROPERTY POSITION_INDEPENDENT_CODE ON)

target_link_libraries(lsqecclib
    ${Boost_FILESYSTEM_LIBRARY}
)

target_link_libraries(lsqecclib ${PYTHON_LIBRARIES})

###################################################
# Python Interface

pybind11_add_module(lsqecclib_bybind ${PROJECT_SOURCE_DIR}/src/lsqecclib_pybind.cpp)

target_include_directories(
        lsqecclib_bybind
        PUBLIC
        ${INCLUDE_DIRS}
)

target_link_libraries(
        lsqecclib_bybind PUBLIC lsqecclib
)


###################################################
# Tests

enable_testing()


# lib
add_executable(
        lsqecc_tests
        tests/patches/fast_patch_computation.cpp
)
target_link_libraries(lsqecc_tests
        lsqecclib
        gtest
        gtest_main
)
add_test(
        NAME unit
        COMMAND ${PROJECT_BINARY_DIR}/lsqecc_tests
)
add_custom_command(
        TARGET lsqecc_tests
        COMMENT "Run lsqecc_tests"
        POST_BUILD
        COMMAND ${PROJECT_BINARY_DIR}/lsqecc_tests
)
