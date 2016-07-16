#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__version__=''' $Id$ '''
__doc__='''Utility functions to position and resize boxes within boxes'''

def aspectRatioFix(preserve,anchor,x,y,width,height,imWidth,imHeight):
    """This function helps position an image within a box.

    It first normalizes for two cases:
    - if the width is None, it assumes imWidth
    - ditto for height
    - if width or height is negative, it adjusts x or y and makes them positive

    Given
    (a) the enclosing box (defined by x,y,width,height where x,y is the \
        lower left corner) which you wish to position the image in, and
    (b) the image size (imWidth, imHeight), and
    (c) the 'anchor point' as a point of the compass - n,s,e,w,ne,se etc \
        and c for centre,

    this should return the position at which the image should be drawn,
    as well as a scale factor indicating what scaling has happened.

    It returns the parameters which would be used to draw the image
    without any adjustments:

        x,y, width, height, scale

    used in canvas.drawImage and drawInlineImage
    """
    scale = 1.0
    if width is None:
        width = imWidth
    if height is None:
        height = imHeight
    if width<0:
        width = -width
        x -= width
    if height<0:
        height = -height
        y -= height
    if preserve:
        imWidth = abs(imWidth)
        imHeight = abs(imHeight)
        scale = min(width/float(imWidth),height/float(imHeight))
        owidth = width
        oheight = height
        width = scale*imWidth-1e-8
        height = scale*imHeight-1e-8
        if anchor not in ('nw','w','sw'):
            dx = owidth-width
            if anchor in ('n','c','s'):
                x += dx/2.
            else:
                x += dx
        if anchor not in ('sw','s','se'):
            dy = oheight-height
            if anchor in ('w','c','e'):
                y += dy/2.
            else:
                y += dy
    return x,y, width, height, scale
