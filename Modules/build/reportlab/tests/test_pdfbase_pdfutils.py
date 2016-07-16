#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
"""Tests for utility functions in reportlab.pdfbase.pdfutils.
"""
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, printLocation
setOutDir(__name__)
import os
import unittest
from reportlab.pdfbase.pdfutils import _AsciiHexEncode, _AsciiHexDecode
from reportlab.pdfbase.pdfutils import asciiBase85Encode, asciiBase85Decode
from reportlab.lib.utils import asBytes

class PdfEncodingTestCase(unittest.TestCase):
    "Test various encodings used in PDF files."

    def testAsciiHex(self):
        "Test if the obvious test for whether ASCII-Hex encoding works."

        plainText = 'What is the average velocity of a sparrow?'
        encoded = _AsciiHexEncode(plainText)
        decoded = _AsciiHexDecode(encoded)

        msg = "Round-trip AsciiHex encoding failed."
        assert decoded == plainText, msg


    def testAsciiBase85(self):
        "Test if the obvious test for whether ASCII-Base85 encoding works."

        msg = "Round-trip AsciiBase85 encoding failed."
        plain = 'What is the average velocity of a sparrow?'

        #the remainder block can be absent or from 1 to 4 bytes
        for i in xrange(256):
            encoded = asciiBase85Encode(plain)
            decoded = asciiBase85Decode(encoded)
            assert decoded == asBytes(plain,'latin1'), msg
            plain += chr(i)

def makeSuite():
    return makeSuiteForClasses(PdfEncodingTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
