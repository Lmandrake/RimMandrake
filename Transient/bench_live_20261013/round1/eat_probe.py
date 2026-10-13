"""BENCH round 1: after the Pyrelands rows, do the site colonists actually EAT from the food cache? Read drafted/job/
Food, MealSurvivalPack count on the map; one governed 3000-tick step (clockgate.advance_chunk -> jawa/safe_advance);
read again.  python.exe eat_probe.py <out.json>"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("src/RimMandrake/Utils", "src/RimMandrake/Utils/modcheck"):
    sys.path.insert(0, os.path.join(HERE, *p.split("/")))
import clockgate as cg  # noqa: E402
from northstar_driver.session import FastSession  # noqa: E402

def read(s):
    out = {"tick": s.call("jawa/time_clock").get("ticksGame")}
    cols = s.call("rimworld/list_colonists", currentMapOnly=True).get("colonists") or []
    rows = []
    for c in cols:
        pid = c.get("pawnId") or c.get("id")
        nd = s.call("jawa/pawn_need", pawn=str(pid).replace("Thing_", ""), action="list")
        food = next((n.get("level") for n in nd.get("needs") or [] if n.get("need") == "Food"), None)
        rows.append({"id": pid, "name": c.get("name"), "drafted": c.get("drafted"), "job": c.get("currentJob") or c.get("job"),
                     "food": food})
    out["pawns"] = rows
    lt = s.call("jawa/list_things", defName="MealSurvivalPack", limit=200) or {}
    out["packs"] = sum((t.get("stackCount") or t.get("count") or 1) for t in lt.get("things") or [])
    out["packStacks"] = len(lt.get("things") or [])
    return out

OUT = {}
s = FastSession(strict=False)
with s:
    OUT["before"] = read(s)
    OUT["executed"] = cg.advance_chunk(s, int(sys.argv[2]) if len(sys.argv) > 2 else 3000)
    OUT["after"] = read(s)
print(json.dumps(OUT, indent=1, default=str))
with open(sys.argv[1], "w") as f:
    json.dump(OUT, f, indent=1, default=str)
