#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
"""Tests for the reportlab.platypus.paragraphs module.
"""
__version__=''' $Id$ '''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys, os, unittest
from operator import truth
from reportlab.pdfbase.pdfmetrics import stringWidth, registerFont, registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.paraparser import ParaParser
from reportlab.platypus.flowables import Flowable, DocAssert
from reportlab.lib.colors import Color
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import _className
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus.frames import Frame, ShowBoundaryValue
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, PageBreak, NextPageTemplate
from reportlab.platypus import tableofcontents
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.tables import TableStyle, Table
from reportlab.platypus.paragraph import Paragraph, _getFragWords, _splitWord

def myMainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."

    canvas.saveState()

    canvas.rect(2.5*cm, 2.5*cm, 15*cm, 25*cm)
    canvas.setFont('Times-Roman', 12)
    pageNumber = canvas.getPageNumber()
    canvas.drawString(10*cm, cm, str(pageNumber))

    canvas.restoreState()

class MyDocTemplate(BaseDocTemplate):
    _invalidInitArgs = ('pageTemplates',)

    def __init__(self, filename, **kw):
        frame1 = Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')
        frame2 = Frame(2.5*cm, 2.5*cm, 310, 25*cm, id='F2')
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('normal', [frame1], myMainPageFrame)
        template1 = PageTemplate('special', [frame2], myMainPageFrame)
        template2 = PageTemplate('template2', [Frame(395, 108, 165, 645, id='second2')])
        self.addPageTemplates([template,template1,template2])

class ParagraphCorners(unittest.TestCase):
    "some corner cases which should parse"
    def check(self,text,bt = getSampleStyleSheet()['BodyText']):
        try:
            P = Paragraph(text,style=bt)
        except:
            raise AssertionError("'%s' should parse"%text)
            
    def test0(self):
        self.check('<para />')
        self.check('<para/>')
        self.check('\t\t\t\n\n\n<para />')
        self.check('\t\t\t\n\n\n<para/>')
        self.check('<para\t\t\t\t/>')
        self.check('<para></para>')
        self.check('<para>      </para>')
        self.check('\t\t\n\t\t\t   <para>      </para>')

    def test1(self):
        "This makes several special paragraphs."

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']
        btN = ParagraphStyle('BodyTextTTNone',parent=bt,textTransform='none')
        btL = ParagraphStyle('BodyTextTTLower',parent=bt,textTransform='lowercase')
        btU = ParagraphStyle('BodyTextTTUpper',parent=bt,textTransform='uppercase')
        btC = ParagraphStyle('BodyTextTTCapitalize',parent=bt,textTransform='capitalize')
        story.append(Paragraph('''This should be ORDINARY text.''',style=bt))
        story.append(Paragraph('''This should be ORDINARY text.''',style=btN))
        story.append(Paragraph('''This should be LOWER text.''',style=btL))
        story.append(Paragraph('''This should be upper text.''',style=btU))
        story.append(Paragraph('''This should be cAPITALIZED text.''',style=btC))

        story.append(Paragraph('''T<i>hi</i>s shoul<font color="red">d b</font>e <b>ORDINARY</b> text.''',style=bt))
        story.append(Paragraph('''T<i>hi</i>s shoul<font color="red">d b</font>e <b>ORDINARY</b> text.''',style=btN))
        story.append(Paragraph('''T<i>hi</i>s shoul<font color="red">d b</font>e <b>LOWER</b> text.''',style=btL))
        story.append(Paragraph('''T<i>hi</i>s shoul<font color="red">d b</font>e <b>upper</b> text.''',style=btU))
        story.append(Paragraph('''T<i>hi</i>s shoul<font color="red">d b</font>e <b>cAPITALIZED</b> text.''',style=btC))
        doc = MyDocTemplate(outputfile('test_platypus_specialparagraphs.pdf'))
        doc.multiBuild(story)

    def test2(self):
        '''CJK splitting in multi-frag case'''
        style = ParagraphStyle('test', wordWrap = 'CJK')
        p = Paragraph('bla <i>blub</i> '*130 , style)
        aW,aH=439.275590551,121.88976378
        w,h=p.wrap(aW,aH)
        S=p.split(aW,aH)
        assert len(S)==2, 'Multi frag CJK splitting failed'
        w0,h0=S[0].wrap(aW,aH)
        assert h0<=aH,'Multi-frag CJK split[0] has wrong height %s >= available %s' % (H0,aH)
        w1,h1=S[1].wrap(aW,aH)
        assert h0+h1==h, 'Multi-frag-CJK split[0].height(%s)+split[1].height(%s) don\'t add to original %s' % (h0,h1,h)

    def test3(self):
        '''compare CJK splitting in some edge cases'''
        from reportlab.pdfgen.canvas import Canvas
        from reportlab.platypus.paragraph import Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.enums import TA_LEFT
        sty = ParagraphStyle('A')
        sty.fontSize = 15
        sty.leading = sty.fontSize*1.2
        sty.fontName = 'Courier'
        sty.alignment = TA_LEFT
        sty.wordWrap = 'CJK'
        p0=Paragraph('ABCDEFGHIJKL]N',sty)
        p1=Paragraph('AB<font color="red">C</font>DEFGHIJKL]N',sty)
        canv = Canvas('test_platypus_paragraph_cjk3.pdf')
        ix = len(canv._code)
        aW = pdfmetrics.stringWidth('ABCD','Courier',15)
        w,h=p0.wrap(aW,1000000)
        y = canv._pagesize[1]-72-h
        p0.drawOn(canv,72,y)
        w,h=p1.wrap(aW,1000000)
        y -= h+10
        p1.drawOn(canv,72,y)
        w,h=p0.wrap(aW*0.25-2,1000000)
        y -= h+10
        p0.drawOn(canv,72,y)
        w,h=p1.wrap(aW/4.-2,1000000)
        y -= h+10
        p1.drawOn(canv,72,y)
        assert canv._code[ix:]==['q', '1 0 0 1 72 697.8898 cm', 'q', '0 0 0 rg', 'BT 1 0 0 1 0 57 Tm /F2 15 Tf 18 TL (ABCD) Tj T* (EFGH) Tj T* (IJKL]) Tj T* (N) Tj T* ET', 'Q', 'Q', 'q', '1 0 0 1 72 615.8898 cm', 'q', 'BT 1 0 0 1 0 57 Tm 18 TL /F2 15 Tf 0 0 0 rg (AB) Tj 1 0 0 rg (C) Tj 0 0 0 rg (D) Tj T* (EFGH) Tj T* (IJKL]) Tj T* (N) Tj T* ET', 'Q', 'Q', 'q', '1 0 0 1 72 353.8898 cm', 'q', '0 0 0 rg', 'BT 1 0 0 1 0 237 Tm /F2 15 Tf 18 TL (A) Tj T* (B) Tj T* (C) Tj T* (D) Tj T* (E) Tj T* (F) Tj T* (G) Tj T* (H) Tj T* (I) Tj T* (J) Tj T* (K) Tj T* (L) Tj T* (]) Tj T* (N) Tj T* ET', 'Q', 'Q', 'q', '1 0 0 1 72 91.88976 cm', 'q', 'BT 1 0 0 1 0 237 Tm 18 TL /F2 15 Tf 0 0 0 rg (A) Tj T* (B) Tj T* 1 0 0 rg (C) Tj T* 0 0 0 rg (D) Tj T* (E) Tj T* (F) Tj T* (G) Tj T* (H) Tj T* (I) Tj T* (J) Tj T* (K) Tj T* (L) Tj T* (]) Tj T* (N) Tj T* ET', 'Q', 'Q']
        canv.showPage()
        canv.save()
        
class ParagraphSplitTestCase(unittest.TestCase):
    "Test multi-page splitting of paragraphs (eyeball-test)."

    def test0(self):
        "This makes one long multi-page paragraph."

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        bt = styleSheet['BodyText']
        text = '''If you imagine that the box of X's tothe left is
an image, what I want to be able to do is flow a
series of paragraphs around the image
so that once the bottom of the image is reached, then text will flow back to the
left margin. I know that it would be possible to something like this
using tables, but I can't see how to have a generic solution.
There are two examples of this in the demonstration section of the reportlab
site.
If you look at the "minimal" euro python conference brochure, at the end of the
timetable section (page 8), there are adverts for "AdSu" and "O'Reilly". I can
see how the AdSu one might be done generically, but the O'Reilly, unsure...
I guess I'm hoping that I've missed something, and that
it's actually easy to do using platypus.
'''
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.lib.testutils import testsFolder
        gif = os.path.join(testsFolder,'pythonpowered.gif')
        story.append(ParagraphAndImage(Paragraph(text,bt),Image(gif)))
        phrase = 'This should be a paragraph spanning at least three pages. '
        description = ''.join([('%d: '%i)+phrase for i in range(250)])
        story.append(ParagraphAndImage(Paragraph(description, bt),Image(gif),side='left'))

        doc = MyDocTemplate(outputfile('test_platypus_paragraphandimage.pdf'))
        doc.multiBuild(story)

    def test1(self):
        "This makes one long multi-page paragraph."

        # Build story.
        story = []
        styleSheet = getSampleStyleSheet()
        h3 = styleSheet['Heading3']
        bt = styleSheet['BodyText']
        text = '''If you imagine that the box of X's tothe left is
an image, what I want to be able to do is flow a
series of paragraphs around the image
so that once the bottom of the image is reached, then text will flow back to the
left margin. I know that it would be possible to something like this
using tables, but I can't see how to have a generic solution.
There are two examples of this in the demonstration section of the reportlab
site.
If you look at the "minimal" euro python conference brochure, at the end of the
timetable section (page 8), there are adverts for "AdSu" and "O'Reilly". I can
see how the AdSu one might be done generically, but the O'Reilly, unsure...
I guess I'm hoping that I've missed something, and that
it's actually easy to do using platypus.We can do greek letters <greek>mDngG</greek>. This should be a
u with a dieresis on top &lt;unichar code=0xfc/&gt;="<unichar code="0xfc"/>" and this &amp;#xfc;="&#xfc;" and this \\xc3\\xbc="\xc3\xbc". On the other hand this
should be a pound sign &amp;pound;="&pound;" and this an alpha &amp;alpha;="&alpha;". You can have links in the page <link href="http://www.reportlab.com" color="blue">ReportLab</link> &amp; <a href="http://www.reportlab.org" color="green">ReportLab.org</a>.
Use scheme "pdf:" to indicate an external PDF link, "http:", "https:" to indicate an external link eg something to open in
your browser. If an internal link begins with something that looks like a scheme, precede with "document:". Empty hrefs should be allowed ie <a href="">&lt;a href=""&gt;test&lt;/a&gt;</a> should be allowed. <strike>This text should have a strike through it.</strike>
'''
        from reportlab.platypus.flowables import ImageAndFlowables, Image
        from reportlab.lib.testutils import testsFolder
        gif = os.path.join(testsFolder,'pythonpowered.gif')
        heading = Paragraph('This is a heading',h3)
        story.append(ImageAndFlowables(Image(gif),[heading,Paragraph(text,bt)]))
        phrase = 'This should be a paragraph spanning at least three pages. '
        description = ''.join([('%d: '%i)+phrase for i in range(250)])
        story.append(ImageAndFlowables(Image(gif),[heading,Paragraph(description, bt)],imageSide='left'))
        story.append(NextPageTemplate('special'))
        story.append(PageBreak())
        VERA = ('Vera','VeraBd','VeraIt','VeraBI')
        for v in VERA:
            registerFont(TTFont(v,v+'.ttf'))
        registerFontFamily(*(VERA[:1]+VERA))
        story.append(ImageAndFlowables(
                        Image(gif,width=280,height=120),
                        Paragraph('''<font name="Vera">The <b>concept</b> of an <i>integrated</i> one <b><i>box</i></b> solution for <i><b>advanced</b></i> voice and
data applications began with the introduction of the IMACS. The
IMACS 200 carries on that tradition with an integrated solution
optimized for smaller port size applications that the IMACS could not
economically address. An array of the most popular interfaces and
features from the IMACS has been bundled into a small 2U chassis
providing the ultimate in ease of installation.</font>''',
                        style=ParagraphStyle(
                                name="base",
                                fontName="Helvetica",
                                leading=12,
                                leftIndent=0,
                                firstLineIndent=0,
                                spaceBefore = 9.5,
                                fontSize=9.5,
                                )
                            ),
                    imageSide='left',
                    )
                )
        story.append(ImageAndFlowables(
                        Image(gif,width=240,height=120),
                        Paragraph('''The concept of an integrated one box solution for advanced voice and
data applications began with the introduction of the IMACS. The
IMACS 200 carries on that tradition with an integrated solution
optimized for smaller port size applications that the IMACS could not
economically address. An array of the most popular interfaces and
features from the IMACS has been bundled into a small 2U chassis
providing the ultimate in ease of installation.''',
                        style=ParagraphStyle(
                                name="base",
                                fontName="Helvetica",
                                leading=12,
                                leftIndent=0,
                                firstLineIndent=0,
                                spaceBefore = 9.5,
                                fontSize=9.5,
                                )
                            ),
                    imageSide='left',
                    )
                )

        story.append(PageBreak())
        story.append(Paragraph('Image larger than the frame',h3))
        story.append(ImageAndFlowables(
                        Image(gif,width=6*110,height=6*44),
                        Paragraph('''The concept of an integrated one box solution for advanced voice and
data applications began with the introduction of the IMACS. The
IMACS 200 carries on that tradition with an integrated solution
optimized for smaller port size applications that the IMACS could not
economically address. An array of the most popular interfaces and
features from the IMACS has been bundled into a small 2U chassis
providing the ultimate in ease of installation.''',
                        style=ParagraphStyle(
                                name="base",
                                fontName="Helvetica",
                                leading=12,
                                leftIndent=0,
                                firstLineIndent=0,
                                spaceBefore = 9.5,
                                fontSize=9.5,
                                )
                            ),
                    imageSide='left',
                    )
                )
        text = '''With this clarification, an important property of these three types of
EC can be defined in such a way as to impose problems of phonemic and
morphological analysis.  Another superficial similarity is the interest
in simulation of behavior, this analysis of a formative as a pair of
sets of features does not readily tolerate a stipulation to place the
constructions into these various categories.  We will bring evidence in
favor of the following thesis:  the earlier discussion of deviance is
not to be considered in determining the extended c-command discussed in
connection with (34).  Another superficial similarity is the interest in
simulation of behavior, relational information may remedy and, at the
same time, eliminate a descriptive fact.  There is also a different
approach to the [unification] problem, the descriptive power of the base
component delimits the traditional practice of grammarians.'''
        gif = os.path.join(testsFolder,'pythonpowered.gif')
        heading = Paragraph('This is a heading',h3)
        story.append(NextPageTemplate('template2'))
        story.append(PageBreak())
        story.append(heading)
        story.append(ImageAndFlowables(Image(gif,width=66,height=81),[Paragraph(text,bt)],imageSide='left',imageRightPadding=10))
        doc = MyDocTemplate(outputfile('test_platypus_imageandflowables.pdf'),showBoundary=1)
        doc.multiBuild(story)

class TwoFrameDocTemplate(BaseDocTemplate):
    "Define a simple document with two frames per page."
    
    def __init__(self, filename, **kw):
        m = 2*cm
        from reportlab.lib import pagesizes
        PAGESIZE = pagesizes.landscape(pagesizes.A4)
        cw, ch = (PAGESIZE[0]-2*m)/2., (PAGESIZE[1]-2*m)
        ch -= 14*cm
        f1 = Frame(m, m+0.5*cm, cw-0.75*cm, ch-1*cm, id='F1', 
            leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0,
            showBoundary=True
        )
        f2 = Frame(cw+2.7*cm, m+0.5*cm, cw-0.75*cm, ch-1*cm, id='F2', 
            leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0,
            showBoundary=True
        )
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('template', [f1, f2])
        self.addPageTemplates(template)


class SplitFrameParagraphTest(unittest.TestCase):
    "Test paragraph split over two frames."

    def test(self):    
        stylesheet = getSampleStyleSheet()
        normal = stylesheet['BodyText']
        normal.fontName = "Helvetica"
        normal.fontSize = 12
        normal.leading = 16
        normal.alignment = TA_JUSTIFY
    
        text = "Bedauerlicherweise ist ein Donaudampfschiffkapit\xc3\xa4n auch <font color='red'>nur</font> <font color='green'>ein</font> Dampfschiffkapit\xc3\xa4n."
        tagFormat = '%s'
        # strange behaviour when using next code line
        # (same for '<a href="http://www.reportlab.org">%s</a>'
        tagFormat = '<font color="red">%s</font>'

        #text = " ".join([tagFormat % w for w in text.split()])
        
        story = [Paragraph((text + " ") * 3, style=normal)]

        from reportlab.lib import pagesizes
        PAGESIZE = pagesizes.landscape(pagesizes.A4)
        
        doc = TwoFrameDocTemplate(outputfile('test_paragraphs_splitframe.pdf'), pagesize=PAGESIZE)
        doc.build(story)

class FragmentTestCase(unittest.TestCase):
    "Test fragmentation of paragraphs."

    def test0(self):
        "Test empty paragraph."

        styleSheet = getSampleStyleSheet()
        B = styleSheet['BodyText']
        text = ''
        P = Paragraph(text, B)
        frags = [f.text for f in P.frags]
        assert frags == []

    def test1(self):
        "Test simple paragraph."

        styleSheet = getSampleStyleSheet()
        B = styleSheet['BodyText']
        text = "X<font name=Courier>Y</font>Z"
        P = Paragraph(text, B)
        frags = [f.text for f in P.frags]
        assert frags == ['X', 'Y', 'Z']

    def test2(self):
        '''test _splitWord'''
        self.assertEqual(_splitWord(u'd\'op\u00e9ration',30,[30],0,'Helvetica',12),[u"d'op\xe9", u'ratio', u'n'])
        self.assertEqual(_splitWord(b'd\'op\xc3\xa9ration',30,[30],0,'Helvetica',12),[u"d'op\xe9", u'ratio', u'n'])

class ULTestCase(unittest.TestCase):
    "Test underlining and overstriking of paragraphs."
    def testUl(self):
        from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, PageBegin
        from reportlab.lib.units import inch
        from reportlab.platypus.flowables import AnchorFlowable
        class MyDocTemplate(BaseDocTemplate):
            _invalidInitArgs = ('pageTemplates',)

            def __init__(self, filename, **kw):
                self.allowSplitting = 0
                kw['showBoundary']=1
                BaseDocTemplate.__init__(self, filename, **kw)
                self.addPageTemplates(
                        [
                        PageTemplate('normal',
                                [Frame(inch, inch, 6.27*inch, 9.69*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))],
                                ),
                        ])

        styleSheet = getSampleStyleSheet()
        normal = ParagraphStyle(name='normal',fontName='Times-Roman',fontSize=12,leading=1.2*12,parent=styleSheet['Normal'])
        normal_sp = ParagraphStyle(name='normal_sp',parent=normal,alignment=TA_JUSTIFY,spaceBefore=12)
        normal_just = ParagraphStyle(name='normal_just',parent=normal,alignment=TA_JUSTIFY)
        normal_right = ParagraphStyle(name='normal_right',parent=normal,alignment=TA_RIGHT)
        normal_center = ParagraphStyle(name='normal_center',parent=normal,alignment=TA_CENTER)
        normal_indent = ParagraphStyle(name='normal_indent',firstLineIndent=0.5*inch,parent=normal)
        normal_indent_lv_2 = ParagraphStyle(name='normal_indent_lv_2',firstLineIndent=1.0*inch,parent=normal)
        texts = ['''Furthermore, a subset of <font size="14">English sentences</font> interesting on quite
independent grounds is not quite equivalent to a stipulation to place
the constructions into these various categories.''',
        '''We will bring evidence in favor of
The following thesis:  most of the methodological work in modern
linguistics can be defined in such a way as to impose problems of
phonemic and morphological analysis.''']
        story =[]
        a = story.append
        a(Paragraph("This should &lt;a href=\"#theEnd\" color=\"blue\"&gt;<a href=\"#theEnd\" color=\"blue\">jump</a>&lt;/a&gt; jump to the end!",style=normal))
        a(XPreformatted("This should &lt;a href=\"#theEnd\" color=\"blue\"&gt;<a href=\"#theEnd\" color=\"blue\">jump</a>&lt;/a&gt; jump to the end!",style=normal))
        a(Paragraph("<a href=\"#theEnd\"><u><font color=\"blue\">ditto</font></u></a>",style=normal))
        a(XPreformatted("<a href=\"#theEnd\"><u><font color=\"blue\">ditto</font></u></a>",style=normal))
        a(Paragraph("This <font color='CMYKColor(0,0.6,0.94,0)'>should</font> &lt;a href=\"#thePenultimate\" color=\"blue\"&gt;<a href=\"#thePenultimate\" color=\"blue\">jump</a>&lt;/a&gt; jump to the penultimate page!",style=normal))
        a(Paragraph("This should &lt;a href=\"#theThird\" color=\"blue\"&gt;<a href=\"#theThird\" color=\"blue\">jump</a>&lt;/a&gt; jump to a justified para!",style=normal))
        a(Paragraph("This should &lt;a href=\"#theFourth\" color=\"blue\"&gt;<a href=\"#theFourth\" color=\"blue\">jump</a>&lt;/a&gt; jump to an indented para!",style=normal))
        for mode in (0,1):
            text0 = texts[0]
            text1 = texts[1]
            if mode:
                text0 = text0.replace('English sentences','<b>English sentences</b>').replace('quite equivalent','<i>quite equivalent</i>')
                text1 = text1.replace('the methodological work','<b>the methodological work</b>').replace('to impose problems','<i>to impose problems</i>')
            for t in ('u','strike'):
                for n in range(6):
                    for s in (normal,normal_center,normal_right,normal_just,normal_indent, normal_indent_lv_2):
                        for autoLeading in ('','min','max'):
                            if n==4 and s==normal_center and t=='strike' and mode==1:
                                a(Paragraph("<font color=green>The second jump at the beginning should come here &lt;a name=\"thePenultimate\"/&gt;<a name=\"thePenultimate\"/>!</font>",style=normal))
                            elif n==4 and s==normal_just and t=='strike' and mode==1:
                                a(Paragraph("<font color=green>The third jump at the beginning should come just below here to a paragraph with just an a tag in it!</font>",style=normal))
                                a(Paragraph("<a name=\"theThird\"/>",style=normal))
                            elif n==4 and s==normal_indent and t=='strike' and mode==1:
                                a(Paragraph("<font color=green>The fourth jump at the beginning should come just below here!</font>",style=normal))
                                a(AnchorFlowable('theFourth'))
                            a(Paragraph('n=%d style=%s(autoLeading=%s) tag=%s'%(n,s.name,autoLeading,t),style=normal_sp))
                            a(Paragraph('<para autoleading="%s">%s<%s>%s</%s>. %s <%s>%s</%s>. %s</para>' % (
                            autoLeading,
                            (s==normal_indent_lv_2 and '<seq id="document" inc="no"/>.<seq id="document_lv_2"/>' or ''),
                            t,' '.join((n+1)*['A']),t,text0,t,' '.join((n+1)*['A']),t,text1),
                            style=s))
        a(Paragraph("The jump at the beginning should come here &lt;a name=\"theEnd\"/&gt;<a name=\"theEnd\"/>!",style=normal))
        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_ul.pdf'))
        doc.build(story)

class AutoLeadingTestCase(unittest.TestCase):
    "Test underlining and overstriking of paragraphs."
    def testAutoLeading(self):
        from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, PageBegin
        from reportlab.lib.units import inch
        from reportlab.platypus.flowables import AnchorFlowable
        class MyDocTemplate(BaseDocTemplate):
            _invalidInitArgs = ('pageTemplates',)

            def __init__(self, filename, **kw):
                self.allowSplitting = 0
                kw['showBoundary']=1
                BaseDocTemplate.__init__(self, filename, **kw)
                self.addPageTemplates(
                        [
                        PageTemplate('normal',
                                [Frame(inch, inch, 6.27*inch, 9.69*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))],
                                ),
                        ])

        from reportlab.lib.testutils import testsFolder
        styleSheet = getSampleStyleSheet()
        normal = ParagraphStyle(name='normal',fontName='Times-Roman',fontSize=12,leading=1.2*12,parent=styleSheet['Normal'])
        normal_sp = ParagraphStyle(name='normal_sp',parent=normal,alignment=TA_JUSTIFY,spaceBefore=12)
        texts = ['''Furthermore, a subset of <font size="14">English sentences</font> interesting on quite
independent grounds is not quite equivalent to a stipulation to place
<font color="blue">the constructions <img src="%(testsFolder)s/../docs/images/testimg.gif"/> into these various categories.</font>'''%dict(testsFolder=testsFolder),
        '''We will bring <font size="18">Ugly Things</font> in favor of
The following thesis:  most of the methodological work in Modern
Linguistics can be <img src="%(testsFolder)s/../docs/images/testimg.gif" valign="baseline" /> defined in such <img src="%(testsFolder)s/../docs/images/testimg.gif" valign="10" /> a way as to impose problems of
phonemic and <u>morphological <img src="%(testsFolder)s/../docs/images/testimg.gif" valign="top"/> </u> analysis.'''%dict(testsFolder=testsFolder)]
        story =[]
        a = story.append
        t = 'u'
        n = 1
        for s in (normal,normal_sp):
            for autoLeading in ('','min','max'):
                a(Paragraph('style=%s(autoLeading=%s)'%(s.name,autoLeading),style=normal_sp))
                a(Paragraph('<para autoleading="%s"><%s>%s</%s>. %s <%s>%s</%s>. %s</para>' % (
                            autoLeading,
                            t,' '.join((n+1)*['A']),t,texts[0],t,' '.join((n+1)*['A']),t,texts[1]),
                            style=s))
        a(Paragraph('''<img src="%(testsFolder)s/../docs/images/testimg.gif" valign="top"/> image is very first thing in the line.'''%dict(testsFolder=testsFolder), style=normal))
        a(Paragraph('some text.... some more.... some text.... some more....', normal))
        a(Paragraph('<img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="0.19in" /> some text <br /> '%dict(testsFolder=testsFolder), normal))
        a(Paragraph('some text.... some more.... some text.... some more....', normal))
        a(Paragraph('<img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="0.19in" /> <br /> '%dict(testsFolder=testsFolder), normal))
        a(Paragraph('some text.... some more.... some text.... some more....', normal))

        #Volker Haas' valign tests
        fmt = '''<font color="red">%(valign)s</font>: Furthermore, a <u>subset</u> <strike>of</strike> <font size="14">English sentences</font> interesting on quite
independent grounds is not quite equivalent to a stipulation to place <img src="%(testsFolder)s/../docs/images/redsquare.png" width="0.5in" height="0.5in" valign="%(valign)s"/>
the constructions into these <u>various</u> categories. We will bring <font size="18">Ugly Things</font> in favor of
The following thesis:  most of the methodological work in Modern
Linguistics can be defined in such a way as to impose problems of
phonemic and <u>morphological</u> <strike>analysis</strike>.'''

        p_style= ParagraphStyle('Normal')
        p_style.autoLeading = 'max'
        for valign in (
                'baseline',
                'sub',
                'super',
                'top',
                'text-top',
                'middle',
                'bottom',
                'text-bottom',
                '0%',
                '2in',
                ):
            a(Paragraph(fmt % dict(valign=valign,testsFolder=testsFolder),p_style))
            a(XPreformatted(fmt % dict(valign=valign,testsFolder=testsFolder),p_style))


        a(Paragraph('<br/><b>Some Paragraph tests of &lt;img width="x%" height="x%"</b>...', normal))
        a(Paragraph('H=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="10%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('H=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="50%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('H=100%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('H=100%% W=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="10%%" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('H=100%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('H=50%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="50%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('<br/><b>Some XPreformatted tests of &lt;img width="x%" height="x%"</b>...', normal))
        a(XPreformatted('H=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="10%%" />'%dict(testsFolder=testsFolder), normal))
        a(XPreformatted('H=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="50%%" />'%dict(testsFolder=testsFolder), normal))
        a(XPreformatted('H=100%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(XPreformatted('H=100%% W=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="10%%" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(XPreformatted('H=100%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="100%%" />'%dict(testsFolder=testsFolder), normal))
        a(XPreformatted('H=50%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="50%%" />'%dict(testsFolder=testsFolder), normal))
        a(Paragraph('<br/><b>Some CJK Paragraph tests of &lt;img width="x%" height="x%"</b>...', normal))
        normalCJK = ParagraphStyle('normalCJK', parent=normal, wordWrap = 'CJK')
        a(Paragraph('H=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="10%%" />'%dict(testsFolder=testsFolder), normalCJK))
        a(Paragraph('H=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="50%%" />'%dict(testsFolder=testsFolder), normalCJK))
        a(Paragraph('H=100%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="0.57in" height="100%%" />'%dict(testsFolder=testsFolder), normalCJK))
        a(Paragraph('H=100%% W=10%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="10%%" height="100%%" />'%dict(testsFolder=testsFolder), normalCJK))
        a(Paragraph('H=100%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="100%%" />'%dict(testsFolder=testsFolder), normalCJK))
        a(Paragraph('H=50%% W=50%% <img src="%(testsFolder)s/../docs/images/testimg.gif" width="50%%" height="50%%" />'%dict(testsFolder=testsFolder), normalCJK))
        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_autoleading.pdf'))
        doc.build(story)

class JustifyTestCase(unittest.TestCase):
    "Test justification of paragraphs."
    def testUl(self):
        from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, PageBegin
        from reportlab.lib.units import inch
        class MyDocTemplate(BaseDocTemplate):
            _invalidInitArgs = ('pageTemplates',)

            def __init__(self, filename, **kw):
                self.allowSplitting = 0
                BaseDocTemplate.__init__(self, filename, **kw)
                self.addPageTemplates(
                        [
                        PageTemplate('normal',
                                [Frame(inch, inch, 6.27*inch, 9.69*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))],
                                ),
                        ])

        styleSheet = getSampleStyleSheet()
        normal = ParagraphStyle(name='normal',fontName='Times-Roman',fontSize=12,leading=1.2*12,parent=styleSheet['Normal'])
        normal_just = ParagraphStyle(name='normal_just',parent=normal,alignment=TA_JUSTIFY,spaceAfter=12)
        text0 = '''Furthermore, a subset of English sentences interesting on quite
independent grounds is not quite equivalent to a stipulation to place
the constructions into these various categories. We will bring evidence in favor of
The following thesis:  most of the methodological work in modern
linguistics can be defined in such a way as to impose problems of
phonemic and morphological analysis.'''
        story =[]
        a = story.append
        for mode in (0,1,2,3,4):
            text = text0
            if mode==1:
                text = text.replace('English sentences','<b>English sentences</b>').replace('quite equivalent','<i>quite equivalent</i>')
                text = text.replace('the methodological work','<b>the methodological work</b>').replace('to impose problems','<i>to impose problems</i>')
                a(Paragraph('Justified paragraph in normal/bold/italic font',style=normal))
            elif mode==2:
                text = '<b>%s</b>' % text
                a(Paragraph('Justified paragraph in bold font',style=normal))
            elif mode==3:
                text = '<i>%s</i>' % text
                a(Paragraph('Justified paragraph in italic font',style=normal))
            elif mode==4:
                text = text.replace('English ','English&nbsp;').replace('quite ','quite&nbsp;')
                text = text.replace(' methodological','&nbsp;methodological').replace(' impose','&nbsp;impose')
                a(Paragraph('Justified paragraph in normal font &amp; some hard spaces',style=normal))
            else:
                a(Paragraph('Justified paragraph in normal font',style=normal))

            a(Paragraph(text,style=normal_just))
        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_just.pdf'))
        doc.build(story)

    def testAutoPageTemplate(self):
        from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, PageBegin
        from reportlab.lib.units import inch
        class onPage:
            def __init__(self,label):
                self.label = label
            def __call__(self,canv,doc):
                canv.drawString(72,72,'This is pageTemplate(%s)' % (self.label,))
        class MyDocTemplate(BaseDocTemplate):
            _invalidInitArgs = ('pageTemplates',)

            def __init__(self, filename, **kw):
                self.allowSplitting = 0
                BaseDocTemplate.__init__(self, filename, **kw)
                self.addPageTemplates(
                        [
                        PageTemplate('normal',
                                [Frame(inch, inch, 6.27*inch, 9.69*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))],
                                onPage = onPage('normal'),
                                ),
                        PageTemplate('auto',
                                [Frame(inch, inch, 6.27*inch, 9.69*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))],
                                onPage = onPage('auto'),
                                autoNextPageTemplate = 'autoFollow',
                                ),
                        PageTemplate('autoFollow',
                                [Frame(inch, inch, 6.27*inch, 9.69*inch, id='first',topPadding=0,rightPadding=0,leftPadding=0,bottomPadding=0,showBoundary=ShowBoundaryValue(color="red"))],
                                onPage = onPage('autoFollow'),
                                ),
                        ])
        styleSheet = getSampleStyleSheet()
        normal = ParagraphStyle(name='normal',fontName='Times-Roman',fontSize=12,leading=1.2*12,parent=styleSheet['Normal'])
        story =[]
        a = story.append
        a(Paragraph('should be on page template normal', normal))
        a(NextPageTemplate('auto'))
        a(PageBreak())
        a(Paragraph('should be on page template auto', normal))
        a(PageBreak())
        a(DocAssert('doc.pageTemplate.id=="autoFollow"','expected doc.pageTemplate.id=="autoFollow"'))
        a(Paragraph('should be on page template autoFollow 1', normal))
        a(PageBreak())
        a(Paragraph('should be on page template autoFollow 2', normal))
        doc = MyDocTemplate(outputfile('test_platypus_paragraphs_AutoNextPageTemplate.pdf'))
        doc.build(story)

#noruntests
def makeSuite():
    return makeSuiteForClasses(ParagraphCorners,SplitFrameParagraphTest,FragmentTestCase, ParagraphSplitTestCase, ULTestCase, JustifyTestCase,
            AutoLeadingTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
