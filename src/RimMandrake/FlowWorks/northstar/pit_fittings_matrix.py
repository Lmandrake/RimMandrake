"""RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL: the pit-fittings acceptance matrix, one live scene.

    python.exe pit_fittings_matrix.py <repo_win_path> <out_win_dir> [stage|fill|read|shots|all|save:<name>]

Owner, 2026-11-12 (the standing test principle for 1-on-1 looks): "Acceptance tests really should have pits like this
prepared that span many pit depths + water depths to ensure the art works everywhere, for NSEW ladders (steel and wood),
plus ramps, spikes, gates, and anything else we've installed, plus items in the pit with it, etc. It's not hard to prepare
one such pit and simply replicate it and its contents in a matrix with different depths of pit and water fill..."

ONE prepared pit (5x5 dug squares) is replicated over a grid: a row per pit depth, a column per whole-notch fill from dry
to brim (one notch = 0.5 m). Depths 1-6 and 8: the wall face's look stops changing past 5 exposed notches
(RM_WallFaceMath.NorthByDrop) and the ladder art spans only the top half-cell, so nothing deeper draws differently from 8.
A last row holds the same pit in TAR (opaque, no see-through) at D4 and D8, because the liquid's own look differs.

The prepared pit (local i east, j north; j=4 the north wall row):
    j=4  spikes(0,4)   wood N (1,4)   STEP (2,4)      steel N (3,4)   cover (4,4)
    j=3  steel W (0,3) .             ramp N (2,3)    .               steel E (4,3)
    j=2  portable W    steel stack   sluice gate     minified table  swale (4,2)
    j=1  wood W (0,1)  .             grate door      .               wood E (4,1)
    j=0  spikes(0,0)   wood S (1,0)  spikes (2,0)    steel S (3,0)   spikes(4,0)
plus a guardrail on the ground south of the pit. The steel stack and the table are spawned (the table then minified). The STEP square is dug to depth - 3 (undug in D1-D3) so the ramp, which
climbs at most 3 notches (pitRampMaxSpan), stands in every pit; it is filled to the same water SURFACE as the pit. The
cover sits on a corner square: it needs a sheer drop of 2 m beside it, and (owner 2026-11-12, no "covered pit bridges")
solid ground on at least two of its sides (PlaceWorker_PitCoverOnSuperdeep, RM_PitDeckMath.RestsOnBanks). A 3x3 D4 probe
pit beside the TAR row proves that rule: a corner cover is placed, an edge-middle cover is refused.
Placement refusals by design (MEASURED 2026-11-12, run1): spikes below D4 (they need a 2 m drop), the portable ladder at
D8 (too deep for it), the guardrail at D1-D2, the cover below D4. Each fitting goes through rimworld/apply_architect_designator (god mode,
so the placeworkers decide exactly as for a player); a refusal is recorded per pit (D1 pits refuse spikes, for one).
Everything is placed dry, then the pit is filled through the engine's driver write (RM_SubmergeDraw.ProofFillRect), so
every fill change must re-mesh the fittings.

Rows (PASS/FAIL each, per fitting square that a state read can decide, RM_SubmergeDraw.ProofSubmerge):
  - found: the fitting is there at the pit's depth and fill;
  - hung ladder (N/E/W): cutZ == faceZ, the ladder's waterline is the waterline drawn on its wall (the owner's
    2026-11-12 north-ladder defect: "2m water depth put the northern ladder behind the pit wall art");
  - share in [0,1] and 0 when dry; printedLevel == the level it is cut at (the fill change re-meshed it).
The owner's look of 2026-11-12 (OWNER_WORDS.md), one row family per finding; every drawer uses RM_UnderLiquid:
  1 tar dark:        a tar pit's look is opaque (clarity 0) and its tint dark (every channel <= 0.10); water is clear.
  2 ramp, 3 portable ladder, 6 wall ladders: seen through clear liquid (seenFoot > 0, seenLine >= seenFoot), hidden in
                     tar (seenLine == 0).
  4 items:           the steel stack and the minified table are covered (share > 0) whenever the pit holds liquid.
  5 swale:           drawn as a floor tile: covered whole (share 1) by any liquid.
  7 D8 variety:      per depth row and fitting, share never falls and seenFoot never rises as the fill rises.
  8 shadows:         the gates cast no sun shadow (live def staticSunShadowHeight 0); and (sheets step, from the shots)
                     the brim-full water pit of every depth darkens no square of the ring just outside its outline
                     against the dry pit of that depth: its shade is only inside.
  9 cover rule:      the probe pit rows above.
Captures: one closest-zoom PNG per pit (mx_D<d>_F<f>[_TAR].png) and a contact sheet per row (sheet_<row>.png).
Grid key labels sit on the map (jawa/review_label) and travel with a keeper save as its sign sidecar.
"""
import json
import os
import shutil
import sys
import time

REPO = sys.argv[1]
OUT = sys.argv[2]
STEP = sys.argv[3] if len(sys.argv) > 3 else "all"
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
B = None                        # the bridge, opened on first call (the `sheets` step runs under WSL python3, no bridge)
LOG = []
ROWS = []
P, S = 5, 8                     # pit side, stride (3 undug squares between pits)
OX, OZ = (int(v) for v in os.environ.get("RM_PFM_ORIGIN", "40,200").split(","))  # SW corner of the top-left pit;
# RM_PFM_ORIGIN="x,z" moves the whole matrix off a SteamGeyser (no bridge tool destroys one; 2026-11-12 a fresh map had two in the default site)
DEPTHS = [1, 2, 3, 4, 5, 6, 8]
TAR = [(4, 1), (4, 2), (4, 3), (4, 4), (8, 2), (8, 4), (8, 6), (8, 8)]
FLUID2 = "RM_Fluid_Tar"
SUB = "RimMandrake.FlowWorks.RM_SubmergeDraw"
# (name, def, local i, j, rotation 0N 1E 2S 3W or None, kind) - kind: hung ladder / ladder / ramp / spikes / other
FITTINGS = [
    ("wood_N", "RM_Ladder", 1, 4, 0, "hung"), ("steel_N", "RM_LadderSteel", 3, 4, 0, "hung"),
    ("wood_S", "RM_Ladder", 1, 0, 2, "hung"), ("steel_S", "RM_LadderSteel", 3, 0, 2, "hung"),
    ("wood_W", "RM_Ladder", 0, 1, 3, "hung"), ("steel_W", "RM_LadderSteel", 0, 3, 3, "hung"),
    ("wood_E", "RM_Ladder", 4, 1, 1, "hung"), ("steel_E", "RM_LadderSteel", 4, 3, 1, "hung"),
    ("portable_W", "RM_LadderPortable", 0, 2, 3, "hung"),
    ("ramp_N", "RM_PitRamp", 2, 3, 0, "ramp"),
    ("spikes_SW", "RM_Spikes", 0, 0, None, "spikes"), ("spikes_S", "RM_Spikes", 2, 0, None, "spikes"),
    ("spikes_SE", "RM_Spikes", 4, 0, None, "spikes"), ("spikes_NW", "RM_Spikes", 0, 4, None, "spikes"),
    ("sluice", "RM_Sluice", 2, 2, 0, "gate"), ("grate", "RM_SecurityGrateDoor", 2, 1, 0, "gate"),
    ("swale", "RM_Swale", 4, 2, None, "swale"), ("cover", "RM_PitCover_PlankLattice", 4, 4, None, "other"),
    ("guardrail", "RM_PitGuardrail", 2, -1, 0, "other"),
]
# goods spawned on the floor (read like the fittings): name, the def ProofSubmerge reports, i, j, kind
GOODS = [("stack", "Steel", 1, 2, "item"), ("minified", "MinifiedThing", 3, 2, "minified")]
GATES = ("RM_Sluice", "RM_SecurityGrateDoor")
COVER = "RM_PitCover_PlankLattice"
PROBE_D = 4                     # the cover-rule probe pit: 3x3 at D4, in the TAR row's free column


STEP_SQ = (2, 4)
RAMP_SPAN = 3


def step_depth(d):
    """The ramp's step square: dug to depth - 3, so the ramp climbs its full span; 0 (undug) in D1-D3."""
    return max(0, d - RAMP_SPAN)


# placements the placeworkers refuse BY DESIGN (MEASURED 2026-11-12 run1/run2): fitting -> (reason prefix, depths refused)
BY_DESIGN = {
    "spikes": ("Spikes go only at the foot of", {1, 2, 3}),
    "portable_W": ("Too deep for a portable ladder", {8}),
    "guardrail": ("A guardrail goes only on the", {1, 2}),
    "cover": ("A concealed pit must be laid", {1, 2, 3}),
}
PLACED = {}


def by_design(name, d):
    return BY_DESIGN.get("spikes" if name.startswith("spikes") else name)


def cells():
    """-> [(key, depth, fill, fluid, x0, z0)] for every pit of the matrix."""
    out = []
    for r, d in enumerate(DEPTHS):
        for f in range(d + 1):
            out.append(("D%d_F%d" % (d, f), d, f, None, OX + f * S, OZ - r * S))
    r = len(DEPTHS)
    for k, (d, f) in enumerate(TAR):
        out.append(("D%d_F%d_TAR" % (d, f), d, f, FLUID2, OX + k * S, OZ - r * S))
    return out


def site():
    """The rect every pit, label and guardrail sits in (x, z, w, h)."""
    x0, z0 = OX - 6, OZ - len(DEPTHS) * S - 4
    return x0, z0, 9 * S + 10, (len(DEPTHS) + 1) * S + 9


def log(k, v):
    LOG.append({k: v})
    print(k, json.dumps(v)[:300])
    sys.stdout.flush()


def bridge():
    global B
    if B is None:
        import validation_core as V
        B = V.Bridge()
    return B


def call(tool, **kw):
    try:
        return bridge().call(tool, **kw) or {}
    except Exception as ex:  # noqa: BLE001
        return {"success": False, "error": str(ex)}


def static(method, arg):
    r = call("jawa/static_call", type=SUB, method=method, args=arg)
    return str(r.get("result") or r.get("error") or r)


def row(name, ok, got):
    ROWS.append({"row": name, "verdict": "PASS" if ok else "FAIL", "got": got})
    if not ok:
        log("FAIL", ROWS[-1])


def designators():
    """defName -> designator id, read from the live Architect menu (never constructed)."""
    want = {f[1] for f in FITTINGS}
    found = {}
    cats = call("rimworld/list_architect_categories")
    for c in cats.get("categories") or []:
        cid = c.get("id") or c.get("categoryId")
        r = call("rimworld/list_architect_designators", categoryId=cid)
        for d in r.get("designators") or []:
            dn = d.get("buildableDefName") or d.get("defName") or ""
            if dn in want and dn not in found:
                found[dn] = d.get("id") or d.get("designatorId")
    log("designators", found)
    return found


def dump():
    stamp = time.strftime("%Y%m%dT%H%M%S")
    with open(os.path.join(OUT, "pfm_%s_%s.json" % (STEP.replace(":", "_"), stamp)), "w") as fh:
        json.dump({"log": LOG, "rows": ROWS}, fh, indent=1)


def sky_gate(when, clear=False):
    """OPEN SKY over site + 6 (owner 2026-11-12: this matrix was once staged under a mountain roof and collapsed in front of
    him). clear=True first removes every roof over site+margin+buffer and the rock/rubble in site+margin (test maps only),
    then a state read asserts it; a roofed or rocky cell refuses the run, UNMEASURED SITE, exit 2, naming the cells."""
    import validation_core as V
    v = V.open_sky_site(bridge(), site()) if clear else V.assert_open_sky(bridge(), site())
    log("open_sky_" + when, {k: v.get(k) for k in ("ok", "rect", "roofCells", "rockCells", "why", "cleared")})
    if not v.get("ok"):
        ROWS.append({"row": "site_open_sky_" + when, "verdict": "UNMEASURED", "got": v.get("why")})
        dump()
        sys.exit(2)


def stage():
    x, z, w, h = site()
    log("reset", static_reset(x, z, w, h))
    sky_gate("before_stage", clear=True)
    log("cleared", {k: v for k, v in call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (x, z, w, h),
                                            categories="All").items() if k in ("success", "destroyed", "counts")})
    call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (x, z, w, h))
    call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % (x, z, w, h))
    sky_gate("after_clear")
    call("jawa/kill_hostiles")
    call("jawa/weather_set", weather="Clear", lockWeather=True)
    for key, d, f, fluid, x0, z0 in cells():
        for i in range(P):
            for j in range(P):
                n = step_depth(d) if (i, j) == STEP_SQ else d
                if n:
                    call("jawa/flowworks_excavation_drive", x=x0 + i, z=z0 + j, deepenLevels=n, setBodyWaterM=-1, fillInLevels=0)
    px, pz = probe()
    for i in range(3):
        for j in range(3):
            call("jawa/flowworks_excavation_drive", x=px + i, z=pz + j, deepenLevels=PROBE_D, setBodyWaterM=-1, fillInLevels=0)
    # HARNESS (2026-11-13): the dug-swim set behind ClimbDepthAt is derived and refreshed only every
    # SwimRefreshTicks (60). On a site that was filled before, a paused restage read each pit's wall
    # above the OLD water (wall = depth - old fill), and every sheer-drop fitting in columns F3+ was
    # refused. Let one refresh run on the fresh, dry pits before placing anything.
    bridge().ticks(70)
    des = designators()
    call("rimworld/set_god_mode", enabled=True)
    placed = {}
    for key, d, f, fluid, x0, z0 in cells():
        got = []
        for name, dn, i, j, rot, kind in FITTINGS:
            if dn not in des:
                got.append(name + ":no-designator")
                continue
            kw = dict(designatorId=des[dn], x=x0 + i, z=z0 + j)
            if rot is not None:
                kw["rotation"] = rot
            r = call("rimworld/apply_architect_designator", **kw)
            ok = r.get("success") is True and not r.get("rejectedCells")
            got.append(name + (":ok" if ok else ":refused " + str(r.get("message") or r.get("rejectedCells") or r.get("error"))[:240]))
        placed[key] = got
        PLACED[key] = got
        for it in got:
            n, res = it.split(":", 1)
            bd = by_design(n, d)
            if res == "ok":
                row("%s_%s_placed" % (key, n), not (bd and d in bd[1]), "placed" + (" (expected refused)" if bd and d in bd[1] else ""))
            else:
                row("%s_%s_refused_by_design" % (key, n), bool(bd and d in bd[1] and bd[0] in res), res[:160])
        # goods: a steel stack and a minified table on the floor
        call("rimworld/spawn_thing", defName="Steel", x=x0 + 1, z=z0 + 2, stackCount=35)
        t = call("rimworld/spawn_thing", defName="Table1x2c", x=x0 + 3, z=z0 + 2)
        tid = t.get("thingId")
        if tid:
            call("jawa/thing_minify", thing=str(tid).replace("Thing_", ""))
    cover_probe(des)
    call("rimworld/set_god_mode", enabled=False)
    log("placed", placed)
    labels()


def probe():
    """South-west corner of the cover-rule probe pit (the TAR row's free column)."""
    return OX + len(TAR) * S, OZ - len(DEPTHS) * S


def cover_probe(des):
    """Owner 2026-11-12: a cover only where >= 2 of its sides are solid ground (no "covered pit bridges")."""
    if COVER not in des:
        row("cover_probe_designator", False, "no designator for " + COVER)
        return
    px, pz = probe()
    for name, i, j, want_ok in (("edge_one_bank", 1, 0, False), ("corner_two_banks", 0, 0, True)):
        r = call("rimworld/apply_architect_designator", designatorId=des[COVER], x=px + i, z=pz + j)
        ok = r.get("success") is True and not r.get("rejectedCells")
        msg = str(r.get("message") or r.get("rejectedCells") or r.get("error") or "")[:240]
        if want_ok:
            row("cover_probe_%s_placed" % name, ok, "placed" if ok else msg)
        else:
            row("cover_probe_%s_refused" % name, not ok and "rest on solid ground" in msg, "placed" if ok else msg)


def static_reset(x, z, w, h):
    r = call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
             args="%d;%d;%d;%d" % (x, z, w, h))
    return str(r.get("result") or r)[:200]


def label_ops():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    from modcheck.reviewmap import label_line
    ops = [label_line(OX - 5, OZ + P + 6, "PIT FITTINGS MATRIX", "rows = pit depth, columns = liquid fill (0.5 m a notch); "
                      "every pit holds the same fittings (see REPORT.md)", "#ffffff", "medium", "pfm")]
    for r, d in enumerate(DEPTHS):
        ops.append(label_line(OX - 5, OZ - r * S + 2, "D%d" % d, "%.1f m deep" % (d * 0.5), "#ffd27f", "medium", "pfm"))
    ops.append(label_line(OX - 5, OZ - len(DEPTHS) * S + 2, "TAR", "same pit, tar", "#ffd27f", "medium", "pfm"))
    px, pz = probe()
    ops.append(label_line(px, pz + 4, "COVER RULE", "corner cover placed, edge-middle refused (2 solid sides)",
                          "#bfe4ff", "small", "pfm"))
    for key, d, f, fluid, x0, z0 in cells():
        ops.append(label_line(x0 + 2, z0 + P + 1, key.replace("_", " "),
                              "%.1f m %s in %.1f m" % (f * 0.5, "tar" if fluid else "water", d * 0.5), "#bfe4ff", "small", "pfm"))
    return ops


def labels():
    call("jawa/review_label", action="clear", tag="pfm")
    r = call("jawa/review_label", action="add", ops="\n".join(label_ops()))
    log("labels", {k: r.get(k) for k in ("success", "added", "message") if k in r})


def fill():
    for key, d, f, fluid, x0, z0 in cells():
        if f:
            fl = "," + fluid if fluid else ""
            log("fill_" + key, static("ProofFillRect", "%d,%d,%d,%d,%g%s" % (x0, z0, P, P, f * 0.5, fl)))
            sd = step_depth(d)
            if sd:   # the step holds the same water surface: its own floor is d - sd notches higher
                log("fill_step_" + key, static("ProofFillRect", "%d,%d,1,1,%g%s" % (x0 + STEP_SQ[0], z0 + STEP_SQ[1], max(0, f - (d - sd)) * 0.5, fl)))
    time.sleep(3)   # the re-mesh the fill change asked for


def kv_of(text):
    return dict(p.split("=", 1) for p in text.split() if "=" in p)


def fnum(kv, k, dflt=-1.0):
    try:
        return float(kv.get(k))
    except (TypeError, ValueError):
        return dflt


def read():
    res = {}                        # (depth, fluid, name) -> [(fill, share, seenFoot)] for the one-law row
    for key, d, f, fluid, x0, z0 in cells():
        pit_look = None
        for name, dn, i, j, rot, kind in FITTINGS + [(g[0], g[1], g[2], g[3], None, g[4]) for g in GOODS]:
            if kind == "other":
                continue
            rid = "%s_%s" % (key, name)
            bd = by_design(name, d)
            if bd and d in bd[1]:
                continue            # refused at placement by design: its own row above
            text = static("ProofSubmerge", "%d,%d" % (x0 + i, z0 + j))
            if text.startswith("REFUSED"):
                row(rid + "_present", False, text)   # a placement refusal shows here too; judged against `placed`
                continue
            kv = kv_of(text)
            row(rid + "_found_at_depth_fill", kv.get("depth") == str(d) and kv.get("fill") == str(f) and kv.get("def") == dn
                and (kind not in ("item", "minified", "swale") or kv.get("kind") == kind), text)
            share, line, foot = fnum(kv, "share"), fnum(kv, "seenLine"), fnum(kv, "seenFoot")
            row(rid + "_share_in_range", 0.0 <= share <= 1.0 and (f > 0 or share == 0.0), kv.get("share"))
            if f > 0 and pit_look is None:
                pit_look = kv
            if share > 0:           # findings 2, 3, 6: the drowned part is seen through clear liquid, hidden in tar
                ok = (line == 0.0) if fluid else (foot > 0.0 and line >= foot - 1e-6)
                row(rid + "_seen_through_clear_hidden_in_tar", ok, "seenLine=%s seenFoot=%s clarity=%s" % (kv.get("seenLine"), kv.get("seenFoot"), kv.get("clarity")))
            if kind in ("item", "minified"):    # finding 4: goods are covered
                row(rid + "_covered", (share > 0) == (f > 0), "share=%s fill=%d" % (kv.get("share"), f))
            if kind == "swale":                 # finding 5: a floor tile, covered whole by any liquid
                row(rid + "_floor_tile_covered", (share == 1.0) == (f > 0), "share=%s fill=%d" % (kv.get("share"), f))
            res.setdefault((d, fluid, name), []).append((f, share, foot if share > 0 else 1.0))
            if kind == "hung" and kv.get("flat") == "no":
                if rot == 2:
                    row(rid + "_south_never_cut", kv.get("cutZ") == "-", kv.get("cutZ"))
                else:
                    cz, fz = kv.get("cutZ"), kv.get("faceZ")
                    same = cz == fz or (cz not in (None, "-") and fz not in (None, "-") and abs(float(cz) - float(fz)) < 0.005)
                    row(rid + "_ladder_meets_its_wall", same, "cutZ=%s faceZ=%s level=%s fill=%s" % (cz, fz, kv.get("level"), f))
            if kind == "gate":      # RM_UnderLiquid.GateMetres(d) = (d + 1) notches; level is in notches
                lv = fnum(kv, "level", 0.0)
                want = min(1.0, lv / (d + 1)) if lv > 0 else 0.0
                row(rid + "_gate_under_by_level", abs(share - want) <= 1.0 / 32 + 1e-6, "share %s want %.3f (level %s, depth %d)" % (kv.get("share"), want, kv.get("level"), d))
            if kind in ("hung", "ramp", "item", "minified", "swale") and f > 0:
                # map-mesh things: printed at the true level the cell now holds (the fill change re-meshed them)
                row(rid + "_printed_at_its_level", kv.get("printedLevel") == kv.get("level"), "%s vs %s" % (kv.get("printedLevel"), kv.get("level")))
        if pit_look is not None:            # finding 1: tar dark and opaque; water clear
            tint = [fnum({"t": v}, "t", 9.0) for v in (pit_look.get("tint") or "").split(",")]
            if fluid:
                ok = fnum(pit_look, "clarity") == 0.0 and len(tint) == 3 and max(tint) <= 0.10
            else:
                ok = fnum(pit_look, "clarity") > 0.0
            row(key + "_liquid_" + ("tar_dark_opaque" if fluid else "water_clear"), ok,
                "clarity=%s tint=%s liquid=%s" % (pit_look.get("clarity"), pit_look.get("tint"), pit_look.get("liquid")))
    for (d, fluid, name), seq in sorted(res.items(), key=lambda kv: (kv[0][0], kv[0][1] or "", kv[0][2])):
        seq.sort()                          # finding 7: one law, so the look moves one way as the fill rises
        bad = [(a, b) for a, b in zip(seq, seq[1:]) if b[1] < a[1] - 1e-6 or b[2] > a[2] + 1e-6]
        row("D%d%s_%s_one_law_over_fill" % (d, "_TAR" if fluid else "", name), not bad,
            "fill,share,seenFoot " + " ".join("%d,%.3f,%.3f" % t for t in seq))
    gd = call("jawa/get_defs", defs=";".join("ThingDef/" + g for g in GATES), fields="staticSunShadowHeight") or {}
    got = {(x.get("defName") or (x.get("fields") or {}).get("defName")): (x.get("fields") or {}).get("staticSunShadowHeight")
           for x in gd.get("defs") or []}
    for g in GATES:                          # finding 8: nothing in a pit throws a sun shadow onto the bank
        v = got.get(g)
        row("gate_%s_casts_no_sun_shadow" % g, v is not None and fnum({"v": v}, "v") == 0.0, "staticSunShadowHeight=%s (%s)" % (v, str(gd)[:160] if v is None else "live def"))
    fails = [r for r in ROWS if r["verdict"] != "PASS"]
    log("rows", {"rows": len(ROWS), "fail": len(fails), "first_fails": [r["row"] for r in fails[:20]]})


def midday():
    for _ in range(14):
        t = call("jawa/time_clock")
        if t.get("ticksAbs") is None:
            return
        hour = (t["ticksAbs"] % 60000) / 2500.0
        if 10 <= hour <= 14:
            log("hour", hour)
            return
        bridge().ticks(2000)


def shot(name, cx, cz, root):
    call("jawa/clear_ui", all=True)
    call("rimworld/jump_camera_to_cell", x=int(cx), z=int(cz))
    call("rimworld/set_camera_zoom", rootSize=root)
    time.sleep(1.2)
    r = call("jawa/take_screenshot", fileName="pfm_%s_%d" % (name, int(time.time())))
    src = r.get("filePath")
    for _ in range(12):
        if src and os.path.exists(src):
            break
        time.sleep(0.5)
    if not src or not os.path.exists(src):
        log("shot_failed", {"name": name, "r": str(r)[:200]})
        return None
    dst = os.path.join(OUT, name + ".png")
    shutil.copyfile(src, dst)
    return dst


ROOT = 8.0                      # camera rootSize: the closest the bridge zooms (MEASURED 2026-11-12: 99 px a cell at 1604 px)
CROP = 8                        # cells kept round each pit in the sheets (pit 5 + 1.5 each side)


def sheets():
    """WSL python3 (PIL): crop every mx_<key>.png to the pit at true scale and tile a row's pits, labelled, into
    sheet_<row>.png (3 across) for the look."""
    from PIL import Image, ImageDraw
    rows = {}
    for key, d, f, fluid, x0, z0 in cells():
        rows.setdefault("TAR" if fluid else "D%d" % d, []).append(key)
    for rname, keys in rows.items():
        tiles = []
        for key in keys:
            p = os.path.join(OUT, "mx_%s.png" % key)
            if not os.path.exists(p):
                continue
            im = Image.open(p).convert("RGB")
            w, h = im.size
            ppc = h / (2.0 * ROOT)
            half = CROP * ppc / 2.0
            cx, cy = w / 2.0, h / 2.0     # the camera sits on the pit's centre square
            t = im.crop((int(cx - half), int(cy - half), int(cx + half), int(cy + half))).resize((600, 600), Image.LANCZOS)
            ImageDraw.Draw(t).rectangle((0, 0, 600, 26), fill=(0, 0, 0))
            ImageDraw.Draw(t).text((6, 6), key, fill=(255, 255, 255))
            tiles.append(t)
        if not tiles:
            continue
        n = 3
        sheet = Image.new("RGB", (600 * n, 600 * ((len(tiles) + n - 1) // n)), (20, 20, 20))
        for k, t in enumerate(tiles):
            sheet.paste(t, ((k % n) * 600, (k // n) * 600))
        sheet.save(os.path.join(OUT, "sheet_%s.png" % rname))
        log("sheet", {"row": rname, "tiles": len(tiles)})
    brim_ring()


RING_DARKER = 0.08              # a ring square more than 8% darker at the brim than dry is a shade outside the pit


def ring_means(path):
    """Mean luminance of each of the 24 squares in the ring just outside the 5x5 pit (camera on the pit's centre)."""
    from PIL import Image
    im = Image.open(path).convert("L")
    w, h = im.size
    ppc = h / (2.0 * ROOT)
    out = {}
    for a in range(-3, 4):
        for b in range(-3, 4):
            if max(abs(a), abs(b)) != 3:
                continue
            x0, y0 = w / 2.0 + (a - 0.5) * ppc, h / 2.0 + (-b - 0.5) * ppc
            box = (int(x0 + 0.15 * ppc), int(y0 + 0.15 * ppc), int(x0 + 0.85 * ppc), int(y0 + 0.85 * ppc))
            px = list(im.crop(box).getdata())
            out[(a, b)] = sum(px) / float(len(px) or 1)
    return out


def brim_ring():
    """Finding 8 (owner 2026-11-12: shadows "only inside the pit"): the brim-full water pit of each depth darkens no
    square just outside its outline against the dry pit of that depth (same fittings, same light)."""
    for d in DEPTHS:
        dry, brim = (os.path.join(OUT, "mx_D%d_F%d.png" % (d, f)) for f in (0, d))
        if not (os.path.exists(dry) and os.path.exists(brim)):
            row("D%d_F%d_brim_no_shade_outside" % (d, d), False, "UNMEASURED: shot missing (%s)" % (dry if not os.path.exists(dry) else brim))
            continue
        m0, m1 = ring_means(dry), ring_means(brim)
        dark = sorted(((m1[k] / m0[k]) if m0[k] else 1.0, k) for k in m0)
        worst = dark[0]
        row("D%d_F%d_brim_no_shade_outside" % (d, d), worst[0] >= 1.0 - RING_DARKER,
            "worst ring square %s at %.3f of dry (%d squares)" % (worst[1], worst[0], len(dark)))


def shots():
    midday()
    call("jawa/review_label", action="hide")
    files = {}
    for key, d, f, fluid, x0, z0 in cells():
        files[key] = shot("mx_" + key, x0 + 2, z0 + 2, ROOT)
    call("jawa/review_label", action="show")
    x, z, w, h = site()
    shot("overview", x + w // 2, z + h // 2, 40.0)
    log("shots", {"count": len([v for v in files.values() if v])})


if __name__ == "__main__":
    t0 = time.time()
    if STEP in ("all", "stage"):
        stage()
    if STEP in ("all", "fill"):
        fill()
    if STEP in ("all", "shots"):
        shots()             # before the read: a map section re-prints only when the camera reaches it
    if STEP in ("all", "read"):
        sky_gate("before_read")
        read()
    if STEP == "sheets":
        sheets()
    if STEP == "labels":
        labels()
    if STEP.startswith("save:"):
        from modcheck.reviewmap import save_keeper
        call("rimworld/pause_game")
        log("save", save_keeper(B, STEP.split(":", 1)[1], signs=label_ops()))
    log("elapsed_s", round(time.time() - t0, 1))
    dump()
    sys.exit(2 if any(r["verdict"] == "UNMEASURED" for r in ROWS) else 1 if any(r["verdict"] != "PASS" for r in ROWS) else 0)
