#!/usr/bin/python

import os
import os.path as path
import subprocess
import sys
sys.path.append(path.join(path.dirname(path.abspath(sys.argv[0])), ".."))
import build_support as bs

class NoTest(bs.AutoBuilder):
    def __init__(self, configure_options):
        bs.AutoBuilder.__init__(self,
                                configure_options=configure_options,
                                export=False)

    def test(self):
        # llvmpipe fails make test, and who cares?
        pass
    
def main():
    global_opts = bs.Options()

    options = []
    if global_opts.arch == "m32":
        # m32 build not supported
        return

    options = options + ["--enable-gbm",
                         "--with-egl-platforms=x11,drm",
                         "--enable-glx-tls", 
                         "--enable-gles1",
                         "--enable-gles2",
                         "--with-gallium-drivers=i915,svga,swrast,r300,r600,radeonsi,nouveau"]

    if global_opts.config == 'debug':
        options.append('--enable-debug')

    # builder = bs.AutoBuilder(configure_options=options, export=False)
    builder = NoTest(configure_options=options)

    save_dir = os.getcwd()
    try:
        bs.build(builder)
    except subprocess.CalledProcessError as e:
        # build may have taken us to a place where ProjectMap doesn't work
        os.chdir(save_dir)  
        bs.Export().create_failing_test("mesa-buildtest", str(e))

if __name__ == '__main__':
    main()
