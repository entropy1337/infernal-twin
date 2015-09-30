#!/usr/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details

"""This is a test on a package level that find all modules,
classes, methods and functions that do not have a doc string
and lists them in individual log files.

Currently, methods with leading and trailing double underscores
are skipped.
"""
from reportlab.lib.testutils import setOutDir,SecureTestCase, GlobDirectoryWalker, outputfile, printLocation
setOutDir(__name__)
import os, sys, glob, re, unittest, inspect
import reportlab
isPy3= reportlab.isPy3
from reportlab.lib.utils import rl_exec

def typ2is(typ):
    return getattr(inspect,'is'+typ)

_typ2key={
        'module':lambda x: (x[0],getattr(x[1],'__name__',''),getattr(x[1],'__path__',getattr(x,'__file__',''))),
        'class':lambda x: (x[0],getattr(x[1],'__name__',''),getattr(x[1],'__module__','')),
        'method':lambda x: (x[0],getattr(x[1],'__name__',''),getattr(x[1],'__module__','')),
        'function':lambda x: (x[0],getattr(x[1],'__name__',''),x[1].__code__.co_filename),
        }
def typ2key(typ):
    return _typ2key[typ]

def obj2typ(obj):
    for typ in ('function','module','class','method'):
        if typ2is(typ)(obj): return typ
    return None


def getClass(obj):
    try:
        return obj.__self__.__class__
    except:
        try:
            return obj.im_class
        except:
            return None

from pkgutil import iter_modules
def walk_packages_ex(path=None, prefix='', onerror=None, cond=None):
    def seen(p, m={}):
        if p in m:
            return True
        m[p] = True

    for importer, name, ispkg in iter_modules(path, prefix):
        if cond and not cond(importer,name,ispkg): continue
        yield importer, name, ispkg

        if ispkg:
            try:
                __import__(name)
            except ImportError:
                if onerror is not None:
                    onerror(name)
            except Exception:
                if onerror is not None:
                    onerror(name)
                else:
                    raise
            else:
                path = getattr(sys.modules[name], '__path__', None) or []

                # don't traverse path items we've seen before
                path = [p for p in path if not seen(p)]

                for item in walk_packages_ex(path, name+'.', onerror, cond):
                    yield item

def rl_module(i,name,pkg):
    return name=='reportlab' or name.startswith('reportlab.')

rl_modules = None
def getRLModules():
    "Get a list of all objects defined *somewhere* in a package."
    global rl_modules
    if rl_modules is None:
        rl_modules = []
        for _,name,_ in walk_packages_ex(cond=rl_module):
            rl_modules.append(name)
    return rl_modules

def getObjects(objects,lookup,mName,modBn,tobj):
    ttyp = obj2typ(tobj)
    for n in dir(tobj):
        obj = getattr(tobj,n,None)
        try:
            if obj in lookup: continue
        except:
            continue
        typ = obj2typ(obj)
        if typ in ('function','method'):
            if os.path.splitext(obj.__code__.co_filename)[0]==modBn:
                lookup[obj] = 1
                objects.setdefault(typ if typ=='function' and ttyp=='module' else 'method',[]).append((mName,obj))
        elif typ=='class':
            if obj.__module__==mName:
                lookup[obj] = 1
                objects.setdefault(typ,[]).append((mName,obj))
                getObjects(objects,lookup,mName,modBn,obj)

def getModuleObjects(modules):
    objects = {}
    lookup = {}
    for mName in modules:
        try:
            NS = {}
            rl_exec("import %s as module" % mName,NS)
        except ImportError:
            continue
        else:
            module = NS['module']
        if module in lookup: continue

        lookup[module] = 1
        objects.setdefault('module',[]).append((mName, module))
        modBn = os.path.splitext(module.__file__)[0]
        getObjects(objects,lookup,mName,modBn,module)
    return objects

class DocstringTestCase(SecureTestCase):
    "Testing if objects in the ReportLab package have docstrings."

    def setUp(self):
        SecureTestCase.setUp(self)
        self.modules = getRLModules()
        self.objects = getModuleObjects(self.modules)

    def _writeLogFile(self, typ):
        "Write log file for different kind of documentable objects."

        objects = self.objects.get(typ,[])
        objects.sort(key=typ2key(typ))

        expl = {'function':'functions',
                'class':'classes',
                'method':'methods',
                'module':'modules'}[typ]

        path = outputfile("test_docstrings-%s.log" % expl)
        file = open(path, 'w')
        file.write('No doc strings found for the following %s below.\n\n' % expl)
        p = re.compile('__.+__')

        lines = []
        for name, obj in objects:
            if typ == 'method':
                n = obj.__name__
                # Skip names with leading and trailing double underscores.
                if p.match(n):
                    continue

            if not obj.__doc__ or len(obj.__doc__) == 0:
                if typ == 'function':
                    lines.append("%s.%s\n" % (name, obj.__name__))
                elif typ == 'class':
                    lines.append("%s.%s\n" % (obj.__module__, getattr(obj,'__qualname__',getattr(obj,'__name__','[unknown __name__]'))))
                else:
                    lines.append("%s\n" % (getattr(obj,'__qualname__',getattr(obj,'__name__','[unknown __name__]'))))

        lines.sort()
        for line in lines:
            file.write(line)

        file.close()

    def test0(self):
        "Test if functions have a doc string."
        self._writeLogFile('function')

    def test1(self):
        "Test if classes have a doc string."
        self._writeLogFile('class')

    def test2(self):
        "Test if methods have a doc string."
        self._writeLogFile('method')

    def test3(self):
        "Test if modules have a doc string."
        self._writeLogFile('module')

def makeSuite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    if sys.platform[:4] != 'java': suite.addTest(loader.loadTestsFromTestCase(DocstringTestCase))
    return suite

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
