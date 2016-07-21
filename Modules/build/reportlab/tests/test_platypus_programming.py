#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__version__=''' $Id$ '''

#tests and documents Page Layout API
__doc__="""Tests low level programming of doc templates
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys
import unittest
class PlatypusProgrammingTestCase(unittest.TestCase):
    "test platypus programming"

    def test0(self):
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus.flowables import DocPara, DocAssert
        from reportlab.platypus.doctemplate import SimpleDocTemplate
        def func(val):
            story = [
                    DocAssert(val,'this should fail'),
                    DocPara('repr(doc._nameSpace)',escape=True),
                    ]
            doc = SimpleDocTemplate(outputfile('test_doc_programming_asserts.pdf'))
            doc.build(story)
        self.assertRaises(AssertionError,func,False)
        func(True)

    def test1(self):
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.platypus.flowables import DocAssign, DocExec, DocPara, DocIf, DocWhile
        normal = ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=8.5, leading=11)
        header = ParagraphStyle(name='Heading1', parent=normal, fontSize=14, leading=19,
                    spaceAfter=6, keepWithNext=1)
        story = [
                DocAssign('currentFrame','doc.frame.id'),
                DocAssign('currentPageTemplate','doc.pageTemplate.id'),
                DocAssign('aW','availableWidth'),
                DocAssign('aH','availableHeight'),
                DocAssign('aWH','availableWidth,availableHeight'),
                DocAssign('i',3),
                DocIf('i>3',Paragraph('The value of i is larger than 3',normal),Paragraph('The value of i is not larger than 3',normal)),
                DocIf('i==3',Paragraph('The value of i is equal to 3',normal),Paragraph('The value of i is not equal to 3',normal)),
                DocIf('i<3',Paragraph('The value of i is less than 3',normal),Paragraph('The value of i is not less than 3',normal)),
                DocWhile('i',[DocPara('i',format='The value of i is %(__expr__)d',style=normal),DocExec('i-=1')]),
                DocPara('repr(doc._nameSpace)',escape=True),
                DocPara('doc.canv.getPageNumber()','The current page number is %(__expr__)d',style=normal) 
                ]
        doc = SimpleDocTemplate(outputfile('test_doc_programming.pdf'))
        doc.build(story)

    def test2(self):
        "This makes one long multi-page paragraph in multi-pass for testing docWhile etc etc"
        from reportlab.platypus.flowables import DocAssign, DocExec, DocPara, DocIf, DocWhile
        from test_platypus_xref import MyDocTemplate
        from reportlab.platypus.tableofcontents import TableOfContents, SimpleIndex
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import Paragraph
        from reportlab.lib import colors
        from reportlab.lib.randomtext import randomText, PYTHON

        # Build story.
        story = []

        styleSheet = getSampleStyleSheet()
        h1 = styleSheet['Heading1']
        h1.pageBreakBefore = 1
        h1.keepWithNext = 1
        h1.outlineLevel = 0

        h2 = styleSheet['Heading2']
        h2.backColor = colors.cyan
        h2.keepWithNext = 1
        h2.outlineLevel = 1

        bt = styleSheet['BodyText']

        story.append(Paragraph("""Cross-Referencing Test""", styleSheet["Title"]))
        story.append(Paragraph("""
            Subsequent pages test cross-references: indexes, tables and individual
            cross references.  The number in brackets at the end of each paragraph
            is its position in the story. (%d)""" % len(story), bt))

        story.append(Paragraph("""Table of Contents:""", styleSheet["Title"]))
        toc = TableOfContents()
        story.append(toc)

        chapterNum = 1
        for i in range(10):
            story.append(Paragraph('Chapter %d: Chapters always starts a new page' % chapterNum, h1))
            chapterNum += chapterNum
            story.append(DocAssign('chapterNum',chapterNum))
            for j in range(3):
                story.append(Paragraph('Heading1 paragraphs should always'
                                'have a page break before.  Heading 2 on the other hand'
                                'should always have a FRAME break before (%d)' % len(story), bt))
                story.append(Paragraph('Heading 2 should always be kept with the next thing (%d)' % len(story), h2))
                for j in range(3):
                    story.append(Paragraph(randomText(theme=PYTHON, sentences=2)+' (%d)' % len(story), bt))
                    story.append(Paragraph('I should never be at the bottom of a frame (%d)' % len(story), h2))
                    story.append(Paragraph(randomText(theme=PYTHON, sentences=1)+' (%d)' % len(story), bt))

            story.extend([
                    DocAssign('currentFrame','doc.frame.id'),
                    DocAssign('currentPageTemplate','doc.pageTemplate.id'),
                    DocAssign('aW','availableWidth'),
                    DocAssign('aH','availableHeight'),
                    DocAssign('aWH','availableWidth,availableHeight'),
                    DocAssign('i',3,life='forever'),
                    DocIf('i>3',Paragraph('The value of i is larger than 3',bt),Paragraph('The value of i is not larger than 3',bt)),
                    DocIf('i==3',Paragraph('The value of i is equal to 3',bt),Paragraph('The value of i is not equal to 3',bt)),
                    DocIf('i<3',Paragraph('The value of i is less than 3',bt),Paragraph('The value of i is not less than 3',bt)),
                    DocWhile('i',[DocPara('i',format='The value of i is %(__expr__)d',style=bt),DocExec('i-=1')]),
                    DocPara('repr(doc._nameSpace)',escape=True),
                    DocPara('doc.canv.getPageNumber()','The current page number is %(__expr__)d') 
                    ])
        story.append(Paragraph('The Index which goes at the back', h1))
        story.append(SimpleIndex())

        doc = MyDocTemplate(outputfile('test_platypus_programming_multipass.pdf'))
        doc.multiBuild(story)

def makeSuite():
    return makeSuiteForClasses(PlatypusProgrammingTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
