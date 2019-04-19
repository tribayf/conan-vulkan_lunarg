#!/usr/bin/env python
# -*- coding: utf-8 -*-


from conans.tools import environment_append
from bincrafters import build_template_default

if __name__ == "__main__":

    builder = build_template_default.get_builder(pure_c=True)

    with environment_append({"LUNARG_HUMAN": "1"}):
        builder.run()
