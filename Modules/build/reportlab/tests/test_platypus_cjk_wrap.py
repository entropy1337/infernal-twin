#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
"""Tests for the reportlab.platypus.paragraphs module.
"""
__version__=''' $Id$ '''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys, os, unittest

from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, PageBreak, NextPageTemplate
from reportlab.platypus.frames import Frame, ShowBoundaryValue
from reportlab.lib.colors import Color
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

from reportlab.pdfbase.cidfonts import CIDFont, findCMapFile, UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics


#says "Japanese is difficult, isn't it?"
shortText = '\u65e5\u672c\u8a9e\u306f\u96e3\u3057\u3044\u3067\u3059\u306d\uff01'


gatwickText = '\xe3\x82\xac\xe3\x83\x88\xe3\x82\xa6\xe3\x82\xa3\xe3\x83\x83\xe3\x82\xaf\xe7\xa9\xba\xe6\xb8\xaf\xe3\x81\xa8\xe9\x80\xa3\xe7\xb5\xa1\xe9\x80\x9a\xe8\xb7\xaf\xe3\x81\xa7\xe7\x9b\xb4\xe7\xb5\x90\xe3\x81\x95\xe3\x82\x8c\xe3\x81\xa6\xe3\x81\x84\xe3\x82\x8b\xe5\x94\xaf\xe4\xb8\x80\xe3\x81\xae\xe3\x83\x9b\xe3\x83\x86\xe3\x83\xab\xe3\x81\xa7\xe3\x81\x82\xe3\x82\x8b\xe5\xbd\x93\xe3\x83\x9b\xe3\x83\x86\xe3\x83\xab\xe3\x81\xaf\xe3\x80\x81VERYLONGENGLISHGOESHERE\xe8\xa1\x97\xe3\x81\xae\xe4\xb8\xad\xe5\xbf\x83\xe9\x83\xa8\xe3\x81\x8b\xe3\x82\x8930\xe5\x88\x86\xe3\x81\xae\xe5\xa0\xb4\xe6\x89\x80\xe3\x81\xab\xe3\x81\x94\xe3\x81\x96\xe3\x81\x84\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82\xe5\x85\xa8\xe5\xae\xa2\xe5\xae\xa4\xe3\x81\xab\xe9\xab\x98\xe9\x80\x9f\xe3\x82\xa4\xe3\x83\xb3\xe3\x82\xbf\xe3\x83\xbc\xe3\x83\x8d\xe3\x83\x83\xe3\x83\x88\xe7\x92\xb0\xe5\xa2\x83\xe3\x82\x92\xe5\xae\x8c\xe5\x82\x99\xe3\x81\x97\xe3\x81\xa6\xe3\x81\x8a\xe3\x82\x8a\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82\xe3\x83\x95\xe3\x82\xa1\xe3\x83\x9f\xe3\x83\xaa\xe3\x83\xbc\xe3\x83\xab\xe3\x83\xbc\xe3\x83\xa0\xe3\x81\xaf5\xe5\x90\x8d\xe6\xa7\x98\xe3\x81\xbe\xe3\x81\xa7\xe3\x81\x8a\xe6\xb3\x8a\xe3\x82\x8a\xe3\x81\x84\xe3\x81\x9f\xe3\x81\xa0\xe3\x81\x91\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82\xe3\x81\xbe\xe3\x81\x9f\xe3\x80\x81\xe3\x82\xa8\xe3\x82\xb0\xe3\x82\xbc\xe3\x82\xaf\xe3\x83\x86\xe3\x82\xa3\xe3\x83\x96\xe3\x83\xab\xe3\x83\xbc\xe3\x83\xa0\xe3\x81\xae\xe3\x81\x8a\xe5\xae\xa2\xe6\xa7\x98\xe3\x81\xaf\xe3\x80\x81\xe3\x82\xa8\xe3\x82\xb0\xe3\x82\xbc\xe3\x82\xaf\xe3\x83\x86\xe3\x82\xa3\xe3\x83\x96\xe3\x83\xa9\xe3\x82\xa6\xe3\x83\xb3\xe3\x82\xb8\xe3\x82\x92\xe3\x81\x94\xe5\x88\xa9\xe7\x94\xa8\xe3\x81\x84\xe3\x81\x9f\xe3\x81\xa0\xe3\x81\x91\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82\xe4\xba\x8b\xe5\x89\x8d\xe3\x81\xab\xe3\x81\x94\xe4\xba\x88\xe7\xb4\x84\xe3\x81\x84\xe3\x81\x9f\xe3\x81\xa0\xe3\x81\x91\xe3\x82\x8b\xe3\x82\xbf\xe3\x82\xa4\xe3\x83\xa0\xe3\x83\x88\xe3\x82\xa5\xe3\x83\x95\xe3\x83\xa9\xe3\x82\xa4\xe3\x83\xbb\xe3\x83\x91\xe3\x83\x83\xe3\x82\xb1\xe3\x83\xbc\xe3\x82\xb8\xe3\x81\xab\xe3\x81\xaf\xe3\x80\x81\xe7\xa9\xba\xe6\xb8\xaf\xe3\x81\xae\xe9\xa7\x90\xe8\xbb\x8a\xe6\x96\x99\xe9\x87\x91\xe3\x81\x8c\xe5\x90\xab\xe3\x81\xbe\xe3\x82\x8c\xe3\x81\xa6\xe3\x81\x8a\xe3\x82\x8a\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82'

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
        frame2 = Frame(2.5*cm, 2.5*cm, 310, 25*cm, id='F2')
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('normal', [frame1], myMainPageFrame)
        template1 = PageTemplate('special', [frame2], myMainPageFrame)
        self.addPageTemplates([template,template1])


class CJKWrap(unittest.TestCase):
    "Exercises cjkFragSplit"

    def test1(self):
        "This makes several special paragraphs."


        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']
        cjk = ParagraphStyle(
                            name="cjkwrap", 
                            fontName="HeiseiMin-W3",
                            parent=styleSheet['BodyText'], 
                            wordWrap="CJK")

        story.append(Paragraph('''This is a test of CJK word wrapping.  
            When using the CJK algorithm, we split between characters.  
            Unfortunately this sucks when English words are involved - for example the title
            of a technical product manual.  This paragraph uses CJK wrapping, so if you can 
            see English words getting broken in two, something went wrong! At the time of writing, it looks OK.
            ''',style=cjk))

        story.append(Paragraph(shortText * 3 + "This should get broken between some words. " + shortText * 2,style=cjk))


        story.append(Paragraph(shortText * 3 + "This_should_be_unbroken_as_we_backtrack_to_previous_kanji. " + shortText * 2,style=cjk))

        story.append(Paragraph(shortText + "This_should_be_broken_in_mid_word_as_we_do_not_backtrack_home_than_half_a_line. " + shortText * 2,style=cjk))


        story.append(Paragraph("Regression test: we really don't want line 2 to start with an exclamation mark." + shortText * 5,style=cjk))


        doc = MyDocTemplate(outputfile('test_platypus_cjk_wrap.pdf'))
        doc.build(story)


#noruntests
def makeSuite():
    return makeSuiteForClasses(CJKWrap,)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
