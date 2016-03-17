#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
"""Tests for context-dependent indentation
"""
__version__='''$Id: test_platypus_indents.py 3660 2010-02-08 18:17:33Z damian $'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys, os, random
from operator import truth
import unittest
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.paraparser import ParaParser
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import Color
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import _className
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate, Indenter, FrameBreak, NextPageTemplate
from reportlab.platypus import tableofcontents
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.tables import TableStyle, Table
from reportlab.platypus.paragraph import *
from reportlab.platypus.paragraph import _getFragWords
from reportlab.platypus.flowables import Spacer


def myMainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."

    canvas.saveState()

    canvas.rect(2.5*cm, 2.5*cm, 15*cm, 25*cm)
    canvas.setFont('Times-Roman', 12)
    pageNumber = canvas.getPageNumber()
    canvas.drawString(10*cm, cm, str(pageNumber))

    canvas.restoreState()


class MyDocTemplate(BaseDocTemplate):
    _invalidInitArgs = ('pageTemplates',)

    def __init__(self, filename, **kw):
        frame1 = Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        template1 = PageTemplate('normal', [frame1], myMainPageFrame)

        frame2 = Frame(2.5*cm, 16*cm, 15*cm, 10*cm, id='F2', showBoundary=1)
        frame3 = Frame(2.5*cm, 2.5*cm, 15*cm, 10*cm, id='F3', showBoundary=1)

        template2 = PageTemplate('updown', [frame2, frame3])
        self.addPageTemplates([template1, template2])


class WrappingTestCase(unittest.TestCase):
    "Test wrapping of long urls"

    def test0(self):
        "This makes one long multi-page paragraph."

        # Build story.
        story = []

        styleSheet = getSampleStyleSheet()
        h1 = styleSheet['Heading1']
        h1.spaceBefore = 18
        bt = styleSheet['BodyText']
        bt.spaceBefore = 6

        story.append(Paragraph('Test of paragraph wrapping',h1))

        story.append(Spacer(18,18))

        txt = "Normally we wrap paragraphs by looking for spaces between the words.  However, with long technical command references and URLs, sometimes this gives ugly results.  We attempt to split really long words on certain tokens:  slashes, dots etc."

        story.append(Paragraph(txt,bt))
        
        story.append(Paragraph('This is an attempt to break long URLs sanely.  Here is a file name: <font face="Courier">C:\\Windows\\System32\\Drivers\\etc\\hosts</font>.  ', bt))
        

        story.append(Paragraph('This paragraph has a URL (basically, a word) too long to fit on one line, so it just overflows. http://some-really-long-site.somewhere-verbose.com/webthingies/framework/xc4987236hgsdlkafh/foo?format=dingbats&amp;content=rubbish. Ideally, we would wrap it in the middle.', bt))


        
        
        doc = MyDocTemplate(outputfile('test_platypus_wrapping.pdf'))
        doc.multiBuild(story)

#noruntests
def makeSuite():
    return makeSuiteForClasses(WrappingTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
