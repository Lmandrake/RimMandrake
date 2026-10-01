from bx import call
import json
for v in ("RM_Vekka111419","RM_Vekka111420","RM_Vekka111775"):
    r=call("jawa/pawn_mental",{"pawn":v,"action":"end"}); print(v, r.get("success"), r.get("message"))
cs=call("rimworld/list_colonists",{})
for c in cs.get("colonists",[]): print(c.get("name"), c.get("pawnId"), {k:c.get(k) for k in ("downed","dead","health","x","z")})
