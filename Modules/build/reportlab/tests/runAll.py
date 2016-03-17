#!/usr/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
"""Runs all test files in all subfolders.
"""
__version__=''' $Id$ '''
import os, glob, sys, traceback, unittest

#we need to ensure 'tests' is on the path.  It will be if you
#run 'setup.py tests', but won't be if you CD into the tests
#directory and run this directly
if __name__=='__main__':
    P=[]
    try:
        from reportlab.lib.testutils import setOutDir
    except ImportError:
        if __name__=='__main__':
            topDir = os.path.dirname(sys.argv[0])
            if not topDir: topDir = os.getcwd()
        else:
            topDir = os.path.dirname(__file__)
        topDir = os.path.dirname(os.path.abspath(topDir))
        if not os.path.isdir(os.path.join(topDir,'reportlab')):
            topDir=os.path.join(topDir,'src')
            assert os.path.isdir(os.path.join(topDir,'reportlab')), "Cannot find reportlab"
        sys.path.insert(0, topDir)
        P.append(topDir)
        del topDir
        from reportlab.lib.testutils import setOutDir

    setOutDir(__name__)
    from reportlab.lib.testutils import testsFolder as topDir
    if topDir:
        topDir = os.path.dirname(topDir)
        if topDir not in sys.path:
            sys.path.insert(0,topDir)
            P.append(topDir)
    del topDir
    from reportlab.lib.testutils import GlobDirectoryWalker, outputfile, printLocation
    pp = os.environ.get('PYTHONPATH','')
    if pp: P.append(pp)
    del pp
    os.environ['PYTHONPATH']=os.pathsep.join(P)
    del P

def makeSuite(folder, exclude=[],nonImportable=[],pattern='test_*.py'):
    "Build a test suite of all available test files."
    allTests = unittest.TestSuite()

    if os.path.isdir(folder): sys.path.insert(0, folder)
    for filename in GlobDirectoryWalker(folder, pattern):
        modname = os.path.splitext(os.path.basename(filename))[0]
        if modname not in exclude:
            try:
                ns ={}
                exec('import %s as module' % modname,ns)
                allTests.addTest(ns['module'].makeSuite())
            except:
                tt, tv, tb = sys.exc_info()[:]
                nonImportable.append((filename,traceback.format_exception(tt,tv,tb)))
                del tt,tv,tb
    del sys.path[0]

    return allTests

def main(pattern='test_*.py'):
    try:
        folder = os.path.dirname(__file__)
        assert folder
    except:
        folder = os.path.dirname(sys.argv[0]) or os.getcwd()
    #allow for Benn's "screwball cygwin distro":
    if not folder:
        folder = '.'
    from reportlab.lib.utils import isSourceDistro
    haveSRC = isSourceDistro()

    def cleanup(folder,patterns=('*.pdf', '*.log','*.svg','runAll.txt', 'test_*.txt','_i_am_actually_a_*.*')):
        if not folder: return
        for pat in patterns:
            for filename in GlobDirectoryWalker(folder, pattern=pat):
                try:
                    os.remove(filename)
                except:
                    pass

    # special case for tests directory - clean up
    # all PDF & log files before starting run.  You don't
    # want this if reusing runAll anywhere else.
    if os.sep+'tests' in folder: cleanup(folder)
    cleanup(outputfile(''))
    NI = []
    cleanOnly = '--clean' in sys.argv
    if not cleanOnly:
        testSuite = makeSuite(folder,nonImportable=NI,pattern=pattern+(not haveSRC and 'c' or ''))
        unittest.TextTestRunner().run(testSuite)

    if haveSRC: cleanup(folder,patterns=('*.pyc','*.pyo'))
    if not cleanOnly:
        if NI:
            sys.stderr.write('\n###################### the following tests could not be imported\n')
            for f,tb in NI:
                print('file: "%s"\n%s\n' % (f,''.join(tb)))
        printLocation()

def mainEx():
    '''for use in subprocesses'''
    try:
        main()
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout.close()
        os.close(sys.stderr.fileno())

def runExternally():
    cmd = '"%s" -c"from tests import runAll;runAll.mainEx()"' % sys.executable
    i,o,e=os.popen3(cmd)
    i.close()
    out = o.read()
    err=e.read()
    return '\n'.join((out,err))

def checkForFailure(outerr):
    return '\nFAILED' in outerr

if __name__ == '__main__': #noruntests
    main()
