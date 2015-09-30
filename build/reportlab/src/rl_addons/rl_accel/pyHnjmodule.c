/* pyHnj is dual licensed under LGPL and MPL. Boilerplate for both
 * licenses follows.
 */

/* pyHnj --- a Python extention wrapper for the libhnj hyphenation library
 * Copyright (C) 2000 Danny Yoo
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the 
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330, 
 * Boston, MA  02111-1307  USA.
*/

/*
 * The contents of this file are subject to the Mozilla Public License
 * Version 1.0 (the "MPL"); you may not use this file except in
 * compliance with the MPL.  You may obtain a copy of the MPL at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the MPL is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the MPL
 * for the specific language governing rights and limitations under the
 * MPL.
 *
 */

#include "Python.h"
#include "hyphen.h"

static PyObject *ErrorObject;

/* ----------------------------------------------------- */

/* Declarations for objects of type Hyphen */

typedef struct {
	PyObject_HEAD
	HyphenDict *hdict;
} Hyphenobject;

staticforward PyTypeObject Hyphentype;


/* ---------------------------------------------------------------- */

static char Hyphen_hyphenate__doc__[] = 
"word -> word with hyphen marks '-' inserted at breakpoints.\n\
\n\
For example:\n\
\n\
###\n\
>>> h = pyHnj.Hyphen()\n\
>>> h.hyphenate('hyphenation')\n\
'hy-phen-ation'\n\
>>> h.hyphenate('supercalifragilisticexpialidocious')\n\
su-per-cal-ifrag-ilis-tic-ex-pi-ali-do-cious\n\
###\n\
\n\
We place hyphens between points where the hyphen code is odd.  Use\n\
getCodes() to view the internal hyphen codes.\n\
\n\
Bugs: It doesn't quite work if there are spaces in the word.  Also,\n\
hyphenating a word twice doesn't look good:\n\
    'su--pe-r-c-al-if-rag--ili-s--ti-c-e-x--pi-ali-do-cious'\n\
";


/* Return the number of odd numbers within the breakcode.  In effect,
   this find the number of hyphens necessary in a full hypheniation.*/
static int countHyphenIntegers(char *mystring) {
  int i = 0;
  while(*mystring != '\0') {
    if (*mystring % 2 == 1)
      i++;
    mystring++;
  }
  return i;
}
/* A utility function to actually fill scratch with the word, along
   with hyphens.  Assumes that enough space has been allocated to
   scratch. */
static void placeHyphens(const char *word, char *buffer, char *scratch) {
  char *tmp = scratch;
  int i = 0;
  while(word[i] != '\0') {
    *tmp = word[i];
    tmp++;
    if((buffer[i]-'0') % 2 == 1) {
      *tmp = '-';
      tmp++;
    }    
    i++;
  }
  *tmp='\0';
}


/* Hyphenate a word completely. */
static PyObject *
Hyphen_hyphenate(Hyphenobject *self, PyObject *args) {
  const char *word;
  char *buffer;
  char *scratch;
  PyObject* result;

  const int BORDER = 2;
  if (!PyArg_ParseTuple(args, "s", &word)) /* No word to hyphenate */
    return NULL;

  buffer = malloc(sizeof(char) * (strlen(word)+BORDER+1));
  if (buffer == NULL) {
    PyErr_NoMemory();
    return NULL; /* out of memory */
  }

  hnj_hyphen_hyphenate(self->hdict, word, strlen(word), buffer);  

  scratch = (char*) malloc(sizeof(char) * 
			   (strlen(word) +  countHyphenIntegers(buffer) + 1));
  if(scratch == NULL) {
    PyErr_NoMemory();
    free(buffer); buffer = NULL;  /* out of memory */
    return NULL;
  }
  
  placeHyphens(word, buffer, scratch);

  free(buffer);
  if((result = Py_BuildValue("s", scratch)) == NULL) {
    free(scratch);
    return NULL;
  }
  free(scratch);
  return result;
}


static char Hyphen_getCodes__doc__[] = 
"word -> The corresponding hyphenation codes.\n\
\n\
Here is an example interpreter session:\n\
\n\
>>> pyHnj.Hyphen().getCodes('hyphenation')\n\
'03002542000'\n\
\n\
The odd numbers correspond to good places to hyphenate a word.  For\n\
more details on the hyphenation algorithm, you may want to read Donald\n\
Knuth's TeXbook. (ISBN 0-201-13448-9)\n\
";

static PyObject *
Hyphen_getCodes(Hyphenobject* self, PyObject* args) {
  const char *word;
  char *buffer;
  PyObject *result;
  const int border = 2;  /* For some reason, libhnj needs the buffer
                            to contain at least 2 extra spaces in the
                            buffer that it writes into.*/
  if (!PyArg_ParseTuple(args, "s", &word))
    return NULL;

  buffer = malloc(sizeof(char) * (strlen(word)+border+1));
  if (buffer == 0) {
    PyErr_NoMemory();
    return NULL;
  }

  hnj_hyphen_hyphenate(self->hdict, word, strlen(word), buffer);  
  buffer[strlen(word)] = '\0';
  result = Py_BuildValue("s", buffer);

  free(buffer);
  return result;
}


static struct PyMethodDef Hyphen_methods[] = {
  {"hyphenate", (PyCFunction)Hyphen_hyphenate, METH_VARARGS, Hyphen_hyphenate__doc__},
  {"getCodes", (PyCFunction)Hyphen_getCodes, METH_VARARGS, Hyphen_getCodes__doc__},
  {NULL, NULL}		/* sentinel */
};

/* ---------- */


static char Hyphen_newHyphenobject__doc__[] =
"name of hyphen dictionary -> instance of Hyphen.\n\
\n\
pyHnj needs a source of hyphen prefixes, so we read it here.  If no\n\
such dictionary exists, or if we cannot read is succesfully, we raise\n\
pyHnj.Error.\n\
";

static Hyphenobject *
newHyphenobject(PyObject *module, PyObject *args) {
  Hyphenobject *self = NULL;
  char *filename = NULL;

  PyArg_ParseTuple(args, "|s", &filename);

  if(filename == NULL)
    filename = "/usr/local/share/pyHnj/hyphen.mashed";  /* default */
    
  self = PyObject_NEW(Hyphenobject, &Hyphentype);
  if (self == NULL)
    return NULL;

  if((self->hdict = hnj_hyphen_load(filename)) == NULL){
	PyErr_Format(PyExc_IOError,"Failed to load hyphenization information from \"%s\"", filename);
	Py_DECREF(self);
    return NULL;
  	}

  return self;
}

static void
Hyphen_dealloc(Hyphenobject *self) {
  if (self->hdict != NULL) {
    hnj_hyphen_free(self->hdict);
    self->hdict = NULL;
  }
  PyObject_DEL(self);
}

static PyObject *
Hyphen_getattr(Hyphenobject *self, char *name) {
  return Py_FindMethod(Hyphen_methods, (PyObject *)self, name);
}

static char Hyphentype__doc__[] = 
"Hyphen instance.\n\
\n\
Hyphen provides the following two functions:\n\
\n\
    getCodes(word) - return the hyphen codes as a string of numbers.\n\
    hyphenate(word) - hyphenate a word using '-'.\n\
\n\
The use of hyphenate() should make abusive hyphenation quite easy.\n\
*grin*\n\
";

static PyTypeObject Hyphentype = {
  PyObject_HEAD_INIT(0)
  0,				/*ob_size*/
  "Hyphen",			/*tp_name*/
  sizeof(Hyphenobject),		/*tp_basicsize*/
  0,				/*tp_itemsize*/
  /* methods */
  (destructor)Hyphen_dealloc,	/*tp_dealloc*/
  (printfunc)0,		/*tp_print*/
  (getattrfunc)Hyphen_getattr,	/*tp_getattr*/
  (setattrfunc)0,	/*tp_setattr*/
  (cmpfunc)0,		/*tp_compare*/
  (reprfunc)0,		/*tp_repr*/
  0,			/*tp_as_number*/
  0,		/*tp_as_sequence*/
  0,		/*tp_as_mapping*/
  (hashfunc)0,		/*tp_hash*/
  (ternaryfunc)0,		/*tp_call*/
  (reprfunc)0,		/*tp_str*/
  
  /* Space for future expansion */
  0L,0L,0L,0L,
  Hyphentype__doc__ /* Documentation string */
};

/* End of code for Hyphen objects */
/* -------------------------------------------------------- */


/* List of methods defined in the module */

static struct PyMethodDef pyHnj_methods[] = {
  {"Hyphen", (PyCFunction)newHyphenobject, METH_VARARGS, Hyphen_newHyphenobject__doc__},
  {NULL, (PyCFunction)NULL, 0, NULL}		/* sentinel */
};


/* Initialization function for the module (*must* be called initpyHnj) */

static char pyHnj_module_documentation[] = 
"This is the pyHnj module.  This code is based on the hyphenization\n\
algorithm in Donald Knuth's TeX.  This particular implementation has\n\
been written by Raph Levien (raph@acm.org).\n\
\n\
This module provides a single Hyphen class which is a wrapper around\n\
Levien's nice pyHnj library.\n\
\n\
Hyphen's constructor takes in, optionally, the name of a prefix text\n\
file.  This module should be distributed with 'hyphen.mashed', which\n\
can process English.\n\
\n\
Functions within Hyphen:\n\
\n\
    getCodes(word)\n\
    hyphenate(word)\n\
";

void
initpyHnj() {
  PyObject *m, *d;

  /* necessary to manually set the type */
  Hyphentype.ob_type = &PyType_Type; 

  /* Create the module and add the functions */
  m = Py_InitModule4("pyHnj", pyHnj_methods,
		     pyHnj_module_documentation,
		     (PyObject*)NULL,PYTHON_API_VERSION);
  
  /* Add some symbolic constants to the module */
  d = PyModule_GetDict(m);
  ErrorObject = PyString_FromString("pyHnj.error");
  PyDict_SetItemString(d, "error", ErrorObject);
  
  
  /* Check for errors */
  if (PyErr_Occurred())
    Py_FatalError("can't initialize module pyHnj");
}
