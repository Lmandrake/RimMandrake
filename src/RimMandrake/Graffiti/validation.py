"""validation.py -- modcheck suite for RimMandrake: Graffiti Framework
(mandrake.rm.graffiti). Trial plan: design/RimMandrake/northstar_trials/Graffiti_trial_plan.md.

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Graffiti

Grounded in the mod's source: `RM_GraffitiMod.cs` for the SIX settings toggles
(`paintingEnabled`, `paintIntervalTicks`, `viewerReactionEnabled`, `breachBiasEnabled`,
`raidExitTaggingEnabled`, `autoCleanProtectionEnabled`); `JobDriver_PaintGraffiti.cs`
(goto, then one finished `Filth_Mark.MakeMark` per sitting of work paced by `paintIntervalTicks`, picking
through `GraffitiPool.PickForSpree`); `JoyGiver_PaintGraffiti.cs` /
`JobGiver_GraffitiPaintingSpree.cs` (the two places `paintingEnabled` is checked);
`Defs/ThinkTreeDefs_Graffiti.xml` (the `RM_GraffitiPaintingSpreeState` hook).

THE SPREE PAINTS THE WHOLE WEIGHTED POOL, NOT ONLY `RM_Graffiti_Vandal`. Every def
carrying a `ModExtension_Graffiti` whose form is Scrawl/Tag/ThrowUp/Glyph can be picked.
This suite therefore counts `MARK_DEFS` -- every mark def this mod ships, read from its own
`Defs/*.xml` at import -- never one defName. (A suite that counted only Vandal read a spree
of six Tags as "no mark": a false fail.)

Behaviour that is UNMEASURED until the first live run: lane geometry vs the 12-cell search
radius of `GraffitiJobUtility.TryFindWallMarkCell`; `_remove_pawns_in` (pawn_force_incapacitate vanish)
removing painters without touching marks; `rimworld/screenshot_cell_rect` result key `path`.
Not expressible with existing bridge tools (see the plan, section 6): per-variant pinning of a
`Graphic_Random` mark and its resolved texture name (gallery pages spawn several of each def
and rely on random variants instead), `GameGlowAt`, assembly MVID. Ideo assignment of the
painters is not driven here, so meme-gated glyphs appear only if the quicktest ideo holds the
meme.

Two settings are proved here by write+read-back only. `viewerReactionEnabled` gates
`ThoughtWorker_ViewedGraffitiMark`: Graffiti's own `RM_Graffiti_ViewedHostileMark` (every
raidExitEligible mark's `onViewHostileMaker`, GRAFFITI_V1_LIVE_PROOF_1) and SacredGraffiti's
`ThoughtDefs_SacredMarks.xml`; its behaviour is proved by `graffiti_v1_live_proof.py A5`.
`breachBiasEnabled` gates `BreachBiasHook` on `RM_Graffiti_WarningGlyph` (`breachLure`=true);
its behavioural A/B needs a breaching raid, not built here.
"""
import contextlib
import os
import re

from modcheck import Suite, ExpectationFailed

suite = Suite("Graffiti")
suite.toggles = ["paintingEnabled", "paintIntervalTicks",
                 "viewerReactionEnabled", "breachBiasEnabled",
                 "raidExitTaggingEnabled", "autoCleanProtectionEnabled"]

VANDAL_DEF = "RM_Graffiti_Vandal"


def _remove_pawns_in(call, rect):
    """Vanish every living pawn in rect ('x,z,w,h'): no death, no corpse. jawa/destroy_batch never removes
    pawns and refuses categories=Pawn (DESTROY_BATCH_NEVER_KILLS_PAWNS_1). Returns how many were removed."""
    r = call("jawa/list_pawns", rect=rect, limit=500)
    n = 0
    for p in ((r or {}).get("pawns") or []) if isinstance(r, dict) else []:
        if p.get("dead") or not p.get("id"):
            continue
        call("jawa/pawn_force_incapacitate", pawn=p["id"], action="vanish")
        n += 1
    return n


_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(os.path.dirname(_HERE))


def _mark_defs(ddir=None):
    """[(defName, form)] for every ThingDef in a mod's Defs/ (default: this mod's) carrying a
    ModExtension_Graffiti. Parsed per `<ThingDef>` block, `form` read from inside it (never a fixed line number)."""
    out = []
    ddir = ddir or os.path.join(_HERE, "Defs")
    if not os.path.isdir(ddir):
        return out
    for fn in sorted(os.listdir(ddir)):
        if not fn.endswith(".xml"):
            continue
        txt = open(os.path.join(ddir, fn), encoding="utf-8").read()
        for blk in re.findall(r"<ThingDef\b.*?</ThingDef>", txt, re.S):
            if "ModExtension_Graffiti" not in blk:
                continue
            nm = re.search(r"<defName>([^<]+)</defName>", blk)
            fm = re.search(r"<form>([^<]+)</form>", blk)
            if nm:
                out.append((nm.group(1), fm.group(1) if fm else "?"))
    return out


_MARKS = _mark_defs()
MARK_DEFS = [d for d, _ in _MARKS] or [VANDAL_DEF]
FORM_OF = dict(_MARKS)
MARK_CSV = ",".join(MARK_DEFS)
SETTINGS = "RimMandrake.Graffiti.RM_GraffitiSettings"

# Foreign pool members (the full list): their mark defs join the spree's pool when loaded, and are reported in
# separate `compat_*` components (northstar_driver doc["compat"]), NEVER in Graffiti's bars or verdict
# (GRAFFITI_NORTHSTAR_GREEN_FULL_1). Read from each member's own repo Defs/, keyed by its packageId.
FOREIGN_MEMBERS = {
    "mandrake.rm.sacredgraffiti": os.path.join(_SRC, "RimMandrake", "SacredGraffiti", "Defs"),
    "mandrake.rsw.graffitiimperial": os.path.join(_SRC, "RimStarWars", "GraffitiImperial", "Defs"),
}
FOREIGN_DEFS = {pid: [d for d, _ in _mark_defs(dd)] for pid, dd in FOREIGN_MEMBERS.items()}

LANE_LEN, LANE_DX, LANE_DZ = 14, 30, 16     # lanes > 12-cell search radius apart
# every JUDGED shot is captured at play zoom, measured on the PNG (modcheck/play_zoom.py; plan 3.9). Live 2026-11-05:
# at the current zoom (rootSize 24 = 19.7 px/cell) the judge called 7 bars UNJUDGEABLE. spree_variety is not: its
# three lanes span 44 cells, wider than one screen at 64 px/cell, and it judged fine at the current zoom.
PLAY_PPC = 64


def _marks_in(t, rect, defs=MARK_CSV):
    """Marks (list of {def, x, z}) in `rect`. A failed/incomplete read is not "zero marks"."""
    r = t.bridge_call("jawa/list_things", defName=defs, rect=rect, limit=500)
    if t._guard():
        if not (r or {}).get("success", True) or (r or {}).get("isCompleteList") is False:
            raise ExpectationFailed("jawa/list_things unreadable or truncated: %r" % (r,))
    return [{"def": x.get("def") or x.get("defName"),
             "x": (x.get("position") or {}).get("x", x.get("x")),
             "z": (x.get("position") or {}).get("z", x.get("z"))}
            for x in ((r or {}).get("things") or [])]


def _running_ids(t):
    """Lower-cased packageIds of the RUNNING game (jawa/running_mods); None when it cannot be read."""
    r = t.bridge_call("jawa/running_mods", assembly="", details=False)
    ids = (r or {}).get("packageIds") if isinstance(r, dict) else None
    return {str(i).lower() for i in ids} if ids else None


def _compat_foreign(t, lanes):
    """One compat component per foreign pool member: which of its marks the spree painted, lane by lane, and
    whether each sits on a cell cardinal to its lane's wall. An absent member reads UNMEASURED 'not loaded'."""
    saved = (t.upstream_failed, t.upstream_reason)
    try:
        running = _running_ids(t) if t._guard() else set()
    except Exception:   # noqa: BLE001 - the probe's failure is reported by the compat rows only
        running = None
    for pid, defs in sorted(FOREIGN_DEFS.items()):
        short = pid.rsplit(".", 1)[-1]
        try:
            _compat_one(t, lanes, pid, short, defs, running)
        finally:     # a compat row's FAIL/UNMEASURED never marks the chain upstream-failed for the next row
            t.upstream_failed, t.upstream_reason = saved


def _compat_one(t, lanes, pid, short, defs, running):
    """One foreign member's compat row (see _compat_foreign)."""
    with t.component("compat_%s_marks" % short):
        if not t._guard():
            return
        if running is None:
            raise ExpectationFailed("UNMEASURED: jawa/running_mods unreadable")
        if pid not in running:
            raise ExpectationFailed("UNMEASURED: %s not on the running list (member absent)" % pid)
        if not defs:
            raise ExpectationFailed("%s is loaded but its repo Defs/ list no ModExtension_Graffiti mark" % pid)
        per = [_marks_in(t, ln["rect"], defs=",".join(defs)) for ln in lanes]
        off = [(i, m) for i, ms in enumerate(per) for m in ms
               if abs(m["z"] - lanes[i]["wall_z"]) != 1
               or not (lanes[i]["x0"] <= m["x"] < lanes[i]["x0"] + LANE_LEN)]
        hist = {}
        for ms in per:
            for m in ms:
                hist[m["def"]] = hist.get(m["def"], 0) + 1
        if off:
            raise ExpectationFailed("%s marks off the wall: %s (histogram %s)" % (short, off[:5], hist))
        t._current.detail = "%s: %d foreign mark(s), per lane %s, histogram %s" % (
            short, sum(len(m) for m in per), [len(m) for m in per], hist)


def _prep_site(t, size):
    """Everything true before the first assertion (plan section 3), expressed with existing tools."""
    t.clear_area(size=size)
    x, z = t.anchor
    h = size // 2
    t.bridge_call("jawa/set_terrain_batch", ops="Concrete:%d,%d,%d,%d" % (x - h, z - h, size, size))
    t.bridge_call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (x - h, z - h, size, size))
    t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
    t.bridge_call("jawa/log_autoopen_suppress")


def _wall_run(t, x0, z, length):
    ops = ";".join("Wall:%d,%d" % (x0 + i, z) for i in range(length))
    t.bridge_call("jawa/spawn_batch", ops=ops, stuff="Steel")


def _all_colonists(t):
    r = t.bridge_call("jawa/list_pawns", limit=200)
    return [p for p in ((r or {}).get("pawns") or []) if p.get("id")]


def _settle_painter(t, pid):
    t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
    t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Rest", level=1.0)
    t.bridge_call("jawa/set_pawn_skill", pawn=pid, skill="Artistic", level=8)
    t.bridge_call("jawa/set_draft", pawnId=pid, drafted=False)


SPREE_STATE = "RM_GraffitiPaintingSpreeState"


@contextlib.contextmanager
def _own_spree(painters):
    """clockgate.expected_disturbance for the row's OWN forced spree (GRAFFITI_NORTHSTAR_GREEN_FULL_1, pilot gen 11):
    the companion latches a colonist's new mental state as kind 'mental', severity 'threat', so without this the
    painter's own RM_GraffitiPaintingSpreeState stops safe_advance and the row reads UNMEASURED on every run. Matches
    only kind 'mental' on one of `painters` whose detail ends in the spree state: another pawn's break, any death or
    hostile still stops the clock (guard: selftest_graffiti_spree_surprise.py)."""
    import clockgate
    ids = set(n for n in (clockgate._thing_number(p) for p in painters if p) if n is not None)

    def pred(tr):
        return (isinstance(tr, dict) and tr.get("kind") == "mental"
                and clockgate._thing_number(tr.get("subjectId")) in ids
                and str(tr.get("detail") or "").endswith(SPREE_STATE))
    with clockgate.expected_disturbance("painter's own forced %s" % SPREE_STATE, pred):
        yield


def _no_cleaning(t):
    for p in _all_colonists(t):
        t.bridge_call("jawa/set_work_priority", pawnId=p["id"], workType="Cleaning", priority=0)


def _lanes(t, n=6):
    """n lanes: 2 columns x 3 rows, each a straight wall run with a painter beside it."""
    x, z = t.anchor
    lanes = []
    for i in range(n):
        lx = x - LANE_DX // 2 - LANE_LEN // 2 + (i % 2) * LANE_DX
        lz = z - LANE_DZ + (i // 2) * LANE_DZ
        lanes.append({"x0": lx, "wall_z": lz, "rect": "%d,%d,%d,%d" % (lx - 1, lz - 3, LANE_LEN + 2, 7)})
    return lanes


@suite.chain("forced_paint_job")
def forced_paint_job(t):
    """Order a plain colonist onto `RM_PaintGraffitiJob` at a cell beside a wall (bypassing
    `JoyGiver_PaintGraffiti`'s own cell search) and prove the periodic toil leaves a mark from
    the whole pool, on schedule with the shipped `paintIntervalTicks`=250. Also the terrain
    calibration: if nothing paints on Concrete the floor rejects the placementMask."""
    x, z = t.anchor
    mark_x, mark_z = x, z
    rect = "%d,%d,8,6" % (mark_x - 4, mark_z - 3)
    with t.component("site_ready_forced_paint"):
        _prep_site(t, 40)
        _wall_run(t, x - 5, z + 1, 11)
        walker = t.spawn_pawn("Colonist", hostile=False)
        _no_cleaning(t)

    with t.component("paints_mark_at_interval", toggle="paintIntervalTicks"):
        _settle_painter(t, walker)
        before = len(_marks_in(t, rect))
        r = t.bridge_call("jawa/ordered_job", pawnId=walker,
                          jobDef="RM_PaintGraffitiJob",
                          targetAX=mark_x, targetAZ=mark_z,
                          waitTicks=3200, timeoutSeconds=25)
        if t._guard():
            if not (bool((r or {}).get("accepted")) and bool((r or {}).get("nowRunningRequested"))):
                raise ExpectationFailed(
                    "jawa/ordered_job RM_PaintGraffitiJob was not accepted and running: %r" % r)
            # the paused site makes the tool's own waitTicks a no-op (ticksElapsed 0, MEASURED live
            # 2026-10-01), so advance the clock ourselves
            t.wait_ticks(3200)      # one finished mark: a piece, the slowest form, takes 2800
            after = len(_marks_in(t, rect))
            if after <= before:
                raise ExpectationFailed(
                    "no new mark (any of %d defs) near (%d,%d) after the paint job "
                    "(before=%d after=%d) -- if the floor rejects Unnatural filth this is an "
                    "environment fault, not a mod fail" % (len(MARK_DEFS), mark_x, mark_z, before, after))
        t.screenshot(rect=(mark_x - 5, mark_z - 2, 11, 5))


@suite.chain("mental_break_spree")
def mental_break_spree(t):
    """The ONE reachable path to `JobGiver_GraffitiPaintingSpree.TryGiveJob`, hence the only proof of
    `paintingEnabled`: force the break, prove the state and a mark near the wall."""
    x, z = t.anchor
    rect = "%d,%d,12,8" % (x - 6, z - 2)
    with t.component("site_ready_mental_break"):
        _prep_site(t, 40)
        _wall_run(t, x - 5, z + 3, 11)
        walker = t.spawn_pawn("Colonist", hostile=False)
        _no_cleaning(t)

    with t.component("mental_break_assigns_paint_job", toggle="paintingEnabled"):
        _settle_painter(t, walker)
        before = len(_marks_in(t, rect))
        r = t.bridge_call("jawa/pawn_force_mental_break", pawn=walker,
                          breakDef="RM_GraffitiPaintingSpreeBreak")
        if t._guard():
            if not (bool((r or {}).get("started"))
                    and (r or {}).get("mentalStateAfter") == "RM_GraffitiPaintingSpreeState"):
                raise ExpectationFailed(
                    "jawa/pawn_force_mental_break did not start RM_GraffitiPaintingSpreeState: %r" % r)
        with _own_spree([walker]):
            t.wait_ticks(1600)      # the walk and one finished mark; a throw-up, the spree's slowest, takes 1200
        if t._guard():
            job = t.bridge_call("jawa/pawn_get", pawn=walker)
            after = len(_marks_in(t, rect))
            if after <= before:
                raise ExpectationFailed(
                    "no new mark near the wall during the forced spree (before=%d after=%d; "
                    "pawn_get=%s)" % (before, after, str(job)[:200]))


@suite.chain("spree_wall")
def spree_wall(t):
    """Bars 1, 2, 7: six painters, each with its own wall lane, a real spree, natural rendering.
    No `map_commit` after painting (plan: a forced commit would hide a mesh bug)."""
    lanes = _lanes(t)
    painters, started = [], []
    with t.component("site_ready_spree_wall"):
        _prep_site(t, 70)
        for ln in lanes:
            _wall_run(t, ln["x0"], ln["wall_z"], LANE_LEN)
        t.bridge_call("jawa/map_commit")                # FIXTURE write (walls/terrain), never marks
        for ln in lanes:
            r = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=ln["x0"] + LANE_LEN // 2,
                              z=ln["wall_z"] + 2, faction="player", count=1)
            row = ((r or {}).get("pawns") or [{}])[0]
            painters.append(row.get("id"))
        _no_cleaning(t)
        for pid in painters:
            if pid:
                _settle_painter(t, pid)
                r = t.bridge_call("jawa/pawn_force_mental_break", pawn=pid,
                                  breakDef="RM_GraffitiPaintingSpreeBreak")
                started.append(bool((r or {}).get("started")))
    per_lane = []
    with t.component("spree_runs"):
        with _own_spree(painters):
            t.wait_ticks(3000)
        # painters out of frame before any shutter: a body must not occlude a mark
        for ln in lanes:
            _remove_pawns_in(t.bridge_call, ln["rect"])
        if t._guard():
            per_lane = [_marks_in(t, ln["rect"]) for ln in lanes]

    with t.component("spree_paints_marks", shows=["mark_actually_appears"]):
        if t._guard():
            if not (started and all(started)):
                raise ExpectationFailed("not every painter entered the spree: %r" % started)
            empty = [i for i, m in enumerate(per_lane) if not m]
            if empty:
                raise ExpectationFailed("lane(s) %s have no mark from the whole pool after 3000 ticks "
                                        "(counts per lane: %s)" % (empty, [len(m) for m in per_lane]))
        l0 = lanes[0]
        t.screenshot(rect=(l0["x0"], l0["wall_z"] - 3, LANE_LEN, 7), ppc=PLAY_PPC)

    with t.component("spree_variety", shows=["marks_visibly_various"]):
        if t._guard():
            allm = [m for lane in per_lane for m in lane]
            defs = sorted({m["def"] for m in allm})
            forms = sorted({FORM_OF.get(d, "?") for d in defs})
            hist = {d: sum(1 for m in allm if m["def"] == d) for d in defs}
            if len(defs) < 3 or len(forms) < 2:
                raise ExpectationFailed("variety too low: %d def(s) %s, %d form(s) %s -- histogram %s"
                                        % (len(defs), defs, len(forms), forms, hist))
        t.screenshot(rect=(lanes[0]["x0"], lanes[0]["wall_z"] - 3, LANE_DX + LANE_LEN, 7 + 2 * LANE_DZ))

    with t.component("wall_closeup", shows=["mark_sits_on_the_wall"]):
        if t._guard():
            ln = lanes[0]
            # cardinal to the run: either long face, or either end cap of it
            bad = [m for m in per_lane[0]
                   if not ((abs(m["z"] - ln["wall_z"]) == 1 and ln["x0"] <= m["x"] < ln["x0"] + LANE_LEN)
                           or (m["z"] == ln["wall_z"] and m["x"] in (ln["x0"] - 1, ln["x0"] + LANE_LEN)))]
            if not per_lane[0] or bad:
                raise ExpectationFailed("lane 0 marks not on cells cardinal to the wall run: %s" % bad[:5])
            m0 = per_lane[0][0]
            t.screenshot(rect=(m0["x"] - 5, ln["wall_z"] - 3, 11, 7), padding=0, ppc=PLAY_PPC)

    _compat_foreign(t, lanes)        # LAST in the chain, and chain state restored: compat never gates a Graffiti row


# ----------------------------------------------------------- galleries (bars 3-6, 8, 9, 10)

_PAGE = 4          # defs per run-of-four slots
_REPEAT = 3        # copies per def per slot: Graphic_Random picks a variant per thing
_PAGES = [MARK_DEFS[i:i + _PAGE] for i in range(0, len(MARK_DEFS), _PAGE)]
_GAL_PAGES = [_PAGES[i:i + 4] for i in range(0, len(_PAGES), 4)]     # 4 runs per screen


def _place_run(t, x0, wall_z, defs, controls=None):
    """One wall run with `defs` placed on the floor row beside it; returns {def: [cells]} placed.
    Every placement is read back (spawn reports success and may place nothing)."""
    _wall_run(t, x0, wall_z, 20)
    ops, cells = [], {}
    for k, d in enumerate(defs):
        for j in range(_REPEAT):
            cx, cz = x0 + 1 + k * 5 + j, wall_z + 1
            ops.append("%s:%d,%d" % (d, cx, cz))
            cells.setdefault(d, []).append((cx, cz))
    for k in range(len(defs)):          # controls on the far side of the slot, same floor row
        if controls:
            ops.append("%s:%d,%d" % (controls, x0 + 1 + k * 5 + 4, wall_z + 1))
    t.bridge_call("jawa/spawn_batch", ops=";".join(ops))
    return cells


def _verify_run(t, x0, wall_z, cells):
    if not t._guard():
        return
    got = _marks_in(t, "%d,%d,22,3" % (x0, wall_z), defs=",".join(cells))
    have = {}
    for m in got:
        have[m["def"]] = have.get(m["def"], 0) + 1
    missing = [d for d in cells if not have.get(d)]
    if missing:
        raise ExpectationFailed("gallery placement dropped def(s) %s (read back %s)" % (missing, have))


@suite.chain("gallery")
def gallery(t):
    """Fixtures are rebuilt per page: `clear_area` also destroys walls. Variant coverage is by
    repetition (_REPEAT copies per def), NOT exact -- exact pinning needs a companion tool (plan 6.12)."""
    x, z = t.anchor
    for pi, runs in enumerate(_GAL_PAGES):
        x0, z0 = x - 12, z - 10

        def build(runs=runs, x0=x0, z0=z0, controls=None, per_run=None):
            _prep_site(t, 50)
            placed = []
            for r, defs in enumerate(runs):
                wz = z0 + r * 6
                cells = _place_run(t, x0, wz, defs, controls)
                placed.append((wz, cells))
            t.bridge_call("jawa/map_commit")              # fixture write
            for wz, cells in placed:
                _verify_run(t, x0, wz, cells)
            return placed

        with t.component("gallery_page_%d" % pi,
                         shows=["mark_reads_at_play_zoom", "mark_reads_as_deliberate",
                                "mark_register_is_punk_urban", "mark_carries_no_earth_signage"]):
            build()
            t.screenshot(rect=(x0, z0 - 1, 22, 6 * len(runs)), ppc=PLAY_PPC)

        for ri, defs in enumerate(runs):
            with t.component("closeup_page_%d_%d" % (pi, ri), shows=["never_real_world_english"]):
                placed = build(runs=[defs])
                t.screenshot(rect=(x0, z0 - 1, 22, 3), padding=0, ppc=PLAY_PPC)

            with t.component("dirt_page_%d_%d" % (pi, ri), shows=["never_reads_as_dirt"]):
                build(runs=[defs], controls="Filth_Dirt")
                t.screenshot(rect=(x0, z0 - 1, 22, 3), padding=0, ppc=PLAY_PPC)


@suite.chain("beauty_pair")
def beauty_pair(t):
    """Bar 8: Vandal (Beauty -15) left, TallyMarks (-3) right, Beauty read off the spawned things."""
    x, z = t.anchor
    with t.component("site_ready_beauty_pair"):
        _prep_site(t, 40)
        _wall_run(t, x - 8, z, 17)
        t.bridge_call("jawa/map_commit")
        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d;RM_Graffiti_TallyMarks:%d,%d"
                      % (VANDAL_DEF, x - 4, z + 1, x + 4, z + 1))

    with t.component("beauty_pair", shows=["mark_ugliness_is_visible"]):
        r = t.bridge_call("jawa/list_things", defName="%s,RM_Graffiti_TallyMarks" % VANDAL_DEF,
                          rect="%d,%d,17,3" % (x - 8, z))
        if t._guard():
            rows = {(a.get("def") or a.get("defName")): a.get("id") for a in ((r or {}).get("things") or [])}
            want = {VANDAL_DEF: -15.0, "RM_Graffiti_TallyMarks": -3.0}
            for d, beauty in want.items():
                if d not in rows:
                    raise ExpectationFailed("%s not placed in the pair" % d)
                st = t.bridge_call("jawa/thing_stats", thing=rows[d], stats="Beauty")
                val = None
                for th in (st or {}).get("things") or []:
                    for s in th.get("stats") or []:
                        if s.get("defName") == "Beauty":
                            val = s.get("value")
                if val is None or abs(float(val) - beauty) > 0.01:
                    raise ExpectationFailed("%s Beauty read %r, expected %s" % (d, val, beauty))
        t.screenshot(rect=(x - 8, z - 1, 17, 4), padding=0, ppc=PLAY_PPC)


# ------------------------------------------------------------------ settings (all six)

def _flip(t, comp, field):
    with t.component(comp, toggle=field):
        t.set_setting(SETTINGS, {field: False})
        t.set_setting(SETTINGS, {field: True})


@suite.chain("viewer_reaction_toggle_flips")
def viewer_reaction_toggle_flips(t):
    """Write + read-back only: no live content exercises it in Graffiti alone (module docstring)."""
    _flip(t, "viewer_reaction_setting_flips", "viewerReactionEnabled")


@suite.chain("breach_bias_toggle_flips")
def breach_bias_toggle_flips(t):
    """Write + read-back only: the behavioural A/B (a breaching raid biased toward a WarningGlyph) is not built."""
    _flip(t, "breach_bias_setting_flips", "breachBiasEnabled")


@suite.chain("raid_exit_tag_toggle_flips")
def raid_exit_tag_toggle_flips(t):
    """Closes the floor gap. Behavioural A/B (an exiting raider tags on/off) is a plan DIAGNOSTIC,
    not built here."""
    _flip(t, "raid_exit_tag_setting_flips", "raidExitTaggingEnabled")


@suite.chain("auto_clean_protection_toggle_flips")
def auto_clean_protection_toggle_flips(t):
    """Closes the floor gap (see raid_exit_tag_toggle_flips)."""
    _flip(t, "auto_clean_protection_setting_flips", "autoCleanProtectionEnabled")


# ------------------------------------------------------- raid marks: retaken, weathered, pressure (scenes.json)
# Staged through the mod's own A2 probe (RM_GraffitiProof.RaidStart / RaidExit, RM_GraffitiProof.cs:172,219): its site is in the
# Home area (RM_GraffitiProof.cs:44), so its exit tags are the enemy marks RM_Graffiti_EnemyClaim counts (GraffitiSocial.cs:227).

PROOF = "RimMandrake.Graffiti.RM_GraffitiProof"
STAGE = "RimMandrake.Graffiti.RM_GraffitiStage"
SOCIAL_PROOF = "RimMandrake.Graffiti.RM_GraffitiSocialProof"
ENEMY_CLAIM = "RM_Graffiti_EnemyClaim"
SCRUB_JOB = "RM_ScrubMark"                  # WorkGiver_ScrubGraffitiDesignated's job (WorkGiver_ScrubGraffitiDesignated.cs:42)
SITE_SETTINGS_ITEM = "RIMMANDRAKE_CHECK_GRAFFITI_SITE_SETTINGS_SIX_OF_EIGHT"
PRESSURE_ITEM = "RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL"
ROOFED_TWIN_ITEM = "RIMMANDRAKE_PAINT_GRAFFITI_ROOFED_TWIN_RANDOM_ENEMY_WONT_DO"
CRAFTS = ["awful", "poor", "normal", "good", "excellent", "masterwork", "legendary"]   # RM_GraffitiKernel.cs:992, QualityCategory labels


def _pressure_built():
    """True once the mod's source carries a raider-pressure setting (the scene's 3 settings, PRESSURE_ITEM). A source read, so an
    unlanded dependency fails by name before any game state is touched."""
    pat = re.compile(r"public\s+static\s+\w+\s+\w*[Pp]ressure\w*\s*=")
    src = os.path.join(_HERE, "Source")
    for d, dirs, files in os.walk(src):
        dirs[:] = [x for x in dirs if x not in ("SelfTest", "obj", "bin")]
        for f in files:
            if f.endswith(".cs") and pat.search(open(os.path.join(d, f), encoding="utf-8-sig").read()):
                return True
    return False


def _need_pressure(what):
    if not _pressure_built():
        raise ExpectationFailed("UNLANDED: %s (no raider-pressure setting in Graffiti/Source): %s cannot be read" % (PRESSURE_ITEM, what))
    raise ExpectationFailed("MISSING TOOL: %s has landed but this scene has no reader for %s yet: write it here, naming the "
                            "settings and letter it built (never a guessed name)" % (PRESSURE_ITEM, what))


def _static(t, typ, method, args=""):
    """jawa/static_call on one of the mod's probes -> (result text, ticksGame); a refusal or REFUSED answer fails the component."""
    r = t.bridge_call("jawa/static_call", type=typ, method=method, args=args)
    if not t._guard():
        return "", None
    text = str((r or {}).get("result") or "")
    if not (r or {}).get("success") or text.startswith("REFUSED") or text.startswith("error="):
        raise ExpectationFailed("%s.%s(%r) answered %r" % (typ.rsplit(".", 1)[-1], method, args, r))
    return text, (r or {}).get("ticksGame")


def _probe_fields(text):
    """'EXIT mid 0 | after 3 | faction Pirate Band' -> {'mid': '0', 'after': '3', 'faction': 'Pirate Band'} (the first word is the verb)."""
    out = {}
    for i, part in enumerate(text.split("|")):
        w = part.split()[1:] if i == 0 else part.split()
        if w:
            out[w[0]] = " ".join(w[1:])
    return out


def _territory_stage(n):
    """RM_GraffitiKernel.TerritoryStage (RM_GraffitiKernel.cs:1257): -1 none, 0 for 1-2 marks, 1 for 3-5, 2 for 6+."""
    return -1 if n <= 0 else (0 if n <= 2 else (1 if n <= 5 else 2))


def _weather_days(form, craft, outdoors, idn):
    """RM_GraffitiKernel.WeatherDays (RM_GraffitiKernel.cs:1208), transcribed; T_WEATHER_OFFLINE pins the kernel it copies."""
    days = 22.0 if outdoors else 44.0
    days *= {"Paste": 0.5, "Stencil": 1.3, "Scrawl": 0.8}.get(form, 1.0)
    days *= [0.75, 0.85, 1.0, 1.1, 1.2, 1.35, 1.35][max(0, min(6, craft))]
    h = (idn * 2246822519 + 3266489917) & 0xFFFFFFFF
    return days * (0.75 + 0.5 * ((h >> 9) & 1023) / 1023.0)


def _whole_map(t):
    mm = t.bridge_call("jawa/map_info") or {}
    return "0,0,%s,%s" % (mm.get("sizeX") or 250, mm.get("sizeZ") or 250)


def _all_marks(t, rect):
    """{thing id: {def, x, z}} for every mark of this mod standing in rect (a truncated read fails, never reads as fewer)."""
    r = t.bridge_call("jawa/list_things", defName=MARK_CSV, rect=rect, limit=2000)
    if not t._guard():
        return {}
    if not (r or {}).get("success", True) or (r or {}).get("isCompleteList") is False:
        raise ExpectationFailed("jawa/list_things unreadable or truncated: %r" % (r,))
    return {x.get("id"): {"def": x.get("def") or x.get("defName"), "x": (x.get("position") or {}).get("x", x.get("x")),
                          "z": (x.get("position") or {}).get("z", x.get("z"))} for x in ((r or {}).get("things") or []) if x.get("id")}


def _claim_holders(t):
    """{pawn id: EnemyClaim stage} for every pawn now holding RM_Graffiti_EnemyClaim (jawa/pawn_thoughts per listed pawn)."""
    held = {}
    for p in _all_colonists(t):
        r = t.bridge_call("jawa/pawn_thoughts", pawn=p["id"]) or {}
        for th in r.get("thoughts") or []:
            if th.get("def") == ENEMY_CLAIM:
                held[p["id"]] = th.get("stage")
    return held


def _claim_stage(t, settle=300):
    """The colony's one EnemyClaim stage (it is map-wide: every holder must agree), or None when nobody holds it."""
    t.wait_ticks(settle)                     # situational thoughts are recomputed on their own cadence, not on the scrub's tick
    held = _claim_holders(t)
    stages = sorted(set(held.values()), key=str)
    if len(stages) > 1:
        raise ExpectationFailed("EnemyClaim holders disagree on its stage (it counts the map's marks, one number): %s" % held)
    return stages[0] if stages else None


def _site_start(t):
    """Every scene's shared start: Graffiti loaded (RM_GraffitiProof.Loaded), the site preflight clean (northstar_site.preflight), and
    socialEnabled at its shipped true."""
    import importlib.util          # Graffiti's own northstar_site.py, by path: a bare import can find Pyrelands' (modcheck/biome_site.py:66)
    spec = importlib.util.spec_from_file_location("graffiti_northstar_site", os.path.join(_HERE, "northstar_site.py"))
    northstar_site = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(northstar_site)
    loaded, _ = _static(t, PROOF, "Loaded")
    if t._guard() and "graffiti True" not in loaded:
        raise ExpectationFailed("RM_GraffitiProof.Loaded: %r" % loaded)

    class _S(object):
        call = staticmethod(lambda tool, **q: t.bridge_call(tool, **q))
    bad = northstar_site.preflight(_S()) if t._guard() else []
    if bad:
        raise ExpectationFailed("site preflight: %s" % "; ".join(bad))
    r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="socialEnabled")
    if t._guard() and str((r or {}).get("value")).lower() != "true":
        raise ExpectationFailed("socialEnabled reads %r, not its shipped true (RM_GraffitiMod.cs:47); EnemyClaim is off without it "
                                "(the site's social pair is %s's to check)" % ((r or {}).get("value"), SITE_SETTINGS_ITEM))


def _raid_start(t, comp):
    """The raid scenes' start: _site_start, then one A2 raid exit. -> (raid faction name, {id: mark} of the exit tags it left)."""
    _site_start(t)
    rect = _whole_map(t)
    before = _all_marks(t, rect)
    started, _ = _static(t, PROOF, "RaidStart")
    exit_, _ = _static(t, PROOF, "RaidExit")       # no tick between: the exit tags are the only new marks
    if not t._guard():
        return None, {}
    tags = {k: v for k, v in _all_marks(t, rect).items() if k not in before}
    f = _probe_fields(exit_)
    if str(f.get("exterior")) != str(len(tags)) or not tags:
        raise ExpectationFailed("%s: the raid exit left %d new mark(s), probe says %r" % (comp, len(tags), exit_))
    t._current.detail = "%s; %s; %d exit tag(s)" % (started, exit_, len(tags))
    return _probe_fields(started).get("faction"), tags


def _scrub_one(t, mid, m, seen_jobs, budget=6000, step=500):
    """Designate one mark with the player's Scrub drag (RM_GraffitiStage.Scrub, through Designator_ScrubGraffiti) and run the clock until it
    is gone. Records each colonist job seen meanwhile in seen_jobs. -> ticks it took; a mark still standing at the budget fails."""
    _static(t, STAGE, "Scrub", "%d,%d,1,1" % (m["x"], m["z"]))
    rect = "%d,%d,1,1" % (m["x"], m["z"])
    waited = 0
    while waited < budget and t._guard():
        t.wait_ticks(step)
        waited += step
        for p in _all_colonists(t):
            g = t.bridge_call("jawa/pawn_get", pawn=p["id"])
            if SCRUB_JOB in str(g):
                seen_jobs.add(p["id"])
        if mid not in _all_marks(t, rect):
            return waited
    raise ExpectationFailed("mark %s (%s at %d,%d) still stands %d ticks after its Scrub designation" % (mid, m["def"], m["x"], m["z"], budget))


@suite.chain("scene_raid_retaken")
def scene_raid_retaken(t):
    """sc_raid_retaken (raid_mark_troubles): scrubbing a raid's exit tags one by one walks RM_Graffiti_EnemyClaim's stage down with the
    count, WorkGiver_ScrubGraffitiDesignated does each scrub, and the thought ends with the last mark. Control: one mark left standing for a
    day keeps the thought (it does not time out). Restore: the runner destroys the quicktest map; nothing persistent changed.
    The raider-pressure settings of the start are PRESSURE_ITEM's; until it lands they are not part of this site."""
    order, steps, seen = [], [], set()
    with t.component("site_ready_raid_retaken"):
        faction, tags = _raid_start(t, "site_ready_raid_retaken")
        if t._guard():
            if len(tags) < 3:
                raise ExpectationFailed("only %d exit tag(s): a stage fall needs >= 3 (TerritoryStage, RM_GraffitiKernel.cs:1257)" % len(tags))
            order = sorted(tags.items(), key=lambda kv: (kv[1]["x"], kv[1]["z"]))
            s0 = _claim_stage(t)
            if s0 != _territory_stage(len(order)):
                raise ExpectationFailed("EnemyClaim stage %r at %d enemy marks, kernel says %d" % (s0, len(order), _territory_stage(len(order))))
            steps.append((len(order), s0))

    with t.component("enemy_claim_falls_with_scrubs"):
        if t._guard():
            for i, (mid, m) in enumerate(order[:-1]):
                _scrub_one(t, mid, m, seen)
                left = len(order) - i - 1
                st = _claim_stage(t)
                steps.append((left, st))
                if st != _territory_stage(left):
                    raise ExpectationFailed("EnemyClaim stage %r at %d marks left, kernel says %d (steps %s)" % (st, left, _territory_stage(left), steps))
            if not seen:
                raise ExpectationFailed("the marks went, but no colonist was seen on %s (WorkGiver_ScrubGraffitiDesignated): steps %s" % (SCRUB_JOB, steps))
            if not any(b[1] < a[1] for a, b in zip(steps, steps[1:])):
                raise ExpectationFailed("the stage never fell with the count: %s" % steps)
            t._current.detail = "(marks, stage): %s; scrubbers %s" % (steps, sorted(seen))

    with t.component("control_one_mark_keeps_claim"):
        if t._guard():
            t.wait_ticks(60000)              # a day with one mark left: a thought that timed out on its own would be gone
            st = _claim_stage(t)
            if st != 0:
                raise ExpectationFailed("one enemy mark standing a day on: EnemyClaim stage %r, expected 0 (it must stay)" % st)

    with t.component("enemy_claim_ends_with_last_mark"):
        if t._guard():
            mid, m = order[-1]
            _scrub_one(t, mid, m, seen)
            st = _claim_stage(t)
            if st is not None:
                raise ExpectationFailed("every enemy mark scrubbed, EnemyClaim still held at stage %r" % st)


def _age_by(t, days, why):
    """Advance TicksGame by `days` (jawa/time_set_ticks, a declared time exception), then run the scene's 2500 ticks so the weathering pass
    (GraffitiSocial's fade >= 1 Destroy) sees the new age."""
    _, now = _static(t, PROOF, "Loaded")
    if not t._guard():
        return
    if now is None:
        raise ExpectationFailed("static_call returned no ticksGame: cannot age the marks")
    r = t.bridge_call("jawa/time_set_ticks", ticks=int(now) + int(days * 60000), timeException=True, why=why)
    if not (r or {}).get("success", False):
        raise ExpectationFailed("jawa/time_set_ticks refused: %r" % (r,))
    t.wait_ticks(2500)


def _craft_at(t, x, z):
    """The craft of the mark at (x, z) from RM_GraffitiSocialProof.Marks ('craft <label>'; '-' is RM_GraffitiKernel.Normal, Filth_Mark.cs:196)."""
    text, _ = _static(t, SOCIAL_PROOF, "Marks")
    for line in text.splitlines():
        if line.startswith("(%d, 0, %d) " % (x, z)):
            mm = re.search(r"\bcraft (\S+)", line)
            lab = mm.group(1) if mm else "-"
            return (CRAFTS.index(lab) if lab in CRAFTS else 2), line
    raise ExpectationFailed("RM_GraffitiSocialProof.Marks lists no mark at (%d, %d)" % (x, z))


@suite.chain("scene_weathered_raid_mark")
def scene_weathered_raid_mark(t):
    """sc_weathered_raid_mark (weathering_bounds_marks, raid_mark_troubles): a raid's unroofed exit mark weathers away while its same-age
    roofed twin stands, so EnemyClaim stays; aged past its own life the roofed one goes too and EnemyClaim ends (and A's raider pressure
    lifts, once PRESSURE_ITEM lands). Control: the roofed twin at the first age still stands. Restore: the runner destroys the quicktest
    map. The scene asks the twin to read faded at the first age; the kernel does not promise it (open/roofed life is 0.3..0.83 for one form
    and craft, RM_GraffitiKernel.cs:1208, and fading starts at 0.6), so its weather step is recorded, not judged."""
    tags, twin = {}, None
    with t.component("site_ready_weathered_raid_mark"):
        faction, tags = _raid_start(t, "site_ready_weathered_raid_mark")
        if t._guard():
            raise ExpectationFailed("MISSING TOOL: no probe paints a mark by the raid's faction (%s) under a roof at the raid's tick: "
                                    "RM_GraffitiProof.RaidExit tags exterior walls only (RM_GraffitiProof.cs:219) and HostileThought "
                                    "picks a random enemy (RM_GraffitiProof.cs:294); filed as %s" % (faction, ROOFED_TWIN_ITEM))

    open_life = roof_life = None
    with t.component("unroofed_mark_weathers_away_first"):
        if t._guard():
            (oid, om), (tid, tm) = sorted(tags.items())[0], twin
            oc, _ = _craft_at(t, om["x"], om["z"])
            tc, _ = _craft_at(t, tm["x"], tm["z"])
            num = lambda i: int(re.search(r"(\d+)$", i).group(1))
            open_life = _weather_days(FORM_OF.get(om["def"], "Scrawl"), oc, True, num(oid))
            roof_life = _weather_days(FORM_OF.get(tm["def"], "Scrawl"), tc, False, num(tid))
            if roof_life <= open_life * 1.02:
                raise ExpectationFailed("SITE: the twin's life %.1f d is not past the open mark's %.1f d; re-stage" % (roof_life, open_life))
            _age_by(t, open_life * 1.02, "sc_weathered_raid_mark: past the unroofed exit mark's WeatherDays")
            left = _all_marks(t, _whole_map(t))
            if oid in left:
                raise ExpectationFailed("unroofed mark %s still stands %.1f d past placing (its life %.1f d)" % (oid, open_life * 1.02, open_life))
            st = _claim_stage(t)
            if st is None:
                raise ExpectationFailed("the roofed twin stands but EnemyClaim ended with the unroofed mark")

    with t.component("control_roofed_twin_stands"):
        if t._guard():
            tid, tm = twin
            if tid not in _all_marks(t, _whole_map(t)):
                raise ExpectationFailed("the roofed twin %s is gone at %.1f d of its %.1f d life: weathering ignores the roof" % (tid, open_life * 1.02, roof_life))
            _, line = _craft_at(t, tm["x"], tm["z"])
            t._current.detail = "twin at the first age: %s" % line

    with t.component("roofed_twin_weathers_and_claim_ends"):
        if t._guard():
            tid, tm = twin
            _age_by(t, roof_life * 1.02 - open_life * 1.02, "sc_weathered_raid_mark: past the roofed twin's WeatherDays")
            if tid in _all_marks(t, _whole_map(t)):
                raise ExpectationFailed("roofed twin %s still stands past its %.1f d life" % (tid, roof_life))
            st = _claim_stage(t)
            if st is not None:
                raise ExpectationFailed("both raid marks weathered away, EnemyClaim still held at stage %r" % st)

    with t.component("raider_pressure_lifts_with_the_marks"):
        if t._guard():
            _need_pressure("faction A's raider pressure before and after its marks weather away")


@suite.chain("scene_raider_pressure")
def scene_raider_pressure(t):
    """sc_raider_pressure (raider_pressure): in each mode (larger, then sooner) A's raid, with two exit marks standing, beats B's at the same
    storyteller points by the setting and a letter names A and points at its marks; one A mark scrubbed keeps the pressure; both scrubbed and
    A matches B. Control: the pressure setting off gives equal raids and no letter. Restore: the runner destroys the quicktest map.
    Every row waits on PRESSURE_ITEM (the switch, mode and push-size settings and the letter); until it lands each fails by that name."""
    with t.component("site_ready_raider_pressure"):
        if not _pressure_built():
            raise ExpectationFailed("UNLANDED: %s: no raider-pressure setting in Graffiti/Source, so there is no pressure to stage" % PRESSURE_ITEM)
        faction, tags = _raid_start(t, "site_ready_raider_pressure")
        if t._guard() and len(tags) < 2:
            raise ExpectationFailed("faction A (%s) left %d exit mark(s); the scene needs two" % (faction, len(tags)))
    for mode in ("larger", "sooner"):
        with t.component("pressure_%s_names_A_and_beats_B" % mode):
            _need_pressure("the %s-mode raid of A against B and the letter naming A" % mode)
        with t.component("pressure_%s_stays_with_one_scrubbed" % mode):
            _need_pressure("A's %s-mode pressure with one of its marks scrubbed" % mode)
        with t.component("pressure_%s_gone_with_both_scrubbed" % mode):
            _need_pressure("A against B in %s mode with both marks scrubbed" % mode)
    with t.component("control_pressure_off_equal_raids"):
        _need_pressure("A against B with the pressure switch off (equal raids, no letter)")


# ------------------------------------------------- own fun, rereads, temperament (scenes.json: sc_own_fun, sc_rereads, sc_temperament)
# Cast through the mod's own social hands (RM_GraffitiSocialProof.cs): Recruit/Cast "Nick/Trait:degree/art" (:47, :68), Befriend (:31),
# Order "painter/def/about/x,z" (:192), Temper (:127), Marks (:177), Ledger "trace" (:269: every read and reread GraffitiSocial.Reads traces,
# GraffitiSocial.cs:452, with its tick); RM_GraffitiStage.Who (RM_GraffitiStage.cs:653) for each colonist's joy and job.

PAINT_JOB = "RM_PaintGraffitiJob"            # what JoyGiver_PaintGraffiti (JoyGiverDefs_Graffiti.xml:8) and JobGiver_IdleTag.cs:20 both give
MOCKERY_DEF = "RM_Graffiti_Mockery"          # ThingDefs_GraffitiSocial.xml:7, meaning Mockery
MAKER_THOUGHT = "RM_Graffiti_LeftMyMark"     # the painter's own thought for a mark about nobody (GraffitiSocial.cs:779)
CLEAN_BREAK = "RM_GraffitiCompulsiveCleaningBreak"          # MentalStateDefs_Graffiti.xml:46
CLEAN_STATE = "RM_GraffitiCompulsiveCleaningState"
READ_AGAIN_TICKS = 60000                     # RM_GraffitiKernel.ReadAgainTicks (RM_GraffitiKernel.cs:767)
SIGHT_RADIUS_SQ = 49                         # RM_GraffitiKernel.SightRadiusSq (RM_GraffitiKernel.cs:764)
BREAK_GATE_ITEM = "RIMMANDRAKE_PROBE_GRAFFITI_CLEAN_BREAK_GATE_FORCE_SKIPS_IT"


def _thought_stages():
    """{ThoughtDef: [baseMoodEffect per stage]} for this mod's ThoughtDefs, read from Defs/ at import (never a number typed here)."""
    import xml.etree.ElementTree as ET
    out = {}
    ddir = os.path.join(_HERE, "Defs")
    for fn in sorted(os.listdir(ddir)) if os.path.isdir(ddir) else []:
        if fn.startswith("ThoughtDefs") and fn.endswith(".xml"):
            for d in ET.parse(os.path.join(ddir, fn)).getroot():
                st = d.find("stages")
                if d.findtext("defName") and st is not None:
                    out[d.findtext("defName")] = [float(s.findtext("baseMoodEffect") or 0) for s in st]
    return out


THOUGHT_STAGES = _thought_stages()


def _cast(t, method, spec):
    """RM_GraffitiSocialProof.Recruit or .Cast -> (nick, [trait specs]) read off the probe's own answer, never off `spec`."""
    text, _ = _static(t, SOCIAL_PROOF, method, spec)
    if not t._guard():
        return spec.split("/")[0], []
    m = re.match(r"(\S+) \[([^\]]*)\]", text)
    if not m:
        raise ExpectationFailed("%s(%r) answered %r" % (method, spec, text))
    return m.group(1), [x for x in m.group(2).split(",") if x]


def _temper(t, nick):
    """RM_GraffitiSocialProof.Temper -> {numb, bad, good, fine, ugly, neat, urge, joy, ...} as the table reads this colonist."""
    text, _ = _static(t, SOCIAL_PROOF, "Temper", nick)
    w = text.split()[1:]
    return dict(zip(w[0::2], w[1::2]))


def _who(t):
    """RM_GraffitiStage.Who -> {nick: {joy, job, give, can, ...}}."""
    text, _ = _static(t, STAGE, "Who")
    out = {}
    for row in text[len("WHO "):].split(" || ") if text.startswith("WHO ") else []:
        parts = row.split()
        if parts:
            out[parts[0]] = dict(p.split("=", 1) for p in parts[1:] if "=" in p)
    return out


def _joy(who, nick):
    try:
        return float(who[nick]["joy"])
    except (KeyError, ValueError):
        raise ExpectationFailed("RM_GraffitiStage.Who has no joy for %s: %r" % (nick, who.get(nick)))


def _hold_at(t, nick, x, z, ticks=900):
    """Draft this colonist and walk it to (x, z), where a drafted pawn waits: a viewer that must not wander off its spot."""
    t.bridge_call("jawa/set_draft", pawnId=nick, drafted=True)
    t.bridge_call("jawa/order_pawn", pawnId=nick, x=x, z=z, waitTicks=0)
    t.wait_ticks(ticks)


def _walls(t, cells, door=None):
    ops = ["Wall:%d,%d" % c for c in cells if c != door] + (["Door:%d,%d" % door] if door else [])
    t.bridge_call("jawa/spawn_batch", ops=";".join(ops), stuff="Steel")


def _box(x0, z0, x1, z1):
    """The perimeter cells of the rectangle (x0, z0)..(x1, z1), inclusive."""
    return sorted({(x, z) for x in range(x0, x1 + 1) for z in (z0, z1)} | {(x, z) for z in range(z0, z1 + 1) for x in (x0, x1)})


def _order_mark(t, painter, defn, about, x, z, budget=6000, step=500):
    """The player orders `painter` to paint `defn` about `about` at floor cell (x, z) (RM_GraffitiSocialProof.Order); the clock runs until
    a mark stands there. -> (thing id, mark)."""
    _static(t, SOCIAL_PROOF, "Order", "%s/%s/%s/%d,%d" % (painter, defn, about, x, z))
    waited = 0
    while waited < budget and t._guard():
        t.wait_ticks(step)
        waited += step
        got = _all_marks(t, "%d,%d,1,1" % (x, z))
        if got:
            return sorted(got.items())[0]
    if not t._guard():
        return None, None
    raise ExpectationFailed("%s ordered to paint %s about %r at (%d,%d): no mark there after %d ticks" % (painter, defn, about, x, z, budget))


def _marks_by(t, nick):
    """Lines of RM_GraffitiSocialProof.Marks whose maker is `nick`."""
    text, _ = _static(t, SOCIAL_PROOF, "Marks")
    return [ln for ln in text.splitlines() if (" by %s about " % nick) in ln]


def _graffiti_thoughts(t, nick):
    """[{def, moodOffset, stage}] of this mod's MOOD thoughts on `nick` (jawa/pawn_thoughts)."""
    r = t.bridge_call("jawa/pawn_thoughts", pawn=nick) or {}
    if t._guard() and not r.get("success", False):
        raise ExpectationFailed("jawa/pawn_thoughts %s unreadable: %r" % (nick, r))
    return [x for x in r.get("thoughts") or [] if str(x.get("def", "")).startswith("RM_Graffiti_")]


_READ_RE = re.compile(r"^\s*\.\s+(\d+) (\S+) (reads|rereads) (\S+)@\((-?\d+), -?\d+, (-?\d+)\)")
_OPINION_RE = re.compile(r"^  opinion of (\S+) ([+-][\d.]+) (.*) \(age (\d+)\)$")


def _ledger(t):
    """RM_GraffitiSocialProof.Ledger("trace"), which also empties the trace ring (60 lines, GraffitiSocial.cs:1070): read it at least as
    often as 60 reads could happen. -> (reads [(tick, nick, kind, def, x, z)], {nick: [ledger lines under that colonist]})."""
    text, _ = _static(t, SOCIAL_PROOF, "Ledger", "trace")
    reads, per, cur = [], {}, None
    for ln in text.splitlines():
        m = _READ_RE.match(ln)
        if m:
            reads.append((int(m.group(1)), m.group(2), m.group(3), m.group(4), int(m.group(5)), int(m.group(6))))
        elif ln and not ln.startswith(" ") and " [" in ln:
            cur = ln.split(" ", 1)[0]
            per[cur] = []
        elif cur and (ln.startswith("  mood ") or ln.startswith("  opinion of ")):
            per[cur].append(ln)
        elif not ln.startswith("  "):
            cur = None
    return reads, per


@suite.chain("scene_own_fun")
def scene_own_fun(t):
    """sc_own_fun (own_fun, inv_joy_and_idle_tag): a colonist low on joy picks the paint joy job, its joy rises and it gets the maker's
    thought; a second colonist, joy not low, idles into JobGiver_IdleTag and tags the wall. Control: painting switched off, neither paints.
    Restore: the runner destroys the quicktest map; the setting is put back here. Which giver handed a job out is not readable (Who says what
    the joy giver WOULD give now, not who gave the running job): the joy colonist's job is read as recreation by its low joy at the start,
    the idle colonist's as the idle tag by its joy being not low when it is seen painting."""
    x, z = t.anchor
    fun, idle = "GrfFun", "GrfIdle"
    rect = "%d,%d,15,6" % (x - 7, z - 3)

    def joys(lvl_fun, lvl_idle):
        for nick, lvl in ((fun, lvl_fun), (idle, lvl_idle)):
            t.bridge_call("jawa/pawn_need", pawn=nick, action="need", need="Joy", level=lvl)
        return _who(t) if t._guard() else {}

    with t.component("site_ready_own_fun"):
        _site_start(t)
        _prep_site(t, 40)
        _wall_run(t, x - 6, z + 1, 13)
        t.bridge_call("jawa/map_commit")                 # fixture write (walls/terrain), never marks
        for nick in (fun, idle):
            _cast(t, "Recruit", "%s//8" % nick)
            _settle_painter(t, nick)
        _no_cleaning(t)
        who = joys(0.2, 0.9)
        if t._guard():
            jf, ji = _joy(who, fun), _joy(who, idle)
            if not (jf < 0.3 and ji >= 0.5):
                raise ExpectationFailed("joy set 0.2/0.9 reads %s=%.2f %s=%.2f (needs < 0.3 and not low)" % (fun, jf, idle, ji))
            urge = [_temper(t, n).get("urge") for n in (fun, idle)]
            if any(u in (None, "0.00") for u in urge):
                raise ExpectationFailed("a colonist has no paint urge (Temper urge %s): GraffitiTemperament.Urge is 0, it can never paint" % urge)
            t._current.detail = "joy %s=%.2f %s=%.2f, urge %s" % (fun, jf, idle, ji, urge)

    seen, joy0 = {}, {}
    with t.component("own_fun_runs"):
        waited = 0
        while waited < 30000 and t._guard() and not (fun in seen and idle in seen and _marks_by(t, fun) and _marks_by(t, idle)):
            t.wait_ticks(500)
            waited += 500
            who = _who(t)
            for nick in (fun, idle):
                if nick not in seen and (who.get(nick) or {}).get("job") == PAINT_JOB:
                    seen[nick] = (waited, _joy(who, nick))
            if idle not in seen and _joy(who, idle) < 0.5:          # keep the idle hand's joy not low: its tag must not be recreation
                t.bridge_call("jawa/pawn_need", pawn=idle, action="need", need="Joy", level=0.9)
        t.wait_ticks(1500)                                           # let the last job finish and the maker thought land
        if t._guard():
            t._current.detail = "seen on %s (ticks, joy): %s after %d ticks" % (PAINT_JOB, seen, waited)

    with t.component("joy_paint_job_runs_and_joy_rises"):
        if t._guard():
            if fun not in seen:
                raise ExpectationFailed("%s (joy < 0.3) never seen on %s in 30000 ticks: the joy giver was not chosen" % (fun, PAINT_JOB))
            after = _joy(_who(t), fun)
            mine = _marks_by(t, fun)
            if after <= seen[fun][1] or not mine:
                raise ExpectationFailed("%s on the paint job at joy %.2f: joy now %.2f, marks by it %d" % (fun, seen[fun][1], after, len(mine)))
            t._current.detail = "joy %.2f -> %.2f; %s" % (seen[fun][1], after, mine[0])

    with t.component("maker_thought_appears"):
        if t._guard():
            th = [x for x in _graffiti_thoughts(t, fun) if x.get("def") == MAKER_THOUGHT]
            if not th:
                raise ExpectationFailed("%s painted but holds no %s: its thoughts %s" % (fun, MAKER_THOUGHT, _graffiti_thoughts(t, fun)))
            t._current.detail = "%s %+.1f" % (MAKER_THOUGHT, float(th[0].get("moodOffset") or 0))

    with t.component("idle_hand_tags_the_wall"):
        if t._guard():
            mine = _marks_by(t, idle)
            if idle not in seen or not mine:
                raise ExpectationFailed("%s (joy kept >= 0.5) seen painting %s, marks by it %d: JobGiver_IdleTag gave no tag" % (idle, seen.get(idle), len(mine)))
            if seen[idle][1] < 0.3:
                raise ExpectationFailed("%s was seen painting at joy %.2f: that is recreation, not an idle tag" % (idle, seen[idle][1]))
            t._current.detail = "%s at joy %.2f: %s" % (idle, seen[idle][1], mine[0])

    with t.component("control_painting_off_no_paint", toggle="paintingEnabled"):
        try:
            t.set_setting(SETTINGS, {"paintingEnabled": False})
            before = {n: len(_marks_by(t, n)) for n in (fun, idle)}
            joys(0.2, 0.9)
            jobs, gives, waited = set(), set(), 0
            while waited < 15000 and t._guard():
                t.wait_ticks(500)
                waited += 500
                who = _who(t)
                for nick in (fun, idle):
                    jobs.add((nick, (who.get(nick) or {}).get("job")))
                gives.add((who.get(fun) or {}).get("give"))
            if t._guard():
                after = {n: len(_marks_by(t, n)) for n in (fun, idle)}
                painted = [j for j in jobs if j[1] == PAINT_JOB]
                if painted or after != before or gives - {"null"}:
                    raise ExpectationFailed("painting off: on %s %s, marks %s -> %s, joy giver offers %s" % (PAINT_JOB, painted, before, after, gives))
                t._current.detail = "15000 ticks off: jobs seen %s" % sorted({j[1] for j in jobs}, key=str)
        finally:
            t.set_setting(SETTINGS, {"paintingEnabled": True})


@suite.chain("scene_rereads")
def scene_rereads(t):
    """sc_rereads (rereads_daily): a walker passing one mockery hourly for two days rereads it at most once a day (READ_AGAIN_TICKS), and its
    opinion off the mark is made once and never renewed; a viewer who only sees the mark across the open yard and one shut in a room with a
    mark it never walks past each read theirs. Control: a second, different mark on the route gives its own first read; a viewer behind
    the route wall, within sight radius of the mockery, reads nothing. Restore: the runner destroys the quicktest map."""
    x, z = t.anchor
    walker, painter, subject = "GrfWalk", "GrfBrush", "GrfButt"
    yard, roomed, walled = "GrfYard", "GrfRoom", "GrfWall"
    m1, m2, m3 = (x - 4, z - 1), (x + 4, z - 1), (x + 13, z + 3)     # mockery and plain mark on the route; a mockery in the closed room
    ids, reads, opinions0, held = {}, [], {}, set()

    def poll():
        got, per = _ledger(t)
        reads.extend(got)
        held.update(n for n, lines in per.items() if lines)
        return got, per

    with t.component("site_ready_rereads"):
        _site_start(t)
        _prep_site(t, 60)
        _walls(t, [(i, z) for i in range(x - 10, x + 11)])                          # the route wall; marks on its south face
        _walls(t, [c for c in _box(x - 7, z, x - 1, z + 6) if c[1] != z], door=(x - 4, z + 6))                # the walled-off control's room, behind the route wall
        _walls(t, _box(x + 12, z + 2, x + 18, z + 8), door=(x + 15, z + 8))         # the closed room with its own mark
        t.bridge_call("jawa/map_commit")
        for nick in (walker, painter, subject, yard, roomed, walled):
            _cast(t, "Recruit", "%s//%s" % (nick, 12 if nick == painter else ""))
            _settle_painter(t, nick)
        _no_cleaning(t)
        for v in (walker, yard, roomed, walled):          # they care about the subject, so a mockery of it moves them
            _static(t, SOCIAL_PROOF, "Befriend", "%s/%s" % (v, subject))
        _hold_at(t, walled, x - 4, z + 2)                 # 3 cells from m1, the route wall between
        _hold_at(t, roomed, x + 16, z + 6)
        _hold_at(t, yard, x - 4, z - 7)                   # 6 cells from m1 across the open yard; m2 is 10 away, out of sight radius
        _hold_at(t, walker, x - 14, z - 2)                # the route's west end, out of sight of both marks while they are painted
        for key, (cx, cz), defn in (("m1", m1, MOCKERY_DEF), ("m2", m2, VANDAL_DEF), ("m3", m3, MOCKERY_DEF)):
            ids[key] = _order_mark(t, painter, defn, subject if defn == MOCKERY_DEF else "", cx, cz)[0]
        t.bridge_call("jawa/set_draft", pawnId=painter, drafted=True)
        t.bridge_call("jawa/order_pawn", pawnId=painter, x=x + 25, z=z - 12, waitTicks=0)     # the painter away from every mark
        if t._guard():
            dist = (m1[0] - (x - 4)) ** 2 + (m1[1] - (z + 2)) ** 2
            if dist > SIGHT_RADIUS_SQ:
                raise ExpectationFailed("SITE: the walled-off viewer is out of sight radius of m1 (%d > %d)" % (dist, SIGHT_RADIUS_SQ))
            poll()                                         # reads while the marks went up count too (the yard and the room see them painted)
            if any(r[1] == walker for r in reads):
                raise ExpectationFailed("SITE: the walker read a mark before its walk: %s" % [r for r in reads if r[1] == walker])
            t._current.detail = "marks %s" % ids

    with t.component("walk_route_two_days"):
        ends = [(x - 8, z - 2), (x + 8, z - 2)]
        for leg in range(48):
            if not t._guard():
                break
            ex, ez = ends[leg % 2]
            t.bridge_call("jawa/order_pawn", pawnId=walker, x=ex, z=ez, waitTicks=0)
            t.wait_ticks(2500)
            got, per = poll()
            if not opinions0 and any(r[1] == walker and (r[4], r[5]) == m1 for r in got):
                opinions0 = {o.group(1) + " " + o.group(3): int(o.group(4))
                             for o in (_OPINION_RE.match(ln) for ln in per.get(walker, [])) if o}
        if t._guard():
            t._current.detail = "%d read line(s) in 48 legs" % len(reads)

    def at(nick, cell):
        return [r for r in reads if r[1] == nick and (r[4], r[5]) == cell]

    with t.component("reread_at_most_once_a_day"):
        if t._guard():
            r1 = at(walker, m1)
            ticks = [r[0] for r in r1]
            gaps = [b - a for a, b in zip(ticks, ticks[1:])]
            kinds = [r[2] for r in r1]
            if len(r1) < 2 or kinds[0] != "reads" or "reads" in kinds[1:]:
                raise ExpectationFailed("walker's reads of the mockery over two days: %s (want one first read, then rereads)" % r1)
            if any(g < READ_AGAIN_TICKS for g in gaps):
                raise ExpectationFailed("walker reread the mockery %s ticks apart (at most once per %d): %s" % (gaps, READ_AGAIN_TICKS, ticks))
            t._current.detail = "reads at %s, gaps %s" % (ticks, gaps)

    with t.component("opinion_changes_once"):
        if t._guard():
            _, per = poll()
            now = {o.group(1) + " " + o.group(3): int(o.group(4)) for o in (_OPINION_RE.match(ln) for ln in per.get(walker, [])) if o}
            if not opinions0:
                raise ExpectationFailed("walker's first read of the mockery left no opinion off the walls: ledger %s" % per.get(walker))
            renewed = {k: (opinions0[k], now[k]) for k in opinions0 if k in now and now[k] <= opinions0[k]}
            new = sorted(set(now) - set(opinions0))
            if renewed or new:
                raise ExpectationFailed("walker's opinions changed after the first read: renewed (age then, now) %s, new %s" % (renewed, new))
            t._current.detail = "opinions (age at first read -> now, None = expired): %s" % {k: (opinions0[k], now.get(k)) for k in opinions0}

    with t.component("in_sight_viewer_gains_thought"):
        if t._guard():
            if not at(yard, m1):
                raise ExpectationFailed("the yard viewer, 6 cells from the mockery in the open, never read it: its reads %s"
                                        % [r for r in reads if r[1] == yard])
            if yard not in held:
                raise ExpectationFailed("the yard viewer read the mockery but holds no thought off the walls")

    with t.component("same_room_viewer_gains_thought"):
        if t._guard():
            if not at(roomed, m3):
                raise ExpectationFailed("the viewer shut in the room never read the mark in it: its reads %s" % [r for r in reads if r[1] == roomed])
            if roomed not in held:
                raise ExpectationFailed("the roomed viewer read its mark but holds no thought off the walls")

    with t.component("control_second_mark_own_first_read"):
        if t._guard():
            r2 = at(walker, m2)
            if not r2 or r2[0][2] != "reads":
                raise ExpectationFailed("the second mark on the route gave the walker no first read of its own: %s (a cap hiding reads?)" % r2)

    with t.component("control_walled_viewer_no_thought"):
        if t._guard():
            mine = [r for r in reads if r[1] == walled]
            if mine or walled in held:
                raise ExpectationFailed("the viewer behind the route wall read %s (held a thought off the walls at some poll: %s): a thought "
                                        "without sight" % (mine, walled in held))


@suite.chain("scene_temperament")
def scene_temperament(t):
    """sc_temperament (temperament, inv_temperament): four viewers before a good and a bad mark. The psychopath feels nothing; the sensitive
    (Nerves -2, volatile: GraffitiTemperament rows bad/good/craft 1.5) takes both larger; the clean freak (Neurotic 2: neat 2) gets the Mess
    debuff and, its mood lowered past the minor threshold, the compulsive cleaning break scrubs a mark. Control: the ordinary viewer's
    offsets equal the def values. Restore: the runner destroys the quicktest map. "Sensitive" and "clean freak" are the personality pass's
    vanilla anchors (design/RimMandrake/graffiti_personality_pass_2026-11-07.md:13)."""
    x, z = t.anchor
    cast = {"GrfPlain": "Industriousness:1", "GrfPsycho": "Psychopath", "GrfSens": "Nerves:-2", "GrfNeat": "Neurotic:2"}
    want = {"GrfPlain": {"numb": "False", "fine": "1", "ugly": "1", "neat": "0"}, "GrfPsycho": {"numb": "True"},
            "GrfSens": {"numb": "False", "fine": "1.5", "ugly": "1.5"}, "GrfNeat": {"numb": "False", "neat": "2"}}
    spots = {"GrfPlain": (x - 1, z - 3), "GrfPsycho": (x + 1, z - 3), "GrfSens": (x, z - 2), "GrfNeat": (x, z - 4)}
    good, bad = (x - 4, z), (x + 4, z)
    marks, thoughts = {}, {}
    with t.component("site_ready_temperament"):
        _site_start(t)
        _prep_site(t, 40)
        _wall_run(t, x - 8, z + 1, 17)
        t.bridge_call("jawa/map_commit")
        t.bridge_call("jawa/paint_area", area="home", ops="%d,%d,17,8" % (x - 8, z - 6), value=True)   # the cleaning break's reach
        for nick, traits in sorted(cast.items()):
            got, tr = _cast(t, "Recruit", "%s/%s/" % (nick, traits))
            if t._guard() and tr != [traits.replace(":0", "")]:
                raise ExpectationFailed("%s cast as %s, the game reads its traits %s" % (nick, traits, tr))
            tm = _temper(t, nick)
            off = {k: (v, tm.get(k)) for k, v in want[nick].items() if tm.get(k) != v}
            if t._guard() and off:
                raise ExpectationFailed("%s's temperament (want, read): %s -- Temper %s" % (nick, off, tm))
            _settle_painter(t, nick)
            _hold_at(t, nick, *spots[nick])
        for nick, art in (("GrfFine", 20), ("GrfClumsy", 1)):
            _cast(t, "Recruit", "%s//%d" % (nick, art))
            _settle_painter(t, nick)
        _no_cleaning(t)
        # the good mark is a stencil: a Scrawl (Vandal) is capped at poor craft (CraftCeiling, RM_GraffitiKernel.cs:999), so it never comes out good
        for key, painter, defn, cell in (("good", "GrfFine", ART_DEF, good), ("bad", "GrfClumsy", VANDAL_DEF, bad)):
            mid, m = _order_mark(t, painter, defn, "", *cell)
            if t._guard():
                craft, line = _craft_at(t, *cell)
                marks[key] = (mid, craft, line)
        for painter in ("GrfFine", "GrfClumsy"):
            t.bridge_call("jawa/set_draft", pawnId=painter, drafted=True)
            t.bridge_call("jawa/order_pawn", pawnId=painter, x=x + 20, z=z - 12, waitTicks=0)
        if t._guard():
            gc, bc = marks["good"][1], marks["bad"][1]
            if gc < 3 or bc > 1:          # CraftStage (RM_GraffitiKernel.cs:1059): good+ is fine art, poor or worse is ugly
                raise ExpectationFailed("SITE: the crafts came out good=%s bad=%s (want good or better, poor or worse); re-stage: %s"
                                        % (CRAFTS[gc], CRAFTS[bc], [marks[k][2] for k in marks]))
            t._current.detail = "good %s, bad %s" % (CRAFTS[gc], CRAFTS[bc])

    with t.component("viewers_pass_both_marks"):
        t.wait_ticks(2500)
        for nick in cast:
            thoughts[nick] = {x["def"]: x for x in _graffiti_thoughts(t, nick)} if t._guard() else {}
        if t._guard():
            t._current.detail = "; ".join("%s %s" % (n, {d: round(float(v.get("moodOffset") or 0), 2) for d, v in th.items()})
                                          for n, th in sorted(thoughts.items()))

    def want_offset(defn, stage, factor):
        st = THOUGHT_STAGES.get(defn) or []
        if not st:
            raise ExpectationFailed("no stages for %s in Defs/ThoughtDefs*.xml" % defn)
        return st[max(0, min(int(stage or 0), len(st) - 1))] * factor

    def offsets(nick, factor, defs=("RM_Graffiti_FineArt", "RM_Graffiti_UglyMark")):
        rows = []
        for d in defs:
            th = thoughts[nick].get(d)
            if th is None:
                raise ExpectationFailed("%s holds no %s; its thoughts %s" % (nick, d, sorted(thoughts[nick])))
            got, exp = float(th.get("moodOffset") or 0), want_offset(d, th.get("stage"), factor)
            rows.append((d, got, exp))
        bad_rows = [r for r in rows if abs(r[1] - r[2]) > 0.05]
        if bad_rows:
            raise ExpectationFailed("%s offsets (def, read, expected) off by more than 0.05: %s" % (nick, bad_rows))
        return rows

    with t.component("control_ordinary_offsets_equal_defs"):
        if t._guard():
            t._current.detail = "%s" % offsets("GrfPlain", 1.0)

    with t.component("psychopath_feels_nothing"):
        if t._guard() and thoughts["GrfPsycho"]:
            raise ExpectationFailed("the psychopath holds %s off the walls" % sorted(thoughts["GrfPsycho"]))

    with t.component("sensitive_larger_both_ways"):
        if t._guard():
            t._current.detail = "%s" % offsets("GrfSens", 1.5)

    with t.component("clean_freak_extra_debuff"):
        if t._guard():
            mess = thoughts["GrfNeat"].get("RM_Graffiti_Mess")
            if mess is None or int(mess.get("stage") or 0) != 1:
                raise ExpectationFailed("the clean freak (neat 2) holds no Mess at stage 1 (filth all over the walls): %s" % thoughts["GrfNeat"])
            if float(mess.get("moodOffset") or 0) >= 0:
                raise ExpectationFailed("the clean freak's Mess is not a debuff: %r" % mess)
            t._current.detail = "Mess %+.1f; Ugly %s" % (float(mess["moodOffset"]), thoughts["GrfNeat"].get("RM_Graffiti_UglyMark"))

    with t.component("clean_freak_cleaning_break"):
        if t._guard():
            th = t.bridge_call("jawa/pawn_break_thresholds", pawn="GrfNeat") or {}
            if not th.get("success"):
                raise ExpectationFailed("jawa/pawn_break_thresholds unreadable: %r" % th)
            t.bridge_call("jawa/pawn_need", pawn="GrfNeat", action="need", need="Mood", level=max(0.0, float(th["thresholdMinor"]) - 0.05))
            th = t.bridge_call("jawa/pawn_break_thresholds", pawn="GrfNeat") or {}
            if float(th.get("marginToMinor", 1)) >= 0:
                raise ExpectationFailed("the clean freak's mood did not fall past its minor threshold: %r" % th)
            t.bridge_call("jawa/set_draft", pawnId="GrfNeat", drafted=False)
            before = _all_marks(t, _whole_map(t))
            r = t.bridge_call("jawa/pawn_force_mental_break", pawn="GrfNeat", breakDef=CLEAN_BREAK)
            if not ((r or {}).get("started") and (r or {}).get("mentalStateAfter") == CLEAN_STATE):
                raise ExpectationFailed("the cleaning break did not start %s: %r" % (CLEAN_STATE, r))
            waited, gone = 0, []
            while waited < 6000 and not gone and t._guard():
                t.wait_ticks(500)
                waited += 500
                gone = sorted(set(before) - set(_all_marks(t, _whole_map(t))))
            if not gone:
                raise ExpectationFailed("the clean freak in %s scrubbed no mark in %d ticks" % (CLEAN_STATE, waited))
            t._current.detail = "mood margin %.2f; scrubbed %s in %d ticks" % (float(th["marginToMinor"]), gone, waited)

    with t.component("cleaning_break_open_only_to_clean_freaks"):
        if t._guard():
            raise ExpectationFailed("MISSING TOOL: no probe reads MentalBreakWorker_GraffitiCleaning.BreakCanOccur for a pawn "
                                    "(jawa/pawn_force_mental_break calls TryDoMentalBreak, which skips it), so 'only neat 2 can break this way' "
                                    "is unread; filed as %s" % BREAK_GATE_ITEM)


# ------------------------------------- settings, breach bias, ideoligion reload (scenes.json sc_settings, sc_breach_bias_raid; H1_IDEO_RELOAD)

GLYPH_DEF = "RM_Graffiti_WarningGlyph"           # breachLure true (Defs/ThingDefs_Graffiti.xml:160,184): BreachBiasHook's lure
BREACH_STRATEGY = "ImmediateAttackBreaching"     # vanilla RaidStrategyDef (named as a def by RUT_EmpireRungs.xml:93)
BREACH_PICK_ITEM = "RIMMANDRAKE_PROBE_GRAFFITI_BREACH_PICK_HOOK_NEVER_READ_LIVE"
IDEO_REMOVE_ITEM = "RIMMANDRAKE_PROBE_GRAFFITI_IDEO_REMOVAL_NO_TOOL_DELETES_ONE"
VARIANT_ITEM = "RIMMANDRAKE_PROBE_GRAFFITI_MARK_VARIANT_SAVED_BUT_UNREAD"
RELOAD_SAVE = "RM_GraffitiSceneReload"           # a disposable save (never a canonical world save)
_MARK_LINE = re.compile(r"^\((-?\d+), 0, (-?\d+)\) (\S+) craft (\S+) beauty \S+ by (.+?) about (.+?)(?: DEFACED| WEATHER\d+| FIT[\d.]+"
                        r"| LASTWORD)* side (-?\d+) room ")


def _mark_rows(t):
    """{(x, z): {def, craft, by, about, side}} for every mark standing, off RM_GraffitiSocialProof.Marks (RM_GraffitiSocialProof.cs:177)."""
    text, _ = _static(t, SOCIAL_PROOF, "Marks")
    out = {}
    for ln in text.splitlines():
        m = _MARK_LINE.match(ln)
        if m:
            out[(int(m.group(1)), int(m.group(2)))] = dict(zip(("def", "craft", "by", "about", "side"), m.groups()[2:]))
        elif ln.strip() and t._guard():
            raise ExpectationFailed("RM_GraffitiSocialProof.Marks line this scene cannot parse: %r" % ln)
    return out


def _classic(t, arg=""):
    """RM_GraffitiSocialProof.Classic (RM_GraffitiSocialProof.cs:238): 'on' is the save's no-ideoligion flag, as GraffitiJobUtility.IdeoOf
    reads it. -> True/False as the game reads it after the call."""
    text, _ = _static(t, SOCIAL_PROOF, "Classic", arg)
    if t._guard() and text not in ("CLASSIC True", "CLASSIC False"):
        raise ExpectationFailed("RM_GraffitiSocialProof.Classic(%r) answered %r" % (arg, text))
    return text == "CLASSIC True"


def _reload(t, name=RELOAD_SAVE):
    """Save the running game under `name` and load it back (rimworld/save_game, rimworld/load_game_ready: Scarlands/validation.py:1056).
    A map that does not come back fails the component."""
    import time
    if not t._guard():
        return
    t.bridge_call("rimworld/save_game", saveName=name)
    time.sleep(3.0)
    t.bridge_call("rimworld/load_game_ready", saveName=name)
    for _ in range(40):
        mi = t.bridge_call("jawa/map_info")
        if isinstance(mi, dict) and mi.get("success") is not False and mi.get("size"):
            return
        time.sleep(1.0)
    raise ExpectationFailed("save %r did not load back to a map within 40 s" % name)


def _graffiti_errors(t):
    """Error lines naming this mod's marks or a dead reference, drained from the game log (jawa/drain_log errorsOnly)."""
    r = t.bridge_call("jawa/drain_log", limit=500, errorsOnly=True) or {}
    if t._guard() and r.get("success") is False:
        raise ExpectationFailed("jawa/drain_log unreadable: %r" % r)
    msgs = [str(m.get("text", "")) for m in r.get("messages") or []]
    return [m for m in msgs if "rmMark" in m or "Graffiti" in m or "Filth_Mark" in m or "Could not resolve reference" in m]


def _breach_pick(t, why):
    """The building BreachingGrid.FindBuildingToBreach returns now (BreachBiasHook.cs:31 postfixes it), and a breaching lord's current
    target. -> (x, z, line). No probe reads either: until BREACH_PICK_ITEM lands this is the scene's MISSING TOOL."""
    if not t._guard():
        return None, None, ""
    raise ExpectationFailed("MISSING TOOL: no probe reads BreachingGrid.FindBuildingToBreach or a breaching lord's current target (no "
                            "Graffiti probe, no jawa/lord_* reader), so %s is unread; filed as %s" % (why, BREACH_PICK_ITEM))


@suite.chain("scene_breach_bias_raid")
def scene_breach_bias_raid(t):
    """sc_breach_bias_raid (stands_alone_settings; inv_breach_bias through coverage_rest): a colonist-painted RM_Graffiti_WarningGlyph on
    wall W, not vanilla's breach pick, draws FindBuildingToBreach and a breaching raid's first target to W while breachBiasEnabled is on;
    off, the pick is vanilla's. Control: W with the glyph removed, bias on, picks vanilla's building. Restore: the runner destroys the
    quicktest map. Every pick read waits on BREACH_PICK_ITEM's probe (_breach_pick)."""
    x, z = t.anchor
    wall = (x + 6, z)                                 # W: the east wall's middle; the glyph stands on the floor cell outside it
    glyph = {}
    with t.component("site_ready_breach_bias_raid"):
        _site_start(t)
        r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="breachBiasEnabled")
        if t._guard() and str((r or {}).get("value")).lower() != "true":
            raise ExpectationFailed("breachBiasEnabled reads %r, not its shipped true (RM_GraffitiMod.cs:44)" % ((r or {}).get("value"),))
        _prep_site(t, 40)
        _walls(t, _box(x - 6, z - 4, x + 6, z + 4), door=(x, z + 4))
        t.bridge_call("jawa/map_commit")
        _cast(t, "Recruit", "GrfLure//10")
        _settle_painter(t, "GrfLure")
        _no_cleaning(t)
        mid, m = _order_mark(t, "GrfLure", GLYPH_DEF, "", wall[0] + 1, wall[1])
        if t._guard():
            glyph.update(id=mid, x=m["x"], z=m["z"])
            t._current.detail = "glyph %s at (%d,%d) beside W %s" % (mid, m["x"], m["z"], wall)
        _hold_at(t, "GrfLure", x, z)                  # inside the box, off the lure

    with t.component("glyph_wall_is_not_vanilla_pick"):
        t.set_setting(SETTINGS, {"breachBiasEnabled": False})
        vx, vz, line = _breach_pick(t, "vanilla's pick with bias off")
        t.set_setting(SETTINGS, {"breachBiasEnabled": True})
        if t._guard() and (vx, vz) == wall:
            raise ExpectationFailed("SITE: vanilla already picks W %s, so the lure proves nothing; re-stage W: %s" % (wall, line))

    with t.component("bias_on_pick_is_glyph_wall", toggle="breachBiasEnabled"):
        px, pz, line = _breach_pick(t, "the pick with bias on")
        if t._guard() and (px, pz) != wall:
            raise ExpectationFailed("bias on, FindBuildingToBreach picks (%d,%d), not W %s: %s" % (px, pz, wall, line))

    with t.component("breaching_raid_first_target_is_glyph_wall", toggle="breachBiasEnabled"):
        r = t.bridge_call("jawa/fire_raid", strategy=BREACH_STRATEGY, dryRun=False)
        if t._guard() and not (r or {}).get("success"):
            raise ExpectationFailed("jawa/fire_raid(strategy=%s) did not fire: %r" % (BREACH_STRATEGY, r))
        t.wait_ticks(600)                             # the lord's breach toil sets its first target
        px, pz, line = _breach_pick(t, "the breaching lord's first target")
        if t._guard() and (px, pz) != wall:
            raise ExpectationFailed("the breaching raid's first target is (%d,%d), not W %s: %s" % (px, pz, wall, line))

    with t.component("bias_off_pick_is_vanilla", toggle="breachBiasEnabled"):
        t.set_setting(SETTINGS, {"breachBiasEnabled": False})
        px, pz, line = _breach_pick(t, "the pick with bias off")
        t.set_setting(SETTINGS, {"breachBiasEnabled": True})
        if t._guard() and (px, pz) == wall:
            raise ExpectationFailed("bias off, the pick is still W %s: the switch does not stop its own behaviour: %s" % (wall, line))

    with t.component("control_no_glyph_pick_is_vanilla"):
        t.bridge_call("jawa/destroy_batch", rects="%d,%d,1,1" % (glyph.get("x", wall[0] + 1), glyph.get("z", wall[1])), categories="All")
        if t._guard() and _all_marks(t, "%d,%d,1,1" % (wall[0] + 1, wall[1])):
            raise ExpectationFailed("the glyph beside W still stands after destroy_batch")
        px, pz, line = _breach_pick(t, "the pick with the glyph gone, bias on")
        if t._guard() and (px, pz) == wall:
            raise ExpectationFailed("with no glyph W %s is still picked: W was chosen for a reason other than the lure: %s" % (wall, line))


def _spree_marks(t):
    """paintingEnabled's behaviour: RM_GraffitiProof's A1 spree (SpreeStart, 3000 ticks, SpreeRead: RM_GraffitiProof.cs:145,156)."""
    started, _ = _static(t, PROOF, "SpreeStart")
    pid = _probe_fields(started).get("pawn")
    with _own_spree([pid]):
        t.wait_ticks(3000)
    text, _ = _static(t, PROOF, "SpreeRead")
    return int(_probe_fields(text).get("marks") or 0), "%s; %s" % (started, text)


def _viewer_thought(t):
    """viewerReactionEnabled's behaviour: RM_GraffitiProof.HostileThought (RM_GraffitiProof.cs:294), its worker active 1 or 0."""
    text, _ = _static(t, PROOF, "HostileThought")
    return int(_probe_fields(text).get("worker") == "True"), text


def _exit_tags(t):
    """raidExitTaggingEnabled's behaviour: one A2 raid exit (RM_GraffitiProof.cs:172,219), its raiders' marks."""
    started, _ = _static(t, PROOF, "RaidStart")
    text, _ = _static(t, PROOF, "RaidExit")
    return int(_probe_fields(text).get("after") or 0), "%s; %s" % (started, text)


def _protected(t):
    """autoCleanProtectionEnabled's behaviour: CleanSetup, the 600-tick wait, CleanRead (RM_GraffitiProof.cs:319,340): 1 when the
    colony's own mark is NOT offered to unforced cleaning (RM_GraffitiKernel.ProtectsFromAutoClean)."""
    _static(t, PROOF, "CleanSetup")
    t.wait_ticks(600)
    text, _ = _static(t, PROOF, "CleanRead")
    return int(_probe_fields(text).get("unforcedOwn") == "False"), text


def _claim_after_raid(t):
    """socialEnabled's behaviour: a raid exit's tags give the colony RM_Graffiti_EnemyClaim (GraffitiSocial.cs:198)."""
    n, line = _exit_tags(t)
    stage = _claim_stage(t)
    return int(stage is not None), "EnemyClaim stage %r after %s" % (stage, line)


def _said_after_raid(t):
    """socialMessagesEnabled's behaviour: the 'left their mark' letter a raid exit sends (GraffitiSocial.cs:795), counted by
    RM_GraffitiSocialProof.Said. Waits out RaidMessageDue's 5000-tick spacing (GraffitiSocial.cs:299) first."""
    t.wait_ticks(5100)
    before, _ = _static(t, SOCIAL_PROOF, "Said", "1")
    n, line = _exit_tags(t)
    after, _ = _static(t, SOCIAL_PROOF, "Said", "1")
    count = lambda s: int((s.split() + ["0", "0"])[1]) if s.startswith("SAID ") else 0
    return count(after) - count(before), "messages %d -> %d after %s" % (count(before), count(after), line)


# each switch's own behaviour, as (setting, measure); ordered so the raid letter's spacing is never spent before its own pair
SWITCHES = [("socialMessagesEnabled", _said_after_raid), ("paintingEnabled", _spree_marks), ("viewerReactionEnabled", _viewer_thought),
            ("raidExitTaggingEnabled", _exit_tags), ("autoCleanProtectionEnabled", _protected), ("socialEnabled", _claim_after_raid)]


@suite.chain("scene_settings_each_switch")
def scene_settings_each_switch(t):
    """sc_settings (stands_alone_settings, inv_settings, inv_standalone): marks painted with ideoligions off keep def, craft, wall side and
    subject across a save and reload; then each switch off stops only its own behaviour and, back on (the control), it returns.
    paintIntervalTicks is a number, not a switch: preflight holds it at its shipped value. breachBiasEnabled's behaviour is
    sc_breach_bias_raid's reader (_breach_pick); the raider-pressure switch is PRESSURE_ITEM's. Restore: the runner destroys the quicktest
    map; the classic flag is set back."""
    x, z = t.anchor
    cells = [(x - 4, z - 1), (x + 4, z - 1)]
    before = {}
    with t.component("site_ready_settings"):
        _site_start(t)
        _prep_site(t, 40)
        _wall_run(t, x - 8, z, 17)
        t.bridge_call("jawa/map_commit")
        if not _classic(t, "on") and t._guard():
            raise ExpectationFailed("RM_GraffitiSocialProof.Classic('on') left the no-ideoligion flag off")
        for nick in ("GrfSetA", "GrfSetB"):
            _cast(t, "Recruit", "%s//10" % nick)
            _settle_painter(t, nick)
        _no_cleaning(t)

    with t.component("mark_painted_ideoligions_off"):
        _order_mark(t, "GrfSetA", VANDAL_DEF, "GrfSetB", *cells[0])     # about a colonist: a subject to carry over
        _order_mark(t, "GrfSetB", VANDAL_DEF, "", *cells[1])
        if t._guard():
            rows = _mark_rows(t)
            before.update({c: rows.get(c) for c in cells})
            if not all(before.values()):
                raise ExpectationFailed("ordered marks not all standing: %s" % before)
            if not _classic(t):
                raise ExpectationFailed("the no-ideoligion flag was off while the marks were painted")
            t._current.detail = "%s" % before

    with t.component("marks_equal_after_reload"):
        _reload(t)
        if t._guard():
            rows = _mark_rows(t)
            off = {c: (before[c], rows.get(c)) for c in cells if rows.get(c) != before[c]}
            if off:
                raise ExpectationFailed("mark fields (before, after) changed across the reload: %s" % off)
            t._current.detail = "def, craft, by, about and side equal at %s" % cells

    for field, measure in SWITCHES:
        with t.component("switch_%s_off_stops_it" % field, toggle=field):
            t.set_setting(SETTINGS, {field: False})
            n, line = measure(t)
            if t._guard():
                if n:
                    raise ExpectationFailed("%s off, its behaviour still ran (%d): %s" % (field, n, line))
                t._current.detail = line
        with t.component("control_%s_on_returns_it" % field, toggle=field):
            t.set_setting(SETTINGS, {field: True})
            n, line = measure(t)
            if t._guard():
                if n <= 0:
                    raise ExpectationFailed("%s back on, its behaviour did not return: %s" % (field, line))
                t._current.detail = line

    with t.component("marks_variant_equal_after_reload"):
        if t._guard():
            raise ExpectationFailed("MISSING TOOL: no probe reads Filth_Mark.variant (scribed as rmMarkVariant, Filth_Mark.cs:304; "
                                    "RM_GraffitiSocialProof.Marks leaves it out), so 'variant equal before and after reload' is unread; "
                                    "filed as %s" % VARIANT_ITEM)

    with t.component("switch_breachBiasEnabled_off_stops_it", toggle="breachBiasEnabled"):
        _breach_pick(t, "breach bias's own behaviour (sc_breach_bias_raid)")

    with t.component("switch_raider_pressure_off_stops_it"):
        if t._guard():
            _need_pressure("the raider-pressure switch, its sooner-or-larger mode and push size")


@suite.chain("scene_ideo_removed_save_reload")
def scene_ideo_removed_save_reload(t):
    """H1_IDEO_RELOAD (inv_standalone, stands_alone_settings): a mark records its maker's ideoligion (rmMarkMakerIdeo, Filth_Mark.cs:297);
    after the colony's ideoligion is removed, a save reloads with 0 Graffiti reference errors (held walk defect #1). Control: the mark
    still stands after the reload with its def and maker, so the error count reads a world that holds the mark. Removing an ideoligion
    waits on IDEO_REMOVE_ITEM. Restore: the runner destroys the quicktest map."""
    x, z = t.anchor
    cell = (x, z - 1)
    before = {}
    with t.component("site_ready_ideo_reload"):
        _site_start(t)
        if _classic(t) and t._guard():
            raise ExpectationFailed("the no-ideoligion flag is on: the mark would record no ideoligion to lose")
        _prep_site(t, 40)
        _wall_run(t, x - 8, z, 17)
        t.bridge_call("jawa/map_commit")
        _cast(t, "Recruit", "GrfIdeo//10")
        _settle_painter(t, "GrfIdeo")
        _no_cleaning(t)
        _order_mark(t, "GrfIdeo", VANDAL_DEF, "", *cell)
        if t._guard():
            before.update(_mark_rows(t).get(cell) or {})
            if not before:
                raise ExpectationFailed("RM_GraffitiSocialProof.Marks lists no mark at %s after the order" % (cell,))
            t._current.detail = "%s" % before

    with t.component("colony_ideo_removed"):
        if t._guard():
            raise ExpectationFailed("MISSING TOOL: no bridge tool or probe removes an ideoligion from Find.IdeoManager (jawa/ideo_* create, "
                                    "assign and edit; only start flow calls RemoveUnusedStartingIdeos), so the held walk defect cannot be "
                                    "staged; filed as %s" % IDEO_REMOVE_ITEM)

    errors = []
    with t.component("save_reloads_zero_graffiti_reference_errors"):
        _graffiti_errors(t)                                  # drain what the staging logged: only the reload's lines count
        _reload(t)
        errors = _graffiti_errors(t) if t._guard() else []
        if errors:
            raise ExpectationFailed("%d Graffiti reference error(s) on reload: %s" % (len(errors), errors[:5]))

    with t.component("control_mark_survives_reload"):
        if t._guard():
            after = _mark_rows(t).get(cell)
            if not after or after["def"] != before.get("def") or after["by"] != before.get("by"):
                raise ExpectationFailed("the mark at %s (before %s) reads %s after the reload" % (cell, before, after))
            t._current.detail = "%s" % after


# ------------------------------------------------- the social layer (scenes.json: sc_mockery, sc_answer_wall, sc_tribute_memorial, sc_fights,
# sc_visitors). Same hands as above (RM_GraffitiSocialProof.cs): Feud (:20), Befriend (:31), Lovers (:109), Kill (:168), Fight (:139, which also
# reads a's opinion of b), PlayLog (:119), Ledger (:269, whose "grudge <pawn> <answer> against <painter>" lines are each open answer and whose
# trace carries every read, answer, confrontation and visitor charge, GraffitiSocial.cs:452/:466/:930/:1013/:644).

TRIBUTE_DEF = "RM_Graffiti_Tribute"                  # ThingDefs_GraffitiSocial.xml:37, meaning Tribute
MEMORIAL_DEF = "RM_Graffiti_Memorial"                # ThingDefs_GraffitiSocial.xml:68, meaning Memorial
INSULT_DEF = "RM_Graffiti_FactionInsult"             # ThingDefs_GraffitiSocial.xml:99, meaning Insult
SPREE_BREAK = "RM_GraffitiPaintingSpreeBreak"        # the break mental_break_spree forces
CONFRONT_JOB = "RM_ConfrontPainter"                  # JobGiver_AnswerMark's confrontation (JobDrivers_AnswerMark.cs:51)
ENEMY_OPINION, FRIEND_OPINION, HATED_OPINION = -15, 20, -30   # RM_GraffitiKernel.cs:777
INSULT_GOODWILL, VISIT_LOSS_CAP = -12, 12            # RM_GraffitiKernel.GoodwillOf (:1263) and VisitLossCap (:1238)
PLAIN = "Industriousness:1"                          # a trait with no temperament row of its own that bears on answers (TemperamentDefs_Graffiti.xml)
HOT = "Brawler,Abrasive"                             # temper 1.5 x 1.5 (TemperamentDefs_Graffiti.xml:29-30); IsHot is temper x vanilla >= 1.5 (:922)
_TRACE_READ = re.compile(r"^\d+ (\S+) reads (\w+)@\((-?\d+), 0, (-?\d+)\) by (\S+) about (\S+) -> (\w+)")
_GRUDGE = re.compile(r"^grudge (\S+) (\w+) against ?(\S*)\s*$", re.M)


def _story(t, acc):
    """RM_GraffitiSocialProof.Ledger("trace"), appended to `acc` (the ring empties on each read). -> (new trace lines, {nick: ledger mood and
    opinion lines}, {nick: (answer, against)} of the grudges open now)."""
    text, _ = _static(t, SOCIAL_PROOF, "Ledger", "trace")
    new = [ln[4:].strip() for ln in text.splitlines() if ln.startswith("  . ")]
    acc.extend(new)
    per, cur = {}, None
    for ln in text.splitlines():
        if ln and not ln.startswith(" ") and " [" in ln:
            cur = ln.split(" ", 1)[0]
            per[cur] = []
        elif cur and (ln.startswith("  mood ") or ln.startswith("  opinion of ")):
            per[cur].append(ln)
        elif not ln.startswith("  "):
            cur = None
    return new, per, {m.group(1): (m.group(2), m.group(3)) for m in _GRUDGE.finditer(text)}


def _reads(acc, nick, cell=None):
    """[(def, (x, z), maker, about, reaction)] of `nick`'s first reads in the trace, at `cell` if given."""
    out = []
    for ln in acc:
        m = _TRACE_READ.match(ln)
        if m and m.group(1) == nick and (cell is None or (int(m.group(3)), int(m.group(4))) == tuple(cell)):
            out.append((m.group(2), (int(m.group(3)), int(m.group(4))), m.group(5), m.group(6), m.group(7)))
    return out


def _fed(t, *nicks):
    for nick in nicks:
        t.bridge_call("jawa/pawn_need", pawn=nick, action="need", need="Food", level=1.0)
        t.bridge_call("jawa/pawn_need", pawn=nick, action="need", need="Rest", level=1.0)


def _recruit(t, nick, traits=PLAIN, art=""):
    """A new colonist cast for the scene (RM_GraffitiSocialProof.Recruit), fed and rested; the traits are read back, never assumed."""
    got, have = _cast(t, "Recruit", "%s/%s/%s" % (nick, traits, art))
    want = [x for x in traits.split(",") if x]
    if t._guard() and sorted(have) != sorted(want):
        raise ExpectationFailed("SITE: %s cast with %s holds %s" % (nick, want, have))
    _fed(t, nick)
    return got


def _opinion(t, a, b):
    """a's opinion of b, as RM_GraffitiSocialProof.Fight reads it ('(opinion N)')."""
    text, _ = _static(t, SOCIAL_PROOF, "Fight", "%s/%s" % (a, b))
    m = re.search(r"\(opinion (-?\d+)\)", text)
    if t._guard() and not m:
        raise ExpectationFailed("RM_GraffitiSocialProof.Fight(%s/%s) gave no opinion: %r" % (a, b, text))
    return int(m.group(1)) if m else 0


def _hot(t, nick):
    hot = _temper(t, nick).get("hot")
    if t._guard() and hot != "True":
        raise ExpectationFailed("SITE: %s cast %s reads hot %r (GraffitiTemperament.IsHot): the confront band is closed to it" % (nick, HOT, hot))


def _mark_line(t, cell):
    text, _ = _static(t, SOCIAL_PROOF, "Marks")
    return next((ln for ln in text.splitlines() if ln.startswith("(%d, 0, %d) " % tuple(cell))), None)


def _stage_pick(t, acc, want, painter, traits, art, cells, tag, friend=None, budget=3000):
    """sc_answer_wall's staging: 'one answer is the pawn's pick (asserted: the answer chosen)'. A fresh subject per try, held drafted (a drafted
    pawn reads but never answers, JobDrivers_AnswerMark.cs:20) 3 cells off its own cell, mocked there by `painter`; its grudge is read off the
    ledger. The first subject whose pick is `want` is returned still drafted; every other one is vanished so it never acts.
    -> (nick, mark id, mark, [(nick, pick)] of the tries)."""
    tries = []
    for i, (cx, cz) in enumerate(cells):
        if not t._guard():
            break
        nick = "%s%d" % (tag, i)
        _recruit(t, nick, traits, art)
        _static(t, SOCIAL_PROOF, "Feud", "%s/%s" % (painter, nick))
        if friend:
            _static(t, SOCIAL_PROOF, "Befriend", "%s/%s" % (friend, nick))
        _hold_at(t, nick, cx, cz - 3, ticks=300)
        mid, m = _order_mark(t, painter, MOCKERY_DEF, nick, cx, cz)
        pick, waited = None, 0
        while waited < budget and t._guard():
            t.wait_ticks(250)
            waited += 250
            _, _, gr = _story(t, acc)
            if nick in gr or _reads(acc, nick, (cx, cz)):
                pick = gr.get(nick)
                break
        tries.append((nick, pick[0] if pick else None))
        if pick and pick[0] == want and pick[1] == painter:
            return nick, mid, m, tries
        t.bridge_call("jawa/pawn_force_incapacitate", pawn=nick, action="vanish")
    if t._guard():
        raise ExpectationFailed("SITE: no subject picked %s against %s in %d tries (nick, pick): %s" % (want, painter, len(tries), tries))
    return None, None, None, tries


@suite.chain("scene_mockery")
def scene_mockery(t):
    """sc_mockery (mockery): a feuding colonist paints a mockery of the other; its subject is hurt (Humiliated) and thinks less of the painter
    (PaintedMe), a rival of the subject enjoys it, the mark's subject is the target, and a neutral viewer holds no amused thought. Control: a
    plain tag by the same painter, read by the same subject first, moves no opinion off the walls. Restore: the runner destroys the quicktest map.
    The scene's 'amused' for a mockery is the kernel's Gleeful (RM_Graffiti_EnjoyedIt): ReactionOf gives a mockery's reader with opinion of the
    subject <= -15 Gleeful (RM_GraffitiKernel.cs:801); RM_Graffiti_Amused is a Jest's. The rest 'walk past' as viewers held in sight."""
    x, z = t.anchor
    painter, subject, rival, neutral, friend = "GrfMock", "GrfMocked", "GrfRival", "GrfPasser", "GrfPal"
    tag_at, mock_at = (x - 3, z), (x + 3, z)          # floor cells on the south face of the wall row z + 1
    acc, per = [], {}
    with t.component("site_ready_mockery"):
        _site_start(t)
        _prep_site(t, 40)
        _wall_run(t, x - 8, z + 1, 17)
        t.bridge_call("jawa/map_commit")
        _recruit(t, painter, PLAIN, 10)
        for nick in (subject, rival, neutral, friend):
            _recruit(t, nick)
        _no_cleaning(t)
        feud, _ = _static(t, SOCIAL_PROOF, "Feud", "%s/%s" % (painter, subject))
        _static(t, SOCIAL_PROOF, "Feud", "%s/%s" % (rival, subject))
        _static(t, SOCIAL_PROOF, "Befriend", "%s/%s" % (friend, subject))
        for nick, dx in ((subject, 0), (rival, 2), (neutral, -2), (friend, 4)):
            _hold_at(t, nick, x + dx, z - 3, ticks=300)
        if t._guard():
            ops = {n: _opinion(t, n, subject) for n in (painter, rival, neutral, friend)}
            if not (ops[painter] <= ENEMY_OPINION and ops[rival] <= ENEMY_OPINION and ENEMY_OPINION < ops[neutral] < FRIEND_OPINION
                    and ops[friend] >= FRIEND_OPINION):
                raise ExpectationFailed("SITE: opinions of %s %s (painter and rival <= %d, neutral between, friend >= %d)"
                                        % (subject, ops, ENEMY_OPINION, FRIEND_OPINION))
            t._current.detail = "%s; opinions of %s %s" % (feud, subject, ops)

    with t.component("control_plain_tag_no_opinion_change"):
        if t._guard():
            _story(t, acc)
            before = _opinion(t, subject, painter)
            _order_mark(t, painter, VANDAL_DEF, "", *tag_at)
            for _ in range(6):
                t.wait_ticks(250)
                _, per, _ = _story(t, acc)
            seen = _reads(acc, subject, tag_at)
            if not seen:
                raise ExpectationFailed("SITE: %s never read the plain tag at %s in 1500 ticks: the control rules nothing out" % (subject, tag_at))
            ours = [ln for ln in per.get(subject, []) if ln.startswith("  opinion of %s " % painter)]
            if ours:
                raise ExpectationFailed("a plain tag moved %s's opinion of its painter off the walls: %s (read %s)" % (subject, ours, seen))
            t._current.detail = "read %s; game opinion %d -> %d (not judged: chitchat moves it)" % (seen[0], before, _opinion(t, subject, painter))

    with t.component("mockery_names_its_subject"):
        if t._guard():
            _order_mark(t, painter, MOCKERY_DEF, subject, *mock_at)
            line = _mark_line(t, mock_at)
            if not line or not line.split(" ", 3)[3].startswith("Mockery ") or (" by %s about %s " % (painter, subject)) not in line:
                raise ExpectationFailed("the ordered mockery at %s reads %r (want Mockery by %s about %s)" % (mock_at, line, painter, subject))
            for _ in range(8):
                t.wait_ticks(250)
                _, per, _ = _story(t, acc)
            t._current.detail = line

    def reaction(nick):
        r = _reads(acc, nick, mock_at)
        return r[0][4] if r else None

    with t.component("subject_hurt_and_thinks_less_of_painter"):
        if t._guard():
            th = [x for x in _graffiti_thoughts(t, subject) if x.get("def") == "RM_Graffiti_Humiliated"]
            low = [ln for ln in per.get(subject, []) if ln.startswith("  opinion of %s -" % painter)]
            if reaction(subject) != "Humiliated" or not th or not low:
                raise ExpectationFailed("%s read the mockery as %r; Humiliated %s; opinion lines %s" % (subject, reaction(subject), th, per.get(subject)))
            t._current.detail = "Humiliated %+.1f; %s" % (float(th[0].get("moodOffset") or 0), low[0].strip())

    with t.component("rival_of_subject_enjoys_it"):
        if t._guard():
            th = [x for x in _graffiti_thoughts(t, rival) if x.get("def") == "RM_Graffiti_EnjoyedIt"]
            if reaction(rival) != "Gleeful" or not th:
                raise ExpectationFailed("%s (hates %s) read the mockery as %r; EnjoyedIt %s" % (rival, subject, reaction(rival), th))
            t._current.detail = "Gleeful, EnjoyedIt %+.1f" % float(th[0].get("moodOffset") or 0)

    with t.component("control_neutral_viewer_not_amused"):
        if t._guard():
            r = reaction(neutral)
            fun = [x for x in _graffiti_thoughts(t, neutral) if x.get("def") in ("RM_Graffiti_EnjoyedIt", "RM_Graffiti_Amused", "RM_Graffiti_EnjoyedInsult")]
            if r is None:
                raise ExpectationFailed("SITE: the neutral viewer never read the mockery: its reads %s" % _reads(acc, neutral))
            if r in ("Gleeful", "Amused") or fun:
                raise ExpectationFailed("the neutral viewer read the mockery as %s and holds %s" % (r, fun))
            t._current.detail = "neutral read it as %s" % r


@suite.chain("scene_answer_wall")
def scene_answer_wall(t):
    """sc_answer_wall (answer_wall): four standing mockeries, each with its subject, a friend of the subject and the painter, each staged so its
    subject's pick is one answer (_stage_pick: a Neurotic subject leans Scrub, RM_GraffitiKernel.cs:845 and TemperamentDefs_Graffiti.xml:42; a
    Tortured Artist leans Reply (:46); a hot head is the only one the confront band opens to); each answer job then completes: the scrub
    leaves the mark gone, the deface leaves it crossed out, the reply leaves the subject's mark beside it, the confront ends in a confrontation
    subject against painter. The painted-out case: the painter's spree goes over a hot colonist's tags (unordered, so Notify_WentOver gives a
    grudge, GraffitiSocial.cs:860) and that ends in a confrontation too. Control: a plain tag nobody minds gets no answer job and stands.
    Restore: the runner destroys the quicktest map."""
    x, z = t.anchor
    painter, friend, tagger = "GrfAnsP", "GrfAnsPal", "GrfAnsTag"
    rows = {"Scrub": z - 19, "Deface": z - 9, "Reply": z + 1, "Confront": z + 11}
    cast = {"Scrub": ("Neurotic:1", 0, 2), "Deface": (PLAIN, 0, 20), "Reply": ("TorturedArtist", 12, 4), "Confront": (HOT, 0, 6)}
    acc, picked = [], {}
    with t.component("site_ready_answer_wall"):
        _site_start(t)
        _prep_site(t, 60)
        for wz in rows.values():
            _wall_run(t, x - 25, wz, 51)
        t.bridge_call("jawa/map_commit")
        _recruit(t, painter, PLAIN, 10)
        _recruit(t, friend)
        _recruit(t, tagger, PLAIN, 8)
        _no_cleaning(t)
        _hold_at(t, friend, x, z - 4, ticks=300)

    for want in ("Scrub", "Deface", "Reply", "Confront"):
        with t.component("pick_%s_staged" % want.lower()):
            if t._guard():
                traits, art, n = cast[want]
                wz = rows[want]
                cells = [(x - 24 + 2 * i, wz - 1) for i in range(n)]
                nick, mid, m, tries = _stage_pick(t, acc, want, painter, traits, art, cells, "GrfAns%s" % want[:2], friend=friend)
                if want == "Confront":
                    _hot(t, nick)
                picked[want] = (nick, mid, m)
                t._current.detail = "tries (nick, pick): %s" % tries

        with t.component("%s_job_completes" % want.lower()):
            if t._guard() and want in picked:
                nick, mid, m = picked[want]
                cell = (m["x"], m["z"])
                t.bridge_call("jawa/set_draft", pawnId=nick, drafted=False)
                done, waited, line = None, 0, None
                while waited < 9000 and t._guard() and not done:
                    t.wait_ticks(500)
                    waited += 500
                    _fed(t, nick)
                    _story(t, acc)
                    if want == "Scrub":
                        done = mid not in _all_marks(t, "%d,%d,1,1" % cell) and [l for l in acc if (" %s scrubbed away " % nick) in l]
                    elif want == "Deface":
                        line = _mark_line(t, cell)
                        done = line and " DEFACED" in line and [l for l in acc if (" %s crossed out " % nick) in l]
                    elif want == "Reply":
                        mine = [ln for ln in _marks_by(t, nick)]
                        near = [ln for ln in mine if abs(int(re.match(r"\((-?\d+)", ln).group(1)) - cell[0]) <= 6]
                        done = near
                    else:
                        done = [l for l in acc if (" %s confronts %s:" % (nick, painter)) in l]
                if t._guard():
                    why = [l for l in acc if (" %s means to %s against %s" % (nick, want, painter)) in l]
                    if not done:
                        raise ExpectationFailed("%s picked %s against %s and %d ticks on it is not done (mark %s: %r; its story %s)"
                                                % (nick, want, painter, waited, cell, _mark_line(t, cell), [l for l in acc if nick in l][-6:]))
                    if not why or not _reads(acc, nick, cell):
                        raise ExpectationFailed("%s's %s has no reason in the trace: read %s, meant %s" % (nick, want, _reads(acc, nick, cell), why))
                    t._current.detail = "%s after %d ticks; because %s -> %s" % (done[0] if isinstance(done, list) else done, waited, _reads(acc, nick, cell)[0], why[0])

    with t.component("painted_out_ends_in_confrontation"):
        hit, rounds = None, []
        for k in range(3):
            if not t._guard() or hit:
                break
            owner, wx, wz = "GrfAnsOut%d" % k, x - 20 + 15 * k, z + 25
            _recruit(t, owner, HOT, 3)                       # art 3: under CanReplyInPaint's 5, so a WorkDestroyed grudge is Confront or nothing
            _hot(t, owner)
            _wall_run(t, wx, wz, 4)
            t.bridge_call("jawa/map_commit")
            for cx in range(wx, wx + 4):
                for cz in (wz - 1, wz + 1):
                    _order_mark(t, owner, VANDAL_DEF, "", cx, cz)
            _hold_at(t, owner, wx + 1, wz - 6, ticks=300)
            _hold_at(t, painter, wx + 1, wz - 2, ticks=300)
            t.bridge_call("jawa/set_draft", pawnId=painter, drafted=False)
            r = t.bridge_call("jawa/pawn_force_mental_break", pawn=painter, breakDef=SPREE_BREAK)
            if t._guard() and not (r or {}).get("started"):
                raise ExpectationFailed("jawa/pawn_force_mental_break %s did not start the spree: %r" % (painter, r))
            grudge = None
            with _own_spree([painter]):
                waited = 0
                while waited < 12000 and t._guard():
                    t.wait_ticks(500)
                    waited += 500
                    _fed(t, owner, painter)
                    _, _, gr = _story(t, acc)
                    grudge = gr.get(owner) or grudge
            rounds.append((owner, grudge))
            if not grudge or grudge[0] != "Confront":
                t.bridge_call("jawa/pawn_force_incapacitate", pawn=owner, action="vanish")
                continue
            t.bridge_call("jawa/set_draft", pawnId=owner, drafted=False)
            waited = 0
            while waited < 20000 and t._guard() and not hit:
                t.wait_ticks(500)
                waited += 500
                _fed(t, owner, painter)
                _story(t, acc)
                hit = next((l for l in acc if (" %s confronts %s:" % (owner, painter)) in l), None)
        if t._guard():
            if not hit:
                raise ExpectationFailed("no painted-out colonist confronted %s: rounds (owner, grudge) %s; went-over lines %s"
                                        % (painter, rounds, [l for l in acc if "painted over" in l or "GrfAnsOut" in l][-8:]))
            t._current.detail = "%s; rounds %s" % (hit, rounds)

    with t.component("control_unoffending_mark_no_answer"):
        if t._guard():
            cell = (x + 20, rows["Reply"] - 1)
            mid, _ = _order_mark(t, tagger, VANDAL_DEF, "", *cell)
            t.wait_ticks(6000)
            _story(t, acc)
            line = _mark_line(t, cell)
            touched = [l for l in acc if ("@(%d, 0, %d)" % cell) in l and (" scrubbed away " in l or " crossed out " in l or " means to " in l)]
            if mid not in _all_marks(t, "%d,%d,1,1" % cell) or (line and " DEFACED" in line) or touched:
                raise ExpectationFailed("a plain tag nobody minds was answered: mark %s now %r; %s" % (mid, line, touched))
            t._current.detail = line


@suite.chain("scene_tribute_memorial")
def scene_tribute_memorial(t):
    """sc_tribute_memorial (tribute_memorial): a colonist whose friend died paints a memorial on its own and its grief eases
    (RM_Graffiti_GriefEased, GraffitiSocial.cs:803); a colonist's partner paints it a tribute, which warms it (Honored) while its rival scoffs
    (HonoredMyEnemy: ReactionOf gives a tribute's reader with opinion of the subject <= -30 Scoffs, RM_GraffitiKernel.cs:801; Jealous is the
    maker's own lover's, and here that lover is the subject). Control: a colonist with no dead friend, painting through the same days, never
    paints a memorial. Restore: the runner destroys the quicktest map. The memorial is the hand's own choice (SocialMark, GraffitiSocial.cs:658);
    a tribute not chosen in the window is ordered, and that is recorded: what is judged of it is how it is read."""
    x, z = t.anchor
    mourner, dead, partner, beloved, rival, plain = "GrfMourn", "GrfGone", "GrfPartner", "GrfLoved", "GrfSpite", "GrfNoGrief"
    acc, per = [], {}
    memorial = tribute = None
    with t.component("site_ready_tribute_memorial"):
        _site_start(t)
        _prep_site(t, 40)
        _wall_run(t, x - 12, z + 1, 25)
        t.bridge_call("jawa/map_commit")
        for nick, art in ((mourner, 8), (dead, ""), (partner, 8), (beloved, ""), (rival, ""), (plain, 8)):
            _recruit(t, nick, PLAIN, art)
        _no_cleaning(t)
        _static(t, SOCIAL_PROOF, "Befriend", "%s/%s" % (mourner, dead))
        lovers, _ = _static(t, SOCIAL_PROOF, "Lovers", "%s/%s" % (partner, beloved))
        _static(t, SOCIAL_PROOF, "Feud", "%s/%s" % (rival, beloved))
        _static(t, SOCIAL_PROOF, "Kill", dead)
        for nick, dx in ((beloved, -2), (rival, 2)):
            _hold_at(t, nick, x + dx, z - 3, ticks=300)
        if t._guard():
            mourns = {n: _temper(t, n).get("mourns") for n in (mourner, plain, partner)}
            spite = _opinion(t, rival, beloved)
            if mourns[mourner] != dead or mourns[plain] != "-" or mourns[partner] != "-" or "lovers=True" not in lovers or spite > HATED_OPINION:
                raise ExpectationFailed("SITE: mourns %s (want %s for %s only); %s; %s of %s %d (want <= %d)"
                                        % (mourns, dead, mourner, lovers, rival, beloved, spite, HATED_OPINION))
            t._current.detail = "mourns %s; %s; rival opinion %d" % (mourns, lovers, spite)

    with t.component("run_until_memorial_and_tribute"):
        waited = 0
        while waited < 60000 and t._guard() and not (memorial and tribute):
            for nick in (mourner, partner, plain):
                t.bridge_call("jawa/pawn_need", pawn=nick, action="need", need="Joy", level=0.2)
            _fed(t, mourner, partner, plain, beloved, rival)
            t.wait_ticks(1000)
            waited += 1000
            _, per, _ = _story(t, acc)
            memorial = memorial or next((l for l in acc if (" %s painted Memorial@" % mourner) in l and ("about %s" % dead) in l), None)
            tribute = tribute or next((l for l in acc if (" %s painted Tribute@" % partner) in l and ("about %s" % beloved) in l), None)
        ordered = False
        if t._guard() and tribute is None:
            ordered = True
            _order_mark(t, partner, TRIBUTE_DEF, beloved, x, z)
            _story(t, acc)
            tribute = next((l for l in acc if (" %s painted Tribute@" % partner) in l), None)
        if t._guard():
            t._current.detail = "after %d ticks: memorial %s; tribute %s%s" % (waited, memorial, tribute, " (ordered: not chosen in the window)" if ordered else "")

    with t.component("memorial_eases_its_painters_grief"):
        if t._guard():
            if not memorial:
                raise ExpectationFailed("%s, grieving %s, painted no memorial in 60000 ticks of low joy: its marks %s" % (mourner, dead, _marks_by(t, mourner)))
            eased = [x for x in _graffiti_thoughts(t, mourner) if x.get("def") == "RM_Graffiti_GriefEased"]
            if not eased:
                raise ExpectationFailed("%s painted %r but holds no RM_Graffiti_GriefEased: %s" % (mourner, memorial, _graffiti_thoughts(t, mourner)))
            t._current.detail = "%s; GriefEased %+.1f" % (memorial, float(eased[0].get("moodOffset") or 0))

    with t.component("tribute_warms_subject_and_rival_scoffs"):
        if t._guard():
            if not tribute:
                raise ExpectationFailed("no tribute by %s about %s stands: %s" % (partner, beloved, _marks_by(t, partner)))
            cell = tuple(int(v) for v in re.search(r"Tribute@\((-?\d+), 0, (-?\d+)\)", tribute).groups())
            for nick in (beloved, rival):
                _hold_at(t, nick, cell[0] + (1 if nick == rival else -1), cell[1] - 3, ticks=300)
            for _ in range(8):
                t.wait_ticks(250)
                _, per, _ = _story(t, acc)
            rb, rr = _reads(acc, beloved, cell), _reads(acc, rival, cell)
            warm = [x for x in _graffiti_thoughts(t, beloved) if x.get("def") == "RM_Graffiti_Honored"]
            sour = [ln for ln in per.get(rival, []) if ln.startswith("  opinion of %s -" % partner)]
            jealous = [x for x in _graffiti_thoughts(t, rival) if x.get("def") == "RM_Graffiti_JealousOfWall"]
            if not rb or rb[0][4] != "Honored" or not warm:
                raise ExpectationFailed("%s read the tribute as %s, Honored %s" % (beloved, rb, warm))
            if not rr or rr[0][4] not in ("Scoffs", "Jealous") or not (sour or jealous):
                raise ExpectationFailed("%s (hates %s) read the tribute as %s; opinion lines %s, jealous %s" % (rival, beloved, rr, per.get(rival), jealous))
            t._current.detail = "%s Honored %+.1f; %s %s %s" % (beloved, float(warm[0].get("moodOffset") or 0), rival, rr[0][4], (sour or jealous)[0])

    with t.component("control_no_dead_friend_no_memorial"):
        if t._guard():
            mine = _marks_by(t, plain)
            if not mine:
                raise ExpectationFailed("SITE: %s painted nothing in the window, so its not painting a memorial rules nothing out" % plain)
            mem = [ln for ln in mine if " Memorial " in ln]
            if mem:
                raise ExpectationFailed("%s, who mourns nobody, painted a memorial: %s" % (plain, mem))
            t._current.detail = "%d mark(s) by %s, none a memorial" % (len(mine), plain)


@suite.chain("scene_fights")
def scene_fights(t):
    """sc_fights (fights_reasons): three subjects of one feud painter's mockeries, each staged to mean a confrontation (_stage_pick): one stays
    drafted, one is area-restricted to a pen away from the painter, one is free, and an unrelated colonist stands by; three in-game days run
    with all three at once (one window, not three sequential runs: the same three cases, a third of the clock). The free one confronts the
    painter, the play log naming the mark as the reason; every confrontation is subject against painter; the drafted one never moves and the
    penned one never leaves its pen. Control: the social layer off, a fresh hot subject under a fresh mockery confronts nobody.
    Restore: the runner destroys the quicktest map; socialEnabled is put back here."""
    x, z = t.anchor
    painter, bystander = "GrfFightP", "GrfFightBy"
    acc, subs, pen = [], {}, (x - 24, z - 24, 7, 7)
    with t.component("site_ready_fights"):
        _site_start(t)
        _prep_site(t, 60)
        _wall_run(t, x - 20, z + 1, 41)
        t.bridge_call("jawa/map_commit")
        _recruit(t, painter, PLAIN, 10)
        _recruit(t, bystander)
        _no_cleaning(t)
        for i, role in enumerate(("drafted", "penned", "free")):
            if t._guard():
                cells = [(x - 20 + 14 * i + 2 * k, z) for k in range(7)]
                nick, mid, m, tries = _stage_pick(t, acc, "Confront", painter, HOT, 0, cells, "GrfF%s" % role[:2].capitalize())
                subs[role] = nick
        if t._guard():
            a = t.bridge_call("jawa/new_allowed_area", label="GrfPen") or {}
            p = t.bridge_call("jawa/paint_area", area="GrfPen", ops="%d,%d,%d,%d" % pen) or {}
            q = t.bridge_call("jawa/set_player_settings", pawnId=subs["penned"], area="GrfPen") or {}
            if not (a.get("success") and p.get("success", True) and q.get("success")):
                raise ExpectationFailed("SITE: the pen did not take: new_allowed_area %r; paint_area %r; set_player_settings %r" % (a, p, q))
            t.bridge_call("jawa/order_pawn", pawnId=subs["penned"], x=pen[0] + 3, z=pen[1] + 3, waitTicks=0)
            for role in ("penned", "free"):
                t.bridge_call("jawa/set_draft", pawnId=subs[role], drafted=False)
            _hold_at(t, bystander, x + 3, z - 5, ticks=0)
            t.bridge_call("jawa/set_draft", pawnId=bystander, drafted=False)
            t._current.detail = "subjects %s, pen %s" % (subs, pen)

    where, jobs = {}, set()
    with t.component("three_days_run"):
        start, waited = None, 0
        while waited < 180000 and t._guard():
            _fed(t, painter, bystander, *subs.values())
            t.wait_ticks(2500)
            waited += 2500
            _story(t, acc)
            pawns = {p.get("name") or p.get("id"): p for p in _all_colonists(t)}
            for role, nick in subs.items():
                pp = pawns.get(nick) or {}
                pos = pp.get("position") or {}
                where.setdefault(role, []).append((pos.get("x", pp.get("x")), pos.get("z", pp.get("z"))))
            who = _who(t)
            jobs.update((n, (who.get(n) or {}).get("job")) for n in subs.values())
        if t._guard():
            t._current.detail = "%d polls; confront lines %s" % (len(where.get("free", [])), [l for l in acc if " confronts " in l])

    lines = [l for l in acc if " confronts " in l]
    with t.component("free_subject_confronts_painter_over_the_mark"):
        if t._guard():
            mine = [l for l in lines if (" %s confronts %s:" % (subs["free"], painter)) in l]
            log, _ = _static(t, SOCIAL_PROOF, "PlayLog", "200")
            why = [ln for ln in log.splitlines() if ("%s confronted %s about what %s painted about %s" % (subs["free"], painter, painter, subs["free"])) in ln]
            if not mine or not why:
                raise ExpectationFailed("%s (free, meant Confront) in three days: confront lines %s; play log reason %s" % (subs["free"], mine, why))
            t._current.detail = "%s; %s" % (mine[0], why[0])

    with t.component("every_confrontation_subject_against_painter"):
        if t._guard():
            bad = [l for l in lines if not any((" %s confronts %s:" % (s, painter)) in l for s in subs.values())]
            if bad or any(bystander in l for l in lines):
                raise ExpectationFailed("confrontations not subject against painter: %s" % (bad or lines))

    with t.component("drafted_and_penned_subjects_stay"):
        if t._guard():
            d = set(where.get("drafted", []))
            out = [c for c in where.get("penned", []) if c[0] is None or not (pen[0] <= c[0] < pen[0] + pen[2] and pen[1] <= c[1] < pen[1] + pen[3])]
            went = [l for l in lines if (" %s confronts " % subs["drafted"]) in l or (" %s confronts " % subs["penned"]) in l]
            if len(d) != 1 or out or went or (subs["drafted"], CONFRONT_JOB) in jobs:
                raise ExpectationFailed("drafted cells %s; penned outside its pen at %s; their confrontations %s; jobs %s" % (sorted(d, key=str), out[:5], went, sorted(jobs, key=str)))
            t._current.detail = "drafted at %s; penned stayed in %s over %d polls" % (sorted(d, key=str), pen, len(where.get("penned", [])))

    with t.component("control_social_off_no_confrontation"):
        try:
            t.set_setting(SETTINGS, {"socialEnabled": False})
            calm = "GrfFightOff"
            _recruit(t, calm, HOT, 0)
            _static(t, SOCIAL_PROOF, "Feud", "%s/%s" % (painter, calm))
            _hold_at(t, calm, x + 16, z - 3, ticks=300)
            t.bridge_call("jawa/set_draft", pawnId=calm, drafted=False)
            _story(t, acc)
            n0 = len(acc)
            _order_mark(t, painter, MOCKERY_DEF, calm, x + 16, z)
            seen, waited = set(), 0
            while waited < 20000 and t._guard():
                _fed(t, calm, painter)
                t.wait_ticks(2000)
                waited += 2000
                _, _, gr = _story(t, acc)
                seen.add((gr.get(calm), (_who(t).get(calm) or {}).get("job")))
            if t._guard():
                late = [l for l in acc[n0:] if " confronts " in l]
                if late or any(g for g, _ in seen) or any(j == CONFRONT_JOB for _, j in seen):
                    raise ExpectationFailed("social off: confront lines %s; (grudge, job) seen %s" % (late, sorted(seen, key=str)))
                t._current.detail = "20000 ticks off: (grudge, job) seen %s" % sorted(seen, key=str)
        finally:
            t.set_setting(SETTINGS, {"socialEnabled": True})


def _factions(t):
    """{name: row} of jawa/list_factions (defName, name, isPlayer, hostile, goodwill, hidden)."""
    r = t.bridge_call("jawa/list_factions") or {}
    return {f.get("name"): f for f in (r.get("factions") or []) if f.get("name")}


@suite.chain("scene_visitors")
def scene_visitors(t):
    """sc_visitors (visitors): an insult to the trader faction on a wall its caravan passes: the caravan walks past it many times and the
    faction's goodwill moves once for the visit, by the insult's -12, never past VisitLossCap. Control: an insult to another faction on the
    same wall moves that faction nothing and the trader's read of it is 'none of theirs, goodwill 0' (GraffitiSocial.cs:639). Restore: the
    runner destroys the quicktest map. The caravan's pawns are declared to the stranger detector (they are the scene's visitors)."""
    x, z = t.anchor
    painter = "GrfInsult"
    ours_at, other_at = (x - 3, z), (x + 3, z)
    acc, trader, other = [], None, None
    with t.component("site_ready_visitors"):
        _site_start(t)
        _prep_site(t, 40)
        _wall_run(t, x - 10, z + 1, 21)
        t.bridge_call("jawa/map_commit")
        _recruit(t, painter, PLAIN, 10)
        _no_cleaning(t)
        fs = _factions(t)
        calm = [f for f in fs.values() if not f.get("isPlayer") and not f.get("hostile") and not f.get("hidden") and f.get("goodwill") is not None]
        # list_pawns names a pawn's faction by its def (JawaBenchTerrainTools.cs:1243) and storyteller_fire takes a FactionDef: the trader
        # must be the only faction of its def, and the other of another def, or a caravan or a read could not be told apart.
        defs = [f.get("defName") for f in fs.values()]
        alone = [f for f in calm if defs.count(f.get("defName")) == 1]
        trader = alone[0] if alone else None
        other = next((f for f in calm if trader and f.get("defName") != trader.get("defName")), None)
        if t._guard() and not (trader and other):
            raise ExpectationFailed("SITE: no non-hostile faction alone of its def plus another of a different def among %s"
                                    % sorted((f.get("name"), f.get("defName")) for f in calm))
        if t._guard():
            _order_mark(t, painter, INSULT_DEF, trader["name"], *ours_at)
            _order_mark(t, painter, INSULT_DEF, other["name"], *other_at)
            _story(t, acc)
            said = [l for l in acc if " painted FactionInsult@" in l]
            if len([l for l in said if ("insulting %s" % trader["name"]) in l]) != 1 or len([l for l in said if ("insulting %s" % other["name"]) in l]) != 1:
                raise ExpectationFailed("SITE: the two insults read %s (one each to %s and %s wanted)" % (said, trader["name"], other["name"]))
            t._current.detail = "trader %s (%s), other %s; %s" % (trader["name"], trader.get("defName"), other["name"], said)

    g0, caravan = {}, []
    with t.component("caravan_arrives"):
        if t._guard():
            names = (trader["name"], trader.get("defName"))
            t.expect("pawn", lambda p: p.get("faction") in names)
            g0 = {n: (_factions(t).get(n) or {}).get("goodwill") for n in (trader["name"], other["name"])}
            r = t.bridge_call("jawa/storyteller_fire", incidentDef="TraderCaravanArrival", faction=trader.get("defName"), dryRun=False) or {}
            if not r.get("fired"):
                raise ExpectationFailed("SITE: TraderCaravanArrival for %s did not fire: %s" % (trader.get("defName"), str(r)[:300]))
            waited = 0
            while waited < 6000 and t._guard() and not caravan:
                t.wait_ticks(500)
                waited += 500
                rr = t.bridge_call("jawa/list_pawns", limit=500) or {}
                caravan = [p["id"] for p in rr.get("pawns") or [] if p.get("faction") in names and not p.get("dead") and p.get("id")]
            if not caravan:
                raise ExpectationFailed("SITE: no pawn of %s on the map %d ticks after the caravan fired: %s" % (trader["name"], waited, str(r)[:200]))
            t._current.detail = "goodwill before %s; caravan %s" % (g0, caravan)

    with t.component("caravan_passes_the_wall"):
        if t._guard():
            for leg in range(10):
                if not t._guard():
                    break
                t.bridge_call("jawa/order_pawn", pawnId=",".join(caravan), x=x + (8 if leg % 2 else -8), z=z - 2, waitTicks=0)
                t.wait_ticks(1500)
                _story(t, acc)
            t._current.detail = "visitor lines %s" % [l for l in acc if (" of %s reads " % trader["name"]) in l]

    charged = [l for l in acc if (" of %s reads " % trader["name"]) in l and re.search(r": goodwill -?\d+$", l) and "none of theirs" not in l]
    with t.component("one_goodwill_change_per_visit_within_cap"):
        if t._guard():
            on_ours = [l for l in charged if ("FactionInsult@(%d, 0, %d)" % ours_at) in l]
            total = sum(int(re.search(r"goodwill (-?\d+)$", l).group(1)) for l in charged)
            g1 = (_factions(t).get(trader["name"]) or {}).get("goodwill")
            if len(on_ours) != 1 or int(re.search(r"goodwill (-?\d+)$", on_ours[0]).group(1)) != INSULT_GOODWILL:
                raise ExpectationFailed("the insult to %s charged %s over the visit (one charge of %d wanted)" % (trader["name"], on_ours, INSULT_GOODWILL))
            if -total > VISIT_LOSS_CAP or g0.get(trader["name"]) is None or g1 is None or g1 - g0[trader["name"]] != total:
                raise ExpectationFailed("the visit charged %d (cap %d); goodwill %s -> %s; lines %s" % (total, VISIT_LOSS_CAP, g0.get(trader["name"]), g1, charged))
            t._current.detail = "%s; goodwill %s -> %s" % (on_ours[0], g0[trader["name"]], g1)

    with t.component("control_other_factions_insult_moves_nothing"):
        if t._guard():
            read = [l for l in acc if (" of %s reads FactionInsult@(%d, 0, %d)" % ((trader["name"],) + other_at)) in l]
            g1 = (_factions(t).get(other["name"]) or {}).get("goodwill")
            if not read:
                raise ExpectationFailed("SITE: the caravan never read the insult to %s: the control rules nothing out" % other["name"])
            if not all("none of theirs, goodwill 0" in l for l in read) or g1 != g0.get(other["name"]):
                raise ExpectationFailed("the insult to %s, read by %s: %s; %s goodwill %s -> %s" % (other["name"], trader["name"], read, other["name"], g0.get(other["name"]), g1))
            t._current.detail = "%s; %s goodwill %s unchanged" % (read[0], other["name"], g1)


# ------------------------------- wall close-up, spree variety, art skill (scenes.json: sc_wall_closeup, sc_spree_variety, sc_art_skill)

ART_DEF = "RM_Graffiti_Stencil_Crown"   # Stencil, no minArtistic, designatorEligible (Defs/ThingDefs_Graffiti.xml): CraftCeiling Legendary
POOL_PICK_ITEM = "RIMMANDRAKE_PROBE_GRAFFITI_POOL_PICK_UNREADABLE_AT_A_CELL"
_SIDE_LINE = re.compile(r" side (-?\d+) room ")


def _side_at(t, cell):
    """The recorded wallSide of the mark at `cell` off RM_GraffitiSocialProof.Marks (' side N room ', RM_GraffitiSocialProof.cs:186); None if no mark."""
    line = _mark_line(t, cell)
    m = _SIDE_LINE.search(line or "")
    return (int(m.group(1)) if m else None), line


def _trace_lines(t):
    """New lines of RM_GraffitiSocialProof.Ledger('trace') (the ring empties on each read, GraffitiSocial.cs:1067)."""
    acc = []
    _story(t, acc)
    return acc


@suite.chain("wall_closeup")
def wall_closeup(t):
    """sc_wall_closeup (sits_on_wall, inv_mark_on_wall): an ordered lane of marks on a wall's front face (each wall north of its cell, side 0)
    is shot close up at play zoom, so a judge can see each mark lie on the face and climb over the crease onto the top (option D), the face
    bolder than the top. Controls: a mark with no wall recorded (spawned on open floor, wallSide NoWall) draws on the floor and is counted
    by RM_GraffitiStage.Count's noWall; an ordered paint on a cell whose only wall is east of it (seen edge-on, a stub) leaves no mark and the
    brush traces "found no wall to paint" (Filth_Mark.cs:349); the south-only cell is RM_GraffitiProof.FarSideSetup/FarSideRead (A9 of
    graffiti_v1_live_proof.py, RM_GraffitiProof.cs:433): a painter's-pick order whose north wall came down leaves no Filth_Mark and
    ProbeWallFaces reads s=0. The pool's own answer at a cell has no reader (POOL_PICK_ITEM). FarSideSetup clears its own site at the map's
    centre, so it runs last. Restore: the runner destroys the quicktest map."""
    x, z = t.anchor
    painter = "GrfFace"
    lane = [(x - 6 + 4 * i, z) for i in range(4)]       # floor cells south of the wall row z + 1: the wall is north of each (side 0)
    edge, stub = (x + 12, z - 8), (x + 13, z - 8)       # one lone wall cell east of `edge`, nothing else within reach
    loose = (x - 12, z - 8)                             # open floor, no wall anywhere beside it
    with t.component("site_ready_wall_closeup"):
        _site_start(t)
        _prep_site(t, 40)
        _wall_run(t, x - 9, z + 1, 17)
        _walls(t, [stub])
        t.bridge_call("jawa/map_commit")                # FIXTURE write (walls/terrain), never marks
        _recruit(t, painter, PLAIN, 10)
        _no_cleaning(t)
        rows = []
        for cell in lane:
            _order_mark(t, painter, ART_DEF, "", *cell)
            side, line = _side_at(t, cell)
            rows.append((cell, side))
            if t._guard() and side != 0:
                raise ExpectationFailed("SITE: the lane mark at %s records wallSide %r, not 0 (its wall north of it): %r" % (cell, side, line))
        t.bridge_call("jawa/set_draft", pawnId=painter, drafted=True)
        t.bridge_call("jawa/order_pawn", pawnId=painter, x=x, z=z - 14, waitTicks=0)
        t.wait_ticks(600)                                 # the painter out of frame before any shutter
        if t._guard():
            t._current.detail = "lane (cell, side): %s" % rows

    with t.component("lane_marks_on_their_front_face", shows=["mark_sits_on_the_wall"]):
        if t._guard():
            faces, _ = _static(t, "RimMandrake.Graffiti.Filth_Mark", "ProbeWallFaces")
            mm = re.search(r"mismatch=(\d+)", faces)
            if not mm or int(mm.group(1)) != 0:
                raise ExpectationFailed("Filth_Mark.ProbeWallFaces: %r (a mark records a side with no wall behind it)" % faces)
            t._current.detail = faces
        for cell in lane:
            t.screenshot(rect=(cell[0] - 2, cell[1] - 1, 5, 4), padding=0, ppc=PLAY_PPC)

    with t.component("control_no_wall_mark_on_floor_flagged"):
        before, _ = _static(t, STAGE, "Count")
        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (ART_DEF, loose[0], loose[1]))
        if t._guard():
            side, line = _side_at(t, loose)
            after, _ = _static(t, STAGE, "Count")
            nb = re.search(r"noWall (\d+)", before)
            na = re.search(r"noWall (\d+)", after)
            if side != -1 or not (nb and na) or int(na.group(1)) != int(nb.group(1)) + 1:
                raise ExpectationFailed("a mark spawned on open floor at %s reads side %r (want -1, NoWall); Count before %r after %r"
                                        % (loose, side, before, after))
            t._current.detail = "%s; %s" % (line, after)
        t.screenshot(rect=(loose[0] - 2, loose[1] - 2, 5, 5), padding=0, ppc=PLAY_PPC)

    with t.component("control_edge_on_cell_gets_no_mark"):
        if t._guard():
            _trace_lines(t)                               # empty the ring: only this order's lines below
            _recruit(t, "GrfEdge", PLAIN, 10)
            _no_cleaning(t)
            _static(t, SOCIAL_PROOF, "Order", "GrfEdge/%s//%d,%d" % (ART_DEF, edge[0], edge[1]))
            waited, said = 0, []
            while waited < 3000 and t._guard():
                t.wait_ticks(500)
                waited += 500
                said += [ln for ln in _trace_lines(t) if "found no wall to paint at (%d, 0, %d)" % edge in ln]
                if _all_marks(t, "%d,%d,1,1" % edge):
                    raise ExpectationFailed("an ordered %s stands at %s, whose only wall (east) is seen edge-on" % (ART_DEF, edge))
                if said:
                    break
            if not said:
                raise ExpectationFailed("no mark at %s, but the brush never traced refusing it in %d ticks: the order may simply not have run"
                                        % (edge, waited))
            t._current.detail = said[0]
            raise ExpectationFailed("MISSING TOOL: no probe asks GraffitiPool.WeightedPick (private) for a pick at %s, so 'the pool returns none' "
                                    "is unread; filed as %s" % (edge, POOL_PICK_ITEM))

    with t.component("control_south_only_cell_holds_no_mark"):
        if t._guard():
            _trace_lines(t)
            setup, _ = _static(t, PROOF, "FarSideSetup")
            f = _probe_fields(setup)
            if f.get("accepted") != "True" or f.get("sideBefore") != "0" or f.get("sideAfter") != "2" or f.get("ordered") != "True":
                raise ExpectationFailed("SITE: FarSideSetup %r (want accepted True, sideBefore 0, sideAfter 2, ordered True)" % setup)
            read, waited, said = "", 0, []
            while waited < 3000 and t._guard():
                t.wait_ticks(250)
                waited += 250
                said += [ln for ln in _trace_lines(t) if "no face in view" in ln and "side 2" in ln]
                read, _ = _static(t, PROOF, "FarSideRead")
                if _probe_fields(read).get("pending") == "False":
                    break
            r = _probe_fields(read)
            sides = re.search(r"sides=\d+,\d+,(\d+),\d+", read)
            if r.get("mark") != "none" or not sides or sides.group(1) != "0":
                raise ExpectationFailed("the south-only cell after its order: %r (want mark none and s=0; a build without the fix reads a mark, s=1)" % read)
            if r.get("pending") != "False" or not said:
                raise ExpectationFailed("the south-only order was not spent with the brush's trace line in %d ticks: %r; trace %s" % (waited, read, said))
            t._current.detail = "%s; %s; %s" % (setup, read, said[0])
            raise ExpectationFailed("MISSING TOOL: the pool pick at the south-only cell (GraffitiPool.WeightedPick) has no reader; filed as %s" % POOL_PICK_ITEM)


def _spree_lanes(t):
    """sc_spree_wall's six lanes: walls, a painter each on a forced RM_GraffitiPaintingSpreeBreak, 3000 ticks, painters vanished.
    -> (lanes, [marks per lane], [spree started per painter]). The same staging as spree_wall, without its components."""
    lanes, painters, started = _lanes(t), [], []
    _prep_site(t, 70)
    for ln in lanes:
        _wall_run(t, ln["x0"], ln["wall_z"], LANE_LEN)
    t.bridge_call("jawa/map_commit")
    for ln in lanes:
        r = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=ln["x0"] + LANE_LEN // 2, z=ln["wall_z"] + 2, faction="player", count=1)
        painters.append((((r or {}).get("pawns") or [{}])[0]).get("id"))
    _no_cleaning(t)
    for pid in painters:
        if pid:
            _settle_painter(t, pid)
            r = t.bridge_call("jawa/pawn_force_mental_break", pawn=pid, breakDef=SPREE_BREAK)
            started.append(bool((r or {}).get("started")))
    with _own_spree(painters):
        t.wait_ticks(3000)
    for ln in lanes:
        _remove_pawns_in(t.bridge_call, ln["rect"])
    per = [_marks_in(t, ln["rect"]) for ln in lanes] if t._guard() else []
    return lanes, per, started


@suite.chain("spree_variety")
def spree_variety(t):
    """sc_spree_variety (marks_various, inv_mark_art_set): after sc_spree_wall's six lanes, read the def and variant of every mark; at least 3
    defs and 5 def-variant pairs. The variant (Filth_Mark.variant, Filth_Mark.cs:44) is saved but no probe prints it (VARIANT_ITEM). Control:
    the pool gated to one def gives one def only (rules out variety from tint alone); no setting or probe gates the pool (RM_GraffitiMod.cs:41-48
    are the eight settings), so it waits on POOL_PICK_ITEM. Restore: the runner destroys the quicktest map."""
    lanes, per, started = [], [], []
    with t.component("site_ready_spree_variety"):
        _site_start(t)
        lanes, per, started = _spree_lanes(t)
        if t._guard():
            if not (started and all(started)):
                raise ExpectationFailed("not every painter entered the spree: %r" % started)
            empty = [i for i, m in enumerate(per) if not m]
            if empty:
                raise ExpectationFailed("SITE: lane(s) %s hold no mark after 3000 ticks (counts %s)" % (empty, [len(m) for m in per]))

    with t.component("variety_three_defs", shows=["marks_visibly_various"]):
        if t._guard():
            allm = [m for lane in per for m in lane]
            hist = {}
            for m in allm:
                hist[m["def"]] = hist.get(m["def"], 0) + 1
            if len(hist) < 3:
                raise ExpectationFailed("%d mark(s) of %d def(s) over six lanes, want >= 3 defs: %s" % (len(allm), len(hist), hist))
            t._current.detail = "%d marks, %d defs: %s" % (len(allm), len(hist), hist)
        for ln in lanes:                                  # lane by lane at play zoom: one lane fits a 64 px/cell screen, all six do not
            t.screenshot(rect=(ln["x0"], ln["wall_z"] - 3, LANE_LEN, 7), ppc=PLAY_PPC)

    with t.component("variety_five_def_variant_pairs"):
        if t._guard():
            raise ExpectationFailed("MISSING TOOL: no probe prints a mark's variant (RM_GraffitiSocialProof.Marks prints def, craft, side; "
                                    "Filth_Mark.variant is unread), so def-variant pairs cannot be counted; filed as %s" % VARIANT_ITEM)

    with t.component("control_pool_gated_to_one_def"):
        if t._guard():
            raise ExpectationFailed("MISSING TOOL: nothing gates GraffitiPool to one def (no setting, no probe), so 'one def only' cannot be "
                                    "staged; filed as %s" % POOL_PICK_ITEM)


def _room(t, x0, z0, w=9, h=7):
    """A closed, roofed w x h room (walls on its edge, a door mid-south). -> (interior centre, front-face cell under the north wall)."""
    _walls(t, _box(x0, z0, x0 + w - 1, z0 + h - 1), door=(x0 + w // 2, z0))
    t.bridge_call("jawa/set_roof_batch", ops="%d,%d,%d,%d" % (x0, z0, w, h), roofDef="RoofConstructed")
    return (x0 + w // 2, z0 + h // 2), (x0 + w // 2, z0 + h - 2)


def _room_beauty(t, cell):
    """Room Beauty at `cell` (jawa/room_get rooms[0].stats.Beauty, JawaBenchStatTools.cs:215); an outdoor or unread room fails."""
    r = t.bridge_call("jawa/room_get", x=cell[0], z=cell[1]) or {}
    if not t._guard():
        return 0.0
    rooms = r.get("rooms") or []
    val = ((rooms[0].get("stats") or {}).get("Beauty")) if rooms else None
    if not isinstance(val, (int, float)):
        raise ExpectationFailed("jawa/room_get at %s gave no indoor room Beauty: %s" % (cell, str(r)[:300]))
    return float(val)


def _held(t, nick, defs):
    return [x for x in _graffiti_thoughts(t, nick) if x.get("def") in defs] if t._guard() else []


@suite.chain("scene_art_skill")
def scene_art_skill(t):
    """sc_art_skill (art_skill, inv_beauty_and_craft): in two identical closed rooms painters of Artistic 2 and 16 each paint ART_DEF on the
    front face; room Beauty falls for the skill-2 hand and rises for the skill-16 one (a crafted mark's Beauty is CraftBeauty(craft),
    RM_GraffitiKernel.cs:1029, through StatPart_GraffitiCraft); the skill-2 room's viewer holds RM_Graffiti_UglyMark (negative), the skill-16
    room's RM_Graffiti_FineArt (positive) (GraffitiSocial.cs:436). A third pair: a skilled feuding painter's mockery of a named colonist; its
    subject holds anger (RM_Graffiti_Humiliated, as in scene_mockery) and beauty (RM_Graffiti_FineArt) together. Control: the same def with
    craft at Normal (spawned with no maker: hasCraft false, Filth_Mark.cs:422) in a second identical pair gives equal Beauty and no
    skill-signed thought. The raider-pressure settings join the start once PRESSURE_ITEM lands. Restore: the runner destroys the quicktest map."""
    x, z = t.anchor
    rooms = {"low": (x - 13, z - 3), "high": (x + 5, z - 3), "ctl_a": (x - 13, z - 14), "ctl_b": (x + 5, z - 14)}
    cells, base, marks = {}, {}, {}
    cast = {"low": ("GrfArt2", 2, "GrfSeeLow"), "high": ("GrfArt16", 16, "GrfSeeHigh")}
    mock_painter, mock_subject = "GrfMockArt", "GrfMockSubj"
    mock_at = (x, z + 9)
    craft_defs = ("RM_Graffiti_FineArt", "RM_Graffiti_UglyMark")
    with t.component("site_ready_art_skill"):
        _site_start(t)
        if _pressure_built():
            _need_pressure("the 3 raider-pressure settings at shipped defaults")
        _prep_site(t, 40)
        for key, (rx, rz) in sorted(rooms.items()):
            cells[key] = _room(t, rx, rz)
        _wall_run(t, x - 6, z + 10, 13)                   # the mockery's wall; its front face is row z + 9
        t.bridge_call("jawa/map_commit")
        base = {k: _room_beauty(t, c[0]) for k, c in cells.items()}
        if t._guard() and len({round(v, 2) for v in base.values()}) != 1:
            raise ExpectationFailed("SITE: the four empty rooms differ in Beauty before any mark: %s" % base)
        for key, (painter, art, viewer) in sorted(cast.items()):
            _recruit(t, painter, PLAIN, art)
            _recruit(t, viewer)
        for viewer in ("GrfSeeCtlA", "GrfSeeCtlB"):
            _recruit(t, viewer)
        _no_cleaning(t)
        for key, (painter, art, viewer) in sorted(cast.items()):
            mid, m = _order_mark(t, painter, ART_DEF, "", *cells[key][1])
            if t._guard():
                craft, line = _craft_at(t, *cells[key][1])
                marks[key] = (mid, craft, line)
            t.bridge_call("jawa/set_draft", pawnId=painter, drafted=True)
            t.bridge_call("jawa/order_pawn", pawnId=painter, x=x + 18, z=z + 16, waitTicks=0)
        if t._guard():
            lo, hi = marks["low"][1], marks["high"][1]
            if lo > 1 or hi < 3:              # CraftStage (RM_GraffitiKernel.cs:1059): poor or worse is ugly, good or better is fine art
                raise ExpectationFailed("SITE: the crafts came out skill 2 %s, skill 16 %s (want poor or worse, good or better); re-stage: %s"
                                        % (CRAFTS[lo], CRAFTS[hi], [marks[k][2] for k in marks]))
            t._current.detail = "empty rooms %s; skill 2 %s, skill 16 %s" % (base, CRAFTS[lo], CRAFTS[hi])

    with t.component("room_beauty_follows_skill", shows=["mark_ugliness_is_visible"]):
        if t._guard():
            after = {k: _room_beauty(t, cells[k][0]) for k in ("low", "high")}
            if not (after["low"] < base["low"] and after["high"] > base["high"]):
                raise ExpectationFailed("room Beauty (before -> after): skill 2 %.2f -> %.2f (want lower), skill 16 %.2f -> %.2f (want higher)"
                                        % (base["low"], after["low"], base["high"], after["high"]))
            t._current.detail = "skill 2 %.2f -> %.2f; skill 16 %.2f -> %.2f" % (base["low"], after["low"], base["high"], after["high"])
        for key in ("low", "high"):
            fx, fz = cells[key][1]
            t.screenshot(rect=(fx - 4, fz - 4, 9, 7), padding=0, ppc=PLAY_PPC)

    with t.component("viewers_take_the_skill_signed_thought"):
        for key in ("low", "high"):
            _hold_at(t, cast[key][2], *cells[key][0])
        t.wait_ticks(2500)
        if t._guard():
            ugly = _held(t, "GrfSeeLow", ("RM_Graffiti_UglyMark",))
            fine = _held(t, "GrfSeeHigh", ("RM_Graffiti_FineArt",))
            if not ugly or float(ugly[0].get("moodOffset") or 0) >= 0:
                raise ExpectationFailed("the skill-2 room's viewer holds no negative UglyMark: %s" % _graffiti_thoughts(t, "GrfSeeLow"))
            if not fine or float(fine[0].get("moodOffset") or 0) <= 0:
                raise ExpectationFailed("the skill-16 room's viewer holds no positive FineArt: %s" % _graffiti_thoughts(t, "GrfSeeHigh"))
            t._current.detail = "UglyMark %+.1f; FineArt %+.1f" % (float(ugly[0]["moodOffset"]), float(fine[0]["moodOffset"]))

    with t.component("skilled_mockery_hurts_and_pleases"):
        if t._guard():
            _recruit(t, mock_painter, PLAIN, 16)
            _recruit(t, mock_subject)
            _no_cleaning(t)
            _static(t, SOCIAL_PROOF, "Feud", "%s/%s" % (mock_painter, mock_subject))
            _hold_at(t, mock_subject, mock_at[0], mock_at[1] - 3, ticks=300)
            _order_mark(t, mock_painter, MOCKERY_DEF, mock_subject, *mock_at)
            craft, line = _craft_at(t, *mock_at)
            if craft < 3:
                raise ExpectationFailed("SITE: the skilled mockery came out %s (want good: Mockery is a Tag, ceiling good); re-stage: %s" % (CRAFTS[craft], line))
            t.bridge_call("jawa/set_draft", pawnId=mock_painter, drafted=True)
            t.bridge_call("jawa/order_pawn", pawnId=mock_painter, x=x + 18, z=z + 16, waitTicks=0)
            t.wait_ticks(2000)
            have = {th.get("def"): th for th in _graffiti_thoughts(t, mock_subject)}
            if "RM_Graffiti_Humiliated" not in have or "RM_Graffiti_FineArt" not in have:
                raise ExpectationFailed("the mockery's subject holds %s; want RM_Graffiti_Humiliated and RM_Graffiti_FineArt together (%s)"
                                        % (sorted(have), line))
            t._current.detail = "%s; Humiliated %+.1f, FineArt %+.1f" % (line, float(have["RM_Graffiti_Humiliated"].get("moodOffset") or 0),
                                                                          float(have["RM_Graffiti_FineArt"].get("moodOffset") or 0))

    with t.component("control_normal_craft_equal_beauty_no_thought"):
        if t._guard():
            for key in ("ctl_a", "ctl_b"):
                fx, fz = cells[key][1]
                t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (ART_DEF, fx, fz))
            for key, viewer in (("ctl_a", "GrfSeeCtlA"), ("ctl_b", "GrfSeeCtlB")):
                _hold_at(t, viewer, *cells[key][0], ticks=0)
            t.wait_ticks(2500)
            lines = [_mark_line(t, cells[k][1]) for k in ("ctl_a", "ctl_b")]
            if not all(ln and " craft - " in ln for ln in lines):
                raise ExpectationFailed("SITE: the control marks are not at Normal with no maker's craft: %s" % lines)
            ba, bb = _room_beauty(t, cells["ctl_a"][0]), _room_beauty(t, cells["ctl_b"][0])
            if abs(ba - bb) > 0.01:
                raise ExpectationFailed("the same def at Normal craft in two identical rooms: Beauty %.2f vs %.2f" % (ba, bb))
            signed = _held(t, "GrfSeeCtlA", craft_defs) + _held(t, "GrfSeeCtlB", craft_defs)
            if signed:
                raise ExpectationFailed("a Normal-craft mark gave a skill-signed thought: %s" % signed)
            t._current.detail = "Beauty %.2f = %.2f; %s" % (ba, bb, lines)


# ------------------------------------- wall loss, lived-in soak, walk (scenes.json: sc_wall_loss, sc_lived_in_soak, sc_walk)

LIVED_IN_SAVE = "RM_GraffitiLivedIn"         # the soak's mid-way keeper, which sc_walk loads (a scene save, never a canonical world save)
SOAK_START_SAVE = "RM_GraffitiSoakStart"      # the soak's restore point, saved before its first tick
WALK_RUNTIME_SAVES = ("RM_GraffitiWalkReload", "RM_GraffitiWalkOrders", "RM_GraffitiWalkStripped")   # deleted at the walk's end
TALLY_DEF = "RM_Graffiti_TallyMarks"
DAY, WEEK = 60000, 7 * 60000
SOAK_WEEKS, SOAK_SAMPLE, SOAK_FORCE_EVERY, SOAK_CONTROL_DAYS = 3, 15000, 2500, 3   # a sample each 6 in-game hours; forced paint hourly
SOAK_MOOD_BAND = 3.0          # tree.json stories_not_tax oracle: "summed mark thoughts per colonist ... about plus or minus 3 on average"
# "few per week" (tree.json stories_not_tax) has no number of his. The agent's reading, 2026-11-15: two a day at most. Its red is "a message
# every few hours" (6+ a day); the lived-in walk of RIMMANDRAKE_WALK_GRAFFITI_LIVED_IN_WALL_WEEKS_NOT_MINUTES measured 1.0-1.4 a day.
SOAK_FEW_MESSAGES = 14
COLONY_W, COLONY_H = 44, 30                   # RM_GraffitiStage.W, H (RM_GraffitiStage.cs:16); origin is the map centre less half (:72)


def _humans(t):
    """List rows of the player's living, spawned humans (jawa/list_pawns id, name = the nick the probes print)."""
    r = t.bridge_call("jawa/list_pawns", limit=500) or {}
    return [p for p in r.get("pawns") or [] if p.get("isPlayer") and p.get("def") == "Human" and p.get("id")
            and not p.get("dead") and p.get("spawned", True)]


def _walls_at(t, cells):
    """The cells among `cells` where a Wall stands now (jawa/list_things defName=Wall); an unreadable read fails, never reads as gone."""
    xs, zs = [c[0] for c in cells], [c[1] for c in cells]
    r = t.bridge_call("jawa/list_things", defName="Wall", limit=500,
                      rect="%d,%d,%d,%d" % (min(xs), min(zs), max(xs) - min(xs) + 1, max(zs) - min(zs) + 1))
    if not t._guard():
        return set(cells)
    if not (r or {}).get("success", True) or (r or {}).get("isCompleteList") is False:
        raise ExpectationFailed("jawa/list_things Wall unreadable or truncated: %r" % (r,))
    have = {((x.get("position") or {}).get("x", x.get("x")), (x.get("position") or {}).get("z", x.get("z"))) for x in (r or {}).get("things") or []}
    return {c for c in cells if c in have}


@suite.chain("scene_wall_loss")
def scene_wall_loss(t):
    """sc_wall_loss (paint_dies_with_wall, inv_wall_loss): three marks painted on one wall run, each on the front face of its own wall cell;
    one wall is deconstructed by a colonist (a Deconstruct designation and its ordered job), another destroyed by damage (jawa/damage Bomb),
    and each mark is gone the tick its wall goes (WallLossPatch prefixes Building.DeSpawn: WallLossPatch.cs:14). Every read pairs the wall
    and its mark between two ticks, so a read with the wall gone and the mark standing, or the mark gone under a standing wall, fails.
    Control: the untouched neighbour's mark stays (rules out a sweep removing every mark). Restore: the runner destroys the quicktest map."""
    x, z = t.anchor
    painter = "GrfWallLoss"
    cells = {"deconstruct": (x - 4, z), "destroy": (x, z), "neighbour": (x + 4, z)}   # floor cells; each one's wall is the cell north
    wall = {k: (c[0], c[1] + 1) for k, c in cells.items()}
    ids = {}
    with t.component("site_ready_wall_loss"):
        _site_start(t)
        _prep_site(t, 30)
        _wall_run(t, x - 6, z + 1, 13)
        t.bridge_call("jawa/map_commit")                # FIXTURE write (walls/terrain), never marks
        _recruit(t, painter, PLAIN, 10)
        _no_cleaning(t)
        for k, c in sorted(cells.items()):
            mid, _m = _order_mark(t, painter, ART_DEF, "", *c)
            side, line = _side_at(t, c)
            if t._guard():
                if side != 0:
                    raise ExpectationFailed("SITE: the %s mark at %s records wallSide %r, not 0 (its wall north of it): %r" % (k, c, side, line))
                ids[k] = mid
        if t._guard():
            if _walls_at(t, list(wall.values())) != set(wall.values()):
                raise ExpectationFailed("SITE: not every wall cell stands before the loss: %s" % sorted(_walls_at(t, list(wall.values()))))
            t._current.detail = "marks %s" % ids
        t.screenshot(rect=(x - 7, z - 2, 15, 5), padding=0, ppc=PLAY_PPC)

    with t.component("deconstructed_wall_takes_its_mark"):
        if t._guard():
            w, c = wall["deconstruct"], cells["deconstruct"]
            t.bridge_call("jawa/designate_batch", action="add", designation="Deconstruct", rect="%d,%d,1,1" % w)
            for p in _humans(t):        # an undesignated Deconstruct order fails its reservation (Rites/validation.py:653); one hand takes it
                t.bridge_call("jawa/ordered_job", pawnId=p["id"], jobDef="Deconstruct", targetAX=w[0], targetAZ=w[1], waitTicks=0)
            waited, up = 0, True
            while waited < 6000 and t._guard():
                t.wait_ticks(60)
                waited += 60
                up = bool(_walls_at(t, [w]))
                standing = ids.get("deconstruct") in _all_marks(t, "%d,%d,1,1" % c)
                if not up and standing:
                    raise ExpectationFailed("the wall at %s was deconstructed by +%d ticks and its mark %s still stands at %s" % (w, waited, ids.get("deconstruct"), c))
                if up and not standing:
                    raise ExpectationFailed("the mark %s at %s went at +%d ticks while its wall %s still stands" % (ids.get("deconstruct"), c, waited, w))
                if not up:
                    break
            if up and t._guard():
                raise ExpectationFailed("SITE: the wall at %s still stands %d ticks after its Deconstruct designation and orders" % (w, waited))
            t._current.detail = "wall %s deconstructed by +%d ticks; its mark went with it" % (w, waited)

    with t.component("destroyed_wall_takes_its_mark"):
        if t._guard():
            w, c = wall["destroy"], cells["destroy"]
            r = t.bridge_call("jawa/damage", damageDef="Bomb", amount=5000, x=w[0], z=w[1], allowColonists=False)
            up = bool(_walls_at(t, [w]))                # no tick between the damage and these reads: the same tick
            standing = ids.get("destroy") in _all_marks(t, "%d,%d,1,1" % c)
            if up:
                raise ExpectationFailed("SITE: jawa/damage Bomb 5000 left the wall at %s standing: %s" % (w, str(r)[:300]))
            if standing:
                raise ExpectationFailed("the wall at %s was destroyed and its mark %s still stands at %s, the same tick" % (w, ids.get("destroy"), c))
            t._current.detail = "wall %s destroyed; its mark gone the same tick" % (w,)

    with t.component("control_untouched_neighbour_keeps_its_mark"):
        if t._guard():
            t.wait_ticks(2500)
            w, c = wall["neighbour"], cells["neighbour"]
            if not _walls_at(t, [w]):
                raise ExpectationFailed("SITE: the neighbour's wall at %s is gone too: the control rules nothing out" % (w,))
            if ids.get("neighbour") not in _all_marks(t, "%d,%d,1,1" % c):
                raise ExpectationFailed("the untouched neighbour's mark %s at %s is gone: marks went that no wall loss explains" % (ids.get("neighbour"), c))
            t._current.detail = "neighbour mark %s stands under its wall %s" % (ids.get("neighbour"), w)
        t.screenshot(rect=(x - 7, z - 2, 15, 5), padding=0, ppc=PLAY_PPC)


def _load(t, name):
    """Load the save `name` (rimworld/load_game_ready, as _reload); a map that does not come back fails the component."""
    import time
    if not t._guard():
        return
    t.bridge_call("rimworld/load_game_ready", saveName=name)
    for _ in range(60):
        mi = t.bridge_call("jawa/map_info")
        if isinstance(mi, dict) and mi.get("success") is not False and mi.get("size"):
            return
        time.sleep(1.0)
    raise ExpectationFailed("save %r did not load to a map within 60 s" % name)


def _said(t):
    """GraffitiSocial.messagesSent, every message the walls sent since the game started (RM_GraffitiSocialProof.Said, GraffitiSocial.cs:593)."""
    text, _ = _static(t, SOCIAL_PROOF, "Said", "1")
    if t._guard() and not text.startswith("SAID "):
        raise ExpectationFailed("RM_GraffitiSocialProof.Said answered %r" % text)
    return int((text.split() + ["0", "0"])[1]) if text.startswith("SAID ") else 0


def _mood_sum(t):
    """(mean over the colonists of each one's summed RM_Graffiti_ mood offsets, {nick: sum}) now (jawa/pawn_thoughts per colonist)."""
    sums = {}
    for p in _humans(t):
        sums[p.get("name") or p["id"]] = round(sum(float(x.get("moodOffset") or 0) for x in _graffiti_thoughts(t, p["id"])), 2)
    return (sum(sums.values()) / len(sums) if sums else 0.0), sums


@contextlib.contextmanager
def _graffiti_minds(ids):
    """clockgate.expected_disturbance for the mod's OWN mental states on these colonists (a spree, a compulsive clean): a soak of an ordinary
    colony meets them by design. Anything else (another break, a death, a raid, a modal) still stops the clock and the row reads it."""
    import clockgate
    nums = set(n for n in (clockgate._thing_number(p) for p in ids if p) if n is not None)

    def pred(tr):
        return (isinstance(tr, dict) and tr.get("kind") == "mental" and clockgate._thing_number(tr.get("subjectId")) in nums
                and str(tr.get("detail") or "").endswith((SPREE_STATE, CLEAN_STATE)))
    with clockgate.expected_disturbance("the colony's own Graffiti mental states", pred):
        yield


def _soak(t, ticks, force_every=None, keep_at=None):
    """Run `ticks` (suite.wait_ticks' verified chunks are the top speed: no game-speed call), a mood sample each SOAK_SAMPLE ticks and the message count each week; with `force_every`, one colonist is
    put on the forced spree (RM_GraffitiStage.Spree "1") that often; at `keep_at` ticks the game is saved as LIVED_IN_SAVE.
    -> ([(tick offset, mean mood sum, {nick: sum})], [messages per week (or part week)], spree calls started)"""
    samples, weeks, forced = [], [], 0
    ids = [p["id"] for p in _humans(t)]
    said0 = _said(t)
    step = force_every or SOAK_SAMPLE
    done, kept = 0, keep_at is None
    with _graffiti_minds(ids):
        while done < ticks and t._guard():
            if force_every:
                text, _ = _static(t, STAGE, "Spree", "1")
                forced += 1 if text.startswith("SPREE started 1") else 0
            t.wait_ticks(step)
            done += step
            if done % SOAK_SAMPLE == 0 or done >= ticks:
                mean, sums = _mood_sum(t)
                samples.append((done, round(mean, 2), sums))
            if done % WEEK == 0 or done >= ticks:
                said = _said(t)
                weeks.append(said - said0)
                said0 = said
            if not kept and done >= keep_at:
                t.bridge_call("rimworld/save_game", saveName=LIVED_IN_SAVE)
                kept = True
    return samples, weeks, forced


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


@suite.chain("scene_lived_in_soak")
def scene_lived_in_soak(t):
    """sc_lived_in_soak (stories_not_tax): a colony of six on ordinary (vanilla Wall) walls, RM_GraffitiStage.Colony's base with Busy's work,
    runs three in-game weeks at top speed with no forcing; after week one the colonists' summed Graffiti mood thoughts average within
    SOAK_MOOD_BAND, and Graffiti messages number SOAK_FEW_MESSAGES or fewer in every week (all kinds: GraffitiSocial.Tell counts every one).
    Mid-way the game is saved as LIVED_IN_SAVE, the lived-in save sc_walk loads. Control: from the same start, painting forced every hour
    for SOAK_CONTROL_DAYS shows a standing tax outside the band (rules out an instrument blind to thoughts). Restore: load SOAK_START_SAVE.
    The 3 raider-pressure settings join the start once PRESSURE_ITEM lands. A raid, a death or another break mid-soak stops the clock
    (clockgate): only the colony's own Graffiti mental states are declared."""
    samples, weeks = [], []
    with t.component("site_ready_lived_in_soak"):
        _site_start(t)
        if _pressure_built():
            _need_pressure("the 3 raider-pressure settings at shipped defaults")
        colony, _ = _static(t, STAGE, "Colony")
        busy, _ = _static(t, STAGE, "Busy")
        have = _humans(t)
        if t._guard() and len(have) > 6:
            raise ExpectationFailed("SITE: the map holds %d colonists before casting, more than the scene's six" % len(have))
        for i in range(6 - len(have) if t._guard() else 0):
            _cast(t, "Recruit", "GrfSoak%d//" % i)          # ordinary colonists: their own traits and skills, nothing cast
        if t._guard():
            have = _humans(t)
            _fed(t, *[p["id"] for p in have])
            mi = t.bridge_call("jawa/map_info") or {}
            ox, oz = int(mi.get("sizeX") or 250) // 2 - COLONY_W // 2, int(mi.get("sizeZ") or 250) // 2 - COLONY_H // 2
            r = t.bridge_call("jawa/list_things", defName="Wall", rect="%d,%d,%d,%d" % (ox, oz, COLONY_W, COLONY_H), limit=1000) or {}
            nwall = len(r.get("things") or [])
            if len(have) != 6 or nwall == 0:
                raise ExpectationFailed("SITE: %d colonists (want 6) and %d vanilla Wall in the base: %s; %s" % (len(have), nwall, colony, busy))
            t.bridge_call("rimworld/save_game", saveName=SOAK_START_SAVE)
            t._current.detail = "%s; %s; colonists %s; %d walls" % (colony, busy, sorted(p.get("name") for p in have), nwall)

    with t.component("soak_three_weeks"):
        if t._guard():
            samples, weeks, _ = _soak(t, SOAK_WEEKS * WEEK, keep_at=SOAK_WEEKS * WEEK // 2)
            if len(_humans(t)) != 6:
                raise ExpectationFailed("SITE: %d of the six colonists are alive after the soak: the colony is no longer the scene's" % len(_humans(t)))
            t._current.detail = "messages per week %s; mood mean by day %s" % (weeks, [s[1] for s in samples if s[0] % DAY == 0])

    with t.component("soak_mood_sum_stays_small"):
        if t._guard():
            late = [s[1] for s in samples if s[0] > WEEK]
            if not late:
                raise ExpectationFailed("no mood sample after week one: the soak never reached a steady state")
            avg = _mean(late)
            if abs(avg) > SOAK_MOOD_BAND:
                worst = max(samples, key=lambda s: abs(s[1]))
                raise ExpectationFailed("after week one the colonists' summed Graffiti mood averages %+.2f (band +-%.1f); worst sample at +%d: %s"
                                        % (avg, SOAK_MOOD_BAND, worst[0], worst[2]))
            t._current.detail = "after week one: mean %+.2f over %d samples (min %+.2f, max %+.2f)" % (avg, len(late), min(late), max(late))

    with t.component("soak_messages_few_per_week"):
        if t._guard():
            if len(weeks) < SOAK_WEEKS or any(n > SOAK_FEW_MESSAGES for n in weeks):
                raise ExpectationFailed("Graffiti messages per week %s (want %d weeks, each <= %d)" % (weeks, SOAK_WEEKS, SOAK_FEW_MESSAGES))
            t._current.detail = "messages per week %s" % weeks

    with t.component("control_forced_hourly_painting_shows_a_tax"):
        if t._guard():
            _load(t, SOAK_START_SAVE)
            ctl, cweeks, forced = _soak(t, SOAK_CONTROL_DAYS * DAY, force_every=SOAK_FORCE_EVERY)
            late = [s[1] for s in ctl if s[0] > DAY]
            avg = _mean(late)
            if not forced:
                raise ExpectationFailed("SITE: RM_GraffitiStage.Spree started no spree in %d hourly calls" % (SOAK_CONTROL_DAYS * 24))
            if abs(avg) <= SOAK_MOOD_BAND:
                raise ExpectationFailed("painting forced hourly for %d days: summed Graffiti mood averages %+.2f, inside the band +-%.1f; the "
                                        "instrument cannot tell a tax (%d sprees, samples %s)" % (SOAK_CONTROL_DAYS, avg, SOAK_MOOD_BAND, forced, late))
            t._current.detail = "forced %d sprees: mean %+.2f after day one; messages %s" % (forced, avg, cweeks)

    with t.component("restore_soak_start"):
        _load(t, SOAK_START_SAVE)


def _colony_rects(t):
    """RM_GraffitiStage.Colony's corridor and its two steel wall rows (RM_GraffitiStage.cs:72,82,86), from the map size it centres on.
    -> (corridor 'x,z,w,h', [corridor floor cells beside the south steel wall])"""
    mi = t.bridge_call("jawa/map_info") or {}
    ox, oz = int(mi.get("sizeX") or 250) // 2 - COLONY_W // 2, int(mi.get("sizeZ") or 250) // 2 - COLONY_H // 2
    return "%d,%d,36,3" % (ox + 4, oz + 13), [(ox + dx, oz + 13) for dx in range(6, 38, 4)]


def _visit(t, trader, acc):
    """A trader caravan of `trader` arrives (jawa/storyteller_fire TraderCaravanArrival, as scene_visitors) and walks the corridor ten
    times. -> (its charge lines off the trace, its goodwill change over the visit)."""
    names = (trader["name"], trader.get("defName"))
    t.expect("pawn", lambda p: p.get("faction") in names)
    g0 = (_factions(t).get(trader["name"]) or {}).get("goodwill")
    r = t.bridge_call("jawa/storyteller_fire", incidentDef="TraderCaravanArrival", faction=trader.get("defName"), dryRun=False) or {}
    if t._guard() and not r.get("fired"):
        raise ExpectationFailed("SITE: TraderCaravanArrival for %s did not fire: %s" % (trader.get("defName"), str(r)[:300]))
    caravan, waited = [], 0
    while waited < 6000 and t._guard() and not caravan:
        t.wait_ticks(500)
        waited += 500
        rr = t.bridge_call("jawa/list_pawns", limit=500) or {}
        caravan = [p["id"] for p in rr.get("pawns") or [] if p.get("faction") in names and not p.get("dead") and p.get("id")]
    if t._guard() and not caravan:
        raise ExpectationFailed("SITE: no pawn of %s on the map %d ticks after the caravan fired" % (trader["name"], waited))
    rect, _cells = _colony_rects(t)
    cx, cz, cw, _ch = (int(v) for v in rect.split(","))
    for leg in range(10):
        if not t._guard():
            break
        t.bridge_call("jawa/order_pawn", pawnId=",".join(caravan), x=cx + (cw - 2 if leg % 2 else 1), z=cz + 1, waitTicks=0)
        t.wait_ticks(1500)
        _story(t, acc)
    charged = [l for l in acc if (" of %s reads " % trader["name"]) in l and re.search(r": goodwill -?\d+$", l) and "none of theirs" not in l]
    g1 = (_factions(t).get(trader["name"]) or {}).get("goodwill")
    return charged, (g1 - g0 if g0 is not None and g1 is not None else None)


def _order_run(t, trader, first):
    """One order of the walk: 'raid' then the trader's visit, or 'trader' then the raid (RM_GraffitiProof A2 RaidStart/RaidExit).
    -> (charge lines of the visit, goodwill change, the raid's exit line)"""
    acc = []
    _story(t, acc)
    del acc[:]                                       # the ring emptied: only this order's lines below
    raid = ""
    if first == "raid":
        _n, raid = _exit_tags(t)
    charged, delta = _visit(t, trader, acc)
    if first == "trader":
        _n, raid = _exit_tags(t)
    return charged, delta, raid


@suite.chain("scene_walk_lived_in")
def scene_walk_lived_in(t):
    """sc_walk (walk_lived_in): LIVED_IN_SAVE (sc_lived_in_soak's mid-way keeper, loaded by name; a fresh map would read under a week of
    ticks) is reloaded and every mark matches the save; a scrawl and tally pair on the lived-in wall is captured at 64 px for his re-show;
    a colonist low on joy takes RM_PaintGraffitiJob and leaves a mark; a spree repeated on the corridor raises the mark count; with an
    insult to a trader faction on the corridor wall, raid then trader, reload, trader then raid: each order charges the insult once and
    both give the same goodwill change. The raider pressure record and letter wait on PRESSURE_ITEM (_need_pressure). Control: the same
    save with every mark stripped (jawa/destroy_batch Filth on each mark's cell) fails the reload check. Restore: keep LIVED_IN_SAVE, delete
    WALK_RUNTIME_SAVES (game_paths.SAVES). Hold: owner_review."""
    rows, trader = {}, None
    with t.component("site_ready_walk_lived_in"):
        _load(t, LIVED_IN_SAVE)
        _site_start(t)
        if _pressure_built():
            _need_pressure("the 3 raider-pressure settings at shipped defaults")
        _, now = _static(t, PROOF, "Loaded")
        if t._guard():
            if now is None or int(now) < WEEK:
                raise ExpectationFailed("SITE: %s loaded at tick %r, under a week: not the lived-in save made mid-way" % (LIVED_IN_SAVE, now))
            rows = _mark_rows(t)
            if not rows:
                raise ExpectationFailed("SITE: %s holds no mark: the lived-in wall is bare" % LIVED_IN_SAVE)
            t._current.detail = "%s at tick %s, %d marks, colonists %s" % (LIVED_IN_SAVE, now, len(rows), sorted(p.get("name") for p in _humans(t)))

    with t.component("reload_keeps_every_mark"):
        _reload(t, WALK_RUNTIME_SAVES[0])
        if t._guard():
            after = _mark_rows(t)
            lost = sorted(set(rows) - set(after))
            changed = sorted(c for c in rows if c in after and after[c] != rows[c])
            if lost or changed or len(after) != len(rows):
                raise ExpectationFailed("after reload %d of %d marks: lost %s, changed %s" % (len(after), len(rows), lost[:5], [(c, rows[c], after[c]) for c in changed[:3]]))
            t._current.detail = "%d marks match the save after reload" % len(after)

    with t.component("reload_keeps_the_pressure_record"):
        if t._guard():
            _need_pressure("the raider pressure record across a reload")

    with t.component("scrawl_and_tally_pair_captured"):
        if t._guard():
            rows = _mark_rows(t)
            scrawls = [c for c, r in rows.items() if FORM_OF.get(r["def"]) == "Scrawl" and r["def"] != TALLY_DEF]
            tallies = [c for c, r in rows.items() if r["def"] == TALLY_DEF]
            if not (scrawls and tallies):
                raise ExpectationFailed("SITE: the lived-in wall holds %d scrawl(s) and %d tally mark(s): no pair to capture" % (len(scrawls), len(tallies)))
            s, k = min(((a, b) for a in scrawls for b in tallies), key=lambda p: abs(p[0][0] - p[1][0]) + abs(p[0][1] - p[1][1]))
            x0, z0 = min(s[0], k[0]) - 2, min(s[1], k[1]) - 2
            t.screenshot(rect=(x0, z0, abs(s[0] - k[0]) + 5, abs(s[1] - k[1]) + 5), padding=0, ppc=PLAY_PPC)
            t._current.detail = "scrawl %s %s, tally %s, for his re-show" % (rows[s]["def"], s, k)

    with t.component("recreation_job_leaves_a_mark"):
        if t._guard():
            hands = _humans(t)
            fun = hands[0].get("name") if hands else None
            if not fun:
                raise ExpectationFailed("SITE: no colonist on the lived-in map")
            for p in hands:
                t.bridge_call("jawa/pawn_need", pawn=p["id"], action="need", need="Joy", level=0.2 if p.get("name") == fun else 0.9)
            before, seen, waited = len(_marks_by(t, fun)), None, 0
            while waited < 15000 and t._guard():
                t.wait_ticks(500)
                waited += 500
                who = _who(t)
                if seen is None and (who.get(fun) or {}).get("job") == PAINT_JOB:
                    seen = waited
                if seen is not None and len(_marks_by(t, fun)) > before:
                    break
            mine = _marks_by(t, fun)
            if seen is None or len(mine) <= before:
                raise ExpectationFailed("%s at joy 0.2: seen on %s at %r, marks by it %d -> %d in %d ticks" % (fun, PAINT_JOB, seen, before, len(mine), waited))
            t._current.detail = "%s on %s at +%d; %s" % (fun, PAINT_JOB, seen, mine[-1])

    with t.component("repeated_spree_adds_marks"):
        if t._guard():
            rect, cells = _colony_rects(t)
            whole = _whole_map(t)
            n0, c0 = len(_all_marks(t, whole)), len(_all_marks(t, rect))
            hands = [p for p in _humans(t)][:2]
            for p, cell in zip(hands, cells[1::3]):
                _hold_at(t, p["id"], cell[0], cell[1], ticks=0)
            t.wait_ticks(900)
            started = []
            for p in hands:
                t.bridge_call("jawa/set_draft", pawnId=p["id"], drafted=False)
                r = t.bridge_call("jawa/pawn_force_mental_break", pawn=p["id"], breakDef=SPREE_BREAK)
                started.append(bool((r or {}).get("started")))
            with _own_spree([p["id"] for p in hands]):
                t.wait_ticks(3000)
            n1, c1 = len(_all_marks(t, whole)), len(_all_marks(t, rect))
            if not (started and all(started)):
                raise ExpectationFailed("SITE: not every corridor painter entered the spree: %r" % started)
            if n1 <= n0:
                raise ExpectationFailed("the repeated spree on the corridor: marks on the map %d -> %d (corridor %d -> %d)" % (n0, n1, c0, c1))
            t._current.detail = "marks on the map %d -> %d, corridor %d -> %d" % (n0, n1, c0, c1)
            t.screenshot(rect=tuple(int(v) for v in rect.split(",")), ppc=PLAY_PPC)

    runs = {}
    with t.component("site_ready_two_orders"):
        if t._guard():
            fs = _factions(t)
            calm = [f for f in fs.values() if not f.get("isPlayer") and not f.get("hostile") and not f.get("hidden") and f.get("goodwill") is not None]
            defs = [f.get("defName") for f in fs.values()]
            alone = [f for f in calm if defs.count(f.get("defName")) == 1]     # as scene_visitors: a caravan told apart by its def
            trader = alone[0] if alone else None
            if not trader:
                raise ExpectationFailed("SITE: no non-hostile faction alone of its def among %s" % sorted((f.get("name"), f.get("defName")) for f in calm))
            _rect, cells = _colony_rects(t)
            free = [c for c in cells if c not in _mark_rows(t)]
            painter = (_humans(t) or [{}])[0].get("name")
            if not free or not painter:
                raise ExpectationFailed("SITE: no free corridor cell (%s) or no painter for the insult" % cells)
            _fed(t, painter)
            _order_mark(t, painter, INSULT_DEF, trader["name"], *free[0])
            runs["insult"] = free[0]
            t.bridge_call("rimworld/save_game", saveName=WALK_RUNTIME_SAVES[1])
            t._current.detail = "insult to %s at %s" % (trader["name"], free[0])

    for first in ("raid", "trader"):
        with t.component("order_%s_first" % first):
            if t._guard():
                if first == "trader":
                    _load(t, WALK_RUNTIME_SAVES[1])
                charged, delta, raid = _order_run(t, trader, first)
                runs[first] = (charged, delta)
                on_ours = [l for l in charged if ("FactionInsult@(%d, 0, %d)" % runs.get("insult", (-1, -1))) in l]
                if len(on_ours) != 1 or delta is None:
                    raise ExpectationFailed("%s first: the insult to %s charged %s; goodwill change %r; raid %s" % (first, trader["name"], on_ours, delta, raid))
                t._current.detail = "%s first: %s; goodwill %+d; %s" % (first, on_ours[0], delta, raid)

    with t.component("both_orders_same_insult_goodwill_once"):
        if t._guard():
            if not ("raid" in runs and "trader" in runs):
                raise ExpectationFailed("an order did not run to its end: ran %s" % sorted(k for k in runs if k != "insult"))
            (ca, da), (cb, db) = runs["raid"], runs["trader"]
            if da != db:
                raise ExpectationFailed("raid then trader moved %s's goodwill %+d, trader then raid %+d: %s / %s" % (trader["name"], da, db, ca, cb))
            t._current.detail = "both orders %+d" % da

    with t.component("both_orders_same_pressure_letter"):
        if t._guard():
            _need_pressure("the pressure letter of each order")

    with t.component("control_stripped_save_fails_reload_check"):
        if t._guard():
            _load(t, WALK_RUNTIME_SAVES[1])
            held = _mark_rows(t)
            t.bridge_call("jawa/destroy_batch", rects=";".join("%d,%d,1,1" % c for c in held), categories="Filth")
            t.bridge_call("rimworld/save_game", saveName=WALK_RUNTIME_SAVES[2])
            _load(t, WALK_RUNTIME_SAVES[2])
            after = _mark_rows(t)
            lost = sorted(set(held) - set(after))
            if not held or len(lost) != len(held):
                raise ExpectationFailed("the stripped save reloads %d of %d marks: the reload check would not fail it (lost %d)" % (len(after), len(held), len(lost)))
            t._current.detail = "stripped save: %d of %d marks missing, the reload check fails it" % (len(lost), len(held))

    with t.component("restore_delete_runtime_saves"):
        import game_paths
        gone = []
        for name in WALK_RUNTIME_SAVES:                     # never LIVED_IN_SAVE, never a canonical world save
            p = os.path.join(game_paths.SAVES, name + ".rws")
            if os.path.exists(p):
                os.remove(p)
                gone.append(name)
        t._current.detail = "deleted %s; kept %s" % (gone, LIVED_IN_SAVE)
