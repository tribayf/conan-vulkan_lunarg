# -*- coding: utf-8 -*-

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import get_env
import os
import tempfile


class VulkanLunarGBase(ConanFile):
    version = "1.1.114.0"
    description = "The LunarG Vulkan SDK provides the development and runtime components required to build, run, and debug Vulkan applications."
    url = "https://github.com/bincrafters/conan-vulkan_lunarg"
    homepage = "https://vulkan.lunarg.com/sdk/home"
    topics = ("conan", "vulkan", "vk", "rendering", "metal", "moltenvk")
    author = "bincrafters <bincrafters@gmail.com>"
    no_copy_source = True

    license = "Various"
    exports = ["LICENSE.md"]

    @property
    def _os(self):
        if self._is_installer:
            return self.settings.os_build
        else:
            return self.settings.os

    @property
    def _arch(self):
        if self._is_installer:
            return self.settings.arch_build
        else:
            return self.settings.arch

    def build_requirements(self):
        if self._os == "Windows":
            self.build_requires("7z_installer/1.0@conan/stable")

    def configure(self):
        if self._os != "Windows" and self._arch != "x86_64":
            raise ConanInvalidConfiguration("LunarG Vulkan SDK only supports 64-bit on non-Windows targets")

    def build(self):
        if self._os == "Windows":
            filename = "VulkanSDK-{version}-Installer.exe".format(version=self.version)
            url = "https://sdk.lunarg.com/sdk/download/{}/windows/{}".format(self.version, filename)
            sha256 = "6233e3095b67b883a55b4fa61fd0376feecb1de1e0a7b3962fa7a85cdd0e663f"
        elif self._os == "Linux":
            filename = "vulkansdk-linux-{arch}-{version}.tar.gz".format(arch=self._arch, version=self.version)
            url = "https://sdk.lunarg.com/sdk/download/{}/linux/{}".format(self.version, filename)
            sha256 = "796d3eedea9d2f5fd0720e5ebd9cc6072c95d5e958abea6d07b121db3973e968"
        elif self._os == "Macos":
            filename = "vulkansdk-macos-{arch}-{version}.tar.gz".format(arch=self._arch, version=self.version)
            url = "https://sdk.lunarg.com/sdk/download/{}/mac/{}".format(self.version, filename)
            sha256 = "db5df93d10b7f689daad9a455baa4eeacb36826edc8270b45585559a4fbb5569"
        else:
            raise ConanInvalidConfiguration("Unknown os: {}".format(self._os))

        # override ratelimit: limit of 5 downloads per url per 24h
        if get_env("LUNARG_HUMAN", False):
            url += "?Human=true"

        targetdlfn = os.path.join(tempfile.gettempdir(), filename)

        if os.path.exists(targetdlfn) and not get_env("VULKAN_LUNARG_FORCE_DOWNLOAD", False):
            self.output.info("Skipping download. Using cached {}".format(targetdlfn))
        else:
            self.output.info("Downloading {} from {}".format(filename, url))
            tools.download(url, targetdlfn)
        tools.check_sha256(targetdlfn, sha256)

        if self._os == "Windows":
            self.run("7z x -snl -y -mmt{cpu_count} -o\"{outdir}\" \"{archive}\"".format(
                cpu_count=tools.cpu_count(),
                outdir="vulkansdk",
                archive=targetdlfn,
            ))
        else:
            tools.untargz(targetdlfn, self.build_folder)
            if self._os == "Linux":
                os.rename(self.version, "vulkansdk")
            else:
                os.rename("vulkansdk-macos-{}".format(self.version), "vulkansdk")
