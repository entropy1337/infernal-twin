#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__doc__='testscript for reportlab.pdfgen'
__version__=''' $Id$ '''
#tests and documents new low-level canvas
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import os
import unittest
from reportlab.pdfgen import canvas   # gmcm 2000/10/13, pdfgen now a package
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.utils import haveImages, fileName2FSEnc

#################################################################
#
#  first some drawing utilities
#
#
################################################################

BASEFONT = ('Times-Roman', 10)
def framePageForm(c):
    c.beginForm("frame")
    c.saveState()
    # forms can't do non-constant operations
    #canvas.setFont('Times-BoldItalic',20)
    #canvas.drawString(inch, 10.5 * inch, title)

    #c.setFont('Times-Roman',10)
    #c.drawCentredString(4.135 * inch, 0.75 * inch,
    #                        'Page %d' % c.getPageNumber())

    #draw a border
    c.setFillColor(colors.ReportLabBlue)
    c.rect(0.3*inch, inch, 0.5*inch, 10*inch, fill=1)
    from reportlab.lib import corp
    c.translate(0.8*inch, 9.6*inch)
    c.rotate(90)
    logo = corp.ReportLabLogo(width=1.3*inch, height=0.5*inch, powered_by=1)
    c.setFillColorRGB(1,1,1)
    c.setStrokeColorRGB(1,1,1)
    logo.draw(c)
    #c.setStrokeColorRGB(1,0,0)
    #c.setLineWidth(5)
    #c.line(0.8 * inch, inch, 0.8 * inch, 10.75 * inch)
    #reset carefully afterwards
    #canvas.setLineWidth(1)
    #canvas.setStrokeColorRGB(0,0,0)\
    c.restoreState()
    c.endForm()

def framePage(canvas, title):
    global closeit
    titlelist.append(title)
    #canvas._inPage0()  # do we need this at all?  would be good to eliminate it
    canvas.saveState()
    canvas.setFont('Times-BoldItalic',20)

    canvas.drawString(inch, 10.5 * inch, title)
    canvas.bookmarkHorizontalAbsolute(title, 10.8*inch)
    #newsection(title)
    canvas.addOutlineEntry(title+" section", title, level=0, closed=closeit)
    closeit = not closeit # close every other one
    canvas.setFont('Times-Roman',10)
    canvas.drawCentredString(4.135 * inch, 0.75 * inch,
                            'Page %d' % canvas.getPageNumber())
    canvas.restoreState()
    canvas.doForm("frame")


def makesubsection(canvas, title, horizontal):
    canvas.bookmarkHorizontalAbsolute(title, horizontal)
    #newsubsection(title)
    canvas.addOutlineEntry(title+" subsection", title, level=1)


# outline helpers
#outlinenametree = []
#def newsection(name):
#    outlinenametree.append(name)


#def newsubsection(name):
#    thissection = outlinenametree[-1]
#    if not isinstance(thissection,tuple):
#        subsectionlist = []
#        thissection = outlinenametree[-1] = (thissection, subsectionlist)
#    else:
#        (sectionname, subsectionlist) = thissection
#    subsectionlist.append(name)


class DocBlock:
    """A DocBlock has a chunk of commentary and a chunk of code.
    It prints the code and commentary, then executes the code,
    which is presumed to draw in a region reserved for it.
    """
    def __init__(self):
        self.comment1 = "A doc block"
        self.code = "canvas.setTextOrigin(cm, cm)\ncanvas.textOut('Hello World')"
        self.comment2 = "That was a doc block"
        self.drawHeight = 0

    def _getHeight(self):
        "splits into lines"
        self.comment1lines = self.comment1.split('\n')
        self.codelines = self.code.split('\n')
        self.comment2lines = self.comment2.split('\n')
        textheight = (len(self.comment1lines) +
                len(self.code) +
                len(self.comment2lines) +
                18)
        return max(textheight, self.drawHeight)

    def draw(self, canvas, x, y):
        #specifies top left corner
        canvas.saveState()
        height = self._getHeight()
        canvas.rect(x, y-height, 6*inch, height)
        #first draw the text
        canvas.setTextOrigin(x + 3 * inch, y - 12)
        canvas.setFont('Times-Roman',10)
        canvas.textLines(self.comment1)
        drawCode(canvas, self.code)
        canvas.textLines(self.comment2)

        #now a box for the drawing, slightly within rect
        canvas.rect(x + 9, y - height + 9, 198, height - 18)
        #boundary:
        self.namespace = {'canvas':canvas,'cm': cm,'inch':inch}
        canvas.translate(x+9, y - height + 9)
        codeObj = compile(self.code, '<sample>','exec')
        exec(codeObj, self.namespace)

        canvas.restoreState()


def drawAxes(canvas, label):
    """draws a couple of little rulers showing the coords -
    uses points as units so you get an imperial ruler
    one inch on each side"""
    #y axis
    canvas.line(0,0,0,72)
    for y in range(9):
        tenths = (y+1) * 7.2
        canvas.line(-6,tenths,0,tenths)
    canvas.line(-6, 66, 0, 72)  #arrow...
    canvas.line(6, 66, 0, 72)  #arrow...

    canvas.line(0,0,72,0)
    for x in range(9):
        tenths = (x+1) * 7.2
        canvas.line(tenths,-6,tenths, 0)
    canvas.line(66, -6, 72, 0)  #arrow...
    canvas.line(66, +6, 72, 0)  #arrow...

    canvas.drawString(18, 30, label)


def drawCrossHairs(canvas, x, y):
    """just a marker for checking text metrics - blue for fun"""

    canvas.saveState()
    canvas.setStrokeColorRGB(0,1,0)
    canvas.line(x-6,y,x+6,y)
    canvas.line(x,y-6,x,y+6)
    canvas.restoreState()


def drawCode(canvas, code):
    """Draws a block of text at current point, indented and in Courier"""
    canvas.addLiteral('36 0 Td')
    canvas.setFillColor(colors.blue)
    canvas.setFont('Courier',10)

    t = canvas.beginText()
    t.textLines(code)
    c.drawText(t)

    canvas.setFillColor(colors.black)
    canvas.addLiteral('-36 0 Td')
    canvas.setFont('Times-Roman',10)


def makeDocument(filename, pageCallBack=None):
    #the extra arg is a hack added later, so other
    #tests can get hold of the canvas just before it is
    #saved
    from reportlab.lib.colors import red, green, blue
    global titlelist, closeit
    titlelist = []
    closeit = 0

    c = canvas.Canvas(filename)
    c.setPageCompression(0)
    c.setPageCallBack(pageCallBack)
    framePageForm(c) # define the frame form
    c.showOutline()

    framePage(c, 'PDFgen graphics API test script')
    makesubsection(c, "PDFgen", 10*inch)

    #quickie encoding test: when canvas encoding not set,
    #the following should do (tm), (r) and (c)
    msg_uni = 'copyright\u00A9 trademark\u2122 registered\u00AE scissors\u2702: ReportLab in unicode!'
    msg_utf8 = msg_uni.replace('unicode','utf8').encode('utf8')
    c.drawString(100, 100, msg_uni)
    c.drawString(100, 80, msg_utf8)

    


    t = c.beginText(inch, 10*inch)
    t.setFont('Times-Roman', 10)
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLines("""
The ReportLab library permits you to create PDF documents directly from
your Python code. The "pdfgen" subpackage is the lowest level exposed
to the user and lets you directly position test and graphics on the
page, with access to almost the full range of PDF features.
  The API is intended to closely mirror the PDF / Postscript imaging
model.  There is an almost one to one correspondence between commands
and PDF operators.  However, where PDF provides several ways to do a job,
we have generally only picked one.
  The test script attempts to use all of the methods exposed by the Canvas
class, defined in reportlab/pdfgen/canvas.py
  First, let's look at text output.  There are some basic commands
to draw strings:
-    canvas.setFont(fontname, fontsize [, leading])
-    canvas.drawString(x, y, text)
-    canvas.drawRightString(x, y, text)
-    canvas.drawCentredString(x, y, text)

The coordinates are in points starting at the bottom left corner of the
page.  When setting a font, the leading (i.e. inter-line spacing)
defaults to 1.2 * fontsize if the fontsize is not provided.

For more sophisticated operations, you can create a Text Object, defined
in reportlab/pdfgen/testobject.py.  Text objects produce tighter PDF, run
faster and have many methods for precise control of spacing and position.
Basic usage goes as follows:
-   tx = canvas.beginText(x, y)
-   tx.textOut('Hello')    # this moves the cursor to the right
-   tx.textLine('Hello again') # prints a line and moves down
-   y = tx.getY()       # getX, getY and getCursor track position
-   canvas.drawText(tx)  # all gets drawn at the end

The green crosshairs below test whether the text cursor is working
properly.  They should appear at the bottom left of each relevant
substring.
""")

    t.setFillColorRGB(1,0,0)
    t.setTextOrigin(inch, 4*inch)
    drawCrossHairs(c, t.getX(),t.getY())
    t.textOut('textOut moves across:')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textOut('textOut moves across:')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textOut('textOut moves across:')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLine('')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLine('textLine moves down')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLine('textLine moves down')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLine('textLine moves down')
    drawCrossHairs(c, t.getX(),t.getY())

    t.setTextOrigin(4*inch,3.25*inch)
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLines('This is a multi-line\nstring with embedded newlines\ndrawn with textLines().\n')
    drawCrossHairs(c, t.getX(),t.getY())
    t.textLines(['This is a list of strings',
                'drawn with textLines().'])
    c.drawText(t)

    t = c.beginText(2*inch,2*inch)
    t.setFont('Times-Roman',10)
    drawCrossHairs(c, t.getX(),t.getY())
    t.textOut('Small text.')
    drawCrossHairs(c, t.getX(),t.getY())
    t.setFont('Courier',14)
    t.textOut('Bigger fixed width text.')
    drawCrossHairs(c, t.getX(),t.getY())
    t.setFont('Times-Roman',10)
    t.textOut('Small text again.')
    drawCrossHairs(c, t.getX(),t.getY())
    c.drawText(t)

    #try out the decimal tabs high on the right.
    c.setStrokeColor(colors.silver)
    c.line(7*inch, 6*inch, 7*inch, 4.5*inch)

    c.setFillColor(colors.black)
    c.setFont('Times-Roman',10)
    c.drawString(6*inch, 6.2*inch, "Testing decimal alignment")
    c.drawString(6*inch, 6.05*inch, "- aim for silver line")
    c.line(7*inch, 6*inch, 7*inch, 4.5*inch)

    c.drawAlignedString(7*inch, 5.8*inch, "1,234,567.89")
    c.drawAlignedString(7*inch, 5.6*inch, "3,456.789")
    c.drawAlignedString(7*inch, 5.4*inch, "123")
    c.setFillColor(colors.red)
    c.drawAlignedString(7*inch, 5.2*inch, "(7,192,302.30)")

    #mark the cursor where it stopped
    c.showPage()


    ##############################################################
    #
    # page 2 - line styles
    #
    ###############################################################

    #page 2 - lines and styles
    framePage(c, 'Line Drawing Styles')



    # three line ends, lines drawn the hard way
    #firt make some vertical end markers
    c.setDash(4,4)
    c.setLineWidth(0)
    c.line(inch,9.2*inch,inch, 7.8*inch)
    c.line(3*inch,9.2*inch,3*inch, 7.8*inch)
    c.setDash() #clears it

    c.setLineWidth(5)
    c.setLineCap(0)
    p = c.beginPath()
    p.moveTo(inch, 9*inch)
    p.lineTo(3*inch, 9*inch)
    c.drawPath(p)
    c.drawString(4*inch, 9*inch, 'the default - butt caps project half a width')
    makesubsection(c, "caps and joins", 8.5*inch)

    c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(inch, 8.5*inch)
    p.lineTo(3*inch, 8.5*inch)
    c.drawPath(p)
    c.drawString(4*inch, 8.5*inch, 'round caps')

    c.setLineCap(2)
    p = c.beginPath()
    p.moveTo(inch, 8*inch)
    p.lineTo(3*inch, 8*inch)
    c.drawPath(p)
    c.drawString(4*inch, 8*inch, 'square caps')

    c.setLineCap(0)

    # three line joins
    c.setLineJoin(0)
    p = c.beginPath()
    p.moveTo(inch, 7*inch)
    p.lineTo(2*inch, 7*inch)
    p.lineTo(inch, 6.7*inch)
    c.drawPath(p)
    c.drawString(4*inch, 6.8*inch, 'Default - mitered join')

    c.setLineJoin(1)
    p = c.beginPath()
    p.moveTo(inch, 6.5*inch)
    p.lineTo(2*inch, 6.5*inch)
    p.lineTo(inch, 6.2*inch)
    c.drawPath(p)
    c.drawString(4*inch, 6.3*inch, 'round join')

    c.setLineJoin(2)
    p = c.beginPath()
    p.moveTo(inch, 6*inch)
    p.lineTo(2*inch, 6*inch)
    p.lineTo(inch, 5.7*inch)
    c.drawPath(p)
    c.drawString(4*inch, 5.8*inch, 'bevel join')

    c.setDash(6,6)
    p = c.beginPath()
    p.moveTo(inch, 5*inch)
    p.lineTo(3*inch, 5*inch)
    c.drawPath(p)
    c.drawString(4*inch, 5*inch, 'dash 6 points on, 6 off- setDash(6,6) setLineCap(0)')
    makesubsection(c, "dash patterns", 5*inch)

    c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(inch, 4.5*inch)
    p.lineTo(3*inch, 4.5*inch)
    c.drawPath(p)
    c.drawString(4*inch, 4.5*inch, 'dash 6 points on, 6 off- setDash(6,6) setLineCap(1)')

    c.setLineCap(0)
    c.setDash([1,2,3,4,5,6],0)
    p = c.beginPath()
    p.moveTo(inch, 4.0*inch)
    p.lineTo(3*inch, 4.0*inch)
    c.drawPath(p)
    c.drawString(4*inch, 4*inch, 'dash growing - setDash([1,2,3,4,5,6],0) setLineCap(0)')

    c.setLineCap(1)
    c.setLineJoin(1)
    c.setDash(32,12)
    p = c.beginPath()
    p.moveTo(inch, 3.0*inch)
    p.lineTo(2.5*inch, 3.0*inch)
    p.lineTo(inch, 2*inch)
    c.drawPath(p)
    c.drawString(4*inch, 3*inch, 'dash pattern, join and cap style interacting - ')
    c.drawString(4*inch, 3*inch - 12, 'round join & miter results in sausages')
    c.textAnnotation('Annotation',Rect=(4*inch, 3*inch-72, inch,inch-12))

    c.showPage()


##############################################################
#
# higher level shapes
#
###############################################################
    framePage(c, 'Shape Drawing Routines')

    t = c.beginText(inch, 10*inch)
    t.textLines("""
Rather than making your own paths, you have access to a range of shape routines.
These are built in pdfgen out of lines and bezier curves, but use the most compact
set of operators possible.  We can add any new ones that are of general use at no
cost to performance.""")
    t.textLine()

    #line demo
    makesubsection(c, "lines", 9*inch)
    c.line(inch, 9*inch, 3*inch, 9*inch)
    t.setTextOrigin(4*inch, 9*inch)
    t.textLine('canvas.line(x1, y1, x2, y2)')

    #bezier demo - show control points
    makesubsection(c, "bezier curves", 8.5*inch)
    (x1, y1, x2, y2, x3, y3, x4, y4) = (
                        inch, 7.8*inch,
                        1.2*inch, 8.8 * inch,
                        3*inch, 8.8 * inch,
                        3.5*inch, 8.05 * inch
                        )
    c.bezier(x1, y1, x2, y2, x3, y3, x4, y4)
    c.setDash(3,3)
    c.line(x1,y1,x2,y2)
    c.line(x3,y3,x4,y4)
    c.setDash()
    t.setTextOrigin(4*inch, 8.3 * inch)
    t.textLine('canvas.bezier(x1, y1, x2, y2, x3, y3, x4, y4)')

    #rectangle
    makesubsection(c, "rectangles", 8*inch)
    c.rect(inch, 7 * inch, 2 * inch, 0.75 * inch)
    t.setTextOrigin(4*inch, 7.375 * inch)
    t.textLine('canvas.rect(x, y, width, height) - x,y is lower left')

    c.roundRect(inch,6.25*inch,2*inch,0.6*inch,0.1*inch)
    t.setTextOrigin(4*inch, 6.55*inch)
    t.textLine('canvas.roundRect(x,y,width,height,radius)')

    makesubsection(c, "arcs", 8*inch)
    c.arc(inch,5*inch,3*inch,6*inch,0,90)
    t.setTextOrigin(4*inch, 5.5*inch)
    t.textLine('canvas.arc(x1, y1, x2, y2, startDeg, extentDeg)')
    t.textLine('Note that this is an elliptical arc, not just circular!')


    #wedge
    makesubsection(c, "wedges", 5*inch)
    c.wedge(inch, 4.5*inch, 3*inch, 3.5*inch, 0, 315)
    t.setTextOrigin(4*inch, 4*inch)
    t.textLine('canvas.wedge(x1, y1, x2, y2, startDeg, extentDeg)')
    t.textLine('Note that this is an elliptical arc, not just circular!')

    #wedge the other way
    c.wedge(inch, 3.75*inch, 3*inch, 2.75*inch, 0, -45)
    t.setTextOrigin(4*inch, 3*inch)
    t.textLine('Use a negative extent to go clockwise')

    #circle
    makesubsection(c, "circles", 3.5*inch)
    c.circle(1.5*inch, 2*inch, 0.5 * inch)
    c.circle(3*inch, 2*inch, 0.5 * inch)
    t.setTextOrigin(4*inch, 2 * inch)
    t.textLine('canvas.circle(x, y, radius)')
    c.drawText(t)

    c.showPage()

##############################################################
#
# Page 4 - fonts
#
###############################################################
    framePage(c, "Font Control")

    c.drawString(inch, 10*inch, 'Listing available fonts...')

    y = 9.5*inch
    for fontname in c.getAvailableFonts():
        c.setFont(fontname,24)
        c.drawString(inch, y, 'This should be %s' % fontname)
        y = y - 28
    makesubsection(c, "fonts and colors", 4*inch)

    c.setFont('Times-Roman', 12)
    t = c.beginText(inch, 4*inch)
    t.textLines("""Now we'll look at the color functions and how they interact
    with the text.  In theory, a word is just a shape; so setFillColorRGB()
    determines most of what you see.  If you specify other text rendering
    modes, an outline color could be defined by setStrokeColorRGB() too""")
    c.drawText(t)

    t = c.beginText(inch, 2.75 * inch)
    t.setFont('Times-Bold',36)
    t.setFillColor(green)  #green
    t.textLine('Green fill, no stroke')

    #t.setStrokeColorRGB(1,0,0)  #ou can do this in a text object, or the canvas.
    t.setStrokeColor(red)  #ou can do this in a text object, or the canvas.
    t.setTextRenderMode(2)   # fill and stroke
    t.textLine('Green fill, red stroke - yuk!')

    t.setTextRenderMode(0)   # back to default - fill only
    t.setFillColorRGB(0,0,0)   #back to default
    t.setStrokeColorRGB(0,0,0) #ditto
    c.drawText(t)
    c.showPage()

#########################################################################
#
#  Page 5 - character spacing
#
#########################################################################
    framePage(c, "Character Spacing")

    c.drawString(inch, 10*inch, 'Listing available fonts...')
    def drawBox(x,y,width,height,color=green,anchor='start'):
        if anchor=='end':
            x -= width
        elif anchor in ('centre','center'):
            x = 0.5*width 
        c.saveState()
        c.setDash(2,2)
        c.setStrokeColor(color)
        c.setLineWidth(0.01)
        c.rect(x,y,width,height,fill=0,stroke=1)
        c.restoreState()

    y = 9.5*inch
    x = 72
    def drawString(x,y, s,fontName,fontSize,cs=1,anchor='start'):
        c.setFont(fontName, fontSize)
        y -= 12
        w = c.stringWidth(s)
        func = c.drawString if anchor=='start' else c.drawRightString if anchor=='end' else c.drawCentredString
        func(x, y, s)
        drawBox(x,y,w,10,anchor=anchor)
        y -= 12
        func(x, y, s,charSpace=cs)
        n = len(s) - 1
        drawBox(x,y,w+n,10,anchor=anchor)
        y -= 12
        return x,y

    x,y = drawString(x,y,u'Hello World','Helvetica',10)
    x,y = drawString(x,y,u'M','Helvetica',10)
    x,y = drawString(x,y,u'MM','Helvetica',10)
    x,y = drawString(x,y,u'M M','Helvetica',10)
    x,y = drawString(x,y,u'M    M','Helvetica',10)

    x = 3*72
    y = 9.5*inch
    x,y = drawString(x,y,u'Hello World','Helvetica',10,anchor='end')
    x,y = drawString(x,y,u'M','Helvetica',10,anchor='end')
    x,y = drawString(x,y,u'MM','Helvetica',10,anchor='end')
    x,y = drawString(x,y,u'M M','Helvetica',10,anchor='end')
    x,y = drawString(x,y,u'M    M','Helvetica',10,anchor='end')

    c.showPage()

#########################################################################
#
#  Page 6 - coord transforms
#
#########################################################################
    framePage(c, "Coordinate Transforms")
    c.setFont('Times-Roman', 12)
    t = c.beginText(inch, 10 * inch)
    t.textLines("""This shows coordinate transformations.  We draw a set of axes,
    moving down the page and transforming space before each one.
    You can use saveState() and restoreState() to unroll transformations.
    Note that functions which track the text cursor give the cursor position
    in the current coordinate system; so if you set up a 6 inch high frame
    2 inches down the page to draw text in, and move the origin to its top
    left, you should stop writing text after six inches and not eight.""")
    c.drawText(t)

    drawAxes(c, "0.  at origin")
    c.addLiteral('%about to translate space')
    c.translate(2*inch, 7 * inch)
    drawAxes(c, '1. translate near top of page')

    c.saveState()
    c.translate(1*inch, -2 * inch)
    drawAxes(c, '2. down 2 inches, across 1')
    c.restoreState()

    c.saveState()
    c.translate(0, -3 * inch)
    c.scale(2, -1)
    drawAxes(c, '3. down 3 from top, scale (2, -1)')
    c.restoreState()

    c.saveState()
    c.translate(0, -5 * inch)
    c.rotate(-30)
    drawAxes(c, "4. down 5, rotate 30' anticlockwise")
    c.restoreState()

    c.saveState()
    c.translate(3 * inch, -5 * inch)
    c.skew(0,30)
    drawAxes(c, "5. down 5, 3 across, skew beta 30")
    c.restoreState()

    c.showPage()

#########################################################################
#
#  Page 7 - clipping
#
#########################################################################
    framePage(c, "Clipping")
    c.setFont('Times-Roman', 12)
    t = c.beginText(inch, 10 * inch)
    t.textLines("""This shows clipping at work. We draw a chequerboard of rectangles
    into a path object, and clip it.  This then forms a mask which limits the region of
    the page on which one can draw.  This paragraph was drawn after setting the clipping
    path, and so you should only see part of the text.""")
    c.drawText(t)

    c.saveState()
    #c.setFillColorRGB(0,0,1)
    p = c.beginPath()
    #make a chesboard effect, 1 cm squares
    for i in range(14):
        x0 = (3 + i) * cm
        for j in range(7):
            y0 = (16 + j) * cm
            p.rect(x0, y0, 0.85*cm, 0.85*cm)
    c.addLiteral('%Begin clip path')
    c.clipPath(p)
    c.addLiteral('%End clip path')
    t = c.beginText(3 * cm, 22.5 * cm)
    t.textLines("""This shows clipping at work.  We draw a chequerboard of rectangles
    into a path object, and clip it.  This then forms a mask which limits the region of
    the page on which one can draw.  This paragraph was drawn after setting the clipping
    path, and so you should only see part of the text.
        This shows clipping at work.  We draw a chequerboard of rectangles
    into a path object, and clip it.  This then forms a mask which limits the region of
    the page on which one can draw.  This paragraph was drawn after setting the clipping
    path, and so you should only see part of the text.
        This shows clipping at work.  We draw a chequerboard of rectangles
    into a path object, and clip it.  This then forms a mask which limits the region of
    the page on which one can draw.  This paragraph was drawn after setting the clipping
    path, and so you should only see part of the text.""")
    c.drawText(t)

    c.restoreState()

    t = c.beginText(inch, 5 * inch)
    t.textLines("""You can also use text as an outline for clipping with the text render mode.
        The API is not particularly clean on this and one has to follow the right sequence;
        this can be optimized shortly.""")
    c.drawText(t)

    #first the outline
    c.saveState()
    t = c.beginText(inch, 3.0 * inch)
    t.setFont('Helvetica-BoldOblique',108)
    t.setTextRenderMode(5)  #stroke and add to path
    t.textLine('Python!')
    t.setTextRenderMode(0)
    c.drawText(t)    #this will make a clipping mask

    #now some small stuff which wil be drawn into the current clip mask
    t = c.beginText(inch, 4 * inch)
    t.setFont('Times-Roman',6)
    t.textLines((('spam ' * 40) + '\n') * 15)
    c.drawText(t)

    #now reset canvas to get rid of the clipping mask
    c.restoreState()

    c.showPage()


#########################################################################
#
#  Page 8 - images
#
#########################################################################
    framePage(c, "Images")
    c.setFont('Times-Roman', 12)
    t = c.beginText(inch, 10 * inch)
    if not haveImages:
        c.drawString(inch, 11*inch,
                     "Python or Java Imaging Library not found! Below you see rectangles instead of images.")

    t.textLines("""PDFgen uses the Python Imaging Library (or, under Jython, java.awt.image and javax.imageio)
        to process a very wide variety of image formats.
        This page shows image capabilities.  If I've done things right, the bitmap should have
        its bottom left corner aligned with the crosshairs.
        There are two methods for drawing images.  The recommended use is to call drawImage.
        This produces the smallest PDFs and the fastest generation times as each image's binary data is
        only embedded once in the file.  Also you can use advanced features like transparency masks.
        You can also use drawInlineImage, which puts images in the page stream directly.
        This is slightly faster for Acrobat to render or for very small images, but wastes
        space if you use images more than once.""")

    c.drawText(t)

    if haveImages:
        from reportlab.lib.testutils import testsFolder
        gif = os.path.join(testsFolder,'pythonpowered.gif')
        c.drawInlineImage(gif,2*inch, 7*inch)
        c.drawInlineImage(os.path.join(testsFolder,'pythonpowered-gs.gif'),4*inch, 7.5*inch)
        tif = os.path.join(testsFolder,'test-cross.tiff')   #example of a mode '1' image
        c.drawInlineImage(tif,1*inch, 1*inch)
        from reportlab.lib.utils import Image as PilImage
        if PilImage:
            c.drawInlineImage(PilImage.open(tif),1.25*inch, 1*inch)
    else:
        c.rect(2*inch, 7*inch, 110, 44)
        c.rect(4*inch, 7*inch, 110, 44)

    c.line(1.5*inch, 7*inch, 4*inch, 7*inch)
    c.line(2*inch, 6.5*inch, 2*inch, 8*inch)
    c.drawString(4.5 * inch, 7.25*inch, 'inline image drawn at natural size')

    if haveImages:
        c.drawInlineImage(gif,2*inch, 5*inch, inch, inch)
    else:
        c.rect(2*inch, 5*inch, inch, inch)

    c.line(1.5*inch, 5*inch, 4*inch, 5*inch)
    c.line(2*inch, 4.5*inch, 2*inch, 6*inch)
    c.drawString(4.5 * inch, 5.25*inch, 'inline image distorted to fit box')

    c.drawString(1.5 * inch, 4*inch, 'Image XObjects can be defined once in the file and drawn many times.')
    c.drawString(1.5 * inch, 3.75*inch, 'This results in faster generation and much smaller files.')

    for i in range(5):
        if haveImages:
            (w, h) = c.drawImage(gif, (1.5 + i)*inch, 3*inch)
        else:
            (w, h) = (144, 10)
            c.rect((1.5 + i)*inch, 3*inch, 110, 44)

    myMask = [254,255,222,223,0,1]
    c.drawString(1.5 * inch, 2.5*inch, "The optional 'mask' parameter lets you define transparent colors. We used a color picker")
    c.drawString(1.5 * inch, 2.3*inch, "to determine that the yellow in the image above is RGB=(225,223,0).  We then define a mask")
    c.drawString(1.5 * inch, 2.1*inch, "spanning these RGB values:  %s.  The background vanishes!!" % myMask)
    c.drawString(2.5*inch, 1.2*inch, 'This would normally be obscured')
    if haveImages:
        c.drawImage(gif, 1*inch, 1.2*inch, w, h, mask=myMask)
        c.drawImage(gif, 3*inch, 1.2*inch, w, h, mask='auto')
        c.drawImage(os.path.join(testsFolder,'test-rgba.png'),5*inch,1.2*inch,width=10,height=10,mask='auto')
        c.drawImage(os.path.join(testsFolder,'test-indexed.png'),5.5*inch,1.2*inch,width=10,height=10,mask='auto')
    else:
        c.rect(1*inch, 1.2*inch, w, h)
        c.rect(3*inch, 1.2*inch, w, h)

    c.showPage()
    c.drawString(1*inch, 10.25*inch, "For rgba type images we can use the alpha channel if we set mask='auto'.")
    c.drawString(1*inch, 10.25*inch-14.4, "The first image is solid red with variable alpha.")
    c.drawString(1*inch, 10.25*inch-2*14.4, "The second image is white alpha=0% to purple=100%")


    for i in range(8):
        c.drawString(1*inch,8*inch+i*14.4,"mask=None   Line %d"%i)
        c.drawString(3*inch,8*inch+i*14.4,"mask='auto' Line %d"%i)
        c.drawString(1*inch,6*inch+i*14.4,"mask=None   Line %d"%i)
        c.drawString(3*inch,6*inch+i*14.4,"mask='auto' Line %d"%i)
    w = 100
    h = 75
    c.rect(1*inch, 8+14.4*inch, w, h)
    c.rect(3*inch, 8+14.4*inch, w, h)
    c.rect(1*inch, 6+14.4*inch, w, h)
    c.rect(3*inch, 6+14.4*inch, w, h)
    if haveImages:
        from reportlab.lib.testutils import testsFolder
        png = os.path.join(testsFolder,'solid_red_alpha.png')
        c.drawImage(png, 1*inch, 8*inch+14.4, w, h, mask=None)
        c.drawImage(png, 3*inch, 8*inch+14.4, w, h, mask='auto')
        png = os.path.join(testsFolder,'alpha_test.png')
        c.drawImage(png, 1*inch, 6*inch+14.4, w, h, mask=None)
        c.drawImage(png, 3*inch, 6*inch+14.4, w, h, mask='auto')
    c.showPage()

    if haveImages:
        import shutil
        c.drawString(1*inch, 10.25*inch, 'This jpeg is actually a gif')
        jpg = outputfile('_i_am_actually_a_gif.jpg')
        shutil.copyfile(gif,jpg)
        c.drawImage(jpg, 1*inch, 9.25*inch, w, h, mask='auto')
        tjpg = os.path.join(os.path.dirname(os.path.dirname(gif)),'docs','images','lj8100.jpg')
        if os.path.isfile(tjpg):
            c.drawString(4*inch, 10.25*inch, 'This gif is actually a jpeg')
            tgif = outputfile(os.path.basename('_i_am_actually_a_jpeg.gif'))
            shutil.copyfile(tjpg,tgif)
            c.drawImage(tgif, 4*inch, 9.25*inch, w, h, mask='auto')

        c.drawString(inch, 9.0*inch, 'Image positioning tests with preserveAspectRatio')

        #preserveAspectRatio test
        c.drawString(inch, 8.8*inch, 'Both of these should appear within the boxes, vertically centered')

    
        x, y, w, h = inch, 6.75* inch, 2*inch, 2*inch
        c.rect(x, y, w, h)
        (w2, h2) = c.drawImage(gif,  #anchor southwest, drawImage
                    x, y, width=w, height=h, 
                    preserveAspectRatio=True, 
                    anchor='c'
                    )
                    
        #now test drawInlineImage across the page            
        x = 5 * inch
        c.rect(x, y, w, h)
        (w2, h2) = c.drawInlineImage(gif,  #anchor southwest, drawInlineImage
                    x, y, width=w, height=h, 
                    preserveAspectRatio=True,
                    anchor='c'
                    )
                    
        c.drawString(inch, 5.75*inch, 
        'anchored by respective corners - use both a wide and a tall one as tests')
        x = 0.25 * inch
        for anchor in ['nw','n','ne','w','c','e','sw','s','se']:
            x += 0.75*inch
            c.rect(x, 5*inch, 0.6*inch, 0.6*inch)
            c.drawImage(
                    gif, x, 5*inch, 
                    width=0.6*inch, height=0.6*inch, 
                    preserveAspectRatio=True,
                    anchor=anchor
                    )
            c.drawString(x, 4.9*inch, anchor)

        x = 0.25 * inch
        tall_red = os.path.join(testsFolder,'tall_red.png')
        for anchor in ['nw','n','ne','w','c','e','sw','s','se']:
            x += 0.75*inch
            c.rect(x, 4*inch, 0.6*inch, 0.6*inch)
            c.drawImage(
                    tall_red, x, 4*inch, 
                    width=0.6*inch, height=0.6*inch, 
                    preserveAspectRatio=True,
                    anchor=anchor
                    )
            c.drawString(x, 3.9*inch, anchor)



        c.showPage()


#########################################################################
#
#  Page 9 - Forms and simple links
#
#########################################################################
    framePage(c, "Forms and Links")
    c.setFont('Times-Roman', 12)
    t = c.beginText(inch, 10 * inch)
    t.textLines("""Forms are sequences of text or graphics operations
      which are stored only once in a PDF file and used as many times
      as desired.  The blue logo bar to the left is an example of a form
      in this document.  See the function framePageForm in this demo script
      for an example of how to use canvas.beginForm(name, ...) ... canvas.endForm().

      Documents can also contain cross references where (for example) a rectangle
      on a page may be bound to a position on another page.  If the user clicks
      on the rectangle the PDF viewer moves to the bound position on the other
      page.  There are many other types of annotations and links supported by PDF.

      For example, there is a bookmark to each page in this document and below
      is a browsable index that jumps to those pages. In addition we show two
      URL hyperlinks; for these, you specify a rectangle but must draw the contents
      or any surrounding rectangle yourself.
      """)
    c.drawText(t)

    nentries = len(titlelist)
    xmargin = 3*inch
    xmax = 7*inch
    ystart = 6.54*inch
    ydelta = 0.4*inch
    for i in range(nentries):
        yposition = ystart - i*ydelta
        title = titlelist[i]
        c.drawString(xmargin, yposition, title)
        c.linkAbsolute(title, title, (xmargin-ydelta/4, yposition-ydelta/4, xmax, yposition+ydelta/2))

    # test URLs
    r1 = (inch, 3*inch, 5*inch, 3.25*inch) # this is x1,y1,x2,y2
    c.linkURL('http://www.reportlab.com/', r1, thickness=1, color=green)
    c.drawString(inch+3, 3*inch+6, 'Hyperlink to www.reportlab.com, with green border')

    r1 = (inch, 2.5*inch, 5*inch, 2.75*inch) # this is x1,y1,x2,y2
    c.linkURL('mailto:reportlab-users@egroups.com', r1) #, border=0)
    c.drawString(inch+3, 2.5*inch+6, 'mailto: hyperlink, without border')

    r1 = (inch, 2*inch, 5*inch, 2.25*inch) # this is x1,y1,x2,y2
    c.linkURL('http://www.reportlab.com/', r1,
                      thickness=2,
                      dashArray=[2,4],
                      color=colors.magenta)
    c.drawString(inch+3, 2*inch+6, 'Hyperlink with custom border style')

    xpdf = fileName2FSEnc(outputfile('test_hello.pdf').replace('\\','/'))
    link = 'Hard link to %s, with red border' % xpdf
    r1 = (inch, 1.5*inch, inch+2*3+c.stringWidth(link,c._fontname, c._fontsize), 1.75*inch) # this is x1,y1,x2,y2
    c.linkURL(xpdf, r1, thickness=1, color=red, kind='GoToR')
    c.drawString(inch+3, 1.5*inch+6, link )
    c.showPage()

    ############# colour gradients
    title = 'Gradients code contributed by Peter Johnson <johnson.peter@gmail.com>'
    c.drawString(1*inch,10.8*inch,title)
    c.addOutlineEntry(title+" section", title, level=0, closed=True)
    c.bookmarkHorizontalAbsolute(title, 10.8*inch)

    c.saveState()
    p = c.beginPath()
    p.moveTo(1*inch,2*inch)
    p.lineTo(1.5*inch,2.5*inch)
    p.curveTo(2*inch,3*inch,3.0*inch,3*inch,4*inch,2.9*inch)
    p.lineTo(5.5*inch,2.1*inch)
    p.close()
    c.clipPath(p)

    # Draw a linear gradient from (0, 2*inch) to (5*inch, 3*inch), from orange to white.
    # The gradient will extend past the endpoints (so you probably want a clip path in place)
    c.linearGradient(1*inch, 2*inch, 6*inch, 3*inch, (red, blue))
    c.restoreState()

    # Draw a radial gradient with a radius of 3 inches.
    # The color starts orange and stays orange until 20% of the radius,
    # then fades to white at 80%, and ends up green at 3 inches from the center.
    # Since extend is false, the gradient stops drawing at the edge of the circle.
    c.radialGradient(4*inch, 6*inch, 3*inch, (red, green, blue), (0.2, 0.8, 1.0), extend=False)
    c.showPage()

    ### now do stuff for the outline
    #for x in outlinenametree: print x
    #stop
    #c.setOutlineNames0(*outlinenametree)
    return c


def run(filename):
    c = makeDocument(filename)
    c.setAuthor('R\xfcp\xe9rt B\xe8\xe4r')
    c.setTitle('R\xc3\xbcp\xc3\xa9rt B\xc3\xa8\xc3\xa4r\'s Book')
    c.setCreator('Some Creator')
    c.setSubject('Some Subject')
    c.save()
    c = makeDocument(filename)
    import os
    f = os.path.splitext(filename)
    f = open('%sm%s' % (f[0],f[1]),'wb')
    f.write(c.getpdfdata())
    f.close()

def pageShapes(c):
    """Demonstrates the basic lines and shapes"""

    c.showPage()
    framePage(c, "Basic line and shape routines""")
    c.setTextOrigin(inch, 10 * inch)
    c.setFont('Times-Roman', 12)
    c.textLines("""pdfgen provides some basic routines for drawing straight and curved lines,
    and also for solid shapes.""")

    y = 9 * inch
    d = DocBlock()
    d.comment1 = 'Lesson one'
    d.code = "canvas.textOut('hello, world')"
    print(d.code)

    d.comment2 = 'Lesson two'

    d.draw(c, inch, 9 * inch)


class PdfgenTestCase(unittest.TestCase):
    "Make documents with lots of Pdfgen features"

    def test0(self):
        "Make a PDFgen document with most graphics features"
        run(outputfile('test_pdfgen_general.pdf'))

    def test1(self):
        c=canvas.Canvas(outputfile('test_pdfgen_obscure.pdf'))
        c.setViewerPreference('PrintScaling','None')
        c.setViewerPreference('HideToolbar','true')
        c.setViewerPreference('HideMenubar','true')
        c.addPageLabel(0, prefix="Front")
        c.addPageLabel(1, style='ROMAN_LOWER', start=2)
        c.addPageLabel(8, style='ARABIC')
        # (These are fixes for missing pages)
        c.addPageLabel(11, style='ARABIC',start=6)
        c.addPageLabel(17, style='ARABIC', start=14)
        c.addPageLabel(21, style='ARABIC', start=22)
        #check that duplicate page start will not cause sort error in python 3.x
        c.addPageLabel(98, style='ROMAN_LOWER', start=99, prefix='r')
        c.addPageLabel(98, style='ARABIC', start=99, prefix='A')
        c.addPageLabel(99, style='LETTERS_UPPER')
        c.addPageLabel(102, prefix="Back",start=1)

        # Make some (mostly) empty pages
        for i in range(113):
            c.drawString(100, 100, 'This is page '+str(i))
            c.showPage()

        # Output the PDF
        c.save()    

    def test2(self):
        c=canvas.Canvas('test_pdfgen_autocropmarks.pdf',cropMarks=True)
        c.saveState()
        c.setStrokeColor((1,0,0))
        c.rect(0,0,c._pagesize[0],c._pagesize[1],stroke=1)
        c.restoreState()
        c.drawString(72,c._pagesize[1]-72,'Auto Crop Marks')
        c.showPage()
        c.saveState()
        c.setStrokeColor((1,0,0))
        c.rect(0,0,c._pagesize[0],c._pagesize[1],stroke=1)
        c.restoreState()
        c.drawString(72,c._pagesize[1]-72,'Auto Crop Marks Another Page')
        c.showPage()
        c.save()

    def test3(self):
        '''some special properties'''
        palette = [
                    colors.CMYKColorSep(0.6,0.34,0,0.1,spotName='625C',density=1),
                    colors.CMYKColorSep(0.13,0.51,0.87,0.48,spotName='464c',density=1),
                    ]
        canv = canvas.Canvas(   'test_pdfgen_general_spots.pdf',
                        pagesize=(346,102),
                        )

        canv.setLineWidth(1)
        canv.setStrokeColor(colors.CMYKColor(0,0,0,1))
        x=10
        y=10
        for c in palette:
            c.density = 1.0
            canv.setFillColor(c)
            canv.setFont('Helvetica',20)
            canv.drawString(x,80,'This is %s' % c.spotName)
            canv.setFont('Helvetica',6)
            canv.rect(x,y,50,50,fill=1)
            canv.setFillColor(c.clone(density=0.5))
            canv.rect(x+55,y,20,20,fill=1)
            canv.setFillColor(colors.CMYKColor(0,0,1,0))
            canv.rect(x+80,y,30,30,fill=1)
            canv.rect(x+120,y,30,30,fill=1)
            alpha = c is palette[0] and 1 or 0.5
            op = c is palette[0] and True or False
            canv.setFillAlpha(alpha)
            canv.setFillColor(colors.CMYKColor(1,0,0,0))
            canv.drawString(x+80+1,y+3,'OP=%d' % int(False))
            canv.drawString(x+80+1,y+23,'Alpha=%.1f' % alpha)
            canv.rect(x+90,y+10,10,10,fill=1)
            canv.setFillOverprint(op)
            canv.drawString(x+120+1,y+3,'OP=%d' % int(op))
            canv.drawString(x+120+1,y+23,'Alpha=%.1f' % alpha)
            canv.rect(x+130,y+10,10,10,fill=1)
            canv.setFillAlpha(1)
            canv.setFillOverprint(False)
            x += canv._pagesize[0]*0.5
        canv.showPage()
        canv.save()

    def test4(self):
        sc = colors.CMYKColorSep
        rgb = ['red','green','blue', 'black']
        cmykb = [(0,0,0,1)]
        cmyk = [(1,0,0,0),(0,1,0,0),(0,0,1,0)]+cmykb
        seps = [sc(1,1,0,0,spotName='sep0'),sc(0,1,1,0,spotName='sep1')]
        sepb = [sc(0,0,0,1,spotName='sepb')]
        #these should all work
        trySomeColors(rgb+cmyk+seps)
        trySomeColors(rgb,'rgb')
        trySomeColors(cmyk,'cmyk')
        trySomeColors(seps+cmyk,'sep_cmyk')
        trySomeColors(seps+sepb,'sep')  #we need a fake black for now
        trySomeColors(seps+['black']+cmykb,'sep_black')
        self.assertRaises(ValueError,trySomeColors,rgb+cmyk+seps,'rgb')
        self.assertRaises(ValueError,trySomeColors,rgb+cmyk,'rgb')
        self.assertRaises(ValueError,trySomeColors,rgb+seps,'rgb')
        trySomeColors(rgb+sepb,'rgb')   #should work because blacks are convertible 
        trySomeColors(rgb+cmykb,'rgb')
        self.assertRaises(ValueError,trySomeColors,cmyk+rgb+seps,'cmyk')
        trySomeColors(cmyk+['black']+seps,'cmyk')   #OK because black & seps are convertible

    def test5(self,uopw=None):
        from reportlab.lib.pagesizes import A4,LETTER
        if uopw:
            from reportlab.lib import pdfencrypt
            encrypt = pdfencrypt.StandardEncryption(uopw[0], uopw[1])
            encrypt.setAllPermissions(0)
            encrypt.canPrint = 1
            canv = canvas.Canvas(outputfile('test_pdfgen_general_page_sizes_encrypted.pdf'),pagesize=A4)
            canv._doc.encrypt = encrypt
        else:
            canv = canvas.Canvas(outputfile('test_pdfgen_general_page_sizes.pdf'),pagesize=A4)
        canv.setFont('Helvetica',10)
        S = A4
        canv.drawString(0,S[1]-10,'Top Left=(%s,%s) Page Size=%s x %s' % (0,S[1],S[0],S[1]))
        canv.drawCentredString(0.5*S[0],0.5*S[1],'Center =(%s,%s) Page Size=%s x %s' % (0.5*S[0],0.5*S[1],S[0],S[1]))
        canv.drawRightString(S[0],2,'Bottom Right=(%s,%s) Page Size=%s x %s' % (S[0],0,S[0],S[1]))
        canv.showPage()
        S = LETTER
        canv.setPageSize(S)
        canv.drawString(0,S[1]-10,'Top Left=(%s,%s) Page Size=%s x %s' % (0,S[1],S[0],S[1]))
        canv.drawCentredString(0.5*S[0],0.5*S[1],'Center =(%s,%s) Page Size=%s x %s' % (0.5*S[0],0.5*S[1],S[0],S[1]))
        canv.drawRightString(S[0],2,'Bottom Right=(%s,%s) Page Size=%s x %s' % (S[0],0,S[0],S[1]))
        canv.showPage()
        S = A4
        canv.setPageSize(S)
        canv.setPageRotation(180)
        canv.drawString(0,S[1]-10,'Top Left=(%s,%s) Page Size=%s x %s' % (0,S[1],S[0],S[1]))
        canv.drawCentredString(0.5*S[0],0.5*S[1],'Center =(%s,%s) Page Size=%s x %s' % (0.5*S[0],0.5*S[1],S[0],S[1]))
        canv.drawRightString(S[0],2,'Bottom Right=(%s,%s) Page Size=%s x %s' % (S[0],0,S[0],S[1]))
        canv.showPage()
        S = A4[1],A4[0]
        canv.setPageSize(S)
        canv.setPageRotation(0)
        canv.drawString(0,S[1]-30,'Top Left=(%s,%s) Page Size=%s x %s' % (0,S[1],S[0],S[1]))
        canv.drawCentredString(0.5*S[0],0.5*S[1],'Center =(%s,%s) Page Size=%s x %s' % (0.5*S[0],0.5*S[1],S[0],S[1]))
        canv.drawRightString(S[0],32,'Bottom Right=(%s,%s) Page Size=%s x %s' % (S[0],0,S[0],S[1]))
        canv.showPage()
        canv.save()

    def test6(self):
        self.test5(('User','Password'))

    def testMultipleSavesOk(self):
        c=canvas.Canvas(outputfile('test_pdfgen_savetwice.pdf'))
        c.drawString(100, 700, 'Hello. This was saved twice')
        c.showPage()

        # Output the PDF
        stuff = c.getpdfdata()
        #multiple calls to save / getpdfdata used to cause errors
        stuff = c.getpdfdata()    


def trySomeColors(C,enforceColorSpace=None):
    from reportlab.lib.utils import getBytesIO
    out=getBytesIO()
    canv = canvas.Canvas(out,enforceColorSpace=enforceColorSpace)
    canv.setFont('Helvetica',10)
    x = 0
    y = 0
    w,h = canv._pagesize
    for c in C:
        if y+10>h:
            y = 0
            x += 10
        canv.setFillColor(c)
        canv.rect(x,y,10,10,fill=1,stroke=0)
        y += 10
    canv.showPage()
    canv.save()

def makeSuite():
    return makeSuiteForClasses(PdfgenTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
