#ifndef __PARSET1_H__
#define __PARSET1_H__

/* Header file for parset1.

   You have to include this header additionally:

   libart_lgpl/art_bpath.h

*/

typedef char*	gt1_read_func_t(void* data, const char* filename, int* size);
typedef struct	{
				void			*data;
				gt1_read_func_t *reader;
				} gt1_encapsulated_read_func_t;
typedef struct 	_Gt1LoadedFont Gt1LoadedFont;
typedef struct 	_Gt1EncodedFont Gt1EncodedFont;
Gt1LoadedFont*	gt1_load_font (const char *filename, gt1_encapsulated_read_func_t *reader);
void			gt1_unload_font (Gt1LoadedFont *);
ArtBpath*		gt1_get_glyph_outline (Gt1EncodedFont *font, int glyphnum, double *p_wx);
#ifdef	AFM
double			gt1_get_kern_pair (Gt1LoadedFont *font, int glyph1, int glyph2);
char*			gt1_get_font_name (Gt1LoadedFont *font);
int				gt1_is_symbol_font(Gt1LoadedFont *font);
#endif
Gt1EncodedFont* gt1_create_encoded_font(char *name, char *pfbPath, char **names, int n, gt1_encapsulated_read_func_t *reader);
Gt1EncodedFont* gt1_get_encoded_font(char *name);
char*			gt1_encoded_font_name(Gt1EncodedFont* e);
void			gt1_del_cache(void);
#endif /* __PARSET1_H__ */
