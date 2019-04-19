# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools, RunEnvironment


class VulkanTestConan(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'
    generators = 'cmake'

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin")

    def test(self):
        if not tools.cross_building(self.settings):
            with tools.chdir(os.path.join(self.build_folder, "bin")):
                with tools.environment_append(RunEnvironment(self).vars):
                    bin_path = "test_package"
                    if self.settings.os == "Windows":
                        self.run("{}.exe".format(bin_path))
                    elif self.settings.os == "Macos":
                        self.run("DYLD_LIBRARY_PATH={} ./{}".format(os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path))
                    else:
                        self.run("LD_LIBRARY_PATH={} ./{}".format(os.environ.get('LD_LIBRARY_PATH', ''), bin_path))
