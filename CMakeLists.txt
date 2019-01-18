cmake_minimum_required(VERSION 3.12)
project(amcp C)

set(CMAKE_C_STANDARD 11)

include_directories(include)

add_library(amcp SHARED src/amcp.c include/amcp.h)
target_link_libraries(amcp zmq msgpackc)

file(GLOB headers "test/*.h")
add_executable(test test/test.c ${headers})
target_link_libraries(test amcp)