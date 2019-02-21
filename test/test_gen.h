#include <amcp.h>

amcp_context* _amcp_ctx_512192;

int32_t test_amcp_connect(const char* addr){
    _amcp_ctx_512192 = amcp_ctx_new(addr);
    return 0;
}

int32_t test_amcp_close(){
    amcp_ctx_destroy(_amcp_ctx_512192);
    return 0;
}

double test_add(int32_t a, double b){
    pm_type _pm[] = {DATA_TYPE_INTEGER, DATA_TYPE_REAL};
    signature ps = {0, 2, _pm, DATA_TYPE_REAL};
    double ret;
    rpc_call(_amcp_ctx_512192, &ps, &ret, a, b);
    return ret;
}

int32_t test_double(int32_t x){
    pm_type _pm[] = {DATA_TYPE_INTEGER};
    signature ps = {1, 1, _pm, DATA_TYPE_INTEGER};
    int32_t ret;
    rpc_call(_amcp_ctx_512192, &ps, &ret, x);
    return ret;
}

double test_inc(double* a){
    pm_type _pm[] = {DATA_TYPE_REAL_REF};
    signature ps = {2, 1, _pm, DATA_TYPE_REAL};
    double ret;
    rpc_call(_amcp_ctx_512192, &ps, &ret, a);
    return ret;
}

double test_mul(double a, double b){
    pm_type _pm[] = {DATA_TYPE_REAL, DATA_TYPE_REAL};
    signature ps = {3, 2, _pm, DATA_TYPE_REAL};
    double ret;
    rpc_call(_amcp_ctx_512192, &ps, &ret, a, b);
    return ret;
}

char* test_show_time(int32_t ac){
    pm_type _pm[] = {DATA_TYPE_INTEGER};
    signature ps = {4, 1, _pm, DATA_TYPE_STRING};
    char* ret;
    rpc_call(_amcp_ctx_512192, &ps, &ret, ac);
    return ret;
}

char* test_upper(char* s){
    pm_type _pm[] = {DATA_TYPE_STRING};
    signature ps = {5, 1, _pm, DATA_TYPE_STRING};
    char* ret;
    rpc_call(_amcp_ctx_512192, &ps, &ret, s);
    return ret;
}

void test_upper_inplace(char* s){
    pm_type _pm[] = {DATA_TYPE_STRING_REF};
    signature ps = {6, 1, _pm, DATA_TYPE_VOID};
    rpc_call(_amcp_ctx_512192, &ps, NULL, s);
    return;
}
