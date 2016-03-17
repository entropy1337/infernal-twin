import time
from reportlab.pdfbase.pdfmetrics import _fonts, findFontAndRegister, _py_getFont
from _rl_accel import getFontU
from getrc import getrc, checkrc
import sys
#fn0 = 'Times-Bold'
#fn1 = 'Times-Roman'
N = 1000000
def tim(N,msg,func,*args):
    t0 = time.time()
    for i in range(N):
        x = func(*args)
    t1 = time.time()
    return "%s N=%d t=%.3f\n%r" % (msg,N,t1-t0,x)
fn0='Courier'
fn1='Helvetica'
font0=_py_getFont(fn0)
font1=_py_getFont(fn1)
getFontU(fn0)

defns = "font0 font1 fn0 fn1 _fonts"
rcv = getrc(defns)
for i in (0,1,2):
    for fn in fn0,fn1:
        print(tim(N,'getFontU',getFontU,fn))
        print(tim(N,'_py_getFont',_py_getFont,fn))
del fn
print("rc diffs=(%s)" % checkrc(defns,rcv))
