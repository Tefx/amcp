from sys import version_info

from .amcp import AMCPEngine
from .amcp_type import DataType

if version_info.major == 2:
    from .amcp_func2 import remote
elif version_info.major == 3:
    # from .amcp_func import RemoteFunction
    from .amcp_func_idx import RemoteFunction
