# -*- coding: utf-8 -*-

from conans import ConanFile, tools, RunEnvironment


class VulkanTestConan(ConanFile):
    exports_sources = ['shader.frag', ]

    def test(self):
        self.run('glslangValidator -V "{}/shader.frag"'.format(self.source_folder))
