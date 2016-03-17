/* Basic value datatypes for implementing the PostScript language */

/* Note: this pulls in a lot of datatypes from the interpreter. That's
   not really clean. Oh well. */

typedef struct _Gt1Value Gt1Value;
typedef struct _Gt1Dict Gt1Dict;
typedef struct _Gt1Array Gt1Array;
typedef struct _Gt1Array Gt1Proc;
typedef struct _Gt1String Gt1String;
typedef struct _Gt1PSContext Gt1PSContext;
typedef struct _Gt1TokenContext Gt1TokenContext;

typedef enum {
  GT1_VAL_NUM,
  GT1_VAL_BOOL,
  GT1_VAL_STR,
  GT1_VAL_NAME,
  GT1_VAL_UNQ_NAME,
  GT1_VAL_DICT,
  GT1_VAL_INTERNAL,
  GT1_VAL_ARRAY,
  GT1_VAL_PROC,
  GT1_VAL_FILE,
  GT1_VAL_MARK
} Gt1ValueType;

struct _Gt1String {
  char *start;
  int size;
};

struct _Gt1Value {
  Gt1ValueType type;
  union {
    double num_val;
    int bool_val;
    Gt1String str_val;
    Gt1NameId name_val;
    Gt1NameId unq_name_val; /* unquoted name - I don't really understand this */
    void (*internal_val)(Gt1PSContext *psc);
    Gt1Dict *dict_val;
    Gt1Array *array_val;
    Gt1Proc *proc_val;
    Gt1TokenContext *file_val; /* to be replaced with a tag, hopefully */
  } val;
};

struct _Gt1Array {
  int n_values;
  Gt1Value vals[1];
};

