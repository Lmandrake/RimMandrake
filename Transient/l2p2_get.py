import sys,os
root=os.getcwd(); U=os.path.join(root,"src","RimMandrake","Utils")
for p in (U, os.path.join(U,"modcheck")): sys.path.insert(0,p)
from rimdrive import Session
with Session(lock=None) as s:
    print(s.call("jawa/mod_settings_field", typeName=sys.argv[1], action="get", field=sys.argv[2]))
    if len(sys.argv)>3: print(s.call("jawa/mod_settings_field", typeName=sys.argv[1], action="set", field=sys.argv[2], value=sys.argv[3]))
