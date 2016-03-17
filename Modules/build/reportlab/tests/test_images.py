#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__version__='''$Id$'''
__doc__="""Tests to do with image handling.

Most of them make use of test\pythonpowereed.gif."""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, printLocation
setOutDir(__name__)
import os
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
import unittest
from reportlab.lib.utils import ImageReader


"""To avoid depending on external stuff, I made a small 5x5 image and
attach its 'file contents' here in several formats.

The image looks like this, with K=black, R=red, G=green, B=blue, W=white.
    K R G B W
    K R G B W
    K R G B W
    K R G B W
    K R G B W
"""
sampleRAW = '\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\xff\xff\xff'
samplePNG = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x05\x00\x00\x00\x05\x08\x02\x00\x00\x00\x02\r\xb1\xb2\x00\x00\x00:IDATx\x9cb```\xf8\x0f\xc3\xff\xff\xff\x07\x00\x00\x00\xff\xffbb@\x05\x00\x00\x00\x00\xff\xffB\xe7\x03\x00\x00\x00\xff\xffB\xe7\x03\x00\x00\x00\xff\xffB\xe7\x03\x00\x00\x00\xff\xff\x03\x00\x9e\x01\x06\x03\x03\xc4A\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

class ReaderTestCase(unittest.TestCase):
    "Simplest tests to import images, work under Jython or PIL"

    def test(self):
        from reportlab.lib.testutils import testsFolder
        from reportlab.lib.utils import rl_isfile
        imageFileName = os.path.join(testsFolder,'pythonpowered.gif')
        assert rl_isfile(imageFileName), "%s not found!" % imageFileName
        ir = ImageReader(imageFileName)
        assert ir.getSize() == (110,44)
        pixels = ir.getRGBData()
        assert md5(pixels).hexdigest() == '02e000bf3ffcefe9fc9660c95d7e27cf'

def makeSuite():
    return makeSuiteForClasses(ReaderTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
