/* An implementation of PostScript dict data structures */

/* You must also include gt1-namecontext.h, gt1-region.h, and gt1-value.h.
   The dicts are all allocated in regions. */

/* For efficiency and type safety, this dict implementation holds
   values as defined in value.h, i.e. values suitable for a PostScript
   implementation. If you want to use this dict in other contexts,
   it would probably be best to duplicate the code. */

typedef struct _Gt1DictEntry Gt1DictEntry;

struct _Gt1DictEntry {
  Gt1NameId key;
  Gt1Value val;
};

/* the dict is sorted by key */
struct _Gt1Dict {
  int n_entries;
  int n_entries_max;
  Gt1DictEntry *entries;
};

Gt1Dict *gt1_dict_new (Gt1Region *r, int size);

Gt1Value *gt1_dict_lookup (Gt1Dict *dict, Gt1NameId key);

void gt1_dict_def (Gt1Region *r, Gt1Dict *d, Gt1NameId key, Gt1Value *val);
