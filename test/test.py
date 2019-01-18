from amcp import RemoteFunction as rf, DataType as dt, AMCPEngine

import pandas as pd


class Test(AMCPEngine):
    @rf
    def add(self, a: dt.INT, b: dt.REAL) -> dt.REAL:
        return a + b

    @rf
    def mul(self, a: dt.REAL, b: dt.REAL) -> dt.REAL:
        return a * b

    @rf
    def double(self, x: dt.INT) -> dt.INT:
        return x * 2

    @rf
    def upper(self, s: dt.STR) -> dt.STR:
        return s.upper()

    @rf
    def show_time(self, ac: dt.INT) -> dt.STR:
        return str(pd.Timedelta(seconds=ac))

    @rf
    def inc(self, a: dt.REAL_REF) -> dt.REAL:
        a[0] += 1
        return 1

    @rf
    def upper_inplace(self, s: dt.STR_REF):
        s[0] = s[0].upper()


if __name__ == '__main__':
    Test().gen_c(header=True).serve_forever("tcp://*:5555")
