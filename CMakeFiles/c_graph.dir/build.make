# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.16

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/danielg/CIS4930_Python/src/graph

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/danielg/CIS4930_Python

# Include any dependencies generated for this target.
include CMakeFiles/c_graph.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/c_graph.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/c_graph.dir/flags.make

CMakeFiles/c_graph.dir/c_graph.cpp.o: CMakeFiles/c_graph.dir/flags.make
CMakeFiles/c_graph.dir/c_graph.cpp.o: src/graph/c_graph.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/danielg/CIS4930_Python/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/c_graph.dir/c_graph.cpp.o"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/c_graph.dir/c_graph.cpp.o -c /home/danielg/CIS4930_Python/src/graph/c_graph.cpp

CMakeFiles/c_graph.dir/c_graph.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/c_graph.dir/c_graph.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/danielg/CIS4930_Python/src/graph/c_graph.cpp > CMakeFiles/c_graph.dir/c_graph.cpp.i

CMakeFiles/c_graph.dir/c_graph.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/c_graph.dir/c_graph.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/danielg/CIS4930_Python/src/graph/c_graph.cpp -o CMakeFiles/c_graph.dir/c_graph.cpp.s

# Object files for target c_graph
c_graph_OBJECTS = \
"CMakeFiles/c_graph.dir/c_graph.cpp.o"

# External object files for target c_graph
c_graph_EXTERNAL_OBJECTS =

libc_graph.so: CMakeFiles/c_graph.dir/c_graph.cpp.o
libc_graph.so: CMakeFiles/c_graph.dir/build.make
libc_graph.so: CMakeFiles/c_graph.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/danielg/CIS4930_Python/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX shared library libc_graph.so"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/c_graph.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/c_graph.dir/build: libc_graph.so

.PHONY : CMakeFiles/c_graph.dir/build

CMakeFiles/c_graph.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/c_graph.dir/cmake_clean.cmake
.PHONY : CMakeFiles/c_graph.dir/clean

CMakeFiles/c_graph.dir/depend:
	cd /home/danielg/CIS4930_Python && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/danielg/CIS4930_Python/src/graph /home/danielg/CIS4930_Python/src/graph /home/danielg/CIS4930_Python /home/danielg/CIS4930_Python /home/danielg/CIS4930_Python/CMakeFiles/c_graph.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/c_graph.dir/depend

