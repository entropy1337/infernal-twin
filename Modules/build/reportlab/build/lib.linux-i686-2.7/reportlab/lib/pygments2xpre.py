"""Helps you output colourised code snippets in ReportLab documents.

Platypus has an 'XPreformatted' flowable for handling preformatted
text, with variations in fonts and colors.   If Pygments is installed,
calling 'pygments2xpre' will return content suitable for display in
an XPreformatted object.  If it's not installed, you won't get colours.

For a list of available lexers see http://pygments.org/docs/

"""
__all__ = ('pygments2xpre',)
from reportlab.lib.utils import isPy3, asBytes, getBytesIO, getStringIO, asUnicode, isUnicode

def _2xpre(s,styles):
    "Helper to transform Pygments HTML output to ReportLab markup"
    s = s.replace('<div class="highlight">','')
    s = s.replace('</div>','')
    s = s.replace('<pre>','')
    s = s.replace('</pre>','')
    for k,c in styles+[('p','#000000'),('n','#000000'),('err','#000000')]:
        s = s.replace('<span class="%s">' % k,'<span color="%s">' % c)
    return s

def pygments2xpre(s, language="python"):
    "Return markup suitable for XPreformatted"
    try:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
    except ImportError:
        return s

    from pygments.lexers import get_lexer_by_name
    rconv = lambda x: x
    if isPy3:
        out = getStringIO()
    else:
        if isUnicode(s):
            s = asBytes(s)
            rconv = asUnicode
        out = getBytesIO()

    l = get_lexer_by_name(language)
    
    h = HtmlFormatter()
    highlight(s,l,h,out)
    styles = [(cls, style.split(';')[0].split(':')[1].strip())
                for cls, (style, ttype, level) in h.class2style.items()
                if cls and style and style.startswith('color:')]
    return rconv(_2xpre(out.getvalue(),styles))

def convertSourceFiles(filenames):
    "Helper function - makes minimal PDF document"

    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, XPreformatted
    from reportlab.lib.styles import getSampleStyleSheet
    styT=getSampleStyleSheet()["Title"]
    styC=getSampleStyleSheet()["Code"]
    doc = SimpleDocTemplate("pygments2xpre.pdf")
    S = [].append
    for filename in filenames:
        S(Paragraph(filename,style=styT))
        src = open(filename, 'r').read()
        fmt = pygments2xpre(src)
        S(XPreformatted(fmt, style=styC))
    doc.build(S.__self__)
    print('saved pygments2xpre.pdf')

if __name__=='__main__':
    import sys
    filenames = sys.argv[1:]
    if not filenames:
        print('usage:  pygments2xpre.py file1.py [file2.py] [...]')
        sys.exit(0)
    convertSourceFiles(filenames)
