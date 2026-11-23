"""python.exe: visit 7, the live read of the lanes the day-end captures of burn_line show (thin straight horizontal burned
strands across the map). Loads the save named by $LANES_SAVE (default burn_line_walking, which burn_line writes while its
front walks), reads every cell's ash-field burn stamp (MapComponent_PyrelandsAshField.ProbeRect, 20x20 per call), takes the
cells burned in the last $LANES_WINDOW ticks (default one day) and measures T_BURN_LANES' own proxy, the share of burned
cells that are one-cell strands (both x-neighbours unburned, or both z-neighbours unburned), plus the longest straight
one-cell strand run along x. The offline model (selftest_pyrelands_burn_front_lanes.py) bars a front at the game's own
even-spread share + 0.10 (vanilla 0.02 at full cover, 0.15 at 0.80 cover): LIMIT 0.25 is the 0.80-cover bar.
Exit 0 PASS (share <= LIMIT), 1 FAIL, 2 UNMEASURED. Writes evidence/lanes_<save>.json and a burned-cell mask PNG."""
import json, os, re, sys
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

SAVE = os.environ.get("LANES_SAVE", "burn_line_walking")
WINDOW = int(os.environ.get("LANES_WINDOW", "60000"))
LIMIT = 0.25
ASH = "RimMandrake.Pyrelands.MapComponent_PyrelandsAshField"
OUT = os.path.join("design", "concepts", "Pyrelands", "version", "in_game", "visit_7", "evidence")


def u(r):
    return r or {}


ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
if SAVE != "-":   # loaded the way the runner reloads the site (settled, homed), never a bare load_game
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Pyrelands"))
    import northstar_site as NS  # noqa: E402
    from northstar_driver.session import FastSession  # noqa: E402
    s = FastSession(strict=False)
    with s:
        mi0 = NS.reload_fixture(s, SAVE, int(os.environ.get("LANES_TILE", "193")), map_id=1)
    print("loaded %s: map %s tile %s %s" % (SAVE, mi0.get("mapId"), mi0.get("tile"), mi0.get("mapBiome")))
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    mi = u(rb.call("jawa/map_info", {}))
    sx, sz = int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or 0)
    if not sx or not sz:
        print(json.dumps({"verdict": "UNMEASURED", "why": "map_info unread: %s" % str(mi)[:300]}))
        sys.exit(2)
    stamp, now, bad = {}, None, 0
    for z0 in range(0, sz, 20):
        for x0 in range(0, sx, 20):
            w, hh = min(20, sx - x0), min(20, sz - z0)
            r = u(rb.call("jawa/static_call", {"type": ASH, "method": "ProbeRect", "args": "%d,%d,%d,%d" % (x0, z0, w, hh)}))
            txt = str(r.get("result") or "")
            if not r.get("success") or txt.startswith("error="):
                bad += 1
                continue
            for part in txt.split("|"):
                m = re.match(r"(\d+),(\d+):.*?burnTick=(-?\d+);.*?now=(\d+);", part)
                if m:
                    stamp[(int(m.group(1)), int(m.group(2)))] = int(m.group(3))
                    now = int(m.group(4))
    if bad or now is None or len(stamp) < sx * sz * 0.99:
        print(json.dumps({"verdict": "UNMEASURED", "why": "ProbeRect read %d of %d cells, %d calls refused" % (len(stamp), sx * sz, bad)}))
        sys.exit(2)
    burned = set(c for c, b in stamp.items() if b >= 0 and now - b <= WINDOW)
    def B(x, z):
        return (x, z) in burned
    strands = [c for c in burned if (not B(c[0] - 1, c[1]) and not B(c[0] + 1, c[1]))
               or (not B(c[0], c[1] - 1) and not B(c[0], c[1] + 1))]
    hstrand = set(c for c in burned if not B(c[0], c[1] - 1) and not B(c[0], c[1] + 1))   # one cell thick across z
    longest, runs20 = 0, 0
    for z in range(sz):
        run = 0
        for x in range(sx + 1):
            if (x, z) in hstrand:
                run += 1
            else:
                longest = max(longest, run)
                runs20 += 1 if run >= 20 else 0
                run = 0
    share = len(strands) / float(max(1, len(burned)))
    try:
        from PIL import Image
        im = Image.new("RGB", (sx, sz), (60, 90, 40))
        for (x, z) in burned:
            im.putpixel((x, sz - 1 - z), (20, 20, 20))
        for (x, z) in strands:
            im.putpixel((x, sz - 1 - z), (230, 60, 30))
        im.resize((sx * 3, sz * 3)).save(os.path.join(OUT, "lanes_%s_mask.png" % SAVE))
    except Exception as e:   # the mask is a picture to look at, never the verdict
        print("mask not drawn: %r" % (e,))
    v = "PASS" if share <= LIMIT else "FAIL"
    res = {"verdict": v, "save": SAVE, "now": now, "window": WINDOW, "burned": len(burned), "strandCells": len(strands),
           "strandShare": round(share, 4), "limit": LIMIT, "longestOneCellRunAlongX": longest, "oneCellRunsAlongX_ge20": runs20}
    json.dump(res, open(os.path.join(OUT, "lanes_%s.json" % SAVE), "w"), indent=1)
    print(json.dumps(res))
    sys.exit(0 if v == "PASS" else 1)
