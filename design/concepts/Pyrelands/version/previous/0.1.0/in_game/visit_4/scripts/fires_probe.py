"""Visit 4 diagnostic (no verdict): what burns on the concrete firebreak beside a burned scorch-fruit pad? Re-stages the
scorchfruit_fire_born pad as its row does (PAD_FIRE_BORN (190,60), 24x24 rect, a 4-cell Concrete ring with its plants
cleared, soil, ember grass, the rect lit at 1.2), advances 11600 ticks, then lists every Fire outside the rect and the
things in each such cell (rimworld/get_cells_info). Run on a reloaded site. Exit 0 always."""
import json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import clockgate  # noqa: E402
X, Z, W = 178, 48, 24
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as raw:
    class _S:
        def call(self, name, **kw):
            return clockgate._unwrap(raw.call(name, kw))
    rb = _S()
    ring = [(X - 4, Z - 4, W + 8, 4), (X - 4, Z + W, W + 8, 4), (X - 4, Z, 4, W), (X + W, Z, 4, W)]
    rs = lambda r: "%d,%d,%d,%d" % r  # noqa: E731
    rb.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (X, Z, W, W), categories="All")
    rb.call("jawa/set_terrain_batch", ops=";".join("Concrete:%s" % rs(r) for r in ring), layer="top")
    rb.call("jawa/set_plants", ops=";".join("CLEAR:%s" % rs(r) for r in ring))
    rb.call("jawa/set_terrain", x=X, z=Z, terrainDef="RM_FE_Ground_Soil", width=W, height=W, layer="top")
    rb.call("jawa/set_plants", ops="RM_FE_Plant_EmberGrass:%d,%d,%d,%d" % (X, Z, W, W), growth=1.0)
    print("fire", json.dumps(rb.call("jawa/map_fire", action="start", rect="%d,%d,%d,%d" % (X, Z, W, W), fireSize=1.2))[:300])
    done = 0
    for target in (2500, 5000, 7500, 10000, 11600):
        while done < target:
            step = min(2500, target - done)
            clockgate.advance_chunk(rb, step)
            done += step
        fires = rb.call("jawa/list_things", defName="Fire", rect="%d,%d,%d,%d" % (X - 4, Z - 4, W + 8, W + 8), limit=2000).get("things") or []
        out = [f for f in fires if not (X <= f.get("x", -1) < X + W and Z <= f.get("z", -1) < Z + W)]
        print("tick+%d fires in pad+ring %d, outside the pad %d" % (done, len(fires), len(out)), flush=True)
        for f in out[:6]:
            ci = rb.call("rimworld/get_cell_info", x=f["x"], z=f["z"])
            print("  OUTSIDE", f.get("x"), f.get("z"), "parent=%s" % f.get("parent"), json.dumps(ci)[:700], flush=True)
    rb.call("jawa/map_fire", action="extinguish", rect="0,0,250,250")
