import json
from bx import call
r = call("jawa/get_defs", {"defs": "BiomeDef/RM_Stillsand;BiomeDef/RM_LongShade;ThingDef/RSW_KraytDragon;ThingDef/RSW_GreaterKraytDragon;ThingDef/RSW_SandStalker;ThingDef/RM_Mirrak", "fields": "modExtensions,comps"}, 60)
json.dump(r, open("getdefs_ext.json","w"), indent=1, default=str)
print({k: r.get(k) for k in ("success","foundCount","notFound","message")})
for d in r.get("defs") or r.get("results") or []:
    print(d.get("defName"), json.dumps(d.get("fields") or {k:v for k,v in d.items() if k in ("modExtensions","comps")}, default=str)[:600])
