__version__=''' $Id$ '''
"""Tests that all manuals can be built.
"""
from reportlab.lib.testutils import setOutDir,SecureTestCase, printLocation
setOutDir(__name__)
import os, sys, unittest

class ManualTestCase(SecureTestCase):
    "Runs all 3 manual-builders from the top."

    def test0(self):
        "Test if all manuals buildable from source."
        from reportlab.lib.testutils import testsFolder
        try:
            docsFolder = os.path.join(os.path.dirname(testsFolder),'docs')
        except:
            print(testsFolder)
            raise
        cwd = os.getcwd()
        os.chdir(docsFolder)
        try:
            if os.path.isfile('reportlab-userguide.pdf'):
                os.remove('reportlab-userguide.pdf')
            #if os.path.isfile('reportlab-reference.pdf'):
            #   os.remove('reportlab-reference.pdf')

            os.system('"%s" genAll.py -s' % sys.executable)

            assert os.path.isfile('reportlab-userguide.pdf'), 'genAll.py failed to generate reportlab-userguide.pdf!'
            #assert os.path.isfile('reportlab-reference.pdf'), 'genAll.py failed to generate reportlab-reference.pdf!'
        finally:
            os.chdir(cwd)

def makeSuite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    if sys.platform[:4] != 'java':
        suite.addTest(loader.loadTestsFromTestCase(ManualTestCase))
    return suite

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
