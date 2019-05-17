import inspect
from inspect import signature
from .amcp_type import DataType
from os import linesep

CCODE_TEMPLATE_DOC = "/*{sep}{{doc}}{sep}*/{sep}".format(sep=linesep)
CCODE_TEMPLATE_SIGNATURE = "{ret} {name}({args})"

CCODE_TEMPLATE_DEFINITION = """pm_type _pm[] = {{{args}}};
    signature ps = {{{name}, {num_args}, _pm, {ret}}};"""
CCODE_TEMPLATE_DEFINITION_NO_PM = """signature ps = {{{name}, 0, NULL, {ret}}};"""

CCODE_TEMPLATE_BODY = """{ret} ret;
    rpc_call({var_ac}, &ps, &ret, {args});"""
CCODE_TEMPLATE_BODY_NO_PM = """{ret} ret;
    rpc_call({var_ac}, &ps, &ret);"""
CCODE_TEMPLATE_BODY_NO_RET = """rpc_call({var_ac}, &ps, NULL, {args});"""
CCODE_TEMPLATE_BODY_NO_PM_NO_RET = """rpc_call({var_ac}, &ps, NULL);"""

CCODE_TEMPLATE_RETURN = """return ret;"""
CCODE_TEMPLATE_RETURN_VOID = """return;"""
CCODE_TEMPLATE_FUNCTION = """{doc}{sig}{{
    {dfi}
    {body}
    {ret}
}}
"""


class RemoteFunction:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        self.obj = None
        self.sig = signature(func)
        self.arg_types = self.mark_refs()

        ret_sig = self.sig.return_annotation
        if ret_sig == self.sig.empty:
            self.sig = self.sig.replace(return_annotation=DataType.VOID)
        self.ret_type = self.sig.return_annotation.value.pdef

    def mark_refs(self):
        refs = []
        k = 0
        for name, p in self.sig.parameters.items():
            if name not in ("self", "cls"):
                if p.annotation.value.ref:
                    refs.append(k)
                k += 1
        return refs

    def set_obj(self, obj):
        self.obj = obj
        return self

    def call_and_pack(self, args):
        # print(self.func.__name__)
        ret = self.func(self.obj, *args)
        # print(self.func.__name__, "finished")
        if self.ret_type is not None:
            ret = [self.ret_type(ret)]
        else:
            ret = [ret]
        ret.extend(args[i] for i in self.arg_types)
        return ret

    def __call__(self, *args, **kwargs):
        return self.func(self.obj, *args, **kwargs)

    def ccode(self, var_ac, idx):
        args = [p for name, p in self.sig.parameters.items() if name not in ("self", "cls")]

        if self.func.__doc__:
            c_doc = CCODE_TEMPLATE_DOC.format(doc=inspect.cleandoc(self.func.__doc__))
        else:
            c_doc = ""

        c_sig = CCODE_TEMPLATE_SIGNATURE.format(
            ret=self.sig.return_annotation.value.cdef,
            name="{}_{}".format(self.obj.__class__.__name__.lower(), self.name),
            args=", ".join("{} {}".format(p.annotation.value.cdef, p.name) for p in args))

        if not args:
            format_str = CCODE_TEMPLATE_DEFINITION_NO_PM
        else:
            format_str = CCODE_TEMPLATE_DEFINITION
        c_def = format_str.format(
            # name=self.name,
            name=idx,
            args=", ".join(p.annotation.value.name for p in args),
            num_args=len(args),
            ret=self.sig.return_annotation.value.name)

        if not args:
            if self.ret_type is not None:
                format_str = CCODE_TEMPLATE_BODY_NO_PM
                format_str_ret = CCODE_TEMPLATE_RETURN
            else:
                format_str = CCODE_TEMPLATE_BODY_NO_PM_NO_RET
                format_str_ret = CCODE_TEMPLATE_RETURN_VOID
        else:
            if self.ret_type is not None:
                format_str = CCODE_TEMPLATE_BODY
                format_str_ret = CCODE_TEMPLATE_RETURN
            else:
                format_str = CCODE_TEMPLATE_BODY_NO_RET
                format_str_ret = CCODE_TEMPLATE_RETURN_VOID
        c_body = format_str.format(
            var_ac=var_ac,
            ret=self.sig.return_annotation.value.cdef,
            args=", ".join(p.name for p in args))
        c_ret = format_str_ret

        return CCODE_TEMPLATE_FUNCTION.format(doc=c_doc, sig=c_sig, dfi=c_def, body=c_body, ret=c_ret)
