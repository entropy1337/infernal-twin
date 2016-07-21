from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import os,unittest
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle, LongTable
from reportlab.platypus.doctemplate import PageAccumulator
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors

styleSheet = getSampleStyleSheet()

class MyPageAccumulator(PageAccumulator):
    def pageEndAction(self,canv,doc):
        L42 = [x[0] for x in self.data if not x[0]%42]
        L13 = [x[0] for x in self.data if not x[0]%13]
        if L42 and L13:
            s = 'Saw multiples of 13 and 42'
        elif L13:
            s = 'Saw multiples of 13'
        elif L42:
            s = 'Saw multiples of 42'
        else:
            return
        canv.saveState()
        canv.setFillColor(colors.purple)
        canv.setFont("Helvetica",6)
        canv.drawString(1*inch,1*inch,s)
        canv.restoreState()

PA = MyPageAccumulator('_42_divides')
class MyDocTemplate(SimpleDocTemplate):
    def beforeDocument(self):
        for pt in self.pageTemplates:
            PA.attachToPageTemplate(pt)

def textAccum2():
    doc = MyDocTemplate(outputfile('test_platypus_accum2.pdf'),
            pagesize=(8.5*inch, 11*inch), showBoundary=1)
    story=[]
    story.append(Paragraph("A table with 500 rows", styleSheet['BodyText']))
    sty = [ ('GRID',(0,0),(-1,-1),1,colors.green),
            ('BOX',(0,0),(-1,-1),2,colors.red),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
            ('FONTSIZE',(0,0),(-1,-1),10),
           ]
    def myCV(s,fontName='Helvetica',fontSize=10,maxWidth=72):
        return '\n'.join(simpleSplit(s,fontName,fontSize,maxWidth))

    data = [[PA.onDrawStr(str(i+1),i+1),
                myCV("xx "* (i%10),maxWidth=100-12),
                myCV("blah "*(i%40),maxWidth=200-12)]
                    for i in range(500)]
    t=LongTable(data, style=sty, colWidths = [50,100,200])
    story.append(t)
    doc.build(story)

def textAccum1():
    doc = MyDocTemplate(outputfile('test_platypus_accum1.pdf'),
            pagesize=(8.5*inch, 11*inch), showBoundary=1)
    story=[]
    story.append(Paragraph("A table with 500 rows", styleSheet['BodyText']))
    sty = [ ('GRID',(0,0),(-1,-1),1,colors.green),
            ('BOX',(0,0),(-1,-1),2,colors.red),
           ]
    data = [[str(i+1), Paragraph("xx "* (i%10),
                styleSheet["BodyText"]),
                Paragraph(("blah "*(i%40))+PA.onDrawText(i+1), styleSheet["BodyText"])]
                    for i in range(500)]
    t=LongTable(data, style=sty, colWidths = [50,100,200])
    story.append(t)
    doc.build(story)


class TablesTestCase(unittest.TestCase):
    "Make documents with tables"

    def test1(self):
        textAccum1()

    def test2(self):
        textAccum2()

def makeSuite():
    return makeSuiteForClasses(TablesTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
