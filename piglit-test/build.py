#!/usr/bin/python

class SlowTimeout:

    def GetDuration(self):
        
# add the --piglit_test option to the standard options.  Parse the
# options, and strip the piglit_test so the options will work as usual
# for subsequent objects.
o = bs.CustomOptions("piglit args allow a specific test")
o.add_argument(arg='--piglit_test', type=str, default="",
                    help="single piglit test to run.")
o.parse_args()

piglit_test = ""
if o.piglit_test:
    piglit_test = o.piglit_test

bs.build(bs.PiglitTester(_suite="gpu",
                         piglit_test=piglit_test),
         time_limit=SlowTimeout())
