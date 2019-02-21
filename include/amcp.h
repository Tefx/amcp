#ifndef AMCP_C_LIBRARY_H
#define AMCP_C_LIBRARY_H

#include <stddef.h>
#include <stdint.h>


typedef int pm_type;
typedef pm_type *pm_list;

typedef struct {
//    char *name;
    int32_t idx;
    size_t pm_num;
    pm_list pm;
    pm_type ret;
} signature;

#define DATA_TYPE_VOID    0x02
#define DATA_TYPE_INTEGER 0x04
#define DATA_TYPE_REAL    0x08
#define DATA_TYPE_STRING  0x10

#define DATA_TYPE_INTEGER_REF (DATA_TYPE_INTEGER | 0x01)
#define DATA_TYPE_REAL_REF (DATA_TYPE_REAL | 0x01)
#define DATA_TYPE_STRING_REF (DATA_TYPE_STRING | 0x01)

#ifdef _MSC_VER
#   ifdef amcp_EXPORTS
#       define DLLEXPORT __declspec(dllexport)
#   else
#       define DLLEXPORT __declspec(dllimport)
#   endif
#else
#   define DLLEXPORT
#endif

typedef struct _amcp_context amcp_context;
DLLEXPORT amcp_context *amcp_ctx_new(const char *addr);
DLLEXPORT void amcp_ctx_destroy(amcp_context *ac);
DLLEXPORT void rpc_call(amcp_context *ac, signature *ps, void *ret, ...);

#endif