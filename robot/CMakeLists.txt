cmake_minimum_required(VERSION 3.10)

project(STORM_Robot)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_BUILD_TYPE Debug)

# Windows
set(OpenCV_DIR C:/lib/build_opencv)
set(Protobuf_DIR C:/protobuf-30.1/protobuf-30.1/cmake)
set(Boost_DIR C:/boost/boost_1_60_0)

include_directories(${OpenCV_INCLUDE_DIRS} ${Boost_INCLUDE_DIRS} ${Protobuf_INCLUDE_DIRS} include)

set(PROTO_FILE "../proto/messages.proto")
# protobuf_generate_cpp(PROTO_SRC PROTO_HEADER ${PROTO_FILE})

set(SOURCE_FILES
    src/robot.cpp
    src/messages.cpp
    src/messages.pb.cc
    src/video.cpp
)

add_executable(robot ${SOURCE_FILES})

target_link_libraries(robot PRIVATE ${OpenCV_LIBS} ${Boost_LIBRARIES} ${Protobuf_LIBRARIES})
