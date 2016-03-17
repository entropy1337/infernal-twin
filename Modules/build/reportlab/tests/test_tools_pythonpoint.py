"""Tests for the PythonPoint tool.
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import os, sys, string
import unittest
import reportlab

class PythonPointTestCase(unittest.TestCase):
    "Some very crude tests on PythonPoint."
    def test0(self):
        "Test if pythonpoint.pdf can be created from pythonpoint.xml."

        join, dirname, isfile, abspath = os.path.join, os.path.dirname, os.path.isfile, os.path.abspath
        from tools.pythonpoint import pythonpoint
        from reportlab.lib.utils import isCompactDistro, open_for_read
        ppDir = dirname(pythonpoint.__file__)
        xml = abspath(join(ppDir, 'demos', 'pythonpoint.xml'))
        datafilename = 'pythonpoint.pdf'
        outDir = outputfile('')
        if isCompactDistro():
            xml = open_for_read(xml)
        pdf = join(outDir, datafilename)
        if isfile(pdf): os.remove(pdf)
        pythonpoint.process(xml, outDir=outDir, verbose=0, datafilename=datafilename)
        assert os.path.exists(pdf)

def makeSuite():
    return makeSuiteForClasses(PythonPointTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
