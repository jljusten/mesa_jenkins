#!/usr/bin/python

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), ".."))
import build_support as bs

class CrucibleBuilder(bs.AutoBuilder):
    def __init__(self):
        self._pm = bs.ProjectMap()
        glslc = "GLSLC=" + self._pm.build_root() + "/bin/glslc"
        mesa_lib = "MESA_LDFLAGS=-L" + self._pm.build_root() + "/lib"
        mesa_include = "MESA_CPPFLAGS=-I" + os.path.abspath(self._pm.project_source_dir() + "/../mesa/include")
        bs.AutoBuilder.__init__(self, configure_options=[glslc, mesa_lib, mesa_include])
        self._build_dir = self._src_dir

    def build(self):
        # libvulkan has been renamed libvulkan_intel.so
        lib_dir = self._build_root + "/lib/"
        if not os.path.exists(lib_dir):
            os.makedirs(lib_dir)
        if not os.path.islink(lib_dir + "libvulkan.so"):
            os.symlink("libvulkan_intel.so", lib_dir + "libvulkan.so")

        bs.AutoBuilder.build(self)
        bin_dir = self._build_root + "/bin/"
        if not os.path.exists(bin_dir):
            os.makedirs(bin_dir)
        bs.run_batch_command(["cp", "-a", "-n",
                              self._build_dir + "/bin/crucible",
                              bin_dir])
        bs.run_batch_command(["cp", "-a", "-n",
                              self._build_dir + "/data/",
                              self._build_root])
        bs.Export().export()

bs.build(CrucibleBuilder())


