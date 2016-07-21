#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history TBC
#$Header$
__version__=''' $Id'''
__doc__="""Tests of intra-paragraph parsing behaviour in Platypus."""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, equalStrings
setOutDir(__name__)
from pprint import pprint as pp
import unittest
from reportlab.platypus import cleanBlockQuotedText
from reportlab.platypus.paraparser import ParaParser, ParaFrag
from reportlab.lib.colors import black

class ParaParserTestCase(unittest.TestCase):
    """Tests of data structures created by paragraph parser.  Esp. ability
    to accept unicode and preserve it"""

    def setUp(self):
        style=ParaFrag()
        style.fontName ='Times-Roman'
        style.fontSize = 12
        style.textColor = black
        style.bulletFontName = black
        style.bulletFontName = 'Times-Roman'
        style.bulletFontSize = 12
        style.bulletOffsetY = 3
        style.textTransform = None
        self.style = style

    def testPlain(self):
        txt = "Hello World"
        stuff = ParaParser().parse(txt, self.style)
        assert isinstance(stuff,tuple)
        assert len(stuff) == 3
        assert  stuff[1][0].text == 'Hello World'

    def testBold(self):
        txt = "Hello <b>Bold</b> World"
        fragList = ParaParser().parse(txt, self.style)[1]
        self.assertEquals([x.text for x in fragList], ['Hello ','Bold',' World'])
        self.assertEquals(fragList[1].fontName, 'Times-Bold')

    def testStrong(self):
        txt = "Hello <strong>Strong</strong> World"
        fragList = ParaParser().parse(txt, self.style)[1]
        self.assertEquals([x.text for x in fragList], ['Hello ','Strong',' World'])
        self.assertEquals(fragList[1].fontName, 'Times-Bold')

    def testItalic(self):
        txt = "Hello <i>Italic</i> World"
        fragList = ParaParser().parse(txt, self.style)[1]
        self.assertEquals([x.text for x in fragList], ['Hello ','Italic',' World'])
        self.assertEquals(fragList[1].fontName, 'Times-Italic')

    def testEm(self):
        txt = "Hello <em>Em</em> World"
        fragList = ParaParser().parse(txt, self.style)[1]
        self.assertEquals([x.text for x in fragList], ['Hello ','Em',' World'])
        self.assertEquals(fragList[1].fontName, 'Times-Italic')

    def testEntity(self):
        "Numeric entities should be unescaped by parser"
        txt = b"Hello &#169; copyright"
        fragList = ParaParser().parse(txt, self.style)[1]
        self.assertEquals([x.text for x in fragList], [u'Hello ', u'\xa9', u' copyright'])

    def testEscaped(self):
        "Escaped high-bit stuff should go straight through"
        txt = "Hello \xc2\xa9 copyright"
        fragList = ParaParser().parse(txt, self.style)[1]
        assert equalStrings(fragList[0].text,txt)

    def testPlainUnicode(self):
        "See if simple unicode goes through"
        txt = "Hello World"
        stuff = ParaParser().parse(txt, self.style)
        assert isinstance(stuff,tuple)
        assert len(stuff) == 3
        assert  stuff[1][0].text == 'Hello World'

    def testBoldUnicode(self):
        txt = "Hello <b>Bold</b> World"
        fragList = ParaParser().parse(txt, self.style)[1]
        self.assertEquals([x.text for x in fragList], ['Hello ','Bold',' World'])
        self.assertEquals(fragList[1].fontName, 'Times-Bold')

    def testEntityUnicode(self):
        "Numeric entities should be unescaped by parser"
        txt = "Hello &#169; copyright"
        fragList = ParaParser().parse(txt, self.style)[1]
        self.assertEquals([x.text for x in fragList], [u'Hello ', u'\xa9', u' copyright'])

    def testEscapedUnicode(self):
        "Escaped high-bit stuff should go straight through"
        txt = u"Hello \xa9 copyright"
        fragList = ParaParser().parse(txt, self.style)[1]
        assert fragList[0].text == txt

    def testBr(self):
        txt = "Hello <br/> World"
        fragList = ParaParser().parse(txt, self.style)[1]
        self.assertEquals([x.text for x in fragList], ['Hello ','',' World'])
        self.assertEquals(fragList[1].lineBreak, True)


    def testRejectsBadlyFormed(self):
        txt = "Hello <b>World"

        def parseIt(txt, style=self.style):
            fragList = ParaParser().parse(txt, self.style)[1]

        self.assertRaises(ValueError, parseIt, txt)
        

    #def testNakedAmpersands(self):
        #We no longer require this error to be raised when using html.parser
        # import pyRXPU
        # from reportlab.platypus.paragraph import Paragraph
        # def func():
        #     txt = "1 & 2"
        #     parser = ParaParser()
        #     parser.caseSensitive = True
        #     frags = ParaParser().parse(txt, self.style)[1]
        #     Paragraph(txt, self.style),
        # self.assertRaises(
        #         pyRXPU.error,
        #         func,
        #         )

def makeSuite():
    return makeSuiteForClasses(ParaParserTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
