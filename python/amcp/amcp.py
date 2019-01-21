from __future__ import print_function

import os
import zmq
import msgpack
from sys import version_info
from uuid import uuid4

if version_info.major == 2:
    from .amcp_func2 import RemoteFunction
elif version_info.major == 3:
    from .amcp_func import RemoteFunction

C_VAR_AC = "_amcp_ctx_{uid}"
C_TEMPLATE = """#include <amcp.h>

amcp_context* {var_ac};

int32_t {cls_name}_amcp_connect(const char* addr){{
    {var_ac} = amcp_ctx_new( addr);
    return 0;
}}

int32_t {cls_name}_amcp_close(){{
    amcp_ctx_destroy({var_ac});
    return 0;
}}

{functions}"""


class AMCPEngine:
    def __init__(self):
        self.libs = {}
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, RemoteFunction):
                attr.set_obj(self)
                self.libs[attr.name.encode("utf-8")] = attr

    def serve_forever(self, addr, silence=True):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(addr)

        print("RPCSever started on {}".format(addr))

        while True:
            message = socket.recv()
            args = msgpack.unpackb(message)
            ret = self.libs[args[0]].call_and_pack(args[1:])
            if not silence: print("Calling", args[0], "Ret", ret)
            socket.send(msgpack.packb(ret))

    def gen_c(self, path="./", header=False):
        var_ac = C_VAR_AC.format(uid=int(uuid4().time % 1e6))
        namespace = self.__class__.__name__.lower()
        buffer = C_TEMPLATE.format(
            var_ac=var_ac,
            cls_name=namespace,
            functions=os.linesep.join(f.ccode(var_ac) for f in self.libs.values()))
        if path is not None:
            filename = "{}_gen.{}".format(namespace, "h" if header else "c")
            with open(os.path.join(path, filename), "w") as f:
                f.write(buffer)
                return self
        else:
            return buffer
