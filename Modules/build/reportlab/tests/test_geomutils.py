#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__version__='''$Id$'''
__doc__="""Tests for geometry utility functions."""

import unittest
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses
setOutDir(__name__)

class GeomTestCase(unittest.TestCase):

    def test_padding(self):
        "Test reportlab.lib.boxstuff.normalizePadding."
        from reportlab.lib.geomutils import normalizeTRBL

        paddings = (
            (4, (4, 4, 4, 4)),
            ((0, 1), (0, 1, 0, 1)),
            ((0, 1, 2), (0, 1, 2, 1)),
            ((0, 1, 2, 3), (0, 1, 2, 3)),
        )
        
        for pin, pout in paddings:
            pres = normalizeTRBL(pin)
            assert pres == pout, "normalizeTRBL(%s) returned %s, expected %s" % (pin, pres, pout)

def makeSuite():
    return makeSuiteForClasses(GeomTestCase)

if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
