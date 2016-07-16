/* A simple region-based allocator */

#include "gt1-misc.h"
#include "gt1-region.h"
#include <string.h> /*for memcpy etc*/

#define REGION_BLOCK_SIZE 4096

typedef struct _Gt1RegionBlock Gt1RegionBlock;

struct _Gt1RegionBlock {
  Gt1RegionBlock *next;
  void *dummy; /* this helps alignment */
  /* actual memory here */
};

struct _Gt1Region {
  Gt1RegionBlock *first;
  Gt1RegionBlock *last;
  char *alloc_ptr;
  int space_left; /* number of bytes left in last block */
};

Gt1Region *
gt1_region_new (void)
{
  Gt1Region *r;
  Gt1RegionBlock *rb;

  r = gt1_new (Gt1Region, 1);
  rb = (Gt1RegionBlock *)gt1_alloc (sizeof(Gt1RegionBlock) + REGION_BLOCK_SIZE);
  rb->next = NULL;
  r->first = rb;
  r->last = rb;
  r->alloc_ptr = ((char *)rb) + sizeof(Gt1RegionBlock);
  r->space_left = REGION_BLOCK_SIZE;

  return r;
}

void *
gt1_region_alloc (Gt1Region *r, int size)
{
  Gt1RegionBlock *rb;
  int pad_size;

  pad_size = (size + 7) & ~7;

  if (pad_size >= REGION_BLOCK_SIZE)
    {
      /* concatentate to front of list and leave last block alone */
      rb = (Gt1RegionBlock *)gt1_alloc (sizeof(Gt1RegionBlock) + size);
      rb->next = r->first;
      r->first = rb;
      return (void*)(((char *)rb) + sizeof(Gt1RegionBlock));
    }
  else if (pad_size > r->space_left)
    {
      /* allocate a new block */
      rb = (Gt1RegionBlock *)gt1_alloc (sizeof(Gt1RegionBlock) + REGION_BLOCK_SIZE);
      rb->next = NULL;
      r->last->next = rb;
      r->last = rb;
      r->alloc_ptr = ((char *)rb) + sizeof(Gt1RegionBlock) + pad_size;
      r->space_left = REGION_BLOCK_SIZE - pad_size;
      return (void*)(((char *)rb) + sizeof(Gt1RegionBlock));
    }
  else
    {
      /* allocate in last block */
      char *p;

      p = r->alloc_ptr;
      r->alloc_ptr += pad_size;
      r->space_left -= pad_size;
      return (void *)p;
    }
}

void *
gt1_region_realloc (Gt1Region *r, void *p, int old_size, int size)
{
  char *new;

  if (old_size >= size)
    return p;

  new = gt1_region_alloc (r, size);
  memcpy (new, p, old_size);
  return new;
}

void
gt1_region_free (Gt1Region *r)
{
  Gt1RegionBlock *rb, *next;

  for (rb = r->first; rb != NULL; rb = next)
    {
      next = rb->next;
      gt1_free (rb);
    }
  gt1_free (r);
}
