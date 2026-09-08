import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with open(r"D:\Luke\dev\Rimworld\Transient\droidworks_detonation_review\grid_with_ids.json") as f:
    grid = json.load(f)

RADIUS = 6  # rect half-extent for the post-kill scan around each site

with RimBridge(host, port, token) as rb:
    for cell in grid:
        r = rb.call("jawa/damage", {
            "damageDef": "Bomb", "amount": 2000, "thingId": cell["pawnId"]})
        print(cell["cell"], "damage ->", json.dumps(r)[:200])
        cell["damage_result"] = r

        rectstr = "%d,%d,%d,%d" % (cell["x"] - RADIUS, cell["z"] - RADIUS, RADIUS * 2, RADIUS * 2)
        lt = rb.call("jawa/list_things", {"rect": rectstr, "includePawns": False})
        things = lt.get("things", [])
        defs_here = [t.get("def") for t in things]
        has_explosion = any(d and "explosion" in d.lower() for d in defs_here)
        has_corpse = any(d and "corpse" in (d or "").lower() for d in defs_here)
        cell["things_after"] = defs_here
        cell["has_explosion"] = has_explosion
        cell["has_corpse"] = has_corpse
        print("  things:", defs_here, "EXPLOSION:", has_explosion, "CORPSE:", has_corpse)

    with open(r"D:\Luke\dev\Rimworld\Transient\droidworks_detonation_review\grid_final.json", "w") as f:
        json.dump(grid, f, indent=2)
