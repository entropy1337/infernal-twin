#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
# tests some paragraph styles
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest
from reportlab.platypus import Paragraph, SimpleDocTemplate, XBox, Indenter, XPreformatted, PageBreak, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.abag import ABag
from reportlab.lib.colors import red, black, navy, white, green
from reportlab.lib.randomtext import randomText
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.rl_config import defaultPageSize, rtlSupport
from reportlab.pdfbase import ttfonts
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping, tt2ps

(PAGE_WIDTH, PAGE_HEIGHT) = defaultPageSize

def myFirstPage(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(red)
    canvas.setLineWidth(5)
    canvas.line(66,72,66,PAGE_HEIGHT-72)
    canvas.setFont('Times-Bold',24)
    canvas.drawString(108, PAGE_HEIGHT-54, "TESTING PARAGRAPH STYLES")
    canvas.setFont('Times-Roman',12)
    canvas.drawString(4 * inch, 0.75 * inch, "First Page")
    canvas.restoreState()

def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(red)
    canvas.setLineWidth(5)
    canvas.line(66,72,66,PAGE_HEIGHT-72)
    canvas.setFont('Times-Roman',12)
    canvas.drawString(4 * inch, 0.75 * inch, "Page %d" % doc.page)
    canvas.restoreState()

def getAFont():
    '''register a font that supports most Unicode characters'''
    I = []
    font_name = 'DejaVuSans'
    I.append([(font_name, 0, 0, font_name),
                 (font_name, 1, 0, font_name + '-Bold'),
                 (font_name, 0, 1, font_name + '-Oblique'),
                 (font_name, 1, 1, font_name + '-BoldOblique'),
                 ])
    font_name = 'FreeSerif'
    I.append([(font_name, 0, 0, font_name),
                 (font_name, 1, 0, font_name + 'Bold'),
                 (font_name, 0, 1, font_name + 'Italic'),
                 (font_name, 1, 1, font_name + 'BoldItalic'),
                 ])
    for info in I:
        n = 0
        for font in info:
            fontName = font[3]
            try:
                pdfmetrics.registerFont(ttfonts.TTFont(fontName,fontName + '.ttf'))
                addMapping(*font)
                n += 1
            except:
                pass
        if n==4: return font[0]
    raise ValueError('could not find suitable font')

class ParagraphTestCase(unittest.TestCase):
    "Test Paragraph class (eyeball-test)."

    def test0(self):
        """Test...

        The story should contain...

        Features to be visually confirmed by a human being are:

            1. ...
            2. ...
            3. ...
        """

        story = []
        SA = story.append

        #need a style
        styNormal = ParagraphStyle('normal')
        styGreen = ParagraphStyle('green',parent=styNormal,textColor=green)

        styDots = ParagraphStyle('styDots',parent=styNormal,endDots='.')
        styDots1 = ParagraphStyle('styDots1',parent=styNormal,endDots=ABag(text=' -',dy=2,textColor='red'))
        styDotsR = ParagraphStyle('styDotsR',parent=styNormal,alignment=TA_RIGHT,endDots=' +')
        styDotsC = ParagraphStyle('styDotsC',parent=styNormal,alignment=TA_CENTER,endDots=' *')
        styDotsJ = ParagraphStyle('styDotsJ',parent=styNormal,alignment=TA_JUSTIFY,endDots=' =')

        istyDots = ParagraphStyle('istyDots',parent=styNormal,firstLineIndent=12,leftIndent=6,endDots='.')
        istyDots1 = ParagraphStyle('istyDots1',parent=styNormal,firstLineIndent=12,leftIndent=6,endDots=ABag(text=' -',dy=2,textColor='red'))
        istyDotsR = ParagraphStyle('istyDotsR',parent=styNormal,firstLineIndent=12,leftIndent=6,alignment=TA_RIGHT,endDots=' +')
        istyDotsC = ParagraphStyle('istyDotsC',parent=styNormal,firstLineIndent=12,leftIndent=6,alignment=TA_CENTER,endDots=' *')
        istyDotsJ = ParagraphStyle('istyDotsJ',parent=styNormal,firstLineIndent=12,leftIndent=6,alignment=TA_JUSTIFY,endDots=' =')

        styNormalCJK = ParagraphStyle('normal',wordWrap='CJK')
        styDotsCJK = ParagraphStyle('styDots',parent=styNormalCJK,endDots='.')
        styDots1CJK = ParagraphStyle('styDots1',parent=styNormalCJK,endDots=ABag(text=' -',dy=2,textColor='red'))
        styDotsRCJK = ParagraphStyle('styDotsR',parent=styNormalCJK,alignment=TA_RIGHT,endDots=' +')
        styDotsCCJK = ParagraphStyle('styDotsC',parent=styNormalCJK,alignment=TA_CENTER,endDots=' *')
        styDotsJCJK = ParagraphStyle('styDotsJ',parent=styNormalCJK,alignment=TA_JUSTIFY,endDots=' =')

        istyDotsCJK = ParagraphStyle('istyDots',parent=styNormalCJK,firstLineIndent=12,leftIndent=6,endDots='.')
        istyDots1CJK = ParagraphStyle('istyDots1',parent=styNormalCJK,firstLineIndent=12,leftIndent=6,endDots=ABag(text=' -',dy=2,textColor='red'))
        istyDotsRCJK = ParagraphStyle('istyDotsR',parent=styNormalCJK,firstLineIndent=12,leftIndent=6,alignment=TA_RIGHT,endDots=' +')
        istyDotsCCJK = ParagraphStyle('istyDotsC',parent=styNormalCJK,firstLineIndent=12,leftIndent=6,alignment=TA_CENTER,endDots=' *')
        istyDotsJCJK = ParagraphStyle('istyDotsJ',parent=styNormalCJK,firstLineIndent=12,leftIndent=6,alignment=TA_JUSTIFY,endDots=' =')
        

        # some to test
        stySpaced = ParagraphStyle('spaced',
                                   parent=styNormal,
                                   spaceBefore=12,
                                   spaceAfter=12)

        SA(Paragraph("This is a normal paragraph. "+ randomText(), styNormal))
        SA(Paragraph("There follows a paragraph with only \"&lt;br/&gt;\"", styNormal))
        SA(Paragraph("<br/>", styNormal))
        SA(Paragraph("This has 12 points space before and after, set in the style. " + randomText(), stySpaced))
        SA(Paragraph("This is normal. " + randomText(), styNormal))
        SA(Paragraph("""<para spacebefore="12" spaceafter="12">
            This has 12 points space before and after, set inline with
            XML tag.  It works too.""" + randomText() + "</para>",
                      styNormal))

        SA(Paragraph("This is normal. " + randomText(), styNormal))

        styBackground = ParagraphStyle('MyTitle',
                                       fontName='Helvetica-Bold',
                                       fontSize=24,
                                       leading=28,
                                       textColor=white,
                                       backColor=navy)
        SA(Paragraph("This is a title with a background. ", styBackground))
        SA(Paragraph("""<para backcolor="pink">This got a background from the para tag</para>""", styNormal))
        SA(Paragraph("""<para>\n\tThis has newlines and tabs on the front but inside the para tag</para>""", styNormal))
        SA(Paragraph("""<para>  This has spaces on the front but inside the para tag</para>""", styNormal))
        SA(Paragraph("""\n\tThis has newlines and tabs on the front but no para tag""", styNormal))
        SA(Paragraph("""  This has spaces on the front but no para tag""", styNormal))
        SA(Paragraph("""This has <font color=blue backcolor=pink>blue text with pink background</font> here.""", styNormal))
        SA(Paragraph("""<span color=blue backcolor=pink>&nbsp;Nothing but blue text with pink background.&nbsp;</span>""", styNormal))
        SA(Paragraph("""This has <i>italic text</i> here.""", styNormal))
        SA(Paragraph("""This has <b>bold text</b> here.""", styNormal))
        SA(Paragraph("""This has <u>underlined text</u> here.""", styNormal))
        SA(Paragraph("""This has <font color=blue><u>blue and <font color=red>red</font> underlined text</u></font> here.""", styNormal))
        SA(Paragraph("""<u>green underlining</u>""", styGreen))
        SA(Paragraph("""<u>green <font size="+4"><i>underlining</i></font></u>""", styGreen))
        SA(Paragraph("""This has m<super>2</super> a superscript.""", styNormal))
        SA(Paragraph("""This has m<sub>2</sub> a subscript. Like H<sub>2</sub>O!""", styNormal))
        SA(Paragraph("""This has a font change to <font name=Helvetica>Helvetica</font>.""", styNormal))
        #This one fails:
        #SA(Paragraph("""This has a font change to <font name=Helvetica-Oblique>Helvetica-Oblique</font>.""", styNormal))
        SA(Paragraph("""This has a font change to <font name=Helvetica><i>Helvetica in italics</i></font>.""", styNormal))

        SA(Paragraph('''This one uses upper case tags and has set caseSensitive=0: Here comes <FONT FACE="Helvetica" SIZE="14pt">Helvetica 14</FONT> with <STRONG>strong</STRONG> <EM>emphasis</EM>.''', styNormal, caseSensitive=0))
        SA(Paragraph('''The same as before, but has set not set caseSensitive, thus the tags are ignored: Here comes <FONT FACE="Helvetica" SIZE="14pt">Helvetica 14</FONT> with <STRONG>strong</STRONG> <EM>emphasis</EM>.''', styNormal))
        SA(Paragraph('''This one uses fonts with size "14pt" and also uses the em and strong tags: Here comes <font face="Helvetica" size="14pt">Helvetica 14</font> with <Strong>strong</Strong> <em>emphasis</em>.''', styNormal, caseSensitive=0))
        SA(Paragraph('''This uses a font size of 3cm: Here comes <font face="Courier" size="3cm">Courier 3cm</font> and normal again.''', styNormal, caseSensitive=0))
        SA(Paragraph('''This is just a very long silly text to see if the <FONT face="Courier">caseSensitive</FONT> flag also works if the paragraph is <EM>very</EM> long. '''*20, styNormal, caseSensitive=0))

        SA(Indenter("1cm"))
        SA(Paragraph("<para><bullet bulletIndent='-0.7cm' bulletOffsetY='2'>1.1</bullet>sample bullet default anchor</para>", styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-0.7cm' bulletOffsetY='2'>1.22</bullet>sample bullet default anchor</para>", styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-0.7cm' bulletOffsetY='2' anchor='start'>1.1</bullet>sample bullet start align</para>", styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-0.7cm' bulletOffsetY='2' anchor='start'>1.22</bullet>sample bullet start align</para>", styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-0.7cm' bulletOffsetY='2' anchor='middle'>1.1</bullet>sample bullet middle align</para>", styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-0.7cm' bulletOffsetY='2' anchor='middle'>1.22</bullet>sample bullet middle align</para>", styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-0.7cm' bulletOffsetY='2' anchor='end'>1.1</bullet>sample bullet end align</para>", styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-0.7cm' bulletOffsetY='2' anchor='end'>1.22</bullet>sample bullet end align</para>", styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-0.7cm' bulletOffsetY='2' anchor='numeric'>1.1</bullet>sample bullet numeric align</para>", styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-0.7cm' bulletOffsetY='2' anchor='numeric'>1.22</bullet>sample bullet numeric align</para>", styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-0.7cm' bulletOffsetY='2' anchor='numeric'><span color='red'>1</span><span color='green'>.</span><span color='blue'>3</span></bullet>sample bullet numeric align</para>", styNormal))

        SA(Paragraph("<para><bullet bulletIndent='-1cm' bulletOffsetY='2'><seq id='s0'/>)</bullet>Indented list bulletOffsetY=2. %s</para>" % randomText(), styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Indenter("1cm"))
        SA(XPreformatted("<para leftIndent='0.5cm' backcolor=pink><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list.</para>", styNormal))
        SA(XPreformatted("<para leftIndent='0.5cm' backcolor=palegreen><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list.</para>", styNormal))
        SA(Indenter("-1cm"))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Indenter("-1cm"))
        SA(Paragraph("<para>Indented list using seqChain/Format<seqChain order='s0 s1 s2 s3 s4'/><seqReset id='s0'/><seqFormat id='s0' value='1'/><seqFormat id='s1' value='a'/><seqFormat id='s2' value='i'/><seqFormat id='s3' value='A'/><seqFormat id='s4' value='I'/></para>", stySpaced))
        SA(Indenter("1cm"))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Indenter("1cm"))
        SA(XPreformatted("<para backcolor=pink boffsety='-3'><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list bulletOffsetY=-3.</para>", styNormal))
        SA(XPreformatted("<para backcolor=pink><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list.</para>", styNormal))
        SA(Indenter("-1cm"))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Indenter("1cm"))
        SA(XPreformatted("<para backcolor=palegreen><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list.</para>", styNormal))
        SA(Indenter("1cm"))
        SA(XPreformatted("<para><bullet bulletIndent='-1cm'><seq id='s2'/>)</bullet>Indented list. line1</para>", styNormal))
        SA(XPreformatted("<para><bullet bulletIndent='-1cm'><seq id='s2'/>)</bullet>Indented list. line2</para>", styNormal))
        SA(Indenter("-1cm"))
        SA(XPreformatted("<para backcolor=palegreen><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list.</para>", styNormal))
        SA(Indenter("-1cm"))
        SA(Indenter("-1cm"))
        
        for i in range(2):
            SA(PageBreak())
            SA(Paragraph('''%s dotted paragraphs''' % (i and 'CJK' or 'Normal'), styNormal))
            SA(Paragraph('''Simple paragraph with dots''', i and styDotsCJK or styDots))
            SA(Paragraph('''Simple indented paragraph with dots''', i and istyDotsCJK or istyDots))
            SA(Paragraph('''Simple centred paragraph with stars''', i and styDotsCCJK or styDotsC))
            SA(Paragraph('''Simple centred indented paragraph with stars''', i and istyDotsCCJK or istyDotsC))
            SA(Paragraph('''Simple right justified paragraph with pluses, but no pluses''', i and styDotsRCJK or styDotsR))
            SA(Paragraph('''Simple right justified indented paragraph with pluses, but no pluses''', i and istyDotsRCJK or istyDotsR))
            SA(Paragraph('''Simple justified paragraph with equals''', i and styDotsJCJK or styDotsJ))
            SA(Paragraph('''Simple justified indented paragraph with equals''', i and istyDotsJCJK or istyDotsJ))
            SA(Paragraph('''A longer simple paragraph with dots''', i and styDotsCJK or styDots))
            SA(Paragraph('''A longer simple indented paragraph with dots''', i and istyDotsCJK or istyDots))
            SA(Paragraph('A very much' +50*' longer'+' simple paragraph with dots', i and styDotsCJK or styDots))
            SA(Paragraph('A very much' +50*' longer'+' simple indented paragraph with dots', i and istyDotsCJK or istyDots))
            SA(Paragraph('A very much' +50*' longer'+' centred simple paragraph with stars', i and styDotsCCJK or styDotsC))
            SA(Paragraph('A very much' +50*' longer'+' centred simple indented paragraph with stars', i and istyDotsCCJK or istyDotsC))
            SA(Paragraph('A very much' +50*' longer'+' right justified simple paragraph with pluses, but no pluses', i and styDotsRCJK or styDotsR))
            SA(Paragraph('A very much' +50*' longer'+' right justified simple indented paragraph with pluses, but no pluses', i and istyDotsRCJK or istyDotsR))
            SA(Paragraph('A very much' +50*' longer'+' justified simple paragraph with equals', i and styDotsJCJK or styDotsJ))
            SA(Paragraph('A very much' +50*' longer'+' justified simple indented paragraph with equals', i and istyDotsJCJK or istyDotsJ))
            SA(Paragraph('''Simple paragraph with dashes that have a dy and a textColor.''', i and styDots1CJK or styDots1))
            SA(Paragraph('''Simple indented paragraph with dashes that have a dy and a textColor.''', i and istyDots1CJK or istyDots1))
            SA(Paragraph('''Complex <font color="green">paragraph</font> with dots''', i and styDotsCJK or styDots))
            SA(Paragraph('''Complex <font color="green">indented paragraph</font> with dots''', i and istyDotsCJK or istyDots))
            SA(Paragraph('''Complex centred <font color="green">paragraph</font> with stars''', i and styDotsCCJK or styDotsC))
            SA(Paragraph('''Complex centred <font color="green">indented paragraph</font> with stars''', i and istyDotsCCJK or istyDotsC))
            SA(Paragraph('''Complex right justfied <font color="green">paragraph</font> with pluses, but no pluses''', i and styDotsRCJK or styDotsR))
            SA(Paragraph('''Complex right justfied <font color="green">indented paragraph</font> with pluses, but no pluses''', i and istyDotsRCJK or istyDotsR))
            SA(Paragraph('''Complex justfied <font color="green">paragraph</font> with equals''', i and styDotsJCJK or styDotsJ))
            SA(Paragraph('''Complex justfied <font color="green">indented paragraph</font> with equals''', i and istyDotsJCJK or istyDotsJ))
            SA(Paragraph('''A longer complex <font color="green">paragraph</font> with dots''', i and styDotsCJK or styDots))
            SA(Paragraph('''A longer complex <font color="green">indented paragraph</font> with dots''', i and istyDotsCJK or istyDots))
            SA(Paragraph('A very much' +50*' longer'+' complex <font color="green">paragraph</font> with dots', i and styDotsCJK or styDots))
            SA(Paragraph('A very much' +50*' longer'+' complex <font color="green">indented paragraph</font> with dots', i and istyDotsCJK or istyDots))
            SA(Paragraph('''Complex <font color="green">paragraph</font> with dashes that have a dy and a textColor.''', i and styDots1CJK or styDots1))
            SA(Paragraph('''Complex <font color="green">indented paragraph</font> with dashes that have a dy and a textColor.''', i and istyDots1CJK or istyDots1))
            SA(Paragraph('A very much' +50*' longer'+' centred complex <font color="green">paragraph</font> with stars', i and styDotsCCJK or styDotsC))
            SA(Paragraph('A very much' +50*' longer'+' centred complex <font color="green">indented paragraph</font> with stars', i and istyDotsCCJK or istyDotsC))
            SA(Paragraph('A very much' +50*' longer'+' right justified <font color="green">complex</font> paragraph with pluses, but no pluses', i and styDotsRCJK or styDotsR))
            SA(Paragraph('A very much' +50*' longer'+' right justified <font color="green">complex</font> indented paragraph with pluses, but no pluses', i and istyDotsRCJK or istyDotsR))
            SA(Paragraph('A very much' +50*' longer'+' justified complex <font color="green">paragraph</font> with equals', i and styDotsJCJK or styDotsJ))
            SA(Paragraph('A very much' +50*' longer'+' justified complex <font color="green">indented paragraph</font> with equals', i and istyDotsJCJK or istyDotsJ))

        template = SimpleDocTemplate(outputfile('test_paragraphs.pdf'),
                                     showBoundary=1)
        template.build(story,
            onFirstPage=myFirstPage, onLaterPages=myLaterPages)
    
    if rtlSupport:
        def testBidi(self):
            fontName = getAFont()

            # create styles based on the registered font
            stySTD = ParagraphStyle('STD', fontName = fontName)
            styRJ = ParagraphStyle('RJ', parent=stySTD, alignment=TA_RIGHT)
            styLTR = ParagraphStyle('LTR', parent=stySTD, wordWrap='LTR')
            styRTL = ParagraphStyle('RTL', parent = stySTD, alignment = TA_RIGHT,
                                    wordWrap = 'RTL', spaceAfter = 12)

            # strings for testing Normal & LTR styles
            ltrStrings = [# English followed by Arabic.
                          b'English followed by \xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a.',
                          # English with Arabic in the middle
                          b'English with \xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a in the middle.',
                          # English symbols (!@#$%^&*) Arabic
                          b'English symbols (!@#$%^&*) \xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a.',
                          # ((testing integers in LTR)) 
                          b'123 LTR 123 Integers 123.',
                          # ((testing decimals in LTR))
                          b'456.78 LTR 456.78 Decimals 456.78.',
                          # Long English text with RTL script in the middle, splitting over multiple lines
                          b'Long \xd8\xb7\xd9\x88\xd9\x8a\xd9\x84 English text'
                              b' \xd9\x86\xd8\xb5 \xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a with RTL script'
                              b' \xd9\x83\xd8\xaa\xd8\xa7\xd8\xa8\xd8\xa9 \xd9\x85\xd9\x86'
                              b' \xd8\xa7\xd9\x84\xd9\x8a\xd9\x85\xd9\x8a\xd9\x86 \xd8\xa5\xd9\x84\xd9\x89'
                              b' \xd8\xa7\xd9\x84\xd9\x8a\xd8\xb3\xd8\xa7\xd8\xb1 in the middle,'
                              b' \xd9\x81\xd9\x8a \xd8\xa7\xd9\x84\xd9\x88\xd8\xb3\xd8\xb7\xd8\x8c'
                              b' splitting \xd9\x85\xd9\x82\xd8\xb3\xd9\x85 over \xd8\xb9\xd9\x84\xd9\x89'
                              b' multiple lines \xd8\xb9\xd8\xaf\xd8\xa9 \xd8\xb3\xd8\xb7\xd9\x88\xd8\xb1.',
                          ]

            # strings for testing RTL
            rtlStrings = [# Arabic followed by English
                          b'\xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a \xd9\x85\xd8\xaa\xd8\xa8\xd9\x88\xd8\xb9'
                              b' \xd8\xa8\xd9\x80 English.',
                          # Arabic with English in the middle
                          b'\xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a \xd9\x85\xd8\xb9 English \xd9\x81\xd9\x8a'
                              b' \xd8\xa7\xd9\x84\xd9\x85\xd9\x86\xd8\xaa\xd8\xb5\xd9\x81.',
                          # Arabic symbols (!@##$%^&*) English
                          b'\xd8\xb1\xd9\x85\xd9\x88\xd8\xb2 \xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a\xd8\xa9'
                              b' (!@#$%^&*) English.',
                          # 123 from right to left 123 integer numbers 123. ((testing integers in RTL))
                          b'123 \xd9\x85\xd9\x86 \xd8\xa7\xd9\x84\xd9\x8a\xd9\x85\xd9\x8a\xd9\x86'
                              b' \xd8\xa5\xd9\x84\xd9\x89 \xd8\xa7\xd9\x84\xd9\x8a\xd8\xb3\xd8\xa7\xd8\xb1'
                              b' 123 \xd8\xa3\xd8\xb1\xd9\x82\xd8\xa7\xd9\x85'
                              b' \xd8\xb5\xd8\xad\xd9\x8a\xd8\xad\xd8\xa9 123.',
                          # 456.78 from right to left 456.78 decimal numbers 456.78. ((testing decimals in RTL))
                          b'456.78 \xd9\x85\xd9\x86 \xd8\xa7\xd9\x84\xd9\x8a\xd9\x85\xd9\x8a\xd9\x86'
                              b' \xd8\xa5\xd9\x84\xd9\x89 \xd8\xa7\xd9\x84\xd9\x8a\xd8\xb3\xd8\xa7\xd8\xb1'
                              b' 456.78 \xd8\xa3\xd8\xb1\xd9\x82\xd8\xa7\xd9\x85'
                              b' \xd8\xb9\xd8\xb4\xd8\xb1\xd9\x8a\xd8\xa9 456.78.',
                          # Long Arabic text with LTR text in the middle, splitting over multiple lines
                          b'\xd9\x86\xd8\xb5 \xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a \xd8\xb7\xd9\x88\xd9\x8a\xd9\x84'
                              b' Long Arabic text \xd9\x85\xd8\xb9 with \xd9\x83\xd8\xaa\xd8\xa7\xd8\xa8\xd8\xa9'
                              b' \xd9\x85\xd9\x86 \xd8\xa7\xd9\x84\xd9\x8a\xd8\xb3\xd8\xa7\xd8\xb1'
                              b' \xd8\xa5\xd9\x84\xd9\x89 \xd8\xa7\xd9\x84\xd9\x8a\xd9\x85\xd9\x8a\xd9\x86'
                              b' LTR script \xd9\x81\xd9\x8a \xd8\xa7\xd9\x84\xd9\x88\xd8\xb3\xd8\xb7\xd8\x8c'
                              b' in the middle, \xd9\x85\xd9\x82\xd8\xb3\xd9\x85 splitted'
                              b' \xd8\xb9\xd9\x84\xd9\x89 over \xd8\xb9\xd8\xaf\xd8\xa9'
                              b' \xd8\xb3\xd8\xb7\xd9\x88\xd8\xb1 multiple lines.'
                          ]

            assert len(ltrStrings) == len(rtlStrings)
            n = len(ltrStrings)
            
            # create a store to be printed
            story = []
            
            story.append(Paragraph("<b><i>Following pairs of left justified texts have style.wordWrap=None &amp; 'LTR'.</i></b><br/>",stySTD))
            # write every LTR string and its corresponding RTL string to be matched.
            for i in xrange(n):
                story.append(Paragraph(ltrStrings[i], stySTD))
                story.append(Paragraph(ltrStrings[i], styLTR))

            story.append(Paragraph("<br/><b><i>Following pairs of right justfied texts have style.wordWrap=None &amp; 'RTL'.</i></b><br/>",stySTD))
            for i in xrange(n):
                story.append(Paragraph(rtlStrings[i], styRJ))
                story.append(Paragraph(rtlStrings[i], styRTL))

            story.append(Paragraph("<b><i><br/>Following texts have style.wordWrap='RTL'</i></b>",stySTD))
            # a few additional scripts for testing.
            story.append(
                Paragraph(b'\xd9\x87\xd8\xb0\xd9\x87 \xd9\x81\xd9\x82\xd8\xb1\xd8\xa9'
                              b' \xd8\xb9\xd8\xa7\xd8\xaf\xd9\x8a\xd8\xa9. ', styRTL))
            story.append(
                Paragraph(b'\xd9\x87\xd8\xb0\xd9\x87 \xd8\xa7\xd9\x84\xd9\x81\xd9\x82\xd8\xb1\xd8\xa9'
                              b' \xd9\x84\xd8\xaf\xd9\x8a\xd9\x87\xd8\xa7 12'
                              b' \xd9\x86\xd9\x82\xd8\xb7\xd8\xa9 \xd9\x82\xd8\xa8\xd9\x84\xd9\x87\xd8\xa7'
                              b' \xd9\x88\xd8\xa8\xd8\xb9\xd8\xaf\xd9\x87\xd8\xa7. ', styRTL))
            story.append(
                Paragraph(b'<para spacebefore="12" spaceafter="12">'
                              b'\xd9\x87\xd8\xb0\xd9\x87 \xd8\xa7\xd9\x84\xd9\x81\xd9\x82\xd8\xb1\xd8\xa9'
                              b' \xd9\x84\xd8\xaf\xd9\x8a\xd9\x87\xd8\xa7 12 \xd9\x86\xd9\x82\xd8\xb7\xd8\xa9'
                              b' \xd9\x82\xd8\xa8\xd9\x84\xd9\x87\xd8\xa7'
                              b' \xd9\x88\xd8\xa8\xd8\xb9\xd8\xaf\xd9\x87\xd8\xa7\xd8\x8c'
                              b' \xd9\x85\xd8\xad\xd8\xaf\xd8\xaf\xd8\xa9 \xd8\xa8\xd9\x80 XML.'
                              b' \xd8\xa5\xd9\x86\xd9\x87\xd8\xa7 \xd8\xaa\xd8\xb9\xd9\x85\xd9\x84'
                              b' \xd8\xa3\xd9\x8a\xd8\xb6\xd8\xa7! \xd9\x80.'
                              b'</para>',
                          styRTL))

            # TODO: add more RTL scripts to the test (Farsi, Hebrew, etc.)

            template = SimpleDocTemplate(outputfile('test_paragraphs_bidi.pdf'))
            template.build(story)

        def testRTLBullets(self):
            try:
                import mwlib.ext
            except ImportError:
                pass

            font_name = getAFont()
            doc = SimpleDocTemplate(outputfile('test_rtl_bullets.pdf'),showBoundary=True)
            p_style = ParagraphStyle('default')
            p_style.leftIndent = 0
            p_style.rightIndent = 0

            list_styles=[ParagraphStyle('list%d' % n) for n in range(3)]
            all_styles = list_styles[:]
            all_styles.append(p_style)

            direction='rtl'

            for s in all_styles:
                s.fontSize = 15
                s.leading = s.fontSize*1.2
                s.fontName = font_name
                if direction=='rtl':
                    s.wordWrap = 'RTL'
                    s.alignment = TA_RIGHT
                else:
                    s.alignment = TA_JUSTIFY

            indent_amount = 20

            for list_lvl, list_style in enumerate(list_styles):
                list_lvl += 1
                list_style.bulletIndent = indent_amount*(list_lvl-1)

                if direction=='rtl':
                    list_style.rightIndent = indent_amount*list_lvl
                else:
                    list_style.leftIndent = indent_amount*list_lvl

            elements =[]

            TEXTS=[
                    b'\xd7\xa9\xd7\xa8 \xd7\x94\xd7\x91\xd7\x99\xd7\x98\xd7\x97\xd7\x95\xd7\x9f, \xd7\x94\xd7\x95\xd7\x90 \xd7\x94\xd7\xa9\xd7\xa8 \xd7\x94\xd7\x90\xd7\x97\xd7\xa8\xd7\x90\xd7\x99 \xd7\xa2\xd7\x9c \xd7\x9e\xd7\xa9\xd7\xa8\xd7\x93 \xd7\x96\xd7\x94. \xd7\xaa\xd7\xa4\xd7\xa7\xd7\x99\xd7\x93 \xd7\x96\xd7\x94 \xd7\xa0\xd7\x97\xd7\xa9\xd7\x91 \xd7\x9c\xd7\x90\xd7\x97\xd7\x93 \xd7\x94\xd7\xaa\xd7\xa4\xd7\xa7\xd7\x99\xd7\x93\xd7\x99\xd7\x9d \xd7\x94\xd7\x91\xd7\x9b\xd7\x99\xd7\xa8\xd7\x99\xd7\x9d \xd7\x91\xd7\x9e\xd7\x9e\xd7\xa9\xd7\x9c\xd7\x94. \xd7\x9c\xd7\xa9\xd7\xa8 \xd7\x94\xd7\x91\xd7\x99\xd7\x98\xd7\x97\xd7\x95\xd7\x9f \xd7\x9e\xd7\xaa\xd7\x9e\xd7\xa0\xd7\x94 \xd7\x9c\xd7\xa8\xd7\x95\xd7\x91 \xd7\x92\xd7\x9d \xd7\xa1\xd7\x92\xd7\x9f \xd7\xa9\xd7\xa8.',
                    b'\xd7\xa9\xd7\xa8 \xd7\x94\xd7\x91\xd7\x99\xd7\x98\xd7\x97\xd7\x95\xd7\x9f, <b>\xd7\x94\xd7\x95\xd7\x90 \xd7\x94\xd7\xa9\xd7\xa8 \xd7\x94\xd7\x90\xd7\x97\xd7\xa8\xd7\x90\xd7\x99 \xd7\xa2\xd7\x9c \xd7\x9e\xd7\xa9\xd7\xa8\xd7\x93 \xd7\x96\xd7\x94.</b> \xd7\xaa\xd7\xa4\xd7\xa7\xd7\x99\xd7\x93 \xd7\x96\xd7\x94 <i>\xd7\xa0\xd7\x97\xd7\xa9\xd7\x91 \xd7\x9c\xd7\x90\xd7\x97\xd7\x93</i> \xd7\x94\xd7\xaa\xd7\xa4\xd7\xa7\xd7\x99\xd7\x93\xd7\x99\xd7\x9d <b><i>\xd7\x94\xd7\x91\xd7\x9b\xd7\x99\xd7\xa8\xd7\x99\xd7\x9d \xd7\x91\xd7\x9e\xd7\x9e\xd7\xa9\xd7\x9c\xd7\x94</i></b>. \xd7\x9c\xd7\xa9\xd7\xa8 \xd7\x94\xd7\x91\xd7\x99\xd7\x98\xd7\x97\xd7\x95\xd7\x9f \xd7\x9e\xd7\xaa\xd7\x9e\xd7\xa0\xd7\x94 \xd7\x9c\xd7\xa8\xd7\x95\xd7\x91 \xd7\x92\xd7\x9d \xd7\xa1\xd7\x92\xd7\x9f \xd7\xa9\xd7\xa8.',
                    u'<bullet>\u2022</bullet>\u05e9\u05e8 \u05d4\u05d1\u05d9\u05d8\u05d7\u05d5\u05df, <b>\u05d4\u05d5\u05d0 \u05d4\u05e9\u05e8 \u05d4\u05d0\u05d7\u05e8\u05d0\u05d9 \u05e2\u05dc \u05de\u05e9\u05e8\u05d3 \u05d6\u05d4.</b> \u05ea\u05e4\u05e7\u05d9\u05d3 \u05d6\u05d4 <i>\u05e0\u05d7\u05e9\u05d1 \u05dc\u05d0\u05d7\u05d3</i> \u05d4\u05ea\u05e4\u05e7\u05d9\u05d3\u05d9\u05dd <b><i>\u05d4\u05d1\u05db\u05d9\u05e8\u05d9\u05dd \u05d1\u05de\u05de\u05e9\u05dc\u05d4</i></b>. \u05dc\u05e9\u05e8\u05d4\u05d1\u05d9\u05d8\u05d7\u05d5\u05df \u05de\u05ea\u05de\u05e0\u05d4 \u05dc\u05e8\u05d5\u05d1 \u05d2\u05dd \u05e1\u05d2\u05df \u05e9\u05e8.',
                    ]

            # simple text in a paragraph
            # working with patch from Hosam Aly
            p = Paragraph(TEXTS[0], p_style)
            elements.append(p)

            elements.append(Spacer(0, 40))

            # uses intra paragraph markup -> style text
            p = Paragraph(TEXTS[1], p_style)
            elements.append(p)
            elements.append(Spacer(0, 40))

            # list item (just a paragraph with a leading <bullet> element
            for list_style in list_styles:
                p = Paragraph(TEXTS[2], list_style)
                elements.append(p)

            doc.build(elements)

        def testParsing(self):
            fontName = getAFont()
            fontNameBI = tt2ps(fontName,1,1)
            stySTD = ParagraphStyle('STD',fontName=fontName)
            styBI = ParagraphStyle('BI',fontName=fontNameBI)
            self.assertRaises(ValueError,Paragraph,'aaaa <b><i>bibibi</b></i> ccccc',stySTD)
            self.assertRaises(ValueError,Paragraph,'AAAA <b><i>BIBIBI</b></i> CCCCC',styBI)

def makeSuite():
    return makeSuiteForClasses(ParagraphTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
