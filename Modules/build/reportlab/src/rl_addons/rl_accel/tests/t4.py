from reportlab.pdfbase.pdfmetrics import getFont, registerFont
from reportlab.pdfbase.ttfonts import TTFont
import time
from sys import getrefcount
registerFont(TTFont("Vera", "Vera.ttf"))
font = getFont('Vera')
_py_stringWidth = font._py_stringWidth
stringWidth = font.stringWidth
#assert stringWidth!=_py_stringWidth
#print "font=%s(%d) widths=%s(%d)" % (
#       hex(id(font)), getrefcount(font),
#       hex(id(font.widths)), getrefcount(font.widths),
#       )

utext = 'This is the end of the \xce\x91\xce\xb2 world.'.decode('utf8')
fontSize = 12
print(stringWidth(utext,fontSize))
print(_py_stringWidth(utext,fontSize))
print(hex(id(font)), getrefcount(font),hex(id(font.face)), getrefcount(font.face), hex(id(font.face.charWidths)), getrefcount(font.face.charWidths), hex(id(font.face.defaultWidth)), getrefcount(font.face.defaultWidth), hex(id(utext)), getrefcount(utext), hex(id(fontSize)), getrefcount(fontSize))

assert stringWidth(utext,fontSize)==_py_stringWidth(utext,fontSize)
def tim(N,msg,func,*args):
    t0 = time.time()
    for i in range(N):
        x = func(*args)
    t1 = time.time()
    return "%s N=%d t=%.3f\n%r" % (msg,N,t1-t0,x)

N=100000
print(tim(N,'_py_stringWidth',_py_stringWidth,utext,fontSize))
print(tim(N,'stringWidth',stringWidth,utext,fontSize))
utext1='ABCDEFG'
N=1000000
print(tim(N,'_py_stringWidth',_py_stringWidth,utext1,fontSize))
print(tim(N,'stringWidth',stringWidth,utext1,fontSize))
utext1='ABCDE\xce\xb2G'
print(tim(N,'_py_stringWidth',_py_stringWidth,utext1,fontSize))
print(tim(N,'stringWidth',stringWidth,utext1,fontSize))
print(hex(id(font)), getrefcount(font),hex(id(font.face)), getrefcount(font.face), hex(id(font.face.charWidths)), getrefcount(font.face.charWidths), hex(id(font.face.defaultWidth)), getrefcount(font.face.defaultWidth), hex(id(utext)), getrefcount(utext), hex(id(fontSize)), getrefcount(fontSize))
