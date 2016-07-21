#Copyright ReportLab Europe Ltd. 2000-2015
#see license.txt for license details
__doc__="""The Reportlab PDF generation library."""
Version = "3.2.0"
__version__=Version

import sys, os, imp

if sys.version_info[0:2]!=(2, 7) and sys.version_info<(3, 3):
    raise ImportError("""reportlab requires Python 2.7+ or 3.3+; 3.0-3.2 are not supported.""")

#define these early in reportlab's life
isPy3 = sys.version_info[0]==3
if isPy3:
    def cmp(a,b):
        return -1 if a<b else (1 if a>b else 0)

    import builtins
    builtins.cmp = cmp
    builtins.xrange = range
    del cmp, builtins
else:
    from future_builtins import ascii
    import __builtin__
    __builtin__.ascii = ascii
    del ascii, __builtin__

#try to use dynamic modifications from
#reportlab.local_rl_mods.py
#reportlab_mods.py or ~/.reportlab_mods
try:
    import reportlab.local_rl_mods
except ImportError:
    pass

def _fake_import(fn,name):
    if os.path.isfile(fn):
        with open(fn,'rb') as f:
            imp.load_source(name,fn,f)

try:
    import reportlab_mods   #application specific modifications can be anywhere on python path
except ImportError:
    try:
        _fake_import(os.path.expanduser(os.path.join('~','.reportlab_mods')),'reportlab_mods')
    except (ImportError,KeyError):
        pass
