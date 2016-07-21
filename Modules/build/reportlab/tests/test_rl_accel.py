__version__=''' $Id'''
__doc__='''basic tests.'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, printLocation
from reportlab.lib.utils import asBytes
setOutDir(__name__)

import unittest
def getFuncs(name):
    return (_c_funcs.get(name,None),'c'),(_py_funcs.get(name,None),'py')

def getrc(defns,depth=1):
    from sys import getrefcount, _getframe
    f = _getframe(depth)
    G0 = f.f_globals
    L = f.f_locals
    if L is not G0:
        LL = [L]
        while 1:
            f = f.f_back
            G = f.f_globals
            L = f.f_locals
            if G is not G0 or G is L: break
            LL.append(L)
        L = {}
        LL.reverse()
        for l in LL:
            L.update(l)
    else:
        L = L.copy()
    G0 = G0.copy()
    return ' '.join([str(getrefcount(eval(x,L,G0))-1) for x in defns.split()])

def checkrc(defns,rcv0):
    rcv1 = getrc(defns,2)
    return ' '.join(["%s %s-->%s" % (x,v,w) for x,v,w in zip(defns.split(),rcv0.split(),rcv1.split()) if v!=w])

class RlAccelTestCase(unittest.TestCase):

    def testFpStr(self):
        # should give siz decimal places if less than 1.
        # if more, give up to seven sig figs
        for func, kind in getFuncs('fp_str'):
            assert func(1,2,3)=='1 2 3', "%s fp_str(1,2,3)=='1 2 3' fails with value %s!" % (kind,ascii(func(1,2,3)))
            assert func(1) == '1', "%s fp_str(1) == '1' fails with value %s!" % (kind,ascii(func(1)))
            assert func(595.275574) == '595.2756', "%s fp_str(595.275574) == '595.2756' fails with value %s!" % (kind,ascii(func(595.25574)))
            assert func(59.5275574) == '59.52756', "%s fp_str(59.5275574) == '59.52756' fails with value %s!" % (kind,ascii(func(59.525574)))
            assert func(5.95275574) == '5.952756', "%s fp_str(5.95275574) == '5.952756' fails with value %s!" % (kind,ascii(func(5.9525574)))

    def testAsciiBase85Encode(self):
        for func, kind in getFuncs('asciiBase85Encode'):
            assert func('Dragan Andric')=='6ul^K@;[2RDIdd%@f~>',"%s asciiBase85Encode('Dragan Andric')=='6ul^K@;[2RDIdd%@f~>' fails with value %s!" % (
                    kind,ascii(func('Dragan Andric')))

    def testAsciiBase85Decode(self):
        for func, kind in getFuncs('asciiBase85Decode'):
            assert func('6ul^K@;[2RDIdd%@f~>')==b'Dragan Andric',"%s asciiBase85Decode('6ul^K@;[2RDIdd%@f~>')=='Dragan Andric' fails with value %s!" % (
                    kind,ascii(func('Dragan Andric')))

    def testAsciiBase85RoundTrip(self):
        plain = 'What is the average velocity of a sparrow?'
        eFuncs = getFuncs('asciiBase85Encode')
        for i in xrange(256):
            for j,(dfunc, kind) in enumerate(getFuncs('asciiBase85Decode')):
                efunc = eFuncs[j][0]
                encoded = efunc(plain)
                decoded = dfunc(encoded)
                assert decoded == asBytes(plain,'latin1'), "Round-trip AsciiBase85 failed for %s & %s\nplain=%s\nencoded=%s\ndecoded=%s" % (
                        ascii(efunc),ascii(dfunc), ascii(plain), ascii(encoded), ascii(decoded))
                if not j:
                    enc0 = encoded
                    dec0 = decoded
                else:
                    assert encoded==enc0, " Python & C encodings differ failed for %s & %s\nplain=%s\nencode0=%s\nencoded=%s\ndecode0=%sdecoded=%s" % (
                        ascii(efunc),ascii(dfunc), ascii(plain), ascii(enc0), ascii(encoded), ascii(dec0), ascii(decoded))
                    assert decoded==dec0, " Python & C decodings differ failed for %s & %s\nplain=%s\nencode0=%s\nencoded=%s\ndecode0=%sdecoded=%s" % (
                        ascii(efunc),ascii(dfunc), ascii(plain), ascii(enc0), ascii(encoded), ascii(dec0), ascii(decoded))
            plain += chr(i)

    def testEscapePDF(self):
        for func, kind in getFuncs('escapePDF'):
            assert func('(test)')=='\\(test\\)',"%s escapePDF('(test)')=='\\\\(test\\\\)' fails with value %s!" % (
                    kind,ascii(func('(test)')))

    def testCalcChecksum(self):
        for func, kind in getFuncs('calcChecksum'):
            assert func('test')==1952805748, "%s calcChecksum('test')==1952805748 fails with value %s!" % (
                    kind,ascii(func(rawBytes('test'))))

    def test_instanceStringWidth(self):
        from reportlab.pdfbase.pdfmetrics import registerFont, getFont, _fonts, unicode2T1
        from reportlab.pdfbase.ttfonts import TTFont
        ttfn = 'Vera'
        t1fn = 'Times-Roman'
        registerFont(TTFont(ttfn, "Vera.ttf"))
        ttf = getFont(ttfn)
        t1f = getFont(t1fn)
        testCp1252 = b'copyright \xa9 trademark \x99 registered \xae ReportLab! Ol\xe9!'
        enc='cp1252'
        senc = 'utf8'
        ts = b'ABCDEF\xce\x91\xce\xb2G'
        utext = b'ABCDEF\xce\x91\xce\xb2G'.decode(senc)
        fontSize = 12
        defns="ttfn t1fn ttf t1f testCp1252 enc senc ts utext fontSize ttf.face ttf.face.charWidths ttf.face.defaultWidth t1f.widths t1f.encName t1f.substitutionFonts _fonts"
        import sys
        F = []
        def tfunc(f,ts,fontSize,enc,funcs,i):
            w1 = funcs[i][0](f,ts,fontSize,enc)
            w2 = funcs[1][0](f,ts,fontSize,enc) #python version
            if abs(w1-w2)>=1e-10: F.append("stringWidth%s(%r,%r,%s,%r)-->%r != f._py_stringWidth(...)-->%r" % (fontType,f,ts,fontSize,enc,w1,w2))
        for font,fontType in ((t1f,'T1'),(ttf,'TTF')):
            funcs = getFuncs('instanceStringWidth'+fontType)
            for i,kind in enumerate(('c','py')):
                for j in (3,2,1,0): #we run several times to allow the refcounts to stabilize
                    if j: rcv = getrc(defns)
                    tfunc(font,testCp1252,fontSize,enc,funcs,i)
                    tfunc(font,ts,fontSize,senc,funcs,i)
                    tfunc(font,utext,fontSize,senc,funcs,i)
                    if not j:
                        rcc = checkrc(defns,rcv)
                        if rcc: F.append("%s %s refcount diffs (%s)" % (fontType,kind,rcc))
        assert not F,"instanceStringWidth failures\n\t%s" % '\n\t'.join(F)

    def test_unicode2T1(self):
        from reportlab.pdfbase.pdfmetrics import getFont, _fonts
        t1fn = 'Times-Roman'
        t1f = getFont(t1fn)
        enc = 'cp1252'
        senc = 'utf8'
        testCp1252 = b'copyright \xa9 trademark \x99 registered \xae ReportLab! Ol\xe9!'.decode(enc)
        utext = b'This is the end of the \xce\x91\xce\xb2 world. This is the end of the \xce\x91\xce\xb2 world jap=\xe3\x83\x9b\xe3\x83\x86. This is the end of the \xce\x91\xce\xb2 world. This is the end of the \xce\x91\xce\xb2 world jap=\xe3\x83\x9b\xe3\x83\x86'.decode('utf8')
        FUNCS = getFuncs('unicode2T1')
        def tfunc(f,ts,func,kind):
            w1 = func(ts,[f]+f.substitutionFonts)
            w2 = FUNCS[1][0](ts,[f]+f.substitutionFonts)
            assert w1==w2,"%s unicode2T1 %r != %r" % (kind,w1,w2)
        defns="t1fn t1f testCp1252 enc senc utext t1f.widths t1f.encName t1f.substitutionFonts _fonts"
        F = []
        for func,kind in FUNCS:
            rcv = getrc(defns)
            tfunc(t1f,testCp1252,func,kind)
            tfunc(t1f,utext,func,kind)
            rcc = checkrc(defns,rcv)
            if rcc: F.append("%s refcount diffs (%s)" % (kind,rcc))
        assert not F,"test_unicode2T1 failures\n\t%s" % '\n\t'.join(F)

    def test_sameFrag(self):
        class ABag:
            def __init__(self,**kwd):
                self.__dict__.update(kwd)
            def __str__(self):
                V=['%s=%r' % v for v in self.__dict__.items()]
                V.sort()
                return 'ABag(%s)' % ','.join(V)

        for func,kind in getFuncs('sameFrag'):
            if not func: continue
            a=ABag(fontName='Helvetica',fontSize=12, textColor="red", rise=0, underline=0, strike=0, link="aaaa")
            b=ABag(fontName='Helvetica',fontSize=12, textColor="red", rise=0, underline=0, strike=0, link="aaaa")
            for name in ("fontName", "fontSize", "textColor", "rise", "underline", "strike", "link"):
                old = getattr(a,name)
                assert func(a,b)==1, "%s sameFrag(%s,%s)!=1" % (kind,a,b)
                assert func(b,a)==1, "%s sameFrag(%s,%s)!=1" % (kind,b,a)
                setattr(a,name,None)
                assert func(a,b)==0, "%s sameFrag(%s,%s)!=0" % (kind,a,b)
                assert func(b,a)==0, "%s sameFrag(%s,%s)!=0" % (kind,b,a)
                delattr(a,name)
                assert func(a,b)==0, "%s sameFrag(%s,%s)!=0" % (kind,a,b)
                assert func(b,a)==0, "%s sameFrag(%s,%s)!=0" % (kind,b,a)
                delattr(b,name)
                assert func(a,b)==1, "%s sameFrag(%s,%s)!=1" % (kind,a,b)
                assert func(b,a)==1, "%s sameFrag(%s,%s)!=1" % (kind,b,a)
                setattr(a,name,old)
                setattr(b,name,old)

def makeSuite():
    # only run the tests if _rl_accel is present
    try:
        from reportlab.lib import _rl_accel, rl_accel
        Klass = RlAccelTestCase
        global _py_funcs, _c_funcs
        _c_funcs=rl_accel._c_funcs
        _py_funcs=rl_accel._py_funcs
    except:
        class Klass(unittest.TestCase):
            pass
    return makeSuiteForClasses(Klass)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
