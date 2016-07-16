#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
"""Tests pageBreakBefore, frameBreakBefore, keepWithNext...
"""
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys, os, time
from operator import truth
import unittest
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.frames import Frame
from reportlab.lib.randomtext import randomText, PYTHON
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Indenter, SimpleDocTemplate
from reportlab.platypus.paragraph import *


def myMainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."

    canvas.saveState()
    canvas.setFont('Times-Roman', 12)
    pageNumber = canvas.getPageNumber()
    canvas.drawString(10*cm, cm, str(pageNumber))
    canvas.restoreState()


class MyDocTemplate(BaseDocTemplate):
    _invalidInitArgs = ('pageTemplates',)

    def __init__(self, filename, **kw):
        frame1 = Frame(2.5*cm, 15.5*cm, 6*cm, 10*cm, id='F1')
        frame2 = Frame(11.5*cm, 15.5*cm, 6*cm, 10*cm, id='F2')
        frame3 = Frame(2.5*cm, 2.5*cm, 6*cm, 10*cm, id='F3')
        frame4 = Frame(11.5*cm, 2.5*cm, 6*cm, 10*cm, id='F4')
        self.allowSplitting = 0
        self.showBoundary = 1
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('normal', [frame1, frame2, frame3, frame4], myMainPageFrame)
        self.addPageTemplates(template)

_text1='''Furthermore, the fundamental error of regarding functional notions as
categorial delimits a general convention regarding the forms of the
grammar.  I suggested that these results would follow from the
assumption that the descriptive power of the base component may remedy
and, at the same time, eliminate a descriptive fact.  Thus a subset of
English sentences interesting on quite independent grounds raises
serious doubts about the ultimate standard that determines the accuracy
of any proposed grammar.  Of course, the natural general principle that
will subsume this case can be defined in such a way as to impose the
strong generative capacity of the theory.  By combining adjunctions and
certain deformations, the descriptive power of the base component is not
subject to the levels of acceptability from fairly high (e.g. (99a)) to
virtual gibberish (e.g. (98d)).
'''
def _test0(self):
    "This makes one long multi-page paragraph."

    # Build story.
    story = []
    a = story.append

    styleSheet = getSampleStyleSheet()
    h1 = styleSheet['Heading1']
    h1.pageBreakBefore = 1
    h1.keepWithNext = 1

    h2 = styleSheet['Heading2']
    h2.frameBreakBefore = 1
    h2.keepWithNext = 1

    h3 = styleSheet['Heading3']
    h3.backColor = colors.cyan
    h3.keepWithNext = 1

    bt = styleSheet['BodyText']
    btj = ParagraphStyle('bodyText1j',parent=bt,alignment=TA_JUSTIFY)
    btr = ParagraphStyle('bodyText1r',parent=bt,alignment=TA_RIGHT)
    btc = ParagraphStyle('bodyText1c',parent=bt,alignment=TA_CENTER)
    a(Paragraph("""
        <a name='top'/>Subsequent pages test pageBreakBefore, frameBreakBefore and
        keepTogether attributes.  Generated at %s.  The number in brackets
        at the end of each paragraph is its position in the story. (%d)""" % (
            time.ctime(time.time()), len(story)), bt))

    for i in range(10):
        a(Paragraph('Heading 1 always starts a new page (%d)' % len(story), h1))
        for j in range(3):
            a(Paragraph('Heading1 paragraphs should always'
                            'have a page break before.  Heading 2 on the other hand'
                            'should always have a FRAME break before (%d)' % len(story), bt))
            a(Paragraph('Heading 2 always starts a new frame (%d)' % len(story), h2))
            a(Paragraph('Heading1 paragraphs should always'
                            'have a page break before.  Heading 2 on the other hand'
                            'should always have a FRAME break before (%d)' % len(story), bt))
            for j in range(3):
                a(Paragraph(randomText(theme=PYTHON, sentences=2)+' (%d)' % len(story), bt))
                a(Paragraph('I should never be at the bottom of a frame (%d)' % len(story), h3))
                a(Paragraph(randomText(theme=PYTHON, sentences=1)+' (%d)' % len(story), bt))

    for align,bts in [('left',bt),('JUSTIFIED',btj),('RIGHT',btr),('CENTER',btc)]:
        a(Paragraph('Now we do &lt;br/&gt; tests(align=%s)' % align, h1))
        a(Paragraph('First off no br tags',h3))
        a(Paragraph(_text1,bts))
        a(Paragraph("&lt;br/&gt; after 'the' in line 4",h3))
        a(Paragraph(_text1.replace('forms of the','forms of the<br/>',1),bts))
        a(Paragraph("2*&lt;br/&gt; after 'the' in line 4",h3))
        a(Paragraph(_text1.replace('forms of the','forms of the<br/><br/>',1),bts))
        a(Paragraph("&lt;br/&gt; after 'I suggested ' in line 5",h3))
        a(Paragraph(_text1.replace('I suggested ','I suggested<br/>',1),bts))
        a(Paragraph("2*&lt;br/&gt; after 'I suggested ' in line 5",h3))
        a(Paragraph(_text1.replace('I suggested ','I suggested<br/><br/>',1),bts))
        a(Paragraph("&lt;br/&gt; at the end of the paragraph!",h3))
        a(Paragraph("""text one<br/>text two<br/>""",bts))
        a(Paragraph("Border with &lt;br/&gt; at the end of the paragraph!",h3))
        bt1 = ParagraphStyle('bodyText1',bts)
        bt1.borderWidth = 0.5
        bt1.borderColor = colors.toColor('red')
        bt1.backColor = colors.pink
        bt1.borderRadius = 2
        bt1.borderPadding = 3
        a(Paragraph("""text one<br/>text two<br/>""",bt1))
        a(Paragraph("Border no &lt;br/&gt; at the end of the paragraph!",h3))
        bt1 = ParagraphStyle('bodyText1',bts)
        bt1.borderWidth = 0.5
        bt1.borderColor = colors.toColor('red')
        bt1.backColor = colors.pink
        bt1.borderRadius = 2
        bt1.borderPadding = 3
        a(Paragraph("""text one<br/>text two""",bt1))
        a(Paragraph("Different border style!",h3))
        bt2 = ParagraphStyle('bodyText1',bt1)
        bt2.borderWidth = 1.5
        bt2.borderColor = colors.toColor('blue')
        bt2.backColor = colors.gray
        bt2.borderRadius = 3
        bt2.borderPadding = 3
        a(Paragraph("""text one<br/>text two<br/>""",bt2))
    for i in 0, 1, 2:
        P = Paragraph("""This is a paragraph with <font color='blue'><a href='#top'>with an incredibly
long and boring link in side of it that
contains lots and lots of stupidly boring and worthless information.
So that we can split the link and see if we get problems like Dinu's.
I hope we don't, but you never do Know.</a></font>""",bt)
        a(P)

    doc = MyDocTemplate(outputfile('test_platypus_breaking.pdf'))
    doc.multiBuild(story)


class BreakingTestCase(unittest.TestCase):
    "Test multi-page splitting of paragraphs (eyeball-test)."
    def test0(self):
        _test0(self)

    def test1(self):
        '''Ilpo Nyyss\xf6nen posted this broken test'''
        normalStyle = ParagraphStyle(name = 'normal')
        keepStyle = ParagraphStyle(name = 'keep', keepWithNext = True)
        content = [
            Paragraph("line 1", keepStyle),
            Indenter(left = 1 * cm),
            Paragraph("line 2", normalStyle),
            ]
        doc = SimpleDocTemplate(outputfile('test_platypus_breaking1.pdf'))
        doc.build(content)

    def test2(self):
        sty = ParagraphStyle(name = 'normal')
        sty.fontName = 'Times-Roman'
        sty.fontSize = 10
        sty.leading = 12

        p = Paragraph('one two three',sty)
        p.wrap(20,36)
        self.assertEqual(len(p.split(20,24)),2) #widows allowed
        self.assertEqual(len(p.split(20,16)),0) #orphans disallowed
        p.allowWidows = 0
        self.assertEqual(len(p.split(20,24)),0) #widows disallowed
        p.allowOrphans = 1
        self.assertEqual(len(p.split(20,16)),2) #orphans allowed

    def test3(self):
        from reportlab.pdfgen.canvas import Canvas

        aW=307
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']
        btj = ParagraphStyle('bodyText1j',parent=bt,alignment=TA_JUSTIFY)
        p=Paragraph("""<a name='top'/>Subsequent pages test pageBreakBefore, frameBreakBefore and
                keepTogether attributes.  Generated at 1111. The number in brackets
                at the end of each paragraph is its position in the story. llllllllllllllllllllllllll 
                bbbbbbbbbbbbbbbbbbbbbb ccccccccccccccccccccccc ddddddddddddddddddddd eeeeyyy""",btj)

        w,h=p.wrap(aW,1000)
        canv=Canvas('test_platypus_paragraph_just.pdf',pagesize=(aW,h))
        i=len(canv._code)
        p.drawOn(canv,0,0)
        ParaCode=canv._code[i:]
        canv.saveState()
        canv.setLineWidth(0)
        canv.setStrokeColorRGB(1,0,0)
        canv.rect(0,0,aW,h)
        canv.restoreState()
        canv.showPage()
        canv.save()
        from reportlab import rl_config
        x = rl_config.paraFontSizeHeightOffset and '50' or '53.17'
        good = ['q', '1 0 0 1 0 0 cm', 'q', 'BT 1 0 0 1 0 '+x+' Tm 3.59 Tw 12 TL /F1 10 Tf 0 0 0 rg (Subsequent pages test pageBreakBefore, frameBreakBefore and) Tj T* 0 Tw .23 Tw (keepTogether attributes. Generated at 1111. The number in brackets) Tj T* 0 Tw .299167 Tw (at the end of each paragraph is its position in the story. llllllllllllllllllllllllll) Tj T* 0 Tw 66.9 Tw (bbbbbbbbbbbbbbbbbbbbbb ccccccccccccccccccccccc) Tj T* 0 Tw (ddddddddddddddddddddd eeeeyyy) Tj T* ET', 'Q', 'Q']
        ok= ParaCode==good
        assert ok, "\nParaCode=%r\nexpected=%r" % (ParaCode,good)

def makeSuite():
    return makeSuiteForClasses(BreakingTestCase)


#noruntests
if __name__ == "__main__": #NORUNTESTS
    if 'debug' in sys.argv:
        _test0(None)
    else:
        unittest.TextTestRunner().run(makeSuite())
        printLocation()
