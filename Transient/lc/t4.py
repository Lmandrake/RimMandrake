import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    r=s.call("jawa/list_pawns"); print(str(r)[:1500])
