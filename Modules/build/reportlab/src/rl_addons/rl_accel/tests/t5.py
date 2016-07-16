from reportlab.pdfbase.pdfmetrics import getFont, registerFont
from reportlab.pdfbase.ttfonts import TTFont
import time
from sys import getrefcount
registerFont(TTFont("Vera", "Vera.ttf"))
font = getFont('Vera')
_py_getCharWidth = font.face._py_getCharWidth
getCharWidth = font.face.getCharWidth
#assert stringWidth!=_py_stringWidth
#print "font=%s(%d) widths=%s(%d)" % (
#       hex(id(font)), getrefcount(font),
#       hex(id(font.widths)), getrefcount(font.widths),
#       )

print([getCharWidth(x) for x in (1,2,30000,32,65)])
print([_py_getCharWidth(x) for x in (1,2,30000,32,65)])
codep = 65
codep1 = 2
print(hex(id(font)), getrefcount(font),hex(id(font.face)), getrefcount(font.face), hex(id(font.face.charWidths)), getrefcount(font.face.charWidths), hex(id(font.face.defaultWidth)), getrefcount(font.face.defaultWidth), hex(id(codep)), getrefcount(codep), hex(id(codep1)), getrefcount(codep1))
print([getCharWidth(x) for x in (1,2,30000,32,65)]==[_py_getCharWidth(x) for x in (1,2,30000,32,65)])

def tim(N,msg,func,*args):
    t0 = time.time()
    for i in range(N):
        x = func(*args)
    t1 = time.time()
    return "%s N=%d t=%.3f\n%r" % (msg,N,t1-t0,x)

N=1000000
print(tim(N,'_py_getCharWidth',_py_getCharWidth,codep))
print(tim(N,'getCharWidth',getCharWidth,codep))
print(tim(N,'_py_getCharWidth',_py_getCharWidth,codep1))
print(tim(N,'getCharWidth',getCharWidth,codep1))
print(hex(id(font)), getrefcount(font),hex(id(font.face)), getrefcount(font.face), hex(id(font.face.charWidths)), getrefcount(font.face.charWidths), hex(id(font.face.defaultWidth)), getrefcount(font.face.defaultWidth), hex(id(codep)), getrefcount(codep), hex(id(codep1)), getrefcount(codep1))
