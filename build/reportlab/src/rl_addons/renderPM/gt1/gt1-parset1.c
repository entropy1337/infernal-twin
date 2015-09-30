#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

#if defined(macintosh)
#	include <extras.h>
#	define strdup _strdup
#endif

#include "libart_lgpl/art_bpath.h"


#include "gt1-misc.h"
#include "gt1-region.h"
#include "gt1-namecontext.h"
#include "gt1-value.h"
#include "gt1-dict.h"

#include "gt1-parset1.h"
#ifdef	AFM
#	include "parseAFM.h"
#endif


/* a big-assed module to parse Adobe Type 1 fonts into meaningful
	 info */

#define noVERBOSE

static int
read_int32_lsb (const char *p)
{
	const unsigned char *q = (unsigned char *)p;

	return q[0] + (q[1] << 8) + (q[2] << 16) + (q[3] << 24);
}

/* this is a pfb to pfa converter

 Reference: Adobe technical note 5040, "Supporting Downloadable PostScript
 Language Fonts", page 9 */
static char *
pfb_to_flat (const char *input, int input_size)
{
	const unsigned char *in = (unsigned char *)input;
	char *flat;
	int flat_size, flat_size_max;
	int in_idx;
	int length;
	int i;
	const char hextab[16] = "0123456789abcdef";

	flat_size = 0;
	flat_size_max = 32768;
	flat = gt1_new (char, flat_size_max);

	for (in_idx = 0; in_idx < input_size;)
		{
			if (in[in_idx] != 128)
	{
		gt1_free (flat);
		return NULL;
	}
			switch (in[in_idx + 1])
	{
	case 1:
		length = read_int32_lsb (input + in_idx + 2);
		if (flat_size + length > flat_size_max)
			{
				do
		flat_size_max <<= 1;
				while (flat_size + length > flat_size_max);
				flat = gt1_renew (flat, char, flat_size_max);
			}
		in_idx += 6;
		memcpy (flat + flat_size, in + in_idx, length);
		flat_size += length;
		in_idx += length;
		break;
	case 2:
		length = read_int32_lsb (input + in_idx + 2);
		if (flat_size + length * 3 > flat_size_max)
			{
				do
		flat_size_max <<= 1;
				while (flat_size + length * 3 > flat_size_max);
				flat = gt1_renew (flat, char, flat_size_max);
			}
		in_idx += 6;
		for (i = 0; i < length; i++)
			{
				flat[flat_size++] = hextab[in[in_idx] >> 4];
				flat[flat_size++] = hextab[in[in_idx] & 15];
				in_idx++;
				if ((i & 31) == 31 || i == length - 1)
		flat[flat_size++] = '\n';
			}
		break;
	case 3:
		/* zero terminate the returned string */
		if (flat_size == flat_size_max)
			gt1_double (flat, char, flat_size_max);
		flat[flat_size] = 0;
		return flat;
	default:
			gt1_free (flat);
			return NULL;
	}
		}
	return flat;
}

struct _Gt1TokenContext {
	char *source;
	int index;
	int pos;
};

typedef enum {
	TOK_NUM,
	TOK_STR,
	TOK_NAME, /* initial / */
	TOK_IDENT,
	TOK_OPENBRACE,
	TOK_CLOSEBRACE,
	TOK_END
} TokenType;

/* we're phasing this out in favor of value.h's Gt1String */
typedef struct _MyGt1String MyGt1String;

struct _MyGt1String {
	char *start;
	char *fin;
};

static void
tokenize_free (Gt1TokenContext *tc)
{
	gt1_free (tc->source);
	gt1_free (tc);
}


static Gt1TokenContext *
tokenize_new (const char *input)
{
	Gt1TokenContext *tc;
	int length;

	tc = gt1_new (Gt1TokenContext, 1);
	length = strlen (input);
	tc->source = gt1_new (char, length + 1);
	memcpy (tc->source, input, length + 1);
	tc->index = 0;
	tc->pos = 0;

	return tc;
}

static Gt1TokenContext *
tokenize_new_from_mystring (MyGt1String *input)
{
	Gt1TokenContext *tc;
	int length;

	tc = gt1_new (Gt1TokenContext, 1);
	length = input->fin - input->start;
	tc->source = gt1_new (char, length + 1);
	memcpy (tc->source, input->start, length + 1);
	tc->index = 0;
	tc->pos = 0;

	return tc;
}

/* this returns a TokenType, and sets result to the token contents.

	 Note: this strips delimiters, like the initial /, and the enclosing ().
*/
static TokenType
tokenize_get (Gt1TokenContext *tc, MyGt1String *result)
{
	unsigned char *s = (unsigned char *)tc->source;
	int index = tc->index;
	int pos = tc->pos;
	unsigned char c;
	TokenType type;

	/* skip comments altogether (maybe later we want them, though) */
	while (c = s[index], isspace (c) || c == '%')
		{
			/* skip leading whitespace */
			while (isspace (s[index]))
	{
		if (s[index] == '\r' || s[index] == '\n')
			pos = 0;
		else
			pos++;
		index++;
	}

			if (s[index] == '%')
	{
		do
			/* skip past end-of-line */
			{
				while (c = s[index], c && c != '\r' && c != '\n')
		index++;
				if (s[index] != 0) index++;
			}
		while (s[index] == '%');
	}
		}

	/* skip leading whitespace */
	while (c = s[index], isspace (c))
		{
			if (c == '\r' || c == '\n')
	pos = 0;
			else
	pos++;
			index++;
		}


	/* ok, so now we're at the actual start of a token */
	result->start = (char*)s + index;

	c = s[index];

	if (c == 0)
		{
			result->fin = (char*)s + index;
			type = TOK_END;
		}
	/* note: GhostScript checks much more strenuously. Further, this
		 predicate does not pass the valid number -.9 */
	else if (isdigit (c) || c == '.' || (c == '-' && isdigit (s[index + 1])))
		{
			/* numeric token */
			while (c = s[index], c && !isspace (c) && c != '{' && c != '/' &&
			 c != '[' && c != ']' && c != '}')
	{
		index++;
		pos++;
	}
			result->fin = (char*)s + index;
			type = TOK_NUM;
		}
	else if (c == '/')
		{
			/* an atom, or whatever that's called */
			index++;
			result->start = (char*)s + index;
			while (c = s[index], c && !isspace (c) && c != '{' && c != '/' &&
			 c != '[' && c != ']' && c != '}' && c != '(')
	{
		index++;
		pos++;
	}
			result->fin = (char*)s + index;
			type = TOK_NAME;
		}
	else if (c == '(')
		{
			int nest;
			int backslash;

			nest = 1;
			index++;
			backslash = 0;
			result->start = (char*)s + index;
			while (c = s[index], c && nest)
	{
		if (backslash)
			backslash = 0;
		else if (c == '(')
			nest++;
		else if (c == ')')
			nest--;
		else if (c == '\\')
			backslash = 1;
		index++;
		if (c == '\r' || c == '\n')
			pos = 0;
		else
			pos++;
	}
			/* we could have a c == 0 error case here */
			result->fin = (char*)s + index - 1;
			type = TOK_STR;
		}
	else if (c == '{')
		{
			index++;
			result->fin = (char*)s + index;
			type = TOK_OPENBRACE;
		}
	else if (c == '}')
		{
			index++;
			result->fin = (char*)s + index;
			type = TOK_CLOSEBRACE;
		}
	else if (c == '[' || c == ']')
		{
			index++;
			result->fin = (char*)s + index;
			type = TOK_IDENT;
		}
	else
		{
			/* treat everything else as an identifier */
			while (c = s[index], c && !isspace (c) && c != '{' && c != '/' &&
			 c != '[' && c != ']' && c != '}' && c != '(')
	{
		index++;
		pos++;
	}
			result->fin = (char*)s + index;
			if (isspace(c))
	index++; /* skip single trailing whitespace char - this is
				useful for readstring */
			type = TOK_IDENT;
		}

	tc->index = index;
	tc->pos = pos;
	return type;
}

static int
ascii_to_hex (unsigned char c)
{
	if (c <= '9') return c - '0';
	else if (c >= 'a') return c + 10 - 'a';
	else return c + 10 - 'A';
}

/* return a hex byte, or -1 on error */

/* we don't deal with comments here */
static int
tokenize_get_hex_byte (Gt1TokenContext *tc)
{
	const unsigned char *s = (const unsigned char *)tc->source;
	int index = tc->index;
	int pos = tc->pos;
	int byte;

	/* skip leading whitespace */
	while (isspace (s[index]))
		{
			if (s[index] == '\r' || s[index] == '\n')
	pos = 0;
			else
	pos++;
			index++;
		}

	if (isxdigit (s[index]) && isxdigit (s[index + 1]))
		{
			byte = (ascii_to_hex (s[index]) << 4) | ascii_to_hex (s[index + 1]);
			index += 2;
		}
	else
		byte = -1;

	tc->index = index;
	tc->pos = pos;
	return byte;
}

/* careful, we're _not_ protected against buffer overruns here */
/* todo: fix this, it's definitely a potential security violation.
	 This almost certainly implies changing the Gt1TokenContext structure
	 to incorporate a size field, and de-emphasizing the use of
	 zero-termination */
static void
tokenize_get_raw (Gt1TokenContext *tc, char *buf, int buf_size)
{
	memcpy (buf, tc->source + tc->index, buf_size);
	tc->index += buf_size;
}

#ifdef DEBUG

static void
print_token (TokenType type, MyGt1String *lexeme)
{
	char *start, *fin;

	start = lexeme->start;
	fin = lexeme->fin;

	switch (type)
		{
		case TOK_NUM:
			printf ("number				 ");
			break;
		case TOK_IDENT:
			printf ("identifier		 ");
			break;
		case TOK_NAME:
			printf ("name					 ");
			break;
		case TOK_STR:
			printf ("string				 ");
			break;
		case TOK_OPENBRACE:
			printf ("open brace		 ");
			break;
		case TOK_CLOSEBRACE:
			printf ("close brace	 ");
			break;
		case TOK_END:
			printf ("end					 ");
			break;
		default:
			break;
		}
	while (start != fin)
		printf ("%c", *start++);
	printf ("\n");
}

static void
test_token (const char *flat)
{
	Gt1TokenContext *tc;
	TokenType type;
	MyGt1String lexeme;

	tc = tokenize_new (flat);
	while (1)
		{
			type = tokenize_get (tc, &lexeme);
			if (type == TOK_END) break;
			print_token (type, &lexeme);
		 }
}

#endif

/* basic PostScript language types */

typedef struct _Gt1ProcStep {
	TokenType tok_type;
	MyGt1String lexeme;
} Gt1ProcStep;

struct _Gt1Proc {
	int n_steps;
	/* sooner or later, we'll want to replace proc steps with
		 plain PostScript values. - probably sooner in fact, because that's
		 the best way to implement nested procedures, which currently do
		 not work. */
	Gt1Value steps[1];
};

/* low-level PostScript routines */

/* note: resulting array is _uninitialized_ ! */
static Gt1Array *
array_new (Gt1Region *r, int size)
{
	Gt1Array *array;

	array = (Gt1Array *)gt1_region_alloc (r, sizeof(Gt1Array) +
				 (size - 1) * sizeof(Gt1Value));
	array->n_values = size;
	return array;
}

struct _Gt1PSContext {
	Gt1Region *r; /* the region all PS values are allocated into */

	Gt1TokenContext *tc; /* this is for readstring, eexec, etc. */

	Gt1NameContext *nc; /* the context for all names */

	Gt1Value *value_stack;
	int n_values, n_values_max;

	/* ghostscript also has an execution stack - what's that? */

	Gt1Dict **gt1_dict_stack;
	int n_dicts, n_dicts_max;

	/* a special dict that holds all the fonts */
	Gt1Dict *fonts;

	Gt1TokenContext **file_stack; /* invariant: top of file stack == tc */
	int n_files, n_files_max;

	int quit; /* maybe this should be a string, for error messages too */
};

/* a very basic PostScript interpreter */

/* make sure that value stack has enough room for pushing n values. */
static void
ensure_stack (Gt1PSContext *psc, int n)
{
	if (psc->n_values + n == psc->n_values_max)
		{
			psc->n_values_max <<= 1;
			psc->value_stack = gt1_renew (psc->value_stack, Gt1Value, psc->n_values_max);
		}
}

static double
parse_num (MyGt1String *number)
{
	double sign;
	double mantissa;
	double decimal;
	int exp_sign;
	int exp;
	int i, length;
	const unsigned char *start;

	start = (const unsigned char *)number->start;
	length = number->fin - number->start;

	i = 0;
	sign = 1;
	if (i < length && start[i] == '-')
		{
			sign = -1;
			i++;
		}
	else if (i < length && start[i] == '+')
		i++;

	mantissa = 0;
	while (i < length && isdigit (start[i]))
		{
			mantissa = (mantissa * 10) + start[i] - '0';
			i++;
		}
	if (i < length && start[i] == '.')
		{
			i++;
			decimal = 1;
			while (i < length && isdigit (start[i]))
	{
		decimal *= 0.1;
		mantissa += (start[i] - '0') * decimal;
		i++;
	}
		}
	if (i < length && (start[i] == 'e' || start[i] == 'E'))
		{
			i++;
			exp_sign = 1;
			if (i < length && start[i] == '-')
	{
		exp_sign = -1;
		i++;
	}
			else if (i < length && start[i] == '+')
	i++;

			exp = 0;
			while (i < length && isdigit (start[i]))
	{
		exp = (exp * 10) + start[i] - '0';
		i++;
	}
			mantissa *= pow (10, exp * exp_sign);
		}
	return sign * mantissa;
}

#ifdef DEBUG

static void
print_mystring (MyGt1String *str)
{
	char *start, *fin;

	start = str->start;
	fin = str->fin;

	while (start != fin)
		printf ("%c", *start++);
}

#endif

static void
print_string (Gt1String *str)
{
	char *start;
	int size;
	int i;

	start = str->start;
	size = str->size;

	for (i = 0; i < size; i++);
		printf ("%c", start[i]);
}

static void
print_value (Gt1PSContext *psc, Gt1Value *val)
{
	switch (val->type)
		{
		case GT1_VAL_NUM:
			printf ("%g", val->val.num_val);
			break;
		case GT1_VAL_BOOL:
			printf ("%s", val->val.bool_val ? "true" : "false");
			break;
		case GT1_VAL_STR:
			printf ("\"");
			print_string (&val->val.str_val);
			printf ("\"");
			break;
		case GT1_VAL_NAME:
			printf ("/%s", gt1_name_context_string (psc->nc, val->val.name_val));
			break;
		case GT1_VAL_UNQ_NAME:
			printf ("%s", gt1_name_context_string (psc->nc, val->val.name_val));
			break;
		case GT1_VAL_DICT:
			printf ("<dictionary %d/%d>",
				val->val.dict_val->n_entries,
				val->val.dict_val->n_entries_max);
			break;
		case GT1_VAL_ARRAY:
			printf ("<array>");
			break;
		case GT1_VAL_PROC:
#if 1
			printf ("<proc>");
#else
			printf ("{ ");
			{ int i;
			for (i = 0; i < val->val.proc_val->n_values; i++)
	{
		print_value (psc, &val->val.proc_val->vals[i]);
		printf (" ");
	}
			printf ("}");
			}
#endif
			break;
		case GT1_VAL_FILE:
			printf ("<file>");
			break;
		case GT1_VAL_INTERNAL:
			printf ("<internal function>");
		case GT1_VAL_MARK:
			printf ("<mark>");
			break;
		default:
			printf ("???%d", val->type);
		}
}

#ifdef DEBUG

static void
print_token_short (TokenType type, MyGt1String *lexeme)
{
	char *start, *fin;

	start = lexeme->start;
	fin = lexeme->fin;

	switch (type)
		{
		case TOK_NUM:
			print_mystring (lexeme);
			break;
		case TOK_IDENT:
			print_mystring (lexeme);
			break;
		case TOK_NAME:
			printf ("/");
			print_mystring (lexeme);
			break;
		case TOK_STR:
			printf ("(");
			print_mystring (lexeme);
			printf (")");
			break;
		case TOK_OPENBRACE:
			printf ("{");
			break;
		case TOK_CLOSEBRACE:
			printf ("}");
			break;
		case TOK_END:
			printf ("end					 ");
			break;
		default:
			break;
		}
}

#endif

static void
print_value_deep (Gt1PSContext *psc, Gt1Value *val, int nest)
{
	int i, j;

	for (i = 0; i < nest; i++)
		printf (" ");

	switch (val->type)
		{
		case GT1_VAL_NUM:
			printf ("%g", val->val.num_val);
			break;
		case GT1_VAL_BOOL:
			printf ("%s", val->val.bool_val ? "true" : "false");
			break;
		case GT1_VAL_STR:
			printf ("\"");
			print_string (&val->val.str_val);
			printf ("\"");
			break;
		case GT1_VAL_NAME:
			printf ("/%s", gt1_name_context_string (psc->nc, val->val.name_val));
			break;
		case GT1_VAL_UNQ_NAME:
			printf ("%s", gt1_name_context_string (psc->nc, val->val.name_val));
			break;
		case GT1_VAL_DICT:
			printf ("<dictionary %d/%d> [\n",
				val->val.dict_val->n_entries,
				val->val.dict_val->n_entries_max);
			for (i = 0; i < val->val.dict_val->n_entries; i++)
	{
		for (j = 0; j < nest; j++)
			printf (" ");
		printf ("key %d\n", val->val.dict_val->entries[i].key);
		print_value_deep (psc, &val->val.dict_val->entries[i].val, nest + 1);
	}
			for (j = 0; j < nest; j++)
	printf (" ");
			printf ("]");
			break;
		case GT1_VAL_ARRAY:
			printf ("[\n");
			for (i = 0; i < val->val.array_val->n_values; i++)
	{
		print_value_deep (psc, &val->val.array_val->vals[i], nest + 1);
	}
			for (j = 0; j < nest; j++)
	printf (" ");
			printf ("]");
			break;
		case GT1_VAL_PROC:
			printf ("{\n");
			for (i = 0; i < val->val.proc_val->n_values; i++)
	{
		print_value_deep (psc, &val->val.proc_val->vals[i], nest + 1);
	}
			for (j = 0; j < nest; j++)
	printf (" ");
			printf ("}");
			break;
		case GT1_VAL_FILE:
			printf ("<file>");
			break;
		case GT1_VAL_INTERNAL:
			printf ("<internal function>");
		case GT1_VAL_MARK:
			printf ("<mark>");
			break;
		default:
			printf ("???");
		}
	printf ("\n");
}

#ifdef DEBUG

static void
print_stack (Gt1PSContext *psc)
{
	int i;

	for (i = 0; i < psc->n_values; i++)
		{
			print_value (psc, &psc->value_stack[i]);
			if (i != psc->n_values - 1)
	printf (" ");
		}
	printf ("\n");
}
#endif

static void
eval_ps_val (Gt1PSContext *psc, Gt1Value *val);

static void
eval_proc (Gt1PSContext *psc, Gt1Proc *proc)
{
	int i;

#ifdef VERBOSE
	printf ("begin proc evaluation\n");
#endif
	for (i = 0; !psc->quit && i < proc->n_values; i++)
		eval_ps_val (psc, &proc->vals[i]);
#ifdef VERBOSE
	printf ("end proc evaluation\n");
#endif
}

static Gt1Value *
gt1_dict_stack_lookup (Gt1PSContext *psc, Gt1NameId key)
{
	int i;
	Gt1Value *val;

	for (i = psc->n_dicts - 1; i >= 0; i--)
		{
			val = gt1_dict_lookup (psc->gt1_dict_stack[i], key);
			if (val != NULL)
	return val;
		}
	return NULL;
}

/* return 1 on success, with result set to the top of the value stack */
static int
get_stack_number (Gt1PSContext *psc, double *result, int index)
{
	if (psc->n_values < index)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
			return 0;
		}
	if (psc->value_stack[psc->n_values - index].type != GT1_VAL_NUM)
		{
			printf ("type error - expecting number\n");
			psc->quit = 1;
			return 0;
		}
	*result = psc->value_stack[psc->n_values - index].val.num_val;
	return 1;
}

/* return 1 on success, with result set to the top of the value stack */
static int
get_stack_dict (Gt1PSContext *psc, Gt1Dict **result, int index)
{
	if (psc->n_values < index)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
			return 0;
		}
	if (psc->value_stack[psc->n_values - index].type != GT1_VAL_DICT)
		{
			printf ("type error - expecting dict\n");
			psc->quit = 1;
			return 0;
		}
	*result = psc->value_stack[psc->n_values - index].val.dict_val;
	return 1;
}

/* return 1 on success, with result set to the top of the value stack */
static int
get_stack_name (Gt1PSContext *psc, Gt1NameId *result, int index)
{
	if (psc->n_values < index)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
			return 0;
		}
	if (psc->value_stack[psc->n_values - index].type != GT1_VAL_NAME)
		{
			printf ("type error - expecting atom\n");
			psc->quit = 1;
			return 0;
		}
	*result = psc->value_stack[psc->n_values - index].val.name_val;
	return 1;
}

/* return 1 on success, with result set to the top of the value stack */
static int
get_stack_file (Gt1PSContext *psc, Gt1TokenContext **result, int index)
{
	if (psc->n_values < index)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
			return 0;
		}
	if (psc->value_stack[psc->n_values - index].type != GT1_VAL_FILE)
		{
			printf ("type error - expecting file\n");
			psc->quit = 1;
			return 0;
		}
	*result = psc->value_stack[psc->n_values - index].val.file_val;
	return 1;
}

/* return 1 on success, with result set to the top of the value stack */
static int
get_stack_string (Gt1PSContext *psc, Gt1String *result, int index)
{
	if (psc->n_values < index)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
			return 0;
		}
	if (psc->value_stack[psc->n_values - index].type != GT1_VAL_STR)
		{
			printf ("type error - expecting string\n");
			psc->quit = 1;
			return 0;
		}
	*result = psc->value_stack[psc->n_values - index].val.str_val;
	return 1;
}

/* return 1 on success, with result set to the top of the value stack */
static int
get_stack_array (Gt1PSContext *psc, Gt1Array **result, int index)
{
	if (psc->n_values < index)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
			return 0;
		}
	if (psc->value_stack[psc->n_values - index].type != GT1_VAL_ARRAY)
		{
			printf ("type error - expecting array\n");
			psc->quit = 1;
			return 0;
		}
	*result = psc->value_stack[psc->n_values - index].val.array_val;
	return 1;
}

/* return 1 on success, with result set to the top of the value stack */
static int
get_stack_bool (Gt1PSContext *psc, int *result, int index)
{
	if (psc->n_values < index)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
			return 0;
		}
	if (psc->value_stack[psc->n_values - index].type != GT1_VAL_BOOL)
		{
			printf ("type error - expecting bool\n");
			psc->quit = 1;
			return 0;
		}
	*result = psc->value_stack[psc->n_values - index].val.bool_val;
	return 1;
}

/* return 1 on success, with result set to the top of the value stack */
static int
get_stack_proc (Gt1PSContext *psc, Gt1Proc **result, int index)
{
	if (psc->n_values < index)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
			return 0;
		}
	if (psc->value_stack[psc->n_values - index].type != GT1_VAL_PROC)
		{
			printf ("type error - expecting proc\n");
			psc->quit = 1;
			return 0;
		}
	*result = psc->value_stack[psc->n_values - index].val.proc_val;
	return 1;
}

/* here begin the internal procedures */

static void
internal_dict (Gt1PSContext *psc)
{
	Gt1Dict *dict;
	double d_size;

	if (get_stack_number (psc, &d_size, 1))
		{
			dict = gt1_dict_new (psc->r, (int)d_size);
			psc->value_stack[psc->n_values - 1].type = GT1_VAL_DICT;
			psc->value_stack[psc->n_values - 1].val.dict_val = dict;
		}
}

static void
internal_begin (Gt1PSContext *psc)
{
	Gt1Dict *dict;

	if (get_stack_dict (psc, &dict, 1))
		{
			if (psc->n_dicts == psc->n_dicts_max)
	gt1_double (psc->gt1_dict_stack, Gt1Dict *, psc->n_dicts_max);
			psc->gt1_dict_stack[psc->n_dicts++] = dict;
			psc->n_values--;
		}
}

static void
internal_end (Gt1PSContext *psc)
{
	/* note: this magic constant changes if we separate out the internal
		 dict from the user one; in fact, GhostScript uses three. */
	if (psc->n_dicts == 1)
		{
			printf ("dict stack underflow\n");
			psc->quit = 1;
		}
	psc->n_dicts--;
}

static void
internal_dup (Gt1PSContext *psc)
{
	if (psc->n_values == 0)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
		}
	else
		{
			ensure_stack (psc, 1);
			psc->value_stack[psc->n_values] =
	psc->value_stack[psc->n_values - 1];
			psc->n_values++;
		}
}

static void
internal_pop (Gt1PSContext *psc)
{
	if (psc->n_values == 0)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
		}
	else
			psc->n_values--;
}

static void
internal_exch (Gt1PSContext *psc)
{
	Gt1Value tmp;
	int stack_size;

	stack_size = psc->n_values;
	if (stack_size < 2)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
		}
	else
		{
			tmp = psc->value_stack[stack_size - 2];
			psc->value_stack[stack_size - 2] =
	psc->value_stack[stack_size - 1];
			psc->value_stack[stack_size - 1] = tmp;
		}
}

/* this doesn't do anything - we don't enforce readonly */
static void
internal_readonly (Gt1PSContext *psc)
{
	if (psc->n_values == 0)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
		}
}

/* this doesn't do anything - we don't enforce executeonly */
static void
internal_executeonly (Gt1PSContext *psc)
{
	if (psc->n_values == 0)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
		}
}

/* this doesn't do anything - we don't enforce noaccess */
static void
internal_noaccess (Gt1PSContext *psc)
{
	if (psc->n_values == 0)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
		}
}

static void
internal_def (Gt1PSContext *psc)
{
	Gt1NameId key;
	Gt1Dict *dict;

	if (get_stack_name (psc, &key, 2))
		{
			dict = psc->gt1_dict_stack[psc->n_dicts - 1];
			gt1_dict_def (psc->r, dict, key, &psc->value_stack[psc->n_values - 1]);
			psc->n_values -= 2;
		}
}

static void
internal_false (Gt1PSContext *psc)
{
	ensure_stack (psc, 1);
	psc->value_stack[psc->n_values].type = GT1_VAL_BOOL;
	psc->value_stack[psc->n_values].val.bool_val = gt1_false;
	psc->n_values++;
}

static void
internal_true (Gt1PSContext *psc)
{
	ensure_stack (psc, 1);
	psc->value_stack[psc->n_values].type = GT1_VAL_BOOL;
	psc->value_stack[psc->n_values].val.bool_val = gt1_true;
	psc->n_values++;
}

static void
internal_StandardEncoding (Gt1PSContext *psc)
{
	ensure_stack (psc, 1);
	/* todo: push actual encoding array */
	psc->value_stack[psc->n_values].type = GT1_VAL_NUM;
	psc->value_stack[psc->n_values].val.num_val = 42;
	psc->n_values++;
}

static void
internalop_openbracket (Gt1PSContext *psc)
{
	ensure_stack (psc, 1);
	psc->value_stack[psc->n_values].type = GT1_VAL_MARK;
	psc->n_values++;
}

static void
internalop_closebracket (Gt1PSContext *psc)
{
	int i;
	Gt1Array *array;
	int size, start_idx;

	for (i = psc->n_values - 1; i >= 0; i--)
		if (psc->value_stack[i].type == GT1_VAL_MARK)
			break;
	if (psc->value_stack[i].type != GT1_VAL_MARK)
		{
			printf ("unmatched mark\n");
			psc->quit = 1;
		}
	start_idx = i + 1;
	size = psc->n_values - start_idx;
	array = array_new (psc->r, size);
	for (i = 0; i < size; i++)
		array->vals[i] = psc->value_stack[start_idx + i];
	psc->n_values -= size;
	psc->value_stack[psc->n_values - 1].type = GT1_VAL_ARRAY;
	psc->value_stack[psc->n_values - 1].val.array_val = array;
}

static void
internal_currentdict (Gt1PSContext *psc)
{
	ensure_stack (psc, 1);
	psc->value_stack[psc->n_values].type = GT1_VAL_DICT;
	psc->value_stack[psc->n_values].val.dict_val =
		psc->gt1_dict_stack[psc->n_dicts - 1];
	psc->n_values++;
}

static void
internal_currentfile (Gt1PSContext *psc)
{
	/* todo: we want to move away from a tc pointer towards tags, to avoid
		 potential security holes from misusing these data structures */
	ensure_stack (psc, 1);
	psc->value_stack[psc->n_values].type = GT1_VAL_FILE;
	psc->value_stack[psc->n_values].val.file_val = psc->tc;
	psc->n_values++;
}

#define EEXEC_C1 ((unsigned short)52845)
#define EEXEC_C2 ((unsigned short)22719)

/* return number of bytes in result */
static int
decrypt_eexec (char *plaintext, const char *ciphertext, int ciphertext_size)
{
	int i;
	unsigned short r;
	unsigned char cipher;
	unsigned char plain;

	r = 55665;	/* initial key */

	for (i = 0; i < ciphertext_size; i++)
		{
			cipher = ciphertext[i];
			plain = (cipher ^ (r>>8));
			r = (cipher + r) * EEXEC_C1 + EEXEC_C2;
			if (i >= 4)
	plaintext[i - 4] = plain;
		}
	return ciphertext_size - 4;
}

/* this one is great fun! */
static void
internal_eexec (Gt1PSContext *psc)
{
	Gt1TokenContext *file_tc;
	char *ciphertext;
	int ciphertext_size, ciphertext_size_max;
	char *plaintext;
	int plaintext_size;
	int num_nulls;
	int byte;
	MyGt1String string;
	Gt1TokenContext *new_tc;

	if (get_stack_file (psc, &file_tc, 1))
		{
			psc->n_values--;

			/* first, suck the encrypted stream from the specified file */
			ciphertext_size = 0;
			ciphertext_size_max = 512;
			ciphertext = gt1_new (char, ciphertext_size_max);
			num_nulls = 0;
			while (num_nulls < 16)
	{
		if (ciphertext_size == ciphertext_size_max)
			gt1_double (ciphertext, char, ciphertext_size_max);
		byte = tokenize_get_hex_byte (file_tc);
		if (byte < 0)
			{
				printf ("eexec input appears to be truncated\n");
				psc->quit = 1;
				return;
			}
		if (byte == 0)
			num_nulls++;
		else
			num_nulls = 0;
		ciphertext[ciphertext_size++] = byte;
	}

			/* then, decrypt it */
			plaintext = gt1_new (char, ciphertext_size);
			plaintext_size = decrypt_eexec (plaintext, ciphertext, ciphertext_size);
			gt1_free (ciphertext);

#if 1 && defined(VERBOSE)
			fwrite (plaintext, 1, plaintext_size, stdout);
#endif

			/* finally, create a new Gt1TokenContext for the string, and switch
	 to executing it. */
			string.start = plaintext;
			string.fin = plaintext + plaintext_size;
			new_tc = tokenize_new_from_mystring (&string);
			gt1_free (plaintext);

			if (psc->n_files_max == psc->n_files)
	{
		printf ("overflow of file stack\n");
		psc->quit = 1;
		return;
	}
			psc->file_stack[psc->n_files++] = new_tc;
			psc->tc = new_tc;

			/* alternatively, we could have recursively called the PostScript
	 evaluation loop from here, but this seems to be just as good. */
		}
}

static void
internal_array (Gt1PSContext *psc)
{
	Gt1Array *array;
	double d_size;

	if (get_stack_number (psc, &d_size, 1))
		{
			array = array_new (psc->r, (int)d_size);
			psc->value_stack[psc->n_values - 1].type = GT1_VAL_ARRAY;
			psc->value_stack[psc->n_values - 1].val.array_val = array;
		}
}

static void
internal_string (Gt1PSContext *psc)
{
	Gt1String string;
	double d_size;
	int size;

	if (get_stack_number (psc, &d_size, 1))
		{
			size = (int)d_size;
			string.start = gt1_region_alloc (psc->r, size);
			string.size = size;
			memset (string.start, 0, size);
			psc->value_stack[psc->n_values - 1].type = GT1_VAL_STR;
			psc->value_stack[psc->n_values - 1].val.str_val = string;
		}
}

static void
internal_readstring (Gt1PSContext *psc)
{
	Gt1String string;
	Gt1TokenContext *file_tc;

	if (get_stack_string (psc, &string, 1) &&
			get_stack_file (psc, &file_tc, 2))
		{
			tokenize_get_raw (file_tc, string.start, string.size);
			psc->value_stack[psc->n_values - 2].type = GT1_VAL_STR;
			psc->value_stack[psc->n_values - 2].val.str_val = string;
			psc->value_stack[psc->n_values - 1].type = GT1_VAL_BOOL;
			psc->value_stack[psc->n_values - 1].val.bool_val = gt1_true;
		}
}

static void
internal_put (Gt1PSContext *psc)
{
	Gt1Array *array;
	double d_index;
	int index;
	Gt1Dict *dict;
	Gt1NameId key;

	if (psc->n_values >= 3 &&
			psc->value_stack[psc->n_values - 3].type == GT1_VAL_DICT &&
			get_stack_name (psc, &key, 2))
		{
			/* dict key val		put  -- */
			get_stack_dict (psc, &dict, 3);
			gt1_dict_def (psc->r, dict, key, &psc->value_stack[psc->n_values - 1]);
			psc->n_values -= 3;
		}
	else if (psc->n_values >= 3 &&
		 psc->value_stack[psc->n_values - 3].type == GT1_VAL_PROC &&
		 get_stack_number (psc, &d_index, 2))
		{
			array = psc->value_stack[psc->n_values - 3].val.proc_val;
			index = (int)d_index;
			if (index < 0 || index >= array->n_values)
	{
		printf ("range check\n");
		psc->quit = 1;
		return;
	}
			array->vals[index] = psc->value_stack[psc->n_values - 1];
			psc->n_values -= 3;
		}
	else if (psc->n_values >= 3 &&
		 get_stack_array (psc, &array, 3) &&
		 get_stack_number (psc, &d_index, 2))
		{
			/* array index val	put  -- */
			index = (int)d_index;
			if (index < 0 || index >= array->n_values)
	{
		printf ("range check\n");
		psc->quit = 1;
		return;
	}
			array->vals[index] = psc->value_stack[psc->n_values - 1];
			psc->n_values -= 3;
		}
}

static void
internal_get (Gt1PSContext *psc)
{
	Gt1Array *array;
	double d_index;
	int index;
	Gt1Dict *dict;
	Gt1NameId key;
	Gt1Value *val;

	if (psc->n_values >= 2 &&
			psc->value_stack[psc->n_values - 2].type == GT1_VAL_DICT &&
			get_stack_name (psc, &key, 1))
		{
			/* dict key		 get	val */
			get_stack_dict (psc, &dict, 2);
			val = gt1_dict_lookup (dict, key);
			if (val == NULL)
	{
		printf ("key not found\n");
		psc->quit = 1;
		return;
	}
#ifdef VERBOSE
			printf ("value: ");
			print_value (psc, val);
			printf ("\n");
#endif
			psc->n_values -= 1;
			psc->value_stack[psc->n_values - 1] = *val;
		}
	else if (psc->n_values >= 2 &&
		 psc->value_stack[psc->n_values - 2].type == GT1_VAL_PROC &&
		 get_stack_number (psc, &d_index, 1))
		{
			/* array index	get  val */
			array = psc->value_stack[psc->n_values - 2].val.proc_val;
			index = (int)d_index;
			if (index < 0 || index >= array->n_values)
	{
		printf ("range check\n");
		psc->quit = 1;
		return;
	}
			psc->n_values -= 1;
			psc->value_stack[psc->n_values - 1] = array->vals[index];
		}
	else if (get_stack_array (psc, &array, 2) &&
		 get_stack_number (psc, &d_index, 1))
		{
			/* array index	get  val */
			index = (int)d_index;
			if (index < 0 || index >= array->n_values)
	{
		printf ("range check\n");
		psc->quit = 1;
		return;
	}
			psc->n_values -= 1;
			psc->value_stack[psc->n_values - 1] = array->vals[index];
		}
}

static void
internal_index (Gt1PSContext *psc)
{
	double d_index;
	int index;

	if (get_stack_number (psc, &d_index, 1))
		{
			index = (int)d_index;
			if (index < 0 || index > psc->n_values - 2)
	{
		printf ("index range check\n");
		psc->quit = 1;
		return;
	}
			psc->value_stack[psc->n_values - 1] =
	psc->value_stack[psc->n_values - (index + 2)];
		}
}

static void
internal_definefont (Gt1PSContext *psc)
{
	Gt1NameId key;
	Gt1Dict *dict;

	if (psc->n_values < 2)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
		}
	else if (get_stack_name (psc, &key, 2))
		{
			dict = psc->fonts;
			gt1_dict_def (psc->r, dict, key, &psc->value_stack[psc->n_values - 1]);
#ifdef VERBOSE
			print_value_deep (psc, &psc->value_stack[psc->n_values - 1], 0);
#endif
			psc->n_values -= 1;
		}
}

static void
internal_mark (Gt1PSContext *psc)
{
	ensure_stack (psc, 1);
	psc->value_stack[psc->n_values].type = GT1_VAL_MARK;
	psc->n_values++;
}

static void
internal_closefile (Gt1PSContext *psc)
{
	Gt1TokenContext *tc;

	if (get_stack_file (psc, &tc, 1))
		{
			if (psc->n_files == 1)
	{
		printf ("file stack underflow\n");
		psc->quit = 1;
	}
			else if (psc->file_stack[psc->n_files - 1] == tc)
	{
		/* pop the file stack */
		tokenize_free (psc->tc);
		psc->n_files--;
		psc->tc = psc->file_stack[psc->n_files - 1];
		psc->n_values--;
	}
			else
	{
		printf ("closefile: whoa, file cowboy!\n");
		psc->quit = 1;
	}
		}
}

static void
internal_cleartomark (Gt1PSContext *psc)
{
	int i;

	for (i = psc->n_values - 1; i >= 0; i--)
		if (psc->value_stack[i].type == GT1_VAL_MARK)
			break;
	if (psc->value_stack[i].type != GT1_VAL_MARK)
		{
			printf ("cleartomark: unmatched mark\n");
			psc->quit = 1;
		}
	psc->n_values = i;
}

static void
internal_systemdict (Gt1PSContext *psc)
{
	ensure_stack (psc, 1);
	psc->value_stack[psc->n_values].type = GT1_VAL_DICT;
	psc->value_stack[psc->n_values].val.dict_val =
		psc->gt1_dict_stack[0];
	psc->n_values++;
}

static void
internal_userdict (Gt1PSContext *psc)
{
	ensure_stack (psc, 1);
	psc->value_stack[psc->n_values].type = GT1_VAL_DICT;
	psc->value_stack[psc->n_values].val.dict_val =
		psc->gt1_dict_stack[2];
	psc->n_values++;
}

static void
internal_known (Gt1PSContext *psc)
{
	Gt1NameId key;
	Gt1Dict *dict;
	int known;

	if (psc->n_values >= 2 &&
			get_stack_dict (psc, &dict, 2) &&
			get_stack_name (psc, &key, 1))
		{
			known = (gt1_dict_lookup (dict, key) != 0);
			psc->n_values -= 1;
			psc->value_stack[psc->n_values - 1].type = GT1_VAL_BOOL;
			psc->value_stack[psc->n_values - 1].val.bool_val = known;
		}
}

static void
internal_ifelse (Gt1PSContext *psc)
{
	Gt1Proc *proc1, *proc2;
	int bool;

	if (psc->n_values >= 3 &&
			get_stack_bool (psc, &bool, 3) &&
			get_stack_proc (psc, &proc1, 2) &&
			get_stack_proc (psc, &proc2, 1))
		{
			psc->n_values -= 3;
			if (bool)
	eval_proc (psc, proc1);
			else
	eval_proc (psc, proc2);
		}
}

static void
internal_if (Gt1PSContext *psc)
{
	Gt1Proc *proc;
	int bool;

	if (psc->n_values >= 2 &&
			get_stack_bool (psc, &bool, 2) &&
			get_stack_proc (psc, &proc, 1))
		{
			psc->n_values -= 2;
			if (bool)
	eval_proc (psc, proc);
		}
}

static void
internal_for (Gt1PSContext *psc)
{
	double initial, increment, limit;
	Gt1Proc *proc;
	double val;

	if (psc->n_values >= 4 &&
			get_stack_number (psc, &initial, 4) &&
			get_stack_number (psc, &increment, 3) &&
			get_stack_number (psc, &limit, 2) &&
			get_stack_proc (psc, &proc, 1))
		{
			psc->n_values -= 4;
			for (val = initial; !psc->quit &&
			 (increment > 0 ? (val <= limit) : (val >= limit));
		 val += increment)
	{
		ensure_stack (psc, 1);
		psc->value_stack[psc->n_values].type = GT1_VAL_NUM;
		psc->value_stack[psc->n_values].val.num_val = val;
		psc->n_values++;
		eval_proc (psc, proc);
	}
		}
}

static void
internal_not (Gt1PSContext *psc)
{
	int bool;

	if (psc->n_values >= 1 &&
			get_stack_bool (psc, &bool, 1))
		{
			psc->value_stack[psc->n_values - 1].val.bool_val = !bool;
		}
}

static void
internal_bind (Gt1PSContext *psc)
{
	Gt1Proc *proc;

	if (psc->n_values >= 1 &&
			get_stack_proc (psc, &proc, 1))
		{
			/* todo: implement, when procs become normal values */
		}
}

static void
internal_exec (Gt1PSContext *psc)
{
	Gt1Proc *proc;

	if (psc->n_values >= 1 &&
			get_stack_proc (psc, &proc, 1))
		{
			psc->n_values -= 1;
			eval_proc (psc, proc);
		}
}

static void
internal_count (Gt1PSContext *psc)
{
	ensure_stack (psc, 1);
	psc->value_stack[psc->n_values].type = GT1_VAL_NUM;
	psc->value_stack[psc->n_values].val.num_val = psc->n_values;
	psc->n_values++;
}

static void
internal_eq (Gt1PSContext *psc)
{
	double a, b;
	Gt1NameId na, nb;

	if (psc->n_values < 2)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
			return;
		}
	if (psc->value_stack[psc->n_values - 1].type == GT1_VAL_NAME &&
			get_stack_name (psc, &na, 2) &&
			get_stack_name (psc, &nb, 1))
		{
			psc->n_values -= 1;
			psc->value_stack[psc->n_values - 1].type = GT1_VAL_BOOL;
			psc->value_stack[psc->n_values - 1].val.bool_val = (na == nb);
		}
	else if (get_stack_number (psc, &a, 2) &&
			get_stack_number (psc, &b, 1))
		{
			psc->n_values -= 1;
			psc->value_stack[psc->n_values - 1].type = GT1_VAL_BOOL;
			psc->value_stack[psc->n_values - 1].val.bool_val = (a == b);
		}
}

static void
internal_ne (Gt1PSContext *psc)
{
	internal_eq (psc);
	if (!psc->quit)
		psc->value_stack[psc->n_values - 1].val.bool_val =
			!psc->value_stack[psc->n_values - 1].val.bool_val;
}

static void
internal_type (Gt1PSContext *psc)
{
	Gt1ValueType type;

	if (psc->n_values >= 1)
		{
			type = psc->value_stack[psc->n_values - 1].type;
			if (type == GT1_VAL_NUM)
	{
		psc->value_stack[psc->n_values - 1].type = GT1_VAL_NAME;
		psc->value_stack[psc->n_values - 1].val.name_val =
			gt1_name_context_intern (psc->nc, "integertype");
	}
			else
	{
		printf ("type not fully implemented");
	}
		}
}

static void
internal_cvx (Gt1PSContext *psc)
{
	Gt1Value *val;

	if (psc->n_values < 1)
		{
			printf ("stack underflow\n");
			psc->quit = 1;
		}
	else
		{
			val = &psc->value_stack[psc->n_values - 1];
			if (val->type == GT1_VAL_NAME)
	val->type = GT1_VAL_UNQ_NAME;
			else if (val->type == GT1_VAL_ARRAY)
	val->type = GT1_VAL_PROC;
			else
	{
		printf ("warning: cvx called on ");
		print_value (psc, val);
		printf ("\n");
	}
		}
}

static void
internal_matrix (Gt1PSContext *psc)
{
	Gt1Array *array;
	int i;

	array = array_new (psc->r, 6);
	for (i = 0; i < 6; i++)
		{
			array->vals[i].type = GT1_VAL_NUM;
			array->vals[i].val.num_val = (i == 0 || i == 3);
		}
	psc->value_stack[psc->n_values].type = GT1_VAL_ARRAY;
	psc->value_stack[psc->n_values].val.array_val = array;
	psc->n_values++;
}

static void
internal_FontDirectory (Gt1PSContext *psc)
{
	ensure_stack (psc, 1);
	psc->value_stack[psc->n_values].type = GT1_VAL_DICT;
	psc->value_stack[psc->n_values].val.dict_val = psc->fonts;
	psc->n_values++;
}

/* the table of internal procedures */

typedef struct _InternalGt1ProcListing {
	char *name;
	void (*function) (Gt1PSContext *psc);
} InternalGt1ProcListing;

InternalGt1ProcListing internal_procs[] = {
	{ "dict", internal_dict },
	{ "begin", internal_begin },
	{ "end", internal_end },
	{ "dup", internal_dup },
	{ "pop", internal_pop },
	{ "exch", internal_exch },
	{ "readonly", internal_readonly },
	{ "executeonly", internal_executeonly },
	{ "noaccess", internal_noaccess },
	{ "def", internal_def },
	{ "false", internal_false },
	{ "true", internal_true },
	{ "StandardEncoding", internal_StandardEncoding },
	{ "[", internalop_openbracket },
	{ "]", internalop_closebracket },
	{ "currentdict", internal_currentdict },
	{ "currentfile", internal_currentfile },
	{ "eexec", internal_eexec },
	{ "array", internal_array },
	{ "string", internal_string },
	{ "readstring", internal_readstring },
	{ "put", internal_put },
	{ "get", internal_get },
	{ "index", internal_index },
	{ "definefont", internal_definefont },
	{ "mark", internal_mark },
	{ "closefile", internal_closefile },
	{ "cleartomark", internal_cleartomark },
	{ "systemdict", internal_systemdict },
	{ "userdict", internal_userdict },
	{ "known", internal_known },
	{ "ifelse", internal_ifelse },
	{ "if", internal_if },
	{ "for", internal_for },
	{ "not", internal_not },
	{ "bind", internal_bind },
	{ "exec", internal_exec },
	{ "count", internal_count },
	{ "eq", internal_eq },
	{ "ne", internal_ne },
	{ "type", internal_type },
	{ "cvx", internal_cvx },
	{ "matrix", internal_matrix },
	{ "FontDirectory", internal_FontDirectory }
};

/* here end the internal procedures */

static Gt1PSContext *
pscontext_new (Gt1TokenContext *tc)
{
	Gt1PSContext *psc;
	Gt1Dict *systemdict;
	Gt1Dict *globaldict;
	Gt1Dict *userdict;
	int i;
	Gt1Value val;

	psc = gt1_new (Gt1PSContext, 1);
	psc->r = gt1_region_new ();
	psc->tc = tc;

	psc->nc = gt1_name_context_new ();

	psc->n_values = 0;
	psc->n_values_max = 16;
	psc->value_stack = gt1_new (Gt1Value, psc->n_values_max);

	psc->n_dicts_max = 16;
	psc->gt1_dict_stack = gt1_new (Gt1Dict *, psc->n_dicts_max);

	systemdict = gt1_dict_new (psc->r, sizeof(internal_procs) /
			 sizeof(InternalGt1ProcListing));
	for (i = 0; i < sizeof(internal_procs) / sizeof(InternalGt1ProcListing); i++)
		{
			val.type = GT1_VAL_INTERNAL;
			val.val.internal_val = internal_procs[i].function;
			gt1_dict_def (psc->r, systemdict,
				gt1_name_context_intern (psc->nc,
							 internal_procs[i].name),
				&val);
		}
	psc->gt1_dict_stack[0] = systemdict;
	globaldict = gt1_dict_new (psc->r, 16);
	psc->gt1_dict_stack[1] = globaldict;
	userdict = gt1_dict_new (psc->r, 16);
	psc->gt1_dict_stack[2] = userdict;
	psc->n_dicts = 3;

	psc->fonts = gt1_dict_new (psc->r, 1);

	psc->n_files_max = 16;
	psc->file_stack = gt1_new (Gt1TokenContext *, psc->n_files_max);
	psc->file_stack[0] = tc;
	psc->n_files = 1;

	psc->quit = 0;
	return psc;
}

static void
pscontext_free (Gt1PSContext *psc)
{
	/* Empty the value stack.  */
	while (psc->n_values > 0) internal_pop (psc);
	gt1_free (psc->value_stack);

	gt1_free	(psc->file_stack);
	gt1_free	(psc->gt1_dict_stack);

	gt1_name_context_free (psc->nc);
	gt1_region_free (psc->r);

	gt1_free (psc);
}



static void
eval_executable (Gt1PSContext *psc, Gt1Value *val)
{
	switch (val->type)
		{
		case GT1_VAL_INTERNAL:
			val->val.internal_val (psc);
			break;
		case GT1_VAL_PROC:
			eval_proc (psc, val->val.proc_val);
			break;
		default:
			ensure_stack (psc, 1);
			psc->value_stack[psc->n_values] = *val;
			psc->n_values++;
			break;
		}
}

/* Scan a value from the psc's token context - usually one token, or
	 a proc. Return the token type. */
static TokenType
parse_ps_token (Gt1PSContext *psc, Gt1Value *val)
{
	MyGt1String lexeme;
	TokenType type;
	Gt1Proc *proc;
	int n_proc, n_proc_max;

	type = tokenize_get (psc->tc, &lexeme);
	switch (type)
		{
		case TOK_NUM:
			val->type = GT1_VAL_NUM;
			val->val.num_val = parse_num (&lexeme);
			break;
		case TOK_NAME:
			val->type = GT1_VAL_NAME;
			val->val.name_val =
	gt1_name_context_intern_size (psc->nc, lexeme.start,
					lexeme.fin - lexeme.start);
					break;
		case TOK_STR:
			val->type = GT1_VAL_STR;
			/* todo: processing of escape characters */
			val->val.str_val.start = lexeme.start;
			val->val.str_val.size = lexeme.fin - lexeme.start;
			break;
		case TOK_IDENT:
			val->type = GT1_VAL_UNQ_NAME;
			val->val.name_val =
	gt1_name_context_intern_size (psc->nc, lexeme.start,
					lexeme.fin - lexeme.start);
			break;
		case TOK_OPENBRACE:
			n_proc = 0;
			n_proc_max = 16;
			proc = (Gt1Proc *)gt1_region_alloc (psc->r, sizeof(Gt1Proc) +
					 (n_proc_max - 1) *
					 sizeof(Gt1Value));
			while (1)
	{
		if (n_proc == n_proc_max)
			{
				int old_size;

				old_size = sizeof(Gt1Proc) + (n_proc_max - 1) * sizeof(Gt1Value);
				n_proc_max <<= 1;

				proc = (Gt1Proc *)gt1_region_realloc (psc->r, proc,
							 old_size,
							 sizeof(Gt1Proc) +
							 (n_proc_max - 1) *
							 sizeof(Gt1Value));
			}
		if (parse_ps_token (psc, &proc->vals[n_proc]) == TOK_CLOSEBRACE ||
				psc->quit)
			break;
		n_proc++;
	}
			proc->n_values = n_proc;
			val->type = GT1_VAL_PROC;
			val->val.proc_val = proc;
			break;
		case TOK_CLOSEBRACE:
		case TOK_END:
			break;
		default:
			printf ("unimplemented token type\n");
			psc->quit = 1;
			break;
		}
	return type;
}

static void
eval_ps_val (Gt1PSContext *psc, Gt1Value *val)
{
	Gt1Value *new_val;

#ifdef VERBOSE
	print_value (psc, val);
	printf ("\n");
#endif
	switch (val->type)
		{
		case GT1_VAL_NUM:
		case GT1_VAL_BOOL:
		case GT1_VAL_STR:
		case GT1_VAL_NAME:
		case GT1_VAL_ARRAY:
		case GT1_VAL_PROC:
		case GT1_VAL_DICT:
			ensure_stack (psc, 1);
			psc->value_stack[psc->n_values] = *val;
			psc->n_values++;
			break;
		case GT1_VAL_UNQ_NAME:
			new_val = gt1_dict_stack_lookup (psc, val->val.name_val);
			if (new_val != NULL)
	eval_executable (psc, new_val);
			else
	{
		printf ("undefined identifier ");
		print_value (psc, val);
		putchar ('\n');
		psc->quit = 1;
	}
			break;
		case GT1_VAL_INTERNAL:
			val->val.internal_val (psc);
			break;
		default:
			printf ("value not handled\n");
			psc->quit = 1;
			break;
		}
#ifdef VERBOSE
	if (!psc->quit)
		{
			printf ("		");
			print_stack (psc);
		}
#endif
}

/* maybe we should return the dict; easier to handle */
static Gt1PSContext *
eval_ps (Gt1TokenContext *tc)
{
	TokenType type;
	Gt1PSContext *psc;
	Gt1Value val;

	psc = pscontext_new (tc);
	do {
		type = parse_ps_token (psc, &val);
		if (type == TOK_END) break;
		if (type == TOK_CLOSEBRACE)
			{
	printf ("unexpected close brace\n");
	break;
			}
		eval_ps_val (psc, &val);
	} while (!psc->quit);

	return psc;
}

/* This routine _assumes_ that plaintext is passed in with enough
	 space to hold the decrypted text */
static void
charstring_decrypt (Gt1String *plaintext, Gt1String *ciphertext)
{
	int ciphertext_size;
	int i;
	unsigned short r;
	unsigned char cipher;
	unsigned char plain;

	ciphertext_size = ciphertext->size;
	if (plaintext->size < ciphertext_size - 4)
		{
			printf ("not enough space allocated for charstring decryption\n");
			return;
		}

	r = 4330;  /* initial key */

	for (i = 0; i < ciphertext_size; i++)
		{
			cipher = ciphertext->start[i];
			plain = (cipher ^ (r>>8));
			r = (cipher + r) * EEXEC_C1 + EEXEC_C2;
			if (i >= 4)
	plaintext->start[i - 4] = plain;
		}
	plaintext->size = ciphertext->size - 4;
}

#ifdef VERBOSE
static void
print_glyph_code (Gt1String *glyph_code)
{
	Gt1String plaintext;
	int i;
	int byte, byte1, byte2, byte3, byte4;

	plaintext.start = gt1_alloc (glyph_code->size);
	plaintext.size = glyph_code->size;
	charstring_decrypt (&plaintext, glyph_code);

	for (i = 0; i < plaintext.size; i++)
		{
			byte = ((unsigned char *)plaintext.start)[i];
			if (byte >= 32 && byte <= 246)
	printf (" %d", byte - 139);
			else if (byte >= 247 && byte <= 250)
	{
		byte1 = ((unsigned char *)plaintext.start)[++i];
		printf (" %d", ((byte - 247) << 8) + byte1 + 108);
	}
			else if (byte >= 251 && byte <= 254)
	{
		byte1 = ((unsigned char *)plaintext.start)[++i];
		printf (" %d", -((byte - 251) << 8) - byte1 - 108);
	}
			else if (byte == 255)
	{
		byte1 = ((unsigned char *)plaintext.start)[++i];
		byte2 = ((unsigned char *)plaintext.start)[++i];
		byte3 = ((unsigned char *)plaintext.start)[++i];
		byte4 = ((unsigned char *)plaintext.start)[++i];
		/* warning: this _must_ be a 32 bit int - alpha portability
			 issue! */
		printf (" %d", (byte1 << 24) + (byte2 << 16) + (byte3 << 8) + byte4);
	}
			else if (byte == 12)
	{
		byte1 = ((unsigned char *)plaintext.start)[++i];
		if (byte1 == 6)
			printf (" seac");
		else if (byte1 == 7)
			printf (" sbw");
		else if (byte1 == 0)
			printf (" dotsection");
		else if (byte1 == 2)
			printf (" hstem3");
		else if (byte1 == 1)
			printf (" vstem3");
		else if (byte1 == 12)
			printf (" div");
		else if (byte1 == 16)
			printf (" callothersubr");
		else if (byte1 == 17)
			printf (" pop");
		else if (byte1 == 33)
			printf (" setcurrentpoint");
		else
			printf (" esc%d", byte1);
	}
			else if (byte == 14)
	printf (" endchar");
			else if (byte == 13)
	printf (" hsbw");
			else if (byte == 9)
	printf (" closepath");
			else if (byte == 6)
	printf (" hlineto");
			else if (byte == 22)
	printf (" hmoveto");
			else if (byte == 31)
	printf (" hvcurveto");
			else if (byte == 5)
	printf (" rlineto");
			else if (byte == 21)
	printf (" rmoveto");
			else if (byte == 8)
	printf (" rrcurveto");
			else if (byte == 30)
	printf (" vhcurveto");
			else if (byte == 7)
	printf (" vlineto");
			else if (byte == 4)
	printf (" vmoveto");
			else if (byte == 1)
	printf (" hstem");
			else if (byte == 3)
	printf (" vstem");
			else if (byte == 10)
	printf (" callsubr");
			else if (byte == 11)
	printf (" return");
			else
	printf (" com%d", byte);
		}
	printf ("\n");
	gt1_free (plaintext.start);
}
#endif

/* Gt1Dict is the toplevel font dict. This allocates a new string for the
	 plaintext and stores it in body. */
static void
get_subr_body (Gt1PSContext *psc, Gt1String *body, Gt1Dict *fontdict, int subr)
{
	Gt1Value *private_val;
	Gt1Value *subrs_val;
	Gt1Array *subrs_array;
	Gt1String *ciphertext;

	private_val = gt1_dict_lookup (fontdict,
					 gt1_name_context_intern (psc->nc, "Private"));
	if (private_val == NULL)
		{
			printf ("No Private array\n");
			return;
		}
	subrs_val = gt1_dict_lookup (private_val->val.dict_val,
				 gt1_name_context_intern (psc->nc, "Subrs"));
	if (subrs_val == NULL)
		{
			printf ("No Subrs array\n");
			return;
		}
	subrs_array = subrs_val->val.array_val;
	/* more type & range checking */
	ciphertext = &subrs_array->vals[subr].val.str_val;
	body->start = gt1_alloc (ciphertext->size);
	body->size = ciphertext->size;
	charstring_decrypt (body, ciphertext);
}

typedef struct _BezState {
	ArtBpath *bezpath;
	int size_bezpath, size_bezpath_max;

/* this is designed to do compression of a string of moveto's in a row. */
	int need_moveto;

	double x, y; /* current point */
	double x0, y0; /* beginning of subpath */
} BezState;

static BezState *
bs_new (void)
{
	BezState *bs;

	bs = gt1_new (BezState, 1);

	bs->size_bezpath = 0;
	bs->size_bezpath_max = 16;
	bs->bezpath = gt1_new (ArtBpath, bs->size_bezpath_max);

	bs->x = 0;
	bs->y = 0;
	bs->x0 = 0;
	bs->y0 = 0;
	bs->need_moveto = 1;

	return bs;
}

static void
bs_moveto (BezState *bs, double x, double y)
{
	bs->x = x;
	bs->y = y;
	bs->need_moveto = 1;
}

static void
bs_rmoveto (BezState *bs, double dx, double dy)
{
	bs->x += dx;
	bs->y += dy;
	bs->need_moveto = 1;
}

static void
bs_do_moveto (BezState *bs)
{
	ArtBpath *bezpath;
	int size_bezpath;

	if (bs->need_moveto)
		{
			bezpath = bs->bezpath;
			size_bezpath = bs->size_bezpath;

			if (size_bezpath == bs->size_bezpath_max)
	{
		gt1_double (bezpath, ArtBpath, bs->size_bezpath_max);
		bs->bezpath = bezpath;
	}
			bezpath[size_bezpath].code = ART_MOVETO;
			bezpath[size_bezpath].x1 = 0;
			bezpath[size_bezpath].y1 = 0;
			bezpath[size_bezpath].x2 = 0;
			bezpath[size_bezpath].y2 = 0;
			bezpath[size_bezpath].x3 = bs->x;
			bezpath[size_bezpath].y3 = bs->y;
			bs->size_bezpath++;
			bs->x0 = bs->x;
			bs->y0 = bs->y;
			bs->need_moveto = 0;
		}
}

static void
bs_rlineto (BezState *bs, double dx, double dy)
{
	ArtBpath *bezpath;
	int size_bezpath;

	bs_do_moveto (bs);

	bezpath = bs->bezpath;
	size_bezpath = bs->size_bezpath;

	if (size_bezpath == bs->size_bezpath_max)
		{
			gt1_double (bezpath, ArtBpath, bs->size_bezpath_max);
			bs->bezpath = bezpath;
		}
	bezpath[size_bezpath].code = ART_LINETO;
	bezpath[size_bezpath].x1 = 0;
	bezpath[size_bezpath].y1 = 0;
	bezpath[size_bezpath].x2 = 0;
	bezpath[size_bezpath].y2 = 0;
	bs->x += dx;
	bs->y += dy;
	bezpath[size_bezpath].x3 = bs->x;
	bezpath[size_bezpath].y3 = bs->y;
	bs->size_bezpath++;
}

static void
bs_rcurveto (BezState *bs,
			 double dx1, double dy1,
			 double dx2, double dy2,
			 double dx3, double dy3)
{
	ArtBpath *bezpath;
	int size_bezpath;
	double x, y;

	bs_do_moveto (bs);

	bezpath = bs->bezpath;
	size_bezpath = bs->size_bezpath;

	if (size_bezpath == bs->size_bezpath_max)
		{
			gt1_double (bezpath, ArtBpath, bs->size_bezpath_max);
			bs->bezpath = bezpath;
		}
	bezpath[size_bezpath].code = ART_CURVETO;
	x = bs->x + dx1;
	y = bs->y + dy1;
	bezpath[size_bezpath].x1 = x;
	bezpath[size_bezpath].y1 = y;
	x += dx2;
	y += dy2;
	bezpath[size_bezpath].x2 = x;
	bezpath[size_bezpath].y2 = y;
	x += dx3;
	y += dy3;
	bezpath[size_bezpath].x3 = x;
	bezpath[size_bezpath].y3 = y;
	bs->x = x;
	bs->y = y;
	bs->size_bezpath++;
}

/* this is for callothersubr (2) */
static void
bs_curveto (BezState *bs,
			double flexbuf[6])
{
	ArtBpath *bezpath;
	int size_bezpath;

	bs->need_moveto = 0;

	bezpath = bs->bezpath;
	size_bezpath = bs->size_bezpath;

	if (size_bezpath == bs->size_bezpath_max)
		{
			gt1_double (bezpath, ArtBpath, bs->size_bezpath_max);
			bs->bezpath = bezpath;
		}
	bezpath[size_bezpath].code = ART_CURVETO;
	bezpath[size_bezpath].x1 = flexbuf[0];
	bezpath[size_bezpath].y1 = flexbuf[1];
	bezpath[size_bezpath].x2 = flexbuf[2];
	bezpath[size_bezpath].y2 = flexbuf[3];
	bezpath[size_bezpath].x3 = flexbuf[4];
	bezpath[size_bezpath].y3 = flexbuf[5];
	bs->size_bezpath++;
}

static void
bs_closepath (BezState *bs)
{
	ArtBpath *bezpath;
	int size_bezpath;

	if (bs->x0 == bs->x && bs->y0 == bs->y)
		return;

	bezpath = bs->bezpath;
	size_bezpath = bs->size_bezpath;

	if (size_bezpath == bs->size_bezpath_max)
		{
			gt1_double (bezpath, ArtBpath, bs->size_bezpath_max);
			bs->bezpath = bezpath;
		}
	bezpath[size_bezpath].code = ART_LINETO;
	bezpath[size_bezpath].x1 = 0;
	bezpath[size_bezpath].y1 = 0;
	bezpath[size_bezpath].x2 = 0;
	bezpath[size_bezpath].y2 = 0;
	bezpath[size_bezpath].x3 = bs->x0;
	bezpath[size_bezpath].y3 = bs->y0;
	bs->size_bezpath++;
}

static ArtBpath *
bs_end (BezState *bs)
{
	ArtBpath *bezpath;
	int size_bezpath;

	bezpath = bs->bezpath;
	size_bezpath = bs->size_bezpath;

	if (size_bezpath == bs->size_bezpath_max)
		gt1_double (bezpath, ArtBpath, bs->size_bezpath_max);
	bezpath[size_bezpath].code = ART_END;
	bezpath[size_bezpath].x1 = 0;
	bezpath[size_bezpath].y1 = 0;
	bezpath[size_bezpath].x2 = 0;
	bezpath[size_bezpath].y2 = 0;
	bezpath[size_bezpath].x3 = 0;
	bezpath[size_bezpath].y3 = 0;

	gt1_free (bs);

	return bezpath;
}

static ArtBpath *
convert_glyph_code_to_begt1_path (Gt1PSContext *psc, Gt1String *glyph_code,
				Gt1Dict *fontdict,
				double *p_wx)
{
	BezState *bs;

	int i;
	int byte, byte1, byte2, byte3, byte4;
	double stack[256];
	int stack_ptr;
	double ps_stack[16];
	int ps_stack_ptr;
	Gt1String exe_stack[10];
	int ret_stack[10];
	int exe_stack_ptr;
	int subr;
	int val; /* needs to be int32! */

	/* stuff for flex */
	double flexbuf[6];
	int flexptr = -1;

	exe_stack_ptr = 0;
	exe_stack[0].start = gt1_alloc (glyph_code->size);
	exe_stack[0].size = glyph_code->size;
	charstring_decrypt (&exe_stack[0], glyph_code);

	bs = bs_new ();

	ps_stack_ptr = 0;
	stack_ptr = 0;
	for (i = 0; exe_stack_ptr || i < exe_stack[exe_stack_ptr].size; i++)
		{
			if (stack_ptr >= 240)
	goto error;
			byte = ((unsigned char *)exe_stack[exe_stack_ptr].start)[i];
			if (byte >= 32 && byte <= 246)
	stack[stack_ptr++] = byte - 139;
			else if (byte >= 247 && byte <= 250)
	{
		byte1 = ((unsigned char *)exe_stack[exe_stack_ptr].start)[++i];
		stack[stack_ptr++] = ((byte - 247) << 8) + byte1 + 108;
	}
			else if (byte >= 251 && byte <= 254)
	{
		byte1 = ((unsigned char *)exe_stack[exe_stack_ptr].start)[++i];
		stack[stack_ptr++] = -((byte - 251) << 8) - byte1 - 108;
	}
			else if (byte == 255)
	{
		byte1 = ((unsigned char *)exe_stack[exe_stack_ptr].start)[++i];
		byte2 = ((unsigned char *)exe_stack[exe_stack_ptr].start)[++i];
		byte3 = ((unsigned char *)exe_stack[exe_stack_ptr].start)[++i];
		byte4 = ((unsigned char *)exe_stack[exe_stack_ptr].start)[++i];
		val = (byte1 << 24) + (byte2 << 16) + (byte3 << 8) + byte4;
		stack[stack_ptr++] = val;
	}
			else if (byte == 12)
	{
		byte1 = ((unsigned char *)exe_stack[exe_stack_ptr].start)[++i];
		if (byte1 == 6)
			printf (" seac");
		else if (byte1 == 7)
			printf (" sbw");
		else if (byte1 == 0)
			{
				/* dotsection */
			}
		else if (byte1 == 2)
			{
				/* hstem3 */
				stack_ptr -= 6;
			}
		else if (byte1 == 1)
			{
				/* vstem3 */
				stack_ptr -= 6;
			}
		else if (byte1 == 12)
			{
				/* div */
				if (stack_ptr < 2)
		goto error;
				if (stack[stack_ptr - 1] == 0)
		goto error;
				stack[stack_ptr - 2] = stack[stack_ptr - 2] / stack[stack_ptr - 1];
				stack_ptr--;
			}
		else if (byte1 == 16)
			{
				/* callothersubr */
				int j;
				int subr;
				int n_args;

				if (stack_ptr < 2)
		goto error;
				subr = (int)stack[--stack_ptr];
				n_args = (int)stack[--stack_ptr];
				if (stack_ptr < n_args)
		goto error;
				if (ps_stack_ptr + n_args > 16)
		goto error;
				for (j = 0; j < n_args; j++)
		ps_stack[ps_stack_ptr++] = stack[--stack_ptr];
#ifdef VERBOSE
				printf ("%d %d callothersubr\nPS:", n_args, subr);
				for (j = 0; j < ps_stack_ptr; j++)
		printf (" %g", ps_stack[j]);
				printf ("\nstack:");
				for (j = 0; j < stack_ptr; j++)
		printf (" %g", stack[j]);
				printf ("\n");
#endif
#undef VERBOSE
				if (subr == 3)
		{
			if (ps_stack_ptr < 1)
				goto error;
			ps_stack[ps_stack_ptr - 1] = 3;
		}
				else if (subr == 0)
		{
			if (ps_stack_ptr < 3)
				goto error;
			ps_stack_ptr--;
		}
				else if (subr == 1)
		{
			bs_do_moveto (bs);
			flexptr = -2;
		}
				else if (subr == 2)
		{
			if (flexptr >= 0)
				{
					flexbuf[flexptr] = bs->x;
					flexbuf[flexptr + 1] = bs->y;
				}
			flexptr += 2;
			if (flexptr == 6)
				{
					bs_curveto (bs, flexbuf);
					flexptr = 0;
				}
		}
			}
		else if (byte1 == 17)
			{
				/* pop */
				if (ps_stack_ptr == 0)
		goto error;
				stack[stack_ptr++] = ps_stack[--ps_stack_ptr];
			}
		else if (byte1 == 33)
			{
				/* setcurrentpoint */
#ifdef VERBOSE
				printf ("%g %g setcurrentpoint, bs is %g, %g\n",
					stack[stack_ptr - 2], stack[stack_ptr - 1],
					bs->x, bs->y);
#endif
				bs->x = stack[stack_ptr - 2];
				bs->y = stack[stack_ptr - 1];
				stack_ptr -= 2;
			}
		else
			printf (" esc%d", byte1);
	}
			else if (byte == 14)
	{
		/* endchar */
		/* nothing really to do here, except maybe some sanitychecking */
	}
			else if (byte == 13)
	{
		/* hsbw */
		bs_moveto (bs, stack[stack_ptr - 2], 0);
		if (p_wx)
			*p_wx = stack[stack_ptr - 1];
		stack_ptr -= 2;
	}
			else if (byte == 9)
	{
		/* closepath */
		bs_closepath (bs);
	}
			else if (byte == 6)
	{
		/* hlineto */
		bs_rlineto (bs, stack[--stack_ptr], 0);
	}
			else if (byte == 22)
	{
		/* hmoveto */
		bs_rmoveto (bs, stack[--stack_ptr], 0);
	}
			else if (byte == 31)
	{
		/* hvcurveto */
		bs_rcurveto (bs, stack[stack_ptr - 4], 0,
					 stack[stack_ptr - 3], stack[stack_ptr - 2],
					 0, stack[stack_ptr - 1]);
		stack_ptr -= 4;
	}
			else if (byte == 5)
	{
		/* rlineto */
		bs_rlineto (bs, stack[stack_ptr - 2], stack[stack_ptr - 1]);
		stack_ptr -= 2;
	}
			else if (byte == 21)
	{
		/* rmoveto */
		bs_rmoveto (bs, stack[stack_ptr - 2], stack[stack_ptr - 1]);
		stack_ptr -= 2;
	}
			else if (byte == 8)
	{
		/* rrcurveto */
		bs_rcurveto (bs, stack[stack_ptr - 6], stack[stack_ptr - 5],
					 stack[stack_ptr - 4], stack[stack_ptr - 3],
					 stack[stack_ptr - 2], stack[stack_ptr - 1]);
		stack_ptr -= 6;
	}
			else if (byte == 30)
	{
		/* vhcurveto */
		bs_rcurveto (bs, 0, stack[stack_ptr - 4],
					 stack[stack_ptr - 3], stack[stack_ptr - 2],
					 stack[stack_ptr - 1], 0);
		stack_ptr -= 4;
	}
			else if (byte == 7)
	{
		/* vlineto */
		bs_rlineto (bs, 0, stack[--stack_ptr]);
	}
			else if (byte == 4)
	{
		/* vmoveto */
		bs_rmoveto (bs, 0, stack[--stack_ptr]);
	}
			else if (byte == 1)
	{
		/* hstem */
		stack_ptr -= 2;
	}
			else if (byte == 3)
	{
		/* vstem */
		stack_ptr -= 2;
	}
			else if (byte == 10)
	{
		/* callsubr */
		subr = (int)stack[--stack_ptr];
#ifdef VERBOSE
		printf ("  /* call subr %d */\n", subr);
#endif
		ret_stack[exe_stack_ptr] = i;
		exe_stack_ptr++;
		if (exe_stack_ptr == 10)
			goto error;
		get_subr_body (psc, &exe_stack[exe_stack_ptr], fontdict, subr);
		i = -1;
	}
			else if (byte == 11)
	{
		/* return */
#ifdef VERBOSE
		printf ("  /* return */\n");
#endif
		/* check exe_stack_ptr */
		gt1_free (exe_stack[exe_stack_ptr].start);
		exe_stack_ptr--;
		i = ret_stack[exe_stack_ptr];
	}
			else
	printf (" com%d", byte);
		}
#ifdef VERBOSE
	printf ("\n");
#endif
	gt1_free (exe_stack[0].start);

	if (stack_ptr != 0)
		printf ("warning: stack_ptr = %d\n", stack_ptr);
	if (ps_stack_ptr != 0)
		printf ("warning: ps_stack_ptr = %d\n", ps_stack_ptr);

	return bs_end (bs);
 error:
	gt1_free (bs_end (bs));
	return NULL;
}

struct _Gt1LoadedFont {
	char*			filename;
	Gt1PSContext	*psc;
#ifdef	AFM
	Font_Info		*fi;
	MunchedFontInfo *mfi;
#endif
	Gt1Dict			*fontdict;
	Gt1NameId		id_charstrings;
	Gt1LoadedFont	*next;	/*chain of known fonts*/
	};
static	Gt1LoadedFont *_loadedFonts=NULL;

struct _Gt1EncodedFont {
	Gt1LoadedFont	*font;
	Gt1NameId		*encoding;
	size_t			n;		/*length of the encoding*/
	char			*name;	/*external font name*/
	Gt1EncodedFont	*next;	/*chain of known fonts*/
};
static	Gt1EncodedFont *_encodedFonts=NULL;

#ifdef	AFM
/* allocate a new filename, same as the old one, but with the extension */
static char * replace_extension (const char *filename, const char *ext)
{
	int i;
	int size_fn, size_ext;
	char *new_fn;

	size_fn = strlen (filename);
	size_ext = strlen (ext);
	for (i = size_fn - 1; i >= 0; i--)
		if (filename[i] == '.' || filename[i] == '/')
			break;
	if (filename[i] != '.')
		i = size_fn;
	new_fn = gt1_new (char, i + size_ext + 1);
	memcpy (new_fn, filename, i);
	memcpy (new_fn + i, ext, size_ext);
	new_fn[i + size_ext] = '\0';
	return new_fn;
}

/* some functions for dealing with defined fonts after evaluation of the font program is complete. */
typedef struct _MunchedFontInfo MunchedFontInfo;
typedef struct _KernPair KernPair;

/* The kern pair table is actually a hash table */
struct _MunchedFontInfo {
	int kern_pair_table_size;
	KernPair *kern_pair_table;
};

struct _KernPair {
	Gt1NameId name1; /* or -1 if empty */
	Gt1NameId name2;
	int xamt, yamt;
};

#define kern_pair_hash(n1,n2) ((n1) * 367 + (n2))

static MunchedFontInfo *
munch_font_info (Gt1PSContext *psc, Font_Info *fi)
{
	MunchedFontInfo *mfi;
	KernPair *table;
	int table_size;
	int i, j;
	Gt1NameId name1, name2;

	mfi = gt1_new (MunchedFontInfo, 1);

	table_size = fi->numOfPairs << 1;
	mfi->kern_pair_table_size = table_size;
	table = gt1_new (KernPair, table_size);
	mfi->kern_pair_table = table;
	for (i = 0; i < mfi->kern_pair_table_size; i++)
		table[i].name1 = -1;

	/* Transfer afm kern pair information into the hash table,
		 taking care to intern the names as we go. */
	for (i = 0; i < fi->numOfPairs; i++)
		{
			name1 = gt1_name_context_intern (psc->nc, fi->pkd[i].name1);
			name2 = gt1_name_context_intern (psc->nc, fi->pkd[i].name2);
			for (j = kern_pair_hash (name1, name2);
		 table[j % table_size].name1 != -1;
		 j++);
			j = j % table_size;
			table[j].name1 = name1;
			table[j].name2 = name2;
			table[j].xamt = fi->pkd[i].xamt;
			table[j].yamt = fi->pkd[i].yamt;
		}

	return mfi;
}

static void free_munched_font_info(MunchedFontInfo *mfi)
{
	gt1_free (mfi->kern_pair_table);
	gt1_free (mfi);
}

static	int try_read_afm(Gt1LoadedFont *font)
{
	char	*afm_filename;
	FILE	*afm_f;
	int		r, status;
	afm_filename = replace_extension(font->filename, ".afm");
	afm_f = fopen(afm_filename, "rb");

	if((r=(afm_f!= NULL))){
		status = parseFile(afm_f, &font->fi, P_GALL);
		fclose (afm_f);
		font->mfi = munch_font_info(psc, font->fi);
		}
	gt1_free (afm_filename);
}

/* get xamt of kern pair */
double gt1_get_kern_pair(Gt1LoadedFont *font, int glyph1, int glyph2)
{
	Gt1NameId name1, name2;
	int i, idx;
	KernPair *table;
	int table_size;

	if (font == NULL)
		return 0;
	name1 = font->encoding[glyph1 & 0xff];
	name2 = font->encoding[glyph2 & 0xff];
	table_size = font->mfi->kern_pair_table_size;
	table = font->mfi->kern_pair_table;
	for (i = kern_pair_hash (name1, name2); idx = i % table_size,
	 table[idx].name1 != -1;
			 i++)
		if (table[idx].name1 == name1 && table[idx].name2 == name2)
			return table[idx].xamt;
	return 0;
}

int gt1_is_symbol_font(Gt1LoadedFont *font)
{
	char* name = gt1_get_font_name(font);
	return stricmp(name,"symbol")==0 || stricmp(name,"zapfdingbats")==0;
}

char * gt1_get_font_name (Gt1LoadedFont *font)
{
	return font->fi->gfi->fontName;
}
#endif

#if defined(_WIN32)
#	define STRNICMP(a,b,n) strnicmp(a,b,n)
#endif
Gt1EncodedFont* gt1_get_encoded_font(char* name)
{
	Gt1EncodedFont	*e = _encodedFonts;
	while(e && strcmp(name,e->name)) e = e->next;
	return e;
}

char*	gt1_encoded_font_name(Gt1EncodedFont* e)
{
	return e->name;
}

static void _gt1_del_encodedFont (Gt1EncodedFont *font)
{
	gt1_free(font->encoding);
	gt1_free(font->name);
}

Gt1EncodedFont* gt1_create_encoded_font(char* name, char *pfbPath, char **names, int n, gt1_encapsulated_read_func_t *reader)
{
	int				i=0;
	Gt1EncodedFont	*e;
	Gt1LoadedFont	*f;
	Gt1NameId*		enc;
	Gt1NameId		_notdef;

	/*find the pfb info (possibly cached)*/
	f = gt1_load_font(pfbPath,reader);
	if(!f) return NULL;
	if((e = gt1_get_encoded_font(name))){
		_gt1_del_encodedFont(e);
		}
	else {
		e = gt1_new(Gt1EncodedFont, 1);
		}
	enc = gt1_new(Gt1NameId, n);
	e->encoding = enc;
	e->n = n;
	e->font = f;
	e->name = strdup(name);
	_notdef = gt1_name_context_interned(f->psc->nc, ".notdef");
	for(i=0;i<n;i++){
		Gt1NameId v = names[i] ? gt1_name_context_interned(f->psc->nc, names[i]) : _notdef;
		enc[i] = v!=GT1_UNKNOWN? v : _notdef;
		}
	e->next = _encodedFonts;
	_encodedFonts = e;
	return e;
}

Gt1LoadedFont *gt1_load_font(const char *filename, gt1_encapsulated_read_func_t *reader)
{
	Gt1LoadedFont *font;
	Gt1Dict *fontdict;

	char *pfb;
	int pfb_size;
	Gt1TokenContext *tc;
	Gt1PSContext *psc;
	char *flat;

	font = _loadedFonts;
	while(font){
		if(!strcmp(filename,font->filename)){
			return font;
			}
		font = font->next;
		}

	pfb = reader ? reader->reader(reader->data,filename,&pfb_size) : NULL;
	if(!pfb){
		int pfb_size_max, bytes_read;
		FILE *f;
		f = fopen(filename, "rb");
		if(f==NULL) return NULL;

		pfb_size = 0;
		pfb_size_max = 32768;
		pfb = gt1_new(char, pfb_size_max);
		while(1){
			bytes_read = fread(pfb + pfb_size, 1, pfb_size_max - pfb_size, f);
			if(bytes_read == 0) break;
			pfb_size += bytes_read;
			gt1_double(pfb, char, pfb_size_max);
			}
		fclose(f);
		}

	/*
	fwrite (pfb, 1, pfb_size, stdout);
	*/

	/* this is a good place to do a "magic" computation on the input file. */

	if(pfb_size)
		{
			if (((unsigned char *)pfb)[0] == 128) flat = pfb_to_flat (pfb, pfb_size);
			else {
		flat = gt1_new (char, pfb_size + 1);
		memcpy (flat, pfb, pfb_size);
		flat[pfb_size] = 0;
	}
		}
	else
		{
			flat = gt1_new (char, 1);
			*flat = 0;
		}
	gt1_free (pfb);

	/*
	printf ("%s", flat);
	*/

	/*
	test_token (flat);
	*/


	tc = tokenize_new (flat);
	gt1_free (flat);
	psc = eval_ps(tc);
	tokenize_free (tc);
	if (psc->fonts->n_entries != 1)
		{
			pscontext_free (psc);
			return NULL;
		}

	font = gt1_new (Gt1LoadedFont, 1);
	font->filename = strdup(filename);
	font->psc = psc;
	fontdict = psc->fonts->entries[0].val.val.dict_val;
	font->fontdict = fontdict;
#ifdef	AFM
	font->fi = NULL;
	font->mfi = NULL;
#endif
	font->id_charstrings = gt1_name_context_intern (psc->nc, "CharStrings");

	font->next = _loadedFonts;
	_loadedFonts = font;
	return font;
}

void gt1_unload_font (Gt1LoadedFont *font)
{
	pscontext_free (font->psc);
	gt1_free(font->filename);
#ifdef	AFM
	if (font->mfi) free_munched_font_info(font->mfi);
	if (font->fi) parseFileFree(font->fi);
#endif
	gt1_free (font);
}

void gt1_del_encodedFont (Gt1EncodedFont *font)
{
	_gt1_del_encodedFont(font);
	gt1_free(font);
}

void gt1_del_cache(void)
{
	while(_encodedFonts){
		Gt1EncodedFont *e = _encodedFonts;
		_encodedFonts = _encodedFonts->next;
		gt1_del_encodedFont(e);
		}
	while(_loadedFonts){
		Gt1LoadedFont *e = _loadedFonts;
		_loadedFonts = _loadedFonts->next;
		gt1_unload_font(e);
		}
}

ArtBpath *_get_glyph_outline(Gt1LoadedFont *font, Gt1NameId glyphname, double *p_wx)
{
	Gt1Value *charstringsval, *glyphcodeval;
	Gt1Dict *charstrings;
	Gt1String *glyphcode;


	/* charstringsval is a structure w/a union */
	charstringsval = gt1_dict_lookup (font->fontdict, font->id_charstrings);
	charstrings = charstringsval->val.dict_val;
	glyphcodeval = gt1_dict_lookup (charstrings, glyphname);
	if (glyphcodeval)
		{
			glyphcode = &glyphcodeval->val.str_val;

#ifdef VERBOSE
			/* note: there is an #undef VERBOSE above, so this is probably
	 going to be ineffective. */
			print_glyph_code (glyphcode);
#endif
			return convert_glyph_code_to_begt1_path(font->psc, glyphcode, font->fontdict, p_wx);
		}
	else {
		/*
		fprintf(stderr, "didn't get glyphcodeval, returning NULL\n");
		*/
		return NULL;
		}
}

ArtBpath *gt1_get_glyph_outline(Gt1EncodedFont *font, int glyphnum, double *p_wx)
{
	
	return (glyphnum<0 || glyphnum>(int)font->n) ?	NULL
				: _get_glyph_outline(font->font,font->encoding[glyphnum],p_wx);
}

#ifdef MAIN
int main (int argc, char **argv)
{
#if 1
	int	i;
	for(i=1;i<argc;i+=2){
		gt1_get_encoded_font(argv[i],argv[i+1]);
		}
	gt1_del_cache();
#else
	char *pfb;
	int pfb_size, pfb_size_max;
	int bytes_read;
	Gt1TokenContext *tc;
	Gt1PSContext *psc;

	char *flat;

	pfb_size = 0;
	pfb_size_max = 32768;
	pfb = gt1_new (char, pfb_size_max);
	while (1)
		{
			bytes_read = fread (pfb + pfb_size, 1, pfb_size_max - pfb_size, stdin);
			if (bytes_read == 0) break;
			pfb_size += bytes_read;
			gt1_double (pfb, char, pfb_size_max);
		}

	/*
	fwrite (pfb, 1, pfb_size, stdout);
	*/

	/* this is a good place to do a "magic" computation on the input file. */

	if (pfb_size)
		{
			if (((unsigned char *)pfb)[0] == 128)
	flat = pfb_to_flat (pfb, pfb_size);
			else
	{
		flat = gt1_new (char, pfb_size + 1);
		memcpy (flat, pfb, pfb_size);
		flat[pfb_size] = 0;
	}
		}

	/*
	*/
	printf ("%s", flat);

#if 0

	/*
	test_token (flat);
	*/

	tc = tokenize_new (flat);
	psc = eval_ps (tc);

	print_defined_fonts (psc);

	return 0;
#endif
#endif
}
#endif
