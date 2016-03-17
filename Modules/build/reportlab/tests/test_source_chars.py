#!/usr/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
"""This tests for things in source files.  Initially, absence of tabs :-)
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, SecureTestCase, GlobDirectoryWalker, printLocation
setOutDir(__name__)
from reportlab.lib.testutils import RL_HOME,testsFolder
__version__=''' $Id$ '''
import os, sys, glob, re
import reportlab
import unittest
from reportlab.lib.utils import open_and_read


class SourceTester(SecureTestCase):
    def setUp(self):
        SecureTestCase.setUp(self)
        try:
            fn = __file__
        except:
            fn = sys.argv[0]

        self.output = open(outputfile(os.path.splitext(os.path.basename(fn))[0]+'.txt'),'w')

    def checkFileForTabs(self, filename):
        txt = open_and_read(filename, 'r')
        chunks = txt.split('\t')
        tabCount = len(chunks) - 1
        if tabCount:
            #raise Exception, "File %s contains %d tab characters!" % (filename, tabCount)
            self.output.write("file %s contains %d tab characters!\n" % (filename, tabCount))

    def checkFileForTrailingSpaces(self, filename):
        txt = open_and_read(filename, 'r')
        initSize = len(txt)
        badLines = 0
        badChars = 0
        for line in txt.split('\n'):
            stripped = line.rstrip()
            spaces = len(line) - len(stripped)  # OK, so they might be trailing tabs, who cares?
            if spaces:
                badLines = badLines + 1
                badChars = badChars + spaces

        if badChars != 0:
            self.output.write("file %s contains %d trailing spaces, or %0.2f%% wastage\n" % (filename, badChars, 100.0*badChars/initSize))

    def testFiles(self):
        w = GlobDirectoryWalker(RL_HOME, '*.py')
        for filename in w:
            self.checkFileForTabs(filename)
            self.checkFileForTrailingSpaces(filename)

def zapTrailingWhitespace(dirname):
    """Eliminates trailing spaces IN PLACE.  Use with extreme care
    and only after a backup or with version-controlled code."""
    assert os.path.isdir(dirname), "Directory not found!"
    print("This will eliminate all trailing spaces in py files under %s." % dirname)
    ok = input("Shall I proceed?  type YES > ")
    if ok != 'YES':
        print('aborted by user')
        return
    w = GlobDirectoryWalker(dirname, '*.py')
    for filename in w:
        # trim off final newline and detect real changes
        txt = open(filename, 'r').read()
        badChars = 0
        cleaned = []
        for line in txt.split('\n'):
            stripped = line.rstrip()
            cleaned.append(stripped)
            spaces = len(line) - len(stripped)  # OK, so they might be trailing tabs, who cares?
            if spaces:
                badChars = badChars + spaces

        if badChars != 0:
            open(filename, 'w').write('\n'.join(cleaned))
            print("file %s contained %d trailing spaces, FIXED" % (filename, badChars))
    print('done')

def makeSuite():
    return makeSuiteForClasses(SourceTester)


#noruntests
if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == 'zap' and os.path.isdir(sys.argv[2]):
        zapTrailingWhitespace(sys.argv[2])
    else:
        unittest.TextTestRunner().run(makeSuite())
        printLocation()
