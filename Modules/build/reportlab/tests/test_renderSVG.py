#!/usr/bin/env python
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys
from xml.dom import minidom
from xml.sax._exceptions import SAXReaderNotAvailable
import unittest
from reportlab.graphics.shapes import *
from reportlab.graphics import renderSVG

def warnIgnoredRestofTest():
    "Raise a warning (if possible) about a not fully completed test."

    version = sys.version_info[:2]
    msg = "XML parser not found - consider installing expat! Rest of test(s) ignored!"
    if version >= (2, 1):
        import warnings
        warnings.warn(msg)
    else:
        # should better also be printed only once...
        print(msg)

# Check if we have a default XML parser available or not.
try:
    import xml
    from xml.sax import make_parser
    p = xml.sax.make_parser()
    HAVE_XML_PARSER = 1
except SAXReaderNotAvailable:
    HAVE_XML_PARSER = 0

def load(path):
    "Helper function to read the generated SVG again."

    doc = minidom.parse(path)
    doc.normalize()
    return doc.documentElement

class RenderSvgSimpleTestCase(unittest.TestCase):
    "Testing renderSVG module."

    def test0(self):
        "Test two strings in drawing."

        path = outputfile("test_renderSVG_simple_test0.svg")

        d = Drawing(200, 100)
        d.add(String(0, 0, "foo"))
        d.add(String(100, 0, "bar"))
        renderSVG.drawToFile(d, path)

        if not HAVE_XML_PARSER:
            warnIgnoredRestofTest()
            return

        svg = load(path)
        fg = svg.getElementsByTagName('g')[0]           # flipping group
        dg = fg.getElementsByTagName('g')[0]            # diagram group
        textChildren = dg.getElementsByTagName('text')  # text nodes
        t0 = textChildren[0].childNodes[0].nodeValue.strip()
        t1 = textChildren[1].childNodes[0].nodeValue.strip()
        assert t0 == 'foo'
        assert t1 == 'bar'

    def test1(self):
        "Test two strings in group in drawing."

        path = outputfile("test_renderSVG_simple_test1.svg")

        d = Drawing(200, 100)
        g = Group()
        g.add(String(0, 0, "foo"))
        g.add(String(100, 0, "bar"))
        d.add(g)
        renderSVG.drawToFile(d, path)

        if not HAVE_XML_PARSER:
            warnIgnoredRestofTest()
            return

        svg = load(path)
        fg = svg.getElementsByTagName('g')[0]           # flipping group
        dg = fg.getElementsByTagName('g')[0]            # diagram group
        g = dg.getElementsByTagName('g')[0]             # custom group
        textChildren = g.getElementsByTagName('text')   # text nodes
        t0 = textChildren[0].childNodes[0].nodeValue.strip()
        t1 = textChildren[1].childNodes[0].nodeValue.strip()

        assert t0 == 'foo'
        assert t1 == 'bar'

    def test2(self):
        "Test two strings in transformed group in drawing."

        path = outputfile("test_renderSVG_simple_test2.svg")

        d = Drawing(200, 100)
        g = Group()
        g.add(String(0, 0, "foo"))
        g.add(String(100, 0, "bar"))
        g.scale(1.5, 1.2)
        g.translate(50, 0)
        d.add(g)
        renderSVG.drawToFile(d, path)

        if not HAVE_XML_PARSER:
            warnIgnoredRestofTest()
            return

        svg = load(path)
        fg = svg.getElementsByTagName('g')[0]           # flipping group
        dg = fg.getElementsByTagName('g')[0]            # diagram group
        g = dg.getElementsByTagName('g')[0]             # custom group
        textChildren = g.getElementsByTagName('text')   # text nodes
        t0 = textChildren[0].childNodes[0].nodeValue.strip()
        t1 = textChildren[1].childNodes[0].nodeValue.strip()

        assert t0 == 'foo'
        assert t1 == 'bar'

    def test3(self):
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        width=300
        height=60

        #Create fairly simple drawing object,
        drawing=Drawing(width, height)

        p=ArcPath(strokeColor=colors.darkgreen,
                          fillColor=colors.green,
                          hrefURL="http://en.wikipedia.org/wiki/Vector_path",
                          hrefTitle="This big letter C is actually a closed vector path.",
                          strokewidth=0)
        p.addArc(1*cm, 1*cm, 0.8*cm, 20, 340, moveTo=True)
        p.addArc(1*cm, 1*cm, 0.9*cm, 20, 340, reverse=True)
        p.closePath()
        drawing.add(p)

        drawing.add(Rect(2.25*cm, 0.1*cm, 1.5*cm, 0.8*cm, rx=0.25*cm, ry=0.25*cm,

        hrefURL="http://en.wikipedia.org/wiki/Rounded_rectangle",
                               hrefTitle="Rounded Rectangle",
                               strokeColor=colors.red,
                               fillColor=colors.yellow))

        drawing.add(String(1*cm, 1*cm, "Hello World!",
                                 hrefURL="http://en.wikipedia.org/wiki/Hello_world",
                                 hrefTitle="Why 'Hello World'?",
                                 fillColor=colors.darkgreen))
        drawing.add(Rect(4.5*cm, 0.5*cm, 5*cm, 1*cm,
                                hrefURL="http://en.wikipedia.org/wiki/Rectangle",
                                hrefTitle="Wikipedia page on rectangles",
                                strokeColor=colors.blue,
                                fillColor=colors.red))
        drawing.add(Ellipse(7*cm, 1*cm, 2*cm, 0.95*cm,
                                  hrefURL="http://en.wikipedia.org/wiki/Ellipse",
                                  strokeColor=colors.black,
                                  fillColor=colors.yellow))
        drawing.add(Circle(7*cm, 1*cm, 0.9*cm,
                                  hrefURL="http://en.wikipedia.org/wiki/Circle",
                                 strokeColor=colors.black,
                                 fillColor=colors.brown))
        drawing.add(Ellipse(7*cm, 1*cm, 0.5*cm, 0.9*cm,
                                  hrefTitle="Tooltip with no link?",
                                  strokeColor=colors.black,
                                  fillColor=colors.black))
        drawing.add(Polygon([4.5*cm, 1.25*cm, 5*cm, 0.1*cm, 4*cm, 0.1*cm],
                                  hrefURL="http://en.wikipedia.org/wiki/Polygon",
                                  hrefTitle="This triangle is a simple polygon.",
                                  strokeColor=colors.darkgreen,
                                  fillColor=colors.green))

        renderSVG.drawToFile(drawing, outputfile("test_renderSVG_simple_test3.svg"))

    def test4(self):
        "Test character encoding."

        path = outputfile("test_renderSVG_simple_test4.svg")
        specialChar = u'\u2019'

        d = Drawing(200, 100)
        d.add(String(0, 0, "foo"+specialChar))
        d.add(String(100, 0, "bar"))
        renderSVG.drawToFile(d, path)

        if not HAVE_XML_PARSER:
            warnIgnoredRestofTest()
            return

        svg = load(path)
        fg = svg.getElementsByTagName('g')[0]           # flipping group
        dg = fg.getElementsByTagName('g')[0]            # diagram group
        textChildren = dg.getElementsByTagName('text')  # text nodes
        t0 = textChildren[0].childNodes[0].nodeValue.strip()
        t1 = textChildren[1].childNodes[0].nodeValue.strip()
        assert t0 == 'foo'+specialChar, "%s should equal %s" % (ascii(t0),ascii('foo'+specialChar))
        assert t1 == 'bar'

    def tearDown(self):
        "When finished, make a little index page to view them in situ"
        
        body = """<html>
    <head><title>renderSVG test output</title></head>
    <body>
        <h1>renderSVG test output in a web page</h1>
        <p>We have four SVG diagrams embedded in this page.  Each is within a cyan-coloured div.
        The first 3 have a native size of 400x200, thus consume a height of 200 pixels on
        the page.  The last is 300x60.</p>

        <div style="background-color:cyan">
            <embed src="test_renderSVG_simple_test0.svg" type="image/svg+xml" />
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderSVG_simple_test1.svg" type="image/svg+xml" />
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderSVG_simple_test2.svg" type="image/svg+xml" />
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderSVG_simple_test3.svg" type="image/svg+xml" />
        </div>

        <hr>
        <p>Test of resizing:  the ones below are sized 50%, 100%, 150%. We did this by explicitly setting
        the width and height in the <code>embed</code> tag.</p>
        <div style="background-color:cyan">
            <embed src="test_renderSVG_simple_test3.svg" type="image/svg+xml" width="150" height="45"/>
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderSVG_simple_test3.svg" type="image/svg+xml" width="300" height="60"/>
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderSVG_simple_test3.svg" type="image/svg+xml" width="450" height="90"/>
        </div>
        <hr/>

        <p>Test of resizing again:  the ones below are sized 50%, 100%, 150% by setting width only.</p>
        <div style="background-color:cyan">
            <embed src="test_renderSVG_simple_test3.svg" type="image/svg+xml" width="150"/>
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderSVG_simple_test3.svg" type="image/svg+xml" width="300"/>
        </div>
        <hr/>
        <div style="background-color:cyan">
            <embed src="test_renderSVG_simple_test3.svg" type="image/svg+xml" width="450"/>
        </div>
        <hr/>

        
    </body>
<html>
"""
        open('test_renderSVG_output.html', 'w').write(body)
        


class RenderSvgAxesTestCase(unittest.TestCase):
    "Testing renderSVG module on Axes widgets."

    def test0(self):
        "Test two strings in drawing."

        path = outputfile("axestest0.svg")
        from reportlab.graphics.charts.axes import XCategoryAxis

        d = XCategoryAxis().demo()
        renderSVG.drawToFile(d, path)

def makeSuite():
    return makeSuiteForClasses(RenderSvgSimpleTestCase, RenderSvgAxesTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
