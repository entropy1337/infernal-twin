#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
"""Tests for the reportlab.lib.colors module.
"""
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import os, math
import unittest
from reportlab.pdfgen.canvas import Canvas
import reportlab.pdfgen.canvas
from reportlab.lib import colors
from reportlab.lib.units import inch, cm

def framePage(canvas, title):
    canvas.setFont('Times-BoldItalic',20)
    canvas.drawString(inch, 10.5 * inch, title)

    canvas.setFont('Times-Roman',10)
    canvas.drawCentredString(4.135 * inch, 0.75 * inch,
                            'Page %d' % canvas.getPageNumber())

    #draw a border
    canvas.setStrokeColorRGB(1,0,0)
    canvas.setLineWidth(5)
    canvas.line(0.8 * inch, inch, 0.8 * inch, 10.75 * inch)
    #reset carefully afterwards
    canvas.setLineWidth(1)
    canvas.setStrokeColorRGB(0,0,0)


class ColorTestCase(unittest.TestCase):
    ""

    def test0(self):
        "Test color2bw function on all named colors."

        cols = list(colors.getAllNamedColors().values())
        for col in cols:
            gray = colors.color2bw(col)
            r, g, b = gray.red, gray.green, gray.blue
            assert r == g == b


    def test1(self):
        "Test colorDistance function."

        cols = list(colors.getAllNamedColors().values())
        for col in cols:
            d = colors.colorDistance(col, col)
            assert d == 0


    def test2(self):
        "Test toColor function on half a dozen ways to say 'red'."

        allRed = [colors.red, [1, 0, 0], (1, 0, 0),
                  b'red', b'RED', b'0xFF0000', b'0xff0000',b'rgb(255,0,0)',
                  u'red', u'RED', u'0xFF0000', u'0xff0000',u'rgb(255,0,0)',
                  ]

        for thing in allRed:
            assert colors.toColor(thing) == colors.red,"colors.toColor(%s)-->%s != colors.red(%s)" % (ascii(thing),ascii(colors.toColor(thing)),colors.red)


    def test3(self):
        "Test roundtrip RGB to CMYK conversion."

        # Take all colors as test subjects, except 'transparent'.
##        rgbCols = colors.getAllNamedColors()
##        del rgbCols['transparent']
        rgbCols = list(colors.getAllNamedColors().items())

        # Make a roundtrip test (RGB > CMYK > RGB).
        for name, rgbCol in rgbCols:
            r1, g1, b1 = rgbCol.red, rgbCol.green, rgbCol.blue
            c, m, y, k = colors.rgb2cmyk(r1, g1, b1)
            r2, g2, b2 = colors.cmyk2rgb((c, m, y, k))
            rgbCol2 = colors.Color(r2, g2, b2)

            # Make sure the differences for each RGB component
            # isreally small (< power(10, -N)!
            N = 16 # max. value found to work on Python2.0 and Win2K.
            deltas = list(map(abs, (r1-r2, g1-g2, b1-b2)))
            assert deltas < [math.pow(10, -N)] * 3

    def test4(self):
        "Construct CMYK instances and test round trip conversion"

        rgbCols = list(colors.getAllNamedColors().items())

        # Make a roundtrip test (RGB > CMYK > RGB).
        for name, rgbCol in rgbCols:
            r1, g1, b1 = rgbCol.red, rgbCol.green, rgbCol.blue
            c, m, y, k = colors.rgb2cmyk(r1, g1, b1)
            cmykCol = colors.CMYKColor(c,m,y,k)
            r2, g2, b2 = cmykCol.red, cmykCol.green, cmykCol.blue #colors.cmyk2rgb((c, m, y, k))
            rgbCol2 = colors.Color(r2, g2, b2)

            # Make sure the differences for each RGB component
            # isreally small (< power(10, -N)!
            N = 16 # max. value found to work on Python2.0 and Win2K.
            deltas = list(map(abs, (r1-r2, g1-g2, b1-b2)))
            assert deltas < [math.pow(10, -N)] * 3

    def test5(self):
        "List and display all named colors and their gray equivalents."

        canvas = reportlab.pdfgen.canvas.Canvas(outputfile('test_lib_colors.pdf'))

        #do all named colors
        framePage(canvas, 'Color Demo - page %d' % canvas.getPageNumber())

        all_colors = list(reportlab.lib.colors.getAllNamedColors().items())
        all_colors.sort() # alpha order by name
        canvas.setFont('Times-Roman', 10)
        text = 'This shows all the named colors in the HTML standard (plus their gray and CMYK equivalents).'
        canvas.drawString(72,740, text)

        canvas.drawString(200,725,'Pure RGB')
        canvas.drawString(300,725,'B&W Approx')
        canvas.drawString(400,725,'CMYK Approx')

        y = 700
        for (name, color) in all_colors:
            canvas.setFillColor(colors.black)
            canvas.drawString(100, y, name)
            canvas.setFillColor(color)
            canvas.rect(200, y-10, 80, 30, fill=1)
            canvas.setFillColor(colors.color2bw(color))
            canvas.rect(300, y-10, 80, 30, fill=1)

            c, m, yel, k = colors.rgb2cmyk(color.red, color.green, color.blue)
            CMYK = colors.CMYKColor(c,m,yel,k)
            canvas.setFillColor(CMYK)
            canvas.rect(400, y-10, 80, 30, fill=1)

            y = y - 40
            if y < 100:
                canvas.showPage()
                framePage(canvas, 'Color Demo - page %d' % canvas.getPageNumber())
                canvas.setFont('Times-Roman', 10)
                y = 700
                canvas.drawString(200,725,'Pure RGB')
                canvas.drawString(300,725,'B&W Approx')
                canvas.drawString(400,725,'CMYK Approx')

        canvas.save()

    def test6(self):
        '''test HexColor'''
        HexColor = colors.HexColor
        Color = colors.Color
        self.assertEquals(HexColor(0xffffff),Color(1,1,1,1))
        self.assertEquals(HexColor(16777215),Color(1,1,1,1))
        self.assertEquals(HexColor(b'#ffffff'),Color(1,1,1,1))
        self.assertEquals(HexColor(b'#FFFFFF'),Color(1,1,1,1))
        self.assertEquals(HexColor(b'0xffffff'),Color(1,1,1,1))
        self.assertEquals(HexColor(b'0xFFFFFF'),Color(1,1,1,1))
        self.assertEquals(HexColor(b'16777215'),Color(1,1,1,1))
        self.assertRaisesRegexp(ValueError,r"invalid literal for int\(\) with base 10:.*ffffff",HexColor,b'ffffff')
        self.assertEquals(HexColor(b'#FFFFFF', htmlOnly=True),Color(1,1,1,1))
        self.assertRaisesRegexp(ValueError,"not a hex string",HexColor,b'0xffffff',htmlOnly=True)
        self.assertRaisesRegexp(ValueError,"not a hex string",HexColor,b'16777215',htmlOnly=True)
        self.assertEquals(HexColor(u'#ffffff'),Color(1,1,1,1))
        self.assertEquals(HexColor(u'#FFFFFF'),Color(1,1,1,1))
        self.assertEquals(HexColor(u'0xffffff'),Color(1,1,1,1))
        self.assertEquals(HexColor(u'0xFFFFFF'),Color(1,1,1,1))
        self.assertEquals(HexColor(u'16777215'),Color(1,1,1,1))
        self.assertRaisesRegexp(ValueError,r"invalid literal for int\(\) with base 10:.*ffffff",HexColor,u'ffffff')
        self.assertEquals(HexColor(u'#FFFFFF', htmlOnly=True),Color(1,1,1,1))
        self.assertRaisesRegexp(ValueError,"not a hex string",HexColor,u'0xffffff',htmlOnly=True)
        self.assertRaisesRegexp(ValueError,"not a hex string",HexColor,u'16777215',htmlOnly=True)

def makeSuite():
    return makeSuiteForClasses(ColorTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
