#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__version__ = '$Id$'
from tools.docco.rl_doc_utils import *
from reportlab.platypus.tableofcontents import TableOfContents
from datetime import datetime
import reportlab

title("ReportLab PDF Library")
title("User Guide")
centred('ReportLab Version ' + reportlab.Version)
centred(datetime.now().strftime('Document generated on %Y/%m/%d %H:%M:%S %Z'))

nextTemplate("TOC")

headingTOC()

toc = TableOfContents()
PS = ParagraphStyle
toc.levelStyles = [
    PS(fontName='Times-Bold', fontSize=14, name='TOCHeading1', leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=16),
    PS(fontSize=12, name='TOCHeading2', leftIndent=40, firstLineIndent=-20, spaceBefore=0, leading=12),
    PS(fontSize=10, name='TOCHeading3', leftIndent=60, firstLineIndent=-20, spaceBefore=0, leading=12),
    PS(fontSize=10, name='TOCHeading4', leftIndent=100, firstLineIndent=-20, spaceBefore=0, leading=12),
]
getStory().append(toc)

nextTemplate("Normal")

########################################################################
#
#               Chapter 1
#
########################################################################


heading1("Introduction")


heading2("About this document")
disc("""This document is an introduction to the ReportLab PDF library.
Some previous programming experience
is presumed and familiarity with the Python Programming language is
recommended.  If you are new to Python, we tell you in the next section
where to go for orientation.
""")

disc("""
This manual does not cover 100% of the features, but should explain all
the main concepts and help you get started, and point you at other
learning resources. 
After working your way through this, you should be ready to begin
writing programs to produce sophisticated reports.
""")

disc("""In this chapter, we will cover the groundwork:""")
bullet("What is ReportLab all about, and why should I use it?")
bullet("What is Python?")
bullet("How do I get everything set up and running?")

todo("""
We need your help to make sure this manual is complete and helpful.
Please send any feedback to our user mailing list,
which is signposted from <a href="http://www.reportlab.com/">www.reportlab.com</a>.
""")

heading2("What is the ReportLab PDF Library?")
disc("""This is a software library that lets you directly
create documents in Adobe's Portable Document Format (PDF) using
the Python programming language.   It also creates charts and data graphics
in various bitmap and vector formats as well as PDF.""")

disc("""PDF is the global standard for electronic documents. It
supports high-quality printing yet is totally portable across
platforms, thanks to the freely available Acrobat Reader.  Any
application which previously generated hard copy reports or driving a printer
can benefit from making PDF documents instead; these can be archived,
emailed, placed on the web, or printed out the old-fashioned way.
However, the PDF file format is a complex
indexed binary format which is impossible to type directly.
The PDF format specification is more than 600 pages long and
PDF files must provide precise byte offsets -- a single extra
character placed anywhere in a valid PDF document can render it
invalid.  This makes it harder to generate than HTML.""")

disc("""Most of the world's PDF documents have been produced
by Adobe's Acrobat tools, or rivals such as JAWS PDF Creator, which act
as 'print drivers'.  Anyone wanting to automate PDF production would
typically use a product like Quark, Word or Framemaker running in a loop
with macros or plugins, connected to Acrobat. Pipelines of several
languages and products can be slow and somewhat unwieldy.
""")


disc("""The ReportLab library directly creates PDF based on
your graphics commands.  There are no intervening steps.  Your applications
can generate reports extremely fast - sometimes orders
of magnitude faster than traditional report-writing
tools.   This approach is shared by several other libraries - PDFlib for C,
iText for Java, iTextSharp for .NET and others.  However, The ReportLab library
differs in that it can work at much higher levels, with a full featured engine
for laying out documents complete with tables and charts.  """)


disc("""In addition, because you are writing a program
in a powerful general purpose language, there are no
restrictions at all on where you get your data from,
how you transform it, and the kind of output
you can create.  And you can reuse code across
whole families of reports.""")

disc("""The ReportLab library is expected to be useful
in at least the following contexts:""")
bullet("Dynamic PDF generation on the web")
bullet("High-volume corporate reporting and database publishing")
bullet("""An embeddable print engine for other applications, including
a 'report language' so that users can customize their own reports. <i>
This is particularly relevant to cross-platform apps which cannot
rely on a consistent printing or previewing API on each operating
system</i>.""")
bullet("""A 'build system' for complex documents with charts, tables
and text such as management accounts, statistical reports and
scientific papers """)
bullet("""Going from XML to PDF in one step""")


heading2("ReportLab's commercial software")
disc("""
The ReportLab library forms the foundation of our commercial solution for
PDF generation, Report Markup Language (RML).  This is available for evaluation
on our web site with full documentation.   We believe that RML is the fastest
and easiest way to develop rich PDF workflows.  You work in a markup language
at a similar level to HTML, using your favorite templating system to populate
an RML document; then call our rml2pdf API function to generate a PDF.  It's
what ReportLab staff use to build all of the solutions you can see on reportlab.com.
Key differences:
""")
bullet("""Fully documented with two manuals, a formal specification (the DTD) and extensive self-documenting tests.  (By contrast, we try to make sure the open source documentation isn't wrong, but we don't always keep up with the code)""")
bullet("""Work in high-level markup rather than constructing graphs of Python objects """)
bullet("""Requires no Python expertise - your colleagues may thank you after you've left!'""")
bullet("""Support for vector graphics and inclusion of other PDF documents""")
bullet("""Many more useful features expressed with a single tag, which would need a lot
of coding in the open source package""")
bullet("""Commercial support is included""")


disc("""
We ask open source developers to consider trying out RML where it is appropriate.
You can register on our site and try out a copy before buying.
The costs are reasonable and linked to the volume of the project, and the revenue
helps us spend more time developing this software.""")


heading2("What is Python?")
disc("""
Python is an <i>interpreted, interactive, object-oriented</i> programming language. It is often compared to Tcl, Perl,
Scheme or Java.
""")

disc("""
Python combines remarkable power with very clear syntax. It has modules, classes, exceptions, very high level
dynamic data types, and dynamic typing. There are interfaces to many system calls and libraries, as well as to
various windowing systems (X11, Motif, Tk, Mac, MFC). New built-in modules are easily written in C or C++.
Python is also usable as an extension language for applications that need a programmable interface.
""")


disc("""
Python is as old as Java and has been growing steadily in popularity for years; since our
library first came out it has entered the mainstream.  Many ReportLab library users are
already Python devotees, but if you are not, we feel that the language is an excellent
choice for document-generation apps because of its expressiveness and ability to get
data from anywhere.
""")

disc("""
Python is copyrighted but <b>freely usable and distributable, even for commercial use</b>.
""")

heading2("Acknowledgements")
disc("""Many people have contributed to ReportLab.  We would like to thank in particular 
(in alphabetical order): 
Albertas Agejevas, 
Alex Buck, 
Andre Reitz, 
Andrew Cutler,
Andrew Mercer, 
Ben Echols,
Benjamin Dumke,
Benn B,
Chad Miller, 
Chris Lee, 
Christian Jacobs, 
Dinu Gherman,
Eric Johnson,
Felix Labrecque,  
Gary Poster, 
Germán M. Bravo,
Guillaume Francois, 
Hans Brand,
Henning Vonbargen,
Hosam Aly,
Ian Stevens, 
James Martin-Collar, 
Jeff Bauer,
Jerome Alet,
Jerry Casiano,
Jorge Godoy,
Keven D Smith,
Magnus Lie Hetland,
Marcel Tromp, 
Marius Gedminas,
Matthew Duggan,
Matthias Kirst,
Matthias Klose,
Max M, 
Michael Egorov,
Mike Folwell,
Mirko Dziadzka,
Moshe Wagner,
Nate Silva,
Paul McNett, 
Peter Johnson, 
PJACock,
Publio da Costa Melo,  
Randolph Bentson,
Robert Alsina,
Robert Hölzl,
Robert Kern,
Ron Peleg,
Simon King,
Stephan Richter,
Steve Halasz, 
T Blatter,
Tim Roberts,
Tomasz Swiderski,
Ty Sarna,
Volker Haas,
Yoann Roman, 
and many more.""")


disc("""Special thanks go to Just van Rossum for his valuable assistance with
font technicalities.""")

disc("""Moshe Wagner and Hosam Aly deserve a huge thanks for contributing to the RTL patch, which is not yet on the trunk.""")

disc("""Marius Gedminas deserves a big hand for contributing the work on TrueType fonts and we
are glad to include these in the toolkit. Finally we thank Michal Kosmulski for the DarkGarden font
for and Bitstream Inc. for the Vera fonts.""")

heading2("Installation and Setup")

disc("""To avoid duplication, the installation instructions are kept in the README file
in our distribution, which can be viewed online at ^http://bitbucket.org/rptlab/reportlab/^""")

disc("""This release (3.0) of ReportLab requires Python versions 2.7, 3.3 or higher.  
	If you need to use Python 2.5 or 2.6, please use the latest ReportLab 2.x package.
""")



heading2("Getting Involved")
disc("""ReportLab is an Open Source project.  Although we are
a commercial company we provide the core PDF generation
sources freely, even for commercial purposes, and we make no income directly
from these modules.  We also welcome help from the community
as much as any other Open Source project.  There are many
ways in which you can help:""")

bullet("""General feedback on the core API. Does it work for you?
Are there any rough edges?  Does anything feel clunky and awkward?""")

bullet("""New objects to put in reports, or useful utilities for the library.
We have an open standard for report objects, so if you have written a nice
chart or table class, why not contribute it?""")

bullet("""Snippets and Case Studies: If you have produced some nice
output, register online on ^http://www.reportlab.com^ and submit a snippet
of your output (with or without scripts).  If ReportLab solved a
problem for you at work, write a little 'case study' and submit it.
And if your web site uses our tools to make reports, let us link to it.
We will be happy to display your work (and credit it with your name
and company) on our site!""")

bullet("""Working on the core code:  we have a long list of things
to refine or to implement.  If you are missing some features or
just want to help out, let us know!""")

disc("""The first step for anyone wanting to learn more or
get involved is to join the mailing list.  To Subscribe visit
$http://two.pairlist.net/mailman/listinfo/reportlab-users$.
From there you can also browse through the group's archives
and contributions.  The mailing list is
the place to report bugs and get support. """)

disc("""The code now lives on BitBucket ($http://bitbucket.org/rptlab/reportlab/$)
in a Mercurial repository, along with an issue tracker and wiki.  Everyone should
feel free to contribute, but if you are working actively on some improvements
or want to draw attention to an issue, please use the mailing list to let us know.""")



heading2("Site Configuration")
disc("""There are a number of options which most likely need to be configured globally for a site.
The python script module $reportlab/rl_config.py$ may be edited to change the values of several
important sitewide properties.""")
bullet("""verbose: set to integer values to control diagnostic output.""")
bullet("""shapeChecking: set this to zero to turn off a lot of error checking in the graphics modules""")
bullet("""defaultEncoding: set this to WinAnsiEncoding or MacRomanEncoding.""")
bullet("""defaultPageSize: set this to one of the values defined in reportlab/lib/pagesizes.py; as delivered
it is set to pagesizes.A4; other values are pagesizes.letter etc.""")
bullet("""defaultImageCaching: set to zero to inhibit the creation of .a85 files on your
hard-drive. The default is to create these preprocessed PDF compatible image files for faster loading""")
bullet("""T1SearchPath: this is a python list of strings representing directories that
may be queried for information on Type 1 fonts""")
bullet("""TTFSearchPath: this is a python list of strings representing directories that
may be queried for information on TrueType fonts""")
bullet("""CMapSearchPath: this is a python list of strings representing directories that
may be queried for information on font code maps.""")
bullet("""showBoundary: set to non-zero to get boundary lines drawn.""")
bullet("""ZLIB_WARNINGS: set to non-zero to get warnings if the Python compression extension is not found.""")
bullet("""pageComression: set to non-zero to try and get compressed PDF.""")
bullet("""allowtableBoundsErrors: set to 0 to force an error on very large Platypus table elements""")
bullet("""emptyTableAction: Controls behaviour for empty tables, can be 'error' (default), 'indicate' or 'ignore'.""")

heading2("Learning More About Python")

disc("""
If you are a total beginner to Python, you should check out one or more from the
growing number of resources on Python programming. The following are freely
available on the web:
""")


bullet("""<b>Python Documentation.  </b>
A list of documentation on the Python.org web site.
$http://www.python.org/doc/$
""")


bullet("""<b>Python Tutorial.  </b>
The official Python Tutorial , originally written by Guido van Rossum himself.
$http://docs.python.org/tutorial/$
""")


bullet("""<b>Learning to Program.  </b>
A tutorial on programming by Alan Gauld. Has a heavy emphasis on
Python, but also uses other languages.
$http://www.freenetpages.co.uk/hp/alan.gauld/$
""")


bullet("""<b>Instant Python</b>.
A 6-page minimal crash course by Magnus Lie Hetland.
$http://www.hetland.org/python/instant-python.php$
""")


bullet("""<b>Dive Into Python</b>.
A free Python tutorial for experienced programmers.
$http://www.diveintopython.net/$
""")


from reportlab.lib.codecharts import SingleByteEncodingChart
from tools.docco.stylesheet import getStyleSheet
styles = getStyleSheet()
indent0_style = styles['Indent0']
indent1_style = styles['Indent1']

heading2("Goals for the 3.x release series")
disc("""ReportLab 3.0 has been produced to help in the migration to Python 3.x.  Python 3.x will
be standard in future Ubuntu releases and is gaining popularity, and a good proportion
of major Python packages now run on Python 3.  """)



bullet("""Python 3.x compatibility.  A single line of code should run on 2.7 and 3.3""")
bullet(""" __init__.py restricts to 2.7 or >=3.3""")
bullet("""__init__.py allow the import of on optional reportlab.local_rl_mods to allow monkey patching etc.""")
bullet("""rl_config now imports rl_settings & optionally local_rl_settings""")
bullet("""ReportLab C extensions now live inside reportlab; _rl_accel is no longer required. All _rl_accel imports now pass through reportlab.lib.rl_accel""")
bullet("""xmllib is gone, alongside the paraparser stuff that caused issues in favour of HTMLParser.""")
bullet("""some obsolete C extensions (sgmlop and pyHnj) are gone""")
bullet("""Improved support for multi-threaded systems to the _rl_accel C extension module.""")
bullet("""Removed reportlab/lib/ para.py & pycanvas.py.  These would better belong in third party packages, which can make use of the monkeypatching feature above.""")
bullet("""Add ability to output greyscale and 1-bit PIL images without conversion to RGB. (contributed by Matthew Duggan)""")
bullet("""highlight annotation (contributed by Ben Echols)""")
bullet("""full compliance with pip, easy_install, wheels etc""")




disc("""Detailed release notes are available at 
$http://www.reportlab.com/software/documentation/relnotes/30/$""")



