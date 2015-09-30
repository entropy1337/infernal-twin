from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation, NearTestCase
setOutDir(__name__)
import unittest,re,codecs
from reportlab.pdfbase import pdfdoc
from reportlab import rl_config

class PdfdocTestCase(NearTestCase):
    """Tests of expected Unicode and encoding behaviour
    """
    def setUp(self):
        self.pdfMultiLine = rl_config.pdfMultiLine
        self.pdfComments = rl_config.pdfComments
        rl_config.pdfMultiLine = 0
        rl_config.pdfComments = 0

    def tearDown(self):
        rl_config.pdfMultiLine = self.pdfMultiLine
        rl_config.pdfComments = self.pdfComments

    def testPDFText(self):
        self.assertEquals(pdfdoc.PDFText(b'Hello World').format(self.doc),b'<48656c6c6f20576f726c64>')

    def testPDFString(self):
        self.assertEquals(pdfdoc.PDFString(b'Hello World').format(self.doc),b'(Hello World)')
        self.assertEquals(pdfdoc.PDFString(b'Hello\xc2\xa2World',0).format(self.doc),b'(Hello\xa2World)')
        self.assertEquals(pdfdoc.PDFString(b'Hello\xc2\xa0World',0).format(self.doc),b'(\xfe\xff\x00H\x00e\x00l\x00l\x00o\x00\xa0\x00W\x00o\x00r\x00l\x00d)')
        self.assertEquals(pdfdoc.PDFString(b'Hello\xc2\xa0World',1).format(self.doc),b'(\\376\\377\\000H\\000e\\000l\\000l\\000o\\000\\240\\000W\\000o\\000r\\000l\\000d)')
        self.assertEquals(pdfdoc.PDFString(u'Hello\xa0World'.encode('utf8'),1).format(self.doc),b'(\\376\\377\\000H\\000e\\000l\\000l\\000o\\000\\240\\000W\\000o\\000r\\000l\\000d)')
        self.assertEquals(pdfdoc.PDFString(u'Hello\xa0World'.encode('utf8'),0).format(self.doc),b'(\xfe\xff\x00H\x00e\x00l\x00l\x00o\x00\xa0\x00W\x00o\x00r\x00l\x00d)')

    def testPDFArray(self):
        self.assertEquals(pdfdoc.PDFArray([1,2,3,4]).format(self.doc),b'[ 1 2 3 4 ]')

    def testPDFIndirectObject(self):
        doc = self.doc
        doc.Reference(pdfdoc.PDFArray([0,1,2,3]),pdfdoc.PDFName('abracadabra')[1:])
        self.assertEquals(pdfdoc.PDFIndirectObject('abracadabra',pdfdoc.PDFArray([3,2,1,0])).format(doc),b'2 0 obj\r\n[ 3 2 1 0 ]\r\nendobj\r\n')

    def testPDFDictionary(self):
        self.assertEquals(pdfdoc.PDFDictionary(dict(A=pdfdoc.PDFArray([1,2,3,4]))).format(self.doc),b'<< /A [ 1 2 3 4 ] >>')

    def testPDFPageLabels(self):
        doc = self.doc
        PL=pdfdoc.PDFPageLabels()
        PL.addPageLabel(0,pdfdoc.PDFPageLabel('D',0,'AA'))
        self.assertEquals(PL.format(doc),b'<< /Nums [ 0 2 0 R ] >>')

    @property
    def doc(self):
        return pdfdoc.PDFDocument()

def makeSuite():
    return makeSuiteForClasses(
        PdfdocTestCase,
        )

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
