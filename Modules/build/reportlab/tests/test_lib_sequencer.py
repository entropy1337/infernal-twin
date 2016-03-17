#Copyright ReportLab Europe Ltd. 2000-2013
#see license.txt for license details
"""Tests for the reportlab.lib.sequencer module.
"""
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, printLocation
setOutDir(__name__)
import sys, random
import unittest
from reportlab.lib.sequencer import Sequencer


class SequencerTestCase(unittest.TestCase):
    "Test Sequencer usage."

    def test0(self):
        "Test sequencer default counter."

        seq = Sequencer()
        msg = 'Initial value is not zero!'
        assert seq._this() == 0, msg


    def test1(self):
        "Test incrementing default counter."

        seq = Sequencer()

        for i in range(1, 101):
            n = seq.next()
            msg = 'Sequence value is not correct!'
            assert seq._this() == n, msg


    def test2(self):
        "Test resetting default counter."

        seq = Sequencer()
        start = seq._this()

        for i in range(1, 101):
            n = seq.next()

        seq.reset()

        msg = 'Sequence value not correctly reset!'
        assert seq._this() == start, msg


    def test3(self):
        "Test incrementing dedicated counter."

        seq = Sequencer()

        for i in range(1, 101):
            n = seq.next('myCounter1')
            msg = 'Sequence value is not correct!'
            assert seq._this('myCounter1') == n, msg


    def test4(self):
        "Test resetting dedicated counter."

        seq = Sequencer()
        start = seq._this('myCounter1')

        for i in range(1, 101):
            n = seq.next('myCounter1')

        seq.reset('myCounter1')

        msg = 'Sequence value not correctly reset!'
        assert seq._this('myCounter1') == start, msg


    def test5(self):
        "Test incrementing multiple dedicated counters."

        seq = Sequencer()
        startMyCounter0 = seq._this('myCounter0')
        startMyCounter1 = seq._this('myCounter1')

        for i in range(1, 101):
            n = seq.next('myCounter0')
            msg = 'Sequence value is not correct!'
            assert seq._this('myCounter0') == n, msg
            m = seq.next('myCounter1')
            msg = 'Sequence value is not correct!'
            assert seq._this('myCounter1') == m, msg

    def testChain(self):
        "Test auto resetting of subsections"
        seq = Sequencer()
        seq.chain('h1', 'h2')  #creates them and links
        self.assertEquals(seq.next('h1'), 1)
        self.assertEquals(seq.next('h1'), 2)
        self.assertEquals(seq.next('h2'), 1)
        self.assertEquals(seq.next('h2'), 2)
        self.assertEquals(seq.next('h2'), 3)

        #start chapter 3
        self.assertEquals(seq.next('h1'), 3)
        #...and the first section should be numbered 1, not 4
        self.assertEquals(seq.next('h2'), 1)        


##    def testRandom(self):
##        "Test randomly manipulating multiple dedicated counters."
##
##        seq = Sequencer()
##        counterNames = ['c0', 'c1', 'c2', 'c3']
##
##        # Init.
##        for cn in counterNames:
##            setattr(self, cn, seq._this(cn))
##            msg = 'Counter start value is not correct!'
##            assert seq._this(cn) == 0, msg
##
##        # Increment/decrement.
##        for i in range(1, 101):
##            n = seq.next('myCounter0')
##            msg = 'Sequence value is not correct!'
##            assert seq._this('myCounter0') == n, msg
##            m = seq.next('myCounter1')
##            msg = 'Sequence value is not correct!'
##            assert seq._this('myCounter1') == m, msg


def makeSuite():
    return makeSuiteForClasses(SequencerTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
