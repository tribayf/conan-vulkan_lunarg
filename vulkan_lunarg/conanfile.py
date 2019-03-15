# -*- coding: utf-8 -*-

import os
from conans import ConanFile
import sys


class VulkanLunarGConan(ConanFile):
    name = "vulkan_lunarg"
    version = "1.1.101.0"
    description = "The LunarG Vulkan SDK provides the development and runtime components required to build, run, and debug Vulkan applications."
    url = "https://github.com/bincrafters/conan-vulkan_lunarg"
    homepage = "https://vulkan.lunarg.com/sdk/home"
    topics = ("conan", "vulkan", "vk", "rendering", "metal", "moltenvk")
    author = "bincrafters <bincrafters@gmail.com>"
    no_copy_source = True

    license = "Various"
    exports = ["../LICENSE.md", "../vulkan_lunarg_common.py"]

    settings = "os", "arch"

    _is_installer = False

    _common = None
    def _add_common(self):
        curdir = os.path.dirname(os.path.realpath(__file__))
        pardir = os.path.dirname(curdir)
        sys.path.insert(0, curdir)
        sys.path.insert(0, pardir)
        from vulkan_lunarg_common import VulkanLunarGCommon
        self._common = VulkanLunarGCommon(self)

    def configure(self):
        self._add_common()
        self._common.configure()

    def build_requirements(self):
        self._add_common()
        self._common.build_requirements()

    def build(self):
        self._add_common()
        self._common.build()

    def package(self):
        if self.settings.os == "Windows":
            base_folder = os.path.join(self.build_folder, "vulkansdk")
            if self.settings.arch == "x86":
                lib_folder = os.path.join(base_folder, "Lib32")
                bin_folder = os.path.join(base_folder, "Bin32")
            elif self.settings.arch == "x86_64":
                lib_folder = os.path.join(base_folder, "Lib")
                bin_folder = os.path.join(base_folder, "Bin")
            self.copy(pattern="*", dst="lib", src=lib_folder)
            self.copy(pattern="*.dll", dst="bin", src=bin_folder)
            self.copy(pattern="*.pdb", dst="bin", src=bin_folder)
            self.copy(pattern="*", dst="include", src=os.path.join(base_folder, "Include"))
            self.copy(pattern="LICENSE.txt", dst="licenses", src=base_folder)
        elif self.settings.os == "Linux":
            base_folder = os.path.join(self.build_folder, "vulkansdk")
            base_pkg_folder = os.path.join(base_folder, str(self.settings.arch))
            self.copy(pattern="*", dst="include", src=os.path.join(base_pkg_folder, "include"))
            self.copy(pattern="*", dst="lib", src=os.path.join(base_pkg_folder, "lib"))
            self.copy(pattern="*", dst="bin", src=os.path.join(base_pkg_folder, "bin"))
            self.copy(pattern="*", dst="etc", src=os.path.join(base_pkg_folder, "etc"))
            self.copy(pattern="LICENSE.txt", dst="licenses", src=base_folder)
        elif self.settings.os == "Macos":
            base_folder = os.path.join(self.build_folder, "vulkansdk", "macOS")
            self.copy(pattern="*", dst="include", src=os.path.join(base_folder, "include"))
            self.copy(pattern="*", dst="lib", src=os.path.join(base_folder, "lib"))
            self.copy(pattern="*", dst="bin", src=os.path.join(base_folder, "bin"))
            self.copy(pattern="*", dst="etc", src=os.path.join(base_folder, "etc"))
            self.copy(pattern="*", dst="Frameworks", src=os.path.join(base_folder, "Frameworks"))

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["vulkan-1"]
        else:
            self.cpp_info.libs = ["vulkan"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = ["lib"]
