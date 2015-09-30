import struct
class _BUILDER:
	'''Virtual base helper class for structured file scanning'''
	def _get_struct_fmt(self,info):
		fmt = '<'
		for f, _, _ in info:
			fmt += f
		return fmt

	def _scan_from_file(self,f,info):
		fmt = self._get_struct_fmt(info)
		size = struct.calcsize(fmt)
		T = struct.unpack(fmt,f.read(size))
		i = 0
		for _, n, _ in info:
			setattr(self,n,T[i])
			i = i + 1

	def _dump(self,A):
		for a in A:
			print(a, getattr(self,a))

	def _attr_names(self,*I):
		A = []
		for i in I:
			if isinstance(i,str):
				A.append(i)
			else:
				A.extend([x[1] for x in i])
		return A

	def _scanZTStr(self,f,loc):
		'''scan a zero terminated string from the file'''
		f.seek(loc)
		s = ''
		while 1:
			c = f.read(1)
			if c=='\000': break
			s = s+c
		return s

	def _scanN(self,N,fmt,f,loc):
		if not loc: return None
		fmt = len(fmt)==1 and ("<%d%c" % (N,fmt)) or ("<"+N*fmt)
		f.seek(loc)
		size = struct.calcsize(fmt)
		return struct.unpack(fmt,f.read(size))

	def _scanNT(self,T,N,fmt,f,loc):
		if not loc: return None
		n = len(fmt)
		X = []
		i = 0
		S = []
		for x in self._scanN(N,fmt,f,loc):
			S.append(x)
			i = i + 1
			if i==n:
				X.append(S)
				i = 0
				S = []
		return list(map(lambda x,T=T: T(*x),X))

class KernPair:
	'''hold info about a possible kerning pair'''
	def __init__(self,first,second,amount):
		self.first = first
		self.scond = second
		self.amount = amount

class KernTrack:
	def __init__(self,degree,minSize,minAmount,maxSize,maxAmount):
		'''
		degree	amount to change the character spacing. Negative values mean closer together,p
				ositive values mean farther apart. 
		minSize minimum font height (in device units) for which to use linear track kerning. 
		minAmount track kerning amount to use for font heights less or equal ktMinSize. 
		maxSize maximum font height (in device units) for which to use linear track kerning.f
				For font heights between ktMinSize and ktMaxSize the track kerning amount has 
				to increase linearily from ktMinAmount to ktMaxAmount. 
		maxAmount track kerning amount to use for font heights greater or equal ktMaxSize. 
		'''
		self.degree = degree
		self.minSize = minSize
		self.minAmount = minAmount
		self.maxSize = maxSize
		self.maxAmount = maxAmount

class PFM(_BUILDER):
	def __init__(self,fn=None):
		if fn:
			if isinstance(fn,str):
				f = open(fn,'rb')
			else:
				f = fn
			self.scan_from_file(f)
			if f is not fn: f.close()

	'''Class to hold information scanned from a type-1 .pfm file'''
	def scan_from_file(self,f):
		self._scan_from_file(f,self._header_struct_info)
		if self.dfType!=0x81: raise ValueError("Not a Type-1 Font description")
		else: self.WidthTable = None
		self._scan_from_file(f,self._extension_struct_info)
		if not self.dfExtentTable: raise ValueError('dfExtentTable is zero')
		if not self.dfExtMetricsOffset: raise ValueError('dfExtMetricsOffset is zero')
		if self.dfDevice: self.DeviceName = self._scanZTStr(f,self.dfDevice)
		else: self.DeviceName = None
		if self.dfFace: self.FaceName = self._scanZTStr(f,self.dfFace)
		else: self.FaceName = None
		f.seek(self.dfExtMetricsOffset)
		self._scan_from_file(f, self._extTextMetrics_struct_info)
		N = self.dfLastChar - self.dfFirstChar + 1
		self.ExtentTable = self._scanN(N,'H',f,self.dfExtentTable)
		if self.dfDriverInfo: self.DriverInfo = self._scanZTStr(f,self.dfDriverInfo)
		else: self.DriverInfo = None
		if self.dfPairKernTable: self.KerningPairs = self._scanNT(KernPair,self.dfPairKernTable,'BBh',f,self.etmKernPairs)
		else: self.KerningPairs = []
		if self.dfTrackKernTable: self.KerningTracks = self._scanNT(KernTrack,self.dfTrackKernTable,'hhhhh',f,self.etmKernTracks)
		else: self.KerningTracks = []

	def dump(self):
		self._dump(
			self._attr_names(
			self._header_struct_info,'WidthTable',
			self._extension_struct_info,
			'DeviceName',
			'FaceName',
			self._extTextMetrics_struct_info,
			'DriverInfo',
			))

	_header_struct_info = (('H','dfVersion',
'''This field contains the version of the PFM file.
For PFM files that conform to this description
(namely PFM files for Type-1 fonts) the
value of this field is always 0x0100.'''),

('i','dfSize',
'''This field contains the total size of the PFM file in bytes.
Some drivers check this field and compare its value with the size of the PFM
file, and if these two values don't match the font is ignored
(I know this happens e.g. with Adobe PostScript printer drivers). '''),

('60s','dfCopyright',
'''This field contains a null-terminated copyright
string, often from the application that created the
PFM file (this normally isn't the
copyright string for the font file itself).
The unused bytes in this field should be set to zero. '''),

('H','dfType',
'''This field contains the font type. The low-order
byte is a combination of the following values
(only the values being of interest in PFM
files are given): 

0x00 (PF_RASTER_TYPE): font is a raster font 
0x01 (PF_VECTOR_TYPE): font is a vector font 
0x80 (PF_DEVICE_REALIZED): font realized by the device driver 

The high-order byte is never used in PFM files, it is always zero. 

In PFM files for Type-1 fonts the value in this field is always 0x0081. '''),

('H','dfPoints',
'''This field contains the point size at which this font
looks best. Since this is not relevant for scalable fonts
the field is ignored. The value
of this field should be set to 0x000a (10 pt). '''),

('H','dfVertRes',
'''This field contains the vertical resolution at which the
font was digitized (the value is in dots per inch).
The value of this field should be
set to 0x012C (300 dpi). '''),

('H','dfHorizRes',
'''This field contains the horizontal resolution at which
the font was digitized (the value is in dots per inch).
The value of this field should
be set to 0x012C (300 dpi). '''),

('H','dfAscent',
'''This field contains the distance from the top of a
character definition cell to the baseline of the
typographical font. It is useful for aligning the
baseline of fonts of different heights. '''),

('H','dfInternalLeading',
'''This field contains the amount of leading inside
the bounds set by the dfPixHeight field in the PFMHEADER
structure. Accent marks may occur in this area. '''),

('H','dfExternalLeading',
'''This field contains the amount of extra leading that the
designer requests the application to add between rows. Since this area is
outside the character definition cells, it contains no marks and will not be altered by text outputs. '''),

('B','dfItalic',
'''This field specifies whether this font is an italic
(or oblique) font. The low-order bit is 1 if the flag
is set, all other bits are zero. '''),

('B','dfUnderline',
'''This field specifies whether this font is an underlined
font. The low-order bit is 1 if the flag is set, all other
bits are zero. '''),

('B','dfStrikeOut',
'''This field specifies whether this font is a striked-out font.
The low-order bit is 1 if the flag is set, all other bits are zero. '''),

('H','dfWeight',
'''This field contains the weight of the characters in this font.
The value is on a scale from 0 through 1000, increments are in
steps of 100 each. The values roughly give the number of black
pixel from every 1000 pixels. Typical values are: 

0 (FW_DONTCARE): unknown or no information 
300 (FW_LIGHT): light font 
400 (FW_NORMAL): normal font 
700 (FW_BOLD): bold font '''),

('B','dfCharSet',
'''This field specifies the character set used in this font.
It can be one of the following values (probably other values
may be used here as well): 

0x00 (ANSI_CHARSET): the font uses the ANSI character set;
this means that the font implements all characters needed for the
current Windows code page (e.g. 1252). In case of a Type-1 font
this font has been created with the encoding StandardEncoding
Note that the code page number itself is not stored in the PFM file. 

0x02 (SYMBOL_CHARSET): the font uses a font-specific encoding
which will be used unchanged in displaying an printing text
using this font. In case of a Type-1 font this font has been
created with a font-specific encoding vector. Typical examples are
the Symbol and the ZapfDingbats fonts. 

0xFF (OEM_CHARSET): the font uses the OEM character set; this
means that the font implements all characters needed for the
code page 437 used in e.g. MS-DOS command line mode (at least
in some versions of Windows, others might use code page
850 instead). In case of a Type-1 font this font has been created with a font-specific encoding vector. '''),

('H','dfPixWidth',
'''This field contains the width of all characters in the font.
For raster fonts this field contains the width in pixels of every
character bitmap if the font is fixed-pitch, otherwise this field
is zero and the character's widths are specified in the WidthTable
table. For vector fonts this field contains the width of the grid
on which the font was digitized. The value is ignored by PostScript
printer drivers. '''),

('H','dfPixHeight',
'''This field contains the height of all characters in the font.
For raster fonts this field contains the height in scan lines of
every character bitmap. For vector fonts this field contains the
height of the grid on which the font was digitized. The value is
ignored by PostScript printer drivers. '''),

('B','dfPitchAndFamily',
'''This field specifies the font pitch and the font family. The
font pitch specifies whether all characters in the font have the
same pitch (this is called fixed pitch too) or variable pitch.
The font family indicates, in a rather general way, the look of a font. 

The least significant bit in this field contains the pitch flag.
If the bit is set the font is variable pitch, otherwise it's fixed pitch. For
Type-1 fonts this flag is set always, even if the Type-1 font is fixed pitch. 

The most significant bits of this field specify the font family.
These bits may have one of the following values: 

0x00 (FF_DONTCARE): no information 
0x10 (FF_ROMAN): serif font, variable pitch 
0x20 (FF_SWISS): sans serif font, variable pitch 
0x30 (FF_MODERN): fixed pitch, serif or sans serif font 
0x40 (FF_SCRIPT): cursive or handwriting font 
0x50 (FF_DECORATIVE): novelty fonts '''),

('H','dfAvgWidth',
'''This field contains the average width of the characters in the font.
For a fixed pitch font this is the same as dfPixWidth in the
PFMHEADER structure. For a variable pitch font this is the width
of the character 'X'. '''),

('H','dfMaxWidth',
'''This field contains the maximum width of the characters in the font.
For a fixed pitch font this value is identical to dfAvgWidth in the
PFMHEADER structure. '''),

('B','dfFirstChar',
'''This field specifies the first character code defined by this font.
Width definitions are stored only for the characters actually present
in a font, so this field must be used when calculating indexes into the
WidthTable or the ExtentTable tables. For text fonts this field is
normally set to 0x20 (character space). '''),

('B','dfLastChar',
'''This field specifies the last character code defined by this font.
Together with the dfFirstChar field in the PFMHEADER structure this
field specifies the valid character range for this font. There must
be an entry in the WidthTable or the ExtentTable tables for every
character between these two values (including these values themselves).
For text fonts this field is normally set to 0xFF (maximum
possible value). '''),

('B','dfDefaultChar',
'''This field specifies the default character to be used whenever a
character is used that is outside the range of the dfFirstChar through
dfLastChar fields in the PFMHEADER structure. The character is given
relative to dfFirstChar so that the actual value of the default
character is the sum of dfFirstChar and dfDefaultChar. Ideally, the
default character should be a visible character in the current font,
e.g. a period ('.'). For text fonts this field is normally set to
either 0x00 (character space) or 0x75 (bullet). '''),

('B','dfBreakChar',
'''This field specifies the word-break character. Applications
use this character to separate words when wrapping or justifying lines of
text. The character is given relative to dfFirstChar in the PFMHEADER
structure so that the actual value of the word-break character
is the sum of dfFirstChar and dfBreakChar. For text fonts this
field is normally set to 0x00 (character space). '''),

('H','dfWidthBytes',
'''This field contains the number of bytes in every row of the
font bitmap. The value is always an even quantity so that rows of the
bitmap start on 16 bit boundaries. This field is not used for vector
fonts, it is therefore zero in e.g. PFM files for Type-1 fonts. '''),

('i','dfDevice',
'''This field contains the offset from the beginning of the PFM file
to the DeviceName character buffer. The DeviceName is always
present in PFM files for Type-1 fonts, this field is therefore never zero.'''),

('i','dfFace',
'''This field contains the offset from the beginning of the PFM file
to the FaceName character buffer. The FaceName is always present
in PFM files for Type-1 fonts, this field is therefore never zero. '''),

('i','dfBitsPointer',
'''This field is not used in PFM files, it must be set to zero. '''),

('i','dfBitsOffset',
'''This field is not used in PFM files, it must be set to zero. '''),
)

#'H','WidthTable[]'
#This section is present in a PFM file only when this PFM file describes a
#variable pitch raster font. Since Type-1 fonts aren't raster fonts this
#section never exists in PFM files for Type-1 fonts.'''
#The WidthTable table consists of (dfLastChar - dfFirstChar + 2) entries of type WORD (dfFirstChar and dfLastChar can be found in the
#PFMHEADER structure). Every entry contains the width of the corresponding character, the last entry in this table is extra, it is set to zero.

	_extension_struct_info=(
('H','dfSizeFields',
'''This field contains the size (in bytes) of the
PFMEXTENSION structure. The value is always 0x001e. '''),

('I','dfExtMetricsOffset',
'''This field contains the offset from the beginning
of the PFM file to the ExtTextMetrics section.
The ExtTextMetrics section is always present in PFM
files for Type-1 fonts, this field is therefore never
zero. '''),

('I','dfExtentTable',
'''This field contains the offset from the beginning
of the PFM file to the ExtentTable table. This table
is always present in PFM files for Type-1 fonts, this
field is therefore never zero. '''),

('I','dfOriginTable',
'''This field contains the offset from the beginning
of the PFM file to a table containing origin coordinates
for screen fonts. This table is not present in PFM files
for Type-1 fonts, the field must therefore be set to zero. '''),

('I','dfPairKernTable',
'''This field contains the offset from the beginning of
the PFM file to the KerningPairs table. The value must
be zero if the PFM file doesn't contain a KerningPairs
table. '''),

('I','dfTrackKernTable',
'''This field contains the offset from the beginning of
the PFM file to the KerningTracks table. The value must
be zero if the PFM file doesn't contain a kerningTracks
table. '''), 
('I','dfDriverInfo',
'''This field contains the offset from the beginning of
the PFM file to the DriverInfo section. This section is
always present in PFM files for Type-1 fonts, this field
is therefore never zero. '''),

('I','dfReserved',
'''This field must be set to zero. '''),
)

#char DeviceName[]
#The DeviceName character buffer is a null-terminated string
#containing the name of the printer driver family. PFM files
#for Type-1 fonts have the string 'PostScript', PFM files for
#PCL fonts have the string 'PCL/HP LaserJet'. 
#char FaceName[]
#The FaceName character buffer is a null-terminated string
#containing the name of the font face. In PFM files for Type-1
#fonts this is normally
#the PostScript name of the font without suffixes like
#'-Bold', '-Italic' etc. 
	_extTextMetrics_struct_info = (('h','etmSize', 
'''This field contains the size (in bytes) of the
EXTTEXTMETRIC structure. The value is always 0x0034. '''),

('h','etmPointSize', 
'''This field contains the nominal point size of the font
in twips (this is a twentieth of a point or 1/1440 inch).
This is the intended graphics art size of the font, the
actual size may differ slightly depending on the resolution
of the output device. In PFM files for Type-1 fonts this value
should be set to 0x00f0 (240 twips or 12 pt). '''),

('h','etmOrientation', 
'''This field contains the orientation of the font.
This value refers to the ability of the font to be
imaged on a page of a given orientation. It
can be one of the following values: 

0x0000: any orientation 
0x0001: portrait (page width is smaller that its height) 
0x0002: landscape (page width is greater than its height) 

In PFM files for Type-1 fonts this field is always 0x0000
since a Type-1 font can be arbitrarily rotated. '''),

('h','etmMasterHeight', 
'''This field contains the font size in device units for
which the values in the ExtentTable table are exact. Since
Type-1 fonts are by convention defined in a box of 1000 x 1000
units, PFM files for Type-1 fonts have the value 0x03E8 (1000,
the number of units per em) in this field. '''),

('h','etmMinScale', 
'''This field contains the minimum valid size for the font in
device units. The minimum valid point size can then be calculated
as follows:
(etmMinScale * points-per-inch) / dfVertRes
The value for 'points-per-inch' is normally 72, the dfVertRes
field can be found in the PFMHEADER structure, it contains the
vertical resolution at which the font was digitized (this
value is in dots per inch). 

In PFM files for Type-1 fonts the value should be set to 0x0003. '''),

('h','etmMaxScale', 
'''This field contains the maximum valid size for the font in
device units. The maximum valid point size can then be calculated
as follows:
(etmMaxScale * points-per-inch) / dfVertRes
(see also above etmMinScale). 

In PFM files for Type-1 fonts the value should be set to 0x03E8 (1000). '''),

('h','etmMasterUnits', 
'''This field contains the integer number of units per em
where an em equals etmMasterHeight in the EXTTEXTMETRIC structure.
In other words, the etmMasterHeight value is expressed in font
units rather than device units. 

In PFM files for Type-1 fonts the value should be set to
0x03E8 (1000). '''),

('h','etmCapHeight', 
'''This field contains the height for uppercase characters
in the font (the value is in font units). Typically, the
character 'H' is used for measurement purposes. 

For Type-1 fonts you may find this value in the AFM file. '''),

('h','etmXHeight', 
'''This field contains the height for lowercase characters
in the font (the value is in font units). Typically, the
character 'x' is used for measurement purposes. 

For Type-1 fonts you may find this value in the AFM file. '''),

('h','etmLowerCaseAscent', 
'''This field contains the distance (in font units) that
the ascender of lowercase letters extends above the baseline.
This distance is typically specified for a lowercase character 'd'. 

For Type-1 fonts you may find this value in the AFM file. '''),

('h','etmLowerCaseDescent', 
'''This field contains the distance (in font units) that
the descender of lowercase letters extends below the baseline.
This distance is typically specified for a lowercase character 'p'. 

For Type-1 fonts you may find this value in the AFM file. '''),

('h','etmSlant', 
'''This field contains the angle in tenth of degrees clockwise
from the upright version of the font. The value is typically not zero only for
an italic or oblique font. 

For Type-1 fonts you may find this value in the AFM file
(search for the entry 'ItalicAngle' and multiply it by 10). '''),

('h','etmSuperScript', 
'''This field contains the recommended amount (in font units)
to offset superscript characters from the baseline. This amount
is typically specified by a negative offset. '''),

('h','etmSubScript', 
'''This field contains the recommended amount (in font units)
to offset subscript characters from the baseline. This amount
is typically specified by a positive offset. '''),

('h','etmSuperScriptSize', 
'''This field contains the recommended size (in font units)
for superscript characters in the font. '''),

('h','etmSubScriptSize', 
'''This field contains the recommended size (in font units)
for subscript characters in the font. '''),

('h','etmUnderlineOffset', 
'''This field contains the offset (in font units) downward
from the baseline where the top of a single underline bar
should appear.

For Type-1 fonts you may find this value in the AFM file. '''),

('h','etmUnderlineWidth', 
'''This field contains the thickness (in font units) of the underline bar.
For Type-1 fonts you may find this value in the AFM file. '''),

('h','etmDoubleUpperUnderlineOffset', 
'''This field contains the offset (in font units) downward from
the baseline where the top of the upper, double underline bar should
appear. '''),

('h','etmDoubleLowerUnderlineOffset', 
'''This field contains the offset (in font units) downward
from the baseline where the top of the lower, double underline
bar should appear. '''),

('h','etmDoubleUpperUnderlineWidth', 
'''This field contains the thickness (in font units) of the
upper, double underline bar. '''),

('h','etmDoubleLowerUnderlineWidth', 
'''This field contains the thickness (in font units) of the
lower, double underline bar. '''),

('h','etmStrikeOutOffset', 
'''This field contains the offset (in font units) upward from
the baseline where the top of a strikeout bar should appear. '''),

('h','etmStrikeOutWidth', 
'''This field contains the thickness (in font units) of the
strikeout bar. '''),

('H','etmKernPairs', 
'''This field contains the number of kerning pairs defined
in the KerningPairs table in this PFM file. The number (and
therefore the table) may not be greater than 512. If the PFM
file doesn't contain a KerningPairs table the value is zero. '''),

('H','etmKernTracks', 
'''This field contains the number of kerning tracks defined in
the KerningTracks table in this PFM file. The number (and therefore the
table) may not be greater than 16. If the PFM file doesn't contain
a KerningTracks table the value is zero. '''),
)

#'H','ExtentTable[]'
#The ExtentTable table must be present in a PFM file for a Type-1 font,
#it contains the unscaled widths (in 1/1000's of an em) of the characters
#in the font. The table consists of (dfLastChar - dfFirstChar + 1) entries
#of type WORD (dfFirstChar and dfLastChar can be found in the PFMHEADER
#structure).  For Type-1 fonts these widths can be found in the AFM file. 

#DRIVERINFO DriverInfo
#The DriverInfo section must be present in a PFM file for a Type-1 font,
#in this case it consists of a null-terminated string containing the
#PostScript name of the font. 

#PAIRKERN KerningPairs[]
#The KerningPairs table need not be present in a PFM file for a Type-1
#font, if it exists it contains etmKernPairs (from the EXTTEXTMETRIC
#structure) entries. Each of these entries looks as follows: 
#B kpFirst This field contains the first (left) character of the kerning pair. 
#B kpSecond This field contains the second (right) character of the kerning pair. 
#h kpKernAmount This field contains the kerning amount in font units, the value
#  is mostly negative. 

#KERNTRACK KerningTracks[]
#The KerningTracks table need not be present in a PFM file for a Type-1 font, if it exists it contains etmKernTracks (from the EXTTEXTMETRIC structure) entries. Each of these entries looks as follows: 
#h ktDegree This field contains the amount to change the character spacing. Negative values mean closer together, positive values mean farther apart. 
#h ktMinSize This field contains the minimum font height (in device units) for which to use linear track kerning. 
#h ktMinAmount This field contains the track kerning amount to use for font heights less or equal ktMinSize. 
#h ktMaxSize This field contains the maximum font height (in device units) for which to use linear track kerning. For font heights between ktMinSize and ktMaxSize the track kerning amount has to increase linearily from ktMinAmount to ktMaxAmount. 
#h ktMaxAmount This field contains the track kerning amount to use for font heights greater or equal ktMaxSize. 

if __name__=='__main__':
	from glob import glob
	for f in glob('/Program Files/Adobe/Acrobat 4.0/resource/font/pfm/*.pfm'):
		print(f)
		p=PFM(f)
		p.dump()
