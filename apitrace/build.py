#!/usr/bin/python


import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), ".."))
import build_support as bs

class ApiTraceBuilder(bs.CMakeBuilder):
    def __init__(self):
        bs.CMakeBuilder.__init__(self)

    def build(self):
        pm = bs.ProjectMap()
        save_dir = os.getcwd()
        os.chdir(self._src_dir)
        try:
            bs.run_batch_command(["patch", "-p1", "retrace/glws_xlib.cpp",
                                  pm.project_build_dir("apitrace") + "/headless.patch"])
        except:
            print "WARN: failed to apply headless patch"
        os.chdir(save_dir)
        bs.CMakeBuilder.build(self)
        
bs.build(ApiTraceBuilder())
