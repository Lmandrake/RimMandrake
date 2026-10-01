import sys,json
from bx import call
r=call("jawa/get_defs",{"defs":sys.argv[1],"fields":sys.argv[2] if len(sys.argv)>2 else "label","limit":50})
print(json.dumps(r,default=str)[:3000])
