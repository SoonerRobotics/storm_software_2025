cmake_minimum_required(VERSION 3.10)

# Project Name
project(STORM_Robot)

# Set C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add include directory
include_directories(${PROJECT_SOURCE_DIR}/include)

# Add source files
add_executable(robot src/robot.cpp)

# Link libraries from lib 
target_link_libraries(robot PRIVATE ${PROJECT_SOURCE_DIR}/lib)

set(rtc_DIR "/usr/local/lib/cmake/rtc") # Adjust path if necessary
find_package(rtc REQUIRED)
