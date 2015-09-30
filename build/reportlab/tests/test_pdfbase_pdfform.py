from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation, NearTestCase
setOutDir(__name__)
import unittest
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfform

class PdfFormTestCase(NearTestCase):
    def testMultipleUsage(self):
        for i in range(2):
            c = canvas.Canvas(outputfile('test_pdfbase_pdfform_multiple_usage_%s.pdf'%i))
            c.drawString(100, 100, "Test")
            pdfform.buttonFieldAbsolute(c, 'button', 'Off', 200, 200)
            c.save()

    def testAAbsoluteAndRelativeFields(self):
        #the old test1 in pdfform
        c = canvas.Canvas(outputfile("test_pdfbase_pdfform_formtest.pdf"))
        # first page
        c.setFont("Courier", 10)
        c.drawString(100, 500, "hello world")
        pdfform.textFieldAbsolute(c, "fieldA", 100, 600, 100, 20, "default value")
        pdfform.textFieldAbsolute(c, "fieldB", 100, 300, 100, 50, "another default value", multiline=1)
        pdfform.selectFieldAbsolute(c, "fieldC", "France", ["Canada", "France", "China"], 100, 200, 100, 20)
        c.rect(100, 600, 100, 20)
        pdfform.buttonFieldAbsolute(c, "field2", "Yes", 100, 700, width=20, height=20)
        c.rect(100, 700, 20, 20)
        pdfform.buttonFieldAbsolute(c, "field3", "Off", 100, 800, width=20, height=20)
        c.rect(100, 800, 20, 20)
        # second page
        c.showPage()
        c.setFont("Helvetica", 7)
        c.translate(50, 20)
        c.drawString(100, 500, "hello world")
        pdfform.textFieldRelative(c, "fieldA_1", 100, 600, 100, 20, "default value 2")
        c.setStrokeColorRGB(1,0,0)
        c.setFillColorRGB(0,1,0.5)
        pdfform.textFieldRelative(c, "fieldB_1", 100, 300, 100, 50, "another default value 2", multiline=1)
        pdfform.selectFieldRelative(c, "fieldC_1", "France 1", ["Canada 0", "France 1", "China 2"], 100, 200, 100, 20)
        c.rect(100, 600, 100, 20)
        pdfform.buttonFieldRelative(c, "field2_1", "Yes", 100, 700, width=20, height=20)
        c.rect(100, 700, 20, 20)
        pdfform.buttonFieldRelative(c, "field3_1", "Off", 100, 800, width=20, height=20)
        c.rect(100, 800, 20, 20)
        c.save()

def makeSuite():
    return makeSuiteForClasses(PdfFormTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
