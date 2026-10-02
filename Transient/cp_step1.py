import sys; sys.path.insert(0,"Transient")
from cp_lib import *
tools = S.list_tools()
names = ["jawa/pawn_census","jawa/pawn_roles","jawa/incident_queue_peek","jawa/incident_queue_remove","jawa/damage_log","jawa/thing_lineage"]
tl = tools if isinstance(tools, list) else tools.get("tools", tools)
have = {t["name"]: t for t in tl}
print("tool count", len(have))
for n in names:
    t = have.get(n)
    if not t: print(n, "ABSENT"); continue
    ps = (t.get("inputSchema") or {}).get("properties") or {}
    print(n, "params:", {k: v.get("type") for k, v in ps.items()})
print("census:", J(call("jawa/pawn_census"), 800))
