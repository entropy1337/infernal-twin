/* A module for a simple "name context", i.e. lisp-style atoms */

#include "gt1-misc.h"

#include "gt1-namecontext.h"
#if defined(_WIN32) || defined(macintosh)
#	include <string.h>
#endif

/* btw, I do not know who wrote the following comment. I modified this
   file somewhat from gimp's app/procedural_db.c hash function. */

/* I have seen something like that in Perl/TK.  --MW */

static unsigned int
gt1_name_context_hash_func (const char *string)
{
  unsigned int result;
  int c;
  int i;

  /*
   * I tried a zillion different hash functions and asked many other
   * people for advice.  Many people had their own favorite functions,
   * all different, but no-one had much idea why they were good ones.
   * I chose the one below (multiply by 9 and add new character)
   * because of the following reasons:
   *
   * 1. Multiplying by 10 is perfect for keys that are decimal strings,
   *    and multiplying by 9 is just about as good.
   * 2. Times-9 is (shift-left-3) plus (old).  This means that each
   *    character's bits hang around in the low-order bits of the
   *    hash value for ever, plus they spread fairly rapidly up to
   *    the high-order bits to fill out the hash value.  This seems
   *    works well both for decimal and non-decimal strings.
   *
   * tclHash.c --
   *
   *      Implementation of in-memory hash tables for Tcl and Tcl-based
   *      applications.
   *
   * Copyright (c) 1991-1993 The Regents of the University of California.
   * Copyright (c) 1994 Sun Microsystems, Inc.
   */

  result = 0;
  for (i = 0; (c = ((const unsigned char *)string)[i]) != '\0'; i++)
    result += (result << 3) + c;

  return result;
}

static unsigned int
gt1_name_context_hash_func_size (const char *string, int size)
{
  unsigned int result;
  int i;

  result = 0;
  for (i = 0; i < size; i++)
    result += (result << 3) + ((const unsigned char *)string)[i];

  return result;
}

Gt1NameContext *
gt1_name_context_new (void)
{
  Gt1NameContext *nc;
  int i;

  nc = gt1_new (Gt1NameContext, 1);
  nc->num_entries = 0;
  nc->table_size = 16;
  nc->table = gt1_new (Gt1NameContextHashEntry, nc->table_size);
  for (i = 0; i < nc->table_size; i++)
    nc->table[i].name = NULL;

  return nc;
}

void
gt1_name_context_free (Gt1NameContext *nc)
{
  int i;

  for (i = 0; i < nc->table_size; i++)
    if (nc->table[i].name != NULL)
      gt1_free (nc->table[i].name);
  gt1_free (nc->table);
  gt1_free (nc);
}

static char *
gt1_name_context_strdup (const char *s)
{
  int len;
  char *new;

  len = strlen (s);
  new = gt1_new (char, len + 1);
  memcpy (new, s, len);
  new[len] = '\0';
  return new;
}

static gt1_boolean
gt1_name_context_streq_size (const char *s1, const char *s2, int size2)
{
  int i;

  /* could rewrite for 32 bits at a time, but I wouldn't worry */
  for (i = 0; i < size2; i++)
    if (s1[i] != s2[i])
      return gt1_false;
  return s1[i] == 0;
}

static char *
gt1_name_context_strdup_size (const char *s, int size)
{
  char *new;

  new = gt1_new (char, size + 1);
  memcpy (new, s, size);
  new[size] = '\0';
  return new;
}

/* double the size of the hash table, rehashing as needed */
static void
gt1_name_context_double (Gt1NameContext *nc)
{
  int i, j;
  int oldsize, newmask;
  Gt1NameContextHashEntry *old_table, *new_table;

  oldsize = nc->table_size;
  old_table = nc->table;
  nc->table_size = oldsize << 1;
  newmask = nc->table_size - 1;
  new_table = gt1_new (Gt1NameContextHashEntry, nc->table_size);

  for (j = 0; j < nc->table_size; j++)
    new_table[j].name = NULL;

  for (i = 0; i < oldsize; i++)
    {
      if (old_table[i].name)
	{
	  for (j = gt1_name_context_hash_func(old_table[i].name);
	       new_table[j & newmask].name;
	       j++);
	  new_table[j & newmask] = old_table[i];
	}
    }

  gt1_free (old_table);
  nc->table = new_table;
}

/* Return the unique (to this name context) Gt1NameId for the given string,
   allocating a new one if necessary. */
Gt1NameId
gt1_name_context_intern (Gt1NameContext *nc, const char *name)
{
  int i;
  int mask;

  mask = nc->table_size - 1;
  for (i = gt1_name_context_hash_func (name); nc->table[i & mask].name; i++)
    if (!strcmp (nc->table[i & mask].name, name))
      return nc->table[i & mask].Gt1NameId;

  /* not found, allocate a new one */
  if (nc->num_entries >= nc->table_size >> 1)
    {
      gt1_name_context_double (nc);
      mask = nc->table_size - 1;
      for (i = gt1_name_context_hash_func (name); nc->table[i & mask].name; i++);
    }

  i &= mask;
  nc->table[i].name = gt1_name_context_strdup (name);
  nc->table[i].Gt1NameId = nc->num_entries;

  return nc->num_entries++;
}
/* Return the unique (to this name context) Gt1NameId for the given string,
   return GT1_UNKNOWN if not found*/
Gt1NameId gt1_name_context_interned (Gt1NameContext *nc, const char *name)
{
  int i;
  int mask;

  mask = nc->table_size - 1;
  for (i = gt1_name_context_hash_func (name); nc->table[i & mask].name; i++)
    if (!strcmp (nc->table[i & mask].name, name))
      return nc->table[i & mask].Gt1NameId;

  return GT1_UNKNOWN;
}

/* Return the unique (to this name context) Gt1NameId for the given
   string, allocating a new one if necessary. The string is not
   necessarily null-terminated; the size is given explicitly. */
Gt1NameId
gt1_name_context_intern_size (Gt1NameContext *nc, const char *name, int size)
{
  int i;
  int mask;

  mask = nc->table_size - 1;
  for (i = gt1_name_context_hash_func_size (name, size);
       nc->table[i & mask].name;
       i++)
    if (gt1_name_context_streq_size (nc->table[i & mask].name, name, size))
      return nc->table[i & mask].Gt1NameId;

  /* not found, allocate a new one */
  if (nc->num_entries >= nc->table_size >> 1)
    {
      gt1_name_context_double (nc);
      mask = nc->table_size - 1;
      for (i = gt1_name_context_hash_func_size (name, size);
	   nc->table[i & mask].name;
	   i++);
    }

  i &= mask;
  nc->table[i].name = gt1_name_context_strdup_size (name, size);
  nc->table[i].Gt1NameId = nc->num_entries;

  return nc->num_entries++;
}

/* This one is slow - it's intended for debugging only */
char *
gt1_name_context_string (Gt1NameContext *nc, Gt1NameId Gt1NameId)
{
  int j;

  for (j = 0; j < nc->table_size; j++)
    if (nc->table[j].name && nc->table[j].Gt1NameId == Gt1NameId)
      return nc->table[j].name;

  return NULL;
}
