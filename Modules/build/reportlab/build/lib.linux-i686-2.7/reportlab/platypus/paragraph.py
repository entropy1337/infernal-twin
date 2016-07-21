#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/platypus/paragraph.py
__version__=''' $Id$ '''
__doc__='''The standard paragraph implementation'''
from string import whitespace
from operator import truth
from unicodedata import category
from reportlab.pdfbase.pdfmetrics import stringWidth, getFont, getAscentDescent
from reportlab.platypus.paraparser import ParaParser
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.geomutils import normalizeTRBL
from reportlab.lib.textsplit import wordSplit, ALL_CANNOT_START
from copy import deepcopy
from reportlab.lib.abag import ABag
from reportlab.rl_config import platypus_link_underline, decimalSymbol, _FUZZ, paraFontSizeHeightOffset
from reportlab.lib.utils import _className, isBytes, unicodeT, bytesT, strTypes
from reportlab.lib.rl_accel import sameFrag
import re
from types import MethodType

#on UTF8/py33 branch, split and strip must be unicode-safe!
#thanks to Dirk Holtwick for helpful discussions/insight
#on this one
_wsc = ''.join((
    u'\u0009',  # HORIZONTAL TABULATION
    u'\u000A',  # LINE FEED
    u'\u000B',  # VERTICAL TABULATION
    u'\u000C',  # FORM FEED
    u'\u000D',  # CARRIAGE RETURN
    u'\u001C',  # FILE SEPARATOR
    u'\u001D',  # GROUP SEPARATOR
    u'\u001E',  # RECORD SEPARATOR
    u'\u001F',  # UNIT SEPARATOR
    u'\u0020',  # SPACE
    u'\u0085',  # NEXT LINE
    #u'\u00A0', # NO-BREAK SPACE
    u'\u1680',  # OGHAM SPACE MARK
    u'\u2000',  # EN QUAD
    u'\u2001',  # EM QUAD
    u'\u2002',  # EN SPACE
    u'\u2003',  # EM SPACE
    u'\u2004',  # THREE-PER-EM SPACE
    u'\u2005',  # FOUR-PER-EM SPACE
    u'\u2006',  # SIX-PER-EM SPACE
    u'\u2007',  # FIGURE SPACE
    u'\u2008',  # PUNCTUATION SPACE
    u'\u2009',  # THIN SPACE
    u'\u200A',  # HAIR SPACE
    u'\u200B',  # ZERO WIDTH SPACE
    u'\u2028',  # LINE SEPARATOR
    u'\u2029',  # PARAGRAPH SEPARATOR
    u'\u202F',  # NARROW NO-BREAK SPACE
    u'\u205F',  # MEDIUM MATHEMATICAL SPACE
    u'\u3000',  # IDEOGRAPHIC SPACE
    ))
_wsc_re_split=re.compile('[%s]+'% re.escape(_wsc)).split
_wsc_end_search=re.compile('[%s]+$'% re.escape(_wsc)).search

def split(text, delim=None):
    if isBytes(text): text = text.decode('utf8')
    if delim is not None and isBytes(delim): delim = delim.decode('utf8')
    return [uword for uword in (_wsc_re_split(text) if delim is None and u'\xa0' in text else text.split(delim))]

def strip(text):
    if isBytes(text): text = text.decode('utf8')
    return text.strip(_wsc)

class ParaLines(ABag):
    """
    class ParaLines contains the broken into lines representation of Paragraphs
        kind=0  Simple
        fontName, fontSize, textColor apply to whole Paragraph
        lines   [(extraSpace1,words1),....,(extraspaceN,wordsN)]

        kind==1 Complex
        lines   [FragLine1,...,FragLineN]
    """

class FragLine(ABag):
    """
    class FragLine contains a styled line (ie a line with more than one style)::

        extraSpace  unused space for justification only
        wordCount   1+spaces in line for justification purposes
        words       [ParaFrags] style text lumps to be concatenated together
        fontSize    maximum fontSize seen on the line; not used at present,
                    but could be used for line spacing.
    """

def _lineClean(L):
    return ' '.join(list(filter(truth,split(strip(L)))))

def cleanBlockQuotedText(text,joiner=' '):
    """This is an internal utility which takes triple-
    quoted text form within the document and returns
    (hopefully) the paragraph the user intended originally."""
    L=list(filter(truth,list(map(_lineClean, split(text, '\n')))))
    return joiner.join(L)

def setXPos(tx,dx):
    if dx>1e-6 or dx<-1e-6:
        tx.setXPos(dx)

def _leftDrawParaLine( tx, offset, extraspace, words, last=0):
    setXPos(tx,offset)
    tx._textOut(' '.join(words),1)
    setXPos(tx,-offset)
    return offset

def _centerDrawParaLine( tx, offset, extraspace, words, last=0):
    m = offset + 0.5 * extraspace
    setXPos(tx,m)
    tx._textOut(' '.join(words),1)
    setXPos(tx,-m)
    return m

def _rightDrawParaLine( tx, offset, extraspace, words, last=0):
    m = offset + extraspace
    setXPos(tx,m)
    tx._textOut(' '.join(words),1)
    setXPos(tx,-m)
    return m

def _nbspCount(w):
    if isBytes(w):
        return w.count(b'\xc2\xa0')
    else:
        return w.count(u'\xa0')

def _justifyDrawParaLine( tx, offset, extraspace, words, last=0):
    setXPos(tx,offset)
    text  = ' '.join(words)
    if last or extraspace<=1e-8:
        #last one, left align
        tx._textOut(text,1)
    else:
        nSpaces = len(words)+sum([_nbspCount(w) for w in words])-1
        if nSpaces:
            tx.setWordSpace(extraspace / float(nSpaces))
            tx._textOut(text,1)
            tx.setWordSpace(0)
        else:
            tx._textOut(text,1)
    setXPos(tx,-offset)
    return offset

def imgVRange(h,va,fontSize):
    '''return bottom,top offsets relative to baseline(0)'''
    if va=='baseline':
        iyo = 0
    elif va in ('text-top','top'):
        iyo = fontSize-h
    elif va=='middle':
        iyo = fontSize - (1.2*fontSize+h)*0.5
    elif va in ('text-bottom','bottom'):
        iyo = fontSize - 1.2*fontSize
    elif va=='super':
        iyo = 0.5*fontSize
    elif va=='sub':
        iyo = -0.5*fontSize
    elif hasattr(va,'normalizedValue'):
        iyo = va.normalizedValue(fontSize)
    else:
        iyo = va
    return iyo,iyo+h

def imgNormV(v,nv):
    if hasattr(v,'normalizedValue'):
        return v.normalizedValue(nv)
    else:
        return v

def _getDotsInfo(style):
    dots = style.endDots
    if isinstance(dots,str):
        text = dots
        fontName = style.fontName
        fontSize = style.fontSize
        textColor = style.textColor
        backColor = style.backColor
        dy = 0
    else:
        text = getattr(dots,'text','.')
        fontName = getattr(dots,'fontName',style.fontName)
        fontSize = getattr(dots,'fontSize',style.fontSize)
        textColor = getattr(dots,'textColor',style.textColor)
        backColor = getattr(dots,'backColor',style.backColor)
        dy = getattr(dots,'dy',0)
    return text,fontName,fontSize,textColor,backColor,dy

_56=5./6
_16=1./6
def _putFragLine(cur_x, tx, line, last, pKind):
    xs = tx.XtraState
    cur_y = xs.cur_y
    x0 = tx._x0
    autoLeading = xs.autoLeading
    leading = xs.leading
    cur_x += xs.leftIndent
    dal = autoLeading in ('min','max')
    if dal:
        if autoLeading=='max':
            ascent = max(_56*leading,line.ascent)
            descent = max(_16*leading,-line.descent)
        else:
            ascent = line.ascent
            descent = -line.descent
        leading = ascent+descent
    if tx._leading!=leading:
        tx.setLeading(leading)
    if dal:
        olb = tx._olb
        if olb is not None:
            xcy = olb-ascent
            if tx._oleading!=leading:
                cur_y += leading - tx._oleading
            if abs(xcy-cur_y)>1e-8:
                cur_y = xcy
                tx.setTextOrigin(x0,cur_y)
                xs.cur_y = cur_y
        tx._olb = cur_y - descent
        tx._oleading = leading
    ws = getattr(tx,'_wordSpace',0)
    nSpaces = 0
    words = line.words
    for i, f in enumerate(words):
        if hasattr(f,'cbDefn'):
            cbDefn = f.cbDefn
            kind = cbDefn.kind
            if kind=='img':
                #draw image cbDefn,cur_y,cur_x
                txfs = tx._fontsize
                if txfs is None:
                    txfs = xs.style.fontSize
                w = imgNormV(cbDefn.width,None)
                h = imgNormV(cbDefn.height,txfs)
                iy0,iy1 = imgVRange(h,cbDefn.valign,txfs)
                cur_x_s = cur_x + nSpaces*ws
                tx._canvas.drawImage(cbDefn.image,cur_x_s,cur_y+iy0,w,h,mask='auto')
                cur_x += w
                cur_x_s += w
                setXPos(tx,cur_x_s-tx._x0)
            else:
                name = cbDefn.name
                if kind=='anchor':
                    tx._canvas.bookmarkHorizontal(name,cur_x,cur_y+leading)
                else:
                    func = getattr(tx._canvas,name,None)
                    if not func:
                        raise AttributeError("Missing %s callback attribute '%s'" % (kind,name))
                    tx._canvas._curr_tx_info=dict(tx=tx,cur_x=cur_x,cur_y=cur_y,leading=leading,xs=tx.XtraState)
                    try:
                        func(tx._canvas,kind,cbDefn.label)
                    finally:
                        del tx._canvas._curr_tx_info
            if f is words[-1]:
                if not tx._fontname:
                    tx.setFont(xs.style.fontName,xs.style.fontSize)
                tx._textOut('',1)
        else:
            cur_x_s = cur_x + nSpaces*ws
            end_x = cur_x_s
            if i > 0:
                end_x = cur_x_s - _trailingSpaceLength(words[i-1].text, tx)
            if (tx._fontname,tx._fontsize)!=(f.fontName,f.fontSize):
                tx._setFont(f.fontName, f.fontSize)
            if xs.textColor!=f.textColor:
                xs.textColor = f.textColor
                tx.setFillColor(f.textColor)
            if xs.rise!=f.rise:
                xs.rise=f.rise
                tx.setRise(f.rise)
            text = f.text
            tx._textOut(text,f is words[-1])    # cheap textOut
            if not xs.underline and f.underline:
                xs.underline = 1
                xs.underline_x = cur_x_s
                xs.underlineColor = f.textColor
            elif xs.underline:
                if not f.underline:
                    xs.underline = 0
                    xs.underlines.append( (xs.underline_x, end_x, xs.underlineColor) )
                    xs.underlineColor = None
                elif xs.textColor!=xs.underlineColor:
                    xs.underlines.append( (xs.underline_x, end_x, xs.underlineColor) )
                    xs.underlineColor = xs.textColor
                    xs.underline_x = cur_x_s
            if not xs.strike and f.strike:
                xs.strike = 1
                xs.strike_x = cur_x_s
                xs.strikeColor = f.textColor
            elif xs.strike:
                if not f.strike:
                    xs.strike = 0
                    xs.strikes.append( (xs.strike_x, end_x, xs.strikeColor) )
                    xs.strikeColor = None
                elif xs.textColor!=xs.strikeColor:
                    xs.strikes.append( (xs.strike_x, end_x, xs.strikeColor) )
                    xs.strikeColor = xs.textColor
                    xs.strike_x = cur_x_s
            if f.link and not xs.link:
                if not xs.link:
                    xs.link = f.link
                    xs.link_x = cur_x_s
                    xs.linkColor = xs.textColor
            elif xs.link:
                if not f.link:
                    xs.links.append( (xs.link_x, end_x, xs.link, xs.linkColor) )
                    xs.link = None
                    xs.linkColor = None
                elif f.link!=xs.link or xs.textColor!=xs.linkColor:
                    xs.links.append( (xs.link_x, end_x, xs.link, xs.linkColor) )
                    xs.link = f.link
                    xs.link_x = cur_x_s
                    xs.linkColor = xs.textColor
            bg = getattr(f,'backColor',None)
            if bg and not xs.backColor:
                xs.backColor = bg
                xs.backColor_x = cur_x_s
            elif xs.backColor:
                if not bg:
                    xs.backColors.append( (xs.backColor_x, end_x, xs.backColor) )
                    xs.backColor = None
                elif f.backColor!=xs.backColor or xs.textColor!=xs.backColor:
                    xs.backColors.append( (xs.backColor_x, end_x, xs.backColor) )
                    xs.backColor = bg
                    xs.backColor_x = cur_x_s
            txtlen = tx._canvas.stringWidth(text, tx._fontname, tx._fontsize)
            cur_x += txtlen
            nSpaces += text.count(' ')+_nbspCount(text)
    cur_x_s = cur_x+(nSpaces-1)*ws
    if last and pKind!='right' and xs.style.endDots:
        _do_dots_frag(cur_x,cur_x_s,line.maxWidth,xs,tx)
    if xs.underline:
        xs.underlines.append( (xs.underline_x, cur_x_s, xs.underlineColor) )
    if xs.strike:
        xs.strikes.append( (xs.strike_x, cur_x_s, xs.strikeColor) )
    if xs.link:
        xs.links.append( (xs.link_x, cur_x_s, xs.link,xs.linkColor) )
    if xs.backColor:
        xs.backColors.append( (xs.backColor_x, cur_x_s, xs.backColor) )
    if tx._x0!=x0:
        setXPos(tx,x0-tx._x0)

def _do_dots_frag(cur_x, cur_x_s, maxWidth, xs, tx):
    text,fontName,fontSize,textColor,backColor,dy = _getDotsInfo(xs.style)
    txtlen = tx._canvas.stringWidth(text, fontName, fontSize)
    if cur_x_s+txtlen<=maxWidth:
        if tx._fontname!=fontName or tx._fontsize!=fontSize:
            tx.setFont(fontName,fontSize)
        maxWidth += getattr(tx,'_dotsOffsetX',tx._x0)
        tx.setTextOrigin(0,xs.cur_y+dy)
        setXPos(tx,cur_x_s-cur_x)
        n = int((maxWidth-cur_x_s)/txtlen)
        setXPos(tx,maxWidth - txtlen*n)
        if xs.textColor!=textColor:
            tx.setFillColor(textColor)
        if backColor: xs.backColors.append((cur_x,maxWidth,backColor))
        tx._textOut(n*text,1)
        if dy: tx.setTextOrigin(tx._x0,xs.cur_y-dy)

def _leftDrawParaLineX( tx, offset, line, last=0):
    setXPos(tx,offset)
    _putFragLine(offset, tx, line, last, 'left')
    setXPos(tx,-offset)

def _centerDrawParaLineX( tx, offset, line, last=0):
    tx._dotsOffsetX = offset + tx._x0
    try:
        m = offset+0.5*line.extraSpace
        setXPos(tx,m)
        _putFragLine(m,tx, line, last,'center')
        setXPos(tx,-m)
    finally:
        del tx._dotsOffsetX

def _rightDrawParaLineX( tx, offset, line, last=0):
    m = offset+line.extraSpace
    setXPos(tx,m)
    _putFragLine(m,tx, line, last, 'right')
    setXPos(tx,-m)

def _justifyDrawParaLineX( tx, offset, line, last=0):
    setXPos(tx,offset)
    extraSpace = line.extraSpace
    simple = last or abs(extraSpace)<=1e-8 or line.lineBreak
    if not simple:
        nSpaces = line.wordCount+sum([_nbspCount(w.text) for w in line.words if not hasattr(w,'cbDefn')])-1
        simple = not nSpaces
    if not simple:
        tx.setWordSpace(extraSpace / float(nSpaces))
        _putFragLine(offset, tx, line, last, 'justify')
        tx.setWordSpace(0)
    else:
        _putFragLine(offset, tx, line, last, 'justify') #no space modification
    setXPos(tx,-offset)

def _trailingSpaceLength(text, tx):
    ws = _wsc_end_search(text)
    return tx._canvas.stringWidth(ws.group(), tx._fontname, tx._fontsize) if ws else 0

def _getFragWords(frags,maxWidth=None):
    ''' given a Parafrag list return a list of fragwords
        [[size, (f00,w00), ..., (f0n,w0n)],....,[size, (fm0,wm0), ..., (f0n,wmn)]]
        each pair f,w represents a style and some string
        each sublist represents a word
    '''
    R = []
    W = []
    n = 0
    hangingStrip = False
    for f in frags:
        text = f.text
        #del f.text # we can't do this until we sort out splitting
                    # of paragraphs
        if text!='':
            if hangingStrip:
                hangingStrip = False
                text = text.lstrip()
            S = split(text)
            if S==[]: S = ['']
            if W!=[] and text[0] in whitespace:
                W.insert(0,n)
                R.append(W)
                W = []
                n = 0

            for w in S[:-1]:
                W.append((f,w))
                n += stringWidth(w, f.fontName, f.fontSize)
                W.insert(0,n)
                R.append(W)
                W = []
                n = 0

            w = S[-1]
            W.append((f,w))
            n += stringWidth(w, f.fontName, f.fontSize)
            if text and text[-1] in whitespace:
                W.insert(0,n)
                R.append(W)
                W = []
                n = 0
        elif hasattr(f,'cbDefn'):
            cb = f.cbDefn
            w = getattr(cb,'width',0)
            if w:
                if hasattr(w,'normalizedValue'):
                    w._normalizer = maxWidth
                    w = w.normalizedValue(maxWidth)
                if W!=[]:
                    W.insert(0,n)
                    R.append(W)
                    W = []
                    n = 0
                R.append([w,(f,'')])
            else:
                W.append((f,''))
        elif hasattr(f, 'lineBreak'):
            #pass the frag through.  The line breaker will scan for it.
            if W!=[]:
                W.insert(0,n)
                R.append(W)
                W = []
                n = 0
            R.append([0,(f,'')])
            hangingStrip = True

    if W!=[]:
        W.insert(0,n)
        R.append(W)

    return R

def _fragWordIter(w):
    for f, s in w[1:]:
        if hasattr(f,'cbDefn'):
            yield f, getattr(f,'width'), s
        elif s:
            if isBytes(s):
                s = s.decode('utf8')    #only encoding allowed
            for c in s:
                yield f, stringWidth(c,f.fontName, f.fontSize), c
        else:
            yield f, 0, s

class _SplitList(list):
    pass

def _splitFragWord(w,maxWidth,maxWidths,lineno):
    '''given a frag word, w, as returned by getFragWords
    split it into frag words that fit in lines of length
    maxWidth
    maxWidths[lineno+1]
    .....
    maxWidths[lineno+n]

    return the new word list
    '''
    R = []
    maxlineno = len(maxWidths)-1
    W = []
    lineWidth = 0
    fragText = u''
    wordWidth = 0
    f = w[1][0]
    for g,cw,c in _fragWordIter(w):
        newLineWidth = lineWidth+cw
        tooLong = newLineWidth>maxWidth
        if g is not f or tooLong:
            f = f.clone()
            if hasattr(f,'text'):
                f.text = fragText
            W.append((f,fragText))
            if tooLong:
                W = _SplitList([wordWidth]+W)
                R.append(W)
                lineno += 1
                maxWidth = maxWidths[min(maxlineno,lineno)]
                W = []
                newLineWidth = wordWidth = cw
            fragText = u''
            f = g
            wordWidth = 0
        wordWidth += cw
        fragText += c
        lineWidth = newLineWidth
    W.append((f,fragText))
    W = _SplitList([wordWidth]+W)
    R.append(W)
    return R

class _SplitText(unicodeT):
    pass

def _splitWord(w,maxWidth,maxWidths,lineno,fontName,fontSize,encoding='utf8'):
    '''
    split w into words that fit in lines of length
    maxWidth
    maxWidths[lineno+1]
    .....
    maxWidths[lineno+n]

    then push those new words onto words
    '''
    #TODO fix this to use binary search for the split points
    R = []
    maxlineno = len(maxWidths)-1
    lineWidth = 0
    wordText = u''
    if isBytes(w):
        w = w.decode(encoding)
    for c in w:
        cw = stringWidth(c,fontName,fontSize,encoding)
        newLineWidth = lineWidth+cw
        if newLineWidth>maxWidth:
            R.append(_SplitText(wordText))
            lineno += 1
            maxWidth = maxWidths[min(maxlineno,lineno)]
            newLineWidth = cw
            wordText = u''
        wordText += c
        lineWidth = newLineWidth
    R.append(_SplitText(wordText))
    return R

def _split_blParaSimple(blPara,start,stop):
    f = blPara.clone()
    for a in ('lines', 'kind', 'text'):
        if hasattr(f,a): delattr(f,a)

    f.words = []
    for l in blPara.lines[start:stop]:
        for w in l[1]:
            f.words.append(w)
    return [f]

def _split_blParaHard(blPara,start,stop):
    f = []
    lines = blPara.lines[start:stop]
    for l in lines:
        for w in l.words:
            f.append(w)
        if l is not lines[-1]:
            i = len(f)-1
            while i>=0 and hasattr(f[i],'cbDefn') and not getattr(f[i].cbDefn,'width',0): i -= 1
            if i>=0:
                g = f[i]
                if not g.text: g.text = ' '
                elif g.text[-1]!=' ': g.text += ' '
    return f

def _drawBullet(canvas, offset, cur_y, bulletText, style, rtl):
    '''draw a bullet text could be a simple string or a frag list'''
    bulletAnchor = style.bulletAnchor
    if rtl or style.bulletAnchor!='start':
        numeric = bulletAnchor=='numeric'
        if isinstance(bulletText,strTypes):
            t =  bulletText
            q = numeric and decimalSymbol in t
            if q: t = t[:t.index(decimalSymbol)]
            bulletWidth = stringWidth(t, style.bulletFontName, style.bulletFontSize)
            if q: bulletWidth += 0.5 * stringWidth(decimalSymbol, style.bulletFontName, style.bulletFontSize)
        else:
            #it's a list of fragments
            bulletWidth = 0
            for f in bulletText:
                t = f.text
                q = numeric and decimalSymbol in t
                if q:
                    t = t[:t.index(decimalSymbol)]
                    bulletWidth += 0.5 * stringWidth(decimalSymbol, f.fontName, f.fontSize)
                bulletWidth += stringWidth(t, f.fontName, f.fontSize)
                if q:
                    break
    else:
        bulletWidth = 0
    if bulletAnchor=='middle': bulletWidth *= 0.5
    cur_y += getattr(style,"bulletOffsetY",0)
    if not rtl:
        tx2 = canvas.beginText(style.bulletIndent-bulletWidth,cur_y)
    else:
        width = rtl[0]
        bulletStart = width+style.rightIndent-(style.bulletIndent+bulletWidth)
        tx2 = canvas.beginText(bulletStart, cur_y)
    tx2.setFont(style.bulletFontName, style.bulletFontSize)
    tx2.setFillColor(getattr(style,'bulletColor',style.textColor))
    if isinstance(bulletText,strTypes):
        tx2.textOut(bulletText)
    else:
        for f in bulletText:
            tx2.setFont(f.fontName, f.fontSize)
            tx2.setFillColor(f.textColor)
            tx2.textOut(f.text)

    canvas.drawText(tx2)
    if not rtl:
        #AR making definition lists a bit less ugly
        #bulletEnd = tx2.getX()
        bulletEnd = tx2.getX() + style.bulletFontSize * 0.6
        offset = max(offset,bulletEnd - style.leftIndent)
    return offset

def _handleBulletWidth(bulletText,style,maxWidths):
    '''work out bullet width and adjust maxWidths[0] if neccessary
    '''
    if bulletText:
        if isinstance(bulletText,strTypes):
            bulletWidth = stringWidth( bulletText, style.bulletFontName, style.bulletFontSize)
        else:
            #it's a list of fragments
            bulletWidth = 0
            for f in bulletText:
                bulletWidth += stringWidth(f.text, f.fontName, f.fontSize)
        bulletLen = style.bulletIndent + bulletWidth + 0.6 * style.bulletFontSize
        if style.wordWrap=='RTL':
            indent = style.rightIndent+style.firstLineIndent
        else:
            indent = style.leftIndent+style.firstLineIndent
        if bulletLen > indent:
            #..then it overruns, and we have less space available on line 1
            maxWidths[0] -= (bulletLen - indent)

def splitLines0(frags,widths):
    '''
    given a list of ParaFrags we return a list of ParaLines

    each ParaLine has
    1)  ExtraSpace
    2)  blankCount
    3)  [textDefns....]
    each text definition is a (ParaFrag, start, limit) triplet
    '''
    #initialise the algorithm
    lines   = []
    lineNum = 0
    maxW    = widths[lineNum]
    i       = -1
    l       = len(frags)
    lim     = start = 0
    while 1:
        #find a non whitespace character
        while i<l:
            while start<lim and text[start]==' ': start += 1
            if start==lim:
                i += 1
                if i==l: break
                start = 0
                f = frags[i]
                text = f.text
                lim = len(text)
            else:
                break   # we found one

        if start==lim: break    #if we didn't find one we are done

        #start of a line
        g       = (None,None,None)
        line    = []
        cLen    = 0
        nSpaces = 0
        while cLen<maxW:
            j = text.find(' ',start)
            if j<0: j==lim
            w = stringWidth(text[start:j],f.fontName,f.fontSize)
            cLen += w
            if cLen>maxW and line!=[]:
                cLen = cLen-w
                #this is the end of the line
                while g.text[lim]==' ':
                    lim = lim - 1
                    nSpaces = nSpaces-1
                break
            if j<0: j = lim
            if g[0] is f: g[2] = j  #extend
            else:
                g = (f,start,j)
                line.append(g)
            if j==lim:
                i += 1

def _old_do_line(tx, x1, y1, x2, y2):
    tx._canvas.line(x1, y1, x2, y2)

def _do_line(tx, x1, y1, x2, y2):
    olw = tx._canvas._lineWidth
    nlw = tx._underlineProportion*tx._fontsize
    if nlw!=olw:
        tx._canvas.setLineWidth(nlw)
        tx._canvas.line(x1, y1, x2, y2)
        tx._canvas.setLineWidth(olw)
    else:
        tx._canvas.line(x1, y1, x2, y2)

def _do_under_line(i, t_off, ws, tx, lm=-0.125):
    y = tx.XtraState.cur_y - i*tx.XtraState.style.leading + lm*tx.XtraState.f.fontSize
    textlen = tx._canvas.stringWidth(' '.join(tx.XtraState.lines[i][1]), tx._fontname, tx._fontsize)
    tx._do_line(t_off, y, t_off+textlen, y)

_scheme_re = re.compile('^[a-zA-Z][-+a-zA-Z0-9]+$')
def _doLink(tx,link,rect):
    parts = link.split(':',1)
    scheme = len(parts)==2 and parts[0].lower() or ''
    if _scheme_re.match(scheme) and scheme!='document':
        kind=scheme.lower()=='pdf' and 'GoToR' or 'URI'
        if kind=='GoToR': link = parts[1]
        tx._canvas.linkURL(link, rect, relative=1, kind=kind)
    else:
        if link[0]=='#':
            link = link[1:]
            scheme=''
        tx._canvas.linkRect("", scheme!='document' and link or parts[1], rect, relative=1)

def _do_link_line(i, t_off, ws, tx):
    xs = tx.XtraState
    leading = xs.style.leading
    y = xs.cur_y - i*leading - xs.f.fontSize/8.0 # 8.0 factor copied from para.py
    text = ' '.join(xs.lines[i][1])
    textlen = tx._canvas.stringWidth(text, tx._fontname, tx._fontsize)
    _doLink(tx, xs.link, (t_off, y, t_off+textlen, y+leading))

def _do_post_text(tx):
    xs = tx.XtraState
    leading = xs.style.leading
    autoLeading = xs.autoLeading
    f = xs.f
    if autoLeading=='max':
        leading = max(leading,1.2*f.fontSize)
    elif autoLeading=='min':
        leading = 1.2*f.fontSize
    ff = 0.125*f.fontSize
    y0 = xs.cur_y
    y = y0 - ff
    csc = None
    for x1,x2,c in xs.underlines:
        if c!=csc:
            tx._canvas.setStrokeColor(c)
            csc = c
        tx._do_line(x1, y, x2, y)
    xs.underlines = []
    xs.underline=0
    xs.underlineColor=None

    ys = y0 + 2*ff
    for x1,x2,c in xs.strikes:
        if c!=csc:
            tx._canvas.setStrokeColor(c)
            csc = c
        tx._do_line(x1, ys, x2, ys)
    xs.strikes = []
    xs.strike=0
    xs.strikeColor=None

    yl = y0 + f.fontSize
    ydesc = yl - leading
    for x1,x2,link,c in xs.links:
        if platypus_link_underline:
            if c!=csc:
                tx._canvas.setStrokeColor(c)
                csc = c
            tx._do_line(x1, y, x2, y)
        _doLink(tx, link, (x1, ydesc, x2, yl))
    xs.links = []
    xs.link=None
    xs.linkColor=None

    for x1,x2,c in xs.backColors:
        tx._canvas.setFillColor(c)
        tx._canvas.rect(x1,ydesc,x2-x1,leading,stroke=0,fill=1)

    xs.backColors=[]
    xs.backColor=None
    xs.cur_y -= leading

def textTransformFrags(frags,style):
    tt = style.textTransform
    if tt:
        tt=tt.lower()
        if tt=='lowercase':
            tt = unicodeT.lower
        elif tt=='uppercase':
            tt = unicodeT.upper
        elif  tt=='capitalize':
            tt = unicodeT.title
        elif tt=='none':
            return
        else:
            raise ValueError('ParaStyle.textTransform value %r is invalid' % style.textTransform)
        n = len(frags)
        if n==1:
            #single fragment the easy case
            frags[0].text = tt(frags[0].text)
        elif tt is unicodeT.title:
            pb = True
            for f in frags:
                u = f.text
                if not u: continue
                if u.startswith(u' ') or pb:
                    u = tt(u)
                else:
                    i = u.find(u' ')
                    if i>=0:
                        u = u[:i]+tt(u[i:])
                pb = u.endswith(u' ')
                f.text = u
        else:
            for f in frags:
                u = f.text
                if not u: continue
                f.text = tt(u)

class cjkU(unicodeT):
    '''simple class to hold the frag corresponding to a str'''
    def __new__(cls,value,frag,encoding):
        self = unicodeT.__new__(cls,value)
        self._frag = frag
        if hasattr(frag,'cbDefn'):
            w = getattr(frag.cbDefn,'width',0)
            self._width = w
        else:
            self._width = stringWidth(value,frag.fontName,frag.fontSize)
        return self
    frag = property(lambda self: self._frag)
    width = property(lambda self: self._width)

def makeCJKParaLine(U,maxWidth,widthUsed,extraSpace,lineBreak,calcBounds):
    words = []
    CW = []
    f0 = FragLine()
    maxSize = maxAscent = minDescent = 0
    for u in U:
        f = u.frag
        fontSize = f.fontSize
        if calcBounds:
            cbDefn = getattr(f,'cbDefn',None)
            if getattr(cbDefn,'width',0):
                descent, ascent = imgVRange(imgNormV(cbDefn.height,fontSize),cbDefn.valign,fontSize)
            else:
                ascent, descent = getAscentDescent(f.fontName,fontSize)
        else:
            ascent, descent = getAscentDescent(f.fontName,fontSize)
        maxSize = max(maxSize,fontSize)
        maxAscent = max(maxAscent,ascent)
        minDescent = min(minDescent,descent)
        if not sameFrag(f0,f):
            f0=f0.clone()
            f0.text = u''.join(CW)
            words.append(f0)
            CW = []
            f0 = f
        CW.append(u)
    if CW:
        f0=f0.clone()
        f0.text = u''.join(CW)
        words.append(f0)
    return FragLine(kind=1,extraSpace=extraSpace,wordCount=1,words=words[1:],fontSize=maxSize,ascent=maxAscent,descent=minDescent,maxWidth=maxWidth,currentWidth=widthUsed,lineBreak=lineBreak)

def cjkFragSplit(frags, maxWidths, calcBounds, encoding='utf8'):
    '''This attempts to be wordSplit for frags using the dumb algorithm'''
    U = []  #get a list of single glyphs with their widths etc etc
    for f in frags:
        text = f.text
        if isBytes(text):
            text = text.decode(encoding)
        if text:
            U.extend([cjkU(t,f,encoding) for t in text])
        else:
            U.append(cjkU(text,f,encoding))
    lines = []
    i = widthUsed = lineStartPos = 0
    maxWidth = maxWidths[0]
    nU = len(U)
    while i<nU:
        u = U[i]
        i += 1
        w = u.width
        if hasattr(w,'normalizedValue'):
            w._normalizer = maxWidth
            w = w.normalizedValue(None)
        widthUsed += w
        lineBreak = hasattr(u.frag,'lineBreak')
        endLine = (widthUsed>maxWidth + _FUZZ and widthUsed>0) or lineBreak
        if endLine:
            extraSpace = maxWidth - widthUsed
            if not lineBreak:
                if ord(u)<0x3000:
                    # we appear to be inside a non-Asian script section.
                    # (this is a very crude test but quick to compute).
                    # This is likely to be quite rare so the speed of the
                    # code below is hopefully not a big issue.  The main
                    # situation requiring this is that a document title
                    # with an english product name in it got cut.


                    # we count back and look for
                    #  - a space-like character
                    #  - reversion to Kanji (which would be a good split point)
                    #  - in the worst case, roughly half way back along the line
                    limitCheck = (lineStartPos+i)>>1        #(arbitrary taste issue)
                    for j in xrange(i-1,limitCheck,-1):
                        uj = U[j]
                        if uj and category(uj)=='Zs' or ord(uj)>=0x3000:
                            k = j+1
                            if k<i:
                                j = k+1
                                extraSpace += sum(U[ii].width for ii in xrange(j,i))
                                w = U[k].width
                                u = U[k]
                                i = j
                                break

                #we are pushing this character back, but
                #the most important of the Japanese typography rules
                #if this character cannot start a line, wrap it up to this line so it hangs
                #in the right margin. We won't do two or more though - that's unlikely and
                #would result in growing ugliness.
                #and increase the extra space
                #bug fix contributed by Alexander Vasilenko <alexs.vasilenko@gmail.com>
                if u not in ALL_CANNOT_START and i>lineStartPos+1:
                    #otherwise we need to push the character back
                    #the i>lineStart+1 condition ensures progress
                    i -= 1
                    extraSpace += w
            lines.append(makeCJKParaLine(U[lineStartPos:i],maxWidth,widthUsed,extraSpace,lineBreak,calcBounds))
            try:
                maxWidth = maxWidths[len(lines)]
            except IndexError:
                maxWidth = maxWidths[-1]  # use the last one

            lineStartPos = i
            widthUsed = 0

    #any characters left?
    if widthUsed > 0:
        lines.append(makeCJKParaLine(U[lineStartPos:],maxWidth,widthUsed,maxWidth-widthUsed,False,calcBounds))

    return ParaLines(kind=1,lines=lines)

class Paragraph(Flowable):
    """ Paragraph(text, style, bulletText=None, caseSensitive=1)
        text a string of stuff to go into the paragraph.
        style is a style definition as in reportlab.lib.styles.
        bulletText is an optional bullet defintion.
        caseSensitive set this to 0 if you want the markup tags and their attributes to be case-insensitive.

        This class is a flowable that can format a block of text
        into a paragraph with a given style.

        The paragraph Text can contain XML-like markup including the tags:
        <b> ... </b> - bold
        <i> ... </i> - italics
        <u> ... </u> - underline
        <strike> ... </strike> - strike through
        <super> ... </super> - superscript
        <sub> ... </sub> - subscript
        <font name=fontfamily/fontname color=colorname size=float>
        <span name=fontfamily/fontname color=colorname backcolor=colorname size=float style=stylename>
        <onDraw name=callable label="a label"/>
        <index [name="callablecanvasattribute"] label="a label"/>
        <link>link text</link>
        attributes of links
        size/fontSize=num
        name/face/fontName=name
        fg/textColor/color=color
        backcolor/backColor/bgcolor=color
        dest/destination/target/href/link=target
        <a>anchor text</a>
        attributes of anchors
        fontSize=num
        fontName=name
        fg/textColor/color=color
        backcolor/backColor/bgcolor=color
        href=href
        <a name="anchorpoint"/>
        <unichar name="unicode character name"/>
        <unichar value="unicode code point"/>
        <img src="path" width="1in" height="1in" valign="bottom"/>
                width="w%" --> fontSize*w/100   idea from Roberto Alsina
                height="h%" --> linewidth*h/100 <ralsina@netmanagers.com.ar>

        The whole may be surrounded by <para> </para> tags

        The <b> and <i> tags will work for the built-in fonts (Helvetica
        /Times / Courier).  For other fonts you need to register a family
        of 4 fonts using reportlab.pdfbase.pdfmetrics.registerFont; then
        use the addMapping function to tell the library that these 4 fonts
        form a family e.g.
        from reportlab.lib.fonts import addMapping
        addMapping('Vera', 0, 0, 'Vera')    #normal
        addMapping('Vera', 0, 1, 'Vera-Italic')    #italic
        addMapping('Vera', 1, 0, 'Vera-Bold')    #bold
        addMapping('Vera', 1, 1, 'Vera-BoldItalic')    #italic and bold

        It will also be able to handle any MathML specified Greek characters.
    """
    def __init__(self, text, style, bulletText = None, frags=None, caseSensitive=1, encoding='utf8'):
        self.caseSensitive = caseSensitive
        self.encoding = encoding
        self._setup(text, style, bulletText or getattr(style,'bulletText',None), frags, cleanBlockQuotedText)


    def __repr__(self):
        n = self.__class__.__name__
        L = [n+"("]
        keys = list(self.__dict__.keys())
        for k in keys:
            L.append('%s: %s' % (repr(k).replace("\n", " ").replace("  "," "),repr(getattr(self, k)).replace("\n", " ").replace("  "," ")))
        L.append(") #"+n)
        return '\n'.join(L)

    def _setup(self, text, style, bulletText, frags, cleaner):

        #This used to be a global parser to save overhead.
        #In the interests of thread safety it is being instantiated per paragraph.
        #On the next release, we'll replace with a cElementTree parser

        if frags is None:
            text = cleaner(text)
            _parser = ParaParser()
            _parser.caseSensitive = self.caseSensitive
            style, frags, bulletTextFrags = _parser.parse(text,style)
            if frags is None:
                raise ValueError("xml parser error (%s) in paragraph beginning\n'%s'"\
                    % (_parser.errors[0],text[:min(30,len(text))]))
            textTransformFrags(frags,style)
            if bulletTextFrags: bulletText = bulletTextFrags

        #AR hack
        self.text = text
        self.frags = frags
        self.style = style
        self.bulletText = bulletText
        self.debug = 0  #turn this on to see a pretty one with all the margins etc.

    def wrap(self, availWidth, availHeight):
        # work out widths array for breaking
        self.width = availWidth
        style = self.style
        leftIndent = style.leftIndent
        first_line_width = availWidth - (leftIndent+style.firstLineIndent) - style.rightIndent
        later_widths = availWidth - leftIndent - style.rightIndent
        self._wrapWidths = [first_line_width, later_widths]

        if style.wordWrap == 'CJK':
            #use Asian text wrap algorithm to break characters
            blPara = self.breakLinesCJK(self._wrapWidths)
        else:
            blPara = self.breakLines(self._wrapWidths)
        self.blPara = blPara
        autoLeading = getattr(self,'autoLeading',getattr(style,'autoLeading',''))
        leading = style.leading
        if blPara.kind==1:
            if autoLeading not in ('','off'):
                height = 0
                if autoLeading=='max':
                    for l in blPara.lines:
                        height += max(l.ascent-l.descent,leading)
                elif autoLeading=='min':
                    for l in blPara.lines:
                        height += l.ascent - l.descent
                else:
                    raise ValueError('invalid autoLeading value %r' % autoLeading)
            else:
                height = len(blPara.lines) * leading
        else:
            if autoLeading=='max':
                leading = max(leading,blPara.ascent-blPara.descent)
            elif autoLeading=='min':
                leading = blPara.ascent-blPara.descent
            height = len(blPara.lines) * leading
        self.height = height
        return self.width, height

    def minWidth(self):
        'Attempt to determine a minimum sensible width'
        frags = self.frags
        nFrags= len(frags)
        if not nFrags: return 0
        if nFrags==1:
            f = frags[0]
            fS = f.fontSize
            fN = f.fontName
            words = hasattr(f,'text') and split(f.text, ' ') or f.words
            func = lambda w, fS=fS, fN=fN: stringWidth(w,fN,fS)
        else:
            words = _getFragWords(frags)
            func  = lambda x: x[0]
        return max(list(map(func,words)))

    def _get_split_blParaFunc(self):
        return self.blPara.kind==0 and _split_blParaSimple or _split_blParaHard

    def split(self,availWidth, availHeight):
        if len(self.frags)<=0: return []

        #the split information is all inside self.blPara
        if not hasattr(self,'blPara'):
            self.wrap(availWidth,availHeight)
        blPara = self.blPara
        style = self.style
        autoLeading = getattr(self,'autoLeading',getattr(style,'autoLeading',''))
        leading = style.leading
        lines = blPara.lines
        if blPara.kind==1 and autoLeading not in ('','off'):
            s = height = 0
            if autoLeading=='max':
                for i,l in enumerate(blPara.lines):
                    h = max(l.ascent-l.descent,leading)
                    n = height+h
                    if n>availHeight+1e-8:
                        break
                    height = n
                    s = i+1
            elif autoLeading=='min':
                for i,l in enumerate(blPara.lines):
                    n = height+l.ascent-l.descent
                    if n>availHeight+1e-8:
                        break
                    height = n
                    s = i+1
            else:
                raise ValueError('invalid autoLeading value %r' % autoLeading)
        else:
            l = leading
            if autoLeading=='max':
                l = max(leading,1.2*style.fontSize)
            elif autoLeading=='min':
                l = 1.2*style.fontSize
            s = int(availHeight/(l*1.0))
            height = s*l

        allowOrphans = getattr(self,'allowOrphans',getattr(style,'allowOrphans',0))
        if (not allowOrphans and s<=1) or s==0: #orphan or not enough room
            del self.blPara
            return []
        n = len(lines)
        allowWidows = getattr(self,'allowWidows',getattr(style,'allowWidows',1))
        if n<=s:
            return [self]
        if not allowWidows:
            if n==s+1: #widow?
                if (allowOrphans and n==3) or n>3:
                    s -= 1  #give the widow some company
                else:
                    del self.blPara #no room for adjustment; force the whole para onwards
                    return []
        func = self._get_split_blParaFunc()

        if style.endDots:
            style1 = deepcopy(style)
            style1.endDots = None
        else:
            style1 = style
        P1=self.__class__(None,style1,bulletText=self.bulletText,frags=func(blPara,0,s))
        #this is a major hack
        P1.blPara = ParaLines(kind=1,lines=blPara.lines[0:s],aH=availHeight,aW=availWidth)
        P1._JustifyLast = 1
        P1._splitpara = 1
        P1.height = height
        P1.width = availWidth
        if style.firstLineIndent != 0:
            style = deepcopy(style)
            style.firstLineIndent = 0
        P2=self.__class__(None,style,bulletText=None,frags=func(blPara,s,n))
        #propagate attributes that might be on self; suggestion from Dirk Holtwick
        for a in ('autoLeading',    #possible attributes that might be directly on self.
                ):
            if hasattr(self,a):
                setattr(P1,a,getattr(self,a))
                setattr(P2,a,getattr(self,a))
        return [P1,P2]

    def draw(self):
        #call another method for historical reasons.  Besides, I
        #suspect I will be playing with alternate drawing routines
        #so not doing it here makes it easier to switch.
        self.drawPara(self.debug)

    def breakLines(self, width):
        """
        Returns a broken line structure. There are two cases

        A) For the simple case of a single formatting input fragment the output is
            A fragment specifier with
                - kind = 0
                - fontName, fontSize, leading, textColor
                - lines=  A list of lines

                        Each line has two items.

                        1. unused width in points
                        2. word list

        B) When there is more than one input formatting fragment the output is
            A fragment specifier with
               - kind = 1
               - lines=  A list of fragments each having fields
                            - extraspace (needed for justified)
                            - fontSize
                            - words=word list
                                each word is itself a fragment with
                                various settings

        This structure can be used to easily draw paragraphs with the various alignments.
        You can supply either a single width or a list of widths; the latter will have its
        last item repeated until necessary. A 2-element list is useful when there is a
        different first line indent; a longer list could be created to facilitate custom wraps
        around irregular objects."""

        if not isinstance(width,(tuple,list)): maxWidths = [width]
        else: maxWidths = width
        lines = []
        self.height = lineno = 0
        maxlineno = len(maxWidths)-1
        style = self.style
        splitLongWords = style.splitLongWords

        #for bullets, work out width and ensure we wrap the right amount onto line one
        _handleBulletWidth(self.bulletText,style,maxWidths)

        maxWidth = maxWidths[0]

        autoLeading = getattr(self,'autoLeading',getattr(style,'autoLeading',''))
        calcBounds = autoLeading not in ('','off')
        frags = self.frags
        nFrags= len(frags)
        if nFrags==1 and not (style.endDots or hasattr(frags[0],'cbDefn') or hasattr(frags[0],'backColor')):
            f = frags[0]
            fontSize = f.fontSize
            fontName = f.fontName
            ascent, descent = getAscentDescent(fontName,fontSize)
            if hasattr(f,'text'):
                text = strip(f.text)
                if not text:
                    return f.clone(kind=0, lines=[],ascent=ascent,descent=descent,fontSize=fontSize)
                else:
                    words = split(text)
            else:
                words = f.words[:]
                for w in words:
                    if strip(w): break
                else:
                    return f.clone(kind=0, lines=[],ascent=ascent,descent=descent,fontSize=fontSize)
            spaceWidth = stringWidth(' ', fontName, fontSize, self.encoding)
            cLine = []
            currentWidth = -spaceWidth   # hack to get around extra space for word 1
            while words:
                word = words.pop(0)
                #this underscores my feeling that Unicode throughout would be easier!
                wordWidth = stringWidth(word, fontName, fontSize, self.encoding)
                newWidth = currentWidth + spaceWidth + wordWidth
                if newWidth>maxWidth:
                    nmw = min(lineno,maxlineno)
                    if wordWidth>max(maxWidths[nmw:nmw+1]) and not isinstance(word,_SplitText) and splitLongWords:
                        #a long word
                        words[0:0] = _splitWord(word,maxWidth-spaceWidth-currentWidth,maxWidths,lineno,fontName,fontSize,self.encoding)
                        continue
                if newWidth <= maxWidth or not len(cLine):
                    # fit one more on this line
                    cLine.append(word)
                    currentWidth = newWidth
                else:
                    if currentWidth > self.width: self.width = currentWidth
                    #end of line
                    lines.append((maxWidth - currentWidth, cLine))
                    cLine = [word]
                    currentWidth = wordWidth
                    lineno += 1
                    maxWidth = maxWidths[min(maxlineno,lineno)]

            #deal with any leftovers on the final line
            if cLine!=[]:
                if currentWidth>self.width: self.width = currentWidth
                lines.append((maxWidth - currentWidth, cLine))

            return f.clone(kind=0, lines=lines,ascent=ascent,descent=descent,fontSize=fontSize)
        elif nFrags<=0:
            return ParaLines(kind=0, fontSize=style.fontSize, fontName=style.fontName,
                            textColor=style.textColor, ascent=style.fontSize,descent=-0.2*style.fontSize,
                            lines=[])
        else:
            if hasattr(self,'blPara') and getattr(self,'_splitpara',0):
                #NB this is an utter hack that awaits the proper information
                #preserving splitting algorithm
                return self.blPara
            n = 0
            words = []
            _words = _getFragWords(frags,maxWidth)
            while _words:
                w = _words.pop(0)
                f=w[-1][0]
                fontName = f.fontName
                fontSize = f.fontSize
                spaceWidth = stringWidth(' ',fontName, fontSize)

                if not words:
                    currentWidth = -spaceWidth   # hack to get around extra space for word 1
                    maxSize = fontSize
                    maxAscent, minDescent = getAscentDescent(fontName,fontSize)

                wordWidth = w[0]
                f = w[1][0]
                if wordWidth>0:
                    newWidth = currentWidth + spaceWidth + wordWidth
                else:
                    newWidth = currentWidth

                #test to see if this frag is a line break. If it is we will only act on it
                #if the current width is non-negative or the previous thing was a deliberate lineBreak
                lineBreak = hasattr(f,'lineBreak')
                if not lineBreak and newWidth>maxWidth and not isinstance(w,_SplitList) and splitLongWords:
                    nmw = min(lineno,maxlineno)
                    if wordWidth>max(maxWidths[nmw:nmw+1]):
                        #a long word
                        _words[0:0] = _splitFragWord(w,maxWidth-spaceWidth-currentWidth,maxWidths,lineno)
                        continue
                endLine = (newWidth>maxWidth and n>0) or lineBreak
                if not endLine:
                    if lineBreak: continue      #throw it away
                    nText = w[1][1]
                    if nText: n += 1
                    fontSize = f.fontSize
                    if calcBounds:
                        cbDefn = getattr(f,'cbDefn',None)
                        if getattr(cbDefn,'width',0):
                            descent,ascent = imgVRange(imgNormV(cbDefn.height,fontSize),cbDefn.valign,fontSize)
                        else:
                            ascent, descent = getAscentDescent(f.fontName,fontSize)
                    else:
                        ascent, descent = getAscentDescent(f.fontName,fontSize)
                    maxSize = max(maxSize,fontSize)
                    maxAscent = max(maxAscent,ascent)
                    minDescent = min(minDescent,descent)
                    if not words:
                        g = f.clone()
                        words = [g]
                        g.text = nText
                    elif not sameFrag(g,f):
                        if currentWidth>0 and ((nText!='' and nText[0]!=' ') or hasattr(f,'cbDefn')):
                            if hasattr(g,'cbDefn'):
                                i = len(words)-1
                                while i>=0:
                                    wi = words[i]
                                    cbDefn = getattr(wi,'cbDefn',None)
                                    if cbDefn:
                                        if not getattr(cbDefn,'width',0):
                                            i -= 1
                                            continue
                                    if not wi.text.endswith(' '):
                                        wi.text += ' '
                                    break
                            else:
                                if not g.text.endswith(' '):
                                    g.text += ' '
                        g = f.clone()
                        words.append(g)
                        g.text = nText
                    else:
                        if nText and nText[0]!=' ':
                            g.text += ' ' + nText

                    ni = 0
                    for i in w[2:]:
                        g = i[0].clone()
                        g.text=i[1]
                        if g.text: ni = 1
                        words.append(g)
                        fontSize = g.fontSize
                        if calcBounds:
                            cbDefn = getattr(g,'cbDefn',None)
                            if getattr(cbDefn,'width',0):
                                descent,ascent = imgVRange(imgNormV(cbDefn.height,fontSize),cbDefn.valign,fontSize)
                            else:
                                ascent, descent = getAscentDescent(g.fontName,fontSize)
                        else:
                            ascent, descent = getAscentDescent(g.fontName,fontSize)
                        maxSize = max(maxSize,fontSize)
                        maxAscent = max(maxAscent,ascent)
                        minDescent = min(minDescent,descent)
                    if not nText and ni:
                        #one bit at least of the word was real
                        n+=1

                    currentWidth = newWidth
                else:  #either it won't fit, or it's a lineBreak tag
                    if lineBreak:
                        g = f.clone()
                        #del g.lineBreak
                        words.append(g)

                    if currentWidth>self.width: self.width = currentWidth
                    #end of line
                    lines.append(FragLine(extraSpace=maxWidth-currentWidth, wordCount=n,
                                        lineBreak=lineBreak, words=words, fontSize=maxSize, ascent=maxAscent, descent=minDescent, maxWidth=maxWidth))

                    #start new line
                    lineno += 1
                    maxWidth = maxWidths[min(maxlineno,lineno)]

                    if lineBreak:
                        n = 0
                        words = []
                        continue

                    currentWidth = wordWidth
                    n = 1
                    g = f.clone()
                    maxSize = g.fontSize
                    if calcBounds:
                        cbDefn = getattr(g,'cbDefn',None)
                        if getattr(cbDefn,'width',0):
                            minDescent,maxAscent = imgVRange(imgNormV(cbDefn.height,fontSize),cbDefn.valign,maxSize)
                        else:
                            maxAscent, minDescent = getAscentDescent(g.fontName,maxSize)
                    else:
                        maxAscent, minDescent = getAscentDescent(g.fontName,maxSize)
                    words = [g]
                    g.text = w[1][1]

                    for i in w[2:]:
                        g = i[0].clone()
                        g.text=i[1]
                        words.append(g)
                        fontSize = g.fontSize
                        if calcBounds:
                            cbDefn = getattr(g,'cbDefn',None)
                            if getattr(cbDefn,'width',0):
                                descent,ascent = imgVRange(imgNormV(cbDefn.height,fontSize),cbDefn.valign,fontSize)
                            else:
                                ascent, descent = getAscentDescent(g.fontName,fontSize)
                        else:
                            ascent, descent = getAscentDescent(g.fontName,fontSize)
                        maxSize = max(maxSize,fontSize)
                        maxAscent = max(maxAscent,ascent)
                        minDescent = min(minDescent,descent)

            #deal with any leftovers on the final line
            if words!=[]:
                if currentWidth>self.width: self.width = currentWidth
                lines.append(ParaLines(extraSpace=(maxWidth - currentWidth),wordCount=n,
                                    words=words, fontSize=maxSize,ascent=maxAscent,descent=minDescent,maxWidth=maxWidth))
            return ParaLines(kind=1, lines=lines)

        return lines

    def breakLinesCJK(self, maxWidths):
        """Initially, the dumbest possible wrapping algorithm.
        Cannot handle font variations."""

        if not isinstance(maxWidths,(list,tuple)): maxWidths = [maxWidths]
        style = self.style
        self.height = 0

        #for bullets, work out width and ensure we wrap the right amount onto line one
        _handleBulletWidth(self.bulletText, style, maxWidths)
        frags = self.frags
        nFrags = len(frags)
        if nFrags==1 and not hasattr(frags[0],'cbDefn') and not style.endDots:
            f = frags[0]
            if hasattr(self,'blPara') and getattr(self,'_splitpara',0):
                return f.clone(kind=0, lines=self.blPara.lines)
            #single frag case
            lines = []
            lineno = 0
            if hasattr(f,'text'):
                text = f.text
            else:
                text = ''.join(getattr(f,'words',[]))

            from reportlab.lib.textsplit import wordSplit
            lines = wordSplit(text, maxWidths, f.fontName, f.fontSize)
            #the paragraph drawing routine assumes multiple frags per line, so we need an
            #extra list like this
            #  [space, [text]]
            #
            wrappedLines = [(sp, [line]) for (sp, line) in lines]
            return f.clone(kind=0, lines=wrappedLines, ascent=f.fontSize, descent=-0.2*f.fontSize)
        elif nFrags<=0:
            return ParaLines(kind=0, fontSize=style.fontSize, fontName=style.fontName,
                            textColor=style.textColor, lines=[],ascent=style.fontSize,descent=-0.2*style.fontSize)

        #general case nFrags>1 or special
        if hasattr(self,'blPara') and getattr(self,'_splitpara',0):
            return self.blPara
        autoLeading = getattr(self,'autoLeading',getattr(style,'autoLeading',''))
        calcBounds = autoLeading not in ('','off')
        return cjkFragSplit(frags, maxWidths, calcBounds)

    def beginText(self, x, y):
        return self.canv.beginText(x, y)

    def drawPara(self,debug=0):
        """Draws a paragraph according to the given style.
        Returns the final y position at the bottom. Not safe for
        paragraphs without spaces e.g. Japanese; wrapping
        algorithm will go infinite."""

        #stash the key facts locally for speed
        canvas = self.canv
        style = self.style
        blPara = self.blPara
        lines = blPara.lines
        leading = style.leading
        autoLeading = getattr(self,'autoLeading',getattr(style,'autoLeading',''))

        #work out the origin for line 1
        leftIndent = style.leftIndent
        cur_x = leftIndent

        if debug:
            bw = 0.5
            bc = Color(1,1,0)
            bg = Color(0.9,0.9,0.9)
        else:
            bw = getattr(style,'borderWidth',None)
            bc = getattr(style,'borderColor',None)
            bg = style.backColor

        #if has a background or border, draw it
        if bg or (bc and bw):
            canvas.saveState()
            op = canvas.rect
            kwds = dict(fill=0,stroke=0)
            if bc and bw:
                canvas.setStrokeColor(bc)
                canvas.setLineWidth(bw)
                kwds['stroke'] = 1
                br = getattr(style,'borderRadius',0)
                if br and not debug:
                    op = canvas.roundRect
                    kwds['radius'] = br
            if bg:
                canvas.setFillColor(bg)
                kwds['fill'] = 1
            bp = getattr(style,'borderPadding',0)
            tbp, rbp, bbp, lbp = normalizeTRBL(bp)
            op(leftIndent - lbp,
                        -bbp,
                        self.width - (leftIndent+style.rightIndent) + lbp+rbp,
                        self.height + tbp+bbp,
                        **kwds)
            canvas.restoreState()

        nLines = len(lines)
        bulletText = self.bulletText
        if nLines > 0:
            _offsets = getattr(self,'_offsets',[0])
            _offsets += (nLines-len(_offsets))*[_offsets[-1]]
            canvas.saveState()
            #canvas.addLiteral('%% %s.drawPara' % _className(self))
            alignment = style.alignment
            offset = style.firstLineIndent+_offsets[0]
            lim = nLines-1
            noJustifyLast = not (hasattr(self,'_JustifyLast') and self._JustifyLast)

            if blPara.kind==0:
                if alignment == TA_LEFT:
                    dpl = _leftDrawParaLine
                elif alignment == TA_CENTER:
                    dpl = _centerDrawParaLine
                elif self.style.alignment == TA_RIGHT:
                    dpl = _rightDrawParaLine
                elif self.style.alignment == TA_JUSTIFY:
                    dpl = _justifyDrawParaLine
                f = blPara
                if paraFontSizeHeightOffset:
                    cur_y = self.height - f.fontSize
                else:
                    cur_y = self.height - getattr(f,'ascent',f.fontSize)
                if bulletText:
                    offset = _drawBullet(canvas,offset,cur_y,bulletText,style,rtl=style.wordWrap=='RTL' and self._wrapWidths or False)

                #set up the font etc.
                canvas.setFillColor(f.textColor)

                tx = self.beginText(cur_x, cur_y)
                if style.underlineProportion:
                    tx._underlineProportion = style.underlineProportion
                    tx._do_line = _do_line
                else:
                    tx._do_line = _old_do_line
                tx._do_line = MethodType(tx._do_line,tx)
                if autoLeading=='max':
                    leading = max(leading,blPara.ascent-blPara.descent)
                elif autoLeading=='min':
                    leading = blPara.ascent-blPara.descent

                # set the paragraph direction
                tx.direction = self.style.wordWrap

                #now the font for the rest of the paragraph
                tx.setFont(f.fontName, f.fontSize, leading)
                ws = lines[0][0]
                t_off = dpl( tx, offset, ws, lines[0][1], noJustifyLast and nLines==1)
                if f.underline or f.link or f.strike or style.endDots:
                    xs = tx.XtraState = ABag()
                    xs.cur_y = cur_y
                    xs.f = f
                    xs.style = style
                    xs.lines = lines
                    xs.underlines=[]
                    xs.underlineColor=None
                    xs.strikes=[]
                    xs.strikeColor=None
                    xs.links=[]
                    xs.link=f.link
                    xs.textColor = f.textColor
                    xs.backColors = []
                    canvas.setStrokeColor(f.textColor)
                    dx = t_off+leftIndent
                    if dpl!=_justifyDrawParaLine: ws = 0
                    underline = f.underline or (f.link and platypus_link_underline)
                    strike = f.strike
                    link = f.link
                    if underline: _do_under_line(0, dx, ws, tx)
                    if strike: _do_under_line(0, dx, ws, tx, lm=0.125)
                    if link: _do_link_line(0, dx, ws, tx)
                    if noJustifyLast and nLines==1 and style.endDots and dpl!=_rightDrawParaLine: _do_dots(0, dx, ws, xs, tx, dpl)

                    #now the middle of the paragraph, aligned with the left margin which is our origin.
                    for i in xrange(1, nLines):
                        ws = lines[i][0]
                        t_off = dpl( tx, _offsets[i], ws, lines[i][1], noJustifyLast and i==lim)
                        dx = t_off+leftIndent
                        if dpl!=_justifyDrawParaLine: ws = 0
                        if underline: _do_under_line(i, dx, ws, tx)
                        if strike: _do_under_line(i, dx, ws, tx, lm=0.125)
                        if link: _do_link_line(i, dx, ws, tx)
                        if noJustifyLast and i==lim and style.endDots and dpl!=_rightDrawParaLine: _do_dots(i, dx, ws, xs, tx, dpl)
                else:
                    for i in xrange(1, nLines):
                        dpl( tx, _offsets[i], lines[i][0], lines[i][1], noJustifyLast and i==lim)
            else:
                if self.style.wordWrap == 'RTL':
                    for line in lines:
                        line.words = line.words[::-1]
                f = lines[0]
                if paraFontSizeHeightOffset:
                    cur_y = self.height - f.fontSize
                else:
                    cur_y = self.height - getattr(f,'ascent',f.fontSize)
                # default?
                dpl = _leftDrawParaLineX
                if bulletText:
                    oo = offset
                    offset = _drawBullet(canvas,offset,cur_y,bulletText,style, rtl=style.wordWrap=='RTL' and self._wrapWidths or False)
                if alignment == TA_LEFT:
                    dpl = _leftDrawParaLineX
                elif alignment == TA_CENTER:
                    dpl = _centerDrawParaLineX
                elif self.style.alignment == TA_RIGHT:
                    dpl = _rightDrawParaLineX
                elif self.style.alignment == TA_JUSTIFY:
                    dpl = _justifyDrawParaLineX
                else:
                    raise ValueError("bad align %s" % repr(alignment))

                #set up the font etc.
                tx = self.beginText(cur_x, cur_y)
                if style.underlineProportion:
                    tx._underlineProportion = style.underlineProportion
                    tx._do_line = _do_line
                else:
                    tx._do_line = _old_do_line
                tx._do_line = MethodType(tx._do_line,tx)
                # set the paragraph direction
                tx.direction = self.style.wordWrap

                xs = tx.XtraState=ABag()
                xs.textColor=None
                xs.backColor=None
                xs.rise=0
                xs.underline=0
                xs.underlines=[]
                xs.underlineColor=None
                xs.strike=0
                xs.strikes=[]
                xs.strikeColor=None
                xs.backColors=[]
                xs.links=[]
                xs.link=None
                xs.leading = style.leading
                xs.leftIndent = leftIndent
                tx._leading = None
                tx._olb = None
                xs.cur_y = cur_y
                xs.f = f
                xs.style = style
                xs.autoLeading = autoLeading

                tx._fontname,tx._fontsize = None, None
                dpl( tx, offset, lines[0], noJustifyLast and nLines==1)
                _do_post_text(tx)

                #now the middle of the paragraph, aligned with the left margin which is our origin.
                for i in xrange(1, nLines):
                    f = lines[i]
                    dpl( tx, _offsets[i], f, noJustifyLast and i==lim)
                    _do_post_text(tx)

            canvas.drawText(tx)
            canvas.restoreState()

    def getPlainText(self,identify=None):
        """Convenience function for templates which want access
        to the raw text, without XML tags. """
        frags = getattr(self,'frags',None)
        if frags:
            plains = []
            for frag in frags:
                if hasattr(frag, 'text'):
                    plains.append(frag.text)
            return ''.join(plains)
        elif identify:
            text = getattr(self,'text',None)
            if text is None: text = repr(self)
            return text
        else:
            return ''

    def getActualLineWidths0(self):
        """Convenience function; tells you how wide each line
        actually is.  For justified styles, this will be
        the same as the wrap width; for others it might be
        useful for seeing if paragraphs will fit in spaces."""
        assert hasattr(self, 'width'), "Cannot call this method before wrap()"
        if self.blPara.kind:
            func = lambda frag, w=self.width: w - frag.extraSpace
        else:
            func = lambda frag, w=self.width: w - frag[0]
        return list(map(func,self.blPara.lines))

if __name__=='__main__':    #NORUNTESTS
    def dumpParagraphLines(P):
        print('dumpParagraphLines(<Paragraph @ %d>)' % id(P))
        lines = P.blPara.lines
        outw = sys.stdout.write
        for l,line in enumerate(lines):
            line = lines[l]
            if hasattr(line,'words'):
                words = line.words
            else:
                words = line[1]
            nwords = len(words)
            outw('line%d: %d(%s)\n  ' % (l,nwords,str(getattr(line,'wordCount','Unknown'))))
            for w in xrange(nwords):
                outw(" %d:'%s'"%(w,getattr(words[w],'text',words[w])))
            print()

    def fragDump(w):
        R= ["'%s'" % w[1]]
        for a in ('fontName', 'fontSize', 'textColor', 'rise', 'underline', 'strike', 'link', 'cbDefn','lineBreak'):
            if hasattr(w[0],a):
                R.append('%s=%r' % (a,getattr(w[0],a)))
        return ', '.join(R)

    def dumpParagraphFrags(P):
        print('dumpParagraphFrags(<Paragraph @ %d>) minWidth() = %.2f' % (id(P), P.minWidth()))
        frags = P.frags
        n =len(frags)
        for l in xrange(n):
            print("frag%d: '%s' %s" % (l, frags[l].text,' '.join(['%s=%s' % (k,getattr(frags[l],k)) for k in frags[l].__dict__ if k!=text])))

        outw = sys.stdout.write
        l = 0
        cum = 0
        for W in _getFragWords(frags,360):
            cum += W[0]
            outw("fragword%d: cum=%3d size=%d" % (l, cum, W[0]))
            for w in W[1:]:
                outw(' (%s)' % fragDump(w))
            print()
            l += 1


    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    import sys
    TESTS = sys.argv[1:]
    if TESTS==[]: TESTS=['4']
    def flagged(i,TESTS=TESTS):
        return 'all' in TESTS or '*' in TESTS or str(i) in TESTS

    styleSheet = getSampleStyleSheet()
    B = styleSheet['BodyText']
    style = ParagraphStyle("discussiontext", parent=B)
    style.fontName= 'Helvetica'
    if flagged(1):
        text='''The <font name=courier color=green>CMYK</font> or subtractive method follows the way a printer
mixes three pigments (cyan, magenta, and yellow) to form colors.
Because mixing chemicals is more difficult than combining light there
is a fourth parameter for darkness.  For example a chemical
combination of the <font name=courier color=green>CMY</font> pigments generally never makes a perfect
black -- instead producing a muddy color -- so, to get black printers
don't use the <font name=courier color=green>CMY</font> pigments but use a direct black ink.  Because
<font name=courier color=green>CMYK</font> maps more directly to the way printer hardware works it may
be the case that &amp;| &amp; | colors specified in <font name=courier color=green>CMYK</font> will provide better fidelity
and better control when printed.
'''
        P=Paragraph(text,style)
        dumpParagraphFrags(P)
        aW, aH = 456.0, 42.8
        w,h = P.wrap(aW, aH)
        dumpParagraphLines(P)
        S = P.split(aW,aH)
        for s in S:
            s.wrap(aW,aH)
            dumpParagraphLines(s)
            aH = 500

    if flagged(2):
        P=Paragraph("""Price<super><font color="red">*</font></super>""", styleSheet['Normal'])
        dumpParagraphFrags(P)
        w,h = P.wrap(24, 200)
        dumpParagraphLines(P)

    if flagged(3):
        text = """Dieses Kapitel bietet eine schnelle <b><font color=red>Programme :: starten</font></b>
<onDraw name=myIndex label="Programme :: starten">
<b><font color=red>Eingabeaufforderung :: (&gt;&gt;&gt;)</font></b>
<onDraw name=myIndex label="Eingabeaufforderung :: (&gt;&gt;&gt;)">
<b><font color=red>&gt;&gt;&gt; (Eingabeaufforderung)</font></b>
<onDraw name=myIndex label="&gt;&gt;&gt; (Eingabeaufforderung)">
Einf&#xfc;hrung in Python <b><font color=red>Python :: Einf&#xfc;hrung</font></b>
<onDraw name=myIndex label="Python :: Einf&#xfc;hrung">.
Das Ziel ist, die grundlegenden Eigenschaften von Python darzustellen, ohne
sich zu sehr in speziellen Regeln oder Details zu verstricken. Dazu behandelt
dieses Kapitel kurz die wesentlichen Konzepte wie Variablen, Ausdr&#xfc;cke,
Kontrollfluss, Funktionen sowie Ein- und Ausgabe. Es erhebt nicht den Anspruch,
umfassend zu sein."""
        P=Paragraph(text, styleSheet['Code'])
        dumpParagraphFrags(P)
        w,h = P.wrap(6*72, 9.7*72)
        dumpParagraphLines(P)

    if flagged(4):
        text='''Die eingebaute Funktion <font name=Courier>range(i, j [, stride])</font><onDraw name=myIndex label="eingebaute Funktionen::range()"><onDraw name=myIndex label="range() (Funktion)"><onDraw name=myIndex label="Funktionen::range()"> erzeugt eine Liste von Ganzzahlen und f&#xfc;llt sie mit Werten <font name=Courier>k</font>, f&#xfc;r die gilt: <font name=Courier>i &lt;= k &lt; j</font>. Man kann auch eine optionale Schrittweite angeben. Die eingebaute Funktion <font name=Courier>xrange()</font><onDraw name=myIndex label="eingebaute Funktionen::xrange()"><onDraw name=myIndex label="xrange() (Funktion)"><onDraw name=myIndex label="Funktionen::xrange()"> erf&#xfc;llt einen &#xe4;hnlichen Zweck, gibt aber eine unver&#xe4;nderliche Sequenz vom Typ <font name=Courier>XRangeType</font><onDraw name=myIndex label="XRangeType"> zur&#xfc;ck. Anstatt alle Werte in der Liste abzuspeichern, berechnet diese Liste ihre Werte, wann immer sie angefordert werden. Das ist sehr viel speicherschonender, wenn mit sehr langen Listen von Ganzzahlen gearbeitet wird. <font name=Courier>XRangeType</font> kennt eine einzige Methode, <font name=Courier>s.tolist()</font><onDraw name=myIndex label="XRangeType::tolist() (Methode)"><onDraw name=myIndex label="s.tolist() (Methode)"><onDraw name=myIndex label="Methoden::s.tolist()">, die seine Werte in eine Liste umwandelt.'''
        aW = 420
        aH = 64.4
        P=Paragraph(text, B)
        dumpParagraphFrags(P)
        w,h = P.wrap(aW,aH)
        print('After initial wrap',w,h)
        dumpParagraphLines(P)
        S = P.split(aW,aH)
        dumpParagraphFrags(S[0])
        w0,h0 = S[0].wrap(aW,aH)
        print('After split wrap',w0,h0)
        dumpParagraphLines(S[0])

    if flagged(5):
        text = '<para> %s <![CDATA[</font></b>& %s < >]]></para>' % (chr(163),chr(163))
        P=Paragraph(text, styleSheet['Code'])
        dumpParagraphFrags(P)
        w,h = P.wrap(6*72, 9.7*72)
        dumpParagraphLines(P)

    if flagged(6):
        for text in ['''Here comes <FONT FACE="Helvetica" SIZE="14pt">Helvetica 14</FONT> with <STRONG>strong</STRONG> <EM>emphasis</EM>.''',
                     '''Here comes <font face="Helvetica" size="14pt">Helvetica 14</font> with <Strong>strong</Strong> <em>emphasis</em>.''',
                     '''Here comes <font face="Courier" size="3cm">Courier 3cm</font> and normal again.''',
                     ]:
            P=Paragraph(text, styleSheet['Normal'], caseSensitive=0)
            dumpParagraphFrags(P)
            w,h = P.wrap(6*72, 9.7*72)
            dumpParagraphLines(P)

    if flagged(7):
        text = """<para align="CENTER" fontSize="24" leading="30"><b>Generated by:</b>Dilbert</para>"""
        P=Paragraph(text, styleSheet['Code'])
        dumpParagraphFrags(P)
        w,h = P.wrap(6*72, 9.7*72)
        dumpParagraphLines(P)

    if flagged(8):
        text ="""- bullet 0<br/>- bullet 1<br/>- bullet 2<br/>- bullet 3<br/>- bullet 4<br/>- bullet 5"""
        P=Paragraph(text, styleSheet['Normal'])
        dumpParagraphFrags(P)
        w,h = P.wrap(6*72, 9.7*72)
        dumpParagraphLines(P)
        S = P.split(6*72,h/2.0)
        print(len(S))
        dumpParagraphLines(S[0])
        dumpParagraphLines(S[1])


    if flagged(9):
        text="""Furthermore, the fundamental error of
regarding <img src="../docs/images/testimg.gif" width="3" height="7"/> functional notions as
categorial delimits a general
convention regarding the forms of the<br/>
grammar. I suggested that these results
would follow from the assumption that"""
        P=Paragraph(text,ParagraphStyle('aaa',parent=styleSheet['Normal'],align=TA_JUSTIFY))
        dumpParagraphFrags(P)
        w,h = P.wrap(6*cm-12, 9.7*72)
        dumpParagraphLines(P)

    if flagged(10):
        text="""a b c\xc2\xa0d e f"""
        P=Paragraph(text,ParagraphStyle('aaa',parent=styleSheet['Normal'],align=TA_JUSTIFY))
        dumpParagraphFrags(P)
        w,h = P.wrap(6*cm-12, 9.7*72)
        dumpParagraphLines(P)

    if flagged(11):
        text="""This page tests out a number of attributes of the <b>paraStyle</b><onDraw name="_indexAdd" label="paraStyle"/> tag.
This paragraph is in a style we have called "style1". It should be a normal <onDraw name="_indexAdd" label="normal"/> paragraph, set in Courier 12 pt.
It should be a normal<onDraw name="_indexAdd" label="normal"/> paragraph, set in Courier (not bold).
It should be a normal<onDraw name="_indexAdd" label="normal"/> paragraph, set in Courier 12 pt."""
        P=Paragraph(text,style=ParagraphStyle('style1',fontName="Courier",fontSize=10))
        dumpParagraphFrags(P)
        w,h = P.wrap(6.27*72-12,10000)
        dumpParagraphLines(P)
