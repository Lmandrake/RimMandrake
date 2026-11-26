"""Visit 5 diagnostic (no verdict): what is the black plant-free patch with two smoking dots south of the colony on the
fresh site? Lists the colonists' cells, every SteamGeyser / non-plant building and filth within 45 cells south of them,
and the terrain census of that box. Exit 0 always."""
import collections, json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import clockgate  # noqa: E402
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as raw:
    def call(name, **kw):
        return clockgate._unwrap(raw.call(name, kw))
    cols = [(p.get("x"), p.get("z")) for p in (call("jawa/list_pawns", limit=1000) or {}).get("pawns") or []
            if p.get("faction") in ("PlayerColony",) or p.get("isColonist")]
    print("COLONISTS", cols)
    cx = int(sum(c[0] for c in cols) / max(1, len(cols))) if cols else 125
    cz = int(sum(c[1] for c in cols) / max(1, len(cols))) if cols else 125
    box = "%d,%d,50,45" % (cx - 25, cz - 48)
    print("BOX", box)
    for grp in ("BuildingArtificial", "BuildingNatural", "Filth"):
        r = call("jawa/list_things", group=grp, rect=box, limit=500) or {}
        c = collections.Counter(x.get("def") for x in r.get("things") or [])
        print(grp, dict(c.most_common(15)))
    g = call("jawa/list_things", defName="SteamGeyser", limit=50) or {}
    print("GEYSERS", [(x.get("x"), x.get("z")) for x in g.get("things") or []])
    t = call("jawa/get_terrain_batch", rects=box) or {}
    cnt = collections.Counter()
    for op in str(t.get("ops") or "").split(";"):
        d, _, rr = op.partition(":")
        p = [int(v) for v in rr.split(",") if v.strip()] if rr else []
        if len(p) >= 2:
            cnt[d] += (p[2] if len(p) > 2 else 1) * (p[3] if len(p) > 3 else 1)
    print("TERRAIN", dict(cnt.most_common(10)))
    pl = call("jawa/list_things", group="Plant", rect=box, limit=3000) or {}
    rows = pl.get("things") or []
    occ = set((x.get("x"), x.get("z")) for x in rows)
    bare = [(x, z) for x in range(cx - 25, cx + 25) for z in range(cz - 48, cz - 3) if (x, z) not in occ]
    print("PLANTS", len(rows), "BARE cells", len(bare), "bare bbox",
          (min(b[0] for b in bare), min(b[1] for b in bare), max(b[0] for b in bare), max(b[1] for b in bare)) if bare else None)
