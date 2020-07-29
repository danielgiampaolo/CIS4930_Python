cmake_minimum_required(VERSION 3.2)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project("netview")
set(SOURCE_FILES csv_parser.cpp)

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})