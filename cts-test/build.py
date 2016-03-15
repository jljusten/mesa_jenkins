#!/usr/bin/python

import os
import sys
import xml.etree.ElementTree  as ET

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), ".."))
import build_support as bs

            
class CtsBuilder:
    def __init__(self):
        o = bs.Options()
        pm = bs.ProjectMap()
        self.build_root = pm.build_root()
        libdir = "x86_64-linux-gnu"
        if o.arch == "m32":
            libdir = "i386-linux-gnu"
        self.env = { "LD_LIBRARY_PATH" : self.build_root + "/lib:" + \
                     self.build_root + "/lib/" + libdir + ":" + self.build_root + "/lib/dri",
                     "LIBGL_DRIVERS_PATH" : self.build_root + "/lib/dri",
                     "GBM_DRIVERS_PATH" : self.build_root + "/lib/dri",
                     # fixes dxt subimage tests that fail due to a
                     # combination of unreasonable tolerances and possibly
                     # bugs in debian's s2tc library.  Recommended by nroberts
                     "S2TC_DITHER_MODE" : "NONE",
                     # forces deqp to run headless
                     "EGL_PLATFORM" : "surfaceless"}
        o.update_env(self.env)

    def build(self):
        pass

    def clean(self):
        pass

    def test(self):
        o = bs.Options()
        pm = bs.ProjectMap()

        mesa_version = bs.PiglitTester().mesa_version()
        if o.hardware == "bxt" or o.hardware == "kbl":
            if "11.0" in mesa_version:
                print "WARNING: bxt/kbl not supported by stable mesa"
                return

        conf_file = bs.get_conf_file(o.hardware, o.arch, "cts-test")

        savedir = os.getcwd()
        cts_dir = self.build_root + "/bin/cts"
        os.chdir(cts_dir)

        # invoke piglit
        self.env["PIGLIT_CTS_BIN"] = cts_dir + "/glcts"
        out_dir = self.build_root + "/test/" + o.hardware

        include_tests = []
        if o.retest_path:
            testlist = bs.TestLister(o.retest_path + "/test/")
            include_tests = testlist.RetestIncludes(project="cts-test")
            if not include_tests:
                # we were supposed to retest failures, but there were none
                return

        extra_excludes = []
        if ("ilk" in o.hardware or "g33" in o.hardware
            or "g45" in o.hardware or "g965" in o.hardware):
            extra_excludes = extra_excludes + ["--exclude-tests", "es3-cts",
                                               "--exclude-tests", "es31-cts"]

        if ("snb" in o.hardware or
            "ivb" in o.hardware or
            "byt" in o.hardware or
            "hsw" in o.hardware):
            extra_excludes += ["--exclude-tests", "es31-cts"]
            
        cmd = [self.build_root + "/bin/piglit",
               "run",
               #"-p", "gbm",
               "-b", "junit",
               "--config", conf_file,
               "-c",
               "--exclude-tests", "esext-cts",
               "--junit_suffix", "." + o.hardware + o.arch] + \
               extra_excludes + \
               include_tests + ["cts", out_dir]

        bs.run_batch_command(cmd, env=self.env,
                             expected_return_code=None,
                             streamedOutput=True)
        os.chdir(savedir)
        single_out_dir = self.build_root + "/../test"
        if not os.path.exists(single_out_dir):
            os.makedirs(single_out_dir)

        if os.path.exists(out_dir + "/results.xml"):
            # Uniquely name all test files in one directory, for
            # jenkins
            filename_components = ["/piglit-cts",
                                   o.hardware,
                                   o.arch]
            if o.shard != "0":
                # only put the shard suffix on for non-zero shards.
                # Having _0 suffix interferes with bisection.
                filename_components.append(o.shard)

            revisions = bs.RepoSet().branch_missing_revisions()
            print "INFO: filtering tests from " + out_dir + "/results.xml"
            self.filter_tests(revisions,
                              out_dir + "/results.xml",
                              single_out_dir + "_".join(filename_components) + ".xml")

            # create a copy of the test xml in the source root, where
            # jenkins can access it.
            cmd = ["cp", "-a", "-n",
                   self.build_root + "/../test", pm.source_root()]
            bs.run_batch_command(cmd)
            bs.Export().export_tests()
        else:
            print "ERROR: no results at " + out_dir + "/results.xml"

        bs.check_gpu_hang()

    def filter_tests(self, revisions, infile, outfile):
        """this method is ripped bleeding from builders.py / PiglitTester"""
        t = ET.parse(infile)
        for a_suite in t.findall("testsuite"):
            # remove skipped tests, which uses ram on jenkins when
            # displaying and provides no value.  
            for a_skip in a_suite.findall("testcase/skipped/.."):
                if a_skip.attrib["status"] in ["crash", "fail"]:
                    continue
                a_suite.remove(a_skip)

            # for each failure, see if there is an entry in the config
            # file with a revision that was missed by a branch
            for afail in a_suite.findall("testcase/failure/..") + a_suite.findall("testcase/error/.."):
                piglit_test = bs.PiglitTest("foo", "foo", afail)
                regression_revision = piglit_test.GetConfRevision()
                abbreviated_revisions = [a_rev[:6] for a_rev in revisions]
                for abbrev_rev in abbreviated_revisions:
                    if abbrev_rev in regression_revision:
                        print "stripping: " + piglit_test.test_name + " " + regression_revision
                        a_suite.remove(afail)
                        # a test may match more than one revision
                        # encoded in a comment
                        break
                
        t.write(outfile)

class SlowTimeout:
    def __init__(self):
        self.hardware = bs.Options().hardware

    def GetDuration(self):
        return 500

bs.build(CtsBuilder(), time_limit=SlowTimeout())
        
