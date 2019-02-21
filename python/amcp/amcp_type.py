from collections import namedtuple
from enum import Enum

_DTItem = namedtuple("DataTypeItem", "cdef, pdef, name, ref")


class DataType(Enum):
    VOID = _DTItem("void", None, "DATA_TYPE_VOID", False)
    INT = _DTItem("int32_t", int, "DATA_TYPE_INTEGER", False)
    INT_REF = _DTItem("int32_t*", NotImplemented, "DATA_TYPE_INTEGER_REF", True)
    REAL = _DTItem("double", float, "DATA_TYPE_REAL", False)
    REAL_REF = _DTItem("double*", NotImplemented, "DATA_TYPE_REAL_REF", True)
    STR = _DTItem("char*", bytes, "DATA_TYPE_STRING", False)
    STR_REF = _DTItem("char*", NotImplemented, "DATA_TYPE_STRING_REF", True)
