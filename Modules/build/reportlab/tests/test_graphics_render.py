#Copyright ReportLab Europe Ltd. 2000-2014
#see license.txt for license details
"""
Tests for renderers
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest, os, sys, glob
from reportlab.lib.utils import isPy3

class RenderTestCase(unittest.TestCase):
    "Test renderPS classes."

    @classmethod
    def setUpClass(cls):
        cls.outDir = outDir = outputfile('render-out')
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
        for x in glob.glob(os.path.join(outDir,'*')):
            os.remove(x)

    def test0(self):
        from reportlab.graphics.renderPS import test
        assert test(self.outDir) is None
    def test1(self):
        from reportlab.graphics.renderPDF import test
        assert test(self.outDir) is None

    def test2(self):
        from reportlab.graphics.renderPM import test
        assert test(self.outDir) is None

    def test3(self):
        from reportlab.graphics.renderSVG import test
        assert test(self.outDir) is None

def makeSuite():
    return makeSuiteForClasses(RenderTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
