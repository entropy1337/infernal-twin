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
from reportlab.platypus.flowables import Spacer, Preformatted

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
        normalStyle = styleSheet['Code']


        story.append(Paragraph('Test of preformatted text wrapping',h1))

        story.append(Spacer(18,18))

        txt = """Our Preformatted class can be used for printing simple blocks
of code. It respects whitespace and newlines, and will not normally attempt 
to wrap your code. However, if your individual lines are too long, this can 
overflow the width of the column and even run off the page. Three optional 
attributes - maximumLineLength, splitCharacters and newLineCharacter - 
can be used to do simple wrapping. maximumLineLength will force the text to
wrap. Note that this simply counts characters - it takes no account of
actual width on the page. The examples below wrap lines above a certain length
and add a '>' to the start of the following line.
"""

        story.append(Paragraph(txt,bt))
        
        story.append(Paragraph("",bt))

        code = """
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/platypus/xpreformatted.py
__version__=''' $Id: xpreformatted.py 3866 2011-06-27 13:08:20Z rgbecker $ '''
__doc__='''A 'rich preformatted text' widget allowing internal markup'''

from reportlab.lib import PyFontify
from paragraph import Paragraph, cleanBlockQuotedText, _handleBulletWidth, ParaLines, _getFragWords, stringWidth, _sameFrag, getAscentDescent, imgVRange, imgNormV
from flowables import _dedenter

class XPreformatted(Paragraph):
    def __init__(self, text, style, bulletText = None, frags=None, caseSensitive=1, dedent=0):
        self.caseSensitive = caseSensitive
        cleaner = lambda text, dedent=dedent: ,'\\n'.join(_dedenter(text or '',dedent))
        self._setup(text, style, bulletText, frags, cleaner)

    def breakLines(self, width):
        if isinstance(width,list): maxWidths = [width]
        else: maxWidths = width
        lines = []
        lineno = 0
        maxWidth = maxWidths[lineno]
        style = self.style
        fFontSize = float(style.fontSize)
        requiredWidth = 0

        #for bullets, work out width and ensure we wrap the right amount onto line one
        _handleBulletWidth(self.bulletText,style,maxWidths)

        self.height = 0
        autoLeading = getattr(self,'autoLeading',getattr(style,'autoLeading',''))
        calcBounds = autoLeading not in ('','off')
        frags = self.frags
        nFrags= len(frags)
        if nFrags==1:
            f = frags[0]
            if hasattr(f,'text'):
                fontSize = f.fontSize
                fontName = f.fontName
                ascent, descent = getAscentDescent(fontName,fontSize)
                kind = 0
                L=f.text.split('\\n')
                for l in L:
                    currentWidth = stringWidth(l,fontName,fontSize)
                    requiredWidth = max(currentWidth,requiredWidth)
                    extraSpace = maxWidth-currentWidth
                    lines.append((extraSpace,l.split(' '),currentWidth))
                    lineno = lineno+1
                    maxWidth = lineno&lt;len(maxWidths) and maxWidths[lineno] or maxWidths[-1]
                blPara = f.clone(kind=kind, lines=lines,ascent=ascent,descent=descent,fontSize=fontSize)
            else:
                kind = f.kind
                lines = f.lines
                for L in lines:
                    if kind==0:
                        currentWidth = L[2]
                    else:
                        currentWidth = L.currentWidth
                    requiredWidth = max(currentWidth,requiredWidth)
                blPara = f.clone(kind=kind, lines=lines)

            self.width = max(self.width,requiredWidth)
            return blPara
        elif nFrags&lt;=0:
            return ParaLines(kind=0, fontSize=style.fontSize, fontName=style.fontName,
                            textColor=style.textColor, ascent=style.fontSize,descent=-0.2*style.fontSize,
                            lines=[])
        else:
            for L in _getFragLines(frags):
                currentWidth, n, w = _getFragWord(L,maxWidth)
                f = w[0][0]
                maxSize = f.fontSize
                maxAscent, minDescent = getAscentDescent(f.fontName,maxSize)
                words = [f.clone()]
                words[-1].text = w[0][1]
                for i in w[1:]:
                    f = i[0].clone()
                    f.text=i[1]
                    words.append(f)
                    fontSize = f.fontSize
                    fontName = f.fontName
                    if calcBounds:
                        cbDefn = getattr(f,'cbDefn',None)
                        if getattr(cbDefn,'width',0):
                            descent,ascent = imgVRange(imgNormV(cbDefn.height,fontSize),cbDefn.valign,fontSize)
                        else:
                            ascent, descent = getAscentDescent(fontName,fontSize)
                    else:
                        ascent, descent = getAscentDescent(fontName,fontSize)
                    maxSize = max(maxSize,fontSize)
                    maxAscent = max(maxAscent,ascent)
                    minDescent = min(minDescent,descent)

                lineno += 1
                maxWidth = lineno&lt;len(maxWidths) and maxWidths[lineno] or maxWidths[-1]
                requiredWidth = max(currentWidth,requiredWidth)
                extraSpace = maxWidth - currentWidth
                lines.append(ParaLines(extraSpace=extraSpace,wordCount=n, words=words, fontSize=maxSize, ascent=maxAscent,descent=minDescent,currentWidth=currentWidth))

            self.width = max(self.width,requiredWidth)
            return ParaLines(kind=1, lines=lines)

        return lines
"""
        
        story.append(Preformatted(code,normalStyle,dedent=0, maxLineLength=60, newLineChars='> '))

        doc = MyDocTemplate(outputfile('test_platypus_preformatted.pdf'))
        doc.multiBuild(story)

#noruntests
def makeSuite():
    return makeSuiteForClasses(WrappingTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
