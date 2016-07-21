#copyright ReportLab Europe Limited. 2000-2012
#see license.txt for license details
__version__=''' $Id$ '''
__doc__="""
This contains tests for the encryption algorithms.

The algorithmic approach is to take values from a known
readable-but-secured PDF file and put them in as assertions.
If a platform varies in any way or we change an algorithm
by mistake, it should shriek at us.

It also generates a directory of files to scan by eyeball,
with meaningful names to suggest the properties they have.

"""
import unittest
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pdfencrypt import computeO, \
    computeU, hexText, unHexText, encryptionkey, encodePDF, \
    encryptCanvas

VERBOSE = 0

class EncryptionAlgorithmTestCase(unittest.TestCase):
    """Acrobat algorithms.  Two specific cases known to work.

    We are dealing with 8 bit strings which may contain nasty
    escape characters, get trashed in FTP or editors etc.  Therefore
    I am using two explicit routines hexText and unHexText which
    provide a 'safe' way to represent strings as hex and which are
    not going to vary with Python versions"""

    def check0wnerHash40Bit(self):
        "owner key calculation"
        ownerHash = computeO('userpass','ownerpass', revision=2)
        assert hexText(ownerHash) == '<F86213EB0CED81F097947F3B343E34CAC8CA92CE8F6FEE2556FA31EC1FE968AF>'
        
    def checkEncryptionKey40Bit(self):
        userPass = 'userpass'
        ownerHash = unHexText('<F86213EB0CED81F097947F3B343E34CAC8CA92CE8F6FEE2556FA31EC1FE968AF>')
        documentID = 'xxxxxxxxxxxxxxxx'        
        permissions = -4
        encKey = encryptionkey(userPass, ownerHash, permissions, documentID, revision=2)
        assert hexText(encKey) == '<7EBBD07A88>'

    def checkUserHash40Bit(self):
        encKey = unHexText('<7EBBD07A88>')
        userHash = computeU(encKey, revision=2, documentId='xxxxxxxxxxxxxxxx')
        assert hexText(userHash) == '<AA154131D8FA105317F7104D2001A345D78A3DEEFA3D85D032FC9B4B35DA72A0>'

    def checkEncryptString40Bit(self):
        assert hexText(encodePDF(unHexText('<3DC3EBDA71>'), 9, 0, 'anonymous')) == '<57AC33DDEB5775982A>'

        
    def check0wnerHash128Bit(self):
        "owner key calculation"
        ownerHash = computeO('userpass','ownerpass', revision=3)
        assert hexText(ownerHash) == '<68E5704AC779A5F0CD89704406587A52F25BF61CADC56A0F8DB6C4DB0052534D>'
        
    def checkEncryptionKey128Bit(self):
        userPass = 'userpass'
        ownerHash = unHexText('<68E5704AC779A5F0CD89704406587A52F25BF61CADC56A0F8DB6C4DB0052534D>')
        documentID = 'xxxxxxxxxxxxxxxx'        
        permissions = -4
        encKey = encryptionkey(userPass, ownerHash, permissions, documentID, revision=3)
        assert hexText(encKey) == '<13DDE7585D9BE366C976DDD56AF541D1>'
        
    def checkUserHash128Bit(self):
        encKey = unHexText('<13DDE7585D9BE366C976DDD56AF541D1>')
        userHash = computeU(encKey, revision=3, documentId='xxxxxxxxxxxxxxxx')
        assert hexText(userHash) == '<A9AE45CDE827FE0B7D6536267948836A00000000000000000000000000000000>'

    def checkEncryptString128Bit(self):
        assert hexText(encodePDF(unHexText('<3C0C5EBE0122D8EB2BDDF8A09FA8E29E>'),
                                 9,
                                 0,
                                 'anonymous')
                       ) == '<27FB3E943FCF61878B>'

class EyeballTestCase(unittest.TestCase):
    "This makes a gaxillion self-explanatory files"
    def check40BitOptions(self):
        userPass = 'userpass'
        for canPrint in (0, 1):
            for canModify in (0, 1):
                for canCopy in (0, 1):
                    for canAnnotate in (0, 1):
                        for strength in (40, 128):
                            # work out a 4-char string to be a mnemonic for the options
                            p = m = c = a = 'x'
                            if canPrint: p = 'P'
                            if canModify: m = 'M'
                            if canCopy: c = 'C'
                            if canAnnotate: a = 'A'

                            filename = 'test_crypto_%03dbit_%s_%s%s%s%s.pdf' % (
                                strength, userPass, p, m, c, a)
                            import os
                            filepath = outputfile(filename)
                            canv = Canvas(filepath)
                            
                            canv.setFont('Helvetica', 24)
                            canv.drawString(100,700, 'PDF Encryption test case')
                            canv.setFont('Helvetica', 16)
                            canv.drawString(100, 675, 'Verify by looking at File - Document Info - Security')

                            canv.drawString(100, 600, 'open password = %s' % userPass)
                            canv.drawString(100, 575, 'strength = %d buts' % strength)
                            canv.drawString(100, 500, 'canPrint = %d' % canPrint)
                            canv.drawString(100, 475, 'canModify = %d' % canModify)
                            canv.drawString(100, 450, 'canCopy = %d' % canCopy)
                            canv.drawString(100, 425, 'canAnnotate = %d' % canAnnotate)

                            encryptCanvas(canv,
                                          userPass,
                                          canPrint=canPrint,
                                          canModify=canModify,
                                          canCopy=canCopy,
                                          canAnnotate=canAnnotate,
                                          strength=strength)
                            
                            canv.save()
                            if VERBOSE: print('saved %s' % filepath)
        
def makeSuite():
    return unittest.TestSuite((
        unittest.makeSuite(EncryptionAlgorithmTestCase,'check'),
        unittest.makeSuite(EyeballTestCase,'check'),
        ))
        
if __name__=='__main__':
    unittest.TextTestRunner().run(makeSuite())
