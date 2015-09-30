from reportlab.pdfbase.pdfmetrics import getFont
import time
from sys import getrefcount
font = getFont('Times-Roman')
_py_stringWidth = font._py_stringWidth
stringWidth = font.stringWidth
assert stringWidth!=_py_stringWidth
#print "font=%s(%d) widths=%s(%d)" % (
#       hex(id(font)), getrefcount(font),
#       hex(id(font.widths)), getrefcount(font.widths),
#       )

utext = 'This is the end of the \xce\x91\xce\xb2 world. This is the end of the \xce\x91\xce\xb2 world jap=\xe3\x83\x9b\xe3\x83\x86. This is the end of the \xce\x91\xce\xb2 world. This is the end of the \xce\x91\xce\xb2 world jap=\xe3\x83\x9b\xe3\x83\x86'.decode('utf8')
print(stringWidth(utext,12))
print(_py_stringWidth(utext,12))
assert stringWidth(utext,12)==_py_stringWidth(utext,12)
def tim(N,msg,func,*args):
    t0 = time.time()
    for i in range(N):
        x = func(*args)
    t1 = time.time()
    return "%s N=%d t=%.3f\n%r" % (msg,N,t1-t0,x)

N=10000
print(tim(N,'_py_stringWidth',_py_stringWidth,utext,12))
print(tim(N,'stringWidth',stringWidth,utext,12))
utext='ABCDEFG'
N=100000
print(tim(N,'_py_stringWidth',_py_stringWidth,utext,12))
print(tim(N,'stringWidth',stringWidth,utext,12))
utext='ABCDEF\xce\xb2'
print(tim(N,'_py_stringWidth',_py_stringWidth,utext,12))
print(tim(N,'stringWidth',stringWidth,utext,12))
utext='ABCDE\xce\xb2G'
print(tim(N,'_py_stringWidth',_py_stringWidth,utext,12))
print(tim(N,'stringWidth',stringWidth,utext,12))
