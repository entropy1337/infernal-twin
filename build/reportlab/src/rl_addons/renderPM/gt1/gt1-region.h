/* A simple region-based allocator */

typedef struct _Gt1Region Gt1Region;

Gt1Region *gt1_region_new (void);
void *gt1_region_alloc (Gt1Region *r, int size);
void *gt1_region_realloc (Gt1Region *r, void *p, int old_size, int size);
void gt1_region_free (Gt1Region *r);
