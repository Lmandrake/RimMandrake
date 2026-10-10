"""run_live.py -- the LIVE Northstar scene-matrix runner for Gimme Some Slack (phase-2 design section 4.4).

    python3    src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py --mock            # offline: placement through fakegame
    python.exe src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py --live --fresh-map  # gimmesomeslack tier, one batched session
    python3    src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py --post <result.json>   # contact sheets, image sanity, review.html
    python3    src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py --compare A.json B.json  # determinism across runs

FAST (owner 2026-10-04, 'we MUST accelerate this test time'): screenshots dominate the ~20 s/scene (frame/camera move, settle sleep,
render, 2-3 MB PNG copy). Split the run in two; the state pass carries every verdict, the sweep only produces the pictures:
    python.exe src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py --live --fresh-map --no-shots --catalog <scenes.json> --out <result.json>
    python.exe src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py --live --sweep-shots <result.json> --catalog <scenes.json>
    python3    src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py --post <result.json>
  --no-shots   state pass with the render skipped: no screenshot_cell_rect / take_screenshot call, no PNG copy. Every camera move,
               settle wait, selection, on/off toggle and view staging is KEPT, because the cord graph rebuilds off camera-driven
               section regeneration (RM_MapComponent_CordGraph: Rebuild runs from an on-screen SectionLayer regenerate or the
               StaleOffscreen flag) and a first cut that also dropped the camera moves failed scenes the full run passed (live,
               2026-10-04: F17_T4_S1, F49_T12_S1, F34_T8_S2, D12_n1000_S0, highlight rows). Screenshot-dependent checks are the single
               row I0_screenshots = SKIP with the reason (a deliberate choice, not a failure to measure). Prove equivalence by --compare against a full run on the same spec.
  --sweep-shots <result.json>  second pass on a live 250x250 map with the site pinned (same --catalog; do NOT pass --fresh-map unless a
               fresh map is intended). Every board is laid out from the SAME origin and destroyed after its census, so nothing from the
               state pass is still standing: the sweep rebuilds each board (same builds, same ticks, so the same geometry), then takes
               that board's shots in plot order (south to north) with no census, no determinism re-reads, no verdict rows, then
               destroys it. Shot records (shot / shot_on / shot_off) are merged into <result.json> (or --out); verdicts are untouched.
               --shot-settle S (default 1.5 for a full run, 0.7 in the sweep) is the wait after a frame move before a frame capture;
               raise it if sweep frames come out blurred or mid-pan. PNG copies run on 4 threads, overlapping the bridge calls.
  --profile    per bridge call name / probe verb: count, total s, avg s in result["timing"]["calls_profile"] and printed (top 25).
  --probe-poll S  seconds between serial polls of a probe (default 0.25; 0.05 was tried and is not proven safe).
  Timing: result["timing"] = wall seconds per phase (site_setup, board_build, board_ticks, scene_probes, determinism, shots,
  shot_copy_wait, hose, teardown, post; shots are nested out of the phase they ran in), per board in boards[].phases_s, printed
  at the end as a TIMING line.

Run python.exe from the repo root with repo-relative paths (bridge calls only work under python.exe; pipe its output
through tr -d '\\r'). --post runs under WSL python3 (numpy/PIL).

What it does (one cold load, one fresh quicktest map):
  1. Catalog: design_spec.build_spec() (109 scenes; the 9 hose scenes are placed after the boards, step 3b). --catalog matrix
     falls back to matrix.py's 84-case complement (converted to the same spec shape).
  2. Site: fresh map, weather Clear locked, clock pinned to noon (time_set_ticks: a scrub, nothing simulated),
     incident queue cleared, non-colonists destroyed, the board REGION (south band, away from the colonists at the
     centre) cleared, Soil, unfogged, unroofed. Scenes are grouped into BOARDS by settings tuple (settings are global)
     and shelf-packed into REGION with GAP cells between plots. GAP = 2*R + 2 where R is the cords' lateral reach,
     read from CordLayer.cs (Cap * 1.1 excursion + Cap/1.6 loop + Wobble, rounded up): sprawlCap is extra LENGTH,
     never lateral reach, so it does not enter R. Connectors wire within 6 cells (PowerConnectionMaker), < GAP.
  3. Per board: probe defaults + the board's settings; one batched build per op type in placer order (terrain,
     Granite, walls, doors, conduit, waterproof conduit, transmitters, connectors, trees); batteries resolved by
     position and set; aerial masts linked by id through AerialProbe (autoLink OFF so no cross-scene link), cut by
     `cut:` and killed by `kill:` (staging ops; the behaviour is validation_aerial.py M14/M15), 30 ticks; 2 ticks for
     nets; poll.
  3b. Hose scenes (MX_H00..H08): reel built by build_batch (RM_HoseReel), then the HoseProbe verbs validation_hose.py proved
     live (12/12 PASS): `check:` (install validity), `lay:`, `flow:x,z=on` (Plump: transitionTicks+5 ticks; Filling50: half a
     transition), a census read of that reel compared with the scene's intrinsic row (state, blend, visible width, width over
     wire >= 4, bend >= 0.95 x setting, no self-intersection, no unwalkable point, couplings). placer.hose_plan emits the calls.
  4. Per scene: GimmeSomeSlackProbe `rect:x,z,w,h` (added for this runner: nodes, edges, strands, ends, nets,
     per-edge + scene geometry hash, strand bbox, laid polylines) compared with expect.intrinsic: counts,
     connectivity, live flags, bounds (strands within [cords_min, cords_max]), sprawl inside plot + R.
     A mismatch is SITE when the scene did not build as specified, HARNESS when a read failed, else MOD.
  5. Screenshot per scene: screenshot_cell_rect (plot + 1 pad, the scene's zoom root) or, for views drawn per frame
     (net selected, power overlay, aerial spans), frame_cell_rect + jawa/take_screenshot with screenshot_mode on.
     Mod-on/off pairs for a handful of scenes via the master switch.
  6. Determinism: the zero-tick rect census re-read twice after all view toggles; the `fresh` builder per board;
     --compare A B across runs/maps.
  7. Result JSON in ../northstar/ (excluded from the mod hash) with a ticks/wall-time table; `modcheck record`.

LEARNED (2026-10-02, smoke + two full passes on two fresh maps, 100 placed scenes each, 71 ticks, ~26 min):
  * HARNESS: python.exe has no numpy, and the oracle imports the numpy mock-up -> the live run reads the spec JSON
    written by `design_spec.py --out` (--catalog <json>); only --mock/--post import the oracle.
  * HARNESS: jawa/list_things returns x/z at top level (no `position`); the first smoke charged NO battery.
  * HARNESS: jawa/time_clock has no hour; local hour = (ticksAbs + round(longitude/360*60000)) % 60000 // 2500,
    pinned to noon with time_set_ticks (pass 1 map started at 06:00).
  * HARNESS: screenshot_cell_rect with rootSize ignores the rect (wide frame, scene small and off-centre): the
    cell-rect capture takes no rootSize. 4 of 100 cell-rect calls returned success=false with no file (pass 2:
    F54, F23, F40, F57) -- the tool, not the scene; the state verdicts stand.
  * HARNESS (oracle): a wall/rock terminal adds one OverFace hanging-tail strand (CordBuilder l.488) that the
    per-edge strand bound never counted (pass 1 F48/F52 tidy: 5 strands vs [4,4]); bound is now + wall_terminals.
  * HARNESS (comparator): a CUT span is stored as two FallenCord entries (design 2.6, two downed wires), so the
    census `fallen` count is downed + fallen ends (pass 1: all 6 cut scenes read 2 vs 0).
  * SITE: destroy_batch All over the region logs "Tried to destroy non-destroyable thing SteamGeyser/VoidMonolith"
    (red errors that are the runner's clear, excluded from Z_log_budget and counted). Pass 2's map spawned 3
    colonists inside REGION (L6 FAIL); 2 + 30 ticks never let them disturb a plot (every scene still PASS).
  * RESOLVED first-run unknowns: WaterproofConduit builds on WaterDeep via build_batch (canal T15 scenes PASS,
    stub_water nodes read); an unfuelled WoodFiredGenerator censuses as `source` while the battery makes the net
    live (device_attached T10 PASS); no scene in the 109 needs a switch OFF (every PowerSwitch is on), so no
    flick tool was needed. Aerial masts auto-linked across scenes would be a SITE hazard: autoLink is set OFF and
    spans are linked by id through AerialProbe.
  * Board pitch: R = 5 (Cap 2.6 from CordLayer.cs), GAP 12; no strand bbox ever exceeded plot + R.
  * MOD (D2_fresh_builder_same, reproduced on both maps): on every board holding the RING topology (T3, 4 boards)
    a fresh CordBuilder on the same map lays ONE edge differently from the incrementally built piece
    (isolated: F12_T3_S0 alone -> fresh edges 6, different 1; F28/F44/F60 alone -> 0). The aerial board misses one
    edge in fresh (18 scenes together; A02/A06 alone -> 0): not isolated. The laid state itself is stable: the
    zero-tick re-reads match 99/99, and pass 1 vs pass 2 (two maps, same origins) give identical geometry hashes
    and census for all 99 comparable scenes.
  * Image tripwires: the census mask PASSes 26 of 35 cell-rect frames; it FAILs on 1-cell density plots (the mask
    lies on the bright battery) and on F06/F09/F34/F37, reads NO_WIRES on the empty control, and FAILs the planted
    negative (ON-census mask over the master-off frame) as it must. Frame captures (selected/overlay/aerial, 60)
    have no cell->pixel transform: UNMEASURED.
"""
import argparse
import collections
import concurrent.futures
import contextlib
import glob
import hashlib
import json
import math
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MODDIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
for p in (HERE, MODDIR):
    if p not in sys.path:
        sys.path.insert(0, p)
try:                                   # numpy-free: the scene -> bridge-call plans (python.exe can import it)
    import placer as PL  # noqa: E402
except ImportError:
    PL = None
try:                                   # numpy-backed (the nodal mock-up); python.exe has no numpy -> --spec JSON
    import design_spec as D  # noqa: E402
    import oracle as O  # noqa: E402
    import scenes as S  # noqa: E402
except ImportError:
    D = O = S = None

OUT_DIR = os.path.join(REPO, "Transient", "mc_matrix_live_20261002")
SHOTS = os.path.join(OUT_DIR, "shots")
RESULT_DIR = os.path.join(MODDIR, "northstar")
PROBE = "RimMandrake.GimmeSomeSlack.GimmeSomeSlackProbe"
APROBE = "RimMandrake.GimmeSomeSlack.Aerial.AerialProbe"
HPROBE = "RimMandrake.GimmeSomeSlack.Hose.HoseProbe"
HOSE_PITCH = 3                         # cells between hose plots (hoses never reach sideways; walls/water are per plot)
PKG = "mandrake.rm.gimmesomeslack"
MAP_W = 250
REGION = (12, 12, 226, 100)             # x, z, w, h: south band; quicktest colonists stand near (125,125)
PAD = 1
TRANSMITTERS = ("Battery", "WoodFiredGenerator", "PowerSwitch", "RM_AerialMast")
CONNECTORS = ("Heater", "ElectricSmelter", "StandingLamp")
ONOFF_PAIRS = ("F01_T0_S1", "F05_T1_S1", "F29_T7_S1", "F49_T12_S1", "F53_T13_S1", "D06_n10_S2")
FRAME_VIEWS = ("selected", "overlay")
PROBE_POLL_S = 0.25                    # --probe-poll; 0.05 was tried 2026-10-04 and is NOT proven safe (see docstring)


# ============================================================================ geometry of the board
def lateral_reach():
    """R: how far a laid cord can stray sideways from its planned path, cells, read from the mod's own source."""
    src = open(os.path.join(MODDIR, "Source", "Core", "CordLayer.cs"), encoding="utf-8").read()
    cap = float(re.search(r"public double Cap = ([\d.]+);", src).group(1))
    wob = float(re.search(r"Wobble = ([\d.]+);", src).group(1))
    reach = cap * 1.1 + cap / 1.6 + wob          # excursion amp <= cap * kAmp(1.1); knot loop r <= 0.5*cap/1.6 (diameter)
    return int(math.ceil(reach)), {"Cap": cap, "Wobble": wob, "reach_cells": round(reach, 3)}


R_REACH, R_SRC = lateral_reach()
GAP = 2 * R_REACH + 2


def settings_key(sc):
    return json.dumps(sc.get("settings") or {}, sort_keys=True)


def make_boards(scenes, region=REGION, gap=GAP):
    groups = collections.OrderedDict()
    for sc in scenes:
        if sc["group"] == "hose":
            continue
        if sc["group"] == "controls":
            key = ("controls", sc["id"])
        elif sc["group"] == "aerial":
            key = ("aerial", settings_key(sc))
        else:
            key = ("ground", settings_key(sc))
        groups.setdefault(key, []).append(sc)
    rx, rz, rw, rh = region
    boards = []
    for key, scs in groups.items():
        pending = sorted(scs, key=lambda s: (-s["plot"][3], s["id"]))
        while pending:
            placed, rest = [], []
            x, z, row_h = rx, rz, 0
            for sc in pending:
                w, h = sc["plot"][2], sc["plot"][3]
                if x + w > rx + rw:
                    x, z, row_h = rx, z + row_h + gap, 0
                if z + h > rz + rh or w > rw:
                    rest.append(sc)
                    continue
                placed.append((sc, (x, z)))
                x += w + gap
                row_h = max(row_h, h)
            if not placed:
                raise SystemExit("scene %s does not fit the region %s" % (pending[0]["id"], region))
            boards.append({"key": list(key), "settings": json.loads(key[1]) if key[0] != "controls" else
                           (placed[0][0].get("settings") or {}), "scenes": placed})
            pending = rest
    for k, b in enumerate(boards):
        b["id"] = "B%02d_%s" % (k, b["key"][0])
        xs = [o[0] for _, o in b["scenes"]] + [o[0] + s["plot"][2] for s, o in b["scenes"]]
        zs = [o[1] for _, o in b["scenes"]] + [o[1] + s["plot"][3] for s, o in b["scenes"]]
        b["bbox"] = [min(xs) - PAD - 1, min(zs) - PAD - 1, max(xs) - min(xs) + 2 * PAD + 2, max(zs) - min(zs) + 2 * PAD + 2]
    return boards


def board_overlap_check(boards):
    """Every pair of plots on a board is >= GAP apart (no cord can reach a neighbour: reach R each side)."""
    bad = []
    for b in boards:
        rects = [(s["id"], o[0], o[1], s["plot"][2], s["plot"][3]) for s, o in b["scenes"]]
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, c = rects[i], rects[j]
                dx = max(c[1] - (a[1] + a[3]), a[1] - (c[1] + c[3]))
                dz = max(c[2] - (a[2] + a[4]), a[2] - (c[2] + c[4]))
                if max(dx, dz) < GAP:
                    bad.append((b["id"], a[0], c[0], dx, dz))
    return bad


# ============================================================================ catalog
def load_catalog(which="design"):
    if which.endswith(".json"):
        return json.load(open(which, encoding="utf-8"))
    if which == "design":
        spec = D.build_spec()
        gaps = {g: p["missing"] for g, p in spec["pair_proofs"].items() if p["missing"]}
        if gaps:
            raise SystemExit("design catalog has a pair gap: %s" % gaps)
        return spec
    import matrix as MX
    cat = MX.build_catalog() if hasattr(MX, "build_catalog") else None
    if not cat:
        raise SystemExit("matrix.py fallback: no build_catalog() in this matrix.py")
    scenes = []
    for c in cat["cases"]:
        sc, case = c["scene"], c["case"]
        lv = O.LEVELS[case["tangle"]]
        settings = {"slack": str(lv["slack"]), "sprawlCap": str(lv["sprawlCap"]), "cordsPerConnection": str(lv["cordsPerConnection"]),
                    "tangles": "True", "style": "CordStyle." + {"jawa": "StarWarsJawa", "extcord": "ExtensionCord",
                                                                 "cybertek": "Cybertek", "starwars": "StarWars"}[case["style"]]}
        e = O.expect(sc, case["tangle"])
        scenes.append({"id": case["case"], "group": "matrix", "factors": case, "plot": [0, 0, sc["w"], sc["h"]], "zoom_root": 11,
                       "settings": settings, "build": D.build_ops(sc), "view": {"overlay": "none", "select_at": None},
                       "expect": {"intrinsic": D.intrinsic(sc, "ropey", "normal")}, "shows": [], "notes": [],
                       "_cords_max": lv["cordsPerConnection"] * e["cord_edges"]})
    return {"spec_version": 1, "generator": "matrix.py", "spec_hash": cat.get("hash"), "scenes": scenes}


# ============================================================================ bridges
class LiveBridge(object):
    def __init__(self):
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
        import rimbridge_client as rb  # noqa: E402
        host, port, token = rb.resolve_endpoint()
        self.S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        self.S.connect()
        self.n = 0

    def call(self, tool, **kw):
        self.n += 1
        r = self.S.call(tool, kw, check=False) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:  # noqa: BLE001
                pass
        return r if isinstance(r, dict) else {"success": False, "raw": r}

    def _probe(self, typ, cmd, wait_s=30.0):
        before = self.call("jawa/mod_settings_field", typeName=typ, action="get", field="serial").get("value")
        s = self.call("jawa/mod_settings_field", typeName=typ, action="set", field="request", value=cmd)
        if not s.get("success"):
            return {"success": False, "error": "probe set failed", "raw": s}
        t0 = time.time()
        while time.time() - t0 < wait_s:
            now = self.call("jawa/mod_settings_field", typeName=typ, action="get", field="serial").get("value")
            if now != before:
                res = self.call("jawa/mod_settings_field", typeName=typ, action="get", field="result").get("value")
                try:
                    return json.loads(res)
                except Exception:  # noqa: BLE001
                    return {"success": False, "raw": str(res)[:300]}
            time.sleep(PROBE_POLL_S)
        return {"success": False, "error": "probe timed out (no frame serviced it)", "cmd": cmd}

    def probe(self, cmd, wait_s=30.0):
        return self._probe(PROBE, cmd, wait_s)

    def ap(self, cmd, wait_s=30.0):
        return self._probe(APROBE, cmd, wait_s)

    def hp(self, cmd, wait_s=20.0):
        """HoseProbe, same request/serial/result protocol as validation_hose.py H.hp."""
        return self._probe(HPROBE, cmd, wait_s)

    def ticks(self, n):
        return self.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=180000)

    def sleep(self, s):
        time.sleep(s)


class MockBridge(object):
    """Offline stand-in: builds land in fakegame.FakeMap (its PowerConnectionMaker emulation decides every hookup);
    `rect:` answers from the oracle run on what was BUILT inside the rect, so a wrong coordinate transform, build
    order or board overlap shows up as a mismatch. Masts are not modelled (aerial scenes read MOCK_SKIP)."""

    def __init__(self, fault=None):
        import fakegame as FG
        self.FG = FG
        self.m = FG.FakeMap()
        self.n = 0
        self.fault = fault
        self.ticks_game = 1000
        self.settings = {}

    def sleep(self, s):
        pass

    def call(self, tool, **kw):
        self.n += 1
        if tool == "jawa/build_batch":
            ok, failed = 0, []
            for op in kw["ops"].split(";"):
                name, rest = op.split(":")
                if name == "RM_AerialMast":
                    failed.append(op + " (mock: masts not modelled)")
                    continue
                n = [int(v) for v in rest.split(",")]
                if name == self.FG.REEL:
                    self.m.tool(tool, {"ops": op}, {})
                    ok += 1
                    continue
                if self.fault == "flip_z" and name == "PowerConduit":
                    n[1] = n[1] + 1
                c = (n[0], n[1])
                if name in self.FG.CONDUITS:
                    self.m.conduit.add(c)
                elif name in ("Wall", "Door", "Granite"):
                    self.m.edifice[c] = name
                else:
                    self.m.spawn(name, c, n[2] if len(n) > 2 else 0)
                ok += 1
            return {"success": True, "survived": ok, "failed": failed}
        if tool == "jawa/destroy_batch":
            self.m.tool(tool, kw, {})
            return {"success": True}
        if tool == "jawa/set_terrain_batch":
            for op in kw["ops"].split(";"):
                name, rest = op.split(":")
                x, z, w, h = [int(v) for v in rest.split(",")]
                for i in range(x, x + w):
                    for j in range(z, z + h):
                        self.m.terrain[(i, j)] = name
            return {"success": True}
        if tool == "jawa/set_plants":
            for op in kw["ops"].split(";"):
                name, rest = op.split(":")
                n = [int(v) for v in rest.split(",")]
                self.m.plants.add((n[0], n[1]))
            return {"success": True}
        if tool == "jawa/list_things":
            x, z, w, h = [int(v) for v in kw["rect"].split(",")]
            return {"success": True, "things": [{"id": t["id"], "def": t["def"], "position": {"x": t["pos"][0], "z": t["pos"][1]}}
                                               for t in self.m.things if t["def"] == kw.get("defName")
                                               and x <= t["pos"][0] < x + w and z <= t["pos"][1] < z + h]}
        if tool == "jawa/battery_set":
            for t in self.m.things:
                if t["id"] == kw["thing"]:
                    t["charged"] = float(kw["value"]) > 0
            return {"success": True, "storedEnergyAfter": 600.0 * float(kw["value"])}
        if tool == "rimworld/step_game_ticks":
            self.ticks_game += kw.get("ticks", 0)
            self.m.hose_tick(int(kw.get("ticks", 0)))
            return {"success": True}
        if tool in ("rimworld/screenshot_cell_rect", "jawa/take_screenshot"):
            return {"success": True, "path": None}
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": MAP_W, "sizeZ": MAP_W}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": []}
        return {"success": True}

    def ticks(self, n):
        return self.call("rimworld/step_game_ticks", ticks=n)

    def ap(self, cmd, wait_s=0):
        return {"success": True, "cmd": cmd, "anchors": [], "mock": True}

    def hp(self, cmd, wait_s=0):
        return self.m.hose_probe(cmd)

    def probe(self, cmd, wait_s=0):
        if cmd.startswith("set:"):
            k, v = cmd[4:].split("=", 1)
            self.settings[k] = v
            return {"success": True}
        if cmd == "defaults":
            self.settings = {}
            return {"success": True}
        if cmd == "census":
            return {"success": True, "ticksGame": self.ticks_game, "enabled": self.settings.get("enabled", "True") != "False",
                    "invisibleApplied": self.settings.get("enabled", "True") != "False", "layerVisible": self.settings.get("enabled", "True") != "False",
                    "spawnedConduitTexture": "ConduitTransparent" if self.settings.get("enabled", "True") != "False" else "Conduit_Atlas"}
        if cmd == "fresh":
            return {"success": True, "edges": 1, "same": 1, "different": 0, "missing": 0}
        if cmd.startswith("rect:"):
            if self.settings.get("enabled") == "False":
                return {"success": True, "cmd": "rect", "graph": False, "nets": 1}
            return self._rect([int(v) for v in cmd[5:].split(",")[:4]])
        return {"success": True, "cmd": cmd}

    def _rect(self, r):
        x, z, w, h = r
        FG = self.FG
        sub = FG.FakeMap()
        inside = lambda c: x <= c[0] < x + w and z <= c[1] < z + h  # noqa: E731
        sub.conduit = {c for c in self.m.conduit if inside(c)}
        sub.edifice = {c: v for c, v in self.m.edifice.items() if inside(c)}
        sub.things = [t for t in self.m.things if inside(t["pos"])]
        sub.plants = {c for c in self.m.plants if inside(c)}
        sub.terrain = {c: v for c, v in self.m.terrain.items() if inside(c)}
        sc = sub.read_back({"site": [x - 2, z - 2, w + 4, h + 4], "origin": [x, z]}, "mock")
        sc["water"] = sorted([c[0] - x, (h - 1) - (c[1] - z)] for c, v in sub.terrain.items() if v.startswith("Water"))
        tmin = 10 ** 9 if self.settings.get("tangles") == "False" else int(self.settings.get("tangleMin", 9))
        e = O.expect(sc, "ropey", tangle_min=tmin)
        nodes = []
        for t, n in e["node_types_live"].items():
            if t != "terminal":
                nodes += [{"t": t, "c": [x, z], "netLive": False, "wt": False}] * n
        for t in e["terminals"]:
            nodes.append({"t": "terminal", "c": [x + t[0], z + (h - 1 - t[1])], "netLive": bool(t[2]), "wt": False})
        for t in e["wall_terminals"]:
            nodes.append({"t": "_wt", "c": [x, z], "netLive": bool(t[2]), "wt": True})
        cpc = int(self.settings.get("cordsPerConnection", 3))
        return {"success": True, "cmd": "rect", "graph": True, "nets": O.nets(sc), "nodes": nodes, "cordEdges": e["cord_edges"],
                "cordsAcrossNets": 0, "cordEndsWithoutNet": 0, "strands": e["cord_edges"] * (1 if cpc == 1 else 2),
                "verticesInUnwalkable": 0, "fellBack": 0, "unroutable": 0, "strandBBox": [x, z, x + w - 1, z + h - 1],
                "edgeHashes": {}, "geometryHash": hashlib.sha1(json.dumps(e, sort_keys=True, default=str).encode()).hexdigest()[:16],
                "polylines": [], "ends": [], "ticksGame": self.ticks_game}


# ============================================================================ the comparison
def summarize(rc):
    """A live `rect:` census -> the intrinsic oracle's vocabulary."""
    nodes = rc.get("nodes") or []
    types = collections.Counter(n["t"] for n in nodes if n["t"] != "_wt")
    return {"junctions": types.get("junction", 0), "terminals": types.get("terminal", 0),
            "terminals_live": sum(1 for n in nodes if n["t"] == "terminal" and n.get("netLive")),
            "stubs": sum(v for k, v in types.items() if k.startswith("stub_")), "tangles": types.get("tangle", 0),
            "cord_edges": rc.get("cordEdges"), "strands": rc.get("strands"), "nets": rc.get("nets"),
            "cross_net_edges": rc.get("cordsAcrossNets"), "unwalkable_vertices": rc.get("verticesInUnwalkable"),
            "wall_terminals": sum(1 for n in nodes if n.get("wt")), "node_types": dict(sorted(types.items())),
            "ends_without_net": rc.get("cordEndsWithoutNet")}


EQ_FIELDS = ("junctions", "terminals", "terminals_live", "stubs", "tangles", "cord_edges", "nets", "cross_net_edges",
             "unwalkable_vertices", "wall_terminals", "node_types")


def compare(exp, got, plot_game):
    out = []
    for k in EQ_FIELDS:
        if k in exp and exp[k] != got.get(k):
            out.append({"field": k, "expected": exp[k], "got": got.get(k)})
    if "cords_min" in exp and got.get("strands") is not None:
        # LEARNED pass 1: every wall terminal adds one hanging tail strand drawn over the wall face (CordBuilder
        # OverFace, l.488) that the oracle's per-edge bound never counted -> F48/F52 tidy read 5 for [4, 4].
        hi = exp["cords_max"] + exp.get("wall_terminals", 0)
        if not (exp["cords_min"] <= got["strands"] <= hi):
            out.append({"field": "strands", "expected": [exp["cords_min"], hi], "got": got["strands"]})
    if got.get("ends_without_net"):
        out.append({"field": "ends_without_net", "expected": 0, "got": got["ends_without_net"]})
    return out


def sprawl_check(rc, plot_game):
    bb = rc.get("strandBBox")
    if not bb:
        return None
    x, z, w, h = plot_game
    over = max(x - bb[0], z - bb[1], bb[2] - (x + w), bb[3] - (z + h), 0)
    return {"bbox": bb, "beyond_plot": round(over, 3), "reach_R": R_REACH, "ok": over <= R_REACH}


# ============================================================================ the run
class Run(object):
    def __init__(self, B, args, mock=False):
        self.B, self.args, self.mock = B, args, mock
        self.rows, self.log, self.scenes, self.boards_out = [], [], {}, []
        self.t0 = time.time()
        self.shots = not getattr(args, "no_shots", False)
        self.sweep = bool(getattr(args, "sweep_shots", None))
        self.settle = getattr(args, "shot_settle", None)
        self.tm, self.btm, self.nshots = {}, None, 0
        self._stack = [["setup", time.time()]]
        self._copies = []
        self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self._framed = None                           # (key, t) of the last frame_cell_rect, to skip a redundant re-frame

    # ------------------------------------------------------------------ per-phase wall clock
    def _acc(self, name, d):
        self.tm[name] = self.tm.get(name, 0.0) + d
        if self.btm is not None:
            self.btm[name] = self.btm.get(name, 0.0) + d

    def switch(self, name):
        """Close the current base phase and open `name` (call only outside a ph() block)."""
        now = time.time()
        top = self._stack[-1]
        self._acc(top[0], now - top[1])
        self._stack[-1] = [name, now]

    @contextlib.contextmanager
    def ph(self, name):
        """Nested phase (shots): the enclosing phase is paused while it runs, so phases add up to the wall clock."""
        now = time.time()
        self._acc(self._stack[-1][0], now - self._stack[-1][1])
        self._stack.append([name, now])
        try:
            yield
        finally:
            now = time.time()
            n, t0 = self._stack.pop()
            self._acc(n, now - t0)
            self._stack[-1][1] = now

    def row(self, rid, status, cls, detail):
        self.rows.append({"id": rid, "status": status, "class": cls, "detail": detail})
        if not self.mock or self.args.verbose:
            print("%-34s %-10s %-8s %s" % (rid, status, cls, json.dumps(detail, default=str)[:140]), flush=True)
        self.progress("%s %s %s" % (rid, status, cls))

    def progress(self, line):
        if self.args.progress:
            with open(self.args.progress, "a", encoding="utf-8") as f:
                f.write("  - %s %s\n" % (time.strftime("%H:%M:%S"), line))

    def eng_ticks(self):
        return (self.B.probe("census") or {}).get("ticksGame")

    # ------------------------------------------------------------------ preflight + site
    def preflight(self):
        B = self.B
        load = None
        if self.args.fresh_map and not self.mock:
            ts = time.time()
            B.call("rimworld/go_to_main_menu")
            r = B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
            st = None
            for _ in range(480):
                st = B.call("rimworld/get_ui_state").get("programState")
                if st == "Playing" and B.call("jawa/map_info").get("success"):
                    break
                time.sleep(0.5)
            load = {"start": r.get("success"), "programState": st, "wall_s": round(time.time() - ts, 1)}
            self.row("L0_fresh_map", "PASS" if st == "Playing" else "FAIL", "SITE", load)
            if st != "Playing":
                raise RuntimeError("no fresh map")
        self.fresh = load
        mi = B.call("jawa/map_info")
        self.map_info = {k: mi.get(k) for k in ("sizeX", "sizeZ", "mapBiome")}
        if mi.get("sizeX") != MAP_W or mi.get("sizeZ") != MAP_W:
            self.row("L1_map_250", "FAIL", "SITE", self.map_info)
            raise RuntimeError("map size")
        self.row("L1_map_250", "PASS", "SITE", self.map_info)
        env = {}
        rm = B.call("jawa/running_mods", assembly="RimMandrakeGimmeSomeSlack", details=False)
        if rm.get("success"):
            env["running"] = [p.lower() for p in rm.get("packageIds") or []]
            env["running_sha256"] = hashlib.sha256("\n".join(env["running"]).encode("utf-8")).hexdigest()
            ms = (rm.get("assembly") or {}).get("matches") or []
            env["assembly_matches"] = len(ms)
            env["assembly_sha256"] = ms[0].get("sha256") if len(ms) == 1 else None
        self.env = env
        if not self.mock:
            self.row("L2_tier_running", "PASS" if PKG in env.get("running", []) else "FAIL", "SITE",
                     "%d mods running, gimmesomeslack %s" % (len(env.get("running", [])), PKG in env.get("running", [])))
            lg0 = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
            self.log_base = max([x.get("Sequence", 0) for x in lg0.get("logs") or []] or [0])
        pd = B.probe("defaults")
        rc = B.probe("rect:0,0,1,1")
        if not pd.get("success") or not rc.get("success"):
            self.row("L3_probe_rect_channel", "FAIL", "HARNESS", {"defaults": pd, "rect": rc})
            raise RuntimeError("probe channel or rect census missing (old DLL deployed?)")
        self.row("L3_probe_rect_channel", "PASS", "HARNESS", "defaults + rect: answered")
        B.ap("defaults")
        a = B.ap("set:autoLink=False")
        self.row("L4_aerial_autolink_off", "PASS" if a.get("success") else "FAIL", "HARNESS", a)
        # site pinning
        w = B.call("jawa/weather_set", weather="Clear", lockWeather=True)
        clk = B.call("jawa/time_clock")
        lon = mi.get("longitude")
        pin = None
        hour = None
        if isinstance(clk.get("ticksAbs"), int) and isinstance(lon, (int, float)):
            # GenDate.HourOfDay: (absTicks + LocalTicksOffsetFromLongitude) % 60000 / 2500
            local = (clk["ticksAbs"] + int(round(lon / 360.0 * 60000))) % 60000
            hour = local // 2500
            add = (12 * 2500 - local) % 60000
            if add:
                pin = B.call("jawa/time_set_ticks", ticks=clk["ticksGame"] + add)
        clk2 = B.call("jawa/time_clock")
        B.call("jawa/incident_queue_clear")
        db = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        B.call("jawa/screenshot_mode", enabled=True)
        self.row("L5_site_pinned", "PASS" if w.get("success") is not False else "FAIL", "SITE",
                 {"weather": w.get("success"), "local_hour_before": hour, "ticksGame_before": clk.get("ticksGame"),
                  "ticksGame_after": clk2.get("ticksGame"), "pinned_noon": bool(pin and pin.get("success")),
                  "nonColonistsDestroyed": db.get("matchedCount")})
        rx, rz, rw, rh = REGION
        rr = "%d,%d,%d,%d" % (rx - 2, rz - 2, rw + 4, rh + 4)
        pw = B.call("jawa/list_pawns", rect=rr, limit=50)
        inside = [p.get("id") or p.get("label") for p in pw.get("pawns") or []]
        self.row("L6_no_pawn_in_region", "PASS" if not inside else "FAIL", "SITE", inside or "region %s empty of pawns" % rr)
        self.region_rect = rr

    def clear(self, rect):
        B = self.B
        B.call("jawa/destroy_batch", rects=rect, categories="All")
        B.call("jawa/set_terrain_batch", ops="Soil:" + rect)
        B.call("jawa/set_fog", action="unfog", rect=rect)
        B.call("jawa/set_roof_batch", ops="None:" + rect)

    # ------------------------------------------------------------------ one board
    def board(self, b):
        B = self.B
        self.btm = {}
        self.switch("board_build")
        tb0, wb0 = self.eng_ticks(), time.time()
        rect = "%d,%d,%d,%d" % tuple(b["bbox"])
        self.progress("board %s %s scenes %d bbox %s" % (b["id"], b["settings"], len(b["scenes"]), rect))
        B.probe("defaults")
        set_res = {}
        for k, v in sorted(b["settings"].items()):
            v2 = v.replace("CordStyle.", "")
            if k == "enabled":
                continue                                  # master switch: applied after the build (controls)
            set_res[k] = B.probe("set:%s=%s" % (k, v2)).get("success")
        self.clear(rect)
        # ---- batched builds in placer order
        per = collections.OrderedDict()               # (def, stuff, rot) -> [(game cell, scene id)]
        water = collections.defaultdict(list)
        plants = []
        batteries, masts, aerial = [], {}, []
        for sc, (X0, Z0) in b["scenes"]:
            for op in sc["build"]:
                if op.get("unbuilt") and op["op"] in ("anchor",):
                    pass
                if op["op"] == "terrain" and op["def"] != "Soil":
                    for c in op.get("cells") or []:
                        water[op["def"]].append((X0 + c[0], Z0 + c[1]))
                elif op["op"] == "build" or op["op"] == "anchor":
                    for c in op.get("cells") or []:
                        per.setdefault((op["def"], op.get("stuff"), op.get("rot")), []).append(((X0 + c[0], Z0 + c[1]), sc["id"]))
                elif op["op"] == "battery":
                    batteries.append(((X0 + op["at"][0], Z0 + op["at"][1]), op["pct"], sc["id"]))
                elif op["op"] == "plant":
                    plants += [(X0 + c[0], Z0 + c[1]) for c in op["cells"]]
            if sc["group"] == "aerial":
                aerial.append(sc)
        if water:
            for d, cells in water.items():
                B.call("jawa/set_terrain_batch", ops=";".join("%s:%d,%d,1,1" % (d, c[0], c[1]) for c in cells))
        order = ["Granite", "Wall", "Door", "PowerConduit", "WaterproofConduit"] + list(TRANSMITTERS) + list(CONNECTORS)
        keys = sorted(per, key=lambda k: (order.index(k[0]) if k[0] in order else 99, k[0]))
        site_fail = collections.defaultdict(list)
        builds = {}
        for k in keys:
            d, stuff, rot = k
            items = per[k]
            kw = {"ops": ";".join("%s:%d,%d%s" % (d, c[0], c[1], "" if rot is None else ",%d" % rot) for c, _ in items),
                  "wipeExisting": False}
            if d != "Granite":
                kw["faction"] = "player"
            if stuff:
                kw["stuff"] = stuff
            r = B.call("jawa/build_batch", **kw)
            builds["%s" % d] = {"want": len(items), "survived": r.get("survived"), "failed": (r.get("failed") or [])[:6]}
            if r.get("survived") != len(items):
                fcells = set()
                for f in r.get("failed") or []:
                    for m in re.finditer(r"(\d+),\s*(?:0,\s*)?(\d+)", json.dumps(f)):
                        fcells.add((int(m.group(1)), int(m.group(2))))
                hit = [sid for c, sid in items if c in fcells] or sorted({sid for _, sid in items})
                for sid in hit:
                    site_fail[sid].append("%s %s/%s survived" % (d, r.get("survived"), len(items)))
        if plants:
            B.call("jawa/set_plants", ops=";".join("Plant_TreeOak:%d,%d,1,1" % c for c in plants), growth=1.0, density=1.0)
        # ---- batteries by position
        bx = b["bbox"]
        lt = B.call("jawa/list_things", defName="Battery", rect=rect, limit=500)
        bypos = {}
        for t in lt.get("things") or []:
            p = t.get("position") or t.get("pos") or t.get("cell")
            if p is None and "x" in t:
                p = (t["x"], t["z"])
            if isinstance(p, dict):
                p = (p.get("x"), p.get("z"))
            elif isinstance(p, (list, tuple)):
                p = (p[0], p[-1])
            elif isinstance(p, str):
                n = [int(v) for v in re.findall(r"-?\d+", p)]
                p = (n[0], n[-1]) if n else None
            bypos[tuple(p) if p else None] = t.get("id") or t.get("thingId")
        bat_res = {}
        for cell, pct, sid in batteries:
            tid = bypos.get(cell)
            if not tid:
                site_fail[sid].append("battery at %s not found" % (cell,))
                continue
            r = B.call("jawa/battery_set", thing=tid, mode="setPct", value=pct)
            bat_res[sid] = r.get("storedEnergyAfter")
            if pct > 0 and not (r.get("storedEnergyAfter") or 0) > 0:
                site_fail[sid].append("battery %s not charged" % tid)
        B.call("jawa/map_commit")
        ticks_b = 0
        # ---- aerial staging: link by id, cut, kill
        aer = {}
        self.switch("board_ticks")
        if aerial and not self.mock:
            B.ticks(1)
            ticks_b += 1
            c0 = B.ap("census")
            apos = {(a["x"], a["z"]): a["id"] for a in c0.get("anchors") or []}
            for sc in aerial:
                X0, Z0 = dict((s["id"], o) for s, o in b["scenes"])[sc["id"]]
                ops = {o["op"]: o for o in sc["build"] if o["op"] in ("anchor", "link")}
                cuts = [o for o in sc["build"] if o["op"] == "explode"]
                kills = [o for o in sc["build"] if o["op"] == "kill"]
                ids = {}
                for c in ops["anchor"]["cells"]:
                    g = (X0 + c[0], Z0 + c[1])
                    ids[tuple(c)] = apos.get(g)
                lk = []
                for pa, pb in ops["link"]["pairs"]:
                    ia, ib = ids.get(tuple(pa)), ids.get(tuple(pb))
                    if ia is None or ib is None:
                        site_fail[sc["id"]].append("mast missing for link %s-%s" % (pa, pb))
                        continue
                    lk.append(B.ap("link:%d,%d" % (ia, ib)).get("verdict"))
                aer[sc["id"]] = {"ids": {"%d,%d" % k: v for k, v in ids.items()}, "links": lk, "cuts": [], "kills": []}
                if any(v not in ("Ok", "Linked", "Success") for v in lk):
                    aer[sc["id"]]["link_verdict_note"] = "verdicts %s" % lk
            B.ticks(2)
            ticks_b += 2
            for sc in aerial:
                X0, Z0 = dict((s["id"], o) for s, o in b["scenes"])[sc["id"]]
                ops = {o["op"]: o for o in sc["build"] if o["op"] in ("anchor", "link")}
                ids = {tuple(json.loads("[%s]" % k)): v for k, v in aer[sc["id"]]["ids"].items()}
                spans = ops["link"]["pairs"]
                for o in sc["build"]:
                    if o["op"] == "explode":
                        # the span whose midpoint this is (design_spec puts the explosion at the span's midpoint)
                        best = min(spans, key=lambda pr: abs((pr[0][0] + pr[1][0]) // 2 - o["at"][0]))
                        ia, ib = ids.get(tuple(best[0])), ids.get(tuple(best[1]))
                        aer[sc["id"]]["cuts"].append(B.ap("cut:%d,%d" % (ia, ib)).get("done") if ia and ib else "no ids")
                    elif o["op"] == "kill":
                        ik = ids.get(tuple(o["at"]))
                        aer[sc["id"]]["kills"].append(B.ap("kill:%d" % ik).get("destroyed") if ik else "no id")
            B.ticks(30)
            ticks_b += 30
            B.ap("poll")
        B.ticks(2)
        ticks_b += 2
        B.sleep(0.5)
        B.probe("poll")
        fresh = None if self.sweep else B.probe("fresh")
        # ---- master switch for the controls board
        if b["settings"].get("enabled") == "False":
            pass                                           # handled per scene below (ON census first, then OFF)
        results = []
        self.switch("scene_probes")
        if self.sweep:
            # sweep: screenshots only, ordered by plot position (south->north, west->east) to keep the camera travel short
            for sc, (X0, Z0) in sorted(b["scenes"], key=lambda so: (so[1][1], so[1][0])):
                self.scene_shots(sc, X0, Z0, b)
        else:
            for sc, (X0, Z0) in sorted(b["scenes"], key=lambda so: so[0]["id"]):
                results.append(self.scene(sc, X0, Z0, site_fail.get(sc["id"]), aer.get(sc["id"]), b))
        # ---- determinism: zero-tick re-reads after every view toggle and on/off pair
        det = []
        self.switch("determinism")
        for sc, (X0, Z0) in sorted(b["scenes"], key=lambda so: so[0]["id"]):
            if self.sweep:
                break
            rec = self.scenes[sc["id"]]
            if rec.get("geometryHash") is None:
                continue
            pg = rec["plot_game"]
            h2 = B.probe("rect:%d,%d,%d,%d,1" % tuple(pg))
            h3 = B.probe("rect:%d,%d,%d,%d,1" % tuple(pg))
            same = (h2.get("geometryHash") == rec["geometryHash"] == h3.get("geometryHash") and
                    summarize(h2) == rec["got"] == summarize(h3))
            rec["determinism"] = {"same": same, "h2": h2.get("geometryHash"), "h3": h3.get("geometryHash")}
            det.append(same)
        tb1 = self.eng_ticks()
        self.switch("teardown")
        B.call("jawa/destroy_batch", rects=rect, categories="All")
        self.switch("idle")
        out = {"id": b["id"], "key": b["key"], "settings": b["settings"], "set": set_res, "bbox": b["bbox"],
               "scenes": [s["id"] for s, _ in b["scenes"]], "builds": builds, "batteries": bat_res, "fresh": fresh,
               "aerial": aer, "ticks": (tb1 - tb0) if isinstance(tb0, int) and isinstance(tb1, int) else ticks_b,
               "ticks_stepped": ticks_b, "wall_s": round(time.time() - wb0, 1),
               "determinism_same": "%d/%d" % (sum(det), len(det)),
               "phases_s": {k: round(v, 1) for k, v in self.btm.items() if k != "idle"}}
        self.btm = None
        self.boards_out.append(out)
        self.progress("board %s done: %s ticks, %ss, det %s, phases %s" % (b["id"], out["ticks"], out["wall_s"], out["determinism_same"], out["phases_s"]))

    # ------------------------------------------------------------------ one scene
    def scene(self, sc, X0, Z0, site_fail, aer, board):
        B = self.B
        sid = sc["id"]
        pg = [X0, Z0, sc["plot"][2], sc["plot"][3]]
        rec = {"id": sid, "group": sc["group"], "factors": sc.get("factors"), "origin": [X0, Z0], "plot_game": pg,
               "board": board["id"], "settings": sc.get("settings"), "notes": sc.get("notes"), "shows": sc.get("shows"),
               "site_fail": site_fail or [], "zoom_root": sc.get("zoom_root"), "view": sc.get("view")}
        self.scenes[sid] = rec
        exp = sc["expect"]["intrinsic"]
        rec["expected"] = exp
        root = sc.get("zoom_root") or 11
        v0 = sc.get("view") or {}
        # --no-shots: the camera only matters to the highlight read (net-selected view); every other scene skips the move + wait
        if not self.mock:
            B.call("rimworld/set_camera_zoom", rootSize=root)
            self.frame(pg, root)
            B.sleep(0.6)
        master_off = (sc.get("settings") or {}).get("enabled") == "False"
        if master_off:
            # the planted negative: ON census (polylines) + ON shot first, then OFF
            B.probe("set:enabled=True")
            on = B.probe("rect:%d,%d,%d,%d" % tuple(pg))
            rec["on_polylines"] = on.get("polylines")
            rec["on_geometryHash"] = on.get("geometryHash")
            rec["shot_on"] = self.shot(sid + "_on", pg, root)
            B.probe("set:enabled=False")
            g = B.probe("census")
            rc = B.probe("rect:%d,%d,%d,%d" % tuple(pg))
            ok = (g.get("enabled") is False and not g.get("invisibleApplied") and not g.get("layerVisible") and
                  g.get("spawnedConduitTexture") not in (None, "ConduitTransparent") and rc.get("graph") is False)
            rec["got"] = {"enabled": g.get("enabled"), "invisibleApplied": g.get("invisibleApplied"), "layerVisible": g.get("layerVisible"),
                          "spawnedConduitTexture": g.get("spawnedConduitTexture"), "rect_graph": rc.get("graph")}
            rec["geometryHash"] = None
            rec["shot"] = self.shot(sid, pg, root)
            B.probe("set:enabled=True")
            st = "PASS" if ok and not site_fail else "FAIL"
            rec["status"], rec["class"] = st, ("SITE" if site_fail else "MOD") if st == "FAIL" else ""
            self.row("MX_" + sid, st, rec["class"] or "MOD", rec["got"] if st == "FAIL" else "master off: vanilla art, no cords; ON census %s strands" % on.get("strands"))
            return rec
        rc = B.probe("rect:%d,%d,%d,%d" % tuple(pg))
        if not rc.get("success"):
            rec.update(status="UNMEASURED", **{"class": "HARNESS"})
            rec["error"] = rc
            self.row("MX_" + sid, "UNMEASURED", "HARNESS", rc)
            return rec
        got = summarize(rc)
        rec["got"], rec["geometryHash"] = got, rc.get("geometryHash")
        rec["edgeHashes"], rec["decals"], rec["polylines"] = rc.get("edgeHashes"), rc.get("decals"), rc.get("polylines")
        rec["sprawl"] = sprawl_check(rc, pg)
        rec["ends"] = rc.get("ends")
        mism = compare(exp, got, pg)
        if sc["group"] == "aerial":
            mism += self.aerial_compare(sc, rec, exp, aer, pg)
        if rec["sprawl"] and not rec["sprawl"]["ok"]:
            mism.append({"field": "sprawl", "expected": "<= R=%d beyond plot" % R_REACH, "got": rec["sprawl"]["beyond_plot"]})
        # net-selected view: the highlight must equal the selected net's cords (M12), then the frame
        v = sc.get("view") or {}
        if v.get("select_at") and not self.mock:
            sa = B.probe("select:%d,%d" % (X0 + v["select_at"][0], Z0 + v["select_at"][1]))
            m1 = B.probe("motion")
            B.sleep(0.3)
            m = B.probe("motion")
            per = m.get("cordsPerNet") or {}
            hl = {"selected": sa.get("thing"), "highlightCords": m.get("highlightCords"), "netCords": per.get(str(m.get("selectedNet")))}
            rec["highlight"] = hl
            if not (sa.get("success") and m.get("highlightCords") and m.get("highlightCords") == hl["netCords"]):
                mism.append({"field": "highlight_cords_eq_net_cords", "expected": True, "got": hl})
            del m1
        elif v.get("overlay") == "power" and not self.mock:
            src = [o for o in sc["build"] if o["op"] == "battery"]
            if src:
                B.probe("set:highlight=False")
                sa = B.probe("select:%d,%d" % (X0 + src[0]["at"][0], Z0 + src[0]["at"][1]))
                rec["overlay_via"] = "battery selected, highlight off (no bridge tool holds the power overlay open)"
                rec["overlay_select"] = sa.get("thing")
        rec["mismatches"] = mism
        if sc["group"] == "aerial" and self.mock:
            rec["status"], rec["class"] = "SKIP", "HARNESS"
        elif not mism:
            rec["status"], rec["class"] = "PASS", ""
        else:
            rec["status"] = "FAIL"
            rec["class"] = "SITE" if site_fail else "MOD"
        frame_cap = (v.get("select_at") or v.get("overlay") == "power" or sc["group"] == "aerial")
        rec["shot"] = self.shot(sid, pg, root, frame=bool(frame_cap))
        sel_used = bool(v.get("select_at")) or (v.get("overlay") == "power")
        if sel_used and not self.mock:
            B.probe("deselect")
            B.probe("set:highlight=True")
        if sid in ONOFF_PAIRS:
            B.probe("set:enabled=False")
            rec["shot_off"] = self.shot(sid + "_off", pg, root)
            B.probe("set:enabled=True")
        fac = sc.get("factors") or {}
        fam = {"StarWars": "StarWars", "ExtensionCord": "ExtCord", "Cybertek": "Cybertek"}.get(fac.get("F"))
        art = None
        if fam and not os.path.isdir(os.path.join(MODDIR, "Textures", "RimMandrake", "GimmeSomeSlack", "Styles", fam)):
            art = "UNBUILT art (no Styles/%s folder)" % fam
        rec["art"] = art
        self.row("MX_" + sid, rec["status"], rec["class"] or "MOD",
                 mism if mism else "graph ok: %d edges, %d strands, %d nets, hash %s%s" % (
                     got["cord_edges"] or 0, got["strands"] or 0, got["nets"] or 0, rec["geometryHash"], ("; " + art) if art else ""))
        return rec

    # ------------------------------------------------------------------ hose scenes
    def hose_layout(self, scs, region=REGION):
        """Shelf-pack the hose plots into REGION (the floor boards are done and cleared by then)."""
        rx, rz, rw, rh = region
        x, z, row_h, out = rx, rz, 0, []
        for sc in scs:
            w, h = sc["plot"][2], sc["plot"][3]
            if x + w > rx + rw:
                x, z, row_h = rx, z + row_h + HOSE_PITCH, 0
            if z + h > rz + rh:
                raise SystemExit("hose scene %s does not fit the region %s" % (sc["id"], region))
            out.append((sc, (x, z)))
            x += w + HOSE_PITCH
            row_h = max(row_h, h)
        return out

    def hose_scenes(self, scs):
        """Place and check the design's hose scenes with validation_hose.py's call shapes (build RM_HoseReel, then the
        HoseProbe `check:`/`lay:`/`flow:` verbs, a census read). Expectations are the scene row's own intrinsic block."""
        B = self.B
        d = B.hp("defaults")
        self.row("H0_probe_channel", "PASS" if d.get("success") else "FAIL", "HARNESS", d if not d.get("success") else "HoseProbe defaults applied")
        if not d.get("success"):
            return
        for sc, (X0, Z0) in self.hose_layout(scs):
            sid = sc["id"]
            pl = PL.hose_plan(sc, (X0, Z0))
            pg = [X0, Z0, sc["plot"][2], sc["plot"][3]]
            rec = {"id": sid, "group": "hose", "factors": sc.get("factors"), "origin": [X0, Z0], "plot_game": pg,
                   "board": "hose", "settings": sc.get("settings"), "notes": sc.get("notes"), "shows": sc.get("shows"),
                   "site_fail": [], "zoom_root": sc.get("zoom_root"), "view": sc.get("view"), "expected": pl["expect"],
                   "reel": pl["reel"], "far": pl["far"]}
            self.scenes[sid] = rec
            reel, far = tuple(pl["reel"]), tuple(pl["far"])
            probes, census = [], None
            for st in pl["steps"]:
                if st["kind"] == "tool":
                    r = B.call(st["tool"], **st["args"])
                    if st["tool"] == "jawa/build_batch" and r.get("survived") is not None:
                        want = len(st["args"]["ops"].split(";"))
                        if r.get("survived") != want:
                            rec["site_fail"].append("%s %s/%s survived" % (st["args"]["ops"].split(":")[0], r.get("survived"), want))
                elif st["kind"] == "hose_probe":
                    r = B.hp(st["cmd"])
                    probes.append({"cmd": st["cmd"], "success": r.get("success"), "reason": r.get("reason")})
                    if st["cmd"].startswith("check:") and r.get("reason") is not None:
                        rec["site_fail"].append("install check refused: %s" % r.get("reason"))
                elif st["kind"] == "hose_census" and not self.sweep:
                    c = B.hp("census")
                    census = c
            rec["probes"] = probes
            if self.sweep:                                  # sweep: built + flowed above, shot only, no verdict
                if not self.mock:
                    rec["shot"] = self.shot(sid, pg, sc.get("zoom_root") or 11, frame=True)
                continue
            h = {}
            for x in (census or {}).get("hoses") or []:
                if tuple(x["reel"]) == reel:
                    h = x
            rec["census"] = {k: h.get(k) for k in ("kind", "laid", "layOk", "layReason", "state", "blend", "visibleWidth", "widthOverWire", "minBendFlat",
                                                  "minBendPlump", "couplings", "flatLen", "pathLen", "poseLen", "selfIntersects",
                                                  "unwalkablePoints", "fellBack", "geometryHash", "provider")}
            rec["census"]["transitionTicks"] = (census or {}).get("transitionTicks")
            diffs = self.hose_compare(pl["expect"], h, census or {})
            if not h:
                status, cls = "FAIL", "SITE"
                diffs = [{"field": "reel", "expected": list(reel), "got": "no hose reel in the census"}]
            elif rec["site_fail"] or not h.get("layOk"):
                status, cls = "FAIL", "SITE"
            elif diffs:
                status, cls = "FAIL", "MOD"
            else:
                status, cls = "PASS", None
            rec.update(status=status, **({"class": cls} if cls else {}))
            rec["diffs"] = diffs
            if not self.mock:
                rec["shot"] = self.shot(sid, pg, sc.get("zoom_root") or 11, frame=True)
            self.row("MX_" + sid, status, cls or "-", diffs or rec["site_fail"] or rec["census"])

    @staticmethod
    def hose_compare(e, h, c):
        """The scene's intrinsic hose expectations against one HoseProbe census row (validation_hose.py H2-H6 thresholds)."""
        out = []
        if not h:
            return out

        def need(field, ok, want, got):
            if not ok:
                out.append({"field": field, "expected": want, "got": got})
        need("kind", h.get("kind") == "Hose", "Hose", h.get("kind"))
        need("state", h.get("state") == e["state"], e["state"], h.get("state"))
        lo, hi = e["blend"]
        b = h.get("blend")
        need("blend", b is not None and lo <= b <= hi, e["blend"], b)
        lo, hi = e["visible_width"]
        w = h.get("visibleWidth")
        need("visible_width", w is not None and lo <= w <= hi, e["visible_width"], w)
        need("width_over_wire_ge", (h.get("widthOverWire") or 0) >= e["width_over_wire_ge"], e["width_over_wire_ge"], h.get("widthOverWire"))
        mb = (c.get("minBendSetting") or e["min_bend_radius_ge"])
        need("min_bend_radius_ge", min(h.get("minBendFlat") or 0, h.get("minBendPlump") or 0) >= 0.95 * mb,
             "0.95 x %s" % mb, [h.get("minBendFlat"), h.get("minBendPlump")])
        need("self_intersections", (0 if not h.get("selfIntersects") else 1) == e["self_intersections"], e["self_intersections"], h.get("selfIntersects"))
        need("unwalkable_points", h.get("unwalkablePoints") == e["unwalkable_points"], e["unwalkable_points"], h.get("unwalkablePoints"))
        # couplings: the two end fittings + one joiner per real bend, none on a straight (owner review 2026-10-04 B17)
        j = h.get("joints")
        exact = 2 + j if isinstance(j, int) else None
        need("couplings", h.get("couplings") == exact and (h.get("couplings") or 0) >= e["couplings_min"],
             {"exact_from_joints": exact, "min": e["couplings_min"]}, h.get("couplings"))
        return out

    def aerial_compare(self, sc, rec, exp, aer, pg):
        if self.mock:
            return []
        c = self.B.ap("census")
        x, z, w, h = pg
        mine = [a for a in c.get("anchors") or [] if x <= a["x"] < x + w and z <= a["z"] < z + h]
        mine.sort(key=lambda a: a["x"])
        up = sum(1 for a in mine for l in a["links"] if l["state"] == "Up") // 2
        cut_ = sum(1 for a in mine for l in a["links"] if l["state"] != "Up") // 2
        fallen = sum(len(a.get("fallen") or []) for a in mine)
        got = {"spans_up": up, "spans_cut": cut_, "fallen_cords": fallen, "pole_live": [a["netLive"] for a in mine],
               "net_repairs": c.get("netRepairs"), "anchors": len(mine)}
        rec["aerial_got"] = got
        rec["aerial_staging"] = aer
        out = []
        killed = len([o for o in sc["build"] if o["op"] == "kill"])
        exp_live = [v for i, v in enumerate(exp.get("pole_live") or []) if v is not None]
        for k, want in (("spans_up", exp.get("spans_up")), ("spans_cut", exp.get("spans_cut")),
                        # a cut span is stored as two FallenCord entries (design 2.6: two downed wires), so the
                        # census counts downed ends AND fallen ends (pass 1: every cut scene read 2 against 0)
                        ("fallen_cords", len(exp.get("fallen_ends") or []) + len(exp.get("downed_ends") or [])), ("net_repairs", exp.get("net_repairs")),
                        ("pole_live", exp_live), ("anchors", len(exp.get("pole_live") or []) - killed)):
            if want is not None and got.get(k) != want:
                out.append({"field": "aerial." + k, "expected": want, "got": got.get(k)})
        return out

    def frame(self, pg, root):
        self.B.call("rimworld/frame_cell_rect", x=pg[0], z=pg[1], width=pg[2], height=pg[3], paddingCells=PAD, rootSize=root)
        self._framed = ((tuple(pg), root), time.time())

    def shot(self, name, pg, root, frame=False):
        B = self.B
        if self.mock:
            return None
        with self.ph("shots" if self.shots else "shots_camera_only"):
            return self._shot(name, pg, root, frame)

    def _shot(self, name, pg, root, frame):
        B = self.B
        render = self.shots
        self.nshots += 1 if render else 0
        settle = self.settle if self.settle is not None else 1.5
        if frame:
            # a frame_cell_rect with the same args was already issued by scene() and nothing moved the camera since: do not
            # repeat it, only wait out whatever part of the settle time has not already elapsed (same total settle).
            fk = self._framed
            if fk and fk[0] == (tuple(pg), root):
                B.sleep(max(0.0, settle - (time.time() - fk[1])))
            else:
                self.frame(pg, root)
                B.sleep(settle)
            self._framed = None
            if not render:
                return {"file": None, "kind": "skipped", "ok": None, "skipped": "--no-shots", "rect": pg}
            r = B.call("jawa/take_screenshot", fileName="mcx_" + name)
        elif not render:
            # --no-shots: the capture tool also moves the camera to the rect; the cord graph rebuilds off camera-driven section
            # regeneration, so make the same move (frame_cell_rect, same settle) and skip only render + PNG + copy.
            self.frame(pg, root)
            B.sleep(settle)
            self._framed = None
            return {"file": None, "kind": "skipped", "ok": None, "skipped": "--no-shots", "rect": pg}
        else:
            # LEARNED smoke 2026-10-02: rootSize overrides the rect framing (a wide frame with the scene small and
            # off-centre), so the cell-rect capture takes the tool's own rect fit; Z is set on the live camera.
            r = B.call("rimworld/screenshot_cell_rect", x=pg[0], z=pg[1], width=pg[2], height=pg[3], paddingCells=PAD,
                       fileName="mcx_" + name, suppressMessage=True)
        src = r.get("path") or r.get("filePath")
        for _ in range(80):
            if src and os.path.exists(src):
                break
            time.sleep(0.05)
        rec = {"file": None, "kind": "frame" if frame else "cell_rect", "src": src,
               "ok": r.get("success"), "pad": PAD, "rect": pg}
        if src and os.path.exists(src):
            dst = os.path.join(SHOTS, name + ".png")
            os.makedirs(SHOTS, exist_ok=True)
            rec["file"] = name + ".png"
            # the 2-3 MB copy across the WSL/Windows boundary overlaps with the next bridge calls; joined in finish_copies()
            self._copies.append((rec, name, self._pool.submit(shutil.copyfile, src, dst)))
        return rec

    def finish_copies(self):
        with self.ph("shot_copy_wait"):
            for rec, name, fut in self._copies:
                try:
                    fut.result()
                except Exception as ex:  # noqa: BLE001
                    rec["file"] = None
                    self.log.append("copy failed %s: %r" % (name, ex))
        self._copies = []
        self._pool.shutdown(wait=True)

    def scene_shots(self, sc, X0, Z0, board):
        """Sweep pass: this scene's screenshots only (the same views, toggles and file names as scene()); no census, no
        verdict. Records land in self.scenes[sid] and are merged into the state pass result by merge_sweep()."""
        B = self.B
        sid = sc["id"]
        pg = [X0, Z0, sc["plot"][2], sc["plot"][3]]
        rec = {"id": sid}
        self.scenes[sid] = rec
        root = sc.get("zoom_root") or 11
        v = sc.get("view") or {}
        if (sc.get("settings") or {}).get("enabled") == "False":
            B.probe("set:enabled=True")
            rec["shot_on"] = self.shot(sid + "_on", pg, root)
            B.probe("set:enabled=False")
            rec["shot"] = self.shot(sid, pg, root)
            B.probe("set:enabled=True")
            return
        selected = False
        if v.get("select_at") and not self.mock:
            B.probe("select:%d,%d" % (X0 + v["select_at"][0], Z0 + v["select_at"][1]))
            selected = True
        elif v.get("overlay") == "power" and not self.mock:
            src = [o for o in sc["build"] if o["op"] == "battery"]
            if src:
                B.probe("set:highlight=False")
                B.probe("select:%d,%d" % (X0 + src[0]["at"][0], Z0 + src[0]["at"][1]))
                selected = True
        frame_cap = (v.get("select_at") or v.get("overlay") == "power" or sc["group"] == "aerial")
        rec["shot"] = self.shot(sid, pg, root, frame=bool(frame_cap))
        if selected:
            B.probe("deselect")
            B.probe("set:highlight=True")
        if sid in ONOFF_PAIRS:
            B.probe("set:enabled=False")
            rec["shot_off"] = self.shot(sid + "_off", pg, root)
            B.probe("set:enabled=True")


def merge_sweep(old_path, res, out):
    """Write the sweep's shot records into the state pass result JSON (verdicts untouched)."""
    old = json.load(open(old_path, encoding="utf-8"))
    n = 0
    for sid, rec in res["scenes"].items():
        tgt = old["scenes"].get(sid)
        if tgt is None:
            continue
        for k in ("shot", "shot_on", "shot_off"):
            if rec.get(k):
                tgt[k] = rec[k]
                n += 1
    old.setdefault("sweep", []).append({"at": res["started"], "wall_s": res["wall_s"], "shots": res["timing"]["shots_taken"],
                                         "phases_s": res["timing"]["phases_s"], "calls": res["calls"], "aborted": res["aborted"]})
    with open(out, "w", encoding="utf-8") as f:
        json.dump(old, f, indent=1, default=str)
    return n


def install_profiler(B):
    """--profile: wall time per bridge call name (jawa/..., rimworld/...) and per probe verb (probe:rect, ap:census, hp:flow ...)
    plus sleep: {name: [count, total_s]}. A probe total includes its serial polling AND the nested jawa/mod_settings_field calls (counted again under their own name), so do not add the rows together."""
    prof = collections.OrderedDict()

    def rec(name, dt):
        e = prof.setdefault(name, [0, 0.0])
        e[0] += 1
        e[1] += dt

    def wrap(attr, namer):
        orig = getattr(B, attr)

        def f(*a, **kw):
            t = time.time()
            try:
                return orig(*a, **kw)
            finally:
                rec(namer(a, kw), time.time() - t)
        setattr(B, attr, f)

    verb = lambda a: str(a[0]).split(":")[0] if a else "?"
    wrap("call", lambda a, kw: a[0] if a else "?")
    wrap("probe", lambda a, kw: "probe:" + verb(a))
    wrap("ap", lambda a, kw: "ap:" + verb(a))
    wrap("hp", lambda a, kw: "hp:" + verb(a))
    wrap("sleep", lambda a, kw: "sleep")
    B.prof = prof
    return prof


def run(args, B, mock=False):
    spec = load_catalog(args.catalog)
    if getattr(args, "scenes", "full") == "reduced":
        import reduced as RD                       # numpy-free: owner 2026-10-05 densification, 109 -> 39 scenes
        spec = RD.reduce_spec(spec)
    scenes = spec["scenes"]
    if args.only:
        scenes = [s for s in scenes if any(s["id"].startswith(o) for o in args.only)]
    sweep_src = getattr(args, "sweep_shots", None)
    if sweep_src:
        # the sweep re-takes exactly the scenes of the state pass it follows (same catalog => same board layout)
        have = set(json.load(open(sweep_src, encoding="utf-8"))["scenes"])
        scenes = [s for s in scenes if s["id"] in have]
    boards = make_boards(scenes)
    if args.max_boards:
        boards = boards[:args.max_boards]
    R = Run(B, args, mock)
    prof = install_profiler(B) if getattr(args, "profile", False) else None
    res = {"mod": "GimmeSomeSlack", "script": "northstar_matrix/run_live.py", "mode": "mock" if mock else "live",
           "pass": "sweep-shots" if sweep_src else ("state-only (--no-shots)" if getattr(args, "no_shots", False) else "full"),
           "tier": "gimmesomeslack", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "spec_hash": spec.get("spec_hash"),
           "catalog": spec.get("generator"), "reach": dict(R_SRC, R=R_REACH, GAP=GAP), "region": REGION,
           "rows": R.rows, "boards": R.boards_out, "scenes": R.scenes}
    ov = board_overlap_check(boards)
    R.row("O0_board_pitch", "PASS" if not ov else "FAIL", "HARNESS",
          ov or "%d boards, every plot pair >= GAP %d apart (R=%d from CordLayer.cs)" % (len(boards), GAP, R_REACH))
    try:
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck"))
        import status as _mc  # noqa: E402
        res["mod_hash"] = _mc.mod_hash(MODDIR)
    except Exception as ex:  # noqa: BLE001
        res["mod_hash"] = None
        R.log.append("mod_hash unavailable: %r" % ex)
    aborted = None
    t_start = None
    if getattr(args, "no_shots", False) and not sweep_src:
        R.row("I0_screenshots", "SKIP", "HARNESS",
              "--no-shots (deliberate; the walk rules screenshots are the human look and never a pass bar): no screenshot was taken, so image sanity (census mask, frame_ok, blank/magenta), the on/off pair shots and "
              "the net-selected/power-overlay frames are UNMEASURED; run --sweep-shots <this result> for them. State verdicts are unaffected.")
    try:
        R.switch("site_setup")
        R.preflight()
        t_start = R.eng_ticks()
        for b in boards:
            R.board(b)
        # hose scenes: placed one by one in REGION (floor boards are done) with validation_hose.py's call shapes,
        # inside the same screenshot-mode session so frame captures work the same way
        hose = [sc for sc in scenes if sc["group"] == "hose"]
        if hose:
            R.switch("hose")
            try:
                R.hose_scenes(hose)
            finally:
                try:
                    B.hp("defaults")
                except Exception:  # noqa: BLE001
                    pass
    except Exception as ex:  # noqa: BLE001
        import traceback
        aborted = "%r" % ex
        R.log.append(traceback.format_exc())
        R.row("ABORT", "FAIL", "HARNESS", aborted)
    finally:
        R.switch("post")
        try:
            B.probe("defaults")
            B.ap("defaults")
            if not mock:
                B.call("jawa/screenshot_mode", enabled=False)
                B.call("jawa/weather_set", weather="Clear", unlock=True)
        except Exception:  # noqa: BLE001
            pass
    R.finish_copies()
    det = [s.get("determinism", {}).get("same") for s in R.scenes.values() if s.get("determinism")]
    if det:
        R.row("D1_zero_tick_rereads_same", "PASS" if all(det) else "FAIL", "MOD",
              "%d/%d scenes: geometry hash + census identical on 2 re-reads after all view toggles" % (sum(det), len(det)))
    fr = [b.get("fresh") or {} for b in R.boards_out]
    if fr and not mock and not sweep_src:
        bad = ["%s %s %s" % (b["id"], b["scenes"], {k: b["fresh"].get(k) for k in ("edges", "different", "missing")})
               for b in R.boards_out if (b.get("fresh") or {}).get("different") or (b.get("fresh") or {}).get("missing")]
        R.row("D2_fresh_builder_same", "PASS" if not bad else "FAIL", "MOD",
              bad or "%d boards: a fresh CordBuilder on the same map reproduces every laid edge" % len(fr))
    if not mock and not sweep_src:
        lg = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
        new = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > getattr(R, "log_base", 0)]
        errs = [e for e in new if str(e.get("Level", "")).lower() in ("error", "exception")]
        # LEARNED pass 1: destroy_batch categories=All over the region names geysers/monoliths it may not destroy
        # ("Tried to destroy non-destroyable thing SteamGeyser...") -- the runner's own clear, not the mod
        site = [e for e in errs if "non-destroyable" in str(e.get("Message", ""))]
        errs = [e for e in errs if e not in site]
        # LEARNED 2026-10-04: a donor mod's map-creation patch (ReGrowthCore.Map_FinalizeInit_Patch NREs on the fresh
        # quicktest map) is the SITE's noise, not ours -- excluded only when no GimmeSomeSlack frame is in the message.
        donor = [e for e in errs if "Map_FinalizeInit" in str(e.get("Message", "")) and "GimmeSomeSlack" not in str(e.get("Message", ""))]
        errs = [e for e in errs if e not in donor]
        R.row("Z_log_budget", "PASS" if not errs else "FAIL", "MOD",
              {"errors": [str(e.get("Message", ""))[:200] for e in errs[:8]], "newWarnings": len(new),
               "siteClearErrorsExcluded": len(site), "donorMapInitErrorsExcluded": len(donor)})
    t_end = R.eng_ticks() if not aborted else None
    res["env"] = getattr(R, "env", {})
    res["map"] = getattr(R, "map_info", None)
    res["fresh_map"] = getattr(R, "fresh", None)
    res["aborted"] = aborted
    res["log"] = R.log
    res["calls"] = getattr(B, "n", None)
    R.switch("done")
    res["wall_s"] = round(time.time() - R.t0, 1)
    res["timing"] = {"phases_s": {k: round(v, 1) for k, v in sorted(R.tm.items(), key=lambda kv: -kv[1]) if k != "done"},
                     "shots_taken": R.nshots, "calls": getattr(B, "n", None),
                     "calls_profile": ({k: {"n": v[0], "total_s": round(v[1], 2), "avg_s": round(v[1] / max(v[0], 1), 3)}
                                        for k, v in sorted(prof.items(), key=lambda kv: -kv[1][1])} if prof else None),
                     "note": "phases add up to wall_s; shots are nested out of the phase they ran in; shot_copy_wait is the "
                             "residual PNG copy that did not overlap the bridge calls"}
    res["ticks_spent"] = (t_end - t_start) if isinstance(t_start, int) and isinstance(t_end, int) else None
    res["budget"] = {"design_ticks_stills": 138, "design_wall_min": "15-20 after cold load",
                     "boards": [{k: b[k] for k in ("id", "ticks", "ticks_stepped", "wall_s")} | {"scenes": len(b["scenes"])}
                                for b in R.boards_out]}
    t = collections.Counter(s.get("status") for s in R.scenes.values())
    c = collections.Counter(s.get("class") for s in R.scenes.values() if s.get("status") == "FAIL")
    res["summary"] = {"scenes": len(R.scenes), "status": dict(t), "fail_class": dict(c)}
    return res


# ============================================================================ post: sheets, sanity, review.html
CAPTION = {"T": "topology", "S": "stage", "F": "style", "P": "power", "V": "view", "Z": "zoom"}


def caption(rec):
    f = rec.get("factors") or {}
    if rec["group"] == "floor":
        return "%s | %s | %s | %s | %s | %s" % (f.get("T"), f.get("S"), f.get("F"), f.get("P"), f.get("V"), f.get("Z"))
    if rec["group"] == "density":
        return "%s cells | %s" % (f.get("n"), f.get("S"))
    if rec["group"] == "aerial":
        return "%s poles x %s | %s | %s | %s" % (f.get("N"), f.get("R"), f.get("St"), f.get("G"), f.get("P"))
    if rec["group"] == "hose":
        return "%s | %s | L%s | %s" % (f.get("St"), f.get("Ro"), f.get("Le"), f.get("Fl"))
    return json.dumps(f)


def post(result_path):
    import contact_sheet as CS
    import numpy as np  # noqa: F401
    from PIL import Image
    res = json.load(open(result_path, encoding="utf-8"))
    recs = res["scenes"]
    sanity = {}
    for sid, rec in sorted(recs.items()):
        shot = (rec.get("shot") or {}).get("file")
        if not shot:
            continue
        p = os.path.join(SHOTS, shot)
        if not os.path.exists(p):
            continue
        off = os.path.join(SHOTS, sid + "_off.png") if (rec.get("shot_off") or {}).get("file") else None
        m = CS.metrics(p, off, None)
        im = Image.open(p)
        W, H = im.size
        pg = rec["plot_game"]
        kind = rec["shot"].get("kind")
        if kind == "cell_rect":
            pad = rec["shot"].get("pad", PAD)
            cw, ch = pg[2] + 2 * pad, pg[3] + 2 * pad
            ppc = W / float(cw)
            m["px_per_cell"] = round(ppc, 3)
            m["frame_ok"] = CS.frame_ok((W, H), (cw, ch), ppc)
            polys = rec.get("polylines") or []
            if rec["group"] == "controls" and rec.get("on_polylines") is not None:
                polys = rec.get("on_polylines")        # planted negative: ON-census mask over the OFF frame
            px = [[((q[0] + 0.0 - (pg[0] - pad)) * ppc, H - (q[1] + 0.0 - (pg[1] - pad)) * ppc) for q in pl] for pl in polys]
            m["mask_check"] = CS.mask_check(p, px)
        else:
            m["frame_ok"] = None
            m["mask_check"] = {"verdict": "UNMEASURED", "detail": "frame capture (per-frame draws): no cell->pixel transform"}
        sanity[sid] = m
        rec["sanity"] = m
    # controls: the empty plot must read NO_WIRES; the ON mask over the master-off frame must FAIL
    neg = {}
    for sid, rec in recs.items():
        if rec["group"] == "controls" and sid in sanity:
            neg[sid] = sanity[sid]["mask_check"]["verdict"]
    # contact sheets: floor by topology (stages left to right), density, aerial, controls
    os.makedirs(OUT_DIR, exist_ok=True)
    groups = collections.OrderedDict()
    for sid, rec in sorted(recs.items()):
        g = rec["group"]
        if g == "floor":
            g = "floor_T%02d_%s" % (D.T_LEVELS.index(rec["factors"]["T"]), rec["factors"]["T"])
        groups.setdefault(rec["group"] if rec["group"] != "floor" else "floor", []).append(sid)
    sheets = []
    for g, ids in groups.items():
        if g == "floor":
            ids = sorted(ids, key=lambda s: (D.T_LEVELS.index(recs[s]["factors"]["T"]), D.S_LEVELS.index(recs[s]["factors"]["S"])))
        items = []
        for sid in ids:
            rec = recs[sid]
            f = (rec.get("shot") or {}).get("file")
            p = os.path.join(SHOTS, f) if f else "/nonexistent"
            mm = dict(sanity.get(sid) or {"ok": False, "wire_evidence": "NO SHOT"})
            mm["ok"] = rec.get("status") == "PASS" and mm.get("ok", False)
            items.append((p, [sid + "  " + rec.get("status", "?") + (" " + rec.get("class", "") if rec.get("status") == "FAIL" else ""),
                              caption(rec)[:60]], mm))
        cols = 4
        for k in range(0, len(items), 16):
            out = os.path.join(OUT_DIR, "sheet_%s_%02d.png" % (g, k // 16 + 1))
            CS.sheet(items[k:k + 16], out, cols=cols, title="Gimme Some Slack matrix (live 2026-10-02): %s %d-%d of %d  (floor rows: tidy, ropey, rat's nest, lattice tangle)" % (
                g, k + 1, min(k + 16, len(items)), len(items)))
            sheets.append(out)
    if not sanity:
        print("post: UNMEASURED image checks: the result holds no screenshot (--no-shots and no --sweep-shots yet)")
    rep = {"result": os.path.basename(result_path), "thresholds": CS.T, "controls_negative": neg, "per_scene": sanity,
           "sheets": [os.path.basename(s) for s in sheets],
           "counts": {"shots": len(sanity), "ok": sum(1 for m in sanity.values() if m.get("ok")),
                      "mask": dict(collections.Counter(m["mask_check"]["verdict"] for m in sanity.values())),
                      "frame_ok_false": [s for s, m in sanity.items() if m.get("frame_ok") is False],
                      "magenta": [s for s, m in sanity.items() if not m.get("no_magenta")],
                      "blank": [s for s, m in sanity.items() if not m.get("non_blank")],
                      "wire_pair": {s: m.get("wire_evidence") for s, m in sanity.items() if m.get("wire_evidence") != "UNMEASURED"}}}
    with open(os.path.join(OUT_DIR, "image_sanity.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1, default=str)
    write_review(res, recs, os.path.join(OUT_DIR, "review.html"))
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    return rep


TEMPLATE = os.path.expanduser("~/.claude/skills/review-sheets/assets/sheet_template.html")


def write_review(res, recs, out):
    """review-sheets template (skill review-sheets): CONFIG + ITEMS filled, one row per scene, thumbnail = the shot,
    effect line = state verdict + factors + image checks. Pre-filled: keep a PASS scene with a clean frame, flag the
    rest. Kept frames become the golden set (design 4.5)."""
    order = sorted(recs, key=lambda s: ({"floor": 0, "density": 1, "aerial": 2, "controls": 3, "hose": 4}.get(recs[s]["group"], 5),
                                        D.T_LEVELS.index(recs[s]["factors"]["T"]) if recs[s]["group"] == "floor" else 0,
                                        D.S_LEVELS.index(recs[s]["factors"]["S"]) if recs[s]["group"] == "floor" else 0, s))
    items, dec = [], {}
    for sid in order:
        r = recs[sid]
        f = (r.get("shot") or {}).get("file")
        san = r.get("sanity") or {}
        warn = [k for k in ("non_blank", "no_magenta", "brightness_ok") if san and not san.get(k)]
        if san.get("frame_ok") is False:
            warn.append("frame size")
        mk = (san.get("mask_check") or {}).get("verdict")
        mism = "; ".join("%s want %s got %s" % (x["field"], json.dumps(x["expected"]), json.dumps(x["got"]))
                         for x in (r.get("mismatches") or []))[:400]
        eff = "%s%s | %s" % (r.get("status"), (" (" + str(r.get("class")) + ")") if r.get("status") == "FAIL" else "", caption(r))
        if mism:
            eff += " | " + mism
        if r.get("art"):
            eff += " | " + r["art"]
        if warn:
            eff += " | image check: " + ", ".join(warn)
        if mk:
            eff += " | wire mask " + mk
        if (r.get("shot_off") or {}).get("file"):
            eff += " | mod-OFF pair: shots/" + r["shot_off"]["file"]
        grp = r["group"] if r["group"] != "floor" else "floor: " + str((r.get("factors") or {}).get("T"))
        good = r.get("status") == "PASS" and not warn and f
        it = {"id": sid, "label": sid, "group": grp, "effect": eff, "prefill": "keep" if good else ("flag" if f else None),
              "contested": bool(r.get("status") == "FAIL")}
        if f:
            it["thumb"] = "shots/" + f
        items.append(it)
        if it["prefill"]:
            dec[sid] = {"decision": it["prefill"], "note": ""}
    cfg = {"sheetId": "mc_matrix_live_20261002", "title": "Gimme Some Slack scene matrix (live)",
           "subtitle": "run %s: %s" % (res.get("started"), json.dumps((res.get("summary") or {}).get("status"))),
           "briefHtml": ("<p>Each tile is one scene of the phase-2 Northstar matrix (design section 4), built on a bland quicktest "
                         "map and photographed paused. The state verdict (PASS/FAIL and its class) comes from the probe census "
                         "against the generator's oracle, never from the picture. Floor rows read tidy, ropey, rat's nest, lattice "
                         "tangle in order for each topology. Only the Jawa family has real art: other styles are labelled. "
                         "Hose scenes (frame captures) show the reel and its laid hose; their state verdict is the HoseProbe census.</p><p>Keep = this frame is right and becomes the golden frame later runs "
                         "are shown beside. Flag = something looks wrong; say what in the note.</p>"),
           "criterion": "Pre-filled keep only when the state oracle passed and the image checks (non-blank, no magenta, brightness, "
                        "frame size) passed -- those rank broken captures, not whether the cords look right; that is yours.",
           "invented": ["Overlay view realised by selecting the scene's battery with the net highlight off (no bridge tool holds the power overlay open).",
                        "Aerial 'explode' staged with the probe's cut: (the explosion behaviour itself is validation_aerial.py M15)."],
           "posture": {"mode": "whitelist", "explain": "Only KEPT frames become golden. Unkept frames are simply not golden; nothing is deleted."},
           "options": [{"key": "keep", "label": "Keep", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
                       {"key": "flag", "label": "Flag", "hotkey": "2", "color": "#e06c6c", "counts": "out"}],
           "groupLabel": "topology / group", "media": True, "decisionsFile": "review.decisions.json",
           "decisionsPath": "D:\\Luke\\dev\\RimMandrake\\Transient\\mc_matrix_live_20261002\\review.decisions.json",
           "sheetPath": "D:\\Luke\\dev\\RimMandrake\\Transient\\mc_matrix_live_20261002\\review.html"}
    html = open(TEMPLATE, encoding="utf-8").read()
    html = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                  lambda m: m.group(1) + "\n" + json.dumps(cfg, indent=1) + "\n" + m.group(3), html, count=1, flags=re.S)
    html = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                  lambda m: m.group(1) + "\n" + json.dumps(items).replace("</", "<\\/") + "\n" + m.group(3), html, count=1, flags=re.S)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    dp = os.path.join(os.path.dirname(out), "review.decisions.json")
    if not os.path.exists(dp):
        with open(dp, "w", encoding="utf-8") as fh:
            json.dump({"posture": "whitelist", "decisions": dec,
                       "reviewStatus": {"state": "prefill", "by": None, "at": None,
                                        "evidence": "generated by run_live.py --post; nobody has reviewed it"}}, fh, indent=1)


# ============================================================================ compare runs
def compare_runs(pa, pb):
    a, b = json.load(open(pa, encoding="utf-8")), json.load(open(pb, encoding="utf-8"))
    ids = sorted(set(a["scenes"]) & set(b["scenes"]))
    ids = [i for i in ids if a["scenes"][i].get("geometryHash") and b["scenes"][i].get("geometryHash")]
    diff = [i for i in ids if (a["scenes"][i]["geometryHash"], a["scenes"][i].get("got")) !=
            (b["scenes"][i]["geometryHash"], b["scenes"][i].get("got"))]
    if len(ids) < 20:
        return False, "only %d comparable scenes (sanity floor 20)" % len(ids)
    return not diff, "%d scenes compared (geometry hash + census), %d differ %s" % (len(ids), len(diff), diff[:8])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--fault", default=None, help="mock fault: flip_z (conduit shifted one cell north)")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--catalog", default="design", help="design | matrix | <scenes.json written by design_spec.py --out>")
    ap.add_argument("--only", nargs="*", help="scene id prefixes")
    ap.add_argument("--scenes", choices=("reduced", "full"), default="reduced",
                    help="reduced (default, 39 scenes: northstar_matrix/reduced.py, owner densification 2026-10-05) or full "
                         "(the phase-2 design's T16 x S4 catalog, 109 scenes, for a design review)")
    ap.add_argument("--max-boards", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--progress", default=None)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--no-shots", action="store_true", help="state pass only: skip every screenshot (and the camera moves that only served them)")
    ap.add_argument("--sweep-shots", default=None, metavar="RESULT_JSON",
                    help="screenshot-only pass: rebuild each board of that state-pass result, take its shots, merge them into the JSON")
    ap.add_argument("--profile", action="store_true", help="record per-call wall time (call name -> count, total s) in result['timing']['calls_profile']")
    ap.add_argument("--probe-poll", type=float, default=0.25, help="seconds between serial polls while waiting for a probe answer (default 0.25)")
    ap.add_argument("--shot-settle", type=float, default=None, help="seconds to wait after a frame move before a frame capture (default 1.5; sweep 0.7)")
    ap.add_argument("--post", default=None, metavar="RESULT_JSON")
    ap.add_argument("--compare", nargs=2, metavar="RESULT_JSON")
    a = ap.parse_args(argv)
    if a.compare:
        ok, msg = compare_runs(*a.compare)
        print(("SAME: " if ok else "DIFFER: ") + msg)
        return 0 if ok else 1
    if a.post:
        rep = post(a.post)
        print("post: %s -> %s" % (json.dumps(rep["counts"], default=str)[:600], OUT_DIR))
        return 0
    if not (a.live or a.mock):
        ap.print_help()
        return 2
    if a.no_shots and a.sweep_shots:
        ap.error("--no-shots and --sweep-shots are opposites")
    global PROBE_POLL_S
    PROBE_POLL_S = a.probe_poll
    if a.sweep_shots and a.shot_settle is None:
        a.shot_settle = 0.7
    B = MockBridge(a.fault) if a.mock else LiveBridge()
    res = run(a, B, mock=a.mock)
    if a.sweep_shots:
        n = merge_sweep(a.sweep_shots, res, a.out or a.sweep_shots)
        print("sweep: %d shot records merged into %s" % (n, a.out or a.sweep_shots))
    elif a.live:
        os.makedirs(RESULT_DIR, exist_ok=True)
        out = a.out or os.path.join(RESULT_DIR, "matrix_live_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        print("result -> %s" % out)
    elif a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
    print("%s: %s ticks %s wall %ss calls %s boards %d aborted %s" % (
        res["mode"].upper(), res["summary"], res["ticks_spent"], res["wall_s"], res["calls"], len(res["boards"]), res["aborted"]))
    print("TIMING %ss wall, %d shots: %s" % (res["wall_s"], res["timing"]["shots_taken"],
          ", ".join("%s %ss" % kv for kv in res["timing"]["phases_s"].items())))
    cp = res["timing"].get("calls_profile")
    if cp:
        print("PROFILE (name n total_s avg_s), top 25:")
        for k, v in list(cp.items())[:25]:
            print("  %-34s %5d %8.1f %7.3f" % (k, v["n"], v["total_s"], v["avg_s"]))
    for b in (res["boards"] if not a.mock else []):
        print("  %-14s %s" % (b["id"], b.get("phases_s")))
    return 0 if not res["aborted"] else 1


if __name__ == "__main__":
    sys.exit(main())
