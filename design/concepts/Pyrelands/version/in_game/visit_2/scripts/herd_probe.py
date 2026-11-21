"""Visit 2: both readings for the herd_thirst check repairs (python.exe, bridge held, the site loaded).
map_comp_read with the short type name (the repaired constant) and with a planted name absent from the map; get_def's
modExtensions type names for RM_Ullai (expects RM_ThirstGrassWateredExtension) and Muffalo (expects none)."""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tk = resolve_endpoint()
out = {}
with RimBridge(h, p, tk) as rb:
    for name in ("MapComponent_PyrelandsHerdThirst", "RimMandrake.Pyrelands.MapComponent_PyrelandsHerdThirst",
                 "MapComponent_PyrelandsHerdThirstPLANTED"):
        r = rb.call("jawa/map_comp_read", {"comp": name})
        out["map_comp_read " + name] = {"success": r.get("success"), "message": str(r.get("message"))[:120]}
    for d in ("RM_Ullai", "Muffalo"):
        r = rb.call("jawa/get_def", {"defName": d})
        out["get_def " + d] = {"success": r.get("success"), "modExtensions": (r.get("extra") or {}).get("modExtensions")}
print(json.dumps(out, indent=1))
json.dump(out, open(r"design\concepts\Pyrelands\version\in_game\visit_2\evidence\herd_probe.json", "w"), indent=1)
