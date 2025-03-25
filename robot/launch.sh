#!/bin/bash

cleanup() {
    echo "Cleaning up..."
    if [[ "$(basename $(pwd))" == "build" ]]; then
        echo "Currently in the build directory, returning to source directory..."
        cd "$SOURCE_DIR" || exit 1
    fi
    rm -rf build
}

build_project() {
    echo "Building the project..."
    mkdir -p build

    cd build || { echo "Failed to navigate to build directory"; cleanup; exit 1; }

    cmake .. || { echo "CMake configuration failed"; cleanup; exit 1; }

    make || { echo "Make failed"; cleanup; exit 1; }

    echo "Build successful"
}

run_executable() {
    echo "Running the executable..."
    ./robot || { echo "Failed to run the executable"; cleanup; exit 1; }
}

case "$1" in
    1)
        build_project
        ;;
    2)
        run_executable
        ;;
    3)
        build_project 
        run_executable  
        cleanup    
        ;;
    4)
        cleanup 
        ;;
    *)
        echo "Invalid argument. Use:"
        echo "1: Build"
        echo "2: Run"
        echo "3: Build, Run, Clean"
        echo "4: Clean"
        exit 1
        ;;
esac

