# -*- coding: utf-8 -*-

from conans import ConanFile, tools, RunEnvironment


class VulkanTestConan(ConanFile):
    exports_sources = 'shader.frag'

    def test(self):
        if not tools.cross_building(self.settings):
            with tools.environment_append(RunEnvironment(self).vars):
                self.run('glslangValidator -V "{}/shader.frag"'.format(self.source_folder))
