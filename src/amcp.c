#include <stdarg.h>
#include <msgpack.h>
#include <zmq.h>

#include "amcp.h"

struct _amcp_context {
    void *context;
    void *requester;
    msgpack_sbuffer buffer;
    msgpack_unpacked und;
    msgpack_packer pk;
    msgpack_unpacker upk;
};

amcp_context *amcp_ctx_new(const char *addr) {
    amcp_context *ac = (amcp_context *) malloc(sizeof(amcp_context));

    ac->context = zmq_ctx_new();
    ac->requester = zmq_socket(ac->context, ZMQ_REQ);
    zmq_connect(ac->requester, addr);

    msgpack_packer_init(&ac->pk, &ac->buffer, msgpack_sbuffer_write);
    msgpack_unpacker_init(&ac->upk, 1024);
    return ac;
}

void amcp_ctx_destroy(amcp_context *ac) {
    msgpack_unpacker_destroy(&ac->upk);

    zmq_close(ac->requester);
    zmq_ctx_destroy(ac->context);
}

int pack_procedure(msgpack_packer *pk, signature *ps, va_list valist) {
    int error = 0;
    char *body;
    size_t len_body;
    msgpack_pack_array(pk, ps->pm_num + 1);

    size_t len_name = strlen(ps->name);
    msgpack_pack_str(pk, len_name);
    msgpack_pack_str_body(pk, ps->name, len_name);
    for (int i = 0; i < ps->pm_num; ++i) {
        if (ps->pm[i] & 0b01) msgpack_pack_array(pk, 1);
        switch (ps->pm[i] & (~0b01)) {
            case DATA_TYPE_INTEGER:
                msgpack_pack_int32(pk, va_arg(valist, int32_t));
                break;
            case DATA_TYPE_REAL:
                msgpack_pack_double(pk, va_arg(valist, double));
                break;
            case DATA_TYPE_STRING:
                body = va_arg(valist, char*);
                len_body = strlen(body);
                msgpack_pack_str(pk, len_body);
                msgpack_pack_str_body(pk, body, len_body);
                break;
            default:
                error = 1;
        }
    }
    return error;
}

#define _ref_item(item) ((item).via.array.ptr[0].via)

int unpack_result(msgpack_unpacker *upk, msgpack_unpacked *und,
                  signature *ps, char *buffer, size_t size, void *ret, va_list valist) {
    int error = 0;

    if (msgpack_unpacker_buffer_capacity(upk) < size)
        msgpack_unpacker_reserve_buffer(upk, size);
    memcpy(msgpack_unpacker_buffer(upk), buffer, size);
    msgpack_unpacker_buffer_consumed(upk, size);
    msgpack_unpacker_next(upk, und);
    msgpack_object_array array = und->data.via.array;

//    msgpack_zone mempool;
//    msgpack_object deserialized;
//    msgpack_zone_init(&mempool, size);
//    msgpack_unpack(buffer, size, NULL, &mempool, &deserialized);
//    msgpack_object_array array = deserialized.via.array;

    if (ps->ret == DATA_TYPE_INTEGER) {
        *(int32_t *) ret = (int32_t) array.ptr[0].via.i64;
    } else if (ps->ret == DATA_TYPE_REAL) {
        *(double *) ret = array.ptr[0].via.f64;
    } else if (ps->ret == DATA_TYPE_STRING) {
        msgpack_object_str str_obj = array.ptr[0].via.str;
        char *ret_as_str = (char *) malloc(str_obj.size + 1);
        memcpy(ret_as_str, str_obj.ptr, str_obj.size);
        ret_as_str[str_obj.size] = 0;
        *(char **) ret = ret_as_str;
    } else if (ps->ret == DATA_TYPE_VOID) {

    } else {
        error = 1;
    }

    for (int i = 0, k = 0; i < ps->pm_num; ++i) {
        if (ps->pm[i] == DATA_TYPE_INTEGER) {
            va_arg(valist, int32_t);
        } else if (ps->pm[i] == DATA_TYPE_REAL) {
            va_arg(valist, double);
        } else if (ps->pm[i] == DATA_TYPE_STRING) {
            va_arg(valist, char*);
        } else if (ps->pm[i] == DATA_TYPE_INTEGER_REF) {
            *va_arg(valist, int32_t*) = (int32_t) _ref_item(array.ptr[++k]).i64;
        } else if (ps->pm[i] == DATA_TYPE_REAL_REF) {
            *va_arg(valist, double*) = _ref_item(array.ptr[++k]).f64;
        } else if (ps->pm[i] == DATA_TYPE_STRING_REF) {
            msgpack_object_str str_obj = _ref_item(array.ptr[++k]).str;
            char *str = va_arg(valist, char*);
            memcpy(str, str_obj.ptr, str_obj.size);
            str[str_obj.size] = 0;
        } else {
            error = 1;
        }
    }

    return error;
}

void _free_buffer(void *data, void *buffer) {
    msgpack_sbuffer_destroy(buffer);
}

void rpc_call(amcp_context *ac, signature *ps, void *ret, ...) {
    va_list valist;
    zmq_msg_t message;

    msgpack_sbuffer_init(&ac->buffer);
    va_start(valist, ret);
    pack_procedure(&ac->pk, ps, valist);
    va_end(valist);
    zmq_msg_init_data(&message, ac->buffer.data, ac->buffer.size, _free_buffer, &ac->buffer);
    zmq_msg_send(&message, ac->requester, 0);

    zmq_msg_init(&message);
    zmq_msg_recv(&message, ac->requester, 0);
    msgpack_unpacked_init(&ac->und);
    va_start(valist, ret);
    unpack_result(&ac->upk, &ac->und, ps, zmq_msg_data(&message), zmq_msg_size(&message), ret, valist);
    va_end(valist);
    msgpack_unpacked_destroy(&ac->und);
    zmq_msg_close(&message);
}