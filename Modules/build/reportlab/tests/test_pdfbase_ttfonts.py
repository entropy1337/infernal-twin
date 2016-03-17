
"""Test TrueType font subsetting & embedding code.

This test uses a sample font (Vera.ttf) taken from Bitstream which is called Vera
Serif Regular and is covered under the license in ../fonts/bitstream-vera-license.txt.
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation, NearTestCase
if __name__=='__main__':
    setOutDir(__name__)
import unittest
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfdoc import PDFDocument, PDFError
from reportlab.pdfbase.ttfonts import TTFont, TTFontFace, TTFontFile, TTFOpenFile, \
                                      TTFontParser, TTFontMaker, TTFError, \
                                      makeToUnicodeCMap, \
                                      FF_SYMBOLIC, FF_NONSYMBOLIC, \
                                      calcChecksum, add32
from reportlab import rl_config
from reportlab.lib.utils import getBytesIO, isPy3, uniChr, int2Byte

def utf8(code):
    "Convert a given UCS character index into UTF-8"
    return uniChr(code).encode('utf8')

def _simple_subset_generation(fn,npages,alter=0):
    c = Canvas(outputfile(fn))
    c.setFont('Helvetica', 30)
    c.drawString(100,700, 'Unicode TrueType Font Test %d pages' % npages)
    # Draw a table of Unicode characters
    for p in range(npages):
        for fontName in ('Vera','VeraBI'):
            c.setFont(fontName, 10)
            for i in range(32):
                for j in range(32):
                    ch = utf8(i * 32 + j+p*alter)
                    c.drawString(80 + j * 13 + int(j / 16.0) * 4, 600 - i * 13 - int(i / 8.0) * 8, ch)
        c.showPage()
    c.save()

class TTFontsTestCase(unittest.TestCase):
    "Make documents with TrueType fonts"

    def testTTF(self):
        "Test PDF generation with TrueType fonts"
        pdfmetrics.registerFont(TTFont("Vera", "Vera.ttf"))
        pdfmetrics.registerFont(TTFont("VeraBI", "VeraBI.ttf"))
        _simple_subset_generation('test_pdfbase_ttfonts1.pdf',1)
        _simple_subset_generation('test_pdfbase_ttfonts3.pdf',3)
        _simple_subset_generation('test_pdfbase_ttfonts35.pdf',3,5)

        # Do it twice with the same font object
        c = Canvas(outputfile('test_pdfbase_ttfontsadditional.pdf'))
        # Draw a table of Unicode characters
        c.setFont('Vera', 10)
        c.drawString(100, 700, b'Hello, ' + utf8(0xffee))
        c.save()


class TTFontFileTestCase(NearTestCase):
    "Tests TTFontFile, TTFontParser and TTFontMaker classes"

    def testFontFileFailures(self):
        "Tests TTFontFile constructor error checks"
        self.assertRaises(TTFError, TTFontFile, "nonexistent file")
        self.assertRaises(TTFError, TTFontFile, getBytesIO(b""))
        self.assertRaises(TTFError, TTFontFile, getBytesIO(b"invalid signature"))
        self.assertRaises(TTFError, TTFontFile, getBytesIO(b"OTTO - OpenType not supported yet"))
        self.assertRaises(TTFError, TTFontFile, getBytesIO(b"\0\1\0\0"))

    def testFontFileReads(self):
        "Tests TTFontParset.read_xxx"

        class FakeTTFontFile(TTFontParser):
            def __init__(self, data):
                self._ttf_data = data
                self._pos = 0

        ttf = FakeTTFontFile(b"\x81\x02\x03\x04" b"\x85\x06" b"ABCD" b"\x7F\xFF" b"\x80\x00" b"\xFF\xFF")
        self.assertEquals(ttf.read_ulong(), 0x81020304) # big-endian
        self.assertEquals(ttf._pos, 4)
        self.assertEquals(ttf.read_ushort(), 0x8506)
        self.assertEquals(ttf._pos, 6)
        self.assertEquals(ttf.read_tag(), 'ABCD')
        self.assertEquals(ttf._pos, 10)
        self.assertEquals(ttf.read_short(), 0x7FFF)
        self.assertEquals(ttf.read_short(), -0x8000)
        self.assertEquals(ttf.read_short(), -1)

    def testFontFile(self):
        "Tests TTFontFile and TTF parsing code"
        ttf = TTFontFile("Vera.ttf")
        self.assertEquals(ttf.name, b"BitstreamVeraSans-Roman")
        self.assertEquals(ttf.flags, FF_SYMBOLIC)
        self.assertEquals(ttf.italicAngle, 0.0)
        self.assertNear(ttf.ascent,759.765625)
        self.assertNear(ttf.descent,-240.234375)
        self.assertEquals(ttf.capHeight, 759.765625)
        self.assertNear(ttf.bbox, [-183.10546875, -235.83984375, 1287.109375, 928.22265625])
        self.assertEquals(ttf.stemV, 87)
        self.assertEquals(ttf.defaultWidth, 600.09765625)

    def testAdd32(self):
        "Test add32"
        self.assertEquals(add32(10, -6), 4)
        self.assertEquals(add32(6, -10), -4&0xFFFFFFFF)
        self.assertEquals(add32(0x80000000, -1), 0x7FFFFFFF)
        self.assertEquals(add32(0x7FFFFFFF, 1), 0x80000000)

    def testChecksum(self):
        "Test calcChecksum function"
        self.assertEquals(calcChecksum(b""), 0)
        self.assertEquals(calcChecksum(b"\1"), 0x01000000)
        self.assertEquals(calcChecksum(b"\x01\x02\x03\x04\x10\x20\x30\x40"), 0x11223344)
        self.assertEquals(calcChecksum(b"\x81"), 0x81000000)
        self.assertEquals(calcChecksum(b"\x81\x02"), 0x81020000)
        self.assertEquals(calcChecksum(b"\x81\x02\x03"), 0x81020300)
        self.assertEquals(calcChecksum(b"\x81\x02\x03\x04"), 0x81020304)
        self.assertEquals(calcChecksum(b"\x81\x02\x03\x04\x05"), 0x86020304)
        self.assertEquals(calcChecksum(b"\x41\x02\x03\x04\xD0\x20\x30\x40"), 0x11223344)
        self.assertEquals(calcChecksum(b"\xD1\x02\x03\x04\x40\x20\x30\x40"), 0x11223344)
        self.assertEquals(calcChecksum(b"\x81\x02\x03\x04\x90\x20\x30\x40"), 0x11223344)
        self.assertEquals(calcChecksum(b"\x7F\xFF\xFF\xFF\x00\x00\x00\x01"), 0x80000000)

    def testFontFileChecksum(self):
        "Tests TTFontFile and TTF parsing code"
        F = TTFOpenFile("Vera.ttf")[1].read()
        TTFontFile(getBytesIO(F), validate=1) # should not fail
        F1 = F[:12345] + b"\xFF" + F[12346:] # change one byte
        self.assertRaises(TTFError, TTFontFile, getBytesIO(F1), validate=1)
        F1 = F[:8] + b"\xFF" + F[9:] # change one byte
        self.assertRaises(TTFError, TTFontFile, getBytesIO(F1), validate=1)

    def testSubsetting(self):
        "Tests TTFontFile and TTF parsing code"
        ttf = TTFontFile("Vera.ttf")
        subset = ttf.makeSubset([0x41, 0x42])
        subset = TTFontFile(getBytesIO(subset), 0)
        for tag in ('cmap', 'head', 'hhea', 'hmtx', 'maxp', 'name', 'OS/2',
                    'post', 'cvt ', 'fpgm', 'glyf', 'loca', 'prep'):
            self.assert_(subset.get_table(tag))

        subset.seek_table('loca')
        for n in range(4):
            pos = subset.read_ushort()    # this is actually offset / 2
            self.failIf(pos % 2 != 0, "glyph %d at +%d should be long aligned" % (n, pos * 2))

        self.assertEquals(subset.name, b"BitstreamVeraSans-Roman")
        self.assertEquals(subset.flags, FF_SYMBOLIC)
        self.assertEquals(subset.italicAngle, 0.0)
        self.assertNear(subset.ascent,759.765625)
        self.assertNear(subset.descent,-240.234375)
        self.assertEquals(subset.capHeight, 759.765625)
        self.assertNear(subset.bbox, [-183.10546875, -235.83984375, 1287.109375, 928.22265625])
        self.assertEquals(subset.stemV, 87)

    def testFontMaker(self):
        "Tests TTFontMaker class"
        ttf = TTFontMaker()
        ttf.add("ABCD", b"xyzzy")
        ttf.add("QUUX", b"123")
        ttf.add("head", b"12345678xxxx")
        stm = ttf.makeStream()
        ttf = TTFontParser(getBytesIO(stm), 0)
        self.assertEquals(ttf.get_table("ABCD"), b"xyzzy")
        self.assertEquals(ttf.get_table("QUUX"), b"123")


class TTFontFaceTestCase(unittest.TestCase):
    "Tests TTFontFace class"

    def testAddSubsetObjects(self):
        "Tests TTFontFace.addSubsetObjects"
        face = TTFontFace("Vera.ttf")
        doc = PDFDocument()
        fontDescriptor = face.addSubsetObjects(doc, "TestFont", [ 0x78, 0x2017 ])
        fontDescriptor = doc.idToObject[fontDescriptor.name].dict
        self.assertEquals(fontDescriptor['Type'], '/FontDescriptor')
        self.assertEquals(fontDescriptor['Ascent'], face.ascent)
        self.assertEquals(fontDescriptor['CapHeight'], face.capHeight)
        self.assertEquals(fontDescriptor['Descent'], face.descent)
        self.assertEquals(fontDescriptor['Flags'], (face.flags & ~FF_NONSYMBOLIC) | FF_SYMBOLIC)
        self.assertEquals(fontDescriptor['FontName'], "/TestFont")
        self.assertEquals(fontDescriptor['FontBBox'].sequence, face.bbox)
        self.assertEquals(fontDescriptor['ItalicAngle'], face.italicAngle)
        self.assertEquals(fontDescriptor['StemV'], face.stemV)
        fontFile = fontDescriptor['FontFile2']
        fontFile = doc.idToObject[fontFile.name]
        self.assert_(fontFile.content != "")


class TTFontTestCase(NearTestCase):
    "Tests TTFont class"

    def testStringWidth(self):
        "Test TTFont.stringWidth"
        font = TTFont("Vera", "Vera.ttf")
        self.assert_(font.stringWidth("test", 10) > 0)
        width = font.stringWidth(utf8(0x2260) * 2, 1000)
        expected = font.face.getCharWidth(0x2260) * 2
        self.assertNear(width,expected)

    def testSplitString(self):
        "Tests TTFont.splitString"
        doc = PDFDocument()
        font = TTFont("Vera", "Vera.ttf")
        text = b"".join(utf8(i) for i in range(511))
        allchars = b"".join(int2Byte(i) for i in range(256))
        nospace = allchars[:32] + allchars[33:]
        chunks = [(0, allchars), (1, nospace)]
        self.assertEquals(font.splitString(text, doc), chunks)
        # Do it twice
        self.assertEquals(font.splitString(text, doc), chunks)

        text = b"".join(utf8(i) for i in range(510, -1, -1))
        allchars = b"".join(int2Byte(i) for i in range(255, -1, -1))
        nospace = allchars[:223] + allchars[224:]
        chunks = [(1, nospace), (0, allchars)]
        self.assertEquals(font.splitString(text, doc), chunks)

    def testSplitStringSpaces(self):
        # In order for justification (word spacing) to work, the space
        # glyph must have a code 32, and no other character should have
        # that code in any subset, or word spacing will be applied to it.

        doc = PDFDocument()
        font = TTFont("Vera", "Vera.ttf")
        text = b"".join(utf8(i) for i in range(512, -1, -1))
        chunks = font.splitString(text, doc)
        state = font.state[doc]
        self.assertEquals(state.assignments[32], 32)
        self.assertEquals(state.subsets[0][32], 32)
        self.assertEquals(state.subsets[1][32], 32)

    def testSubsetInternalName(self):
        "Tests TTFont.getSubsetInternalName"
        doc = PDFDocument()
        font = TTFont("Vera", "Vera.ttf")
        # Actually generate some subsets
        text = b"".join(utf8(i) for i in range(513))
        font.splitString(text, doc)
        self.assertRaises(IndexError, font.getSubsetInternalName, -1, doc)
        self.assertRaises(IndexError, font.getSubsetInternalName, 3, doc)
        self.assertEquals(font.getSubsetInternalName(0, doc), "/F1+0")
        self.assertEquals(font.getSubsetInternalName(1, doc), "/F1+1")
        self.assertEquals(font.getSubsetInternalName(2, doc), "/F1+2")
        self.assertEquals(doc.delayedFonts, [font])

    def testAddObjectsEmpty(self):
        "TTFont.addObjects should not fail when no characters were used"
        font = TTFont("Vera", "Vera.ttf")
        doc = PDFDocument()
        font.addObjects(doc)

    def no_longer_testAddObjectsResets(self):
        "Test that TTFont.addObjects resets the font"
        # Actually generate some subsets
        doc = PDFDocument()
        font = TTFont("Vera", "Vera.ttf")
        font.splitString('a', doc)            # create some subset
        doc = PDFDocument()
        font.addObjects(doc)
        self.assertEquals(font.frozen, 0)
        self.assertEquals(font.nextCode, 0)
        self.assertEquals(font.subsets, [])
        self.assertEquals(font.assignments, {})
        font.splitString('ba', doc)           # should work

    def testParallelConstruction(self):
        "Test that TTFont can be used for different documents at the same time"
        ttfAsciiReadable = rl_config.ttfAsciiReadable
        try:
            rl_config.ttfAsciiReadable = 1
            doc1 = PDFDocument()
            doc2 = PDFDocument()
            font = TTFont("Vera", "Vera.ttf")
            self.assertEquals(font.splitString('hello ', doc1), [(0, b'hello ')])
            self.assertEquals(font.splitString('hello ', doc2), [(0, b'hello ')])
            self.assertEquals(font.splitString(u'\u0410\u0411'.encode('UTF-8'), doc1), [(0, b'\x80\x81')])
            self.assertEquals(font.splitString(u'\u0412'.encode('UTF-8'), doc2), [(0, b'\x80')])
            font.addObjects(doc1)
            self.assertEquals(font.splitString(u'\u0413'.encode('UTF-8'), doc2), [(0, b'\x81')])
            font.addObjects(doc2)
        finally:
            rl_config.ttfAsciiReadable = ttfAsciiReadable

    def testAddObjects(self):
        "Test TTFont.addObjects"
        # Actually generate some subsets
        ttfAsciiReadable = rl_config.ttfAsciiReadable
        try:
            rl_config.ttfAsciiReadable = 1
            doc = PDFDocument()
            font = TTFont("Vera", "Vera.ttf")
            font.splitString('a', doc)            # create some subset
            internalName = font.getSubsetInternalName(0, doc)[1:]
            font.addObjects(doc)
            pdfFont = doc.idToObject[internalName]
            self.assertEquals(doc.idToObject['BasicFonts'].dict[internalName], pdfFont)
            self.assertEquals(pdfFont.Name, internalName)
            self.assertEquals(pdfFont.BaseFont, "AAAAAA+BitstreamVeraSans-Roman")
            self.assertEquals(pdfFont.FirstChar, 0)
            self.assertEquals(pdfFont.LastChar, 127)
            self.assertEquals(len(pdfFont.Widths.sequence), 128)
            toUnicode = doc.idToObject[pdfFont.ToUnicode.name]
            self.assert_(toUnicode.content != "")
            fontDescriptor = doc.idToObject[pdfFont.FontDescriptor.name]
            self.assertEquals(fontDescriptor.dict['Type'], '/FontDescriptor')
        finally:
            rl_config.ttfAsciiReadable = ttfAsciiReadable

    def testMakeToUnicodeCMap(self):
        "Test makeToUnicodeCMap"
        self.assertEquals(makeToUnicodeCMap("TestFont", [ 0x1234, 0x4321, 0x4242 ]),
"""/CIDInit /ProcSet findresource begin
12 dict begin
begincmap
/CIDSystemInfo
<< /Registry (TestFont)
/Ordering (TestFont)
/Supplement 0
>> def
/CMapName /TestFont def
/CMapType 2 def
1 begincodespacerange
<00> <02>
endcodespacerange
3 beginbfchar
<00> <1234>
<01> <4321>
<02> <4242>
endbfchar
endcmap
CMapName currentdict /CMap defineresource pop
end
end""")


def makeSuite():
    suite = makeSuiteForClasses(
        TTFontsTestCase,
        TTFontFileTestCase,
        TTFontFaceTestCase,
        TTFontTestCase)
    return suite


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
