# -*- coding: utf-8 -*-

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import get_env
import os
import tempfile


class VulkanLunarGBase(ConanFile):
    version = "1.1.106.0"
    description = "The LunarG Vulkan SDK provides the development and runtime components required to build, run, and debug Vulkan applications."
    url = "https://github.com/bincrafters/conan-vulkan_lunarg"
    homepage = "https://vulkan.lunarg.com/sdk/home"
    topics = ("conan", "vulkan", "vk", "rendering", "metal", "moltenvk")
    author = "bincrafters <bincrafters@gmail.com>"
    no_copy_source = True

    license = "Various"
    exports = ["LICENSE.md"]

    _source_subfolder = "source_subfolder"

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

    def system_requirements(self):
        self.output.warn("in system_requirements")
        if tools.os_info.with_apt or tools.os_info.with_yum:
            if tools.os_info.with_apt:
                self.output.warn("apt detected")
                packages = [
                    "libwayland-dev",
                    "libxrandr-dev",
                ]
            elif tools.os_info.with_yum:
                self.output.warn("yum detected")
                packages = [
                    "wayland-devel",
                    "libXrandr-devel",
                ]
            installer = tools.SystemPackageTool()
            for package in packages:
                installer.install(package)

    def configure(self):
        if self._os != "Windows" and self._arch != "x86_64":
            raise ConanInvalidConfiguration("LunarG Vulkan SDK only supports 64-bit on non-Windows targets")

    def build(self):
        if self._os == "Windows":
            filename = "VulkanSDK-{version}-Installer.exe".format(version=self.version)
            url = "https://sdk.lunarg.com/sdk/download/{}/windows/{}".format(self.version, filename)
            sha256 = "24b5c9d415912c0fb07f973f10f671a488b0e33ca991409bcabf1d4bebf0b804"
        elif self._os == "Linux":
            filename = "vulkansdk-linux-{arch}-{version}.tar.gz".format(arch=self._arch, version=self.version)
            url = "https://sdk.lunarg.com/sdk/download/{}/linux/{}".format(self.version, filename)
            sha256 = "78739f6418f10bc9784743ab3d297b278106663256fe8b7482edfea6c65c7ec3"
        elif self._os == "Macos":
            filename = "vulkansdk-macos-{arch}-{version}.tar.gz".format(arch=self._arch, version=self.version)
            url = "https://sdk.lunarg.com/sdk/download/{}/mac/{}".format(self.version, filename)
            sha256 = "3806e7d0550ee00c61ae5ea45e9e87babcd952f1b4705232dc420ddc3e865314"
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
                outdir=self._source_subfolder,
                archive=targetdlfn,
            ))
        else:
            tools.untargz(targetdlfn, self.build_folder)
            if self._os == "Linux":
                os.rename(self.version, self._source_subfolder)
            else:
                os.rename("vulkansdk-macos-{}".format(self.version), self._source_subfolder)

        if self._os == "Linux":
            tools.replace_in_file(os.path.join(self._source_subfolder, "build_tools.sh"),
                                  "python2 ",
                                  "python ")
            tools.replace_in_file(os.path.join(self._source_subfolder, "source", "shaderc", "update_shaderc_sources.py"),
                                  "cmp=lambda x,y: cmp(x.subdir, y.subdir)",
                                  "key=lambda x: x.subdir")

            self.run("\"{}\"".format("{}/build_tools.sh".format(self._source_subfolder)))
            with tools.chdir(os.path.join(self._source_subfolder, "x86_64", "bin")):
                for file in os.listdir("."):
                    self.run("strip \"{}\"".format(file))
