"""Stillsand content live: atlas spawn, zuurrik on blood, loomma sunstruck open vs roofed, soorrak flight state (report only)."""
import json, collections
from bx import call
from st_sandswim_lib import *  # noqa

OUT = {}
def log(k, v):
    OUT[k] = v
    print(k, json.dumps(v, default=str)[:900], flush=True)
    json.dump(OUT, open("st3.json", "w"), indent=1, default=str)

def kinds_on_map():
    return collections.Counter(p.get("kindDef") for p in pawns() if not p.get("dead"))

def sev(pid, hd):
    h = call("jawa/pawn_get", {"pawn": pid}).get("pawns") or []
    if not h:
        return "absent"
    for x in h[0].get("hediffs") or []:
        if x.get("def") == hd:
            return x.get("severity")
    return 0

# 1. atlas: one of each Stillsand kind on a fresh sand pad
KINDS = "Aurrok Drazzik Duumma Gaanok Guzzka Ikee Liikka Loomma Nizzek Oommok Oorrik Qorrax Ruukka ShadeMite Siidda Soorrak Vaalok Veessa Vekka Vozzik Zuurrik".split()
log("paint_atlas", paint(150, 160, 90, 40, "Sand"))
atlas = {}
for i, k in enumerate(KINDS):
    ids, msg = spawn("RM_" + k, 155 + (i % 10) * 8, 170 + (i // 10) * 10, "none")
    atlas["RM_" + k] = ids[0] if ids else msg
log("atlas_spawn", atlas)
log("texture_audit", call("jawa/texture_audit", {"filter": "RM_", "limit": 200}))

# 2. soorrak flight STATE read (report only, never start)
sid = atlas.get("RM_Soorrak")
log("soorrak_flight_report", call("jawa/pawn_flight", {"action": "report", "pawn": sid}))

# 3. loomma: open sand vs roofed
lo_open, _ = spawn("RM_Loomma", 120, 200, "none", 3)
paint(100, 215, 12, 12, "Sand")
roof = call("jawa/set_roof_batch", {"ops": "100,215,12,12", "roofDef": "RoofConstructed"})
lo_roof, _ = spawn("RM_Loomma", 106, 221, "none", 3)
log("loomma_setup", {"open": lo_open, "roofed": lo_roof, "roof": {k: roof.get(k) for k in ("success", "message")}})

# 4. zuurrik: blood on sand
paint(60, 60, 20, 20, "Sand")
cells = [(64 + (j % 4) * 2, 64 + (j // 4) * 2) for j in range(12)]
r = call("jawa/spawn_batch", {"ops": ";".join(f"Filth_Blood:{x},{z}" for x, z in cells)})
log("blood_spawn", {k: r.get(k) for k in ("success", "message", "spawned", "failed")})
b = call("jawa/list_things", {"defName": "Filth_Blood", "rect": "60,60,20,20", "limit": 100})
log("blood_present", len(b.get("things") or []))
log("t0", {"zuurrik": kinds_on_map().get("RM_Zuurrik", 0),
           "loomma_open": [sev(p, "RM_LoommaSunstruck") for p in lo_open],
           "loomma_roof": [sev(p, "RM_LoommaSunstruck") for p in lo_roof]})
for i in range(10):
    step(600)
    b = call("jawa/list_things", {"defName": "Filth_Blood", "rect": "60,60,20,20", "limit": 100})
    log(f"t{i+1}", {"zuurrik": kinds_on_map().get("RM_Zuurrik", 0), "blood": len(b.get("things") or []),
                    "loomma_open": [sev(p, "RM_LoommaSunstruck") for p in lo_open],
                    "loomma_roof": [sev(p, "RM_LoommaSunstruck") for p in lo_roof]})
print("DONE")
