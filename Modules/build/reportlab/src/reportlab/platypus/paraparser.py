#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/platypus/paraparser.py
__version__=''' $Id$ '''
__doc__='''The parser used to process markup within paragraphs'''
import string
import re
import sys
import os
import copy
import base64
from pprint import pprint as pp
import unicodedata
import reportlab.lib.sequencer

from reportlab.lib.abag import ABag
from reportlab.lib.utils import ImageReader, isPy3, annotateException, encode_label, asUnicode, asBytes, uniChr
from reportlab.lib.colors import toColor, white, black, red, Color
from reportlab.lib.fonts import tt2ps, ps2tt
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch,mm,cm,pica
if isPy3:
    from html.parser import HTMLParser
    from html.entities import name2codepoint
else:
    from HTMLParser import HTMLParser
    from htmlentitydefs import name2codepoint

_re_para = re.compile(r'^\s*<\s*para(?:\s+|>|/>)')

sizeDelta = 2       # amount to reduce font size by for super and sub script
subFraction = 0.5   # fraction of font size that a sub script should be lowered
superFraction = 0.5 # fraction of font size that a super script should be raised

DEFAULT_INDEX_NAME='_indexAdd'

def _convnum(s, unit=1, allowRelative=True):
    if s[0] in ('+','-') and allowRelative:
        try:
            return ('relative',int(s)*unit)
        except ValueError:
            return ('relative',float(s)*unit)
    else:
        try:
            return int(s)*unit
        except ValueError:
            return float(s)*unit

def _num(s, unit=1, allowRelative=True):
    """Convert a string like '10cm' to an int or float (in points).
       The default unit is point, but optionally you can use other
       default units like mm.
    """
    if s.endswith('cm'):
        unit=cm
        s = s[:-2]
    if s.endswith('in'):
        unit=inch
        s = s[:-2]
    if s.endswith('pt'):
        unit=1
        s = s[:-2]
    if s.endswith('i'):
        unit=inch
        s = s[:-1]
    if s.endswith('mm'):
        unit=mm
        s = s[:-2]
    if s.endswith('pica'):
        unit=pica
        s = s[:-4]
    return _convnum(s,unit,allowRelative)

def _numpct(s,unit=1,allowRelative=False):
    if s.endswith('%'):
        return _PCT(_convnum(s[:-1],allowRelative=allowRelative))
    else:
        return _num(s,unit,allowRelative)

class _PCT:
    def __init__(self,v):
        self._value = v*0.01

    def normalizedValue(self,normalizer):
        normalizer = normalizer or getattr(self,'_normalizer')
        return normalizer*self._value

def _valignpc(s):
    s = s.lower()
    if s in ('baseline','sub','super','top','text-top','middle','bottom','text-bottom'):
        return s
    if s.endswith('%'):
        n = _convnum(s[:-1])
        if isinstance(n,tuple):
            n = n[1]
        return _PCT(n)
    n = _num(s)
    if isinstance(n,tuple):
        n = n[1]
    return n

def _autoLeading(x):
    x = x.lower()
    if x in ('','min','max','off'):
        return x
    raise ValueError('Invalid autoLeading=%r' % x )

def _align(s):
    s = s.lower()
    if s=='left': return TA_LEFT
    elif s=='right': return TA_RIGHT
    elif s=='justify': return TA_JUSTIFY
    elif s in ('centre','center'): return TA_CENTER
    else: raise ValueError('illegal alignment %r' % s)

def _bAnchor(s):
    s = s.lower()
    if not s in ('start','middle','end','numeric'):
        raise ValueError('illegal bullet anchor %r' % s)
    return s

_paraAttrMap = {'font': ('fontName', None),
                'face': ('fontName', None),
                'fontsize': ('fontSize', _num),
                'size': ('fontSize', _num),
                'leading': ('leading', _num),
                'autoleading': ('autoLeading', _autoLeading),
                'lindent': ('leftIndent', _num),
                'rindent': ('rightIndent', _num),
                'findent': ('firstLineIndent', _num),
                'align': ('alignment', _align),
                'spaceb': ('spaceBefore', _num),
                'spacea': ('spaceAfter', _num),
                'bfont': ('bulletFontName', None),
                'bfontsize': ('bulletFontSize',_num),
                'boffsety': ('bulletOffsetY',_num),
                'bindent': ('bulletIndent',_num),
                'bcolor': ('bulletColor',toColor),
                'banchor': ('bulletAnchor',_bAnchor),
                'color':('textColor',toColor),
                'backcolor':('backColor',toColor),
                'bgcolor':('backColor',toColor),
                'bg':('backColor',toColor),
                'fg': ('textColor',toColor),
                }

_bulletAttrMap = {
                'font': ('bulletFontName', None),
                'face': ('bulletFontName', None),
                'size': ('bulletFontSize',_num),
                'fontsize': ('bulletFontSize',_num),
                'offsety': ('bulletOffsetY',_num),
                'indent': ('bulletIndent',_num),
                'color': ('bulletColor',toColor),
                'fg': ('bulletColor',toColor),
                'anchor': ('bulletAnchor',_bAnchor),
                }

#things which are valid font attributes
_fontAttrMap = {'size': ('fontSize', _num),
                'face': ('fontName', None),
                'name': ('fontName', None),
                'fg':   ('textColor', toColor),
                'color':('textColor', toColor),
                'backcolor':('backColor',toColor),
                'bgcolor':('backColor',toColor),
                }
#things which are valid span attributes
_spanAttrMap = {'size': ('fontSize', _num),
                'face': ('fontName', None),
                'name': ('fontName', None),
                'fg':   ('textColor', toColor),
                'color':('textColor', toColor),
                'backcolor':('backColor',toColor),
                'bgcolor':('backColor',toColor),
                'style': ('style',None),
                }
#things which are valid font attributes
_linkAttrMap = {'size': ('fontSize', _num),
                'face': ('fontName', None),
                'name': ('fontName', None),
                'fg':   ('textColor', toColor),
                'color':('textColor', toColor),
                'backcolor':('backColor',toColor),
                'bgcolor':('backColor',toColor),
                'dest': ('link', None),
                'destination': ('link', None),
                'target': ('link', None),
                'href': ('link', None),
                }
_anchorAttrMap = {'fontSize': ('fontSize', _num),
                'fontName': ('fontName', None),
                'name': ('name', None),
                'fg':   ('textColor', toColor),
                'color':('textColor', toColor),
                'backcolor':('backColor',toColor),
                'bgcolor':('backColor',toColor),
                'href': ('href', None),
                }
_imgAttrMap = {
                'src': ('src', None),
                'width': ('width',_numpct),
                'height':('height',_numpct),
                'valign':('valign',_valignpc),
                }
_indexAttrMap = {
                'name': ('name',None),
                'item': ('item',None),
                'offset': ('offset',None),
                'format': ('format',None),
                }

def _addAttributeNames(m):
    K = list(m.keys())
    for k in K:
        n = m[k][0]
        if n not in m: m[n] = m[k]
        n = n.lower()
        if n not in m: m[n] = m[k]

_addAttributeNames(_paraAttrMap)
_addAttributeNames(_fontAttrMap)
_addAttributeNames(_spanAttrMap)
_addAttributeNames(_bulletAttrMap)
_addAttributeNames(_anchorAttrMap)
_addAttributeNames(_linkAttrMap)

def _applyAttributes(obj, attr):
    for k, v in attr.items():
        if isinstance(v,(list,tuple)) and v[0]=='relative':
            if hasattr(obj, k):
                v = v[1]+getattr(obj,k)
            else:
                v = v[1]
        setattr(obj,k,v)

#Named character entities intended to be supported from the special font
#with additions suggested by Christoph Zwerschke who also suggested the
#numeric entity names that follow.
greeks = {
    'Aacute': u'\xc1',
    'aacute': u'\xe1',
    'Acirc': u'\xc2',
    'acirc': u'\xe2',
    'acute': u'\xb4',
    'AElig': u'\xc6',
    'aelig': u'\xe6',
    'Agrave': u'\xc0',
    'agrave': u'\xe0',
    'alefsym': u'\u2135',
    'Alpha': u'\u0391',
    'alpha': u'\u03b1',
    'and': u'\u2227',
    'ang': u'\u2220',
    'Aring': u'\xc5',
    'aring': u'\xe5',
    'asymp': u'\u2248',
    'Atilde': u'\xc3',
    'atilde': u'\xe3',
    'Auml': u'\xc4',
    'auml': u'\xe4',
    'bdquo': u'\u201e',
    'Beta': u'\u0392',
    'beta': u'\u03b2',
    'brvbar': u'\xa6',
    'bull': u'\u2022',
    'cap': u'\u2229',
    'Ccedil': u'\xc7',
    'ccedil': u'\xe7',
    'cedil': u'\xb8',
    'cent': u'\xa2',
    'Chi': u'\u03a7',
    'chi': u'\u03c7',
    'circ': u'\u02c6',
    'clubs': u'\u2663',
    'cong': u'\u2245',
    'copy': u'\xa9',
    'crarr': u'\u21b5',
    'cup': u'\u222a',
    'curren': u'\xa4',
    'dagger': u'\u2020',
    'Dagger': u'\u2021',
    'darr': u'\u2193',
    'dArr': u'\u21d3',
    'deg': u'\xb0',
    'delta': u'\u03b4',
    'Delta': u'\u2206',
    'diams': u'\u2666',
    'divide': u'\xf7',
    'Eacute': u'\xc9',
    'eacute': u'\xe9',
    'Ecirc': u'\xca',
    'ecirc': u'\xea',
    'Egrave': u'\xc8',
    'egrave': u'\xe8',
    'empty': u'\u2205',
    'emsp': u'\u2003',
    'ensp': u'\u2002',
    'Epsilon': u'\u0395',
    'epsilon': u'\u03b5',
    'epsiv': u'\u03b5',
    'equiv': u'\u2261',
    'Eta': u'\u0397',
    'eta': u'\u03b7',
    'ETH': u'\xd0',
    'eth': u'\xf0',
    'Euml': u'\xcb',
    'euml': u'\xeb',
    'euro': u'\u20ac',
    'exist': u'\u2203',
    'fnof': u'\u0192',
    'forall': u'\u2200',
    'frac12': u'\xbd',
    'frac14': u'\xbc',
    'frac34': u'\xbe',
    'frasl': u'\u2044',
    'Gamma': u'\u0393',
    'gamma': u'\u03b3',
    'ge': u'\u2265',
    'harr': u'\u2194',
    'hArr': u'\u21d4',
    'hearts': u'\u2665',
    'hellip': u'\u2026',
    'Iacute': u'\xcd',
    'iacute': u'\xed',
    'Icirc': u'\xce',
    'icirc': u'\xee',
    'iexcl': u'\xa1',
    'Igrave': u'\xcc',
    'igrave': u'\xec',
    'image': u'\u2111',
    'infin': u'\u221e',
    'int': u'\u222b',
    'Iota': u'\u0399',
    'iota': u'\u03b9',
    'iquest': u'\xbf',
    'isin': u'\u2208',
    'Iuml': u'\xcf',
    'iuml': u'\xef',
    'Kappa': u'\u039a',
    'kappa': u'\u03ba',
    'Lambda': u'\u039b',
    'lambda': u'\u03bb',
    'lang': u'\u2329',
    'laquo': u'\xab',
    'larr': u'\u2190',
    'lArr': u'\u21d0',
    'lceil': u'\uf8ee',
    'ldquo': u'\u201c',
    'le': u'\u2264',
    'lfloor': u'\uf8f0',
    'lowast': u'\u2217',
    'loz': u'\u25ca',
    'lrm': u'\u200e',
    'lsaquo': u'\u2039',
    'lsquo': u'\u2018',
    'macr': u'\xaf',
    'mdash': u'\u2014',
    'micro': u'\xb5',
    'middot': u'\xb7',
    'minus': u'\u2212',
    'mu': u'\xb5',
    'Mu': u'\u039c',
    'nabla': u'\u2207',
    'nbsp': u'\xa0',
    'ndash': u'\u2013',
    'ne': u'\u2260',
    'ni': u'\u220b',
    'notin': u'\u2209',
    'not': u'\xac',
    'nsub': u'\u2284',
    'Ntilde': u'\xd1',
    'ntilde': u'\xf1',
    'Nu': u'\u039d',
    'nu': u'\u03bd',
    'Oacute': u'\xd3',
    'oacute': u'\xf3',
    'Ocirc': u'\xd4',
    'ocirc': u'\xf4',
    'OElig': u'\u0152',
    'oelig': u'\u0153',
    'Ograve': u'\xd2',
    'ograve': u'\xf2',
    'oline': u'\uf8e5',
    'omega': u'\u03c9',
    'Omega': u'\u2126',
    'Omicron': u'\u039f',
    'omicron': u'\u03bf',
    'oplus': u'\u2295',
    'ordf': u'\xaa',
    'ordm': u'\xba',
    'or': u'\u2228',
    'Oslash': u'\xd8',
    'oslash': u'\xf8',
    'Otilde': u'\xd5',
    'otilde': u'\xf5',
    'otimes': u'\u2297',
    'Ouml': u'\xd6',
    'ouml': u'\xf6',
    'para': u'\xb6',
    'part': u'\u2202',
    'permil': u'\u2030',
    'perp': u'\u22a5',
    'phis': u'\u03c6',
    'Phi': u'\u03a6',
    'phi': u'\u03d5',
    'piv': u'\u03d6',
    'Pi': u'\u03a0',
    'pi': u'\u03c0',
    'plusmn': u'\xb1',
    'pound': u'\xa3',
    'prime': u'\u2032',
    'Prime': u'\u2033',
    'prod': u'\u220f',
    'prop': u'\u221d',
    'Psi': u'\u03a8',
    'psi': u'\u03c8',
    'radic': u'\u221a',
    'rang': u'\u232a',
    'raquo': u'\xbb',
    'rarr': u'\u2192',
    'rArr': u'\u21d2',
    'rceil': u'\uf8f9',
    'rdquo': u'\u201d',
    'real': u'\u211c',
    'reg': u'\xae',
    'rfloor': u'\uf8fb',
    'Rho': u'\u03a1',
    'rho': u'\u03c1',
    'rlm': u'\u200f',
    'rsaquo': u'\u203a',
    'rsquo': u'\u2019',
    'sbquo': u'\u201a',
    'Scaron': u'\u0160',
    'scaron': u'\u0161',
    'sdot': u'\u22c5',
    'sect': u'\xa7',
    'shy': u'\xad',
    'sigmaf': u'\u03c2',
    'sigmav': u'\u03c2',
    'Sigma': u'\u03a3',
    'sigma': u'\u03c3',
    'sim': u'\u223c',
    'spades': u'\u2660',
    'sube': u'\u2286',
    'sub': u'\u2282',
    'sum': u'\u2211',
    'sup1': u'\xb9',
    'sup2': u'\xb2',
    'sup3': u'\xb3',
    'supe': u'\u2287',
    'sup': u'\u2283',
    'szlig': u'\xdf',
    'Tau': u'\u03a4',
    'tau': u'\u03c4',
    'there4': u'\u2234',
    'thetasym': u'\u03d1',
    'thetav': u'\u03d1',
    'Theta': u'\u0398',
    'theta': u'\u03b8',
    'thinsp': u'\u2009',
    'THORN': u'\xde',
    'thorn': u'\xfe',
    'tilde': u'\u02dc',
    'times': u'\xd7',
    'trade': u'\uf8ea',
    'Uacute': u'\xda',
    'uacute': u'\xfa',
    'uarr': u'\u2191',
    'uArr': u'\u21d1',
    'Ucirc': u'\xdb',
    'ucirc': u'\xfb',
    'Ugrave': u'\xd9',
    'ugrave': u'\xf9',
    'uml': u'\xa8',
    'upsih': u'\u03d2',
    'Upsilon': u'\u03a5',
    'upsilon': u'\u03c5',
    'Uuml': u'\xdc',
    'uuml': u'\xfc',
    'weierp': u'\u2118',
    'Xi': u'\u039e',
    'xi': u'\u03be',
    'Yacute': u'\xdd',
    'yacute': u'\xfd',
    'yen': u'\xa5',
    'yuml': u'\xff',
    'Yuml': u'\u0178',
    'Zeta': u'\u0396',
    'zeta': u'\u03b6',
    'zwj': u'\u200d',
    'zwnj': u'\u200c',
    }

known_entities = dict([(k,uniChr(v)) for k,v in name2codepoint.items()])
for k in greeks:
    if k not in known_entities:
        known_entities[k] = greeks[k]
f = isPy3 and asBytes or asUnicode
K = list(known_entities.keys())
for k in K:
    known_entities[f(k)] = known_entities[k]
del k, f, K

#------------------------------------------------------------------------
class ParaFrag(ABag):
    """class ParaFrag contains the intermediate representation of string
    segments as they are being parsed by the ParaParser.
    fontname, fontSize, rise, textColor, cbDefn
    """

_greek2Utf8=None
def _greekConvert(data):
    global _greek2Utf8
    if not _greek2Utf8:
        from reportlab.pdfbase.rl_codecs import RL_Codecs
        import codecs
        #our decoding map
        dm = codecs.make_identity_dict(range(32,256))
        for k in range(0,32):
            dm[k] = None
        dm.update(RL_Codecs._RL_Codecs__rl_codecs_data['symbol'][0])
        _greek2Utf8 = {}
        for k,v in dm.items():
            if not v:
                u = '\0'
            else:
                if isPy3:
                    u = chr(v)
                else:
                    u = unichr(v).encode('utf8')
            _greek2Utf8[chr(k)] = u
    return ''.join(map(_greek2Utf8.__getitem__,data))

#------------------------------------------------------------------
# !!! NOTE !!! THIS TEXT IS NOW REPLICATED IN PARAGRAPH.PY !!!
# The ParaFormatter will be able to format the following
# tags:
#       < /b > - bold
#       < /i > - italics
#       < u > < /u > - underline
#       < strike > < /strike > - strike through
#       < super > < /super > - superscript
#       < sup > < /sup > - superscript
#       < sub > < /sub > - subscript
#       <font name=fontfamily/fontname color=colorname size=float>
#        <span name=fontfamily/fontname color=colorname backcolor=colorname size=float style=stylename>
#       < bullet > </bullet> - bullet text (at head of para only)
#       <onDraw name=callable label="a label"/>
#       <index [name="callablecanvasattribute"] label="a label"/>
#       <link>link text</link>
#           attributes of links 
#               size/fontSize=num
#               name/face/fontName=name
#               fg/textColor/color=color
#               backcolor/backColor/bgcolor=color
#               dest/destination/target/href/link=target
#       <a>anchor text</a>
#           attributes of anchors 
#               fontSize=num
#               fontName=name
#               fg/textColor/color=color
#               backcolor/backColor/bgcolor=color
#               href=href
#       <a name="anchorpoint"/>
#       <unichar name="unicode character name"/>
#       <unichar value="unicode code point"/>
#       <img src="path" width="1in" height="1in" valign="bottom"/>
#               width="w%" --> fontSize*w/100   idea from Roberto Alsina
#               height="h%" --> linewidth*h/100 <ralsina@netmanagers.com.ar>
#       <greek> - </greek>
#
#       The whole may be surrounded by <para> </para> tags
#
# It will also be able to handle any MathML specified Greek characters.
#------------------------------------------------------------------
class ParaParser(HTMLParser):

    #----------------------------------------------------------
    # First we will define all of the xml tag handler functions.
    #
    # start_<tag>(attributes)
    # end_<tag>()
    #
    # While parsing the xml ParaFormatter will call these
    # functions to handle the string formatting tags.
    # At the start of each tag the corresponding field will
    # be set to 1 and at the end tag the corresponding field will
    # be set to 0.  Then when handle_data is called the options
    # for that data will be aparent by the current settings.
    #----------------------------------------------------------

    def __getattr__( self, attrName ):
        """This way we can handle <TAG> the same way as <tag> (ignoring case)."""
        if attrName!=attrName.lower() and attrName!="caseSensitive" and not self.caseSensitive and \
            (attrName.startswith("start_") or attrName.startswith("end_")):
                return getattr(self,attrName.lower())
        raise AttributeError(attrName)

    #### bold
    def start_b( self, attributes ):
        self._push('b',bold=1)

    def end_b( self ):
        self._pop('b')

    def start_strong( self, attributes ):
        self._push('strong',bold=1)

    def end_strong( self ):
        self._pop('strong')

    #### italics
    def start_i( self, attributes ):
        self._push('i',italic=1)

    def end_i( self ):
        self._pop('i')

    def start_em( self, attributes ):
        self._push('em', italic=1)

    def end_em( self ):
        self._pop('em')

    #### underline
    def start_u( self, attributes ):
        self._push('u',underline=1)

    def end_u( self ):
        self._pop('u')

    #### strike
    def start_strike( self, attributes ):
        self._push('strike',strike=1)

    def end_strike( self ):
        self._pop('strike')

    #### link
    def start_link(self, attributes):
        self._push('link',**self.getAttributes(attributes,_linkAttrMap))

    def end_link(self):
        if self._pop('link').link is None:
            raise ValueError('<link> has no target or href')

    #### anchor
    def start_a(self, attributes):
        A = self.getAttributes(attributes,_anchorAttrMap)
        name = A.get('name',None)
        if name is not None:
            name = name.strip()
            if not name:
                self._syntax_error('<a name="..."/> anchor variant requires non-blank name')
            if len(A)>1:
                self._syntax_error('<a name="..."/> anchor variant only allows name attribute')
                A = dict(name=A['name'])
            A['_selfClosingTag'] = 'anchor'
        else:
            href = A.get('href','').strip()
            A['link'] = href    #convert to our link form
            A.pop('href',None)
        self._push('a',**A)

    def end_a(self):
        frag = self._stack[-1]
        sct = getattr(frag,'_selfClosingTag','')
        if sct:
            if not (sct=='anchor' and frag.name):
                raise ValueError('Parser failure in <a/>')
            defn = frag.cbDefn = ABag()
            defn.label = defn.kind = 'anchor'
            defn.name = frag.name
            del frag.name, frag._selfClosingTag
            self.handle_data('')
            self._pop('a')
        else:
            if self._pop('a').link is None:
                raise ValueError('<link> has no href')

    def start_img(self,attributes):
        A = self.getAttributes(attributes,_imgAttrMap)
        if not A.get('src'):
            self._syntax_error('<img> needs src attribute')
        A['_selfClosingTag'] = 'img'
        self._push('img',**A)

    def end_img(self):
        frag = self._stack[-1]
        if not getattr(frag,'_selfClosingTag',''):
            raise ValueError('Parser failure in <img/>')
        defn = frag.cbDefn = ABag()
        defn.kind = 'img'
        defn.src = getattr(frag,'src',None)
        defn.image = ImageReader(defn.src)
        size = defn.image.getSize()
        defn.width = getattr(frag,'width',size[0])
        defn.height = getattr(frag,'height',size[1])
        defn.valign = getattr(frag,'valign','bottom')
        del frag._selfClosingTag
        self.handle_data('')
        self._pop('img')

    #### super script
    def start_super( self, attributes ):
        self._push('super',super=1)

    def end_super( self ):
        self._pop('super')

    def start_sup( self, attributes ):
        self._push('sup',super=1)

    def end_sup( self ):
        self._pop('sup')

    #### sub script
    def start_sub( self, attributes ):
        self._push('sub',sub=1)

    def end_sub( self ):
        self._pop('sub')

    #### greek script
    #### add symbol encoding
    def handle_charref(self, name):
        try:
            if name[0]=='x':
                n = int(name[1:],16)
            else:
                n = int(name)
        except ValueError:
            self.unknown_charref(name)
            return
        self.handle_data(uniChr(n))   #.encode('utf8'))

    def syntax_error(self,lineno,message):
        self._syntax_error(message)

    def _syntax_error(self,message):
        if message[:10]=="attribute " and message[-17:]==" value not quoted": return
        self.errors.append(message)

    def start_greek(self, attr):
        self._push('greek',greek=1)

    def end_greek(self):
        self._pop('greek')

    def start_unichar(self, attr):
        if 'name' in attr:
            if 'code' in attr:
                self._syntax_error('<unichar/> invalid with both name and code attributes')
            try:
                v = unicodedata.lookup(attr['name'])
            except KeyError:
                self._syntax_error('<unichar/> invalid name attribute\n"%s"' % ascii(attr['name']))
                v = '\0'
        elif 'code' in attr:
            try:
                v = int(eval(attr['code']))
                v = chr(v) if isPy3 else unichr(v)
            except:
                self._syntax_error('<unichar/> invalid code attribute %s' % ascii(attr['code']))
                v = '\0'
        else:
            v = None
            if attr:
                self._syntax_error('<unichar/> invalid attribute %s' % list(attr.keys())[0])

        if v is not None:
            self.handle_data(v)
        self._push('unichar',_selfClosingTag='unichar')

    def end_unichar(self):
        self._pop('unichar')

    def start_font(self,attr):
        A = self.getAttributes(attr,_spanAttrMap)
        if 'fontName' in A:
            A['fontName'], A['bold'], A['italic'] = ps2tt(A['fontName'])
        self._push('font',**A)

    def end_font(self):
        self._pop('font')

    def start_span(self,attr):
        A = self.getAttributes(attr,_spanAttrMap)
        if 'style' in A:
            style = self.findSpanStyle(A.pop('style'))
            D = {}
            for k in 'fontName fontSize textColor backColor'.split():
                v = getattr(style,k,self)
                if v is self: continue
                D[k] = v
            D.update(A)
            A = D
        if 'fontName' in A:
            A['fontName'], A['bold'], A['italic'] = ps2tt(A['fontName'])
        self._push('span',**A)

    def end_span(self):
        self._pop('span')

    def start_br(self, attr):
        self._push('br',_selfClosingTag='br',lineBreak=True,text='')
        
    def end_br(self):
        #print('\nend_br called, %d frags in list' % len(self.fragList))
        frag = self._stack[-1]
        if not (frag._selfClosingTag=='br' and frag.lineBreak):
                raise ValueError('Parser failure in <br/>')
        del frag._selfClosingTag
        self.handle_data('')
        self._pop('br')

    def _initial_frag(self,attr,attrMap,bullet=0):
        style = self._style
        if attr!={}:
            style = copy.deepcopy(style)
            _applyAttributes(style,self.getAttributes(attr,attrMap))
            self._style = style

        # initialize semantic values
        frag = ParaFrag()
        frag.sub = 0
        frag.super = 0
        frag.rise = 0
        frag.underline = 0
        frag.strike = 0
        frag.greek = 0
        frag.link = None
        if bullet:
            frag.fontName, frag.bold, frag.italic = ps2tt(style.bulletFontName)
            frag.fontSize = style.bulletFontSize
            frag.textColor = hasattr(style,'bulletColor') and style.bulletColor or style.textColor
        else:
            frag.fontName, frag.bold, frag.italic = ps2tt(style.fontName)
            frag.fontSize = style.fontSize
            frag.textColor = style.textColor
        return frag

    def start_para(self,attr):
        frag = self._initial_frag(attr,_paraAttrMap)
        frag.__tag__ = 'para'
        self._stack = [frag]

    def end_para(self):
        self._pop('para')

    def start_bullet(self,attr):
        if hasattr(self,'bFragList'):
            self._syntax_error('only one <bullet> tag allowed')
        self.bFragList = []
        frag = self._initial_frag(attr,_bulletAttrMap,1)
        frag.isBullet = 1
        frag.__tag__ = 'bullet'
        self._stack.append(frag)

    def end_bullet(self):
        self._pop('bullet')

    #---------------------------------------------------------------
    def start_seqdefault(self, attr):
        try:
            default = attr['id']
        except KeyError:
            default = None
        self._seq.setDefaultCounter(default)

    def end_seqdefault(self):
        pass

    def start_seqreset(self, attr):
        try:
            id = attr['id']
        except KeyError:
            id = None
        try:
            base = int(attr['base'])
        except:
            base=0
        self._seq.reset(id, base)

    def end_seqreset(self):
        pass

    def start_seqchain(self, attr):
        try:
            order = attr['order']
        except KeyError:
            order = ''
        order = order.split()
        seq = self._seq
        for p,c in zip(order[:-1],order[1:]):
            seq.chain(p, c)
    end_seqchain = end_seqreset

    def start_seqformat(self, attr):
        try:
            id = attr['id']
        except KeyError:
            id = None
        try:
            value = attr['value']
        except KeyError:
            value = '1'
        self._seq.setFormat(id,value)
    end_seqformat = end_seqreset

    # AR hacking in aliases to allow the proper casing for RML.
    # the above ones should be deprecated over time. 2001-03-22
    start_seqDefault = start_seqdefault
    end_seqDefault = end_seqdefault
    start_seqReset = start_seqreset
    end_seqReset = end_seqreset
    start_seqChain = start_seqchain
    end_seqChain = end_seqchain
    start_seqFormat = start_seqformat
    end_seqFormat = end_seqformat

    def start_seq(self, attr):
        #if it has a template, use that; otherwise try for id;
        #otherwise take default sequence
        if 'template' in attr:
            templ = attr['template']
            self.handle_data(templ % self._seq)
            return
        elif 'id' in attr:
            id = attr['id']
        else:
            id = None
        increment = attr.get('inc', None)
        if not increment:
            output = self._seq.nextf(id)
        else:
            #accepts "no" for do not increment, or an integer.
            #thus, 0 and 1 increment by the right amounts.
            if increment.lower() == 'no':
                output = self._seq.thisf(id)
            else:
                incr = int(increment)
                output = self._seq.thisf(id)
                self._seq.reset(id, self._seq._this() + incr)
        self.handle_data(output)

    def end_seq(self):
        pass

    def start_ondraw(self,attr):
        defn = ABag()
        if 'name' in attr: defn.name = attr['name']
        else: self._syntax_error('<onDraw> needs at least a name attribute')

        if 'label' in attr: defn.label = attr['label']
        defn.kind='onDraw'
        self._push('ondraw',cbDefn=defn)
        self.handle_data('')
        self._pop('ondraw')
    start_onDraw=start_ondraw 
    end_onDraw=end_ondraw=end_seq

    def start_index(self,attr):
        attr=self.getAttributes(attr,_indexAttrMap)
        defn = ABag()
        if 'item' in attr:
            label = attr['item']
        else:
            self._syntax_error('<index> needs at least an item attribute')
        if 'name' in attr:
            name = attr['name']
        else:
            name = DEFAULT_INDEX_NAME
        format = attr.get('format',None)
        if format is not None and format not in ('123','I','i','ABC','abc'):
            raise ValueError('index tag format is %r not valid 123 I i ABC or abc' % offset)
        offset = attr.get('offset',None)
        if offset is not None:
            try:
                offset = int(offset)
            except:
                raise ValueError('index tag offset is %r not an int' % offset)
        defn.label = encode_label((label,format,offset))
        defn.name = name
        defn.kind='index'
        self._push('index',cbDefn=defn)
        self.handle_data('')
        self._pop('index',)
    end_index=end_seq

    def start_unknown(self,attr):
        pass
    end_unknown=end_seq

    #---------------------------------------------------------------
    def _push(self,tag,**attr):
        frag = copy.copy(self._stack[-1])
        frag.__tag__ = tag
        _applyAttributes(frag,attr)
        self._stack.append(frag)

    def _pop(self,tag):
        frag = self._stack.pop()
        if tag==frag.__tag__: return frag
        raise ValueError('Parse error: saw </%s> instead of expected </%s>' % (tag,frag.__tag__))

    def getAttributes(self,attr,attrMap):
        A = {}
        for k, v in attr.items():
            if not self.caseSensitive:
                k = k.lower()
            if k in list(attrMap.keys()):
                j = attrMap[k]
                func = j[1]
                try:
                    A[j[0]] = v if func is None else func(v)
                except:
                    self._syntax_error('%s: invalid value %s'%(k,v))
            else:
                self._syntax_error('invalid attribute name %s'%k)
        return A

    #----------------------------------------------------------------

    def __init__(self,verbose=0, caseSensitive=0, ignoreUnknownTags=1):
        HTMLParser.__init__(self,
            **(dict(convert_charrefs=False) if sys.version_info>=(3,4) else {}))
        self.verbose = verbose
        #HTMLParser is case insenstive anyway, but the rml interface still needs this
        #all start/end_ methods should have a lower case version for HMTMParser
        self.caseSensitive = caseSensitive
        self.ignoreUnknownTags = ignoreUnknownTags

    def _iReset(self):
        self.fragList = []
        if hasattr(self, 'bFragList'): delattr(self,'bFragList')

    def _reset(self, style):
        '''reset the parser'''

        HTMLParser.reset(self)
        # initialize list of string segments to empty
        self.errors = []
        self._style = style
        self._iReset()

    #----------------------------------------------------------------
    def handle_data(self,data):
        "Creates an intermediate representation of string segments."

        #The old parser would only 'see' a string after all entities had
        #been processed.  Thus, 'Hello &trade; World' would emerge as one
        #fragment.    HTMLParser processes these separately.  We want to ensure
        #that successive calls like this are concatenated, to prevent too many
        #fragments being created.

        frag = copy.copy(self._stack[-1])
        if hasattr(frag,'cbDefn'):
            kind = frag.cbDefn.kind
            if data: self._syntax_error('Only empty <%s> tag allowed' % kind)
        elif hasattr(frag,'_selfClosingTag'):
            if data!='': self._syntax_error('No content allowed in %s tag' % frag._selfClosingTag)
            return
        else:
            # if sub and super are both on they will cancel each other out
            if frag.sub == 1 and frag.super == 1:
                frag.sub = 0
                frag.super = 0

            if frag.sub:
                frag.rise = -frag.fontSize*subFraction
                frag.fontSize = max(frag.fontSize-sizeDelta,3)
            elif frag.super:
                frag.rise = frag.fontSize*superFraction
                frag.fontSize = max(frag.fontSize-sizeDelta,3)

            if frag.greek:
                frag.fontName = 'symbol'
                data = _greekConvert(data)

        # bold, italic, and underline
        frag.fontName = tt2ps(frag.fontName,frag.bold,frag.italic)

        #save our data
        frag.text = data

        if hasattr(frag,'isBullet'):
            delattr(frag,'isBullet')
            self.bFragList.append(frag)
        else:
            self.fragList.append(frag)

    def handle_cdata(self,data):
        self.handle_data(data)

    def _setup_for_parse(self,style):
        self._seq = reportlab.lib.sequencer.getSequencer()
        self._reset(style)  # reinitialise the parser

    def _complete_parse(self):
        "Reset after parsing, to be ready for next paragraph"
        del self._seq
        style = self._style
        del self._style
        if len(self.errors)==0:
            fragList = self.fragList
            bFragList = hasattr(self,'bFragList') and self.bFragList or None
            self._iReset()
        else:
            fragList = bFragList = None

        return style, fragList, bFragList

    def _tt_handle(self,tt):
        "Iterate through a pre-parsed tuple tree (e.g. from pyRXP)"
        #import pprint
        #pprint.pprint(tt)
        #find the corresponding start_tagname and end_tagname methods.
        #These must be defined.
        tag = tt[0]
        try:
            start = getattr(self,'start_'+tag)
            end = getattr(self,'end_'+tag)
        except AttributeError:
            if not self.ignoreUnknownTags:
                raise ValueError('Invalid tag "%s"' % tag)
            start = self.start_unknown
            end = self.end_unknown

        #call the start_tagname method
        start(tt[1] or {})
        #if tree node has any children, they will either be further nodes,
        #or text.  Accordingly, call either this function, or handle_data.
        C = tt[2]
        if C:
            M = self._tt_handlers
            for c in C:
                M[isinstance(c,(list,tuple))](c)

        #call the end_tagname method
        end()

    def _tt_start(self,tt):
        self._tt_handlers = self.handle_data,self._tt_handle
        self._tt_handle(tt)

    def tt_parse(self,tt,style):
        '''parse from tupletree form'''
        self._setup_for_parse(style)
        self._tt_start(tt)
        return self._complete_parse()

    def findSpanStyle(self,style):
        raise ValueError('findSpanStyle not implemented in this parser')

    #HTMLParser interface
    def parse(self, text, style):
        "attempt replacement for parse"
        self._setup_for_parse(style)
        text = asUnicode(text)
        if not(len(text)>=6 and text[0]=='<' and _re_para.match(text)):
            text = u"<para>"+text+u"</para>"
        try:
            self.feed(text)
        except:
            annotateException('\nparagraph text %s caused exception' % ascii(text))
        return self._complete_parse()

    def handle_starttag(self, tag, attrs):
        "Called by HTMLParser when a tag starts"

        #tuple tree parser used to expect a dict.  HTML parser
        #gives list of two-element tuples
        if isinstance(attrs, list):
            d = {}
            for (k,  v) in attrs:
                d[k] = v
            attrs = d
        if not self.caseSensitive: tag = tag.lower()
        try:
            start = getattr(self,'start_'+tag)
        except AttributeError:
            if not self.ignoreUnknownTags:
                raise ValueError('Invalid tag "%s"' % tag)
            start = self.start_unknown
        #call it
        start(attrs or {})
        
    def handle_endtag(self, tag):
        "Called by HTMLParser when a tag ends"
        #find the existing end_tagname method
        if not self.caseSensitive: tag = tag.lower()
        try:
            end = getattr(self,'end_'+tag)
        except AttributeError:
            if not self.ignoreUnknownTags:
                raise ValueError('Invalid tag "%s"' % tag)
            end = self.end_unknown
        #call it
        end()

    def handle_entityref(self, name):
        "Handles a named entity.  "
        try:
            v = known_entities[name]
        except:
            v = u'&%s;' % name
        self.handle_data(v)

if __name__=='__main__':
    from reportlab.platypus import cleanBlockQuotedText
    from reportlab.lib.styles import _baseFontName
    _parser=ParaParser()
    def check_text(text,p=_parser):
        print('##########')
        text = cleanBlockQuotedText(text)
        l,rv,bv = p.parse(text,style)
        if rv is None:
            for l in _parser.errors:
                print(l)
        else:
            print('ParaStyle', l.fontName,l.fontSize,l.textColor)
            for l in rv:
                sys.stdout.write(l.fontName,l.fontSize,l.textColor,l.bold, l.rise, '|%s|'%l.text[:25])
                if hasattr(l,'cbDefn'):
                    print('cbDefn',getattr(l.cbDefn,'name',''),getattr(l.cbDefn,'label',''),l.cbDefn.kind)
                else: print()

    style=ParaFrag()
    style.fontName=_baseFontName
    style.fontSize = 12
    style.textColor = black
    style.bulletFontName = black
    style.bulletFontName=_baseFontName
    style.bulletFontSize=12

    text='''
    <b><i><greek>a</greek>D</i></b>&beta;<unichr value="0x394"/>
    <font name="helvetica" size="15" color=green>
    Tell me, O muse, of that ingenious hero who travelled far and wide
    after</font> he had sacked the famous town of Troy. Many cities did he visit,
    and many were the nations with whose manners and customs he was acquainted;
    moreover he suffered much by sea while trying to save his own life
    and bring his men safely home; but do what he might he could not save
    his men, for they perished through their own sheer folly in eating
    the cattle of the Sun-god Hyperion; so the god prevented them from
    ever reaching home. Tell me, too, about all these things, O daughter
    of Jove, from whatsoever source you<super>1</super> may know them.
    '''
    check_text(text)
    check_text('<para> </para>')
    check_text('<para font="%s" size=24 leading=28.8 spaceAfter=72>ReportLab -- Reporting for the Internet Age</para>'%_baseFontName)
    check_text('''
    <font color=red>&tau;</font>Tell me, O muse, of that ingenious hero who travelled far and wide
    after he had sacked the famous town of Troy. Many cities did he visit,
    and many were the nations with whose manners and customs he was acquainted;
    moreover he suffered much by sea while trying to save his own life
    and bring his men safely home; but do what he might he could not save
    his men, for they perished through their own sheer folly in eating
    the cattle of the Sun-god Hyperion; so the god prevented them from
    ever reaching home. Tell me, too, about all these things, O daughter
    of Jove, from whatsoever source you may know them.''')
    check_text('''
    Telemachus took this speech as of good omen and rose at once, for
    he was bursting with what he had to say. He stood in the middle of
    the assembly and the good herald Pisenor brought him his staff. Then,
    turning to Aegyptius, "Sir," said he, "it is I, as you will shortly
    learn, who have convened you, for it is I who am the most aggrieved.
    I have not got wind of any host approaching about which I would warn
    you, nor is there any matter of public moment on which I would speak.
    My grieveance is purely personal, and turns on two great misfortunes
    which have fallen upon my house. The first of these is the loss of
    my excellent father, who was chief among all you here present, and
    was like a father to every one of you; the second is much more serious,
    and ere long will be the utter ruin of my estate. The sons of all
    the chief men among you are pestering my mother to marry them against
    her will. They are afraid to go to her father Icarius, asking him
    to choose the one he likes best, and to provide marriage gifts for
    his daughter, but day by day they keep hanging about my father's house,
    sacrificing our oxen, sheep, and fat goats for their banquets, and
    never giving so much as a thought to the quantity of wine they drink.
    No estate can stand such recklessness; we have now no Ulysses to ward
    off harm from our doors, and I cannot hold my own against them. I
    shall never all my days be as good a man as he was, still I would
    indeed defend myself if I had power to do so, for I cannot stand such
    treatment any longer; my house is being disgraced and ruined. Have
    respect, therefore, to your own consciences and to public opinion.
    Fear, too, the wrath of heaven, lest the gods should be displeased
    and turn upon you. I pray you by Jove and Themis, who is the beginning
    and the end of councils, [do not] hold back, my friends, and leave
    me singlehanded- unless it be that my brave father Ulysses did some
    wrong to the Achaeans which you would now avenge on me, by aiding
    and abetting these suitors. Moreover, if I am to be eaten out of house
    and home at all, I had rather you did the eating yourselves, for I
    could then take action against you to some purpose, and serve you
    with notices from house to house till I got paid in full, whereas
    now I have no remedy."''')

    check_text('''
But as the sun was rising from the fair sea into the firmament of
heaven to shed light on mortals and immortals, they reached Pylos
the city of Neleus. Now the people of Pylos were gathered on the sea
shore to offer sacrifice of black bulls to Neptune lord of the Earthquake.
There were nine guilds with five hundred men in each, and there were
nine bulls to each guild. As they were eating the inward meats and
burning the thigh bones [on the embers] in the name of Neptune, Telemachus
and his crew arrived, furled their sails, brought their ship to anchor,
and went ashore. ''')
    check_text('''
So the neighbours and kinsmen of Menelaus were feasting and making
merry in his house. There was a bard also to sing to them and play
his lyre, while two tumblers went about performing in the midst of
them when the man struck up with his tune.]''')
    check_text('''
"When we had passed the [Wandering] rocks, with Scylla and terrible
Charybdis, we reached the noble island of the sun-god, where were
the goodly cattle and sheep belonging to the sun Hyperion. While still
at sea in my ship I could bear the cattle lowing as they came home
to the yards, and the sheep bleating. Then I remembered what the blind
Theban prophet Teiresias had told me, and how carefully Aeaean Circe
had warned me to shun the island of the blessed sun-god. So being
much troubled I said to the men, 'My men, I know you are hard pressed,
but listen while I <strike>tell you the prophecy that</strike> Teiresias made me, and
how carefully Aeaean Circe warned me to shun the island of the blessed
sun-god, for it was here, she said, that our worst danger would lie.
Head the ship, therefore, away from the island.''')
    check_text('''A&lt;B&gt;C&amp;D&quot;E&apos;F''')
    check_text('''A&lt; B&gt; C&amp; D&quot; E&apos; F''')
    check_text('''<![CDATA[<>&'"]]>''')
    check_text('''<bullet face=courier size=14 color=green>+</bullet>
There was a bard also to sing to them and play
his lyre, while two tumblers went about performing in the midst of
them when the man struck up with his tune.]''')
    check_text('''<onDraw name="myFunc" label="aaa   bbb">A paragraph''')
    check_text('''<para><onDraw name="myFunc" label="aaa   bbb">B paragraph</para>''')
    # HVB, 30.05.2003: Test for new features
    _parser.caseSensitive=0
    check_text('''Here comes <FONT FACE="Helvetica" SIZE="14pt">Helvetica 14</FONT> with <STRONG>strong</STRONG> <EM>emphasis</EM>.''')
    check_text('''Here comes <font face="Helvetica" size="14pt">Helvetica 14</font> with <Strong>strong</Strong> <em>emphasis</em>.''')
    check_text('''Here comes <font face="Courier" size="3cm">Courier 3cm</font> and normal again.''')
    check_text('''Before the break <br/>the middle line <br/> and the last line.''')
    check_text('''This should be an inline image <img src='../../../docs/images/testimg.gif'/>!''')
    check_text('''aaa&nbsp;bbbb <u>underline&#32;</u> cccc''')
