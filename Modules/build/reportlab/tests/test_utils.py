#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__version__='''$Id$'''
__doc__="""Test reportlab.lib.util module"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest
from reportlab.lib.utils import FmtSelfDict, encode_label, decode_label

class FmtTestCase(unittest.TestCase):

    def testFmt(self):
        class MixedIn(FmtSelfDict):
            def __init__(self):
                self.a = 'AA'
                self._b = '_BB'
                self.d = '(overridden)'
        obj = MixedIn()
        self.assertEqual('blah', obj._fmt('blah'))
        self.assertEqual('blah %', obj._fmt('blah %%'))
        self.assertRaises(ValueError, obj._fmt, 'blah %')
        self.assertEqual(
            'moon AA june_BB spoon %(a)sCC ni',
            obj._fmt('moon %(a)s june%(_b)s spoon %%(a)s%(c)s %(d)s', c='CC', C='boon', d='ni'))
        self.assertRaises(AttributeError, obj._fmt, '%(c)s')  # XXX bit weird, can this be changed?

    def testLabelCoding(self):
        a = (1,2,[3,4],"a"), [1,2,"4",b'4']
        assert a == decode_label(encode_label(a))

def makeSuite():
    return makeSuiteForClasses(FmtTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
