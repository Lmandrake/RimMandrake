"""Count water-ish terrain on the current map (python.exe)."""
import sys, json, os, re, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tok = resolve_endpoint()
with RimBridge(h, p, tok) as rb:
    g = rb.call("rimworld/get_game_info", {})
    n = 250
    r = rb.call("jawa/get_terrain_batch", {"rects": "0,0,%d,%d" % (n, n)})
    c = collections.Counter(); where = collections.defaultdict(list)
    for op in (r.get("ops") or "").split(";"):
        if not op: continue
        d, rect = op.split(":"); x, z, w, hh = map(int, rect.split(","))
        c[d] += w * hh
        if re.search("Water|Slime|Brine|Mud|Marsh|Ice|Lava|Tar|Acid|Propane", d): where[d].append((x, z, w))
    print(c.most_common(25))
    for d, l in where.items(): print(d, len(l), l[:6])
