/*
* Copyright ReportLab Europe Ltd. 2000-2007
* licensed under the same terms as the ReportLab Toolkit
* see http://www.reportlab.co.uk/svn/public/reportlab/trunk/reportlab/license.txt
* for details.
* history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/lib/_rl_accel.c
*/
#include "Python.h"
#if PY_MAJOR_VERSION >= 3
#	define isPy3
#endif
#include <stdlib.h>
#include <math.h>
#define DEFERRED_ADDRESS(A) 0
#if defined(__GNUC__) || defined(sun) || defined(_AIX) || defined(__hpux)
#	define STRICMP strcasecmp
#elif defined(_MSC_VER)
#	define STRICMP stricmp
#elif defined(macintosh)
# include <extras.h>
# define strdup _strdup
# define STRICMP _stricmp
#else
#	error "Don't know how to define STRICMP"
#endif
#ifndef max
#	define max(a,b) ((a)>(b)?(a):(b))
#endif
#ifndef min
#	define min(a,b) ((a)<(b)?(a):(b))
#endif
#define VERSION "0.70"
#define MODULE "_rl_accel"

struct module_state	{
	PyObject *moduleVersion;
	int moduleLineno;
#ifndef isPy3
	PyObject *module;
#endif
	};
#ifdef isPy3
#	define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#	define STRNAME "str"
#	define BYTESNAME "bytes"
#else
	static struct module_state _state;
#	include "bytesobject.h"
#	ifndef PyVarObject_HEAD_INIT
#		define PyVarObject_HEAD_INIT(type, size) \
        	PyObject_HEAD_INIT(type) size,
#	endif
#	ifndef Py_TYPE
#		define Py_TYPE(ob) (((PyObject*)(ob))->ob_type)
#	endif
#	define PyBytes_AS_STRING	PyString_AS_STRING
#	define PyBytes_AsString		PyString_AsString
#	define PyBytes_GET_SIZE 	PyString_GET_SIZE
#	define GETSTATE(m) (&_state)
#	define STRNAME "unicode"
#	define BYTESNAME "str"
#endif

#define ERROR_EXIT() {GETSTATE(module)->moduleLineno=__LINE__;goto L_ERR;}
#define ADD_TB(module,name) _add_TB(module,name)
#include "compile.h"
#include "frameobject.h"
#include "traceback.h"
static void _add_TB(PyObject *module,char *funcname)
{
	int	moduleLineno = GETSTATE(module)->moduleLineno;
	PyObject *py_globals = NULL;
	PyCodeObject *py_code = NULL;
	PyFrameObject *py_frame = NULL;

#ifdef isPy3
	py_globals = PyModule_GetDict(module);
#else
	py_globals = PyModule_GetDict(GETSTATE(module)->module);
#endif
	if(!py_globals) goto bad;
	py_code = PyCode_NewEmpty(
						__FILE__,		/*PyObject *filename,*/
						funcname,	/*PyObject *name,*/
						moduleLineno	/*int firstlineno,*/
						);
	if(!py_code) goto bad;
	py_frame = PyFrame_New(
		PyThreadState_Get(), /*PyThreadState *tstate,*/
		py_code,			 /*PyCodeObject *code,*/
		py_globals,			 /*PyObject *globals,*/
		0					 /*PyObject *locals*/
		);
	if(!py_frame) goto bad;
	py_frame->f_lineno = moduleLineno;
	PyTraceBack_Here(py_frame);
bad:
	Py_XDECREF(py_code);
	Py_XDECREF(py_frame);
}

#define a85_0		   1L
#define a85_1		   85L
#define a85_2		 7225L
#define a85_3	   614125L
#define a85_4	 52200625L

PyObject *_a85_encode(PyObject *module, PyObject *args)
{
	unsigned char	*inData;
	int				length, blocks, extra, i, k, lim;
	unsigned long	block, res;
	char			*buf;
	PyObject		*retVal=NULL, *inObj, *_o1=NULL;
	if(!PyArg_ParseTuple(args, "O", &inObj)) return NULL;
	if(PyUnicode_Check(inObj)){
		_o1 = PyUnicode_AsLatin1String(inObj);
		if(!_o1){
			PyErr_SetString(PyExc_ValueError,"argument not decodable as latin1");
			ERROR_EXIT();
			}
		inData = PyBytes_AsString(_o1);
		inObj = _o1;
		if(!inData){
			PyErr_SetString(PyExc_ValueError,"argument not converted to internal char string");
			ERROR_EXIT();
			}
		}
	else if(!PyBytes_Check(inObj)){
		PyErr_SetString(PyExc_ValueError,"argument should be " BYTESNAME " or latin1 decodable " STRNAME);
		ERROR_EXIT();
		}
	inData = PyBytes_AsString(inObj);
	length = PyBytes_GET_SIZE(inObj);

	blocks = length / 4;
	extra = length % 4;

	buf = (char*)malloc((blocks+1)*5+3);
	lim = 4*blocks;

	for(k=i=0; i<lim; i += 4){
		/*
		 * If you evere have trouble with this consider using masking to ensure
		 * that the shifted quantity is only 8 bits long
		 */
		block = ((unsigned long)inData[i]<<24)|((unsigned long)inData[i+1]<<16)
				|((unsigned long)inData[i+2]<<8)|((unsigned long)inData[i+3]);
		if (block == 0) buf[k++] = 'z';
		else {
			res = block/a85_4;
			buf[k++] = (char)(res+33);
			block -= res*a85_4;

			res = block/a85_3;
			buf[k++] = (char)(res+33);
			block -= res*a85_3;

			res = block/a85_2;
			buf[k++] = (char)(res+33);
			block -= res*a85_2;

			res = block / a85_1;
			buf[k++] = (char)(res+33);

			buf[k++] = (char)(block-res*a85_1+33);
			}
		}

	if(extra>0){
		block = 0L;

		for (i=0; i<extra; i++)
			block += (unsigned long)inData[length-extra+i] << (24-8*i);

		res = block/a85_4;
		buf[k++] = (char)(res+33);
		if(extra>=1){
			block -= res*a85_4;

			res = block/a85_3;
			buf[k++] = (char)(res+33);
			if(extra>=2){
				block -= res*a85_3;

				res = block/a85_2;
				buf[k++] = (char)(res+33);
				if(extra>=3) buf[k++] = (char)((block-res*a85_2)/a85_1+33);
				}
			}
		}

	buf[k++] = '~';
	buf[k++] = '>';
	retVal = PyUnicode_FromStringAndSize(buf, k);
	free(buf);
	if(!retVal){
		PyErr_SetString(PyExc_ValueError,"failed to create return " STRNAME " value" );
		ERROR_EXIT();
		}
L_exit:
	Py_XDECREF(_o1);
	return retVal;
L_ERR:
	ADD_TB(module,"asciiBase85Encode");
	goto L_exit;
}

PyObject *_a85_decode(PyObject *module, PyObject *args)
{
	unsigned char	*inData, *p, *q, *tmp, *buf;
	unsigned int	length, blocks, extra, k, num, c1, c2, c3, c4, c5;
	static unsigned pad[] = {0,0,0xffffff,0xffff,0xff};
	PyObject		*retVal=NULL, *inObj, *_o1=NULL;
	if(!PyArg_ParseTuple(args, "O", &inObj)) return NULL;
	if(PyUnicode_Check(inObj)){
		_o1 = PyUnicode_AsLatin1String(inObj);
		if(!_o1){
			PyErr_SetString(PyExc_ValueError,"argument not decodable as latin1");
			ERROR_EXIT();
			}
		inData = PyBytes_AsString(_o1);
		inObj = _o1;
		if(!inData){
			PyErr_SetString(PyExc_ValueError,"argument not converted to internal char string");
			ERROR_EXIT();
			}
		}
	else if(!PyBytes_Check(inObj)){
		PyErr_SetString(PyExc_ValueError,"argument should be " BYTESNAME " or latin1 decodable " STRNAME);
		ERROR_EXIT();
		}
	inData = PyBytes_AsString(inObj);
	length = PyBytes_GET_SIZE(inObj);
	for(k=0,q=inData, p=q+length;q<p && (q=(unsigned char*)strchr((const char*)q,'z'));k++, q++);	/*count 'z'*/
	length += k*4;
	tmp = q = (unsigned char*)malloc(length+1);
	while(inData<p && (k = *inData++)){
		if(isspace(k)) continue;
		if(k=='z'){
			/*turn 'z' into '!!!!!'*/
			memcpy(q,"!!!!!",5);
			q += 5;
			}
		else
			*q++ = k;
		}
	inData = tmp;
	length = q - inData;
	buf = inData+length-2;
	if(buf[0]!='~' || buf[1]!='>'){
		PyErr_SetString(PyExc_ValueError, "Invalid terminator for Ascii Base 85 Stream");
		free(inData);
		ERROR_EXIT();
		}
	length -= 2;
	buf[0] = 0;

	blocks = length / 5;
	extra = length % 5;

	buf = (unsigned char*)malloc((blocks+1)*4);
	q = inData+blocks*5;
	for(k=0;inData<q;inData+=5){
		c1 = inData[0]-33;
		c2 = inData[1]-33;
		c3 = inData[2]-33;
		c4 = inData[3]-33;
		c5 = inData[4]-33;
		num = (((c1*85+c2)*85+c3)*85+c4)*85+c5;
		buf[k++] = num>>24;
		buf[k++] = num>>16;
		buf[k++] = num>>8;
		buf[k++] = num;
		}
	if(extra>1){
		c1 = inData[0]-33;
		c2 = extra>=2 ? inData[1]-33: 0;
		c3 = extra>=3 ? inData[2]-33: 0;
		c4 = extra>=4 ? inData[3]-33: 0;
		c5 = 0;
		num = (((c1*85+c2)*85+c3)*85+c4)*85+c5 + pad[extra];
		if(extra>1){
			buf[k++] = num>>24;
			if(extra>2){
				buf[k++] = num>>16;
				if(extra>3){
					buf[k++] = num>>8;
					}
				}
			}
		}
	retVal = PyBytes_FromStringAndSize((const char*)buf, k);
	free(buf);
	free(tmp);
	if(!retVal){
		PyErr_SetString(PyExc_ValueError,"failed to create return " BYTESNAME " value" );
		ERROR_EXIT();
		}
L_exit:
	Py_XDECREF(_o1);
	return retVal;
L_ERR:
	ADD_TB(module,"asciiBase85Decode");
	goto L_exit;
}

static	char* _fp_fmts[]={"%.0f", "%.1f", "%.2f", "%.3f", "%.4f", "%.5f", "%.6f"};
static	char *_fp_one(PyObject* module,PyObject *pD)
{
	double	d, ad;
	static	char s[30];
	int l;
	char*	dot;
	if((pD=PyNumber_Float(pD))){
		d = PyFloat_AS_DOUBLE(pD);
		Py_DECREF(pD);
		}
	else {
		PyErr_SetString(PyExc_ValueError, "bad numeric value");
		return NULL;
		}
	ad = fabs(d);
	if(ad<=1.0e-7){
		s[0]='0';
		s[1]=0;
		}
	else{
		if(ad>1e20){
			PyErr_SetString(PyExc_ValueError, "number too large");
			return NULL;
			}
		if(ad>1) l = min(max(0,6-(int)log10(ad)),6);
		else l = 6;
		sprintf(s,_fp_fmts[l], d);
		if(l){
			l = strlen(s)-1;
			while(l && s[l]=='0') l--;
			if(s[l]=='.' || s[l]==',') s[l]=0;
			else {
				s[l+1]=0;
				if(s[0]=='0' && (s[1]=='.'||s[1]==',')){
					if(s[1]==',') s[1] = '.';
					return s+1;
					}
				}
			if((dot=strchr(s,','))) *dot = '.';
			}
		}
	return s;
}

PyObject *_fp_str(PyObject *module, PyObject *args)
{
	int				aL;
	PyObject		*retVal;
	char			*pD;
	char			*buf, *pB;
	int				i;

	if((aL=PySequence_Length(args))>=0){
		if(aL==1){
			retVal = PySequence_GetItem(args,0);
			if((i=PySequence_Length(retVal))>=0){
				aL = i;
				args = retVal;
				}
			else PyErr_Clear();
			Py_DECREF(retVal);
			}
		buf=malloc(31*aL);
		pB = buf;
		for(i=0;i<aL;i++){
			retVal = PySequence_GetItem(args,i);
			if(retVal){
				pD = _fp_one(module,retVal);
				Py_DECREF(retVal);
				}
			else pD = NULL;
			if(!pD){
				free(buf);
				return NULL;
				}
			if(pB!=buf){
				*pB++ = ' ';
				}
			strcpy(pB,pD);
			pB = pB + strlen(pB);
			}
		*pB = 0;
#ifdef isPy3
		retVal = PyUnicode_FromString(buf);
#else
		retVal = PyBytes_FromString(buf);
#endif
		free(buf);
		return retVal;
		}
	else {
		PyErr_Clear();
		PyArg_ParseTuple(args, "O:_fp_str", &retVal);
		return NULL;
		}
}

static PyObject *_escapePDF(unsigned char* text, int textlen)
{
	unsigned char*	out = PyMem_Malloc((textlen<<2)+1);
	int				j=0, i=0;
	char			buf[4];
	PyObject*		ret;

	while(i<textlen){
		unsigned char c = text[i++];
		if(c<32 || c>=127){
			sprintf(buf,"%03o",c);
			out[j++] = '\\';
			out[j++] = buf[0];
			out[j++] = buf[1];
			out[j++] = buf[2];
			}
		else {
			if(c=='\\' || c=='(' || c==')') out[j++] = '\\';
			out[j++] = c;
			}
		}
#ifdef isPy3
	ret = PyUnicode_FromStringAndSize((const char *)out,j);
#else
	ret = PyBytes_FromStringAndSize((const char *)out,j);
#endif
	PyMem_Free(out);
	return ret;
}

static PyObject *escapePDF(PyObject *module, PyObject* args)
{
	unsigned char	*text;
	int				textLen;

	if (!PyArg_ParseTuple(args, "s#:escapePDF", &text, &textLen)) return NULL;
	return _escapePDF(text,textLen);
}

static PyObject *sameFrag(PyObject *module, PyObject* args)
{
	PyObject *f, *g;
	static char *names[] = {"fontName", "fontSize", "textColor", "rise", "underline", "strike", "link", "backColor", NULL};
	int	r=0, t;
	char **p;
	if (!PyArg_ParseTuple(args, "OO:sameFrag", &f, &g)) return NULL;
	if(PyObject_HasAttrString(f,"cbDefn")||PyObject_HasAttrString(g,"cbDefn")
		|| PyObject_HasAttrString(f,"lineBreak")||PyObject_HasAttrString(g,"lineBreak")) goto L0;
	for(p=names;*p;p++){
		PyObject *fa, *ga;
		fa = PyObject_GetAttrString(f,*p);
		ga = PyObject_GetAttrString(g,*p);
		if(fa && ga){
#ifdef	isPy3
			t = PyObject_RichCompareBool(fa,ga,Py_NE);
#else
			t = PyObject_Compare(fa,ga);
#endif
			Py_DECREF(fa);
			Py_DECREF(ga);
			if(PyErr_Occurred()) goto L1;
			}
		else{
			t = fa==ga ? 0 : 1;
			Py_XDECREF(fa);
			Py_XDECREF(ga);
			PyErr_Clear();
			}
		if(t) goto L0;
		}
	r = 1;
L0:	return PyBool_FromLong((long)r);
L1:	return NULL;
}

static PyObject *ttfonts_calcChecksum(PyObject *module, PyObject* args)
{
	unsigned char	*data;
	int				dataLen;
	unsigned long	Sum = 0L;
	unsigned char	*EndPtr;
	unsigned long n;
	int leftover;


	if (!PyArg_ParseTuple(args, "s#:calcChecksum", &data, &dataLen)) return NULL;
	EndPtr = data + (dataLen & ~3);

	/*full ULONGs*/
	while(data < EndPtr){
		n = ((*data++) << 24);
		n += ((*data++) << 16);
		n += ((*data++) << 8);
		n += ((*data++));
		Sum += n;
		}

	/*pad with zeros*/
	leftover = dataLen & 3;
	if(leftover){
		n = ((*data++) << 24);
		if (leftover>1) n += ((*data++) << 16);
		if (leftover>2) n += ((*data++) << 8);
		Sum += n;
		}

	return PyLong_FromUnsignedLong(Sum&0xFFFFFFFFU);
}

static PyObject *ttfonts_add32(PyObject *module, PyObject* args)
{
	unsigned long x, y;
	if(!PyArg_ParseTuple(args, "kk:add32", &x, &y)) return NULL;
	return PyLong_FromUnsignedLong((x+y)&0xFFFFFFFFU);
}

static PyObject *hex32(PyObject *module, PyObject* args)
{
	unsigned long x;
	char	buf[20];
	if(!PyArg_ParseTuple(args, "k:hex32", &x)) return NULL;
	sprintf(buf,"0X%8.8lX",x);
	return PyUnicode_FromString(buf);
}

static PyObject *_GetExcValue(void)
{
	PyObject *type = NULL, *value = NULL, *tb = NULL, *result=NULL;
	PyErr_Fetch(&type, &value, &tb);
	PyErr_NormalizeException(&type, &value, &tb);
	if(PyErr_Occurred()) goto L_BAD;
	if(!value){
		value = Py_None;
		Py_INCREF(value);
		}
	Py_XINCREF(value);
	result = value;
L_BAD:
	Py_XDECREF(type);
	Py_XDECREF(value);
	Py_XDECREF(tb);
	return result;
}
static PyObject *_GetAttrString(PyObject *obj, char *name)
{
	PyObject *res = PyObject_GetAttrString(obj, name);
	if(!res) PyErr_SetString(PyExc_AttributeError, name);
	return res;
}

static PyObject *unicode2T1(PyObject *module, PyObject *args, PyObject *kwds)
{
	long		i, j, _i1, _i2;
	PyObject	*R, *font, *res, *utext=NULL, *fonts=NULL,
				*_o1 = NULL, *_o2 = NULL, *_o3 = NULL;
	static char *argnames[] = {"utext","fonts",NULL};
	char		*encStr;
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", argnames, &utext, &fonts)) return NULL;
	Py_INCREF(utext);
	Py_INCREF(fonts);
	R = Py_None; Py_INCREF(Py_None);
	font = Py_None; Py_INCREF(Py_None);


	_o2 = PyList_New(0); if(!_o2) ERROR_EXIT();
	Py_DECREF(R);
	R = _o2;
	_o2 = NULL;

	_o2 = PySequence_GetItem(fonts,0); if(!_o2) ERROR_EXIT();
	_o1 = PySequence_GetSlice(fonts, 1, 0x7fffffff); if(!_o1) ERROR_EXIT();
	Py_DECREF(font);
	font = _o2;
	Py_DECREF(fonts);
	fonts = _o1;
	_o1 = _o2 = NULL;

	_o2 = _GetAttrString(font, "encName"); if(!_o2) ERROR_EXIT();

	if(PyUnicode_Check(_o2)){
#ifdef	isPy3
		encStr = PyUnicode_AsUTF8(_o2);
#else
		_o1 = PyUnicode_AsUTF8String(_o2);
		if(!_o1){
			PyErr_SetString(PyExc_ValueError,"font.encName not UTF8 encoded bytes");
			ERROR_EXIT();
			}
		encStr = PyBytes_AsString(_o1);
		Py_DECREF(_o1);
		_o1 = NULL;
#endif
		}
	else if(PyBytes_Check(_o2)){
		encStr = PyBytes_AsString(_o2);
		}
	else{
		PyErr_SetString(PyExc_ValueError,"font.encName is not bytes or unicode");
		ERROR_EXIT();
		}
	if(PyErr_Occurred()) ERROR_EXIT();
	Py_DECREF(_o2);
	_o2 = NULL;
	if(strstr(encStr,"UCS-2")) encStr = "UTF16";

	while((_i1=PyObject_IsTrue(utext))>0){
		if((_o1 = PyUnicode_AsEncodedString(utext, encStr, NULL))){
			_o2 = PyTuple_New(2); if(!_o2) ERROR_EXIT();
			Py_INCREF(font);
			PyTuple_SET_ITEM(_o2, 0, font);
			PyTuple_SET_ITEM(_o2, 1, _o1);
			_o1 = NULL;
			if(PyList_Append(R, _o2)) ERROR_EXIT();
			Py_DECREF(_o2); _o2 = NULL;
			break;
			}
		else{
			Py_XDECREF(_o1); _o1 = NULL;
			if(!PyErr_ExceptionMatches(PyExc_UnicodeEncodeError)) ERROR_EXIT();
			_o1 = _GetExcValue(); if(!_o1) ERROR_EXIT();
			PyErr_Clear();
			_o2 = _GetAttrString(_o1, "args"); if(!_o2) ERROR_EXIT();
			Py_DECREF(_o1);
			_o1 = PySequence_GetSlice(_o2, 2, 4); if(!_o1) ERROR_EXIT();
			Py_DECREF(_o2);
			_o2 = PySequence_GetItem(_o1, 0); if(!_o2) ERROR_EXIT();
			i = PyLong_AsLong(_o2); if(PyErr_Occurred()) ERROR_EXIT();
			Py_DECREF(_o2);

			_o2 = PySequence_GetItem(_o1, 1); if(!_o1) ERROR_EXIT();
			j = PyLong_AsLong(_o2); if(PyErr_Occurred()) ERROR_EXIT();
			Py_DECREF(_o2);

			Py_DECREF(_o1); _o2 = _o1 = 0;

			if(i){
				_o1 = PySequence_GetSlice(utext, 0, i); if(!_o1) ERROR_EXIT();
				_o2 = PyUnicode_AsEncodedString(_o1, encStr, NULL); if(!_o2) ERROR_EXIT();
				Py_DECREF(_o1);
				_o1 = PyTuple_New(2); if(!_o1) ERROR_EXIT();
				Py_INCREF(font);
				PyTuple_SET_ITEM(_o1, 0, font);
				PyTuple_SET_ITEM(_o1, 1, _o2);
				_o2 = NULL;
				if(PyList_Append(R, _o1)) ERROR_EXIT();
				Py_DECREF(_o1); _o1 = NULL;
				}

			_i2 = PyObject_IsTrue(fonts); if(_i2<0) ERROR_EXIT();
			if(_i2){
				_o1 = PySequence_GetSlice(utext, i, j); if(!_o1) ERROR_EXIT();
				_o2 = PyTuple_New(2); if(!_o2) ERROR_EXIT();
				PyTuple_SET_ITEM(_o2, 0, _o1);
				Py_INCREF(fonts);
				PyTuple_SET_ITEM(_o2, 1, fonts);
				_o1 = unicode2T1(module,_o2,NULL); if(!_o1) ERROR_EXIT();
				Py_DECREF(_o2); _o2 = 0;
				_o3 = PyTuple_New(1); if(!_o3) ERROR_EXIT();
				PyTuple_SET_ITEM(_o3, 0, _o1);
				_o1 = _GetAttrString(R, "extend"); if(!_o1) ERROR_EXIT();
				_o2 = PyObject_CallObject(_o1, _o3); if(!_o2) ERROR_EXIT();
				Py_DECREF(_o1);
				Py_DECREF(_o3);
				Py_DECREF(_o2); _o1 = _o2 = _o3 = NULL;
				}
			else{
				_o3 = _GetAttrString(font,"_notdefChar");
				if(!_o3) ERROR_EXIT();
				_o2 = PyLong_FromLong((j - i)); if(!_o2) ERROR_EXIT();
				_o1 = PyNumber_Multiply(_o3, _o2); if(!_o1) ERROR_EXIT();
				Py_DECREF(_o2); Py_DECREF(_o3); _o2=_o3=NULL;
				_o2 = PyTuple_New(2); if(!_o2) ERROR_EXIT();
				_o3 = _GetAttrString(font,"_notdefFont"); if(!_o3) ERROR_EXIT();
				PyTuple_SET_ITEM(_o2, 0, _o3);
				PyTuple_SET_ITEM(_o2, 1, _o1);
				Py_INCREF(_o3); _o3=NULL;
				_o1 = NULL;
				if(PyList_Append(R, _o2)) ERROR_EXIT();
				Py_DECREF(_o2); _o2 = NULL;
				}

			_o1 = PySequence_GetSlice(utext, j, 0x7fffffff); if(!_o1) ERROR_EXIT();
			Py_DECREF(utext);
			utext = _o1;
			_o1 = NULL;
			}
		}
	if(_i1<0) ERROR_EXIT();

	Py_INCREF(R);
	res = R;
	goto L_OK;

L_ERR:
	ADD_TB(module,"unicode2T1");
	Py_XDECREF(_o1);
	Py_XDECREF(_o2);
	Py_XDECREF(_o3);
	res = NULL;
L_OK:
	Py_DECREF(R);
	Py_DECREF(font);
	Py_DECREF(utext);
	Py_DECREF(fonts);
	return res;
}
static PyObject *instanceStringWidthT1(PyObject *module, PyObject *args, PyObject *kwds)
{
	PyObject *L=0, *t=0, *f=0, *self, *text, *size, *res,
				*encoding = 0, *_o1 = 0, *_o2 = 0, *_o3 = 0;
	unsigned char *b;
	const char *encStr;
	int n, m, i, j, s, _i1;
	static char *argnames[]={"self","text","size","encoding",0};
	if(!PyArg_ParseTupleAndKeywords(args, kwds, "OOO|O", argnames, &self, &text, &size, &encoding)) return 0;
	Py_INCREF(text);
	if(!encoding) encStr="utf8";
	else if(PyUnicode_Check(encoding)){
#ifdef	isPy3
		encStr = PyUnicode_AsUTF8(encoding);
#else
		_o1 = PyUnicode_AsUTF8String(encoding);
		if(!_o1){
			PyErr_SetString(PyExc_ValueError,"encoding not UTF8 encoded bytes");
			ERROR_EXIT();
			}
		encStr = PyBytes_AsString(_o1);
		Py_DECREF(_o1);
		_o1 = NULL;
#endif
		}
	else if(PyBytes_Check(encoding)){
		encStr = PyBytes_AS_STRING(encoding);
		}
	else{
		PyErr_SetString(PyExc_ValueError, "invalid type for encoding");
		ERROR_EXIT();
		}
	L = NULL;
	t = NULL;
	f = NULL;

	if(!PyUnicode_Check(text)){
		if(PyBytes_Check(text)){
			_o1=PyUnicode_Decode(PyBytes_AS_STRING(text), PyBytes_GET_SIZE(text), encStr,"strict");
			if(!_o1) ERROR_EXIT();
			Py_DECREF(text);
			text = _o1;
			_o1 = NULL;
			}
		else{
			PyErr_SetString(PyExc_ValueError, "invalid type for argument text");
			ERROR_EXIT();
			}
		}

	_o3 = PyList_New(1); if(!_o3) ERROR_EXIT();
	Py_INCREF(self);
	PyList_SET_ITEM(_o3, 0, self);
	_o2 = _GetAttrString(self, "substitutionFonts"); if(!_o2) ERROR_EXIT();
	_o1 = PyNumber_Add(_o3, _o2); if(!_o1) ERROR_EXIT();
	Py_DECREF(_o3); _o3 = 0;
	Py_DECREF(_o2); _o2 = NULL;
	_o3 = PyTuple_New(2); if(!_o3) ERROR_EXIT();
	Py_INCREF(text);
	PyTuple_SET_ITEM(_o3, 0, text);
	PyTuple_SET_ITEM(_o3, 1, _o1);
	_o1 = NULL;
	_o2 = unicode2T1(module,_o3,NULL); if(!_o2) ERROR_EXIT();
	Py_DECREF(_o3); _o3 = NULL;
	L = _o2;
	_o2 = NULL;

	n = PyList_GET_SIZE(L);

	for(s=i=0;i<n;++i){
		_o1 = PyList_GetItem(L,i); if(!_o1) ERROR_EXIT();
		Py_INCREF(_o1);

		_o2 = PySequence_GetItem(_o1, 0); if(!_o2) ERROR_EXIT();
		Py_XDECREF(f);
		f = _o2;
		_o2 = NULL;

		_o2 = _GetAttrString(f, "widths"); if(!_o2) ERROR_EXIT();
		Py_DECREF(f);
		f = _o2;
		_o2 = NULL;

		_o2 = PySequence_GetItem(_o1, 1); if(!_o2) ERROR_EXIT();
		Py_XDECREF(t);
		t = _o2;
		Py_DECREF(_o1);
		_o1 = _o2 = NULL;

		m = PyBytes_Size(t);
		b = (unsigned char*)PyBytes_AS_STRING(t);

		for(j=0;j<m;++j){
			_i1 = (long)(b[j]);
			_o2 = PyList_GetItem(f,_i1); if(!_o2) {PyErr_Format(PyExc_IndexError,"widths index %d out of range",_i1);ERROR_EXIT();}
			_i1 = PyLong_AsLong(_o2);
			_o2 = NULL;	/*we borrowed this*/
			if(PyErr_Occurred()) ERROR_EXIT();
			s += _i1;
			}
		}

	_o1 = PyFloat_FromDouble((s * 0.001)); if(!_o1) ERROR_EXIT();
	res = PyNumber_Multiply(_o1, size); if(!res) ERROR_EXIT();
	Py_DECREF(_o1);
	goto L_OK;
L_ERR:
	ADD_TB(module,"instanceStringWidthT1");
	Py_XDECREF(_o1);
	Py_XDECREF(_o2);
	Py_XDECREF(_o3);
	res = NULL;
L_OK:
	Py_XDECREF(L);
	Py_XDECREF(t);
	Py_XDECREF(f);
	Py_DECREF(text);
	return res;
}
static PyObject *instanceStringWidthTTF(PyObject *module, PyObject *args, PyObject *kwds)
{
	PyObject *self, *text, *size, *res,
				*encoding = 0, *_o1=NULL, *_o2=NULL, *_o3=NULL;
	Py_UNICODE *b;
	int n, i;
	double s, _d1, dw;
	static char *argnames[]={"self","text","size","encoding",0};
	if(!PyArg_ParseTupleAndKeywords(args, kwds, "OOO|O", argnames, &self, &text, &size, &_o1)) return 0;
	Py_INCREF(text);
	if(_o1){
		encoding = _o1;
		_o1 = NULL;
		Py_INCREF(encoding);
		}
	else{
		_o1 = PyUnicode_FromString("utf8"); if(!_o1) ERROR_EXIT();
		encoding = _o1;
		_o1 = NULL;
		}

	if(!PyUnicode_Check(text)){
		i = PyObject_IsTrue(encoding); if(i<0) ERROR_EXIT();
		if(!i){
			Py_DECREF(encoding);
			encoding = PyUnicode_FromString("utf8"); if(!encoding) ERROR_EXIT();
			}
		_o1 = _GetAttrString(text, "decode"); if(!_o1) ERROR_EXIT();
		_o3 = PyTuple_New(1); if(!_o3) ERROR_EXIT();
		Py_INCREF(encoding);
		PyTuple_SET_ITEM(_o3, 0, encoding);
		_o2 = PyObject_CallObject(_o1, _o3); if(!_o2) ERROR_EXIT();
		Py_DECREF(_o1);
		Py_DECREF(_o3); _o1 = _o3 = NULL;
		Py_DECREF(text);
		text = _o2; /*no _o2=NULL as we assign there straight away*/ 
		}

	/*self.face.charWidths --> _o1, self.face.defaultWidth --> _o3*/
	_o2 = _GetAttrString(self, "face"); if(!_o2) ERROR_EXIT();
	_o1 = _GetAttrString(_o2, "charWidths"); if(!_o1) ERROR_EXIT(); if(!PyDict_Check(_o1)){PyErr_SetString(PyExc_TypeError, "TTFontFace instance charWidths is not a dict");ERROR_EXIT();}
	_o3 = _GetAttrString(_o2, "defaultWidth"); if(!_o3) ERROR_EXIT();
	Py_DECREF(_o2); _o2 = NULL;
	dw = PyFloat_AsDouble(_o3);
	if(PyErr_Occurred()) ERROR_EXIT();
	Py_DECREF(_o3);	_o3=NULL;

	n = PyUnicode_GET_SIZE(text);
	b = PyUnicode_AS_UNICODE(text);

	for(s=i=0;i<n;++i){
		_o3 = PyLong_FromLong((long)b[i]); if(!_o3) ERROR_EXIT();
		_o2 = PyDict_GetItem(_o1,_o3);
		Py_DECREF(_o3); _o3 = NULL;
		if(!_o2) _d1 = dw;
		else{
			_d1 = PyFloat_AsDouble(_o2);
			_o2=NULL;	/*no decref as we borrowed it*/
			if(PyErr_Occurred()) ERROR_EXIT();
			}
		s += _d1;
		}
	Py_DECREF(_o1);
	_o1 = PyFloat_FromDouble((s * 0.001)); if(!_o1) ERROR_EXIT();
	res = PyNumber_Multiply(_o1, size); if(!res) ERROR_EXIT();
	Py_DECREF(_o1);
	goto L_OK;
L_ERR:
	ADD_TB(module,"instanceStringWidthTTF");
	Py_XDECREF(_o1);
	Py_XDECREF(_o2);
	Py_XDECREF(_o3);
	res = NULL;
L_OK:
	Py_DECREF(text);
	Py_DECREF(encoding);
	return res;
}

#define HAVE_BOX
#ifdef HAVE_BOX
/*Box start**************/
typedef struct {
	PyObject_HEAD
	unsigned	is_box:1;
	unsigned	is_glue:1;
	unsigned	is_penalty:1;
	unsigned	is_none:1;
	double		width,stretch,shrink,penalty;
	int			flagged;
	char		character;
	} BoxObject;

static void BoxFree(BoxObject* self)
{
	PyObject_Del(self);
}

static int Box_set_int(char* name, int* pd, PyObject *value)
{
	PyObject *v = PyNumber_Long(value);
	if(!v) return -1;
	*pd = PyLong_AsLong(v);
	Py_DECREF(v);
	return 0;
}

static int Box_set_double(char* name, double* pd, PyObject *value)
{
	PyObject *v = PyNumber_Float(value);
	if(!v) return -1;
	*pd = PyFloat_AsDouble(v);
	Py_DECREF(v);
	return 0;
}

static int Box_set_character(BoxObject *self, PyObject *value)
{
	if(value==Py_None){
		self->is_none = 1;
		}
	else {
		char *v = PyBytes_AsString(value);
		if(!v) return -1;
		if(PyBytes_GET_SIZE(value)!=1){
			PyErr_Format(PyExc_AttributeError,"Bad size %d('%s') for attribute character",PyBytes_GET_SIZE(value),v);
			return -1;
			}
		self->character = v[0];
		self->is_none = 0;
		}

	return 0;
}

static int Box_setattr(BoxObject *self, char *name, PyObject* value)
{
	if(!strcmp(name,"width")) return Box_set_double(name,&self->width,value);
	else if(!strcmp(name,"character")) return Box_set_character(self,value);
	else if(!strcmp(name,"stretch")) return Box_set_double(name,&self->stretch,value);
	else if(!strcmp(name,"shrink")) return Box_set_double(name,&self->shrink,value);
	else if(!strcmp(name,"penalty")) return Box_set_double(name,&self->penalty,value);
	else if(!strcmp(name,"flagged")) return Box_set_int(name,&self->flagged,value);
	else if(
			!strcmp(name,"is_penalty") ||
			!strcmp(name,"is_box") ||
			!strcmp(name,"is_glue")
			) PyErr_Format(PyExc_AttributeError, "readonly attribute %s", name);
	else PyErr_Format(PyExc_AttributeError, "no attribute %s", name);
	return -1;
}

static double _Glue_compute_width(BoxObject *self, double r)
{
	if(self->is_glue) return self->width+r*(r<0?self->shrink:self->stretch);
	return self->width;
}

static PyObject* Glue_compute_width(BoxObject *self, PyObject *args)
{
	double r;
	if(!PyArg_ParseTuple(args, "d:compute_width", &r)) return NULL;
	return PyFloat_FromDouble(_Glue_compute_width(self,r));
}

static struct PyMethodDef Box_methods[] = {
	{"compute_width", (PyCFunction)Glue_compute_width, METH_VARARGS|METH_KEYWORDS, "compute_width(r)"},
	{NULL, NULL}		/* sentinel */
	};

static PyObject* Box_get_character(unsigned is_none, char c)
{
	if(!is_none) return PyBytes_FromStringAndSize(&c,1);
	else {
		Py_INCREF(Py_None);
		return Py_None;
		}
}

static PyObject* Box_getattr(BoxObject *self, char *name)
{
	if(!strcmp(name,"width")) return PyFloat_FromDouble(self->width);
	else if(!strcmp(name,"character")) return Box_get_character(self->is_none,self->character);
	else if(!strcmp(name,"is_box")) return PyBool_FromLong(self->is_box);
	else if(!strcmp(name,"is_glue")) return PyBool_FromLong(self->is_glue);
	else if(!strcmp(name,"is_penalty")) return PyBool_FromLong(self->is_penalty);
	else if(!strcmp(name,"stretch")) return PyFloat_FromDouble(self->stretch);
	else if(!strcmp(name,"shrink")) return PyFloat_FromDouble(self->shrink);
	else if(!strcmp(name,"penalty")) return PyFloat_FromDouble(self->penalty);
	else if(!strcmp(name,"flagged")) return PyBool_FromLong(self->flagged);
	return PyObject_GetAttrString((PyObject *)self, name);
}

static PyTypeObject BoxType = {
	PyVarObject_HEAD_INIT(NULL,0)
	"_rl_accel.Box",				/*tp_name*/
	sizeof(BoxObject),				/*tp_basicsize*/
	0,								/*tp_itemsize*/
	/* methods */
	(destructor)BoxFree,			/*tp_dealloc*/
	(printfunc)0,					/*tp_print*/
	(getattrfunc)Box_getattr,		/*tp_getattr*/
	(setattrfunc)Box_setattr,		/*tp_setattr*/
	0,								/*tp_reserved*/
	0,								/*tp_repr*/
	0,								/*tp_as_number*/
	0,								/*tp_as_sequence*/
	0,								/*tp_as_mapping*/
	0,								/*tp_hash*/
	0,								/*tp_call*/
	0,								/*tp_str*/
	0,	 							/*tp_getattro*/
	0,								/*tp_setattro*/
	0,								/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,				/*tp_flags*/
	"Box instance, see doc string for details.", /*tp_doc*/
	0,								/*tp_traverse*/
	0,								/*tp_clear*/
	0,								/*tp_richcompare*/
	0,								/*tp_weaklistoffset*/
	0,								/*tp_iter*/
	0,								/*tp_iternext*/
	Box_methods,					/*tp_methods*/
	0,								/*tp_members*/
	0,								/*tp_getset*/
	0,								/*tp_base*/
	0,								/*tp_dict*/
	0,								/*tp_descr_get*/
	0,								/*tp_descr_set*/
	0,								/*tp_dictoffset*/
	0,								/*tp_init*/
	0,								/*tp_alloc*/
	0,								/*tp_new*/
	0,								/*tp_free*/
	0,								/*tp_is_gc*/
};

static BoxObject* Box(PyObject* module, PyObject* args, PyObject* kw)
{
	BoxObject* self;
	char	*kwlist[] = {"width","character",NULL};
	PyObject	*pC=NULL;
	double		w;

	if(!PyArg_ParseTupleAndKeywords(args,kw,"d|O:Box",kwlist,&w,&pC)) return NULL;
	if(!(self = PyObject_New(BoxObject, &BoxType))) return NULL;
	self->shrink = self->stretch = self->penalty = (double)(self->is_glue = self->is_penalty = self->flagged = 0);
	self->is_box = 1;
	self->width = w;
	if(Box_set_character(self, pC ? pC : Py_None)){
		BoxFree(self);
		return NULL;
		}

	return self;
}

static BoxObject* Glue(PyObject* module, PyObject* args, PyObject* kw)
{
	BoxObject* self;
	char	*kwlist[] = {"width","stretch","shrink",NULL};
	double		width,stretch,shrink;

	if(!PyArg_ParseTupleAndKeywords(args,kw,"ddd:Glue",kwlist,&width,&stretch,&shrink)) return NULL;
	if(!(self = PyObject_New(BoxObject, &BoxType))) return NULL;
	self->penalty = (double)(self->is_box = self->is_penalty = self->flagged = 0);
	self->is_glue = self->is_none = 1;
	self->width = width;
	self->stretch = stretch;
	self->shrink = shrink;

	return self;
}

static BoxObject* Penalty(PyObject* module, PyObject* args, PyObject* kw)
{
	BoxObject* self;
	char	*kwlist[] = {"width","penalty","flagged",NULL};
	double	width,penalty;
	int		flagged = 0;

	if(!PyArg_ParseTupleAndKeywords(args,kw,"dd|i:Penalty",kwlist,&width,&penalty,&flagged)) return NULL;
	if(!(self = PyObject_New(BoxObject, &BoxType))) return NULL;
	self->shrink = self->stretch = (double)(self->is_box = self->is_glue = 0);
	self->is_penalty = self->is_none = 1;
	self->width = width;
	self->penalty = penalty;
	self->flagged = flagged;
	return self;
}
/*Box end****************/
/* BoxList -- a list subtype */
typedef struct {
	PyListObject list;
	int state;
	} BoxListobject;

static PyObject *BoxList_getstate(BoxListobject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ":getstate")) return NULL;
	return PyLong_FromLong(self->state);
}

static PyObject *BoxList_setstate(BoxListobject *self, PyObject *args)
{
	int state;

	if (!PyArg_ParseTuple(args, "i:setstate", &state))
		return NULL;
	self->state = state;
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *BoxList_specialmeth(PyObject *self, PyObject *args, PyObject *kw)
{
	PyObject *result = PyTuple_New(3);
	if(result!=NULL){
		if(self==NULL) self = Py_None;
		if(kw==NULL) kw = Py_None;
		Py_INCREF(self);
		PyTuple_SET_ITEM(result, 0, self);
		Py_INCREF(args);
		PyTuple_SET_ITEM(result, 1, args);
		Py_INCREF(kw);
		PyTuple_SET_ITEM(result, 2, kw);
		}
	return result;
}

static PyMethodDef BoxList_methods[] = {
	{"getstate", (PyCFunction)BoxList_getstate, METH_VARARGS, "getstate() -> state"},
	{"setstate", (PyCFunction)BoxList_setstate, METH_VARARGS, "setstate(state)"},
	/* These entries differ only in the flags; they are used by the tests in test.test_descr. */
	{"classmeth", (PyCFunction)BoxList_specialmeth, METH_VARARGS | METH_KEYWORDS | METH_CLASS, "classmeth(*args, **kw)"},
	{"staticmeth", (PyCFunction)BoxList_specialmeth, METH_VARARGS | METH_KEYWORDS | METH_STATIC, "staticmeth(*args, **kw)"},
	{NULL,	NULL},
	};

static PyTypeObject BoxList_type;

static int BoxList_init(BoxListobject *self, PyObject *args, PyObject *kwds)
{
	if(PyList_Type.tp_init((PyObject *)self, args, kwds)<0) return -1;
	self->state = 0;
	return 0;
}

static PyObject *BoxList_state_get(BoxListobject *self)
{
	return PyLong_FromLong(self->state);
}

static PyGetSetDef BoxList_getsets[] = {
	{"state", (getter)BoxList_state_get, NULL, PyDoc_STR("an int variable for demonstration purposes")},
	{0}
	};

static PyTypeObject BoxList_type = {
    PyVarObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type), 0)
	"_rl_accel.BoxList",
	sizeof(BoxListobject),
	0,
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	0,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	BoxList_methods,			/* tp_methods */
	0,					/* tp_members */
	BoxList_getsets,			/* tp_getset */
	DEFERRED_ADDRESS(&PyList_Type),		/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	(initproc)BoxList_init,		/* tp_init */
	0,					/* tp_alloc */
	0,					/* tp_new */
};
#endif

#ifdef	HAVE_BOX
#define _BOX__DOC__ \
	"\tBox(width,character=None) creates a Knuth character Box with the specified width.\n" \
	"\tGlue(width,stretch,shrink) creates a Knuth glue Box with the specified width, stretch and shrink.\n" \
	"\tPenalty(width,penalty,flagged=0) creates a Knuth penalty Box with the specified width and penalty.\n" \
	"\tBoxList() creates a knuth box list.\n"
#endif

PyDoc_STRVAR(__DOC__,
"_rl_accel contains various accelerated utilities\n\
\n\
\tescapePDF makes a string safe for PDF\n\
\n\
\tasciiBase85Encode does what is says\n\
\tasciiBase85Decode does what is says\n\
\n\
\tfp_str converts numeric arguments to a single blank separated string\n\
\tcalcChecksum calculate checksums for TTFs (legacy)\n\
\tadd32 32 bit unsigned addition (legacy)\n\
\thex32 32 bit unsigned to 0X8.8X string\n\
\tinstanceStringWidthT1 version2 Font instance stringWidth\n\
\tinstanceStringWidthTTF version2 TTFont instance stringWidth\n\
\tunicode2T1 version2 pdfmetrics.unicode2T1\n"
_BOX__DOC__
);

static struct PyMethodDef _methods[] = {
	{"asciiBase85Encode", _a85_encode, METH_VARARGS, "asciiBase85Encode(\".....\") return encoded " STRNAME},
	{"asciiBase85Decode", _a85_decode, METH_VARARGS, "asciiBase85Decode(\".....\") return decoded " BYTESNAME},
	{"escapePDF", escapePDF, METH_VARARGS, "escapePDF(s) return PDF safed string"},
	{"fp_str", _fp_str, METH_VARARGS, "fp_str(a0, a1,...) convert numerics to blank separated string"},
	{"sameFrag", sameFrag, 1, "sameFrag(f,g) return 1 if fragments have same style"},
	{"calcChecksum", ttfonts_calcChecksum, METH_VARARGS, "calcChecksum(string) calculate checksums for TTFs (returns long)"},
	{"add32", ttfonts_add32, METH_VARARGS, "add32(x,y)  32 bit unsigned x+y (returns long)"},
	{"hex32", hex32, METH_VARARGS, "hex32(x)  32 bit unsigned-->0X8.8X string"},
	{"unicode2T1", (PyCFunction)unicode2T1, METH_VARARGS|METH_KEYWORDS, "return a list of (font,string) pairs representing the unicode text"},
	{"instanceStringWidthT1", (PyCFunction)instanceStringWidthT1, METH_VARARGS|METH_KEYWORDS, "Font.stringWidth(self,text,fontName,fontSize,encoding='utf8') --> width"},
	{"instanceStringWidthTTF", (PyCFunction)instanceStringWidthTTF, METH_VARARGS|METH_KEYWORDS, "TTFont.stringWidth(self,text,fontName,fontSize,encoding='utf8') --> width"},
#ifdef	HAVE_BOX
	{"Box",	(PyCFunction)Box,	METH_VARARGS|METH_KEYWORDS, "Box(width,character=None) create a Knuth Box instance"},
	{"Glue", (PyCFunction)Glue,	METH_VARARGS|METH_KEYWORDS, "Glue(width,stretch,shrink) create a Knuth Glue instance"},
	{"Penalty", (PyCFunction)Penalty,	METH_VARARGS|METH_KEYWORDS, "Penalty(width,penalty,flagged=0) create a Knuth Penalty instance"},
#endif
	{NULL,		NULL}		/* sentinel */
	};

/*Initialization function for the module (*must* be called init_pdfmetrics)*/
#ifdef isPy3
static int _traverse(PyObject *m, visitproc visit, void *arg) {
	struct module_state *st = GETSTATE(m);
	Py_VISIT(st->moduleVersion);
	return 0;
	}

static int _clear(PyObject *m) {
	struct module_state *st = GETSTATE(m);
	Py_CLEAR(st->moduleVersion);
	return 0;
	}

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT,
	"_rl_accel",
	__DOC__,
	sizeof(struct module_state),
	_methods,
	NULL,
	_traverse,
	_clear,
	NULL
	};

PyMODINIT_FUNC PyInit__rl_accel(void)
#else
void init_rl_accel(void)
#endif
{
	PyObject			*module=NULL;
	struct module_state *st=NULL;
	/*Create the module and add the functions and module doc string*/
#ifdef isPy3
	module = PyModule_Create(&moduledef);
#else
	module = Py_InitModule3("_rl_accel", _methods,__DOC__);
#endif
	if(!module) goto err;
	st=GETSTATE(module);
	/*Add some symbolic constants to the module */
	st->moduleVersion = PyBytes_FromString(VERSION);
	if(!st->moduleVersion)goto err;
#ifndef isPy3
	st->module = module;
#endif
	PyModule_AddObject(module, "version", st->moduleVersion );

#ifdef	HAVE_BOX
#ifndef isPy3
	BoxType.ob_type = &PyType_Type;
#endif
	if(PyType_Ready(&BoxType)<0) goto err;
	BoxList_type.tp_base = &PyList_Type;
	if(PyType_Ready(&BoxList_type)<0) goto err;
	Py_INCREF(&BoxList_type);
	if(PyModule_AddObject(module, "BoxList", (PyObject *)&BoxList_type)<0)goto err;
#endif

#ifdef isPy3
	return module;
#else
	return;
#endif

err:/*Check for errors*/
#ifdef isPy3
	if(st){
		Py_XDECREF(st->moduleVersion);
		}
	Py_XDECREF(module);
	return NULL;
#else
	if (PyErr_Occurred()) Py_FatalError("can't initialize module _rl_accel");
#endif
}
