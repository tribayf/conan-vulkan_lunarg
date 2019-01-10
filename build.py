from conan.packager import ConanMultiPackager
import os
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager()
    os.environ['LUNARG_HUMAN'] = '1'
    if platform.system() == 'Windows':
        builder.add(settings={'arch': 'x86'})
    builder.add(settings={'arch': 'x86_64'})
    builder.run()
