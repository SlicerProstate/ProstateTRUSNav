cmake_minimum_required(VERSION 2.8.9)

project(ProstateTrusNav)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "")
set(EXTENSION_CATEGORY "IGT")
set(EXTENSION_CONTRIBUTORS "")
set(EXTENSION_DESCRIPTION "")
set(EXTENSION_ICONURL "")
set(EXTENSION_SCREENSHOTURLS "")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(ProstateTrusNav)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
