import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
DEFS=["RUT_Tea_AgeReversal","RUT_Tea_Bioregeneration","RUT_Tea_Pleasure","RUT_Symbiont_Quickflesh","RUT_Symbiont_Nightwake","RUT_Symbiont_Sheenblood","RUT_Symbiont_Mycoid"]
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/get_defs",{"defs":";".join("ThingDef/"+d for d in DEFS),"fields":"comps,modExtensions","deep":True})
    for row in r.get("defs",[]):
        cs=row["fields"]["comps"]
        life=[c.get("lifespanTicks") for c in cs if isinstance(c,dict) and "lifespanTicks" in c]
        tr=[c.get("minSafeTemperature") for c in cs if isinstance(c,dict) and "minSafeTemperature" in c]
        print(row["defName"],"lifespanTicks",life,"minSafeTemp",tr,"modExt",row["fields"].get("modExtensions"))
    h=rb.call("jawa/get_defs",{"defs":"HediffDef/RUT_Sym_Quickflesh;HediffDef/RUT_Sym_Nightwake;HediffDef/RUT_Sym_Sheenblood;HediffDef/RUT_Sym_Mycoid;HediffDef/RUT_AgeReversalSated","fields":"stages,comps","deep":True})
    for row in h.get("defs",[]):
        print("==",row["defName"]); print("  stages:",json.dumps(row["fields"]["stages"])[:900]); print("  comps:",json.dumps(row["fields"]["comps"])[:300])
