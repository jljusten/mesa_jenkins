#!/usr/bin/python


import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), ".."))
import build_support as bs

builder = bs.CMakeBuilder()

bs.build(builder)
