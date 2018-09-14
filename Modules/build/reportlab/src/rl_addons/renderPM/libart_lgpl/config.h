/* config.h.  Generated automatically by configure.  */
/* config.h.in.  Generated automatically from configure.in by autoheader.  */

/* Define if your processor stores words with the most significant
   byte first (like Motorola and SPARC, unlike Intel and VAX).  */
#ifdef macintosh
#	define WORDS_BIGENDIAN
#else
/* #undef WORDS_BIGENDIAN */
#endif

/*allegedly this will take care of 'FAT' binaries in OS X*/
#if defined(__LITTLE_ENDIAN__)
#	undef WORDS_BIGENDIAN
#elif defined(__BIG_ENDIAN__)
#	undef WORDS_BIGENDIAN
#	define WORDS_BIGENDIAN 1
#endif

/* Name of package */
#define PACKAGE "libart_lgpl"

/* Version number of package */
#define VERSION "2.3.10"
