import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
KEEP=("mentalBreakThresholdOffset","restFallFactor","hungerRateFactor","naturalHealingFactor","statOffsets","statFactors","capMods","painFactor","socialFightChanceFactor","makeImmuneTo")
with RimBridge(host, port, token) as rb:
    h=rb.call("jawa/get_defs",{"defs":"HediffDef/RUT_Sym_Nightwake;HediffDef/RUT_Sym_Quickflesh;HediffDef/RUT_Sym_Sheenblood;HediffDef/RUT_Sym_Mycoid;HediffDef/RUT_Bioregenerating","fields":"stages","deep":True})
    for row in h.get("defs",[]):
        st=row["fields"]["stages"][0]
        print(row["defName"], {k:v for k,v in st.items() if k in KEEP and v not in (None,[],1.0,0.0,-1.0)} or {k:v for k,v in st.items() if k in KEEP})
