#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan.packager import ConanMultiPackager
from conans.errors import ConanException
from conans.tools import get_env, environment_append
import os

if __name__ == "__main__":

    build_vulkan_lunarg_installer = get_env("BUILD_VULKAN_LUNARG_INSTALLER", False)

    subdir = "vulkan_lunarg_installer" if build_vulkan_lunarg_installer else "vulkan_lunarg"
    builder = ConanMultiPackager(
        cwd=os.path.join(os.path.dirname(os.path.realpath(__file__)), subdir),
        docker_entry_script="cd {}".format(subdir),
    )
    archs_str = get_env("ARCH")
    if not archs_str:
        raise ConanException("Need ARCH environment variable")
    archs = archs_str.split(",")

    archkey_str = "arch_build" if build_vulkan_lunarg_installer else "arch"

    for arch in archs:
        builder.add(settings={archkey_str: arch, })

    with environment_append({"LUNARG_HUMAN": "1"}):
        builder.run()
