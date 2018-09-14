from reportlab.pdfbase.pdfmetrics import _py_stringWidth
from _rl_accel import stringWidthU
import time
testCp1252 = 'copyright %s trademark %s registered %s ReportLab! Ol%s!' % (chr(169), chr(153),chr(174), chr(0xe9))
enc='cp1252'
assert stringWidthU('ABCDEF','Times-Roman',12)==_py_stringWidth('ABCDEF','Times-Roman',12)
assert stringWidthU(testCp1252,'Times-Roman',12,enc)==_py_stringWidth(testCp1252,'Times-Roman',12,enc)
def tim(N,msg,func,*args):
    t0 = time.time()
    for i in range(N):
        x = func(*args)
    t1 = time.time()
    return "%s N=%d t=%.3f\n%r" % (msg,N,t1-t0,x)

print(tim(1000000,'_py_stringWidth',_py_stringWidth,'ABCDEF','Times-Roman',12))
print(tim(1000000,'stringWidthU',stringWidthU,'ABCDEF','Times-Roman',12))
