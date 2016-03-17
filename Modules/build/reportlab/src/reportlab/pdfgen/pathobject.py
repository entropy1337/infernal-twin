#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/pdfgen/pathobject.py
__version__=''' $Id$ '''
__doc__="""
PDFPathObject is an efficient way to draw paths on a Canvas. Do not
instantiate directly, obtain one from the Canvas instead.

Progress Reports:
8.83, 2000-01-13, gmcm: created from pdfgen.py

"""

from reportlab.pdfgen import pdfgeom
from reportlab.lib.rl_accel import fp_str


class PDFPathObject:
    """Represents a graphic path.  There are certain 'modes' to PDF
    drawing, and making a separate object to expose Path operations
    ensures they are completed with no run-time overhead.  Ask
    the Canvas for a PDFPath with getNewPathObject(); moveto/lineto/
    curveto wherever you want; add whole shapes; and then add it back
    into the canvas with one of the relevant operators.

    Path objects are probably not long, so we pack onto one line

    the code argument allows a canvas to get the operatiosn appended directly so
    avoiding the final getCode
    """
    def __init__(self,code=None):
        self._code = (code,[])[code is None]
        self._code_append = self._init_code_append

    def _init_code_append(self,c):
        assert c.endswith(' m') or c.endswith(' re'), 'path must start with a moveto or rect'
        code_append = self._code.append
        code_append('n')
        code_append(c)
        self._code_append = code_append

    def getCode(self):
        "pack onto one line; used internally"
        return ' '.join(self._code)

    def moveTo(self, x, y):
        self._code_append('%s m' % fp_str(x,y))

    def lineTo(self, x, y):
        self._code_append('%s l' % fp_str(x,y))

    def curveTo(self, x1, y1, x2, y2, x3, y3):
        self._code_append('%s c' % fp_str(x1, y1, x2, y2, x3, y3))

    def arc(self, x1,y1, x2,y2, startAng=0, extent=90):
        """Contributed to piddlePDF by Robert Kern, 28/7/99.
        Draw a partial ellipse inscribed within the rectangle x1,y1,x2,y2,
        starting at startAng degrees and covering extent degrees.   Angles
        start with 0 to the right (+x) and increase counter-clockwise.
        These should have x1<x2 and y1<y2.

        The algorithm is an elliptical generalization of the formulae in
        Jim Fitzsimmon's TeX tutorial <URL: http://www.tinaja.com/bezarc1.pdf>."""

        self._curves(pdfgeom.bezierArc(x1,y1, x2,y2, startAng, extent))

    def arcTo(self, x1,y1, x2,y2, startAng=0, extent=90):
        """Like arc, but draws a line from the current point to
        the start if the start is not the current point."""
        self._curves(pdfgeom.bezierArc(x1,y1, x2,y2, startAng, extent),'lineTo')

    def rect(self, x, y, width, height):
        """Adds a rectangle to the path"""
        self._code_append('%s re' % fp_str((x, y, width, height)))

    def ellipse(self, x, y, width, height):
        """adds an ellipse to the path"""
        self._curves(pdfgeom.bezierArc(x, y, x + width,y + height, 0, 360))

    def _curves(self,curves,initial='moveTo'):
        getattr(self,initial)(*curves[0][:2])
        for curve in curves:
            self.curveTo(*curve[2:])

    def circle(self, x_cen, y_cen, r):
        """adds a circle to the path"""
        x1 = x_cen - r
        y1 = y_cen - r
        width = height = 2*r
        self.ellipse(x1, y1, width, height)

    def roundRect(self, x, y, width, height, radius):
        """Draws a rectangle with rounded corners. The corners are
        approximately quadrants of a circle, with the given radius."""
        #use a precomputed set of factors for the bezier approximation
        #to a circle. There are six relevant points on the x axis and y axis.
        #sketch them and it should all make sense!
        t = 0.4472 * radius

        x0 = x
        x1 = x0 + t
        x2 = x0 + radius
        x3 = x0 + width - radius
        x4 = x0 + width - t
        x5 = x0 + width

        y0 = y
        y1 = y0 + t
        y2 = y0 + radius
        y3 = y0 + height - radius
        y4 = y0 + height - t
        y5 = y0 + height

        self.moveTo(x2, y0)
        self.lineTo(x3, y0) #bottom row
        self.curveTo(x4, y0, x5, y1, x5, y2) #bottom right
        self.lineTo(x5, y3) #right edge
        self.curveTo(x5, y4, x4, y5, x3, y5) #top right
        self.lineTo(x2, y5) #top row
        self.curveTo(x1, y5, x0, y4, x0, y3) #top left
        self.lineTo(x0, y2) #left edge
        self.curveTo(x0, y1, x1, y0, x2, y0) #bottom left
        self.close()

    def close(self):
        "draws a line back to where it started"
        self._code_append('h')
