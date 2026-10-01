from bx import call
import json
r=call("jawa/spawn_pawn",{"kindDef":"RM_Oorrik","x":160,"z":195,"faction":"none"}); print(json.dumps(r,default=str)[:1500])
