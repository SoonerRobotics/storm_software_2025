cmake_minimum_required(VERSION 3.10)

project(STORM_Robot)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

find_package(OpenCV REQUIRED)
find_package(Boost REQUIRED COMPONENTS system thread)

include_directories(${OpenCV_INCLUDE_DIRS} ${Boost_INCLUDE_DIRS} include)

set(SOURCE_FILES
    src/robot.cpp
    src/messages.cpp
    src/video.cpp
)

add_executable(robot ${SOURCE_FILES})

target_link_libraries(robot PRIVATE ${OpenCV_LIBS} ${Boost_LIBRARIES})
