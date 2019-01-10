# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools
from conans.util.env_reader import get_env
import tempfile


class LunarGVulkanSDKConan(ConanFile):
    name = 'vulkan_lunarg'
    version = '1.1.92.1'
    description = 'The LunarG Vulkan SDK provides the development and runtime components required to build, run, and debug Vulkan applications.'
    url = 'https://github.com/bincrafters/conan-lunarg_vulkan_sdk'
    homepage = 'https://vulkan.lunarg.com/sdk/home'
    author = 'bincrafters <bincrafters@gmail.com>'
    no_copy_source = True

    license = 'Various'
    exports = ['LICENSE.md']

    settings = 'os', 'arch'

    def build(self):
        prefix_url = 'https://sdk.lunarg.com/sdk/download/{version}'.format(version=self.version)
        win_name = 'VulkanSDK-{version}-Installer.exe'.format(version=self.version)
        win_url = '{prefix}/windows/{name}'.format(prefix=prefix_url, name=win_name)
        win_sha256 = '601c019b8dca1ecece47be279c7a77056fe081d2b5f1804ac9c5d80b7bef7fea'
        mac_name = 'vulkansdk-macos-{arch}-{version}'.format(arch=self.settings.arch, version=self.version)
        mac_url = '{prefix}/mac/{name}.tar.gz'.format(prefix=prefix_url, name=mac_name)
        mac_sha256 = {
            'x86_64': '1dc5c758ba83cc0b1e3baa533a5b2052afa378df87a84ee3e56ab6d97df12865',
        }
        lin_name = 'vulkansdk-linux-{arch}-{version}'.format(arch=self.settings.arch, version=self.version)
        lin_url = '{prefix}/linux/{name}.tar.gz'.format(prefix=prefix_url, name=lin_name)
        lin_sha256 = {
            'x86_64': 'bbbdce02334e078e54bd1d796a1d983073054f57379ecfb89aa4194020ad4c32',
        }

        if self.settings.os == 'Windows':
            url = win_url
            name = win_name
            sha256 = win_sha256
        else:
            if self.settings.os == 'Linux':
                url = lin_url
                sha256 = lin_sha256[str(self.settings.arch)]
                name = lin_name
            elif self.settings.os == 'Macos':
                url = mac_url
                sha256 = mac_sha256[str(self.settings.arch)]
                name = mac_name

        targetdlfn = '{}'.format(os.path.join(tempfile.gettempdir(), name))
        if self.settings.os != 'Windows':
            targetdlfn += '.tar.gz'

        # cache downloads because lunarg has rate limit of 5 downloads per url per 24h
        # (this ratelimit can be overridden by adding "?human=true" to the url
        if get_env('LUNARG_HUMAN', False):
            url += '?Human=true'
        if os.path.exists(targetdlfn) and not get_env('LUNARG_FORCE_DOWNLOAD', False):
            self.output.info('Skipping download. Using cached {}'.format(targetdlfn))
        else:
            self.output.info('Downloading sdk from {} to {}'.format(url, targetdlfn))
            tools.download(url, targetdlfn)
        tools.check_sha256(targetdlfn, sha256)

        if self.settings.os == 'Windows':
            self.run('"{}" /S'.format(targetdlfn))
        else:
            tools.untargz(targetdlfn, self.build_folder)
            if self.settings.os == 'Linux':
                os.rename(self.version, 'vulkansdk')
            else:
                os.rename('vulkansdk-macos-{version}'.format(version=self.version), 'vulkansdk')

        if self.settings.os == 'Macos':
            possible_broken_symlink = os.path.join(self.build_folder, 'vulkansdk', 'macOS', 'lib', 'libshaderc_shared.dylib')
            if not os.path.exists(possible_broken_symlink):
                try:
                    os.remove(possible_broken_symlink)
                except FileNotFoundError:
                    pass

    def package(self):
        if self.settings.os == 'Windows':
            base_folder = 'C:\\VulkanSDK\\{version}'.format(version=self.version)
            if self.settings.arch == 'x86':
                lib_folder = os.path.join(base_folder, 'Lib32')
                bin_folder = os.path.join(base_folder, 'Bin32')
            elif self.settings.arch == 'x86_64':
                lib_folder = os.path.join(base_folder, 'Lib')
                bin_folder = os.path.join(base_folder, 'Bin')
            self.copy(pattern='*', dst='lib', src=lib_folder)
            self.copy(pattern='*.dll', dst='bin', src=bin_folder)
            self.copy(pattern='*.pdb', dst='bin', src=bin_folder)
            self.copy(pattern='*', dst='include', src=os.path.join(base_folder, 'Include'))
            self.copy(pattern='LICENSE.txt', dst='licenses', src=base_folder)
        elif self.settings.os == 'Linux':
            base_folder = os.path.join(self.build_folder, 'vulkansdk')
            base_pkg_folder = os.path.join(base_folder, str(self.settings.arch))
            self.copy(pattern='*', dst='include', src=os.path.join(base_pkg_folder, 'include'))
            self.copy(pattern='*', dst='lib', src=os.path.join(base_pkg_folder, 'lib'))
            self.copy(pattern='*', dst='bin', src=os.path.join(base_pkg_folder, 'bin'))
            self.copy(pattern='*', dst='etc', src=os.path.join(base_pkg_folder, 'etc'))
            self.copy(pattern='LICENSE.txt', dst='licenses', src=base_folder)
        elif self.settings.os == 'Macos':
            base_folder = os.path.join(self.build_folder, 'vulkansdk', 'macOS')
            self.copy(pattern='*', dst='include', src=os.path.join(base_folder, 'include'))
            self.copy(pattern='*', dst='lib', src=os.path.join(base_folder, 'lib'))
            self.copy(pattern='*', dst='bin', src=os.path.join(base_folder, 'bin'))
            self.copy(pattern='*', dst='etc', src=os.path.join(base_folder, 'etc'))
            self.copy(pattern='*', dst='Frameworks', src=os.path.join(base_folder, 'Frameworks'))

    def package_info(self):
        if self.settings.os == 'Windows':
            self.cpp_info.libs = ['vulkan-1']
        else:
            self.cpp_info.libs = ['vulkan']
        self.cpp_info.includedirs = ['include']
        self.cpp_info.bindirs = ['bin']
        self.cpp_info.libdirs = ['lib']
