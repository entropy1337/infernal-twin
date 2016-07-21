#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
"""Tests for the Platypus SimpleIndex and AlphabeticIndex classes.
"""
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys, os
from os.path import join, basename, splitext
from math import sqrt
import unittest
from reportlab.lib.units import cm
from reportlab.lib.utils import commajoin, asUnicode
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate
from reportlab.platypus.tableofcontents import SimpleIndex
from reportlab.lib import randomtext
import re
from xml.sax.saxutils import quoteattr

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

def makeBodyStyle():
    "Body text style - the default will do"
    return ParagraphStyle('body', spaceBefore=20)
    
class IndexTestCase(unittest.TestCase):
    "Test SimpleIndex classes (eyeball-test)."

    def test0(self):
        '''
        Test case for Indexes. This will draw an index %sat the end of the
        document with dots seperating the indexing terms from the page numbers.
        Index terms are grouped by their first 2, and first 3 characters.
        The page numbers should be clickable and link to the indexed word.
        '''
        # Build story.
        
        for headers in False, True:
            path = outputfile('test_platypus_index%s.pdf' % (headers and '_headers' or ''))
            doc = MyDocTemplate(path)
            story = []
            styleSheet = getSampleStyleSheet()
            bt = styleSheet['BodyText']
    
            description = '<font color=red>%s</font>' % (self.test0.__doc__  % (headers and 'with alphabetic headers ' or ''))
            story.append(Paragraph(description, bt))
            index = SimpleIndex(dot=' . ', headers=headers)

            def addParas(words):
                words = [asUnicode(w) for w in words]
                txt = u' '.join([(len(w) > 5 and u'<index item=%s/>%s' % (quoteattr(commajoin([w[:2], w[:3], w])), w) or w) for w in words])
                para = Paragraph(txt, makeBodyStyle())
                story.append(para)
    
            for i in xrange(20):
                addParas(randomtext.randomText(randomtext.PYTHON, 5).split(' '))
            addParas([u+w for u in u'E\xc8\xc9\xca\xcb' for w in (u'erily',u'asily')])
            addParas([u+w for u in u'A\xc0\xc4\xc1\xc3\xc2' for w in (u'dvance',u'ttend')])
            addParas([u+w for u in u'O\xd2\xd6\xd3\xd2' for w in (u'rdinary',u'verflow')])
            addParas([u+w for u in u'U\xd9\xdc\xdb' for w in (u'ndertow',u'nbeliever')])
            addParas([u+w for u in u'e\xe8\xea\xeb\xe9' for w in (u'ventide',u'lision')])
            addParas([u+w for u in u'o\xf2\xf5\xf3\xf4' for w in (u'verture',u'ntology')])

            #test ampersand in index term
            txt = '\nMarks &amp; Spencer - purveyors of fine groceries, underwear and ampersands - should have their initials displayed however they were input.\n<index item="M&amp;S,groceries"/><index item="M&amp;S,underwear"/><index item="M&amp;S,ampersands"/>'
            para = Paragraph(txt, makeBodyStyle())
            story.append(para)
        

            story.append(index)
    
            doc.build(story, canvasmaker=index.getCanvasMaker())

def makeSuite():
    return makeSuiteForClasses(IndexTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
