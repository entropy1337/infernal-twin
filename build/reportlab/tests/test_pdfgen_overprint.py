#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
# full screen test
"""Tests for overprint/knockout.

This has been placed in a separate file so output can be passed to printers
"""
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest

class OverprintTestCase(unittest.TestCase):
    "Testing overprint/knockout."


    def test0(self):
        "This should open in full screen mode."
        import os
        from reportlab.pdfgen.canvas import Canvas
        from reportlab.lib.colors import PCMYKColor, PCMYKColorSep
        filename = 'test_pdfgen_overprint.pdf'
        desc = "Overprint/knockout tests for ReportLab library"

        black = PCMYKColor(0,0,0,100)
        cyan = PCMYKColorSep(100,0,0,0,spotName='myCyan')
        magenta = PCMYKColorSep(0,100,0,0,spotName='myMagenta')

        c = Canvas(filename)
        c.setFillColor(black)
        c.setFont('Helvetica', 20)
        c.drawString(100, 700, desc)

        c.setFont('Helvetica', 10)
        c.drawString(100, 670, "To view this page properly you probably need to enable 'overprint preview' in Acrobat Reader")
        c.drawString(100, 658, "or use a tool like Illustrator, Quark or Acrobat to view separated plates. Starting in")
        c.drawString(100, 646, "Acrobat Reader 9 there is a setting that lets you turn on the overprint preview, although")
        c.drawString(100, 634, "it's not on by default (Preferences > Page Display > Use Overprint Preview: Always).")
        
        c.drawString(100, 616, "In the top example, the magenta rectangle overprints the cyan one. In the lower one, it")
        c.drawString(100, 604, "'knocks out' the cyan underneath which is the default in PDF. This means that the overlap")
        c.drawString(100, 592, "area of the first example should show blue, because the two colours merge. However, in many")
        c.drawString(100, 580, "PDF viewers and cheap printers, both examples will probably look the same - magenta")
        c.drawString(100, 568, "rectangle knocks out part of the cyan one.")
        
        c.drawString(100, 550, "If you can view the separated CMYK plates in a tool like Illustrator, on the cyan plate")
        c.drawString(100, 538, "you should see the top rectangle as complete and the bottom one has a chunk knocked out of")
        c.drawString(100, 526, "the top right corner.")

        c.setFillOverprint(True)
        c.setFillColor(cyan)
        c.rect(100, 300, 200, 100, fill=True, stroke=False)
        c.setFillColor(magenta)
        c.rect(200, 350, 200, 100, fill=True, stroke=False)

        c.setFillOverprint(False)
        c.setFillColor(cyan)
        c.rect(100, 100, 200, 100, fill=True, stroke=False)
        c.setFillColor(magenta)
        c.rect(200, 150, 200, 100, fill=True, stroke=False)

        c.save()
        assert os.path.exists(filename)


def makeSuite():
    return makeSuiteForClasses(OverprintTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
