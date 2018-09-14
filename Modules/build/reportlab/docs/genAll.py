#!/bin/env python
import os, sys, traceback
def _genAll(verbose=1):
    from reportlab.lib.testutils import setOutDir
    setOutDir(__name__)
    from reportlab.lib.testutils import testsFolder
    topDir=os.path.dirname(testsFolder)
    L = [os.path.join(topDir,f) for f in (
            #'docs/reference/genreference.py',
            'docs/userguide/genuserguide.py',
            #'tools/docco/graphdocpy.py',
            )   
        ]
    for f in ('src/rl_addons/pyRXP/docs/PyRXP_Documentation.rml',
            ):
        f = os.path.join(topDir,f)
        if os.path.isfile(f):
            L += [f]
            break
    for p in L:
        os.chdir(os.path.dirname(p))
        if p[-4:]=='.rml':
            try:
                from rlextra.rml2pdf.rml2pdf import main
                main(exe=0,fn=[os.path.basename(p)], quiet=not verbose, outDir=d)
            except:
                if verbose: traceback.print_exc()
        else:
            cmd = '"%s" %s %s' % (sys.executable,os.path.basename(p), not verbose and '-s' or '')
            if verbose: print(cmd)
            os.system(cmd)

"""Runs the manual-building scripts"""
if __name__=='__main__':
    #need a quiet mode for the test suite
    if '-s' in sys.argv:  # 'silent
        verbose = 0
    else:
        verbose = 1
    d = os.path.dirname(sys.argv[0])
    if not d:
        d = os.getcwd()
    elif not os.path.isabs(d):
        d = os.path.abspath(d)
    sys.path.insert(0,os.path.dirname(d))
    _genAll(verbose)
