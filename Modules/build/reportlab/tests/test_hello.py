#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__version__='''$Id$'''
__doc__="""most basic test possible that makes a PDF.

Useful if you want to test that a really minimal PDF is healthy,
since the output is about the smallest thing we can make."""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.paraparser import _greekConvert

class HelloTestCase(unittest.TestCase):
    "Simplest test that makes PDF"

    def test(self):
        c = Canvas(outputfile('test_hello.pdf'))
        #Author with Japanese text
        c.setAuthor(b'\xe3\x83\x9b\xe3\x83\x86\xe3\x83\xab\xe3\x83\xbbe\xe3\x83\x91\xe3\x83\xb3\xe3\x83\x95\xe3\x83\xac\xe3\x83\x83\xe3\x83\x88')
        #Subject with Arabic magic
        c.setSubject('\u0643\u0644\u0627\u0645 \u0639\u0631\u0628\u064a')
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Hello World!')
        c.drawString(100,700-36*1.2, _greekConvert('Hello Brave New World')+'!')
        c.save()

    def test_rl_config_reset(self):
        from reportlab import rl_config
        from reportlab.pdfbase import pdfmetrics, _fontdata
        tfd = pdfmetrics._typefaces
        fbn = _fontdata.fontsByName
        tfd[' a ']=1
        fbn[' b ']=1
        ntfd = len(tfd)
        nfbn = len(fbn)
        from reportlab.lib import sequencer
        seq = sequencer.getSequencer()
        seq._dingo = 1
        rl_config._reset()
        assert not hasattr(seq,'_dingo')
        assert ' a ' not in tfd and len(tfd)<ntfd
        assert ' a ' not in fbn and len(fbn)<nfbn

def makeSuite():
    return makeSuiteForClasses(HelloTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
