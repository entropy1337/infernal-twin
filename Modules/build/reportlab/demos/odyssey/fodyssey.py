#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__version__=''' $Id$ '''
__doc__=''

#REPORTLAB_TEST_SCRIPT
import sys, copy, os
from reportlab.platypus import *
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

import reportlab.rl_config
reportlab.rl_config.invariant = 1

styles = getSampleStyleSheet()

Title = "The Odyssey"
Author = "Homer"

def myFirstPage(canvas, doc):
    canvas.saveState()
    canvas.restoreState()

def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "Page %d" % doc.page)
    canvas.restoreState()

def go():
    doc = SimpleDocTemplate('fodyssey.pdf',showBoundary='showboundary' in sys.argv)
    doc.allowSplitting = not 'nosplitting' in sys.argv
    doc.build(Elements,myFirstPage,myLaterPages)

Elements = []

ChapterStyle = copy.copy(styles["Heading1"])
ChapterStyle.alignment = TA_CENTER
ChapterStyle.fontsize = 16
InitialStyle = copy.deepcopy(ChapterStyle)
InitialStyle.fontsize = 16
InitialStyle.leading = 20
PreStyle = styles["Code"]

def newPage():
    Elements.append(PageBreak())

def chapter(txt, style=ChapterStyle):
    newPage()
    Elements.append(Paragraph(txt, style))
    Elements.append(Spacer(0.2*inch, 0.3*inch))

def fTitle(txt,style=InitialStyle):
    Elements.append(Paragraph(txt, style))

ParaStyle = copy.deepcopy(styles["Normal"])
ParaStyle.spaceBefore = 0.1*inch
if 'right' in sys.argv:
    ParaStyle.alignment = TA_RIGHT
elif 'left' in sys.argv:
    ParaStyle.alignment = TA_LEFT
elif 'justify' in sys.argv:
    ParaStyle.alignment = TA_JUSTIFY
elif 'center' in sys.argv or 'centre' in sys.argv:
    ParaStyle.alignment = TA_CENTER
else:
    ParaStyle.alignment = TA_JUSTIFY

def spacer(inches):
    Elements.append(Spacer(0.1*inch, inches*inch))

def p(txt, style=ParaStyle):
    Elements.append(Paragraph(txt, style))

def pre(txt, style=PreStyle):
    spacer(0.1)
    p = Preformatted(txt, style)
    Elements.append(p)

def parseOdyssey(fn):
    from time import time
    E = []
    t0=time()
    text = open(fn,'r').read()
    i0 = text.index('Book I')
    endMarker = 'covenant of peace between the two contending parties.'
    i1 = text.index(endMarker)+len(endMarker)
    PREAMBLE=list(map(str.strip,text[0:i0].split('\n')))
    L=list(map(str.strip,text[i0:i1].split('\n')))
    POSTAMBLE=list(map(str.strip,text[i1:].split('\n')))

    def ambleText(L):
        while L and not L[0]: L.pop(0)
        while L:
            T=[]
            while L and L[0]:
                T.append(L.pop(0))
            yield T
            while L and not L[0]: L.pop(0)

    def mainText(L):
        while L:
            B = L.pop(0)
            while not L[0]: L.pop(0)
            T=[]
            while L and L[0]:
                T.append(L.pop(0))
            while not L[0]: L.pop(0)
            P = []
            while L and not (L[0].startswith('Book ') and len(L[0].split())==2):
                E=[]
                while L and L[0]:
                    E.append(L.pop(0))
                P.append(E)
                if L:
                    while not L[0]: L.pop(0)
            yield B,T,P

    t1 = time()
    print("open(%s,'r').read() took %.4f seconds" %(fn,t1-t0))

    E.append([spacer,2])
    E.append([fTitle,'<font color=red>%s</font>' % Title, InitialStyle])
    E.append([fTitle,'<font size=-4>by</font> <font color=green>%s</font>' % Author, InitialStyle])

    for T in ambleText(PREAMBLE):
        E.append([p,'\n'.join(T)])

    for (B,T,P) in mainText(L):
        E.append([chapter,B])
        E.append([p,'<font size="+1" color="Blue"><b>%s</b></font>' % '\n'.join(T),ParaStyle])
        for x in P:
            E.append([p,' '.join(x)])
    firstPre = 1
    for T in ambleText(POSTAMBLE):
        E.append([p,'\n'.join(T)])

    t3 = time()
    print("Parsing into memory took %.4f seconds" %(t3-t1))
    del L
    t4 = time()
    print("Deleting list of lines took %.4f seconds" %(t4-t3))
    for i in range(len(E)):
        E[i][0](*E[i][1:])
    t5 = time()
    print("Moving into platypus took %.4f seconds" %(t5-t4))
    del E
    t6 = time()
    print("Deleting list of actions took %.4f seconds" %(t6-t5))
    go()
    t7 = time()
    print("saving to PDF took %.4f seconds" %(t7-t6))
    print("Total run took %.4f seconds"%(t7-t0))

for fn in ('odyssey.full.txt','odyssey.txt'):
    if os.path.isfile(fn):
        break
if __name__=='__main__':
    parseOdyssey(fn)
