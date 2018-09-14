#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
"""Tests for the Platypus TableOfContents class.

Currently there is only one such test. Most such tests, like this
one, will be generating a PDF document that needs to be eye-balled
in order to find out if it is 'correct'.
"""
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys, os
from os.path import join, basename, splitext
from math import sqrt
import random
import unittest
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.flowables import Flowable, Spacer
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate
from reportlab.platypus import tableofcontents, PageBreak
from reportlab.lib import randomtext
from xml.sax.saxutils import escape as xmlEscape


def myMainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."

    canvas.saveState()

    canvas.rect(2.5*cm, 2.5*cm, 15*cm, 25*cm)
    canvas.setFont('Times-Roman', 12)
    pageNumber = canvas.getPageNumber()
    canvas.drawString(10*cm, cm, str(pageNumber))

    canvas.restoreState()


class MyDocTemplate(BaseDocTemplate):
    "The document template used for all PDF documents."

    _invalidInitArgs = ('pageTemplates',)

    def __init__(self, filename, **kw):
        frame1 = Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('normal', [frame1], myMainPageFrame)
        self.addPageTemplates(template)


    def afterFlowable(self, flowable):
        "Registers TOC entries."

        if flowable.__class__.__name__ == 'Paragraph':
            styleName = flowable.style.name
            if styleName[:7] == 'Heading':
                key = str(hash(flowable))
                self.canv.bookmarkPage(key)

                # Register TOC entries.
                level = int(styleName[7:])
                text = flowable.getPlainText()
                pageNum = self.page
                # Try calling this with and without a key to test both
                # Entries of every second level will have links, others won't
                if level % 2 == 1:
                    self.notify('TOCEntry', (level, text, pageNum, key))
                else:
                    self.notify('TOCEntry', (level, text, pageNum))


def makeHeaderStyle(level, fontName='Times-Roman'):
    "Make a header style for different levels."

    assert level >= 0, "Level must be >= 0."

    PS = ParagraphStyle
    size = 24.0 / sqrt(1+level)
    style = PS(name = 'Heading' + str(level),
               fontName = fontName,
               fontSize = size,
               leading = size*1.2,
               spaceBefore = size/4.0,
               spaceAfter = size/8.0)

    return style


def makeBodyStyle():
    "Body text style - the default will do"
    return ParagraphStyle('body')


def makeTocHeaderStyle(level, delta, epsilon, fontName='Times-Roman'):
    "Make a header style for different levels."

    assert level >= 0, "Level must be >= 0."

    PS = ParagraphStyle
    size = 12
    style = PS(name = 'Heading' + str(level),
               fontName = fontName,
               fontSize = size,
               leading = size*1.2,
               spaceBefore = size/4.0,
               spaceAfter = size/8.0,
               firstLineIndent = -epsilon,
               leftIndent = level*delta + epsilon)

    return style


class TocTestCase(unittest.TestCase):
    "Test TableOfContents class (eyeball-test)."

    def test0(self):
        """Test story with TOC and a cascaded header hierarchy.

        The story should contain exactly one table of contents that is
        immediatly followed by a list of of cascaded levels of header
        lines, each nested one level deeper than the previous one.

        Features to be visually confirmed by a human being are:

            1. TOC lines are indented in multiples of 1 cm.
            2. Wrapped TOC lines continue with additional 0.5 cm indentation.
            3. Only entries of every second level has links
            ...
        """

        maxLevels = 12

        # Create styles to be used for document headers
        # on differnet levels.
        headerLevelStyles = []
        for i in range(maxLevels):
            headerLevelStyles.append(makeHeaderStyle(i))

        # Create styles to be used for TOC entry lines
        # for headers on differnet levels.
        tocLevelStyles = []
        d, e = tableofcontents.delta, tableofcontents.epsilon
        for i in range(maxLevels):
            tocLevelStyles.append(makeTocHeaderStyle(i, d, e))

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']

        description = '<font color=red>%s</font>' % self.test0.__doc__
        story.append(XPreformatted(description, bt))

        toc = tableofcontents.TableOfContents()
        toc.levelStyles = tocLevelStyles
        story.append(toc)

        for i in range(maxLevels):
            story.append(Paragraph('HEADER, LEVEL %d' % i,
                                   headerLevelStyles[i]))
            #now put some body stuff in.
            txt = xmlEscape(randomtext.randomText(randomtext.PYTHON, 5))
            para = Paragraph(txt, makeBodyStyle())
            story.append(para)

        path = outputfile('test_platypus_toc.pdf')
        doc = MyDocTemplate(path)
        doc.multiBuild(story)



    def test1(self):
        """This shows a table which would take more than one page,
        and need multiple passes to render.  But we preload it
        with the right headings to make it go faster.  We used
        a simple 100-chapter document with one level.
        """

        chapters = 30   #goes over one page
        
        headerStyle = makeHeaderStyle(0)
        d, e = tableofcontents.delta, tableofcontents.epsilon
        tocLevelStyle = makeTocHeaderStyle(0, d, e)

        # Build most of the story; we'll re-use it to 
        # make documents with different numbers of passes.

        story = []
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']

        description = '<font color=red>%s</font>' % self.test1.__doc__
        story.append(XPreformatted(description, bt))

        for i in range(chapters):
            story.append(PageBreak())
            story.append(Paragraph('This is chapter %d' % (i+1),
                                   headerStyle))
            #now put some lengthy body stuff in.  
            for paras in range(random.randint(1,3)):
                txt = xmlEscape(randomtext.randomText(randomtext.PYTHON, 5))
                para = Paragraph(txt, makeBodyStyle())
                story.append(para)


        #try 1: empty TOC, 3 passes

        toc = tableofcontents.TableOfContents()
        toc.levelStyles = [tocLevelStyle]   #only need one
        story1 = [toc] + story


        path = outputfile('test_platypus_toc_preload.pdf')
        doc = MyDocTemplate(path)
        passes = doc.multiBuild(story1)
        self.assertEquals(passes, 3)

        #try 2: now preload the TOC with the entries

        toc = tableofcontents.TableOfContents()
        toc.levelStyles = [tocLevelStyle]   #only need one
        tocEntries = []
        for i in range(chapters):
            #add tuple of (level, text, pageNum, key)
            #with an initial guess of pageNum=0
            tocEntries.append((0, 'This is chapter %d' % (i+1), 0, None))
        toc.addEntries(tocEntries)

        story2 = [toc] + story


        path = outputfile('test_platypus_toc_preload.pdf')
        doc = MyDocTemplate(path)
        passes = doc.multiBuild(story2)
        self.assertEquals(passes, 2)



        #try 3: preload again but try to be really smart and work out
        #in advance what page everything starts on.  We cannot
        #use a random story for this.


        toc3 = tableofcontents.TableOfContents()
        toc3.levelStyles = [tocLevelStyle]   #only need one
        tocEntries = []
        for i in range(chapters):
            #add tuple of (level, text, pageNum, key)
            #with an initial guess of pageNum= 3
            tocEntries.append((0, 'This is chapter %d' % i, 2+i, None))
        toc3.addEntries(tocEntries)

        story3 = [toc3] 
        for i in range(chapters):
            story3.append(PageBreak())
            story3.append(Paragraph('This is chapter %d' % (i+1),
                                   headerStyle))
            txt = """
                The paragraphs in this are not at all random, because
                we need to be absolutely, totally certain they will fit 
                on one page.  Each chapter will be one page long.
            """
            para = Paragraph(txt, makeBodyStyle())
            story3.append(para)


        path = outputfile('test_platypus_toc_preload.pdf')
        doc = MyDocTemplate(path)
        passes = doc.multiBuild(story3)

        # I can't get one pass yet'
        #self.assertEquals(passes, 1)

    def test2(self):
        chapters = 20   #so we know we use only one page
        from reportlab.lib.colors import pink

        #TOC and this HParagraph class just handle the collection
        TOC = []
        fontSize = 14
        leading = fontSize*1.2
        descent = 0.2*fontSize
        x = 2.5*cm          #these come from the frame size
        y = (25+2.5)*cm - leading
        x1 = (15+2.5)*cm

        class HParagraph(Paragraph):
            def __init__(self,key,text,*args,**kwds):
                self._label = text
                self._key = key
                Paragraph.__init__(self,text,*args,**kwds)

            def draw(self):
                Paragraph.draw(self)
                TOC.append((self._label,self.canv.getPageNumber(),self._key))
                self.canv.bookmarkHorizontal('TOC_%s' % self._key,0,+20)

        class UseForm(Flowable):
            _ZEROSIZE = 1
            def __init__(self,formName):
                self._formName = formName
                self.width = self.height = 0

            def draw(self):
                self.canv.doForm(self._formName)
                for i in range(chapters):
                    yb = y - i*leading      #baseline
                    self.canv.linkRect('','TOC_%s' % i,(x,yb-descent,x1,yb+fontSize),thickness=0.5,color=pink,relative=0)

            def drawOn(self,canvas,x,y,_sW=0):
                Flowable.drawOn(self,canvas,0,0,canvas._pagesize[0])

        class MakeForm(UseForm):
            def draw(self):
                canv = self.canv
                canv.saveState()
                canv.beginForm(self._formName)
                canv.setFont("Helvetica",fontSize)
                for i,(text,pageNumber,key) in enumerate(TOC):
                    yb = y - i*leading      #baseline
                    canv.drawString(x,yb,text)
                    canv.drawRightString(x1,y-i*leading,str(pageNumber))
                canv.endForm()
                canv.restoreState()

        headerStyle = makeHeaderStyle(0)
        S = [Spacer(0,180),UseForm('TOC')]
        RT = 'STARTUP COMPUTERS BLAH BUZZWORD STARTREK PRINTING PYTHON CHOMSKY'.split()
        for i in range(chapters):
            S.append(PageBreak())
            S.append(HParagraph(i,'This is chapter %d' % (i+1), headerStyle))
            txt = xmlEscape(randomtext.randomText(RT[i*13 % len(RT)], 15))
            para = Paragraph(txt, makeBodyStyle())
            S.append(para)

        S.append(MakeForm('TOC'))

        doc = MyDocTemplate(outputfile('test_platypus_toc_simple.pdf'))
        doc.build(S)

def makeSuite():
    return makeSuiteForClasses(TocTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
