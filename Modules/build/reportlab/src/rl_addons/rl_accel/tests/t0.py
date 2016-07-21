import os, time, sys
from reportlab.pdfbase.pdfmetrics import _py_getFont, _py_unicode2T1
from _rl_accel import unicode2T1
from getrc import getrc, checkrc
utext = 'ABCDEF \xce\x91BCDEF\xce\x91'.decode('utf8')
utext = 'This is the end of the \xce\x91\xce\xb2 world. This is the end of the \xce\x91\xce\xb2 world jap=\xe3\x83\x9b\xe3\x83\x86. This is the end of the \xce\x91\xce\xb2 world. This is the end of the \xce\x91\xce\xb2 world jap=\xe3\x83\x9b\xe3\x83\x86'.decode('utf8')
fontName = 'Times-Roman'
fontSize=12
N = 30000
def tim(msg,func,*args):
    t0 = time.time()
    for i in range(N):
        x = func(*args)
    t1 = time.time()
    return "%s N=%d t=%.3f\n%r" % (msg,N,t1-t0,x)

#print tim('_py_stringWidth', _py_stringWidth, utext, fontName, fontSize)
#print tim('stringWidth2', stringWidth2, utext, fontName, fontSize)

font = _py_getFont(fontName)
assert unicode2T1(utext,[font]+font.substitutionFonts)==_py_unicode2T1(utext,[font]+font.substitutionFonts)
#print unicode2T1(u'ABCDEF',[font]+font.substitutionFonts)
#print _py_unicode2T1(u'ABCDEF',[font]+font.substitutionFonts)
defns = "font font.widths font.substitutionFonts font.encName fontName utext"
rcv = getrc(defns)
print(tim('unicode2T1',unicode2T1,utext,[font]+font.substitutionFonts))
print(tim('_py_unicode2T1',_py_unicode2T1,utext,[font]+font.substitutionFonts))
print("rc diffs=(%s)" % checkrc(defns,rcv))
