# amcp
Invoking python code in AutoMod using RPC

~~(*Currently only Python 3 is supported since it uses Function Annotations as type hinting. Support of Python 2 will be added soon.*)~~

*Support of Python 2 is not tested.*

## Installation

  ```
  copy include/$ARCH/*.h to $ASI/include
  copy bin/$ARCH/*.dll to $ASI/bin
  copy bin/$ARCH/*.lib to $ASI/lib
  ```
  where `$ASI` is the AutoMod install path. Also, add `ASILIBS=amcp.lib` in Environment Variables.
  
  The Python module is under `python/`. Dependencies: `pyzmq` and `msgpack`

## Example

### Step 1: Define functions in Python 

  For Python 3+
  ```Python
  from amcp import RemoteFunction, DataType as dt, AMCPEngine
  import pandas as pd

  class Test(AMCPEngine):
      @RemoteFunction
      def time_delta(self, ac: dt.INT) -> dt.STR:
          # dt.STR corresponds to bytes in python
          return "Time delta is {}".format(pd.Timedelta(seconds=ac)).encode("utf-8") 


  test_server = Test()
  ```
  
  For Python 2
  ```Python
  from amcp import remote, DataType as dt, AMCPEngine
  import pandas as pd

  class Test(AMCPEngine):
      @remote([dt.INT], dt.STR)
      def time_delta(self, ac):
          return "Time delta is {}".format(pd.Timedelta(seconds=ac))

  test_server = Test()
  ```
  
  The method decorated by `RemoteFunction` (or `remote` for Python 2) will be invokable from AutoMod. Data types currently supported: `VOID`, `INT`, `INT_REF`, `REAL`, `REAL_REF`, `STR` and `STR_REF`. `*_REF` are reference types which can be modified inside the functions (like pointers in C). In Python code, the referred values are accessed by `v[0]`. For example:
  ```Python
  @RemoteFunction
  def iadd(self, a: dt.INT_REF, i: dt.INT):
      a[0] += i
  ```
  for which the corresponding C function signature will be `void test_iadd(int32_t* a, int32_t i);`.
  
### Step 2: Generate C code

  ```Python
  test_server.gen_c(path=None)
  ```
  will generate C code similar to the following. 
  ```C
  #include <amcp.h>

  amcp_context* _amcp_ctx_830913;

  int32_t test_amcp_connect(const char* addr){
      _amcp_ctx_830913 = amcp_ctx_new( addr);
      return 0;
  }

  int32_t test_amcp_close(){
      amcp_ctx_destroy(_amcp_ctx_830913);
      return 0;
  }

  char* test_time_delta(int32_t ac){
      pm_type _pm[] = {DATA_TYPE_INTEGER};
      signature ps = {"time_delta", 1, _pm, DATA_TYPE_STRING};
      char* ret;
      rpc_call(_amcp_ctx_830913, &ps, &ret, ac);
      return ret;
  }
  ```
  We can also use `test.gen_c(path="./")` to directly write the code to `./test_gen.c` (or `test.gen_c(path="./", header=True)` to write the code to `./test_gen.h`). 
  
### Step 3: Start the RPC server

  ```
  test_server.serve_forever("tcp://*:5555")
  ```

  Note that this module uses [ZeroMQ](http://zeromq.org/) as the underlying network library. Thus, any *endpoint* supported by ZeroMQ is acceptable as listening address. **The server and AutoMod executable need not be on the same host.** Refer to http://api.zeromq.org/4-2:zmq-bind for more info.


### Step 4: Include the generated C source and declear the functions in AutoMod
### Step 5: Connect the server in `model initialization` or `model ready` function
  ```
  begin model initialization function
    return test_amcp_connect("tcp://{server-ip}:5555")
  end
  ```
  Again, the connecting address is a *ZeroMQ endpoint*.

### Step 6: Then, we can directly call `test_time_delta` from AutoMod source:
  ```
  begin P_test arriving
    while 1=1 do begin
      print test_time_delta(ac as seconds) to message
      wait for 5 sec
    end
  end
  ```

### Step 7: Close the connection in `model finished` function
  ```
  begin model finished function
    return test_amcp_close()
  end
  ```
