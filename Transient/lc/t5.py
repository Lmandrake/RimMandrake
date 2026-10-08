import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    print(sorted(n for n in s.tools if any(k in n.lower() for k in ("gizmo","command","click","invoke","designat","verb","float","action"))))
