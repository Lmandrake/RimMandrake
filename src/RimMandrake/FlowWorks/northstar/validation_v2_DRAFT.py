"""validation_v2_DRAFT.py -- FlowWorks functional script v2 (DRAFT, not wired into modcheck).

Plan (authority): design/RimMandrake/flowworks_northstar_script_plan_2026-10-02.md
Evidence:         design/RimMandrake/flowworks_northstar_interrogation_2026-10-02.md ("INT")

This does NOT replace src/RimMandrake/FlowWorks/validation.py and never edits the walk.

    python3 src/RimMandrake/FlowWorks/northstar/validation_v2_DRAFT.py --offline
        tier O: defs, settings defaults, UNBUILT register, geometry, pulse-oracle selftest.
        0 game ticks, no bridge. Exit 0 = every offline check PASS.

    (live)  `suite` below is a modcheck Suite, built only when modcheck imports. Its chains
        expect the pristine save NS_FlowWorks_Bland_v2 (plan section 2) to be LOADED, paused,
        on the `flowworks` modset tier. Live use is UNPROVEN: every live predicate is UNMEASURED
        until a first run.

Design rules (plan section 1):
  R1 static absolute plots, validated offline; R2 a cell is used by one scene per load;
  R3 one ActiveFluid per load; R4 zero ticks first; R5 time in PULSES at a pinned 60-tick
  pulse, exact predicted F vectors from PulseOracle; R6 read the quantity, not a proxy;
  R7 stimulate without pathing; R8 every positive has a same-scene negative control;
  R9 UNBUILT features are recorded from a source fact, not staged to fail; R10 few reads.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)                       # src/RimMandrake/FlowWorks
SRC = os.path.join(MOD, "Source")
DEFS = os.path.join(MOD, "Defs")

MAP_W = MAP_H = 250        # the bland save's map size; L5 refuses a different size
SINK_BAND = 10             # GenGrid.NoBuildEdgeWidth (RM_MapComponent_Excavation.IsSinkCell)
PULSE_PIN = 60             # RimMandrakeFlowWorksSettings.PulseIntervalTicks clamp floor
PULSE_SHIPPED = 250

S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
S_PITS = "RimMandrake.FlowWorks.Pits.PitsSettings"
S_RIVER = "RimMandrake.FlowWorks.ManyWaters.RiverSteamSettings"

# Shipped defaults (O2 cross-checks these against the C# initializers AND Scribe defaults).
BOOL_DEFAULTS = {
    S_FW: dict(depthEngineEnabled=True, channelConfinementEnabled=True, digToDepthEnabled=True,
               liquidCorrosionEnabled=False, liquidIgnitionEnabled=False, fillInEnabled=True,
               fillInDisplacementEnabled=True, sourceBudgetEnabled=True, stickyLimitlessEnabled=True,
               recessionEnabled=True, refillEnabled=True, rainFillsExcavationsEnabled=True,
               edgeSinksEnabled=True, superdeepCaptureEnabled=True, superdeepCapturesOwnFaction=False,
               ladderRequiredToExitEnabled=True, superdeepShootingRuleEnabled=True,
               bottleLoopEnabled=True, bottleDirtyStageEnabled=True, tankLoopEnabled=True,
               liquidDrillingEnabled=True, typedLiquidShoresEnabled=True),
    S_PITS: dict(trapTriggerEnabled=True, fallDamageEnabled=True, escapeEnabled=True,
                 pitCellExposureEnabled=True),
    S_RIVER: dict(riverSteamEnabled=True),
}
FLOAT_DEFAULTS = {"pulseIntervalTicks": 250.0, "flowPerPulse": 1.0, "rainFillPerPulse": 0.1,
                  "minLimitlessBodyCells": 50.0}


# ============================================================================ the pulse oracle
CARDINAL = [(0, 1), (1, 0), (0, -1), (-1, 0)]   # GenAdj.CardinalDirections: N, E, S, W


class PulseOracle(object):
    """A pure-Python port of RM_MapComponent_Excavation.DoPulse / ResolveComponent / PickDonor /
    CompareDeepestFirst (Source/RM_MapComponent_Excavation.cs l.762-1025), for the depth engine
    only: no rain (weather pinned Clear), no recession/refill (stock.Pulse) -- scenes are chosen
    so neither changes the predicted vector (plan section 3, E-tier). Deterministic by
    construction: recipients sorted (-D, cell index), donors scanned N,E,S,W with strict '>'.

    VALIDATED once against live data (INT section 2): given plot D's geometry (5x5 limited pond,
    12-cell D=3 channel running east, stock 125) it reproduces BOTH oscillating F vectors the
    2026-10-01 run recorded at ticks 538,130..539,880, exactly."""

    def __init__(self, w, h, sources, bodies, per=1, budget=True, sink_band=None):
        self.w, self.h = w, h
        self.D, self.F = {}, {}
        self.src = dict(sources)          # cell -> body id
        self.bodies = bodies              # id -> {"limitless": bool, "stock": float}
        self.per, self.budget, self.sink_band = per, budget, sink_band
        self.drained = 0

    def idx(self, c):
        return c[1] * self.w + c[0]

    def inb(self, c):
        return 0 <= c[0] < self.w and 0 <= c[1] < self.h

    def exc(self, c):
        return self.D.get(c, 0) > 0

    def is_source(self, c):
        return c in self.src and not self.exc(c)

    def can_supply(self, c):
        if not self.budget:
            return True
        b = self.bodies[self.src[c]]
        return b["limitless"] or b["stock"] >= 1

    def is_sink(self, c):
        if self.sink_band is None or not self.exc(c):
            return False
        x, z = c
        return x < self.sink_band or z < self.sink_band or x >= self.w - self.sink_band or z >= self.h - self.sink_band

    def dig(self, c, levels=1):
        self.D[c] = min(4, self.D.get(c, 0) + levels)
        self.F.setdefault(c, 0)

    def set_fill(self, c, f):
        if not self.exc(c):
            return False
        self.F[c] = max(0, min(f, self.D[c]))
        return True

    def _pick(self, r, dr):
        best, best_score = None, -1
        for dx, dz in CARDINAL:
            n = (r[0] + dx, r[1] + dz)
            if not self.inb(n):
                continue
            src = self.is_source(n)
            if src:
                if not self.can_supply(n):
                    continue
                dn = fn = 4
            else:
                dn = self.D.get(n, 0)
                if dn == 0:
                    continue
                fn = self.F[n]
            if fn == 0:
                continue
            if dr <= dn and fn < dn:
                continue
            score = 1000 if src else fn * 10 + dn
            if score > best_score:
                best_score, best = score, n
        return best

    def pulse(self):
        seen = set()
        for seed in sorted(self.D, key=self.idx):
            if seed in seen or not self.exc(seed):
                continue
            comp, queue = [], [seed]
            seen.add(seed)
            while queue:
                c = queue.pop(0)
                comp.append(c)
                if self.is_source(c):
                    continue
                for dx, dz in CARDINAL:
                    n = (c[0] + dx, c[1] + dz)
                    if n in seen or not self.inb(n):
                        continue
                    if self.exc(n) or self.is_source(n):
                        seen.add(n)
                        queue.append(n)
            for c in comp:                                   # sinks drain before the flow
                if self.exc(c) and self.is_sink(c):
                    take = min(self.F[c], self.per)
                    self.F[c] -= take
                    self.drained += take
            rec = sorted([c for c in comp if self.exc(c) and self.F[c] < self.D[c]],
                         key=lambda c: (-self.D[c], self.idx(c)))
            for r in rec:
                moved = 0
                while moved < self.per and self.F[r] < self.D[r]:
                    d = self._pick(r, self.D[r])
                    if d is None:
                        break
                    if self.is_source(d):
                        b = self.bodies[self.src[d]]
                        if self.budget and not b["limitless"]:
                            if b["stock"] < 1:
                                break
                            b["stock"] -= 1
                    else:
                        self.F[d] -= 1
                    self.F[r] += 1
                    moved += 1

    def run(self, cells, pulses):
        out = []
        for _ in range(pulses):
            self.pulse()
            out.append([self.F[c] for c in cells])
        return out


def rect_cells(x, z, w, h):
    return [(x + i, z + j) for i in range(w) for j in range(h)]


# ============================================================================ the site (R1/R2)
# Absolute cells on the 250x250 bland save. Water bodies are PAINTED by the save builder;
# everything else starts as undug Soil. Every scene owns its cells; O4 proves disjointness.
BODIES = {
    "W1": dict(cells=rect_cells(0, 100, 16, 4), limitless=True),     # west edge, 64 cells
    "W2": dict(cells=[(60, 60)], limitless=False, capacity=5),
    "W3": dict(cells=[(60, 80), (61, 80)], limitless=False, capacity=10),
    "W4": dict(cells=rect_cells(0, 140, 10, 4), limitless=False),    # edge, 40 < 50 cells
    "W5": dict(cells=rect_cells(100, 100, 8, 8), limitless=False),   # 64 cells, interior
    "W6": dict(cells=rect_cells(0, 170, 16, 4), limitless=False),    # classified with sticky OFF
    "W7": dict(cells=rect_cells(0, 180, 16, 4), limitless=True),     # identical twin, sticky ON
}


def _run(x, z, n, dx, dz):
    return [(x + dx * i, z + dz * i) for i in range(n)]


SCENES = {
    # E2 -- channels off W1 (limitless). East/north = index ascending away from the source.
    "E2_east_A": dict(cells=_run(16, 100, 4, 1, 0), D=1, body="W1", dir="E"),
    "E2_east_B": dict(cells=_run(16, 103, 4, 1, 0), D=1, body="W1", dir="E"),   # twin of A
    "E2_north": dict(cells=_run(12, 104, 4, 0, 1), D=1, body="W1", dir="N"),
    "E2_south": dict(cells=_run(12, 99, 4, 0, -1), D=1, body="W1", dir="S"),
    # E3 -- W2 (cap 5) feeding an 8-cell south-running channel (south: no oscillation confound)
    "E3_budget": dict(cells=_run(60, 59, 8, 0, -1), D=1, body="W2", dir="S"),
    # E4 -- W3 (cap 10), engine on/off
    "E4_engine": dict(cells=_run(60, 79, 4, 0, -1), D=1, body="W3", dir="S"),
    # E5 -- sink band vs interior twin, no source (fill set by the driver)
    "E5_sink": dict(cells=[(170, 5), (171, 5)], D=1, sink=True),
    "E5_inner": dict(cells=[(170, 20), (171, 20)], D=1),
    "E5_sink_off": dict(cells=[(174, 5), (175, 5)], D=1, sink=True),
    # E6 -- rain
    "E6_open": dict(cells=[(180, 60)], D=1),
    "E6_roofed": dict(cells=[(182, 60)], D=1, roof=(181, 59, 3, 3)),
    "E6_toggle_off": dict(cells=[(186, 60)], D=1),
    # E7 -- fill-in displacement (engine OFF): F = 0,2,2 then fill in the middle
    "E7_on": dict(cells=[(190, 60), (191, 60), (192, 60)], D=2),
    "E7_off": dict(cells=[(195, 60), (196, 60), (197, 60)], D=2),
    # E8 -- the player dig path
    "E8_dig": dict(cells=[(200, 60)], D=0),
    # S-tier, zero ticks
    "S1_ladder": dict(cells=[(130, 60), (132, 60), (134, 60), (136, 60)]),
    "S2_clamp": dict(cells=[(130, 64), (132, 64)]),
    "S4_band": dict(cells=[(130, 9), (130, 11)], sink=True),
    "S6_digdepth": dict(cells=[(140, 64), (142, 64)]),
    "S7_capture": dict(cells=[(150, 60), (152, 60), (154, 60)]),
    "S8_capture_off": dict(cells=[(156, 60)]),
    "S9_ladder": dict(cells=[(160, 60), (162, 60), (162, 61)]),
}


def edge_distance(c):
    return min(c[0], c[1], MAP_W - 1 - c[0], MAP_H - 1 - c[1])


def oracle_for(scene_key, pulses):
    """Predicted F vectors for one E-tier channel scene (per pulse)."""
    s = SCENES[scene_key]
    body = BODIES[s["body"]]
    stock = 0.0 if body["limitless"] else float(body.get("capacity", 5 * len(body["cells"])))
    o = PulseOracle(MAP_W, MAP_H, {c: 0 for c in body["cells"]},
                    {0: {"limitless": body["limitless"], "stock": stock}}, sink_band=SINK_BAND)
    for c in s["cells"]:
        o.dig(c, s["D"])
    return o.run(s["cells"], pulses)


# ============================================================================ tier O (offline)
class Check(object):
    def __init__(self, cid, ok, detail=""):
        self.cid, self.ok, self.detail = cid, ok, detail

    def __repr__(self):
        return "%-4s %-6s %s" % (self.cid, "PASS" if self.ok else "FAIL", self.detail)


def _xml_blocks():
    out = {}
    for root, _, files in os.walk(DEFS):
        for fn in files:
            if fn.endswith(".xml"):
                t = open(os.path.join(root, fn), encoding="utf-8").read()
                for m in re.finditer(r"<([\w.]+)(\s[^>]*)?>\s*(?:<!--.*?-->\s*)*<defName>([^<]+)</defName>(.*?)</\1>", t, re.S):
                    out[m.group(3)] = (m.group(1), m.group(2) or "", m.group(4), fn)
    return out


def _field(block, name):
    m = re.search(r"<%s>(.*?)</%s>" % (name, name), block, re.S)
    return m.group(1).strip() if m else None


def o1_defs():
    defs = _xml_blocks()
    probs = []
    if "RM_Channel_Empty" not in defs:            # sanity probe: the parser can find a known def
        return Check("O1", False, "parser blind: RM_Channel_Empty not found (%d defs)" % len(defs))
    w = defs.get("RM_Fluid_Water")
    if not w:
        probs.append("RM_Fluid_Water missing")
    else:
        for f, want in (("floodTerrain", "RM_Fill_Water_Trace"), ("volumePerTile", "1"),
                        ("canalCellsPerSourceCell", "5"), ("ticksPerTile", "60")):
            if _field(w[2], f) != want:
                probs.append("RM_Fluid_Water.%s=%r want %r" % (f, _field(w[2], f), want))
    for name, cost in (("RM_Channel_Empty", "30"), ("RM_Channel_Mid", "45"),
                       ("RM_Channel_Deep", "80"), ("RM_Channel_Superdeep", "300")):
        b = defs.get(name)
        if not b or _field(b[2], "pathCost") != cost:
            probs.append("%s pathCost %r want %s" % (name, b and _field(b[2], "pathCost"), cost))
    sp = defs.get("RM_SuperdeepPit")
    if not sp or _field(sp[2], "drawerType") != "None":
        probs.append("RM_SuperdeepPit drawerType is not None (the holder must be invisible)")
    lad = defs.get("RM_Ladder")
    if not lad or "PlaceWorker_LadderOnExcavation" not in lad[2]:
        probs.append("RM_Ladder lacks PlaceWorker_LadderOnExcavation")
    for n in ("RM_DigCanal", "RM_FillInCanal", "RM_DigCanalJob", "RM_DigCanalWorkGiver",
              "RM_Fluid_Tar", "RM_Fluid_SlimeGreen", "RM_SuperdeepPit"):
        if n not in defs:
            probs.append("missing def " + n)
    return Check("O1", not probs, "; ".join(probs) or "%d defs parsed" % len(defs))


def o2_settings_defaults():
    probs, seen = [], 0
    srcs = {}
    for root, _, files in os.walk(SRC):
        for fn in files:
            if fn.endswith(".cs"):
                srcs[fn] = open(os.path.join(root, fn), encoding="utf-8").read()
    allsrc = "\n".join(srcs.values())
    for typ, fields in BOOL_DEFAULTS.items():
        for f, want in fields.items():
            m1 = re.search(r"public static bool %s\s*=\s*(true|false)" % f, allsrc)
            m2 = re.search(r'Scribe_Values\.Look\(ref %s, "%s", (true|false)\)' % (f, f), allsrc)
            seen += 1
            got = {m1 and m1.group(1), m2 and m2.group(1)}
            if got != {str(want).lower()}:
                probs.append("%s: init/scribe %s want %s" % (f, sorted(map(str, got)), want))
    for f, want in FLOAT_DEFAULTS.items():
        m1 = re.search(r"public static float %s\s*=\s*([\d.]+)f" % f, allsrc)
        if not m1 or float(m1.group(1)) != want:
            probs.append("%s=%s want %s" % (f, m1 and m1.group(1), want))
    if seen != 27:
        probs.append("toggle census %d != 27" % seen)
    return Check("O2", not probs, "; ".join(probs) or "27 toggles + 4 floats match C#")


# UNBUILT register (R9): bar -> (source fact that keeps it UNBUILT, predicate over sources).
def _src_all():
    out = []
    for root, _, files in os.walk(SRC):
        for fn in files:
            if fn.endswith(".cs"):
                out.append(open(os.path.join(root, fn), encoding="utf-8").read())
    return "\n".join(out)


def _engine_src():
    return open(os.path.join(SRC, "RM_MapComponent_Excavation.cs"), encoding="utf-8").read()


UNBUILT = {
    "fill_fluid_distinct": ("one activeFluid field per map component",
                            lambda s, d: "private FluidDef activeFluid;" in s),
    "pit_covered_invisible": ("no superdeep cover (only legacy Building_TerrainMimicCover)",
                              lambda s, d: "SuperdeepCover" not in s),
    "pit_covered_seam_at_max_zoom": ("same as pit_covered_invisible", lambda s, d: "SuperdeepCover" not in s),
    "sluice_gate_state_legible": ("no Sluice def", lambda s, d: not any("Sluice" in k for k in d)),
    "spikes_read_distinct": ("no per-cell spike def on excavations (RM_OpenPit_Spiked / RM_PitDigSite_*_Spiked are the legacy building pit)",
                             lambda s, d: not any("Spike" in k and k.startswith("RM_")
                                                  and not k.startswith(("RM_OpenPit", "RM_PitDigSite", "RM_PitCell")) for k in d)),
    "ladder_state_legible": ("RM_Ladder has no raised/lowered state (thingClass Building)",
                             lambda s, d: d.get("RM_Ladder") is not None and "<thingClass>Building</thingClass>" in d["RM_Ladder"][2]),
    "tar_fill_front_lags_water": ("FlowPerPulse is global; viscosity not read by the engine",
                                  lambda s, d: "viscosity" not in re.sub(r"//.*", "", _engine_src()).lower()),
    "pawn_height_ladder_legible": ("no pawn draw offset by depth", lambda s, d: not re.search(r"DepthAt\([^)]*\)[^;\n]*(DrawPos|DrawOffset|drawLoc)", s)),
    "pawn_lowers_on_deeper_cell": ("same", lambda s, d: not re.search(r"DepthAt\([^)]*\)[^;\n]*(DrawPos|DrawOffset|drawLoc)", s)),
    "pawn_rises_on_shallower_cell": ("same", lambda s, d: not re.search(r"DepthAt\([^)]*\)[^;\n]*(DrawPos|DrawOffset|drawLoc)", s)),
    "pit_trapped_reads_as_trapped": ("same (walls above head need the offset)", lambda s, d: not re.search(r"DepthAt\([^)]*\)[^;\n]*(DrawPos|DrawOffset|drawLoc)", s)),
    "slime_occupant_below_surface": ("same", lambda s, d: not re.search(r"DepthAt\([^)]*\)[^;\n]*(DrawPos|DrawOffset|drawLoc)", s)),
}


def o3_unbuilt_register():
    s, d = _src_all(), _xml_blocks()
    landed = [bar for bar, (_, pred) in UNBUILT.items() if not pred(s, d)]
    # A landed feature is a PROMOTION (stage the bar now), reported, not a failure of the mod.
    return Check("O3", True, "%d UNBUILT bars registered; FEATURE LANDED, stage now: %s"
                 % (len(UNBUILT) - len(landed), landed or "none"))


def o4_geometry():
    probs, owner = [], {}
    for name, b in BODIES.items():
        for c in b["cells"]:
            owner.setdefault(c, []).append(name)
        if b["limitless"] and not any(edge_distance(c) == 0 for c in b["cells"]):
            probs.append("%s declared limitless but touches no edge" % name)
        if b["limitless"] and len(b["cells"]) < FLOAT_DEFAULTS["minLimitlessBodyCells"]:
            probs.append("%s declared limitless with %d < 50 cells" % (name, len(b["cells"])))
    for name, s in SCENES.items():
        for c in s["cells"]:
            if not (0 <= c[0] < MAP_W and 0 <= c[1] < MAP_H):
                probs.append("%s cell %s out of bounds" % (name, c))
            owner.setdefault(c, []).append(name)
            in_band = edge_distance(c) < SINK_BAND
            if in_band and not s.get("sink"):
                probs.append("%s cell %s in the sink band but not declared a sink scene" % (name, c))
    dup = {c: o for c, o in owner.items() if len(o) > 1}
    if dup:
        probs.append("cells shared by scenes/bodies: %s" % list(dup.items())[:4])
    # channels must not touch any other scene's cells (separate components)
    allc = {c: n for n, s in SCENES.items() for c in s["cells"]}
    for n, s in SCENES.items():
        for c in s["cells"]:
            for dx, dz in CARDINAL:
                m = allc.get((c[0] + dx, c[1] + dz))
                if m and m != n:
                    probs.append("%s touches %s at %s" % (n, m, c))
    return Check("O4", not probs, "; ".join(sorted(set(probs)))[:600] or
                 "%d scenes, %d bodies, all in bounds and disjoint" % (len(SCENES), len(BODIES)))


def o5_oracle_selftest():
    probs = []
    # (1) the live reproduction (INT section 2) -- plot D geometry, 2026-10-01 run
    px, pz = 167, 204
    o = PulseOracle(250, 250, {c: 0 for c in rect_cells(px, pz, 5, 5)},
                    {0: {"limitless": False, "stock": 125.0}})
    cells = _run(px + 5, pz + 2, 12, 1, 0)
    for c in cells:
        o.dig(c, 3)
    hist = [tuple(v) for v in o.run(cells, 60)]
    live = [(3, 3, 2, 3, 3, 2, 2, 3, 3, 2, 2, 3), (3, 3, 3, 2, 2, 3, 3, 2, 2, 3, 3, 2)]
    if not all(v in hist[-10:] for v in live):
        probs.append("oracle no longer reproduces the measured live oscillation")
    # (2) hand-worked: 3-cell east channel off a limitless source oscillates, south fills
    def chan(dx, dz, n=3, p=12):
        oo = PulseOracle(100, 100, {(50, 50): 0}, {0: {"limitless": True, "stock": 0}})
        cs = _run(50 + dx, 50 + dz, n, dx, dz)
        for c in cs:
            oo.dig(c)
        return oo.run(cs, p)
    e, s = chan(1, 0), chan(0, -1)
    if e[-2:] != [[1, 0, 1], [1, 1, 0]] and e[-2:] != [[1, 1, 0], [1, 0, 1]]:
        probs.append("east 3-cell: %s (hand-worked: period-2 [1,0,1]<->[1,1,0])" % e[-2:])
    if s[-1] != [1, 1, 1]:
        probs.append("south 3-cell final %s want [1,1,1]" % s[-1])
    # (3) determinism: identical inputs, identical outputs
    if oracle_for("E2_east_A", 8) != oracle_for("E2_east_A", 8):
        probs.append("oracle non-deterministic")
    # (4) budget: W2 (cap 5) -> E3 channel receives exactly 5 levels and no more. The VECTOR does
    # not come to rest: a partly filled equal-depth run keeps shuttling units (period 2) after
    # the source is spent -- the same OVERFLOW-clause behaviour as the east/north oscillation
    # (INT section 2). So the check is on the SUM, and E3 asserts the exact oracle vector.
    v = oracle_for("E3_budget", 14)
    if any(sum(row) != 5 for row in v[-4:]):
        probs.append("E3 budget: last sums %s (want 5)" % [sum(r) for r in v[-4:]])
    return Check("O5", not probs, "; ".join(probs) or "live oscillation reproduced; hand cases; budget 5")


def run_offline():
    checks = [o1_defs(), o2_settings_defaults(), o3_unbuilt_register(), o4_geometry(), o5_oracle_selftest()]
    for c in checks:
        print(c)
    print("E2 predictions (8 pulses, last 2):")
    for k in ("E2_east_A", "E2_north", "E2_south"):
        print("  %-10s %s" % (k, oracle_for(k, 8)[-2:]))
    return 0 if all(c.ok for c in checks) else 1


# ============================================================================ live tiers (modcheck)
try:
    sys.path.insert(0, os.path.join(MOD, "..", "Utils"))
    from modcheck import Suite, ExpectationFailed      # noqa: E402
except Exception:                                      # offline use needs no modcheck
    Suite = None

    class ExpectationFailed(Exception):
        pass


def _ok(r):
    return bool((r or {}).get("success"))


def _need(cond, msg):
    if not cond:
        raise ExpectationFailed(msg)


def _rep(t, c):
    r = t.bridge_call("jawa/flowworks_excavation_report", x=c[0], z=c[1])
    _need(_ok(r), "excavation_report%s failed: %r" % (c, r))
    return r


def _vec(t, cells):
    return [_rep(t, c).get("fill") for c in cells]


def _engine(t):
    r = t.bridge_call("jawa/flowworks_engine_state")
    _need(_ok(r), "engine_state failed: %r" % (r,))
    return r


def _dig(t, c, n):
    r = t.bridge_call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=-1)
    _need(_ok(r), "dig %s failed: %r" % (c, r))
    return r


def _fill(t, c, f):
    return t.bridge_call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=f)


def _step_pulses(t, n):
    """R5: land exactly one tick after each of the next n pulses (pulse fires at tick >= next)."""
    for _ in range(n):
        until = _engine(t).get("ticksUntilNextPulse")
        t.wait_ticks(int(until) + 1)


def _body(t, cell, classify=True):
    r = t.bridge_call("jawa/flowworks_body_report", x=cell[0], z=cell[1], classify=classify)
    _need(_ok(r), "body_report%s failed: %r" % (cell, r))
    return r.get("body") or {}


if Suite is not None:
    suite = Suite("FlowWorks_v2_DRAFT")
    suite.toggles = [f for d in BOOL_DEFAULTS.values() for f in d]

    @suite.chain("L_preflight")
    def chain_preflight(t):
        with t.component("L4_settings_at_defaults"):
            for typ, fields in BOOL_DEFAULTS.items():
                for f, want in fields.items():
                    r = t.bridge_call("jawa/mod_settings_field", typeName=typ, action="get", field=f)
                    _need(_ok(r) and str(r.get("value")) == str(want), "%s=%r, shipped %s" % (f, r, want))
        with t.component("L5_site_pristine"):
            e = _engine(t)
            _need(e.get("excavatedCellCount") == 0 and e.get("bodyCount") == 0,
                  "site not pristine: %r" % e)
            _need(e.get("pulseIntervalTicks") == PULSE_SHIPPED, "pulse interval %r" % e.get("pulseIntervalTicks"))
        with t.component("L4_pin_pulse"):
            t.set_setting(S_FW, {"pulseIntervalTicks": float(PULSE_PIN)})
            _need(_engine(t).get("pulseIntervalTicks") == PULSE_PIN, "pulse pin not read back")

    @suite.chain("S_state_zero_ticks")
    def chain_state(t):
        cells = SCENES["S1_ladder"]["cells"]
        with t.component("S1_dig_ladder", shows=["pit_depth_ladder_legible", "canal_reads_as_dug_channel"]):
            for d, c in enumerate(cells, 1):
                _dig(t, c, d)
            _need([_rep(t, c).get("depth") for c in cells] == [1, 2, 3, 4], "depth ladder wrong")
            for c, ter in zip(cells, ("RM_Channel_Empty", "RM_Channel_Mid", "RM_Channel_Deep", "RM_Channel_Superdeep")):
                r = t.bridge_call("jawa/canal_cell_report", x=c[0], z=c[1])
                _need(_ok(r) and (r.get("terrain") == ter or (r.get("cell") or {}).get("terrain") == ter),
                      "terrain at %s is not %s: %r" % (c, ter, r))
            # neg: deepening a D=4 cell stays 4 (LAW 1 max)
            _need(_dig(t, cells[3], 1).get("depth") == 4, "D=4 deepened past SUPERDEEP")
            h = t.bridge_call("jawa/list_things", defName="RM_SuperdeepPit", rect="%d,%d,1,1" % cells[3])
            h3 = t.bridge_call("jawa/list_things", defName="RM_SuperdeepPit", rect="%d,%d,1,1" % cells[2])
            _need(len((h or {}).get("things") or []) == 1 and not (h3 or {}).get("things"),
                  "holder must exist at D=4 only")
        a, b = SCENES["S2_clamp"]["cells"]
        with t.component("S2_fill_clamp"):
            _dig(t, a, 2)
            _need(_fill(t, a, 9).get("fill") == 2, "F not clamped to D")
            r = _fill(t, b, 1)
            _need(r.get("fillSet") is False and r.get("fill") == 0, "driver wrote fill on undug ground: %r" % r)
        with t.component("S3_classification"):
            got = {k: _body(t, BODIES[k]["cells"][0]) for k in ("W1", "W2", "W3", "W4", "W5")}
            _need(got["W1"].get("limitless") is True, "sanity probe: W1 (edge, 64) not limitless")
            for k in ("W2", "W3", "W4", "W5"):
                _need(got[k].get("limitless") is False, "%s should be LIMITED: %r" % (k, got[k]))
            _need(got["W2"].get("capacity") == 5 and got["W3"].get("capacity") == 10, "capacities %r" % got)
        with t.component("S4_sink_band", toggle="edgeSinksEnabled"):
            band, inner = SCENES["S4_band"]["cells"]
            _dig(t, band, 1)
            _dig(t, inner, 1)
            _need(_rep(t, band).get("isSinkCell") is True and _rep(t, inner).get("isSinkCell") is False,
                  "sink band misread")
        with t.component("S5_sticky_limitless", toggle="stickyLimitlessEnabled"):
            t.set_setting(S_FW, {"stickyLimitlessEnabled": False})
            try:
                off = _body(t, BODIES["W6"]["cells"][0])
            finally:
                t.set_setting(S_FW, {"stickyLimitlessEnabled": True})
            on = _body(t, BODIES["W7"]["cells"][0])
            _need(off.get("limitless") is False and on.get("limitless") is True, "sticky toggle: %r / %r" % (off, on))
        # S6/S7/S8/S9: designation and capture -- shapes of designate_batch/pawn_get are
        # UNMEASURED; written against tool_schemas.json parameter names, response keys to verify.
        with t.component("S7_capture_on_cell", toggle="superdeepCaptureEnabled",
                         shows=["pit_occupant_below_floor", "never_snared_standing"]):
            hp, cp, h3 = SCENES["S7_capture"]["cells"]
            _dig(t, hp, 4)
            _dig(t, cp, 4)
            _dig(t, h3, 3)
            ids = {}
            for k, c, fac in (("hostile", hp, "hostile"), ("colonist", cp, "player"), ("hostile_d3", h3, "hostile")):
                r = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist" if fac == "player" else "Pirate",
                                  x=c[0], z=c[1], faction=fac, count=1)
                _need(_ok(r), "spawn %s failed: %r" % (k, r))
                ids[k] = r["pawns"][0]["id"]
            t.wait_ticks(2)
            rows = {p.get("id"): p for p in (t.bridge_call("jawa/list_pawns", limit=500, includeCorpses=True) or {}).get("pawns") or []}
            cap = rows.get(ids["hostile"])
            # No `cap is None` escape: a missing row is an instrument failure, not a capture.
            # TODO (owed tool jawa/flowworks_pit_report): assert the holder's innerContainer holds ids["hostile"].
            _need(cap is not None and cap.get("spawned") is False and cap.get("dead") is False,
                  "hostile on D=4 not proven captured alive: %r" % cap)
            _need((rows.get(ids["colonist"]) or {}).get("spawned") is True, "own colonist captured by default")
            _need((rows.get(ids["hostile_d3"]) or {}).get("spawned") is True, "D=3 captured a pawn (only D=4 may)")

    @suite.chain("E_engine_pulses")
    def chain_engine(t):
        with t.component("E2_channel_vs_oracle",
                         shows=["canal_fill_spreads_along_itself", "canal_holds_only_the_channel",
                                "never_liquid_on_open_ground", "canal_fill_front_watchable"]):
            keys = ("E2_east_A", "E2_east_B", "E2_north", "E2_south")
            for k in keys:
                for c in SCENES[k]["cells"]:
                    _dig(t, c, 1)
            # 8 pulses: the south 4-cell control first reads full at pulse 7 (oracle; GPT review caught
            # an earlier 6-pulse version that would have failed its own control).
            pred = {k: oracle_for(k, 8) for k in keys}
            for p in range(1, 9):
                _step_pulses(t, 1)
                if p in (1, 3, 8):
                    for k in keys:
                        live = _vec(t, SCENES[k]["cells"])
                        _need(live == pred[k][p - 1],
                              "%s pulse %d: live %s != oracle %s (HARNESS if A==B, else MOD)" % (k, p, live, pred[k][p - 1]))
            _need(_vec(t, SCENES["E2_east_A"]["cells"]) == _vec(t, SCENES["E2_east_B"]["cells"]), "twins differ")
        with t.component("E2_channels_fill", shows=[]):
            # The bar-level claim. EXPECTED RED on east/north until FLOWWORKS_CHANNEL_OSCILLATION_1;
            # the south twin is the negative control that must be GREEN.
            south = _vec(t, SCENES["E2_south"]["cells"])
            _need(all(f == 1 for f in south), "south channel did not fill: %s" % south)
            for k in ("E2_east_A", "E2_north"):
                v = _vec(t, SCENES[k]["cells"])
                _need(all(f == 1 for f in v), "%s channel never fills (oscillation, INT section 2): %s" % (k, v))
        with t.component("E3_budget_exhaustion",
                         shows=["empty_reservoir_stops_flow", "reservoir_fill_visibly_drops",
                                "never_full_reservoir_after_heavy_draw"]):
            cells = SCENES["E3_budget"]["cells"]
            # Recession OFF for the accounting: a spent 1-cell pond that recedes is no longer a source,
            # so the budget-OFF negative control could never supply (GPT review). Recession is owed
            # its own scene (body.recededCount), not a rider on this one.
            t.set_setting(S_FW, {"recessionEnabled": False})
            for c in cells:
                _dig(t, c, 1)
            pred = oracle_for("E3_budget", 14)
            _step_pulses(t, 14)
            live = _vec(t, cells)
            _need(live == pred[-1], "E3 live %s != oracle %s" % (live, pred[-1]))
            b = _body(t, BODIES["W2"]["cells"][0], classify=False)
            _need(sum(live) == 5 and (b.get("stock") or 0) < 1, "budget: sum %d stock %r" % (sum(live), b))
            _step_pulses(t, 2)                                           # stops: sum unchanged
            _need(sum(_vec(t, cells)) == 5, "a spent body kept supplying")
            t.set_setting(S_FW, {"sourceBudgetEnabled": False})       # neg control: budget OFF
            try:
                _step_pulses(t, 2)
                _need(sum(_vec(t, cells)) > 5, "budget OFF did not let a spent body supply")
            finally:
                t.set_setting(S_FW, {"sourceBudgetEnabled": True, "recessionEnabled": True})
        with t.component("E4_engine_off", toggle="depthEngineEnabled"):
            cells = SCENES["E4_engine"]["cells"]
            t.set_setting(S_FW, {"depthEngineEnabled": False})
            try:
                for c in cells:
                    _dig(t, c, 1)
                n0 = _engine(t).get("nextPulseTick")
                t.wait_ticks(2 * PULSE_PIN)
                _need(_vec(t, cells) == [0, 0, 0, 0] and _engine(t).get("nextPulseTick") == n0,
                      "engine moved while OFF")
            finally:
                t.set_setting(S_FW, {"depthEngineEnabled": True})
            _step_pulses(t, 1)
            _need(sum(_vec(t, cells)) >= 1, "engine ON did not move liquid (neg control)")

    @suite.chain("U_unbuilt_register")
    def chain_unbuilt(t):
        """R9: each UNBUILT bar FAILS with its source fact, at zero ticks, until the fact flips."""
        s, d = _src_all(), _xml_blocks()
        for bar, (fact, pred) in sorted(UNBUILT.items()):
            with t.component("unbuilt_" + bar, shows=[bar]):
                # Never PASSes: a flipped fact means "feature landed -- stage a scene", not green.
                _need(False, ("UNBUILT: %s" % fact) if pred(s, d) else
                      "FEATURE LANDED (source fact flipped): stage a real scene for %s" % bar)


if __name__ == "__main__":
    if "--offline" in sys.argv or len(sys.argv) == 1:
        sys.exit(run_offline())
