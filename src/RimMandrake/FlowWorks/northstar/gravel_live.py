"""GRAVEL live check (DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY + PIT_DIG_FIX_SAND_SLIDES_BACK_IN, owner 2026-10-25: "you can't dig
in sand or mud (just slides back in)"; rock ground "produces a chunk or gravel"; "it takes 1 gravel or 2 chunks to put it all
back in again"; mining rock "should now also produce the same material as the ground digging when it fails to produce a
chunk"). Design: D:\\ClaudeWork\\rimmandrake\\dig_spoil_20261025\\DESIGN.md.

  python.exe src/RimMandrake/FlowWorks/northstar/gravel_live.py [out.json] [--origin X,Z] [--fresh-map]

PROVE  on a cleared 17x17 plot, with the five gravel toggles on, rock-ground digging on, finds and deep stone off (restored
       after), and one fresh colonist (Mining 10, Hauling off, every other colonist vanished):
       GS_sand_refused            a Sand square: Designator_DigCanal refuses it with "slide back in"; a soil square beside it
                                  is accepted (the control: the instrument can see an acceptance).
       GS_fill_costs_one_gravel   a soil square bridged to D1, 1 RM_Gravel spawned beside it: the work giver offers the fill
                                  job, and the fill ordered with that gravel takes D1 -> D0 and spends exactly 1 gravel (the
                                  probe before the gravel is recorded, not judged: map chunks also pay).
       GS_rock_ground_cut_yields_gravel_or_chunk
                                  a Granite_Rough square: an ordered colonist cut D0 -> D1 leaves exactly one new spoil item,
                                  1 RM_Gravel or 1 ChunkGranite, never both, never nothing.
       GS_mined_rock_miss_yields_gravel
                                  4 spawned Granite walls, 4 apart, each mined by an ordered Mine job: each wall leaves exactly
                                  one of ChunkGranite or RM_Gravel within 1 square, all four measured, at least one leaving gravel.
       ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN (owner card 2026-10-25):
       GS_ice_cut_yields_crushed_ice
                                  an Ice square: an ordered cut D0 -> D1 leaves exactly 1 RM_CrushedIce, no gravel, no chunk.
       GS_crushed_ice_melts_to_water
                                  1 RM_CrushedIce spawned on open ground above 0 C: gone within 15000 ticks, and the world
                                  release ledgers (RM_IceMelter.ProofMeltLedger: spilled + into water + nearby) rose by exactly
                                  10000 dL (1,000 L: the notch its cut removed, ICE_YIELD_DECIDE_ONE_CUT_FOUR_NOTCHES).
                                  A cold site -> UNMEASURED(SITE).
       ICE_MELT_TAME_STACK_FLOOD (owner card 2026-10-25, "Melt one pile at a time"):
       GS_crushed_ice_stack_thaws_one_at_a_time
                                  a stack of 2 RM_CrushedIce on open ground above 0 C: the first melt leaves exactly 1 behind
                                  and the ledgers rose by exactly 10000 dL; the second melts later, +10000 dL more. The room
                                  cooling is owed to a roofed-room row (outdoors pushes no heat); RM_IceMelter.ProofMeltCooling
                                  is recorded in the detail.
       DIG_FILL_TUNE_HOURS_OF_SHOVEL_WORK (owner card 2026-10-25):
       GS_dig_labour_multiplier_scales_the_cut
                                  the same colonist cuts one soil square D0 -> D1 at digLabourMultiplier 1.0, then another at
                                  4.0 (the default): the second takes 3x..5x the ticks of the first (walk time included).
       Owed, not staged here: the ice melter filling a tank (power + tank + bill), and a raider fetching fill before filling
       (a raid at a trench, raid_ladder_live.py) -- both pinned offline in GroundClassChecks.
       The rows above run at digLabourMultiplier 1.0 (legacy work) so their 6000-tick waits hold.
       PIT_DIG_FIX_SAND_SLIDES_BACK_IN:
       GS_mud_refused             a Mud square refused like sand ("slide back in"), the same soil control accepted.
       DIG_SPOIL, added 2026-10-25:
       GS_rubble_cut_yields_gravel
                                  a Gravel (rubble) square: an ordered cut D0 -> D1 leaves exactly 1 RM_Gravel, no chunk.
       GS_gravel_recipe_takes_gravel
                                  Outer Rim's form-duracrete bill at a force-powered fabricator off the plot, 10 durasteel and
                                  1 RM_Gravel beside it: the colonist's real DoBill job eats the gravel and makes duracrete. Outer
                                  Rim absent -> UNMEASURED(SITE); duracrete made with the gravel untouched -> UNMEASURED (a chunk
                                  paid).
       --only GS_a,GS_b runs just those rows (the mine row alone can outrun a 540 s call).
EXPECT the eleven rows PASS.
LIES   a job never taken or a cut never made measures nothing -> UNMEASURED(SITE); spoil already lying there is excluded by a
       before/after stack diff; four walls that all drop a chunk prove nothing about a miss -> UNMEASURED(MOD), never PASS;
       a deployed DLL without the gravel build has no RM_Gravel setting -> UNMEASURED(HARNESS).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import shovel_stage  # noqa: E402
import work_bar  # noqa: E402
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
MELTER = "RimMandrake.FlowWorks.RM_IceMelter"
ITEM = "DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY"
GRAVEL = "RM_Gravel"
ROCK_TERRAIN, ROCK_WALL, ROCK_CHUNK = "Granite_Rough", "Granite", "ChunkGranite"
SLIDE_WORDS = "slide back in"
ROWS = ("GS_sand_refused", "GS_fill_costs_one_gravel", "GS_rock_ground_cut_yields_gravel_or_chunk",
        "GS_mined_rock_miss_yields_gravel", "GS_ice_cut_yields_crushed_ice", "GS_crushed_ice_melts_to_water",
        "GS_crushed_ice_stack_thaws_one_at_a_time", "GS_dig_labour_multiplier_scales_the_cut", "GS_mud_refused", "GS_rubble_cut_yields_gravel",
        "GS_gravel_recipe_takes_gravel")
ITEM_PIT = "PIT_DIG_FIX_SAND_SLIDES_BACK_IN"
ITEM_ICE, ITEM_LABOUR = "ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN", "DIG_FILL_TUNE_HOURS_OF_SHOVEL_WORK"
ITEM_MELT = "ICE_MELT_TAME_STACK_FLOOD"
ROW_ITEM = {"GS_ice_cut_yields_crushed_ice": ITEM_ICE, "GS_crushed_ice_melts_to_water": "ICE_YIELD_DECIDE_ONE_CUT_FOUR_NOTCHES",
            "GS_crushed_ice_stack_thaws_one_at_a_time": ITEM_MELT,
            "GS_dig_labour_multiplier_scales_the_cut": ITEM_LABOUR, "GS_mud_refused": ITEM_PIT}
MUD_TERRAIN, RUBBLE_TERRAIN = "Mud", "Gravel"
# GS_gravel_recipe_takes_gravel: Outer Rim's duracrete (one of RM_Gravel's mod-extension recipes) at its powered fabricator
FAB, FAB_GIVER, FAB_RECIPE = "OuterRim_HypertechFabricator", "DoBills_OuterRim_HypertechFabricator", "OuterRim_DuracreteCrafting"
FAB_OTHER, FAB_PRODUCT = ("OuterRim_Durasteel", 10), "OuterRim_Duracrete"
ICE, ICE_TERRAIN, MELT_DL = "RM_CrushedIce", "Ice", 10000   # one notch (ICE_YIELD_DECIDE_ONE_CUT_FOUR_NOTCHES)
LABOUR_RATIO = (3.0, 5.0)
RUN_SETTINGS = {"sandMudSlidesBackEnabled": True, "digSpoilEnabled": True, "fillCostsSpoilEnabled": True,
                "mineGravelEnabled": True, "gravelRecipesEnabled": True, "digRockGroundEnabled": True,
                "digRockChunksEnabled": True, "digRockChunkMultiplier": 1.0, "digDeepStoneEnabled": False,
                "digFindsEnabled": False, "digCostRisesWithDepth": False,
                "iceDigEnabled": True, "digLabourMultiplier": 1.0,
                # rock, rubble and ice cuts cost digRockWorkMultiplier x the work (default 4): 12,800 work outruns the 6000-tick
                # waits (2026-10-25: the ice cut never landed). These rows judge the yield, not the time: x1.
                "digRockWorkMultiplier": 1.0}


class MeasureError(Exception):
    """A bridge read that failed: the row it feeds is UNMEASURED(HARNESS), never judged on an empty answer."""


def things_of(resp):
    """list_things rows, or MeasureError when the call failed (an empty plot reads [] only on success)."""
    if not isinstance(resp, dict) or resp.get("success") is False or not isinstance(resp.get("things"), list):
        raise MeasureError("list_things failed: %s" % str(resp)[:160])
    return resp["things"]


def job_gate(probe, order, job_def):
    """Same idiom as deep_stone_live.job_gate: the work giver must hand this pawn job_def on the cell, then the exact JobDef is
    ORDERED (no wait for the AI scan). Returns (ok, why)."""
    wg, pw = (probe or {}).get("workGiver") or {}, (probe or {}).get("pawn") or {}
    if not (probe or {}).get("success"):
        return False, "flowworks_job_probe unavailable or refused: %s" % str((probe or {}).get("message") or probe)[:160]
    if (probe or {}).get("designationPresent") is not True:
        return False, "no designation at the cell"
    if pw.get("workTypeDisabled") is True:
        return False, "the colonist has Mining disabled"
    if wg.get("hasJobOnCell") is not True or wg.get("jobDef") != job_def:
        return False, "the work giver hands this pawn no %s (shouldSkip=%s hasJobOnCell=%s jobDef=%s)" % (
            job_def, wg.get("shouldSkip"), wg.get("hasJobOnCell"), wg.get("jobDef"))
    if not (order or {}).get("accepted"):
        return False, "ordered_job refused: %s" % str((order or {}).get("note") or (order or {}).get("error") or order)[:160]
    return True, "ordered"


def sand_verdict(sand_probe, soil_probe):
    """GS_sand_refused. The soil control must be accepted, or the designator reading is blind -> UNMEASURED."""
    sd = (sand_probe or {}).get("designator") or {}
    kd = (soil_probe or {}).get("designator") or {}
    if not (sand_probe or {}).get("success") or not (soil_probe or {}).get("success"):
        return "UNMEASURED", "a designator probe failed"
    if kd.get("accepted") is not True:
        return "UNMEASURED", "the soil control was refused too (%s): the reading cannot tell sand apart" % kd.get("reason")
    if sd.get("accepted") is False and SLIDE_WORDS in str(sd.get("reason") or ""):
        return "PASS", "sand refused: %s" % sd.get("reason")
    return "FAIL", "sand accepted=%s reason=%s" % (sd.get("accepted"), sd.get("reason"))


def stacks(things, defs):
    """Total stackCount per def over list_things rows."""
    out = {d: 0 for d in defs}
    for t in things or []:
        d = t.get("def")
        if d in out:
            out[d] += int(t.get("stackCount") or 1)
    return out


def spoil_delta(before, after):
    """New gravel and chunks between two stacks() reads (negative = spent)."""
    return {d: after.get(d, 0) - before.get(d, 0) for d in set(before) | set(after)}


def cut_verdict(delta, depth1=1):
    """GS_rock_ground_cut_yields_gravel_or_chunk: one cut D0 -> D1 and exactly one new spoil item, gravel or chunk."""
    g, ch = delta.get(GRAVEL, 0), delta.get(ROCK_CHUNK, 0)
    if depth1 == 1 and (g, ch) in ((1, 0), (0, 1)):
        return "PASS"
    return "FAIL"


def mine_verdict(per_wall, walls):
    """GS_mined_rock_miss_yields_gravel over [(gravel_delta, chunk_delta)] for the walls actually mined, of `walls` placed.
    Any bad yield is FAIL; PASS needs every wall measured and at least one miss seen."""
    if any((g, ch) not in ((1, 0), (0, 1)) for g, ch in per_wall):
        return "FAIL"
    if len(per_wall) < walls or not any(g == 1 for g, _ in per_wall):
        return "UNMEASURED"
    return "PASS"


def ice_cut_verdict(delta, depth1=1):
    """One cut through ice ground: exactly one crushed ice, nothing else."""
    if depth1 != 1:
        return "FAIL"
    return "PASS" if delta.get(ICE, 0) == 1 and not delta.get(GRAVEL) and not delta.get(ROCK_CHUNK) else "FAIL"


def melt_verdict(gone, ledger0, ledger1):
    """The ice is gone and the world took exactly MELT_DL more (spilled + into water + nearby)."""
    if not gone or ledger0 is None or ledger1 is None:
        return "UNMEASURED"
    return "PASS" if sum(ledger1[:3]) - sum(ledger0[:3]) == MELT_DL else "FAIL"


def thaw_verdict(left_after_first, ledger0, ledger1, ledger2):
    """ICE_MELT_TAME_STACK_FLOOD: a stack of 2 melts one at a time. left_after_first is the stack left when the first
    melt was seen (1 = one pile; 0 = the whole stack at once, the old flood); ledger1 at that moment, ledger2 when the
    second is gone (None: not seen)."""
    if left_after_first is None or ledger0 is None or ledger1 is None:
        return "UNMEASURED"
    if left_after_first != 1 or sum(ledger1[:3]) - sum(ledger0[:3]) != MELT_DL:
        return "FAIL"
    if ledger2 is None:
        return "UNMEASURED"
    return "PASS" if sum(ledger2[:3]) - sum(ledger0[:3]) == 2 * MELT_DL else "FAIL"


def labour_verdict(t1, t4):
    if not t1 or not t4:
        return "UNMEASURED"
    return "PASS" if LABOUR_RATIO[0] <= t4 / float(t1) <= LABOUR_RATIO[1] else "FAIL"


def parse_ledger(resp):
    try:
        v = (resp or {}).get("result")
        return [int(x) for x in str(v).split(";")]
    except (TypeError, ValueError):
        return None


def _same_number(a, b):
    try:
        return abs(float(a) - float(b)) < 1e-6
    except (TypeError, ValueError):
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--only", default="", help="comma-separated row ids to run (default: every row)")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "gravel_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "gravel_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ROW_ITEM.get(rid, ITEM), "detail": det})
        print("%-44s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:600]), flush=True)
        save()

    only = {r_.strip() for r_ in a.only.split(",") if r_.strip()}
    if only - set(ROWS):
        print("unknown row ids: %s" % sorted(only - set(ROWS)), flush=True)
        return 2

    def want(*rids):
        return not only or bool(only & set(rids))

    def unmeasured_rest(cls, why):
        done = {r["id"] for r in rows}
        for rid in ROWS:
            if rid not in done and want(rid):
                row(rid, "UNMEASURED", cls, {"why": why})

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    def sget(f):
        return (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f) or {}).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v)) or {"success": False}

    def things(x, z, w, h, def_name=None):
        kw = {"rect": "%d,%d,%d,%d" % (x, z, w, h), "limit": 300}
        if def_name:
            kw["defName"] = def_name
        return things_of(B.call("jawa/list_things", **kw))

    def spoil_near(cx, cz, r):
        return stacks(things(cx - r, cz - r, 2 * r + 1, 2 * r + 1), (GRAVEL, ROCK_CHUNK, ICE))

    def depth(cx, cz):
        return (B.call("jawa/flowworks_excavation_drive", x=cx, z=cz, deepenLevels=0, setFill=-1) or {}).get("depth")

    def cut_once(cx, cz, terrain, limit=6000):
        """Order one cut at (cx, cz) on `terrain`; -> (ticks or None, depth after, detail)."""
        B.call("jawa/set_terrain", terrainDef=terrain, x=cx, z=cz)
        d0 = depth(cx, cz)
        B.call("jawa/designate_batch", action="add", designation="RM_DigCanal", rect="%d,%d,1,1" % (cx, cz))
        pr = B.call("jawa/flowworks_job_probe", x=cx, z=cz, kind="dig", pawnId=pid) or {}
        od = B.call("jawa/ordered_job", pawnId=pid, jobDef="RM_DigCanalJob", targetAX=cx, targetAZ=cz, waitTicks=0) or {}
        ok_, why_ = job_gate(pr, od, "RM_DigCanalJob")
        det_ = {"terrain": pr.get("terrain"), "depth0": d0}
        if pr.get("terrain") != terrain or d0 != 0 or not ok_:
            return None, d0, dict(det_, why="not %s at D0 or the dig job was not taken: %s" % (terrain, why_))
        at_, d1_ = wait_depth(cx, cz, d0, limit)
        return at_, d1_, det_

    def wait_depth(cx, cz, d0, limit=6000):
        t = 0
        while t < limit:
            step(250)
            t += 250
            d = depth(cx, cz)
            if d not in (None, d0):
                return t, d
        return None, depth(cx, cz)

    ox, oz = (int(v) for v in a.origin.split(","))
    sand, soil = (ox + 2, oz + 12), (ox + 4, oz + 12)
    fill, fill_mat = (ox + 10, oz + 12), (ox + 13, oz + 12)
    cut = (ox + 5, oz + 6)
    ice_cut, melt_at, thaw_at = (ox + 9, oz + 6), (ox + 13, oz + 6), (ox + 15, oz + 9)
    lab1, lab4 = (ox + 3, oz + 15), (ox + 7, oz + 15)
    mud, rubble = (ox + 6, oz + 12), (ox + 1, oz + 9)
    fab_at = (ox + 21, oz + 5)   # off the 17x17 plot: its durasteel and gravel never enter the plot's stack counts
    walls = [(ox + 1 + 4 * i, oz + 1) for i in range(4)]
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        unmeasured_rest("HARNESS", "no game in Playing")
        return 2
    # HARNESS (2026-10-25): a lapsed companion_profile.json grant refuses every test-only tool (flowworks_job_probe,
    # static_call) and the rows read UNMEASURED(SITE) as if the cut never happened. Refuse up front instead.
    prof = (B.call("jawa/companion_handshake") or {}).get("effectiveProfile")
    if prof != "test":
        unmeasured_rest("HARNESS", "companion profile is %r, not 'test': renew companion_profile.json expiresUtc" % prof)
        return 2
    res["site_calm"] = V.site_calm(B)
    before = {k: sget(k) for k in RUN_SETTINGS}
    res["settings_before"] = before
    if any(v is None for v in before.values()):
        unmeasured_rest("HARNESS", "a setting is unreadable (deployed DLL older than the gravel build?)")
        return 2
    cids = []
    try:
        for k, v in RUN_SETTINGS.items():
            sset(k, v)
        got = {k: sget(k) for k in RUN_SETTINGS}
        res["settings_run"] = got
        off = {k: got[k] for k, v in RUN_SETTINGS.items() if str(got[k]).lower() != str(v).lower()
               and not _same_number(got[k], v)}
        if off:
            unmeasured_rest("HARNESS", "settings did not take: %s" % off)
            return 2
        rect = (ox, oz, 17, 17)
        B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
        # HARNESS (2026-10-25): ProofResetRect leaves designations; a previous run's dig squares were taken up by the AI
        # colonist on its own, and the x4 labour cut was then already under way at x1 work when ordered (ratio 0.875)
        for des_ in ("RM_DigCanal", "RM_FillInCanal", "Mine"):
            B.call("jawa/designate_batch", action="remove", designation=des_, rect="%d,%d,%d,%d" % rect)
        site_rows = []
        V.prepare_site(B, rect, site_rows, "gravel_site")
        if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
            unmeasured_rest("SITE", "site not prepared: %s" % str(site_rows[:2])[:200])
            return 2
        if things(ox, oz, 17, 17, GRAVEL):
            unmeasured_rest("SITE", "gravel already lies on the plot after the reset")
            return 2
        for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
            if not p.get("dead") and p.get("isPlayer"):
                B.call("jawa/pawn_force_incapacitate", pawn=p.get("id"), action="vanish")
        # HARNESS (run7 2026-10-25): a random Colonist can arrive DOWNED (an 80-year-old Gestor never stood up, so the fill and
        # cut rows waited 6000 ticks on nobody); a downed one is vanished and re-rolled, never worked.
        cids, rolls = [], []
        for _ in range(6):
            r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=ox + 8, z=oz + 9, faction="player", count=1) or {}
            got = [p_.get("id") for p_ in r.get("pawns") or [] if p_.get("id")]
            if not got:
                break
            step(5)
            st_ = {p_.get("id"): p_ for p_ in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []}.get(got[0]) or {}
            # HARNESS (2026-10-25): a roll can also come incapable of Mining (every dig row then read UNMEASURED); the probe's
            # pawn block says so before any row runs, and that roll is re-rolled too
            nomine = ((B.call("jawa/flowworks_job_probe", x=soil[0], z=soil[1], kind="dig", pawnId=got[0]) or {})
                      .get("pawn") or {}).get("workTypeDisabled") is True
            rolls.append({"id": got[0], "downed": st_.get("downed"), "dead": st_.get("dead"), "miningDisabled": nomine})
            if st_ and not st_.get("downed") and not st_.get("dead") and not nomine:
                cids = got
                break
            B.call("jawa/pawn_force_incapacitate", pawn=got[0], action="vanish", _answer=True)
        res["colonist_rolls"] = rolls
        if not cids:
            unmeasured_rest("HARNESS", "no colonist spawned: %s" % str(r)[:200])
            return 2
        for c_ in cids:
            B.call("jawa/set_pawn_skill", pawn=c_, skill="Mining", level=10, _answer=True)
            # one colonist, hauling off: nobody carries spoil out of the counted squares between polls
            bar_ok, bar_why = work_bar.set_all(B.call, c_, [("Mining", 1), ("Hauling", 0)])
            if not bar_ok:
                unmeasured_rest("HARNESS", "work bar did not take: %s" % bar_why)
                return 2
        # SHOVELS_BUILD_NO_DIGGING_BARE_HANDED: no shovel, no dig or fill job; stage one so these rows measure gravel
        shovel_bad = [w for w in (shovel_stage.give_shovel(B.call, c_) for c_ in cids) if not w[0]]
        if shovel_bad:
            unmeasured_rest("HARNESS", "shovel not staged: %s" % shovel_bad[0][1])
            return 2
        pid = cids[0]

        # 1. sand slides back in; the soil control beside it is accepted
        if want("GS_sand_refused"):
            B.call("jawa/set_terrain", terrainDef="Sand", x=sand[0], z=sand[1])
            sp = B.call("jawa/flowworks_job_probe", x=sand[0], z=sand[1], kind="dig", pawnId=pid) or {}
            kp = B.call("jawa/flowworks_job_probe", x=soil[0], z=soil[1], kind="dig", pawnId=pid) or {}
            st, why = sand_verdict(sp, kp)
            if sp.get("terrain") != "Sand":   # a set_terrain that did not take would judge the old ground as sand
                st, why = "UNMEASURED", "sand square reads %s, not Sand" % sp.get("terrain")
            row("GS_sand_refused", st, "HARNESS" if st == "UNMEASURED" else "MOD",
                {"why": why, "sand": sp.get("designator"), "soil": kp.get("designator")})

        # 1b. PIT_DIG: mud slides back in exactly as sand does (owner 2026-10-25 "you can't dig in sand or mud"); the same soil
        # control reads the instrument
        if want("GS_mud_refused"):
            B.call("jawa/set_terrain", terrainDef=MUD_TERRAIN, x=mud[0], z=mud[1])
            mp = B.call("jawa/flowworks_job_probe", x=mud[0], z=mud[1], kind="dig", pawnId=pid) or {}
            kp = B.call("jawa/flowworks_job_probe", x=soil[0], z=soil[1], kind="dig", pawnId=pid) or {}
            st, why = sand_verdict(mp, kp)
            if mp.get("terrain") != MUD_TERRAIN:
                st, why = "UNMEASURED", "mud square reads %s, not %s" % (mp.get("terrain"), MUD_TERRAIN)
            row("GS_mud_refused", st, "HARNESS" if st == "UNMEASURED" else "MOD",
                {"why": why, "mud": mp.get("designator"), "soil": kp.get("designator")})

        # 2. a fill costs one gravel
        if want("GS_fill_costs_one_gravel"):
            B.call("jawa/flowworks_excavation_drive", x=fill[0], z=fill[1], deepenLevels=1, setFill=-1)
            d0 = depth(*fill)
            des = B.call("jawa/designate_batch", action="add", designation="RM_FillInCanal", rect="%d,%d,1,1" % fill) or {}
            dry = B.call("jawa/flowworks_job_probe", x=fill[0], z=fill[1], kind="fillin", pawnId=pid) or {}
            B.call("rimworld/spawn_thing", defName=GRAVEL, stackCount=1, x=fill_mat[0], z=fill_mat[1])
            gv = things(fill_mat[0], fill_mat[1], 1, 1, GRAVEL)
            # WorkGiver_FillInCanal caches "has material" per pawn per TICK: a probe in the same paused tick as the dry probe
            # reads the dry answer back (run7: wetProbe hasJobOnCell False, true one tick on). Let a tick pass first.
            step(2)
            g0 = stacks(things(ox, oz, 17, 17, GRAVEL), (GRAVEL,))[GRAVEL]
            wet = B.call("jawa/flowworks_job_probe", x=fill[0], z=fill[1], kind="fillin", pawnId=pid) or {}
            det = {"depth0": d0, "designate": str(des)[:200], "dryProbe": str(dry.get("workGiver"))[:200],
                   "wetProbe": str(wet.get("workGiver"))[:200], "gravelBefore": g0}
            if d0 != 1 or not gv:
                row("GS_fill_costs_one_gravel", "UNMEASURED", "SITE", dict(det, why="no D1 pit or the gravel did not spawn"))
            else:
                order = B.call("jawa/ordered_job", pawnId=pid, jobDef="RM_FillInCanalJob", targetAX=fill[0], targetAZ=fill[1],
                               targetBId=gv[0].get("id"), count=1, waitTicks=0) or {}
                job_ok, job_why = job_gate(wet, order, "RM_FillInCanalJob")
                if not job_ok:
                    row("GS_fill_costs_one_gravel", "UNMEASURED", "SITE", dict(det, why="fill job not taken: " + job_why))
                else:
                    at, d1 = wait_depth(fill[0], fill[1], d0)
                    step(10)
                    g1 = stacks(things(ox, oz, 17, 17, GRAVEL), (GRAVEL,))[GRAVEL]
                    # the fetched stack is gone from the whole map, not merely hauled off the plot. A gravel still in a hand cannot
                    # fake this row: with fillCostsSpoilEnabled read back on, D1 -> D0 needs paid credit, and only the tip toil
                    # pays, destroying what it tips.
                    spent = gv[0].get("id") not in {t.get("id") for t in things_of(B.call("jawa/list_things", defName=GRAVEL, limit=5000))}
                    det.update(depth1=d1, filledAt=at, gravelAfter=g1, gravelDestroyed=spent)
                    if at is None:
                        row("GS_fill_costs_one_gravel", "UNMEASURED", "SITE", dict(det, why="no fill in 6000 ticks"))
                    else:
                        # the dry probe is detail only: chunks lying anywhere on the map pay for a fill, so "no job without
                        # material" cannot be isolated here (GroundClassChecks pins the rule offline)
                        good = d1 == 0 and g0 - g1 == 1 and spent
                        row("GS_fill_costs_one_gravel", "PASS" if good else "FAIL", "MOD", det)

        # 3. a cut in rock ground leaves one gravel or one chunk
        if want("GS_rock_ground_cut_yields_gravel_or_chunk"):
            B.call("jawa/set_terrain", terrainDef=ROCK_TERRAIN, x=cut[0], z=cut[1])
            s0, c0 = spoil_near(cut[0], cut[1], 3), depth(*cut)
            des = B.call("jawa/designate_batch", action="add", designation="RM_DigCanal", rect="%d,%d,1,1" % cut) or {}
            probe = B.call("jawa/flowworks_job_probe", x=cut[0], z=cut[1], kind="dig", pawnId=pid) or {}
            order = B.call("jawa/ordered_job", pawnId=pid, jobDef="RM_DigCanalJob", targetAX=cut[0], targetAZ=cut[1], waitTicks=0) or {}
            job_ok, job_why = job_gate(probe, order, "RM_DigCanalJob")
            det = {"depth0": c0, "spoilBefore": s0, "designate": str(des)[:200], "probe": str(probe.get("designator"))[:200]}
            if probe.get("terrain") != ROCK_TERRAIN:
                job_ok, job_why = False, "cut square reads %s, not %s" % (probe.get("terrain"), ROCK_TERRAIN)
            if c0 != 0 or not job_ok:
                row("GS_rock_ground_cut_yields_gravel_or_chunk", "UNMEASURED", "SITE",
                    dict(det, why="not at D0 or the dig job was not taken: " + job_why))
            else:
                at, c1 = wait_depth(cut[0], cut[1], c0)
                step(10)
                s1 = spoil_near(cut[0], cut[1], 3)
                delta = spoil_delta(s0, s1)
                det.update(depth1=c1, cutAt=at, spoilAfter=s1, delta=delta)
                if at is None:
                    row("GS_rock_ground_cut_yields_gravel_or_chunk", "UNMEASURED", "SITE", dict(det, why="no cut in 6000 ticks"))
                else:
                    row("GS_rock_ground_cut_yields_gravel_or_chunk", cut_verdict(delta, c1), "MOD", det)

        # 3b. a cut in rubble ground (vanilla Gravel terrain, RM_GroundClassMath.RubbleTerrains) leaves exactly one gravel
        if want("GS_rubble_cut_yields_gravel"):
            s0 = spoil_near(rubble[0], rubble[1], 2)
            at, r1, det = cut_once(rubble[0], rubble[1], RUBBLE_TERRAIN)
            step(10)
            delta = spoil_delta(s0, spoil_near(rubble[0], rubble[1], 2))
            det.update(depth1=r1, cutAt=at, delta=delta)
            if at is None:
                row("GS_rubble_cut_yields_gravel", "UNMEASURED", "SITE", dict(det, why=det.get("why") or "no cut in 6000 ticks"))
            else:
                good = r1 == 1 and delta.get(GRAVEL, 0) == 1 and delta.get(ROCK_CHUNK, 0) == 0
                row("GS_rubble_cut_yields_gravel", "PASS" if good else "FAIL", "MOD", det)

        # 4. mining a natural rock wall: a missed chunk leaves gravel
        if want("GS_mined_rock_miss_yields_gravel"):
            per_wall, wall_log = [], []
            for wx, wz in walls:
                B.call("rimworld/spawn_thing", defName=ROCK_WALL, stackCount=1, x=wx, z=wz)
                w = things(wx, wz, 1, 1, ROCK_WALL)
                if not w:
                    wall_log.append({"at": (wx, wz), "why": "wall did not spawn"})
                    continue
                b0 = spoil_near(wx, wz, 1)
                B.call("jawa/designate_batch", action="add", designation="Mine", rect="%d,%d,1,1" % (wx, wz))
                order = B.call("jawa/ordered_job", pawnId=pid, jobDef="Mine", targetAId=w[0].get("id"), waitTicks=0) or {}
                if not order.get("accepted"):
                    wall_log.append({"at": (wx, wz), "why": "Mine order refused: %s" % str(order)[:160]})
                    continue
                t = 0
                while t < 6000 and things(wx, wz, 1, 1, ROCK_WALL):
                    step(250)
                    t += 250
                step(10)
                if things(wx, wz, 1, 1, ROCK_WALL):
                    wall_log.append({"at": (wx, wz), "why": "not mined in 6000 ticks"})
                    continue
                dl = spoil_delta(b0, spoil_near(wx, wz, 1))
                per_wall.append((dl.get(GRAVEL, 0), dl.get(ROCK_CHUNK, 0)))
                wall_log.append({"at": (wx, wz), "minedAt": t, "delta": dl})
            mv = mine_verdict(per_wall, len(walls))
            why = {"UNMEASURED": "a wall went unmeasured, or every wall dropped a chunk (the miss path never ran)"}.get(mv)
            row("GS_mined_rock_miss_yields_gravel", mv, "SITE" if not per_wall else "MOD",
                {"walls": wall_log, "perWall": per_wall, "why": why})

        # 5. ICE_DIG: a cut through ice ground leaves one crushed ice
        if want("GS_ice_cut_yields_crushed_ice"):
            s0 = spoil_near(ice_cut[0], ice_cut[1], 3)
            at, i1, det = cut_once(ice_cut[0], ice_cut[1], ICE_TERRAIN)
            step(10)
            delta = spoil_delta(s0, spoil_near(ice_cut[0], ice_cut[1], 3))
            det.update(depth1=i1, cutAt=at, delta=delta)
            if at is None:
                row("GS_ice_cut_yields_crushed_ice", "UNMEASURED", "SITE", dict(det, why=det.get("why") or "no cut in 6000 ticks"))
            else:
                row("GS_ice_cut_yields_crushed_ice", ice_cut_verdict(delta, i1), "MOD", det)

        # 6. ICE_DIG: loose crushed ice melts into the notch of water its cut removed, conserved. Row 5's crushed ice is cleared
        # first: melting while this row measures, it would double the ledger delta.
        if want("GS_crushed_ice_melts_to_water"):
            for t5 in things(ice_cut[0] - 4, ice_cut[1] - 4, 9, 9, ICE):
                B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t5.get("x"), t5.get("z")), categories="Item")
            B.call("rimworld/spawn_thing", defName=ICE, stackCount=1, x=melt_at[0], z=melt_at[1])
            lg0 = parse_ledger(B.call("jawa/static_call", type=MELTER, method="ProofMeltLedger", args=""))
            placed = things(melt_at[0], melt_at[1], 1, 1, ICE)
            t = 0
            while placed and t < 15000 and things(melt_at[0], melt_at[1], 1, 1, ICE):
                step(500)
                t += 500
            gone = bool(placed) and not things(melt_at[0], melt_at[1], 1, 1, ICE)
            lg1 = parse_ledger(B.call("jawa/static_call", type=MELTER, method="ProofMeltLedger", args=""))
            mv = melt_verdict(gone, lg0, lg1)
            det = {"spawned": bool(placed), "gone": gone, "ticks": t, "ledger0": lg0, "ledger1": lg1}
            why = None if mv != "UNMEASURED" else ("no crushed ice spawned" if not placed else "ledger unreadable (DLL older?)"
                                                    if lg0 is None or lg1 is None else "not melted in 15000 ticks (cold site?)")
            row("GS_crushed_ice_melts_to_water", mv, "MOD" if mv != "UNMEASURED" else ("HARNESS" if placed and gone else "SITE"),
                dict(det, why=why))

        # 6b. ICE_MELT_TAME_STACK_FLOOD: a stack thaws one pile at a time (row 5's and row 6's ice is cleared first, also when
        # this row runs alone under --only: one melt at a time on the ledgers)
        if want("GS_crushed_ice_stack_thaws_one_at_a_time"):
            for t6 in things(ice_cut[0] - 4, ice_cut[1] - 4, 9, 9, ICE) + things(melt_at[0] - 1, melt_at[1] - 1, 3, 3, ICE):
                B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t6.get("x"), t6.get("z")), categories="Item")
            B.call("rimworld/spawn_thing", defName=ICE, stackCount=2, x=thaw_at[0], z=thaw_at[1])
            cool0 = (B.call("jawa/static_call", type=MELTER, method="ProofMeltCooling", args="") or {}).get("result")
            lg0 = parse_ledger(B.call("jawa/static_call", type=MELTER, method="ProofMeltLedger", args=""))

            def left():
                return stacks(things(thaw_at[0], thaw_at[1], 1, 1, ICE), (ICE,)).get(ICE, 0)

            n0, t, left1, lg1, lg2 = left(), 0, None, None, None
            while n0 == 2 and t < 15000:
                step(500)
                t += 500
                n = left()
                if n < 2:
                    left1 = n
                    lg1 = parse_ledger(B.call("jawa/static_call", type=MELTER, method="ProofMeltLedger", args=""))
                    break
            t1 = t
            while left1 == 1 and t < t1 + 15000 and left() > 0:
                step(500)
                t += 500
            if left1 == 1 and left() == 0:
                lg2 = parse_ledger(B.call("jawa/static_call", type=MELTER, method="ProofMeltLedger", args=""))
            cool1 = (B.call("jawa/static_call", type=MELTER, method="ProofMeltCooling", args="") or {}).get("result")
            tv = thaw_verdict(left1, lg0, lg1, lg2)
            det = {"spawned": n0, "leftAfterFirst": left1, "firstAt": t1, "ticks": t, "ledger0": lg0, "ledger1": lg1,
                   "ledger2": lg2, "cooling0": cool0, "cooling1": cool1}
            why = None if tv != "UNMEASURED" else ("stack of 2 not spawned" if n0 != 2 else "ledger unreadable (DLL older?)"
                                                    if lg0 is None else "a pile did not melt in 15000 ticks (cold site?)")
            row("GS_crushed_ice_stack_thaws_one_at_a_time", tv, "MOD" if tv != "UNMEASURED" else ("HARNESS" if n0 != 2 or lg0 is None else "SITE"),
                dict(det, why=why))

        # 7. DIG_FILL: the labour multiplier scales a soil cut (x1, then x4 = the default)
        if want("GS_dig_labour_multiplier_scales_the_cut"):
            t1, _, det1 = cut_once(lab1[0], lab1[1], "Soil", 6000)
            sset("digLabourMultiplier", 4.0)
            t4, _, det4 = cut_once(lab4[0], lab4[1], "Soil", 40000)
            sset("digLabourMultiplier", 1.0)
            lv = labour_verdict(t1, t4)
            row("GS_dig_labour_multiplier_scales_the_cut", lv, "MOD" if lv != "UNMEASURED" else "SITE",
                {"x1": det1, "x4": det4, "ticksX1": t1, "ticksX4": t4, "ratio": (t4 / float(t1)) if t1 and t4 else None,
                 "want": LABOUR_RATIO})

        # 8. DIG_SPOIL: gravel stands in for a stone chunk in a patched recipe -- a real bill, done by the colonist, eats the
        # gravel and makes the product. A product made while the gravel still lies there means a chunk paid: UNMEASURED.
        if want("GS_gravel_recipe_takes_gravel"):
            det = {"recipe": FAB_RECIPE}
            if not (B.call("jawa/get_def", defName=FAB_RECIPE, defType="RecipeDef") or {}).get("success"):
                row("GS_gravel_recipe_takes_gravel", "UNMEASURED", "SITE", dict(det, why="Outer Rim not loaded: no recipe"))
            else:
                B.call("jawa/research_bulk", mode="finish_all")
                bb = B.call("jawa/build_batch", ops="%s:%d,%d,0" % (FAB, fab_at[0], fab_at[1]), faction="player") or {}
                fab = things(fab_at[0] - 2, fab_at[1] - 2, 5, 5, FAB)
                if not fab:
                    row("GS_gravel_recipe_takes_gravel", "UNMEASURED", "SITE", dict(det, why="no fabricator: %s" % str(bb)[:200]))
                else:
                    fid = fab[0].get("id")
                    det["power"] = (B.call("jawa/power_net", thing=fid, forcePowerOn=True) or {}).get("powerOnAfter")
                    B.call("rimworld/spawn_thing", defName=FAB_OTHER[0], stackCount=FAB_OTHER[1], x=fab_at[0], z=fab_at[1] - 3)
                    B.call("rimworld/spawn_thing", defName=GRAVEL, stackCount=1, x=fab_at[0] + 1, z=fab_at[1] - 3)
                    gv = things(fab_at[0] + 1, fab_at[1] - 3, 1, 1, GRAVEL)
                    det["bill"] = str(B.call("jawa/bill_add", giverId=fid, recipe=FAB_RECIPE, repeatMode="repeatcount",
                                             repeatCount=1, storeMode="dropfloor"))[:200]
                    # HARNESS (2026-10-25): WorkGiver_DoBill first hands out HaulToCell when something lies on the bench's
                    # squares (billOnJob null); the bill job comes on a later ask, once that haul is done
                    tries = []
                    for _ in range(4):
                        db = B.call("jawa/do_bill_now", pawnId=pid, billGiverId=fid, workGiverDef=FAB_GIVER, waitTicks=60) or {}
                        tries.append(db.get("jobDefFromJobOnThing"))
                        if db.get("billOnJob"):
                            break
                        step(600)
                    det["doBill"] = {k: db.get(k) for k in ("success", "accepted", "billOnJob", "message")}
                    det["doBillTries"] = tries
                    made, t = [], 0
                    while gv and db.get("billOnJob") and t < 12000 and not made:
                        step(500)
                        t += 500
                        made = things(fab_at[0] - 3, fab_at[1] - 4, 7, 8, FAB_PRODUCT)   # near this bench only
                    alive = gv and gv[0].get("id") in {x.get("id") for x in things_of(
                        B.call("jawa/list_things", defName=GRAVEL, limit=5000))}
                    det.update(ticks=t, product=[(m.get("x"), m.get("z"), m.get("stackCount")) for m in made],
                               gravelSpawned=bool(gv), gravelStillThere=alive)
                    if not gv or not db.get("billOnJob") or not made:
                        row("GS_gravel_recipe_takes_gravel", "UNMEASURED", "SITE",
                            dict(det, why="no gravel, bill job refused, or nothing made in 12000 ticks"))
                    elif alive:
                        row("GS_gravel_recipe_takes_gravel", "UNMEASURED", "SITE", dict(det, why="made, but a chunk paid"))
                    else:
                        row("GS_gravel_recipe_takes_gravel", "PASS", "MOD", det)

        return 0 if all(r["status"] == "PASS" for r in rows) else 1
    except MeasureError as e:
        unmeasured_rest("HARNESS", str(e))
        return 2
    finally:
        # the run's colonist is LEFT standing: every other colonist was vanished above, and vanishing the last one ends the
        # game ("Game Over" letter, run7 2026-10-25) under whatever runs next on this map
        for k, v in before.items():
            if v is not None:
                try:
                    sset(k, v)
                except Exception as ex:  # noqa: BLE001 -- restore every field, whatever one throws
                    print("RESTORE %s failed: %s" % (k, ex), flush=True)
        try:
            bad = {k: sget(k) for k, v in before.items() if v is not None and str(sget(k)).lower() != str(v).lower()}
        except Exception as ex:  # noqa: BLE001
            bad = {"readback": str(ex)}
        res["settings_restore_failed"] = bad
        if bad:
            print("SETTINGS NOT RESTORED: %s" % bad, flush=True)
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()


if __name__ == "__main__":
    sys.exit(main())
