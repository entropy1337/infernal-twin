/* An implementation of PostScript dict data structures.

   We use binary trees, because they're so much fun!
   */

#include "gt1-misc.h"
#include "gt1-region.h"
#include "gt1-namecontext.h"
#include "gt1-value.h"
#include "gt1-dict.h"

Gt1Dict *
gt1_dict_new (Gt1Region *r, int size)
{
  Gt1Dict *dict;

  if (size < 1) size = 1;

  dict = (Gt1Dict *)gt1_region_alloc (r, sizeof(Gt1Dict));
  dict->n_entries = 0;
  dict->n_entries_max = size;
  dict->entries = (Gt1DictEntry *)gt1_region_alloc (r, sizeof (Gt1DictEntry) *
						    size);
  return dict;
}

Gt1Value *
gt1_dict_lookup (Gt1Dict *dict, Gt1NameId key)
{
  int l, r;
  int mid;
  Gt1DictEntry *entries = dict->entries;

  l = 0;
  r = dict->n_entries;
  while (l < r)
    {
      mid = (l + r - 1) >> 1;
      if (entries[mid].key == key)
	return &entries[mid].val;
      else if (entries[mid].key > key)
	r = mid;
      else
	l = mid + 1;
    }
  return NULL;
  
}

void
gt1_dict_def (Gt1Region *r, Gt1Dict *d, Gt1NameId key, Gt1Value *val)
{
  int i;

  int l_ix, r_ix;
  int mid;
  Gt1DictEntry *entries = d->entries;

  l_ix = 0;
  r_ix = d->n_entries;
  while (l_ix < r_ix)
    {
      mid = (l_ix + r_ix - 1) >> 1;
      if (entries[mid].key == key)
	{
	  entries[mid].val = *val;
	  return;
	}
      else if (entries[mid].key > key)
	r_ix = mid;
      else
	l_ix = mid + 1;
    }

  if (d->n_entries == d->n_entries_max)
    {
      int old_size;

      old_size = d->n_entries_max * sizeof(Gt1DictEntry);
      d->n_entries_max <<= 1;
      entries = (Gt1DictEntry *)gt1_region_realloc (r,
						    entries,
						    old_size,
						    d->n_entries_max - 1 *
						    sizeof(Gt1DictEntry));
      d->entries = entries;
    }

  /* ok, now insert at point l_ix */
  for (i = d->n_entries - 1; i >= l_ix; i--)
    entries[i + 1] = entries[i];

  entries[l_ix].key = key;
  entries[l_ix].val = *val;
  d->n_entries++;
}
