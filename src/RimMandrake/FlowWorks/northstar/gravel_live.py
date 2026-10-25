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
EXPECT the four rows PASS.
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
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
ITEM = "DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY"
GRAVEL = "RM_Gravel"
ROCK_TERRAIN, ROCK_WALL, ROCK_CHUNK = "Granite_Rough", "Granite", "ChunkGranite"
SLIDE_WORDS = "slide back in"
ROWS = ("GS_sand_refused", "GS_fill_costs_one_gravel", "GS_rock_ground_cut_yields_gravel_or_chunk",
        "GS_mined_rock_miss_yields_gravel")
RUN_SETTINGS = {"sandMudSlidesBackEnabled": True, "digSpoilEnabled": True, "fillCostsSpoilEnabled": True,
                "mineGravelEnabled": True, "gravelRecipesEnabled": True, "digRockGroundEnabled": True,
                "digRockChunksEnabled": True, "digRockChunkMultiplier": 1.0, "digDeepStoneEnabled": False,
                "digFindsEnabled": False, "digCostRisesWithDepth": False}


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
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-44s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:600]), flush=True)
        save()

    def unmeasured_rest(cls, why):
        done = {r["id"] for r in rows}
        for rid in ROWS:
            if rid not in done:
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
        return stacks(things(cx - r, cz - r, 2 * r + 1, 2 * r + 1), (GRAVEL, ROCK_CHUNK))

    def depth(cx, cz):
        return (B.call("jawa/flowworks_excavation_drive", x=cx, z=cz, deepenLevels=0, setFill=-1) or {}).get("depth")

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
    walls = [(ox + 1 + 4 * i, oz + 1) for i in range(4)]
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        unmeasured_rest("HARNESS", "no game in Playing")
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
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=ox + 8, z=oz + 9, faction="player", count=1) or {}
        cids = [p_.get("id") for p_ in r.get("pawns") or [] if p_.get("id")]
        if not cids:
            unmeasured_rest("HARNESS", "no colonist spawned: %s" % str(r)[:200])
            return 2
        for c_ in cids:
            B.call("jawa/set_pawn_skill", pawn=c_, skill="Mining", level=10, _answer=True)
            B.call("jawa/set_work_priority", pawnId=c_, workType="Mining", priority=1)
            # one colonist, hauling off: nobody carries spoil out of the counted squares between polls
            B.call("jawa/set_work_priority", pawnId=c_, workType="Hauling", priority=0)
        pid = cids[0]

        # 1. sand slides back in; the soil control beside it is accepted
        B.call("jawa/set_terrain", terrainDef="Sand", x=sand[0], z=sand[1])
        sp = B.call("jawa/flowworks_job_probe", x=sand[0], z=sand[1], kind="dig", pawnId=pid) or {}
        kp = B.call("jawa/flowworks_job_probe", x=soil[0], z=soil[1], kind="dig", pawnId=pid) or {}
        st, why = sand_verdict(sp, kp)
        row("GS_sand_refused", st, "HARNESS" if st == "UNMEASURED" else "MOD",
            {"why": why, "sand": sp.get("designator"), "soil": kp.get("designator")})

        # 2. a fill costs one gravel
        B.call("jawa/flowworks_excavation_drive", x=fill[0], z=fill[1], deepenLevels=1, setFill=-1)
        d0 = depth(*fill)
        des = B.call("jawa/designate_batch", action="add", designation="RM_FillInCanal", rect="%d,%d,1,1" % fill) or {}
        dry = B.call("jawa/flowworks_job_probe", x=fill[0], z=fill[1], kind="fillin", pawnId=pid) or {}
        B.call("rimworld/spawn_thing", defName=GRAVEL, stackCount=1, x=fill_mat[0], z=fill_mat[1])
        gv = things(fill_mat[0], fill_mat[1], 1, 1, GRAVEL)
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
        B.call("jawa/set_terrain", terrainDef=ROCK_TERRAIN, x=cut[0], z=cut[1])
        s0, c0 = spoil_near(cut[0], cut[1], 3), depth(*cut)
        des = B.call("jawa/designate_batch", action="add", designation="RM_DigCanal", rect="%d,%d,1,1" % cut) or {}
        probe = B.call("jawa/flowworks_job_probe", x=cut[0], z=cut[1], kind="dig", pawnId=pid) or {}
        order = B.call("jawa/ordered_job", pawnId=pid, jobDef="RM_DigCanalJob", targetAX=cut[0], targetAZ=cut[1], waitTicks=0) or {}
        job_ok, job_why = job_gate(probe, order, "RM_DigCanalJob")
        det = {"depth0": c0, "spoilBefore": s0, "designate": str(des)[:200], "probe": str(probe.get("designator"))[:200]}
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

        # 4. mining a natural rock wall: a missed chunk leaves gravel
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
        return 0 if all(r["status"] == "PASS" for r in rows) else 1
    except MeasureError as e:
        unmeasured_rest("HARNESS", str(e))
        return 2
    finally:
        for c_ in cids:
            B.call("jawa/pawn_force_incapacitate", pawn=c_, action="vanish", _answer=True)
        for k, v in before.items():
            if v is not None:
                sset(k, v)
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()


if __name__ == "__main__":
    sys.exit(main())
