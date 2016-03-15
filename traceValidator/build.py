#!/usr/bin/python

import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), ".."))
import build_support as bs

class TraceValidator(object):
    def __init__(self):
        self.pm = bs.ProjectMap()
        self.build_root = self.pm.build_root()
        self.data = "/mnt/jenkins/results/traceValidator/"
        self.data_dir = self.build_root + "/data"
        # self.data = "/home/majanes/tmp/data/"

    def build(self):
        pass
    def clean(self):
        bs.rmtree(self.data_dir)
    def test(self):
        libdir = "x86_64-linux-gnu"
        o = bs.Options()
        if o.arch == "m32":
            libdir = "i386-linux-gnu"
        env = { "LD_LIBRARY_PATH" : self.build_root + "/lib:" + \
                self.build_root + "/lib/" + libdir + ":" + \
                self.build_root + "/lib/dri",
                "LIBGL_DRIVERS_PATH" : self.build_root + "/lib/dri",
                "GBM_DRIVERS_PATH" : self.build_root + "/lib/dri",
                # Set the path to include buildroot/bin so fast skipping works
                'PATH': '{}:{}'.format(os.path.join(self.build_root, 'bin'),
                                       os.environ['PATH'])}

        bs.run_batch_command(["rsync", "-rlptD", 
                              self.data, self.data_dir])

        # invoke script file on each of the files in the data dir
        # look for run_batch_command
        processor = os.path.dirname(os.path.abspath(sys.argv[0])) + "/imageprocessor.py"
        for a_file in os.listdir(self.data_dir):
            
            (out, err) = bs.run_batch_command(["python", processor, "verify",
                                               "-a", self.data_dir + "/" + a_file, "-t", "10"],
                                              env=env)
            if out:
                print "out: " + out
            if err:
                print "err: " + err
        # str lookup for PASS/FAIL from the out result


bs.build(TraceValidator())

