"""validation.py -- modcheck suite for RimMandrake: Graffiti Framework
(mandrake.rm.graffiti). Trial plan: design/RimMandrake/northstar_trials/Graffiti_trial_plan.md.

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Graffiti

Grounded in the mod's source: `RM_GraffitiMod.cs` for the SIX settings toggles
(`paintingEnabled`, `paintIntervalTicks`, `viewerReactionEnabled`, `breachBiasEnabled`,
`raidExitTaggingEnabled`, `autoCleanProtectionEnabled`); `JobDriver_PaintGraffiti.cs`
(goto, then a periodic `Filth_Mark.MakeMark` toil gated on `paintIntervalTicks`, picking
through `GraffitiPool.PickForSpree`); `JoyGiver_PaintGraffiti.cs` /
`JobGiver_GraffitiPaintingSpree.cs` (the two places `paintingEnabled` is checked);
`Defs/ThinkTreeDefs_Graffiti.xml` (the `RM_GraffitiPaintingSpreeState` hook).

THE SPREE PAINTS THE WHOLE WEIGHTED POOL, NOT ONLY `RM_Graffiti_Vandal`. Every def
carrying a `ModExtension_Graffiti` whose form is Scrawl/Tag/ThrowUp/Glyph can be picked.
This suite therefore counts `MARK_DEFS` -- every mark def this mod ships, read from its own
`Defs/*.xml` at import -- never one defName. (A suite that counted only Vandal read a spree
of six Tags as "no mark": a false fail.)

Behaviour that is UNMEASURED until the first live run: lane geometry vs the 12-cell search
radius of `GraffitiJobUtility.TryFindWallMarkCell`; `jawa/destroy_batch categories=Pawn`
removing painters without touching marks; `rimworld/screenshot_cell_rect` result key `path`.
Not expressible with existing bridge tools (see the plan, section 6): per-variant pinning of a
`Graphic_Random` mark and its resolved texture name (gallery pages spawn several of each def
and rely on random variants instead), `GameGlowAt`, assembly MVID. Ideo assignment of the
painters is not driven here, so meme-gated glyphs appear only if the quicktest ideo holds the
meme.

Two settings still gate nothing reachable in Graffiti alone: `viewerReactionEnabled`
(`ThoughtWorker_ViewedGraffitiMark`, re-measure: SacredGraffiti ships its ThoughtDef) and
`breachBiasEnabled` (needs a def with `breachLure`). They carry write+read-back components.
"""
import os
import re

from modcheck import Suite, ExpectationFailed

suite = Suite("Graffiti")
suite.toggles = ["paintingEnabled", "paintIntervalTicks",
                 "viewerReactionEnabled", "breachBiasEnabled",
                 "raidExitTaggingEnabled", "autoCleanProtectionEnabled"]

VANDAL_DEF = "RM_Graffiti_Vandal"


def _mark_defs():
    """[(defName, form)] for every ThingDef in this mod's Defs/ carrying a ModExtension_Graffiti.
    Parsed per `<ThingDef>` block, `form` read from inside it (never a fixed line number)."""
    out = []
    ddir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Defs")
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

LANE_LEN, LANE_DX, LANE_DZ = 14, 30, 16     # lanes > 12-cell search radius apart


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
                          waitTicks=600, timeoutSeconds=60)
        if t._guard():
            if not (bool((r or {}).get("accepted")) and bool((r or {}).get("nowRunningRequested"))):
                raise ExpectationFailed(
                    "jawa/ordered_job RM_PaintGraffitiJob was not accepted and running: %r" % r)
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
        t.wait_ticks(900)
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
        t.wait_ticks(3000)
        # painters out of frame before any shutter: a body must not occlude a mark
        for ln in lanes:
            t.bridge_call("jawa/destroy_batch", rects=ln["rect"], categories="Pawn")
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
        t.screenshot(rect=(l0["x0"], l0["wall_z"] - 3, LANE_LEN, 7))

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
            bad = [m for m in per_lane[0]
                   if abs(m["z"] - ln["wall_z"]) != 1 or not (ln["x0"] <= m["x"] < ln["x0"] + LANE_LEN)]
            if not per_lane[0] or bad:
                raise ExpectationFailed("lane 0 marks not on cells cardinal to the wall run: %s" % bad[:5])
            m0 = per_lane[0][0]
            t.screenshot(rect=(m0["x"] - 3, ln["wall_z"] - 2, 7, 5), padding=0)


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
            t.screenshot(rect=(x0, z0 - 1, 22, 6 * len(runs)))

        for ri, defs in enumerate(runs):
            with t.component("closeup_page_%d_%d" % (pi, ri), shows=["never_real_world_english"]):
                placed = build(runs=[defs])
                t.screenshot(rect=(x0, z0 - 1, 22, 3), padding=0)

            with t.component("dirt_page_%d_%d" % (pi, ri), shows=["never_reads_as_dirt"]):
                build(runs=[defs], controls="Filth_Dirt")
                t.screenshot(rect=(x0, z0 - 1, 22, 3), padding=0)


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
        t.screenshot(rect=(x - 8, z - 1, 17, 4), padding=0)


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
    """Write + read-back only: needs a def with `breachLure`, which no shipped def carries."""
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
