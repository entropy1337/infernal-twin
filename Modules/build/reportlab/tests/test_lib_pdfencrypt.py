#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2013
#see license.txt for license details
__version__='''$Id$'''
__doc__="""Testing to encrypt a very minimal pdf using a Canvas and a DocTemplate.
TODO: Automatiocally test that this pdf is really encrypted.
"""
import unittest
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import pdfencrypt
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph

def parsedoc(fileName):
    """
    Using PDFParseContext object from Pagecatcher module to check for encryption.
    """
    try:
        from rlextra.pageCatcher.pageCatcher import PDFParseContext
    except ImportError:
        return
    pdfContent = open(fileName, 'rb').read()
    p = PDFParseContext(pdfContent, prefix="PageForms")
    p.parse()
    assert p.encrypt

def testStdEnc(expectedO,expectedU,expectedKey,
                strength=40, overrideID='xxxxxxxxxxxxxxxx',
                userPass='User',ownerPass='Owner',
                ):
    # do a 40 bit example known to work in Acrobat Reader 4.0
    enc = pdfencrypt.StandardEncryption(userPass,ownerPass, strength=strength)
    enc.setAllPermissions(0)
    enc.canPrint = 1
    enc.prepare(None,overrideID)

    pdfencrypt.equalityCheck(pdfencrypt.hexText(enc.O),expectedO, '%d bit O value'%strength)
    pdfencrypt.equalityCheck(pdfencrypt.hexText(enc.U),expectedU, '%d bit U value'%strength)
    pdfencrypt.equalityCheck(pdfencrypt.hexText(enc.key),expectedKey, '%d bit key value'%strength)

class EncryptTestCase(unittest.TestCase):

    def test_canvas(self):
        "Test generating an encrypted pdf by setting a user password on the Canvas."
        fname = outputfile('test_encrypt_canvas.pdf')
        c = Canvas(fname, encrypt='User')
        c.setAuthor('Anonymous')
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Top secret')
        c.save()
        parsedoc(fname)

    def test_standardencryption(self):
        "Test generating an encrypted pdf by passing a StandardEncryption object to the Canvas."
        encrypt = pdfencrypt.StandardEncryption(userPassword='User', ownerPassword='Owner')
        encrypt.setAllPermissions(0)
        encrypt.canPrint = 1
        fname = outputfile('test_encrypt_canvas2.pdf')
        c = Canvas(fname, encrypt=encrypt)
        c.setAuthor('Anonymous')
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Top secret')
        c.save()
        parsedoc(fname)

    def test_doctemplate(self):
        "Test generating an encrypted pdf by setting a user password on the DocTemplate."
        header = ParagraphStyle(name='Heading', fontSize=36)
        story = [Paragraph("Top secret", header)]
        fname = outputfile('test_encrypt_doctemplate.pdf')
        doc = SimpleDocTemplate(fname, encrypt='User')
        doc.build(story)
        parsedoc(fname)

    def test_standardencryption128(self):
        "Test generating an encrypted pdf by passing a StandardEncryption object to the Canvas."
        encrypt = pdfencrypt.StandardEncryption(userPassword='User', ownerPassword='Owner',strength=128)
        encrypt.setAllPermissions(0)
        encrypt.canPrint = 1
        fname = outputfile('test_encrypt_canvas2_128.pdf')
        c = Canvas(fname, encrypt=encrypt)
        c.setAuthor('Anonymous')
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'More Top secret uses 128 bit encryption!')
        c.save()
        parsedoc(fname)

    def test_calcs(self):
        testStdEnc(
                expectedO = '<FA7F558FACF8205D25A7F1ABFA02629F707AE7B0211A2BB26F5DF4C30F684301>',
                expectedU = '<4E6F35A0356D6A624A72387D71FFB92EA4457E435307A9DD0BA9DE0618F5BABD>',
                expectedKey = '<DC96439AD9>',
                strength=40, overrideID='xxxxxxxxxxxxxxxx',
                userPass='User',ownerPass='Owner',
                )
        testStdEnc(
                expectedO = '<E60E73846B1C9EB09986B2C20DEAEF48BCC2210F75AE640655EDDFF8B67E7DD6>',
                expectedU = '<D9E804E73FB37EDECF35176140304BD600000000000000000000000000000000>',
                expectedKey = '<7C0C9D27068EB81B291698B2CC278A48>',
                strength=128, overrideID='xxxxxxxxxxxxxxxx',
                userPass='User',ownerPass='Owner',
                )
        testStdEnc(
                expectedO = '<FA7F558FACF8205D25A7F1ABFA02629F707AE7B0211A2BB26F5DF4C30F684301>',
                expectedU = '<CB749297C89784B4BC94228F38B5FD4318398CA68F327A615A6CD8A5FCDB8C52>',
                expectedKey = '<1528D3A2F9>',
                strength=40, overrideID=b'\xbf\x08\xdf\x96I\x959e\x8f\x03\xcb\xb4\x11 W\xa9',
                userPass='User',ownerPass='Owner',
                )
        testStdEnc(
                expectedO = '<E60E73846B1C9EB09986B2C20DEAEF48BCC2210F75AE640655EDDFF8B67E7DD6>',
                expectedU = '<9A823CD6C39CEA508577319287621BF800000000000000000000000000000000>',
                expectedKey = '<6F8DB99AA5D9693CA757C2F03DAB71FF>',
                strength=128, overrideID=b'\xbf\x08\xdf\x96I\x959e\x8f\x03\xcb\xb4\x11 W\xa9',
                userPass='User',ownerPass='Owner',
                )

def makedoc(fileName, userPass="User", ownerPass="Owner"):
    """
    Creates a simple encrypted pdf.
    """
    encrypt = pdfencrypt.StandardEncryption(userPass, ownerPass)
    encrypt.setAllPermissions(0)
    encrypt.canPrint = 1

    c = Canvas(fileName)
    c._doc.encrypt = encrypt

    c.drawString(100, 500, "hello world")

    c.save()

class ManualTestCase(unittest.TestCase):
    "Runs manual encrypted file builders."

    def test(self):
        filepath = outputfile('test_pdfencryption.pdf')
        makedoc(filepath)
        parsedoc(filepath)

def makeSuite():
    return makeSuiteForClasses(EncryptTestCase,ManualTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
