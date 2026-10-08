import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    r=s.call("jawa/select_things",action="select",ids="RM_Draftprint97213"); print(str(r)[:300])
    r=s.call("rimworld/list_selected_gizmos"); print(str(r)[:1800])
