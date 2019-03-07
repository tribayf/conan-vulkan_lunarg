# -*- coding: utf-8 -*-

from collections import namedtuple
from conans import tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import get_env
import os
import tempfile


FetchMetadata = namedtuple("FetchMetadata", ("url", "filename", "sha256"))


class VulkanLunarGCommon:
    def __init__(self, conanfile):
        self.conanfile = conanfile

    @property
    def os(self):
        if self.conanfile._is_installer:
            return self.conanfile.settings.os_build
        else:
            return self.conanfile.settings.os

    @property
    def arch(self):
        if self.conanfile._is_installer:
            return self.conanfile.settings.arch_build
        else:
            return self.conanfile.settings.arch

    def configure(self):
        if self.os != "Windows" and self.arch != "x86_64":
            raise ConanInvalidConfiguration("LunarG Vulkan SDK only supports 64-bit")

    def get_fetch_metadata(self):
        if self.os == "Windows":
            filename = "VulkanSDK-{version}-Installer.exe".format(version=self.conanfile.version)
            url = "https://sdk.lunarg.com/sdk/download/{}/windows/{}".format(self.conanfile.version, filename)
            sha256 = "9161e719d23967592601eb385ef58ac7f4d9c18892dc8dbc1d431cb5a3957673"
        elif self.os == "Linux":
            filename = "vulkansdk-linux-{arch}-{version}.tar.gz".format(arch=self.arch, version=self.conanfile.version)
            url = "https://sdk.lunarg.com/sdk/download/{}/linux/{}".format(self.conanfile.version, filename)
            sha256 = "5cf01379a9f2606e2cd528d78ca2d8287e3fbc32f048f911eae07c94b2763bcd"
        elif self.os == "Macos":
            filename = "vulkansdk-macos-{arch}-{version}.tar.gz".format(arch=self.arch, version=self.conanfile.version)
            url = "https://sdk.lunarg.com/sdk/download/{}/macos/{}".format(self.conanfile.version, filename)
            sha256 = "b175849a1c609b561ef2406ced3f2e408af2970725a45f49547d03cefd5bbc39"
        else:
            raise ConanInvalidConfiguration("Unknown os: {}".format(self.os))

        # override ratelimit: limit of 5 downloads per url per 24h
        if get_env("LUNARG_HUMAN", False):
            url += "?Human=true"

        return FetchMetadata(url, filename, sha256)

    def fetch_data(self):
        fetch_data = self.get_fetch_metadata()

        targetdlfn = os.path.join(tempfile.gettempdir(), fetch_data.filename)

        if os.path.exists(targetdlfn) and not get_env("VULKAN_LUNARG_FORCE_DOWNLOAD", False):
            self.conanfile.output.info("Skipping download. Using cached {}".format(targetdlfn))
        else:
            self.conanfile.output.info("Downloading {} from {}".format(fetch_data.filename, fetch_data.url))
            tools.download(fetch_data.url, targetdlfn)
        tools.check_sha256(targetdlfn, fetch_data.sha256)

        return targetdlfn

    def build(self):
        targetdlfn = self.fetch_data()

        if self.os == "Windows":
            self.conanfile.run("\"{}\" /S".format(targetdlfn))
        else:
            tools.untargz(targetdlfn, self.conanfile.build_folder)
            if self.os == "Linux":
                os.rename(self.conanfile.version, "vulkansdk")
            else:
                os.rename("vulkansdk-macos-{version}".format(version=self.conanfile.version), "vulkansdk")
