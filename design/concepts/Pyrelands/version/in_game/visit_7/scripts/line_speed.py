"""python.exe: visit 7. Read the burn stamps along the one-cell trails the burn_line_walking mask shows away from the front
(LINE_RECTS, "x,z,w,h;..."), and print each burned cell with its stamp in time order: the ticks per cell along a trail say
what moved along it (a walking animal, a fire-hawk). Loads LANES_SAVE first (default burn_line_walking)."""
import json, os, re, sys
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
SAVE = os.environ.get("LANES_SAVE", "burn_line_walking")
RECTS = os.environ.get("LINE_RECTS", "66,137,28,5;54,88,26,5;162,81,21,5;129,57,15,5;85,76,16,16;186,211,14,11")
if SAVE != "-":
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Pyrelands"))
    import northstar_site as NS  # noqa: E402
    from northstar_driver.session import FastSession  # noqa: E402
    s = FastSession(strict=False)
    with s:
        NS.reload_fixture(s, SAVE, int(os.environ.get("LANES_TILE", "193")), map_id=1)
ASH = "RimMandrake.Pyrelands.MapComponent_PyrelandsAshField"
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    for rect in RECTS.split(";"):
        r = rb.call("jawa/static_call", {"type": ASH, "method": "ProbeRect", "args": rect}) or {}
        cells, now = [], 0
        for part in str(r.get("result") or "").split("|"):
            m = re.match(r"(\d+),(\d+):.*?terrain=([^;]*);.*?burnTick=(-?\d+);.*?now=(\d+);", part)
            if m and int(m.group(4)) >= 0:
                now = int(m.group(5))
                if now - int(m.group(4)) <= 120000:
                    cells.append((int(m.group(4)), int(m.group(1)), int(m.group(2)), m.group(3)))
        cells.sort()
        seq = [(c[0] - cells[0][0], c[1], c[2]) for c in cells] if cells else []
        print(json.dumps({"rect": rect, "burned": len(cells), "firstBurnAgo": (now - cells[0][0]) if cells else None,
                          "spanTicks": (cells[-1][0] - cells[0][0]) if cells else None,
                          "dt_x_z": seq[:40]}))
    lp = rb.call("jawa/list_pawns", {"limit": 500}) or {}
    print("animals:", json.dumps([(q.get("kind") or q.get("kindDef"), q.get("x"), q.get("z"), q.get("onFire"))
                                  for q in (lp.get("pawns") or []) if not q.get("colonist")])[:2500])
