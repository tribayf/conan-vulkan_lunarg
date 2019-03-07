# -*- coding: utf-8 -*-

import os
from conans import ConanFile
import sys


class LunarGVulkanSDKInstallerConan(ConanFile):
    name = "vulkan_lunarg_installer"
    version = "1.1.101.0"
    description = "The LunarG Vulkan SDK provides the development and runtime components required to build, run, and debug Vulkan applications."
    url = "https://github.com/bincrafters/conan-lunarg_vulkan_sdk"
    homepage = "https://vulkan.lunarg.com/sdk/home"
    topics = ("conan", "vulkan", "vk", "rendering", "metal", "moltenvk")
    author = "bincrafters <bincrafters@gmail.com>"
    no_copy_source = True

    license = "Various"
    exports = ["../LICENSE.md", "../vulkan_lunarg_common.py"]

    settings = "os_build", "arch_build"

    _is_installer = True

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

    def build(self):
        self._add_common()
        self._common.build()
                
    def package(self):
        if self.settings.os_build == "Windows":
            base_folder = "C:\\VulkanSDK\\{version}".format(version=self.version)
            if self.settings.arch_build == "x86":
                bin_folder = os.path.join(base_folder, "Bin32")
                tools_folder = os.path.join(base_folder, "Tools32")
            elif self.settings.arch_build == "x86_64":
                bin_folder = os.path.join(base_folder, "Bin")
                tools_folder = os.path.join(base_folder, "Tools")
            self.copy(pattern="*.exe", dst="bin", src=bin_folder)
            self.copy(pattern="*", dst="bin/tools", src=tools_folder)
            self.copy(pattern="LICENSE.txt", dst="licenses", src=base_folder)
        elif self.settings.os_build == "Linux":
            base_folder = os.path.join(self.build_folder, "vulkansdk")
            self.copy(pattern="LICENSE.txt", dst="licenses", src=base_folder)
            bin_folder = os.path.join(base_folder, str(self.settings.arch_build), "bin")
            self.copy(pattern="*", dst="bin", src=bin_folder)
        elif self.settings.os_build == "Macos":
            base_folder = os.path.join(self.build_folder, "vulkansdk", "macOS")
            self.copy(pattern="*", dst="bin", src=os.path.join(base_folder, "bin"))

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        if self.settings.os_build == "Windows":
            self.cpp_info.bindirs.append("bin/tools")

        for bindir in self.cpp_info.bindirs:
            bindir_fullpath = os.path.join(self.package_folder, bindir)
            self.output.info("Appending PATH environment variable: {}".format(bindir_fullpath))
            self.env_info.PATH.append(bindir_fullpath)
