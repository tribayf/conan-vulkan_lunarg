# -*- coding: utf-8 -*-

import os
from vulkan_lunarg_common import  VulkanLunarGBase


class VulkanLunarGInstallerConan(VulkanLunarGBase):
    name = "vulkan_lunarg_installer"
    version = "1.1.106.0"
    exports = VulkanLunarGBase.exports + ["vulkan_lunarg_common.py"]
    settings = "os_build", "arch_build"

    _is_installer = True

    def package(self):
        if self.settings.os_build == "Windows":
            base_folder = os.path.join(self.build_folder, self._source_subfolder)
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
            base_folder = os.path.join(self.build_folder, self._source_subfolder)
            bin_folder = os.path.join(base_folder, str(self.settings.arch_build), "bin")
            self.copy(pattern="*", dst="bin", src=bin_folder)
            self.copy(pattern="LICENSE.txt", dst="licenses", src=base_folder)
        elif self.settings.os_build == "Macos":
            base_folder = os.path.join(self.build_folder, self._source_subfolder, "macOS")
            self.copy(pattern="*", dst="bin", src=os.path.join(base_folder, "bin"))

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        if self.settings.os_build == "Windows":
            self.cpp_info.bindirs.append("bin/tools")

        for bindir in self.cpp_info.bindirs:
            bindir_fullpath = os.path.join(self.package_folder, bindir)
            self.output.info("Appending PATH environment variable: {}".format(bindir_fullpath))
            self.env_info.PATH.append(bindir_fullpath)
