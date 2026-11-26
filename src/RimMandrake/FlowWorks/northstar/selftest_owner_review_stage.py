#!/usr/bin/env python3
"""Offline selftest of owner_review_stage.py: every failure a staging call can have must land in Stage.notes (never a silent
success), and each bars row frames its OWN rect. No game: FakeGame. Run: python3 <this file>"""
# selftest temp containment (BENCH, FLOWWORKS_SELFTESTS_FIX_TMPDIR_LEAKS): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_owner_review_stage_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fw_walk_common as C  # noqa: E402
import owner_review_stage as ORS  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


class A(object):
    mock = True
    no_shots = True
    mock_fail = None


class Bad(C.FakeGame):
    """Refuses excavation, build and proofs, answers nothing for spawn_batch."""
    def call(self, tool, **kw):
        if tool in ("jawa/flowworks_excavation_drive",):
            return {"success": False, "message": "refused"}
        if tool == "jawa/build_batch":
            return {"success": False, "failed": "nope"}
        if tool == "jawa/spawn_batch":
            return None
        if tool == "jawa/static_call":
            return {"success": True, "result": "REFUSED: no"}
        return C.FakeGame.call(self, tool, **kw)


def stage(game_cls):
    import tempfile
    w = C.make_walk(A(), tempfile.mkdtemp())
    w.B = game_cls()
    return ORS.Stage(w, False)


s = stage(Bad)
s.dig((100, 100), 2)
s.fill((100, 100), 1)
s.place("RM_Ladder", (101, 101), rot=0)
s.item("RM_ClimbingGear", (102, 102))
ok, _ = s.proof(ORS.SUSP, "ProofBuild", "1,1;5,1;rope;god")
s.store((103, 103))
n = " | ".join(s.notes)
check("refused dig is noted", "dig (100, 100)" in n, n)
check("refused fill is noted", "fill (100, 100)" in n, n)
check("a thing not on the map is noted", "place RM_Ladder" in n and "NOT on the map" in n, n)
check("empty spawn_batch reply is noted", "item RM_ClimbingGear" in n, n)
check("a REFUSED proof is noted and returns not-ok", (not ok) and "ProofBuild" in n, n)
check("a refused tank fill is noted", "tank at (103, 103) NOT filled" in n, n)
g = stage(C.FakeGame)
g.dig((100, 100), 2)
g.fill((100, 100), 1)
check("honest fake: no false notes from dig/fill", not g.notes, g.notes)
L = ORS.layout(100, 100)
rects = [ORS.bars_row_rect(L, r) for r in ORS.BARS_ROWS]
check("each bars row has its own rect", len(set(rects)) == len(ORS.BARS_ROWS), rects)
bx, bz, bw, bh = L["bars_rect"]
check("every bars row rect sits inside the bars site", all(bx <= r[0] and r[0] + r[2] <= bx + bw and bz <= r[1] and r[1] + r[3] <= bz + bh for r in rects), rects)
# WATER_LOOK_DIAGNOSE_GREY_ON_THE_ROT: the swatch verdict and the whole-row framing
check("good temperate water (83,93,97) reads as water", ORS.water_verdict([83, 93, 97]) is True)
check("can-fail: the grey Rot pit water (67,61,47) does not", ORS.water_verdict([67, 61, 47]) is False)
check("an unread picture is no verdict", ORS.water_verdict(None) is None and ORS.water_verdict([1, None, 3]) is None)
sw = ORS.swatch_rect(100, 100)
rx, rz, rw, rh = L["rect"]
check("the swatch sits inside the cleared site, clear of the ladders row (z >= 100)",
      rx <= sw[0] and sw[0] + sw[2] <= rx + rw and rz <= sw[1] and sw[1] + sw[3] <= 100, (sw, L["rect"]))
import water_scenes_walk as WSW  # noqa: E402
fr = WSW.fit_root_size((97, 131, 66, 12))
check("a 66-wide row is framed whole (16:9 view %.0f cells wide >= 70)" % (2 * fr * WSW.SCREEN_ASPECT), 2 * fr * WSW.SCREEN_ASPECT >= 70, fr)
check("a small rect never zooms below the engine floor 11 (the old rootSize 8 sat under it)", WSW.fit_root_size((0, 0, 3, 3)) == WSW.ROOT_FLOOR)
check("the 64x70 overview fits top to bottom", 2 * WSW.fit_root_size(L["rect"]) >= 74)
# REVIEW_STAGER_FIX_NUMBER_EVERY_STATION: every station numbered, its world label carries the number of its caption line,
# and the default rows are dense (the 2026-10-24 map spaced sprinkler nets 14 apart and bridges 13 apart, unnumbered).
import io  # noqa: E402
import contextlib  # noqa: E402


def dry_stage(rows):
    d = ORS.Stage(None, True)
    L = ORS.layout(100, 100)
    caps = {}
    with contextlib.redirect_stdout(io.StringIO()):
        for row in rows:
            if row == "gates":
                caps["gates_sluice"] = ORS.row_gates(d, L, "RM_Sluice", "gates_sluice", "WoodLog")
                caps["gates_grate"] = ORS.row_gates(d, L, "RM_SecurityGrateDoor", "gates_grate", "Steel")
            else:
                caps[row] = ORS.ROWS[row](d, L)
        ops = d.labels()
    return d, caps, ops


d, caps, ops = dry_stage(ORS.ALL_ROWS)
check("every default row registers stations", {st["row"] for st in d.stations} >= set(ORS.ALL_ROWS) - {"gates"} | {"gates_sluice", "gates_grate"},
      sorted({st["row"] for st in d.stations}))
check("stations numbered 1..N", [st["n"] for st in d.stations] == list(range(1, len(d.stations) + 1)))
lines = [c for row in caps.values() for c in (row if isinstance(row, list) else [])]
check("every caption line is numbered and matches the station list",
      lines == ["%d  %s" % (st["n"], st["text"]) for st in d.stations], lines[:4])
check("one world label per station, its text = the station's number",
      [o.split("|")[2] for o in ops] == [str(st["n"]) for st in d.stations], ops[:3])
check("every label is pinned on the row north of its station",
      all(tuple(map(int, o.split("|")[:2])) == ORS.station_label_cell(st) for o, st in zip(ops, d.stations)))
# RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_ELEVEN: walk_twins.py reads only sign books (reviewmap.sign_book); a save with
# number labels and no sign read COULD NOT LOOK (visit 4's save). One sign per station, key = its number, beside its label.
sops = ORS.station_sign_ops(d.stations) if hasattr(ORS, "station_sign_ops") else []
check("one sign book per station, title 'SIGN <n> <short>'",
      [o.split("|")[2].split(" - DO:")[0] for o in sops] == ["SIGN %d %s" % (st["n"], " ".join(st["short"].replace("|", "/").split())) for st in d.stations],
      sops[:2])
check("every sign sits on its station's label cell",
      len(sops) == len(d.stations) and all(tuple(map(int, o.split("|")[:2])) == ORS.station_label_cell(st) for o, st in zip(sops, d.stations)))
check("no sign name ends in AFTER or START (no station of this stager shows an aftermath)",
      sops and not any(o.split("|")[2].split(" - DO:")[0].split()[-1] in ("AFTER", "START") for o in sops))
probs = ORS.layout_problems(d.stations, rows=ORS.ALL_ROWS)
check("default rows are dense, no overlap, no label inside a station", not probs, probs[:6])
bars = [st for st in d.stations if st["row"] in ORS.BARS_ROWS]
check("every bars station sits inside its own row's camera rect",
      all(ORS._inside((st["rect"][0], st["rect"][1]), ORS.bars_row_rect(L, st["row"])) and
          ORS._inside((st["rect"][0] + st["rect"][2] - 1, st["rect"][1] + st["rect"][3]), ORS.bars_row_rect(L, st["row"]))
          for st in bars), [st for st in bars if not ORS._inside((st["rect"][0], st["rect"][1]), ORS.bars_row_rect(L, st["row"]))][:2])
br = [st for st in d.stations if st["row"] in ("bars_bridges", "bars_bridge_kinds") and "bridge" in st["text"] and not st["text"].startswith("concealed")]
check("every bridge spans a pit 3 wide (owner: 'see these bridges over pits')",
      br and all(st["rect"][3] == 3 and "over a 4 m pit" in st["text"] for st in br), [st["text"] for st in br][:3])
# can-fail: the old spacing (sprinkler nets 14 apart, bridges 13 apart) and an unnumbered row are caught
old = [dict(n=k + 1, row="sprinklers", lane=0, rect=(100 + 14 * k, 150, 6, 6), text="net", short="net") for k in range(4)]
check("can-fail: the old 14-apart sprinkler nets read as sparse", any("sparse" in p for p in ORS.layout_problems(old)))
old_tr = [dict(n=k + 1, row="bars_trench", lane=0, rect=(150 + 5 * k, 122, 10, 3), text="t", short="t") for k in range(2)]
check("can-fail: the old trench pitch (shooter inside the next station) reads as overlap",
      any("overlap" in p for p in ORS.layout_problems(old_tr)))
check("can-fail: numbering with a hole is caught",
      any("numbers" in p for p in ORS.layout_problems([dict(old[0]), dict(old[1], n=3)])))
h, hcaps, hops = dry_stage(("hoses", "picks"))
check("optional rows are numbered too (hoses scenes, picks)", len(hops) == len(h.stations) >= 10 and
      all(c.split("  ")[0].isdigit() for c in hcaps["hoses"]["lines"] + hcaps["picks"]), len(hops))
# REVIEW_STAGER_FIX_BARS_OFF_SMALL_MAP: the default origin must fit a 250 map; an off-map station is a failure, not a note.
fo = ORS.fit_origin(100, 100, (250, 250))
x0, z0, x1, z1 = ORS.site_extent(ORS.layout(*fo))
check("fit_origin puts the whole site on a 250x250 map", x0 >= 0 and z0 >= 0 and x1 <= 250 and z1 <= 250, (fo, (x0, z0, x1, z1)))
check("fit_origin leaves a map that already fits alone", ORS.fit_origin(20, 20, (400, 400)) == (20, 20))
try:
    ORS.fit_origin(100, 100, (150, 150))
    check("a map smaller than the site is refused", False)
except ValueError:
    check("a map smaller than the site is refused", True)
Lf = ORS.layout(*fo)
df = ORS.Stage(None, True)
with contextlib.redirect_stdout(io.StringIO()):
    for row in ORS.BARS_ROWS:
        ORS.ROWS[row](df, Lf)
check("fitted bars stations are all on the 250 map", not ORS.offmap_problems(df.stations, (250, 250)), ORS.offmap_problems(df.stations, (250, 250))[:2])
check("can-fail: the default origin 100,100 puts every bars station off a 250 map (old behaviour)",
      len(ORS.offmap_problems(bars, (250, 250))) >= 24 - 4 and ORS.offmap_problems(bars, (250, 250)), len(ORS.offmap_problems(bars, (250, 250))))
import subprocess  # noqa: E402
r = subprocess.run([sys.executable, os.path.join(HERE, "owner_review_stage.py"), "--dry-run", "--origin", "100,100"], capture_output=True, text=True)
check("an explicit origin that does not fit is refused (exit 4), nothing planned", r.returncode == 4 and "REFUSED" in r.stdout, (r.returncode, r.stdout[:200]))
r = subprocess.run([sys.executable, os.path.join(HERE, "owner_review_stage.py"), "--dry-run"], capture_output=True, text=True)
check("the default dry run fits the 250 map and succeeds", r.returncode == 0 and "origin moved" in r.stdout, (r.returncode, r.stdout[-200:]))
# REVIEW_STAGER_FIX_BRIDGE_LANES_SWAPPED: the caption's lane word must match the map (RimWorld z grows north)
brs = [st for st in d.stations if st["row"] == "bars_bridges" and "suspension" in st["text"]]
def zof(st): return st["rect"][1]
ok_lanes = True
for tier in ("rope", "timber", "steel", "heavy"):
    on = [st for st in brs if st["short"] == tier + " rails on"][0]
    off_ = [st for st in brs if st["short"] == tier + " rails off"][0]
    ok_lanes = ok_lanes and ("north lane" in on["text"] and "south lane" in off_["text"]) and zof(on) > zof(off_)
check("railings-on bridges sit NORTH (higher z) of the railings-off ones, as the captions say", ok_lanes, [(st["short"], st["rect"][1]) for st in brs][:4])
# RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD: every bridge and jetty kind also stands NORTH/SOUTH
# (owner 2026-11-22: "please next time draw some North/South bridges for me to study as well"), plus an unlit fire under a deck.
import re as _re  # noqa: E402
PROOF_RE = _re.compile(r"proof RM_(?:Suspension|FluidIdentity)Proofs?\.(Proof\w+)\((.*)\)$")


def ns_problems(plan):
    """[str] what the plan's north/south bridges lack (pure): a vertical twin of every kind, each jetty rooted on dry ground
    with its tip over the pit, and the fire station's chemfuel under its own deck with no fire started."""
    dug, builds, fills, probs = set(), [], [], []
    for ln in plan:
        ln = ln.strip()
        m = _re.match(r"dig \((\d+), (\d+)\) depth", ln)
        if m:
            dug.add((int(m.group(1)), int(m.group(2))))
            continue
        m = PROOF_RE.match(ln)
        if not m:
            continue
        meth, arg = m.groups()
        if meth == "ProofFillWithFluid":
            x, z, _, fl = arg.split(",")
            fills.append(((int(x), int(z)), fl))
            continue
        if meth not in ("ProofBuild", "ProofLook", "ProofJetty"):
            continue
        a = arg.split(";")
        if meth == "ProofLook":
            kind, c1, c2 = "look:" + a[0], a[1], a[2]
        else:
            c1, c2, kind = a[0], a[1], ("jetty:" if meth == "ProofJetty" else "") + a[2]
        (x1, z1), (x2, z2) = [tuple(map(int, c.split(","))) for c in (c1, c2)]
        builds.append((kind, (x1, z1), (x2, z2)))
    ns = [b for b in builds if b[1][0] == b[2][0] and b[1][1] != b[2][1]]
    want = {"rope", "timber", "steel", "heavy", "steelgrated", "heavygrated"} | {"look:" + l for l in ("Scrapper", "Industrial", "Modern", "Futuristic")}
    missing = want - {k for k, _, _ in ns}
    if missing:
        probs.append("no north/south twin of %s" % sorted(missing))
    for tier in ("steel", "heavy"):
        ways = set()
        for k, root, tip in ns:
            if k != "jetty:" + tier:
                continue
            if root in dug or tip not in dug:
                probs.append("%s jetty %s->%s: root must be dry ground and tip over the pit" % (tier, root, tip))
            ways.add("north" if tip[1] > root[1] else "south")
        if ways != {"north", "south"}:
            probs.append("%s jetty reaches only %s north/south" % (tier, sorted(ways)))
    fuel = [c for c, fl in fills if fl == "RM_Fluid_Chemfuel"]
    decks = [(r, t) for k, r, t in ns if k == "timber"]
    if not fuel or not any(all(c[0] == r[0] and min(r[1], t[1]) < c[1] < max(r[1], t[1]) and c in dug for c in fuel) for r, t in decks):
        probs.append("no chemfuel pit wholly under a north/south timber deck: fuel %s decks %s" % (fuel[:4], decks[:2]))
    if any("map_fire" in ln and "start" in ln and not ln.strip().startswith("station") for ln in plan):
        probs.append("the fire station is lit while staging; it must stay unlit")
    return probs


nsp = ns_problems(d.plan)
check("every bridge kind, look and jetty also stands north/south; jetties root on dry ground both ways; chemfuel under a timber deck",
      not nsp, nsp)
fire = [st for st in d.stations if st["row"] == "bars_bridges_ns" and st["text"].startswith("fire under a deck")]
check("the fire station is staged unlit and its caption names the call that lights it",
      len(fire) == 1 and "UNLIT" in fire[0]["text"] and "jawa/map_fire action=start" in fire[0]["text"], fire)
ns_st = [st for st in d.stations if st["row"] == "bars_bridges_ns"]
check("north/south stations are tall (3 wide, 6 long) and come after the older stations",
      ns_st and all(st["rect"][2:] == (3, 6) for st in ns_st) and min(st["n"] for st in ns_st) > max(
          st["n"] for st in d.stations if st["row"] != "bars_bridges_ns"), [(st["n"], st["rect"]) for st in ns_st][:3])
d0, _, _ = dry_stage(tuple(r for r in ORS.ALL_ROWS if r != "bars_bridges_ns"))
check("the stations of the earlier walks keep their numbers (1..%d unchanged)" % len(d0.stations),
      [(st["n"], st["text"]) for st in d0.stations] == [(st["n"], st["text"]) for st in d.stations[:len(d0.stations)]])
# can-fail: each fault is planted in the real plan and must read red
_bad_root = list(d.plan)
_j = [i for i, ln in enumerate(d.plan) if "ProofJetty" in ln and ";heavy;god" in ln][-1]
_m = PROOF_RE.match(d.plan[_j].strip()).group(2).split(";")
_bad_root[_j] = d.plan[_j].replace(_m[0] + ";" + _m[1], _m[1] + ";" + _m[0])      # root and tip swapped: root over the pit
check("can-fail: a jetty rooted over the pit reads red", any("root must be dry ground" in p for p in ns_problems(_bad_root)))
check("can-fail: a plan without the north/south row reads red", any("no north/south twin" in p for p in ns_problems(d0.plan)))
check("can-fail: a lit fire station reads red",
      any("unlit" in p for p in ns_problems(d.plan + ['  call jawa/map_fire action=start rect="1,1,1,4"'])))
check("can-fail: water, not chemfuel, in the fire pit reads red",
      any("chemfuel" in p for p in ns_problems([ln.replace(",RM_Fluid_Chemfuel", ",RM_Fluid_Water") for ln in d.plan])))


def _shift_fuel(ln):
    m = _re.search(r"ProofFillWithFluid\((\d+),", ln)
    return ln.replace(m.group(0), "ProofFillWithFluid(%d," % (int(m.group(1)) + 3)) if m else ln


check("can-fail: chemfuel beside, not under, the deck reads red", any("chemfuel" in p for p in ns_problems([_shift_fuel(ln) for ln in d.plan])))
# RIMMANDRAKE_FIX_FLOWWORKS_REVIEW_STAGER_NS_ROW_IN_EDGE_BAND_READ_AS_BUILT. Range swept: square and oblong maps 200..400
# (every vanilla size and the 250 quicktest) x requested origins over the whole map and off it; a site that fits is read
# station by station with the band check, a site that cannot fit must be refused; and --only subsets (each row alone, the
# default sweep, every row, live_session B9's list), since the fit reads only the rects of the rows that run. Left out:
# seeds, settings and time (the layout is pure geometry of the origin and the map size; nothing else moves a station).
def _plan_stations(origin, rows=None):
    st = ORS.Stage(None, True)
    with contextlib.redirect_stdout(io.StringIO()):
        Lx = ORS.layout(*origin)
        for row in rows or ORS.ALL_ROWS + ORS.OPT_ROWS:
            if row == "gates":
                ORS.row_gates(st, Lx, "RM_Sluice", "gates_sluice", "WoodLog")
                ORS.row_gates(st, Lx, "RM_SecurityGrateDoor", "gates_grate", "Steel")
            else:
                ORS.ROWS[row](st, Lx)
    return st.stations


_cases = _bad = _refused = _nst = 0
_worst = None
B9_ROWS = ["ladders", "spikes", "gates", "shallows", "sprinklers", "hoses", "bars_joint", "bars_dry", "bars_trench", "bars_access",
           "bars_bridges"]          # live_session.py B9's --only list
SUBSETS = [None, list(ORS.ALL_ROWS), B9_ROWS] + [[r] for r in ORS.ALL_ROWS + ORS.OPT_ROWS]
for W in (200, 225, 250, 275, 300, 325, 350, 400):
    for H in (200, 250, 300, 400):
        for req in ((100, 100), (0, 0), (W, H), (W // 2, 5), (5, H // 2), (-50, 500)):
          for rows in SUBSETS:
            try:
                fo = ORS.fit_origin(req[0], req[1], (W, H), rows=rows)
            except ValueError:
                _refused += 1
                continue
            _cases += 1
            sts = _plan_stations(fo, rows)
            _nst += len(sts)
            if not sts:
                _bad += 1
                continue
            probs = ORS.edgeband_problems(sts, (W, H)) + ORS.offmap_problems(sts, (W, H))
            gap = min(min(r[0], r[1], W - r[0] - r[2], H - r[1] - r[3]) for r in (x["rect"] for x in sts))
            _worst = gap if _worst is None else min(_worst, gap)
            if probs:
                _bad += 1
                print("   band case %s req %s rows %s -> %s: %s" % ((W, H), req, rows and rows[:3], fo, probs[:2]))
print("   edge sweep: %d fitted cases read (%d stations), %d refused (site wider than map less the band), worst station gap to an edge %s "
      "(limit %d), %d in the band" % (_cases, _nst, _refused, _worst, ORS.NO_BUILD_EDGE, _bad))
check("every fitted station on every map size stays out of the no-build edge band", _cases > 100 and _bad == 0 and
      _worst >= ORS.NO_BUILD_EDGE, (_cases, _bad, _worst))
check("a 250 map still fits the whole default site", ORS.fit_origin(100, 100, (250, 250)) is not None)
import live_session as _LS  # noqa: E402
_z = _LS.plan_zones((250, 250))["owner"]
_b9 = (_z[0] + 3, _z[1] + 5)
check("live_session B9's explicit origin still fits its rows unmoved on a 250 map (it would be refused)",
      ORS.fit_origin(_b9[0], _b9[1], (250, 250), rows=B9_ROWS) == _b9, (_b9, ORS.fit_origin(_b9[0], _b9[1], (250, 250), rows=B9_ROWS)))
r = subprocess.run([sys.executable, os.path.join(HERE, "owner_review_stage.py"), "--dry-run", "--origin", "%d,%d" % _b9,
                    "--only", ",".join(B9_ROWS)], capture_output=True, text=True)
check("live_session B9's argv dry-runs on the 250 map unmoved (main fits the rows it runs)",
      r.returncode == 0 and "origin moved" not in r.stdout, (r.returncode, r.stdout[-300:]))
_old = ORS.FIT_MARGIN
try:            # can-fail: the old margin of 2 reproduces visit 11 (stations in the band on the 250 quicktest)
    import inspect
    _src = inspect.signature(ORS.fit_origin).parameters["margin"].default
    _vis = _plan_stations(ORS.fit_origin(100, 100, (250, 250), margin=2))
    _hit = ORS.edgeband_problems(_vis, (250, 250))
    _ns_hit = [p for p in _hit if any(st["n"] == int(p.split()[1]) and st["row"] == "bars_bridges_ns" for st in _vis)]
    check("can-fail: the old margin 2 puts bars_bridges_ns stations in the band on a 250 map (visit 11)", len(_ns_hit) >= 3, _hit[:4])
    check("fit_origin's default margin is the no-build edge", _src == ORS.NO_BUILD_EDGE, _src)
finally:
    ORS.FIT_MARGIN = _old
VISIT11 = "BUILD ok=False anchors=0 decks=0 blueprints=0 records=0 reason=Anchor: Too close to map edge."
check("visit 11's ProofBuild reply reads as a failure", ORS.proof_failed(VISIT11))
for bad in ("REFUSED: arg must be x,z", "JETTY ok=False anchors=0 decks=0 blueprints=0 railed=0 reason=x", "RAILS none",
            "LOOK look=Modern parts=0 reason=Too close to map edge."):
    check("a not-built reply reads as a failure: %s" % bad[:30], ORS.proof_failed(bad))
for good in ("BUILD ok=True anchors=2 decks=4 blueprints=0 records=1 reason=-", "JETTY ok=True anchors=1 decks=2 blueprints=0 railed=2",
             "RAILS on=True railed=6", "LOOK look=Modern parts=6 styled=6 pink=0 paths=a", "FILLED (1, 2, 3) W=10000dL fluid=RM_Fluid_Chemfuel",
             "", None):
    check("a built reply is not a failure: %r" % (good,)[:40], not ORS.proof_failed(good))


class EdgeRefuses(C.FakeGame):
    """Answers static_call the way the live game did on visit 11: success=true, the verdict ok=False in the text."""
    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            return {"success": True, "result": VISIT11}
        return C.FakeGame.call(self, tool, **kw)


e = stage(EdgeRefuses)
ok, _ = e.proof(ORS.SUSP, "ProofBuild", "240,151;240,156;rope;god")
check("Stage.proof returns not-ok and notes a 'BUILD ok=False' reply", (not ok) and any("Too close to map edge" in n for n in e.notes), e.notes)


# RIMMANDRAKE_TRACE_FLOWWORKS_TWO_NOTCH_STRIP_READS_FIVE_THOUSAND_LITRES: station 17 "0.2 m" read 0.5 m and 1,000 L on all five
# squares on visits 2, 4 and 11 (owner, 2026-11-20: "the 0.2m still shows 0.5m depth upon hover over"). The mod was right:
# flowworks_excavation_drive's setBodyWaterM sets the WHOLE connected dug body (RM_MapComponent_Excavation.TrySetBodyWaterM),
# so "fill square 0 with 1 notch" filled all five squares to 0.5 m. The shared FakeGame writes one square, so the mock never
# showed it. BodyFake mirrors TrySetBodyWaterM: one level surface `metres` above the body's deepest floor, clamped to each brim.
class BodyFake(C.FakeGame):
    U = 10000                        # RM_LevelSolve.U: decilitres in one 0.5 m notch of one square (1,000 L)
    ROUND_TO_NOTCH = False           # planted fault: a driver that can only set whole notches

    def __init__(self):
        C.FakeGame.__init__(self)
        self.dl = {}

    def _body(self, seed):
        body, seen = [seed], {seed}
        for c in body:
            for dx, dz in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                n = (c[0] + dx, c[1] + dz)
                if self.depth.get(n, 0) > 0 and n not in seen:
                    seen.add(n)
                    body.append(n)
        return body

    def call(self, tool, **kw):
        if tool == "jawa/flowworks_excavation_drive":
            c = (kw["x"], kw["z"])
            self.depth[c] = self.depth.get(c, 0) + int(kw.get("deepenLevels") or 0)
            m = float(kw.get("setBodyWaterM", -1))
            if m >= 0 and self.depth.get(c, 0) > 0:
                if self.ROUND_TO_NOTCH:
                    m = round(m / 0.5) * 0.5
                body = self._body(c)
                deepest = max(self.depth[b] for b in body)
                surface = int(round(m / (0.5 / self.U)))
                for b in body:
                    self.dl[b] = max(0, min(self.depth[b] * self.U, surface - (deepest - self.depth[b]) * self.U))
            return {"success": True}
        return C.FakeGame.call(self, tool, **kw)

    def _static(self, typ, method, arg):
        if method == "ProofReadout":
            c = tuple(int(v) for v in arg.split(","))
            if self.depth.get(c, 0) == 0:
                return {"success": True, "result": "OK -"}
            dl = self.dl.get(c, 0)
            return {"success": True, "result": "OK Hole %.1f m · Water %.2f m (%s L)" % (
                self.depth[c] * 0.5, dl * 0.5 / self.U, "{:,}".format(dl // 10))}
        return C.FakeGame._static(self, typ, method, arg)


def shallows_strip(game_cls):
    s = stage(game_cls)
    L = ORS.layout(100, 100)
    with contextlib.redirect_stdout(io.StringIO()):
        ORS.row_shallows(s, L)
    ox, oz = L["shallows"]
    reads = [WSW.parse_readout(s.w.B._static(WSW.NSP, "ProofReadout", "%d,%d" % (ox + i, oz + 1))["result"]) for i in range(5)]
    return s, reads


b, reads = shallows_strip(BodyFake)
print("  station 17 on BodyFake: water_m %s, litres %s (total %d L; the sign: 0.2 m on 5 squares = 2,000 L)" % (
    [r["water_m"] for r in reads], [r["litres"] for r in reads], sum(r["litres"] for r in reads)))
check("station 17 '0.2 m': every strip square reads 0.2 m of water in a 0.5 m hole (per-body fill, as the bridge does it)",
      all(r and r["water_m"] == 0.2 and r["hole_m"] == 0.5 for r in reads), reads)
check("station 17 holds the 2,000 L its sign stands for, not 5,000 L", sum(r["litres"] for r in reads) == 2000, reads)
check("station 17 staged as signed: no NOT AS SIGNED note", not any("NOT AS SIGNED" in n for n in b.notes), b.notes)


class NotchOnly(BodyFake):
    ROUND_TO_NOTCH = True


b2, _ = shallows_strip(NotchOnly)
check("can-fail: a driver that rounds to whole notches leaves station 17 NOT AS SIGNED in the notes",
      any("0.2 m strip NOT AS SIGNED" in n for n in b2.notes), b2.notes)
# Review-stage swimmers (Steve2 job J20261124T165357Z-e3c928, 2026-11-24): bars_joint spawned its
# drafted swimmers (2 m and 1 m of water in 4 m holes) before FINISH stepped the clock up to 12 x 2000 ticks toward midday;
# a swimmer who cannot climb a 4 m wall tires and drowns by the mod's own swim rule, and the governor stopped the run on
# "died: RM_PitDrowning". The swimmers go in after the last clock step, so no tick runs with a staged swimmer in the water.
_RealFake = C.FakeGame


class Clocked(_RealFake):
    """Records the order of pawn spawns and clock steps; its clock starts at midnight so FINISH must step."""
    def __init__(self):
        _RealFake.__init__(self)
        self.order = []

    def call(self, tool, **kw):
        if tool == "jawa/spawn_pawn":
            self.order.append(("spawn", (kw.get("x"), kw.get("z"))))
        elif tool == "rimworld/step_game_ticks":
            self.order.append(("ticks", kw.get("ticks")))
        elif tool == "jawa/time_clock":
            return {"success": True, "ticksAbs": self.tick}
        return _RealFake.call(self, tool, **kw)

    def ticks(self, n):
        self.order.append(("ticks", n))
        return _RealFake.ticks(self, n)


def swimmer_order():
    games = []
    real = C.FakeGame

    def make():
        g = Clocked()
        games.append(g)
        return g
    C.FakeGame = make
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            ORS.main(["--mock", "--only", "bars_joint", "--no-save", "--no-shots"])
    finally:
        C.FakeGame = real
    return games[-1].order


order = swimmer_order()
ticks_at = [i for i, o in enumerate(order) if o[0] == "ticks"]
spawn_at = [i for i, o in enumerate(order) if o[0] == "spawn"]
check("bars_joint staged its two swimmers (mock)", len(spawn_at) >= 2, order)
check("the clock stepped toward midday (mock, clock at midnight)", bool(ticks_at), order)
check("no clock step runs after a swimmer is in the water (a 4 m hole drowns a tired swimmer)",
      bool(spawn_at) and bool(ticks_at) and min(spawn_at) > max(ticks_at), order)


print("selftest_owner_review_stage: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
