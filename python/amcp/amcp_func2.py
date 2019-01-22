from inspect import getargspec
from .amcp_type import DataType

CCODE_TEMPLATE_SIGNATURE = "{ret} {name}({args})"

CCODE_TEMPLATE_DEFINITION = """pm_type _pm[] = {{{args}}};
    signature ps = {{"{name}", {num_args}, _pm, {ret}}};"""
CCODE_TEMPLATE_DEFINITION_NO_PM = """signature ps = {{"{name}", 0, NULL, {ret}}};"""

CCODE_TEMPLATE_BODY = """{ret} ret;
    rpc_call({var_ac}, &ps, &ret, {args});"""
CCODE_TEMPLATE_BODY_NO_PM = """{ret} ret;
    rpc_call({var_ac}, &ps, &ret);"""
CCODE_TEMPLATE_BODY_NO_RET = """rpc_call({var_ac}, &ps, NULL, {args});"""
CCODE_TEMPLATE_BODY_NO_PM_NO_RET = """rpc_call({var_ac}, &ps, NULL);"""

CCODE_TEMPLATE_RETURN = """return ret;"""
CCODE_TEMPLATE_RETURN_VOID = """return;"""
CCODE_TEMPLATE_FUNCTION = """{sig}{{
    {dfi}
    {body}
    {ret}
}}
"""


class RemoteFunction:
    def __init__(self, func, param=None, ret=DataType.VOID):
        self.func = func
        self.name = func.__name__
        self.obj = None
        self.ret_type = ret
        self.arg_types = []
        param = param or []
        arg_names = [p for p in getargspec(func).args if p not in ["self", "cls"]]
        self.sig = list(zip(arg_names, param))
        self.arg_types = [i for i, p in enumerate(self.sig) if p[1].value.ref]

    def set_obj(self, obj):
        self.obj = obj
        return self

    def call_and_pack(self, args):
        ret = self.func(self.obj, *args)
        ret = [self.ret_type.value.pdef(ret)]
        ret.extend(args[i] for i in self.arg_types)
        return ret

    def __call__(self, *args, **kwargs):
        return self.func(self.obj, *args, **kwargs)

    def ccode(self, var_ac):
        c_sig = CCODE_TEMPLATE_SIGNATURE.format(
            ret=self.ret_type.value.cdef,
            name="{}_{}".format(self.obj.__class__.__name__.lower(), self.name),
            args=", ".join("{} {}".format(p.value.cdef, name) for name, p in self.sig))

        if not self.sig:
            format_str = CCODE_TEMPLATE_DEFINITION_NO_PM
        else:
            format_str = CCODE_TEMPLATE_DEFINITION
        c_def = format_str.format(
            name=self.name,
            args=", ".join(p.value.name for name, p in self.sig),
            num_args=len(self.sig),
            ret=self.ret_type.value.name)

        if not self.sig:
            if self.ret_type is not DataType.VOID:
                format_str = CCODE_TEMPLATE_BODY_NO_PM
                format_str_ret = CCODE_TEMPLATE_RETURN
            else:
                format_str = CCODE_TEMPLATE_BODY_NO_PM_NO_RET
                format_str_ret = CCODE_TEMPLATE_RETURN_VOID
        else:
            if self.ret_type is not DataType.VOID:
                format_str = CCODE_TEMPLATE_BODY
                format_str_ret = CCODE_TEMPLATE_RETURN
            else:
                format_str = CCODE_TEMPLATE_BODY_NO_RET
                format_str_ret = CCODE_TEMPLATE_RETURN_VOID

        c_body = format_str.format(
            var_ac=var_ac,
            ret=self.ret_type.value.cdef,
            args=", ".join(name for name, _ in self.sig))
        c_ret = format_str_ret

        return CCODE_TEMPLATE_FUNCTION.format(sig=c_sig, dfi=c_def, body=c_body, ret=c_ret)


def remote(param=None, ret=DataType.VOID):
    def wrapper(func):
        return RemoteFunction(func, param=param, ret=ret)
    return wrapper
