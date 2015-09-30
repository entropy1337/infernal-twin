#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
"""Tests for reportlab.lib.utils
"""
__version__=''' $Id$ '''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, printLocation
setOutDir(__name__)
import os, time, sys
import reportlab
import unittest
from reportlab.lib import colors
from reportlab.lib.utils import recursiveImport, recursiveGetAttr, recursiveSetAttr, rl_isfile, \
                                isCompactDistro, isPy3

def _rel_open_and_read(fn):
    from reportlab.lib.utils import open_and_read
    from reportlab.lib.testutils import testsFolder
    cwd = os.getcwd()
    os.chdir(testsFolder)
    try:
        return open_and_read(fn)
    finally:
        os.chdir(cwd)

class ImporterTestCase(unittest.TestCase):
    "Test import utilities"
    count = 0

    def setUp(self):
        from reportlab.lib.utils import get_rl_tempdir
        s = repr(int(time.time())) + repr(self.count)
        self.__class__.count += 1
        self._tempdir = get_rl_tempdir('reportlab_test','tmp_%s' % s)
        if not os.path.isdir(self._tempdir):
            os.makedirs(self._tempdir,0o700)
        _testmodulename = os.path.join(self._tempdir,'test_module_%s.py' % s)
        f = open(_testmodulename,'w')
        f.write('__all__=[]\n')
        f.close()
        if sys.platform=='darwin' and isPy3:
            time.sleep(0.3)
        self._testmodulename = os.path.splitext(os.path.basename(_testmodulename))[0]

    def tearDown(self):
        from shutil import rmtree
        rmtree(self._tempdir,1)

    def test1(self):
        "try stuff known to be in the path"
        m1 = recursiveImport('reportlab.pdfgen.canvas')
        import reportlab.pdfgen.canvas
        assert m1 == reportlab.pdfgen.canvas

    def test2(self):
        "try under a well known directory NOT on the path"
        from reportlab.lib.testutils import testsFolder
        D = os.path.join(testsFolder,'..','tools','pythonpoint')
        fn = os.path.join(D,'stdparser.py')
        if rl_isfile(fn) or rl_isfile(fn+'c') or rl_isfile(fn+'o'):
            m1 = recursiveImport('stdparser', baseDir=D)

    def test3(self):
        "ensure CWD is on the path"
        try:
            cwd = os.getcwd()
            os.chdir(self._tempdir)
            m1 = recursiveImport(self._testmodulename)
        finally:
            os.chdir(cwd)

    def test4(self):
        "ensure noCWD removes current dir from path"
        try:
            cwd = os.getcwd()
            os.chdir(self._tempdir)
            import sys
            try:
                del sys.modules[self._testmodulename]
            except KeyError:
                pass
            self.assertRaises(ImportError,
                              recursiveImport,
                              self._testmodulename,
                              noCWD=1)
        finally:
            os.chdir(cwd)

    def test5(self):
        "recursive attribute setting/getting on modules"
        import reportlab.lib.units
        inch = recursiveGetAttr(reportlab, 'lib.units.inch')
        assert inch == 72

        recursiveSetAttr(reportlab, 'lib.units.cubit', 18*inch)
        cubit = recursiveGetAttr(reportlab, 'lib.units.cubit')
        assert cubit == 18*inch

    def test6(self):
        "recursive attribute setting/getting on drawings"
        from reportlab.graphics.charts.barcharts import sampleH1
        drawing = sampleH1()
        recursiveSetAttr(drawing, 'barchart.valueAxis.valueMax', 72)
        theMax = recursiveGetAttr(drawing, 'barchart.valueAxis.valueMax')
        assert theMax == 72

    def test7(self):
        "test open and read of a simple relative file"
        b = _rel_open_and_read('../docs/images/Edit_Prefs.gif')

    def test8(self):
        "test open and read of a relative file: URL"
        b = _rel_open_and_read('file:../docs/images/Edit_Prefs.gif')

    def test9(self):
        "test open and read of an http: URL"
        from reportlab.lib.utils import open_and_read
        b = open_and_read('http://www.reportlab.com/rsrc/encryption.gif')

    def test10(self):
        "test open and read of a simple relative file"
        from reportlab.lib.utils import open_and_read, getBytesIO
        b = getBytesIO(_rel_open_and_read('../docs/images/Edit_Prefs.gif'))
        b = open_and_read(b)

    def test11(self):
        "test open and read of an RFC 2397 data URI with base64 encoding"
        result = _rel_open_and_read('data:image/gif;base64,R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs=')
        self.assertEquals(result,b'GIF87a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')

    def test12(self):
        "test open and read of an RFC 2397 data URI without an encoding"
        result = _rel_open_and_read('data:text/plain;,Hello%20World')
        self.assertEquals(result,b'Hello World')

    def testRecursiveImportErrors(self):
        "check we get useful error messages"
        try:
            m1 = recursiveImport('reportlab.pdfgen.brush')
            self.fail("Imported a nonexistent module")
        except ImportError as e:
            self.assertIn('reportlab.pdfgen.brush',str(e))
            
        try:
            m1 = recursiveImport('totally.non.existent')
            self.fail("Imported a nonexistent module")
        except ImportError as e:
            self.assertIn('totally',str(e))

        try:
            #import a module in the 'tests' directory with a bug
            m1 = recursiveImport('unimportable')
            self.fail("Imported a buggy module")
        except Exception as e:
            self.assertIn(reportlab.isPy3 and 'division by zero' or 'integer division or modulo by zero',str(e))

def makeSuite():
    return makeSuiteForClasses(ImporterTestCase)

if __name__ == "__main__": #noruntests
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
