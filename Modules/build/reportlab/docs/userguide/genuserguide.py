#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/docs/userguide/genuserguide.py
__version__=''' $Id$ '''
__doc__ = """
This module contains the script for building the user guide.
"""

def run(pagesize=None, verbose=0, outDir=None):
    import sys,os
    from reportlab.lib.utils import open_and_read, asUnicode
    cwd = os.getcwd()
    docsDir=os.path.dirname(os.path.dirname(sys.argv[0]) or cwd)
    topDir=os.path.dirname(docsDir)
    if not outDir: outDir=docsDir
    G = {}
    sys.path.insert(0,topDir)
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
    pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
    registerFontFamily('Vera',normal='Vera',bold='VeraBd',italic='VeraIt',boldItalic='VeraBI')
    from tools.docco.rl_doc_utils import setStory, getStory, RLDocTemplate, defaultPageSize, H1, H2, H3, H4
    from tools.docco import rl_doc_utils
    exec('from tools.docco.rl_doc_utils import *', G, G)
    destfn = os.path.join(outDir,'reportlab-userguide.pdf')
    doc = RLDocTemplate(destfn,pagesize = pagesize or defaultPageSize)


    #this builds the story
    setStory()

    for f in (
        'ch1_intro',
        'ch2_graphics',
        'ch2a_fonts',
        'ch3_pdffeatures',
        'ch4_platypus_concepts',
        'ch5_paragraphs',
        'ch6_tables',
        'ch7_custom',
        'graph_intro',
        'graph_concepts',
        'graph_charts',
        'graph_shapes',
        'graph_widgets',
        'app_demos',
        ):
        #python source is supposed to be utf8 these days
        exec(asUnicode(open_and_read(f+'.py')), G, G)
    del G

    story = getStory()
    if verbose: print('Built story contains %d flowables...' % len(story))
    doc.multiBuild(story)
    if verbose: print('Saved "%s"' % destfn)

def makeSuite():
    "standard test harness support - run self as separate process"
    from tests.utils import ScriptThatMakesFileTest
    return ScriptThatMakesFileTest('../docs/userguide', 'genuserguide.py', 'reportlab-userguide.pdf')

def main():
    import sys
    outDir = [x for x in sys.argv if x[:9]=='--outdir=']
    if outDir:
        outDir = outDir[0]
        sys.argv.remove(outDir)
        outDir = outDir[9:]
    else:
        outDir = None
    verbose = '-s' not in sys.argv
    if not verbose: sys.argv.remove('-s')
    timing = '-timing' in sys.argv
    if timing: sys.argv.remove('-timing')
    prof = '-prof' in sys.argv
    if prof: sys.argv.remove('-prof')

    if len(sys.argv) > 1:
        try:
            pagesize = (w,h) = eval(sys.argv[1])
        except:
            print('Expected page size in argument 1', sys.argv[1])
            raise
        if verbose:
            print('set page size to',sys.argv[1])
    else:
        pagesize = None
    if timing:
        from time import time
        t0 = time()
        run(pagesize, verbose,outDir)
        if verbose:
            print('Generation of userguide took %.2f seconds' % (time()-t0))
    elif prof:
        import profile
        profile.run('run(pagesize,verbose,outDir)','genuserguide.stats')
    else:
        run(pagesize, verbose,outDir)
if __name__=="__main__":
    main()
