#!/usr/bin/python
#/*
# * Copyright @2016 Intel Corporation
# *
# * Permission is hereby granted, free of charge, to any person obtaining a
# * copy of this software and associated documentation files (the "Software"),
# * to deal in the Software without restriction, including without limitation
# * the rights to use, copy, modify, merge, publish, distribute, sublicense,
# * and/or sell copies of the Software, and to permit persons to whom the
# * Software is furnished to do so, subject to the following conditions:
#
# * The above copyright notice and this permission notice shall be included
# * in all copies or substantial portions of the Software.
# *
# * You should have received a copy of the MIT License,
# * If not, see <https://opensource.org/licenses/MIT>.
# *
# * Author: Sirisha Gandikota <sirisha.gandikota@intel.com>
#
# DEPENDENCIES:
# APITrace (https://github.com/apitrace/apitrace) installed on your system
# Python Image Library (PIL) installed
# python-numpy installed on your system
#
# */

import Image
import ImageChops
import tarfile
import subprocess
import sys
import tempfile
import shutil
import os
from numpy import mean, sqrt, square
import argparse


######### generate() ###########
def generate(traceFile, frameNo, archFile):
    cmd = "glretrace --headless --snapshot=" + frameNo + " " + traceFile
    targetImgFile = frameNo + ".png"
    mvCmd = "mv *" + frameNo + ".png " + targetImgFile
    frameFile = "frameNum.txt"

    # Write the frame number to a file
    fp = open(frameFile, 'w')
    fp.write(frameNo)
    fp.close()

    # Extract image from tracefile
    print("Generating archive file, please wait...")
    retCode = subprocess.call(cmd, shell=True)
    retCode = subprocess.call(mvCmd, shell=True)

    #Tar the tracefile and imagefile
    tar = tarfile.open(archFile, "w:gz")
    tar.add(traceFile)
    tar.add(frameFile)
    tar.add(targetImgFile)
    tar.close()
    print(("Generated archive file " + archFile))

    #Delete intermediary files
    os.remove(frameFile)
    os.remove(targetImgFile)
    return retCode


########## verify() ############
def verify(archFile, threshold):
    tmpDir = tempfile.mkdtemp(prefix='tmp') + "/"
    frameNo = 0
    frameFile = tmpDir + "frameNum.txt"
    traceFile = tmpDir + "*.trace"
    sourceImgFile = ""
    targetImgFile = ""

    # untar the tar file
    tar = tarfile.open(archFile, "r:gz")
    tar.extractall(tmpDir)
    tar.close()

    #Extract image from tracefile
    fp = open(frameFile, "r")
    frameNo = fp.readline()
    fp.close()
    sourceImgFile = tmpDir + frameNo + ".png"

    cmd = "glretrace --headless --snapshot=" + frameNo + " " + traceFile
    targetImgFile = tmpDir + frameNo + "_target.png"
    mvCmd = "mv " + "?*" + frameNo + ".png " + targetImgFile
    print("Verification in progress, please wait...")
    retCode = subprocess.call(cmd, shell=True)
    retCode = subprocess.call(mvCmd, shell=True)

    #compare the image from tar and extracted image
    img1 = Image.open(targetImgFile)
    img2 = Image.open(sourceImgFile)

    diff = ImageChops.difference(img1, img2)
    diff.save(tmpDir + "image_diff.png")

    hist1 = img1.histogram()
    hist2 = img2.histogram()

    # Find rms error between the image histograms
    rmse = sqrt(mean(square([(hist1[i] - hist2[i]) for i in range(len(hist1))])))
    print(("RMSE = " + str(rmse) + ", Threshold = " + str(threshold)))

    if int(rmse) > int(threshold):
        print("FAIL")
    else:
        print("PASS")

    #Clean up tmp folder
    shutil.rmtree(tmpDir)
    return retCode


########## main() ############
def main(argv):
    usageMsg = "Usage: \n python imagecompare.py generate  -i <tracefile> -f <f no> -a <output.tar.gz> \n python imagecompare.py verify  -a <output.tar.gz> -t <threshold>\n "
    traceFile = ''
    archFile = ''
    frameNo = 0
    cmdFunc = ''
    retVal = 0
    threshold = 0

    #Scan inputs
    parser = argparse.ArgumentParser(usage=usageMsg)
    parser.add_argument("cmd")
    parser.add_argument("-i", "--ifile", dest="traceFile", help="trace file", metavar="FILE")
    parser.add_argument("-f", "--frameNo", dest="frameNo")
    parser.add_argument("-a", "--afile", dest="archFile", help="archive file", metavar="FILE")
    parser.add_argument("-t", "--threshold", type=int, dest="threshold")

    args = parser.parse_args()

    cmdFunc = args.cmd
    traceFile = args.traceFile
    frameNo = args.frameNo
    archFile = args.archFile
    threshold = args.threshold

    if cmdFunc == 'generate':
        if len(sys.argv) != 8:
            print((usageMsg))
            sys.exit()
        else:
            retVal = generate(traceFile, frameNo, archFile)
    elif cmdFunc == 'verify':
        if len(sys.argv) != 6:
            print((usageMsg))
            sys.exit()
        else:
            retVal = verify(archFile, threshold)

    return retVal


if __name__ == "__main__":
    main(sys.argv[1:])
