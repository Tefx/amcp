from amcp import RemoteFunction, DataType as dt, AMCPEngine
import pandas as pd

class Test(AMCPEngine):
    @RemoteFunction
    def time_delta(self, ac: dt.INT) -> dt.STR:
        # dt.STR corresponds to bytes in python
        return "Time delta is {}".format(pd.Timedelta(seconds=ac)).encode("utf-8")


test_server = Test()
test_server.serve_forever("tcp://*:12345")