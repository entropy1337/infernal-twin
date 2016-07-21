/* What allocation functions are we going to use? */

#ifndef __GT1_MISC_H__
#define __GT1_MISC_H__

#include <stdlib.h> /* for malloc, etc. */
#if defined(macintosh) || defined (__linux__) || defined(__FreeBSD_kernel__) || (__GNU__)
#	include <string.h> /* for memcpy() */
#endif

#define gt1_alloc malloc
#define gt1_free free
#define gt1_realloc realloc

/* These aren't, strictly speaking, configuration macros, but they're
   damn handy to have around, and may be worth playing with for
   debugging. */
#define gt1_new(type, n) ((type *)gt1_alloc ((n) * sizeof(type)))
#define gt1_renew(p, type, n) ((type *)gt1_realloc (p, (n) * sizeof(type)))

/* This one must be used carefully - in particular, p and max should
   be variables. They can also be pstruct->el lvalues. */
#define gt1_double(p, type, max) p = gt1_renew (p, type, max <<= 1)

typedef int gt1_boolean;
#define gt1_false 0
#define gt1_true 1

typedef unsigned char uchar;

/* define pi */
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif  /*  M_PI  */

void
gt1_die (const char *fmt, ...);

#endif /* __GT1_MISC_H__ */
