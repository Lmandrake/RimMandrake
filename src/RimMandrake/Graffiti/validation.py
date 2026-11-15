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
        for key, painter, cell in (("good", "GrfFine", good), ("bad", "GrfClumsy", bad)):
            mid, m = _order_mark(t, painter, VANDAL_DEF, "", *cell)
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
