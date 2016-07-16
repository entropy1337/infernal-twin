CHANGES
=======

This is a summary of changes made to the reportlab source code for each release.
Please refer to subversion backlogs (using the release dates) for more details
or for releases which we have not provide a higher level changes list for.
E.g. to retrieve the changes made between release 3.1 and release 3.2, type::

  $ hg log -r adb3f0d

The contributors lists are in no order and apologies to those accidentally not
mentioned. If we missed you, please let us know!


RELEASE 3.2  01/06/2015
-----------------------

   * Added proportional underlining specific to font sizes, set via the `underlineProportion` attribute of ParagraphStyles. 
   * TrueType fonts: added support for cmaps 10 & 13
   * DocTemplate class now supports a boolean `displayDocTitle` argument.
   * TableofContents now supports a formatter argument to allow formatting of the displayed page numbers (eg for appendices etc).
   * Table `repeatRows` can now be a tuple of row numbers to allow incomplete ranges of rows to be repeated. 
   * Tables now do pass instance.`spaceBefore` & `spaceAfter` to their split children when split 
   * Several strangenesses were fixed in the pdfbase.pdfform module; Multiple usage is now allowed.
   * Error message fixes
   * Various environment fixes for Google Application Environment
   * Resource fixes
   * PDFDoc can now set the `Lang` attribute
   * canvas.drawString and similar now allow the character spacing to be set 
   * Index of accented stuff has been improved
   * RTL code was improved
   * fix Propertyset.clone
   * `flowables.py`: fix ImageAndFlowables so it avoids testing negative availableWidth 

### Contributors:
   * Steven Jacobs
   * Philip Semanchuk
   * Marius Gedminas
   * masklinn
   * Kale Franz
   * Albertas Agejavas
   • Anders Hammarquist
   * jvanzuela @ bitbucket
   * Glen Lindermann
   * Greg Jones
   * James Bynd
   * fcoelho @ bitbucket


RELEASE 3.1  22/04/2014
-----------------------

If you are running ReportLab 3.0.x, the changes are minor.
   * support for emoji - characters outside the Unicode basic multilingual plane
   * improved pip-based installers will pull in all the needed dependencies; Pillow 2.4 appears to deal with all our issues.

### Contributors
   * Ivan Tchomgue
   * Waldemar Osuch
   * masayuku
   * alexandrel_sgi


RELEASE 3.0  14/02/2014
-----------------------

ReportLab 3.0 now supports Python 2.7, 3.3 and higher.  

There has been a substantial internal rewrite to ensure consistent use of unicode strings for
  natural-language text, and of bytes for all file format internals.  The intent
  is to make as few API changes as possible so that there should be little or no
  impact on users and their applications.  Changes are too numerous but can be
  seen on Bitbucket.

### Python 3.x compatibility
  * Python 3.x compatibility.  A single line of code should run on 2.7 and 3.3
  * __init__.py restricts to 2.7 or >=3.3
  * __init__.py allow the import of on optional reportlab.local_rl_mods to allow monkey patching etc.
  * rl_config now imports rl_settings & optionally local_rl_settings
  * ReportLab C extensions now live inside reportlab; _rl_accel is no longer required; All _rl_accel imports now 
	pass through reportlab.lib.rl_accel
  * xmllib is gone, alongside the paraparser stuff that caused issues in favour of HTMLParser.
  * some obsolete C extensions (sgmlop and pyHnj) are gone
  * Improved support for multi-threaded systems to the _rl_accel extension module.
  * Removed reportlab/lib/ para.py & pycanvas.py;  these would better belong in third party packages, 
	which can make use of the monkeypatching feature above.


### New features
  * Add ability to output greyscale and 1-bit PIL images without conversion to RGB. (contributed by Matthew Duggan)
  * highlight annotation (contributed by Ben Echols)

### Other
  * numerous very minor fixes, visible through BitBucket.


RELEASE 2.7  04/04/2013
-----------------------

#### Charts / graphics enhancements
  * Added SimpleTimeSeriesPlot
  * added _computeMaxSpace
  * added in lineStyle (for bars)
  * improved SVG rendering
  * Pie Chart now has an `innerRadiusFraction` to allow doughnut-like appearance for 2d charts  (it has no effect with 3d charts). 
	 The separate 'doughnut' chart lacks many pie chart features and should only be used if you wanted multiple nested doughnuts. 

#### Charts/graphics bug fixes
  * piecharts.py: fix Pie3d __init__ to call its superclass
  * linecharts.py: fix swatch creation
  * fixed `y` axis in the simple time series plot

#### PDF
  * Fixes to testshapes & pdfform resetting
  * colors.py
  * various minor fixes

#### Platypus
  * Defined a small bullet rather than a big circle as the default for unordered lists
  * fixed attribute spelling bug
  * fixed CJK + endDots

### Acknowledgements
  Many thanks to Andrew Cutler, Dinu Gherman, Matthias Kirst and Stephan Richter for their contributions to this release.


RELEASE 2.6  27/09/2012
-----------------------

This is a minor release focusing mainly on improved documentation.  There are a 
number of minor enhancements, and a larger number of previous-undocumented
enhancements which we have documented better.

#### General changes
   * Manuals have been reformatted with more pleasing code snippets and tables of 
     contents, and reviewed and expanded

#### Flowing documents (Platypus)
   * Added support for HTML-style list objects
   * Added flexible mechanism for drawing bullets
   * Allowed XPreformatted objects to use Asian line wrapping
   * Added an `autoNextPageTemplate` attribute to PageTemplates.  For example you 
     can now set up a 'chapter first page template' which will always be followed
     by a 'continuation template' on the next page break, saving the programmer from
     having to issue control flow commands in the story.
   * added a TopPadder flowable, which will 'wrap' another Flowable and move it 
     to the bottom of the current page.  
   * More helpful error messages when large tables cannot be rendered
   * Documentation for images within text (`test_032_images`)
   * Trailing dots for use on contents pages

#### Charts and graphics
   * Support for UPCA bar codes
   * We now have a semi-intelligent system for labelling pie charts with 
     callout lines.  Thanks to James Martin-Collar, a maths student at Warwick 
     University, who did this as his summer internship.
   * Axes - added startOffset and endOffset properties; allowed for axis 
     background annotations.
   * Bar charts - allow more control of z Index (i.e. drawing order of axes and
     lines)
   * Pie charts - fixed bugs in 3d appearance
   * SVG output back end has seen some bugs fixed and now outputs resizeable SVG
   
### Contributors
   * Alex Buck
   * Felix Labrecque <felixl@densi.com>
   * Peter Johnson <johnson.peter@gmail.com>
   * James Martin-Collar
   * Guillaume Francois
   

RELEASE 2.5  at 18:00 GMT  01/Oct/2010
--------------------------------------

Many new features have been added and numerous bugs have been fixed.

Thanks to everybody who has contributed to the open-source toolkit in
the run-up to the 2.5 release, whether by reporting bugs, sending patches,
or contributing to the reportlab-users mailing list.
Major contributors are credited in the user documentation.

   * Support for colour separated PDF output and other optimisations and
     features for high-quality printing, including enforcement of colour
     models for CMYK, RGB, and "spot colours"
   * Long table optimisations are now turned on by default.  Previously,
     documents with very long tables spanning many pages could take a long
     time to create because we considered the whole table to work out row
     and column sizes.  A patch was submitted some time ago to fix this
     controlled by a flag in the rl_config file, but this was set 'off'
     for compatibility.  Users are often not aware of this and we haven't
     found any real-world cases where the new layout technique works badly,
     so we are turning this behaviour on.
   * New support for QR barcodes - [try our demo!](https://www.reportlab.com/demos/qr/)

#### PDF
   * Colour separation and other enhancements for high-end print
   * Python 2.7 support

#### Charts
   * reportlab.graphics.charts.axes
       * ValueAxis
           * avoidBoundSpace - Space to allow above and below
           * abf_ignore_zero - Set to True to make the avoidBoundFrac calculations treat zero as non-special
           * keepTickLabelsInside - Ensure tick labels do not project beyond bounds of axis if true
       * NormalDateXValueAxis
           * specialTickClear - clear rather than delete close ticks when forced first/end dates
       * AdjYValueAxis
           * labelVOffset - add this to the labels
   * reportlab.graphics.charts.barcharts
       * BarChart
           * categoryLabelBarSize - width to leave for a category label to go between categories
           * categoryLabelBarOrder - where any label bar should appear first/last
           * barRecord (advanced) - callable(bar,label=labelText,value=value,**kwds) to record bar information
   * reportlab.graphics.charts.legends
       * SubColProperty
           * dx - x offset from default position
           * dy - y offset from default position
       * Legend
           * swdx - x position adjustment for the swatch
           * swdy - y position adjustment for the swatch
   * reportlab.graphics.charts.piecharts
       * Pie
           * wedgeRecord (advanced) - callable(wedge,*args,**kwds)

   * reportlab.graphics.charts.utils
       * DrawTimeCollector - generic mechanism for collecting information about nodes at the time they are about to be drawn


RELEASE 2.4  at 18:00 GMT  20/Jan/2010
--------------------------------------

#### PDF
   * lots of improvements and verbosity to error messages and the way they are handled.
   * font size can now be specified in pixels
   * unicode file names are now accepted

#### Platypus
   * canvas auto cropmarks
   * added support for styles h4-h6
   * Improved support for onDraw and SimpleIndex
   * Add support for index tableStyle
   * Added an alphabetic grouping indexing class
   * Added support for multi-level and alphabetical indexes
   * Added support for an unlimited number of TOC levels with default styles
   * Index entries can now be clickable.

#### Graphics
   * Axes values can be reversible.
   * Labels on the axes can now be drawn above or below the axes (hi or low).
   * A per swatch callout is now allowed in the legend.
   * A new anchroing mode for string 'numeric' that align numerical strings by their decimal place.
   * Shapes have new attributes to specify if the shape should grow to take all canvas area (vertically or horizontally) or if the canvas should shrink to fit the shape size.
   * color objects now have a clone method.
   * colors module has a fade function that returns a list of different shades made up of one base colour.
   * added in support for Overprint/Opacity & Separated colours

#### Bugs fixes
   * word counting in complex paragraphs has been fixed.
   * SimpleIndex and TableOfContents bugs have been fixed.
   * Fix for position of hyperlinks when crop marks are added.
   * flowables.py: fix special case of doctemplate with no frames
   * PDFFormXObject.format missing Resources bug patch from Scott Meyer
   * KeepInFrame justification bug has been fixed.
   * paragraph.py: fix linebreaking bug thanks to Roberto Alsina
   * fix unicode/str issue bug found by Michael Egorov <michwill@gmail.com>
   * YCategoryAxis makeTickLabels fix contributed by Mike Folwell <mjf@pearson.co.uk>
   * pdfdoc.py: fix ro PDFDate contributed by Robert Alsina
   * and others ..

### Contributors
   * PJACock's (<peter@maubp.freeserve.co.uk>)
   * Hans Brand
   * Ian Stevens
   * Yoann Roman <yroman-reportlab@altalang.com>
   * Randolph Bentson
   * Volker Haas
   * Simon King
   * Henning Vonbargen
   * Michael Egorov <michwill@gmail.com>
   * Mike Folwell <mjf@pearson.co.uk>
   * Robert Alsina
   * and more ...


RELEASE 2.3  at 18:00 GMT  04/Feb/2009
--------------------------------------

#### PDF
   * Encryption support (see encrypt parameter on Canvas and BaseDocTemplate constructor)

#### Platypus
   * TableOfContents - Creates clickable tables of contents
   * Variable border padding for paragraphs (using the borderPadding style attribute)
   * New programming Flowable, docAssert, used to assert expressions on wrap time.

#### Bug fixes
   * Fixed old documentation and installation issues
   * 610 - Fixed Image anchoring code to match documentation
   * 704 - renderSVG groups problem
   * 706 - rl_codecs.py now compatible with WordAxe
   * and others...

### Contributors 
   * Yoann Roman
   * Dinu Gherman
   * Dirk Holtwick
   * Marcel Tromp
   * Henning von Bargen
   * Paul Barrass
   * Adrian Klaver
   * Hans Brand
   * Ian Stevens


RELEASE 2.2  at 18:00 GMT  10/Sep/2008
--------------------------------------

#### PDF
   * pdfmetrics: Added registerFontFamily function
   * Basic support for pdf document viewer preferences (e.g.: fullscreen).

#### Platypus
   * Paragraph <img> tag support for inline images.
   * Paragraph autoleading support (helps with <img> tags).
   * Platypus doctemplate programming support.
   * Support for tables with non-uniform row length.

#### Graphics
   * RGBA image support for suitable bitmap types.
   * LTO labelling barcode.

And many bugfixes...

### Contributors 
   * Matt Folwell
   * Jerome Alet
   * Harald Armin Massa
   * kevin@booksys.com
   * Sebastian Ware
   * Martin Tate
   * Wietse Jacobs
   * Christian Jacobs
   * Volker Haas
   * Dinu Gherman
   * Dirk Datzert
   * Yuan Hong
   * Ilpo Nyyss�nen
   * Thomas Heller
   * Gael Chardon
   * Alex Smishlajev
   * Martin Loewis
   * Dirk Holtwick
   * Philippe Makowskic
   * Ian Sparks
   * Albertas Agejevas
   * Gary Poster
   * Martin Zohlhuber
   * Francesco Pierfederici
   * michael@stroeder.com
   * Derik Barclay
   * Publio da Costa Melo 
   * Jon Dyte
   * David Horkoff
   * picodello@yahoo.it
   * R�diger M�hl
   * Paul Winkler
   * Bernhard Herzog
   * Alex Martelli
   * Stuart Bishop
   * Gael Chardon


RELEASE 2.1  at 15:00 GMT  24/May/2007
--------------------------------------

### Contributors 
   * Ilpo Nyyss�nen
   * Thomas Heller
   * Gael Chardon
   * Alex Smishlajev
   * Martin Loewis       
   * Dirk Holtwick
   * Philippe Makowskic
   * Dinu Gherman
   * Ian Sparks
 

RELEASE 2.0  at 15:00 GMT  23/May/2006
--------------------------------------

### Contributions
   * Andre Reitz
   * Max M
   * Albertas Agejevas
   * T Blatter
   * Ron Peleg
   * Gary Poster
   * Steve Halasz
   * Andrew Mercer
   * Paul McNett
   * Chad Miller

### Unicode support

This is the Big One, and the reason some apps may break. You must now pass in 
text either in UTF-8 or as unicode string objects. The library will handle 
everything to do with output encoding. There is more information on this below.

Since this is the biggest change, we'll start by reviewing how it worked in the 
past. In ReportLab 1.x, any string input you passed to our APIs was supposed to 
be in the same encoding as the font you selected for output. If using the 
default fonts in Acrobat Reader (Helvetica/Times/Courier), you would have 
implicitly used WinAnsi encoding, which is almost exactly the same as Latin-1. 
However, if using TrueType fonts, you would have been using UTF-8. For Asian 
fonts, you had a wide choice of encodings but had to specify which one (e.g 
Shift-JIS or EUC for Japanese). This state of affairs meant that you had to 
make sure that every piece of text input was in the same encoding as the font 
used to display it.

With ReportLab 2, none of that necessary. Instead:

Here is what's different now:

#### Input text encoding is UTF-8 or Python Unicode strings

  Any text you pass to a canvas API (drawString etc.), Paragraph or other 
  flowable constructor, into a table cell, or as an attribute of a graphic (e.g. 
  chart.title.text), is supposed to be unicode. If you use a traditional Python 
  string, it is assumed to be UTF-8. If you pass a Unicode object, we know it's 
  unicode. 

#### Font encodings

  Fonts still work in different ways, and the built-in ones will still use 
  WinAnsi or MacRoman internally while TrueType will use UTF-8. However, the 
  library hides this from you; it converts as it writes out the PDF file. As 
  before, it's still your job to make sure the font you use has the characters 
  you need, or you may get either a traceback or a visible error character. 
  Asian CID fonts

  You no longer need to specify the encoding for the built-in Asian fonts, 
  just the face name. ReportLab knows about the standard fonts in Adobe's Asian 
  Language Packs. 

#### Asian Truetype fonts

  The standard Truetype fonts differ slightly for Asian languages (e.g 
  msmincho.ttc). These can now be read and used, albeit somewhat inefficiently. 
  Asian word wrapping

  Previously we could display strings in Asian languages, but could not 
  properly wrap paragraphs as there are no gaps between the words. We now have a 
  basic word wrapping algorithm.

#### unichar tag

  A convenience tag, <unichar/> has also been added. You can now do <unichar 
  code="0xfc"/> or <unichar name='LATIN SMALL LETTER U WITH DIAERESIS'/> and get 
  a lowercase u umlaut. Names should be those in the Unicode Character Database.
  Accents, Greeks and symbols

  The correct way to refer to all non-ASCII characters is to use their 
  unicode representation. This can be literal Unicode or UTF-8. Special symbols 
  and Greek letters (collectively, "greeks") inserted in paragraphs using the 
  greek tag (e.g. <greek>lambda</greek>) or using the entity references (e.g. 
  &lambda;) are now processed in a different way than in version 1. Previously, 
  these were always rendered using the Zapf Dingbats font. Now they are always 
  output in the font you specified, unless that font does not support that 
  character. If the font does not support the character, and the font you 
  specified was an Adobe Type 1 font, Zapf Dingbats is used as a fallback. 
  However, at present there is no fallback in the case of TTF fonts. Note that 
  this means that documents that contain greeks and specify a TTF font may need 
  changing to explicitly specify the font to use for the greek character, or you 
  will see a black square in place of that character when you view your PDF 
  output in Acrobat Reader.

### Other New Features

#### PDF

  * Improved low-level annotation support for PDF "free text annotations"
    FreeTextAnnotation allows showing and hiding of an arbitrary PDF "form" 
    (reusable chunk of PDF content) depending on whether the document is printed or 
    viewed on-screen, or depending on whether the mouse is hovered over the 
    content, etc.
  * TTC font collection files are now readable:
    ReportLab now supports using TTF fonts packaged in .TTC files
  * East Asian font support (CID and TTF):
    You no longer need to specify the encoding for the built-in Asian 
    fonts, just the face name. ReportLab knows about the standard fonts in Adobe's 
    Asian Language Packs. 
  * Native support for JPEG CMYK images:
    ReportLab now takes advantage of PDF's native JPEG CMYK image support, 
    so that JPEG CMYK images are no longer (lossily) converted to RGB format before 
    including them in PDF. 

#### Platypus

  * Link support in paragraphs:
    Platypus paragraphs can now contain link elements, which support both 
    internal links to the same PDF document, links to other local PDF documents, 
    and URL links to pages on the web. Some examples:

    Web links::

        <link href="http://www.reportlab.com/">ReportLab<link>

    Internal link to current PDF document::

        <link href="summary">ReportLab<link>

    External link to a PDF document on the local filesystem::

        <link href="pdf:c:/john/report.pdf">ReportLab<link>

  * Improved wrapping support:
    Support for wrapping arbitrary sequence of flowables around an image, 
    using reportlab.platypus.flowables.ImageAndFlowables (similar to 
    ParagraphAndImage).
  * `KeepInFrame`:
    Sometimes the length of a piece of text you'd like to include in a 
    fixed piece of page "real estate" is not guaranteed to be constrained to a 
    fixed maximum length. In these cases, KeepInFrame allows you to specify an 
    appropriate action to take when the text is too long for the space allocated 
    for it. In particular, it can shrink the text to fit, mask (truncate) 
    overflowing text, allow the text to overflow into the rest of the document, or 
    raise an error.
  * Improved convenience features for inserting unicode symbols and other 
  characters:
    `<unichar/>` lets you conveniently insert unicode characters using the 
    standard long name or code point. Characters inserted with the `<greek>` tags 
    (e.g. `<greek>lambda</greek>`) or corresponding entity references (e.g. &lambda;) 
    support arbitrary fonts (rather than only Zapf Dingbats).
  * Table spans and splitting improved:
    Cell spanning in tables used to go wrong sometimes when the table split 
    over a page. We believe this is improved, although there are so many table 
    features that it's hard to define correct behaviour in all cases.
  * `KeepWithNext` improved:
    Paragraph styles have long had an attribute keepWithNext, but this was 
    buggy when set to True. We believe this is fixed now. keepWithNext is important 
    for widows and orphans control; you typically set it to True on headings, to 
    ensure at least one paragraph appears after the heading and that you don't get 
    headings alone at the bottom of a column. 

#### Graphics
  * Barcodes:
    The barcode package has been added to the standard reportlab 
    toolkit distribution (it used to live separately in our contributions area). It 
    has also seen fairly extensive reworking for production use in a recent 
    project. These changes include adding support for the standard European EAN 
    barcodes (EAN 8 and EAN13).
  * Improvements to Legending:
    Instead of manual placement, there is now a attachment point (N, 
    S, E, W, etc.), so that the legend is always automatically positioned correctly 
    relative to the chart. Swatches (the small sample squares of colour / pattern 
    fill sometimes displayed in the legend) can now be automatically created from 
    the graph data. Legends can now have automatically-computed totals (useful for 
    financial applications).
  * More and better ways to place piechart labels:
    New smart algorithms for automatic pie chart label positioning 
    have been added. You can now produce nice-looking labels without manual 
    positioning even for awkward cases in big runs of charts.
  * Adjustable piechart slice ordering:
    For example. pie charts with lots of small slices can be 
    configured to alternate thin and thick slices to help the label placement 
    algorithm work better.
  * Improved spiderplots

#### Noteworthy bug fixes
  * Fixes to TTF splitting (patch from Albertas Agejevas):
    This affected some documents using font subsetting
  * Tables with spans improved splitting:
    Splitting of tables across pages did not work correctly when the table had
    row/column spans
  * Fix runtime error affecting keepWithNext


Older releases
--------------

Please refer to subversion backlogs for a low level change list

	RELEASE 1.20 at 18:00 GMT  25/Nov/2004
	RELEASE 1.19 at 18:00 GMT  21/Jan/2004
	RELEASE 1.18 at 12:00 GMT  9/Jul/2003
	RELEASE 1.17 at 16:00 GMT  3/Jan/2003
	RELEASE 1.16 at 16:00 GMT  7/Nov/2002
	RELEASE 1.15 at 14:00 GMT  9/Aug/2002
	RELEASE 1.14 at 18:00 GMT 28/May/2002
	RELEASE 1.13 at 15:00 GMT 27/March/2002
	RELEASE 1.12 at 17:00 GMT 28/February/2002
	RELEASE 1.11 at 14:00 GMT 12/December/2001
	RELEASE 1.10 at 14:00 GMT 06/November/2001
	RELEASE 1.09 at 14:00 BST 13/August/2001
	RELEASE 1.08 at 12:00 BST 19/June/2001
	RELEASE 1.07 at 11:54 BST 2001/05/02
	RELEASE 1.06 at 14:00 BST 2001/03/30
	RELEASE 1.03 on 2001/02/09
	RELEASE 1.02 on 2000/12/11
	RELEASE 1.01 on 2000/10/10
	RELEASE 1.00 on 2000/07/20
	RELEASE 0.95 on 2000/07/14
	RELEASE 0.94 on 2000/06/20
