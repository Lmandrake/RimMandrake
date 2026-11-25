#!/usr/bin/env python3
"""prove_ordered_rescue.py - the live proof of jawa/order, jawa/motive and the force record
(RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER). Page: design/specs/2026-11-23-bridge-v2/boundary.md
§THE ORDER THROUGH THE GIVER, THE MOTIVE, THE FORCE RECORD. Reading: design/specs/2026-11-23-bridge-v2/live/ordered_rescue/.

    python3 src/RimMandrake/rimflow/game_lock.py run ArchBig --for "ordered rescue proof" -- \\
        python.exe <clone>\\src\\RimMandrake\\bridgetools\\prove_ordered_rescue.py --host ArchBig

THE LOCK IS THE CALLER'S (python.exe, not WSL python, reaches the bridge). A TEST-profile game on a quicktest map that is
not canonical; it starts a quicktest map when none is loaded. It downs one colonist, builds one bed, spawns one hostile and
removes it again; the pawns stand where the quicktest put them. Five rows:
  R0 (the scene) another colonist rescues the downed victim to a bed (jawa/ordered_job Rescue): a humanlike is tended only
     in bed (WorkGiver_Tend.GoodLayingStatusForTend). A victim not in bed after the rescue is NO VERDICT;
  R1 a colonist ordered level=giver giver=DoctorTendToHumanlikes on the victim in bed tends the victim: the tend job ends
     Succeeded (SUCCESS). The rescue itself is no work order: DoctorRescue is directOrderable=false in 1.6 (Core
     WorkGivers.xml), and the player's rescue (FloatMenuOptionProvider_RescuePawn) builds a plain Rescue job with no work
     giver on it, which the job tap cannot tell from a raw one (measured on ArchBig 2026-11-25: "the giver is not
     directOrderable"). A tend through the float menu carries its WorkGiverDef, so the tap can check it;
  R2 the same order with the doctor not assigned to Doctor: given false with the float menu's reason (the option is
     offered and disabled, not absent), no tick spent;
  R3 jawa/motive on a hostile with no lord: refused NO_LORD;
  R4 the force level on the receipt is checked against the game: inside a jawa/run_until run with the pawns bound, the job
     tap's job_start row names the reply's `via` for level=giver (a work giver and a JobGiver), and for level=raw it names
     no giver; the session's force record says the level used (3, 3, 4);
  R5 a giver made to refuse (the target is a colonist who is not downed): given false, the reason, nothing started.
The wrong code that R4 must catch (GPT's): an executor that always starts a raw job and copies the declared level onto
the receipt. Then the job tap names the job queue, not the work giver.
Exit 0 every row PASS, 1 a row FAIL, 2 no verdict (no game, no stage, a refusal before any row)."""
import argparse
import datetime
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "rimflow"))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
sys.path.insert(0, HERE)

GIVER = "DoctorTendToHumanlikes"    # a directOrderable WorkGiverDef of Doctor (Core/Defs/WorkGiverDefs/WorkGivers.xml, RimSage)
NODE = "JobGiver_WanderColony"       # a ThinkNode_JobGiver with no target of its own
TEND_TICKS = 5000                    # the tend run; measured: 1500 ticks was short (ArchSmall 2026-11-25)
WORKTYPE = "Doctor"                  # the giver's work type
LINES = []


def log(s):
    LINES.append(s)
    print(s, flush=True)


# ------------------------------------------------------------------------------------------------ the judges (pure)
def judge_tap(rows, alias, reply, want_giver):
    """None when the first job_start of `alias` that the order made agrees with the reply, else why not. want_giver: the
    giver's name for a level-3 order; None for a raw order (the row must then name neither a work giver nor a JobGiver
    that the run asked)."""
    if not reply or not reply.get("success"):
        return "the order was refused: %s" % short(reply)
    if not reply.get("started"):
        return "the order started nothing: %s" % short(reply)
    job = str(reply.get("job") or "")
    mine = [r for r in rows if r.get("rec") == "job_start" and r.get("alias") == alias and job and r.get("job") == job]
    if not mine:
        return "no job_start row of %s for the reply's job %s (rows of %s: %s)" % (
            alias, job, alias, [(r.get("def"), r.get("giver")) for r in rows if r.get("rec") == "job_start" and r.get("alias") == alias][:6])
    g = mine[0].get("giver")
    if want_giver is not None:
        if reply.get("via") != want_giver:
            return "the reply's via is %r, the order asked %r" % (reply.get("via"), want_giver)
        if g != want_giver:
            return "the tap's giver is %r, the reply's via %r" % (g, want_giver)
        if reply.get("levelUsed") != 3:
            return "levelUsed %r for a giver order" % reply.get("levelUsed")
        return None
    if reply.get("via") != "raw" or reply.get("levelUsed") != 4:
        return "a raw order replied via %r, levelUsed %r" % (reply.get("via"), reply.get("levelUsed"))
    if str(g).startswith("WorkGiverDef:") or g in (NODE,):
        return "the tap names the giver %r for a raw job" % g
    return None


def judge_force(summary, alias_id, want_used):
    """None when the session's force record of the actor holds the levels used in order, else why not."""
    ent = None
    for k, v in (summary or {}).items():
        if k in alias_id:
            ent = v
    if not isinstance(ent, dict):
        return "no force entry for %s in %s" % (alias_id, short(summary))
    used = [e.get("used") for e in ent.get("entries") or [] if isinstance(e, dict)]
    if used[-len(want_used):] != want_used:
        return "the record's levels used are %s, the orders used %s" % (used, want_used)
    return None


def short(r, n=300):
    return json.dumps(r, default=str)[:n] if r is not None else "None"


def selfcheck():
    """The judges on hand-made rows: a good run passes, GPT's always-raw executor fails R4."""
    good = {"success": True, "started": True, "job": "TendPatient#11", "via": "WorkGiverDef:DoctorTendToHumanlikes", "levelUsed": 3}
    rows = [{"rec": "job_start", "alias": "rA", "def": "TendPatient", "giver": "WorkGiverDef:DoctorTendToHumanlikes", "seq": 5, "job": "TendPatient#11"}]
    bad_rows = [{"rec": "job_start", "alias": "rA", "def": "TendPatient", "giver": "ThinkNode_QueuedJob", "seq": 5, "job": "TendPatient#11"}]
    raw = {"success": True, "started": True, "job": "Goto#12", "via": "raw", "levelUsed": 4}
    raw_rows = [{"rec": "job_start", "alias": "rA", "def": "Goto", "giver": "ThinkNode_QueuedJob", "seq": 6, "job": "Goto#12"}]
    out = [judge_tap(rows, "rA", good, "WorkGiverDef:DoctorTendToHumanlikes") is None,
           judge_tap(bad_rows, "rA", good, "WorkGiverDef:DoctorTendToHumanlikes") is not None,      # the always-raw plant
           judge_tap(raw_rows, "rA", raw, None) is None,
           judge_tap(rows, "rA", dict(good, via="raw", levelUsed=4, job="TendPatient#11"), None) is not None,
           judge_tap(rows, "rA", dict(good, started=False), "WorkGiverDef:DoctorTendToHumanlikes") is not None,
           judge_force({"Human1": {"entries": [{"used": 3}, {"used": 4}]}}, ("rA", "Human1"), [3, 4]) is None,
           judge_force({"Human1": {"entries": [{"used": 3}, {"used": 3}]}}, ("rA", "Human1"), [3, 4]) is not None]
    print("prove_ordered_rescue selfcheck: %d of %d" % (sum(out), len(out)))
    return 0 if all(out) else 1


# ------------------------------------------------------------------------------------------------ the stage
def colonists(W):
    out = []
    for p in W.call("jawa/pawn_get", limit=200).get("pawns") or []:
        if p.get("faction") != "PlayerColony" or p.get("downed") or p.get("dead"):
            continue
        x, z = p.get("x"), p.get("z")
        if x is None and isinstance(p.get("position"), dict):
            x, z = p["position"].get("x"), p["position"].get("z")
        if p.get("thingId") and x is not None and "Human" in str(p.get("thingId")):
            out.append((p["thingId"], int(x), int(z)))
    return out


def xz_of(t):
    if t.get("x") is not None:
        return int(t["x"]), int(t["z"])
    p = t.get("position")
    if isinstance(p, dict):
        return int(p.get("x")), int(p.get("z"))
    if isinstance(p, str) and "," in p:
        bits = [int(v) for v in p.strip("() ").split(",")]
        return bits[0], bits[-1]
    return None


def job_of(v):
    """A read of jobs.curJob.loadID -> the id, NONE for a pawn with no job, UNREADABLE for any other failure."""
    if v.get("state") == "ok":
        return v.get("v")
    return "NONE" if "null at 'curJob'" in str(v.get("detail")) else "UNREADABLE"


def read1(R, of, path):
    v = R.read((of, path))
    return v[0] if v else {"state": "error", "v": None}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--host", default=None, help="the game by name (ArchBig, ArchSmall); none = the default endpoint")
    ap.add_argument("--selfcheck", action="store_true", help="the judges on hand-made rows; no game")
    ap.add_argument("--log", default=None, help="also write the lines to this file")
    a = ap.parse_args(argv)
    if a.selfcheck:
        return selfcheck()
    from prove_tap_certificate import connect
    import canonical_saves
    W = connect(a.host)
    import prove_run_until as R
    log("ordered rescue proof %s on %s, driver %s" % (datetime.datetime.now().isoformat(timespec="seconds"), a.host or "default", R.DRIVER))
    rc = run(W, R, canonical_saves)
    if a.log:
        with open(a.log, "w", encoding="utf-8") as f:
            f.write("\n".join(LINES) + "\n")
    return rc


def run(W, R, canonical_saves):
    hs = W.call("jawa/companion_handshake")
    if str(hs.get("effectiveProfile") or "").lower() != "test":
        log("NO VERDICT: the companion's effective profile is %r, not test" % hs.get("effectiveProfile"))
        return 2
    repo = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    names, starts = canonical_saves.read(repo)
    g = hs.get("game") or {}
    if g.get("programState") != "Playing":
        if not R.start_map():
            log("NO VERDICT: no quicktest map")
            return 2
        g = W.call("jawa/companion_handshake").get("game") or {}
    save = g.get("save")
    if save and (save in names or any(save.startswith(s) for s in starts)):
        log("NO VERDICT: the loaded save %r is canonical" % save)
        return 2
    for d, ty in ((GIVER, "WorkGiverDef"), ("TendPatient", "JobDef"), ("Goto", "JobDef"), ("Rescue", "JobDef"), ("Bed", "ThingDef"), ("WoodLog", "ThingDef")):
        r = W.call("jawa/get_def", defName=d, defType=ty)
        if not r.get("success", False) or r.get("error"):
            log("NO VERDICT: %s %s is not in this game: %s" % (ty, d, R.brief(r)))
            return 2
    col = colonists(W)
    mi = W.call("jawa/map_info")
    if len(col) < 3:
        log("NO VERDICT: the stage needs three standing colonists, the map has %d" % len(col))
        return 2
    # the doctor: the first colonist whose Doctor work is not disabled (set_work_priority refuses a priority on a disabled
    # type; measured on ArchSmall 2026-11-25: a colonist that "will never do doctoring" spoiled the tend rows)
    doc = None
    for i, (pid, _x, _z) in enumerate(col):
        if W.call("jawa/set_work_priority", pawnId=pid, workType=WORKTYPE, priority=1, manualPriorities=True).get("success"):
            doc = i
            break
    if doc is None:
        log("NO VERDICT: no colonist on the map can do Doctor work")
        return 2
    col = [col[doc]] + col[:doc] + col[doc + 1:]
    (A, ax, az), (B, _bx, _bz), (C, _cx, _cz) = col[0], col[1], col[2]
    sx, sz = int(mi["sizeX"]), int(mi["sizeZ"])
    ax, az = min(max(ax, 12), sx - 13), min(max(az, 12), sz - 13)
    log("stage: save %r, map %s, tick %s; rescuer %s, victim %s, standing %s near %d,%d" % (save, g.get("currentMapId"), mi.get("ticksGame"), A, B, C, ax, az))

    # R0, the scene (before the session: it steps ticks): a bed, the victim downed, the standing colonist rescues the victim
    bx, bz = ax, min(az + 5, sz - 3)
    W.call("jawa/build_batch", ops="Bed:%d,%d,0" % (bx, bz), stuff="WoodLog", faction="player", readBack=True)
    beds = [t.get("id") for t in W.call("jawa/list_things", defName="Bed", limit=200).get("things") or [] if xz_of(t) == (bx, bz)]
    down = W.call("jawa/pawn_force_incapacitate", pawn=B, action="downed", allowBleedingWounds=False)
    if not beds or not down.get("downedAfter"):
        log("NO VERDICT: the scene: bed %s, downed %s" % (beds, short(down)))
        return 2
    oj = W.call("jawa/ordered_job", pawnId=C, jobDef="Rescue", targetAId=B, targetBId=beds[0], count=1, waitTicks=0)
    lay = None
    for _ in range(12):
        W.call("rimworld/step_game_ticks", ticks=250)
        lay = W.call("jawa/read_paths", reads=json.dumps([{"of": "thing:%s" % B, "path": "jobs.curJob.def.defName"},
                                                          {"of": "thing:%s" % B, "path": "jobs.curJob.targetA.thingInt.thingIDNumber"}])).get("values") or []
        if lay and lay[0].get("v") == "LayDown":
            break
    if not lay or lay[0].get("v") != "LayDown":
        log("NO VERDICT: the scene: the victim is not in bed after the rescue (%s; rescue order %s)" % (short(lay), short(oj, 200)))
        return 2
    log("staged: bed %s at %d,%d; victim %s downed (%s) and in bed (%s); rescue by %s" % (
        beds[0], bx, bz, B, down.get("downedAfter"), [v.get("v") for v in lay], C, ))
    rows = []
    R.open_session(lease=120)
    try:
        W.call("jawa/session", action="bind", driver=R.DRIVER, bindings=json.dumps({"rA": A, "rB": B, "rC": C}))
        # R2: not assigned to Doctor -> the float menu's refusal, before any tick
        W.call("jawa/set_work_priority", pawnId=A, workType=WORKTYPE, priority=0, manualPriorities=True)
        t0 = R.tick()
        r2 = W.call("jawa/order", actor="rA", level="giver", giver=GIVER, target="rB")
        t1 = R.tick()
        W.call("jawa/set_work_priority", pawnId=A, workType=WORKTYPE, priority=1, manualPriorities=True)
        bad = None
        if not r2.get("success") or r2.get("given") is not False or r2.get("started"):
            bad = "the order was not refused by the giver: %s" % short(r2)
        elif not r2.get("reason") or str(r2.get("reason")).startswith("the float menu offers no order"):
            bad = "the float menu offered no disabled option (the scene is wrong, or the reason is lost): %s" % short(r2)
        elif t0 != t1:
            bad = "a tick passed: %s -> %s" % (t0, t1)
        rows.append(("R2 a doctor not assigned to Doctor is refused by the float menu before a tick", bad,
                     "given %s, reason %r, levelUsed %s, tick %s -> %s" % (r2.get("given"), r2.get("reason"), r2.get("levelUsed"), t0, t1)))

        # R5: a giver made to refuse: the target stands
        j0 = job_of(read1(R, "rA", "jobs.curJob.loadID"))
        t0 = R.tick()
        r5 = W.call("jawa/order", actor="rA", level="giver", giver=GIVER, target="rC")
        j1 = job_of(read1(R, "rA", "jobs.curJob.loadID"))
        bad = None
        if not r5.get("success") or r5.get("given") is not False or r5.get("started"):
            bad = "the giver did not refuse a standing target: %s" % short(r5)
        elif j0 != j1 or "UNREADABLE" in (j0, j1):
            bad = "the doctor's job changed (or could not be read): %s -> %s" % (j0, j1)
        rows.append(("R5 a giver made to refuse (target not downed): given false, nothing started", bad,
                     "given %s, reason %r, job %s -> %s, tick %s -> %s" % (r5.get("given"), r5.get("reason"), j0, j1, t0, R.tick())))

        # R1 + R4: the tend, inside one run with the cast bound (the job taps on)
        st = W.call("jawa/session", action="state")
        t0 = R.tick() or 0
        acts = [{"tool": "jawa/order", "at": 1, "id": R.req("tend"), "args": {"actor": "rA", "level": "giver", "giver": GIVER, "target": "rB"}}]
        # a tend by an unskilled doctor with no medicine outlasts 1500 ticks (ArchSmall 2026-11-25: TendPatient still on)
        rep = R.run(R.at_tick(t0 + TEND_TICKS), TEND_TICKS + 200, acts=acts, limit_s=600)
        trace = W.read_trace({"recordDir": st.get("recordDir"), "session": st.get("writerSession") or st.get("session"), "run": rep.get("run")}, 15) if rep.get("run") else []
        ra = (rep.get("acts") or [{}])[0].get("reply") or {}
        ends = [r for r in trace if r.get("rec") == "job_end" and r.get("alias") == "rA" and r.get("job") == ra.get("job")]
        bad = None
        if not ra.get("given") or not ra.get("started") or not str(ra.get("job")).startswith("TendPatient#"):
            bad = "the tend was not given and started (the job after is %s): %s" % (ra.get("job"), short(ra))
        elif not ends or ends[0].get("cond") != "Succeeded":
            bad = "the tend job %s did not end Succeeded in %s ticks: %s" % (ra.get("job"), R.tick() - t0, [(r.get("def"), r.get("cond")) for r in ends][:3])
        rows.append(("R1 a doctor ordered through DoctorTendToHumanlikes tends the downed colonist (the job ends Succeeded)", bad,
                     "reply given %s started %s via %s job %s; run %s %s; job_end %s" % (
                         ra.get("given"), ra.get("started"), ra.get("via"), ra.get("job"), rep.get("run"), rep.get("why"),
                         [(r.get("def"), r.get("cond")) for r in ends][:2])))
        r4 = [judge_tap(trace, "rA", ra, "WorkGiverDef:" + GIVER)]
        r4_info = ["tend: tap giver %s" % [r.get("giver") for r in trace if r.get("rec") == "job_start" and r.get("alias") == "rA"][:4]]

        # R4 (on): a JobGiver through its node, then a raw Goto, in a second run. The Goto's cell is a standing colonist's
        # cell at least 3 cells off (ArchSmall 2026-11-25: a guessed cell ended the Goto at once), else the bed's cell.
        here = {pid: (x, z) for pid, x, z in colonists(W)}
        a_at = here.get(A)
        far = [c for pid, c in here.items() if pid != A and a_at and max(abs(c[0] - a_at[0]), abs(c[1] - a_at[1])) >= 3]
        goto = far[0] if far else (bx, bz)
        t0 = R.tick() or 0
        acts = [{"tool": "jawa/order", "at": 1, "id": R.req("node"), "args": {"actor": "rA", "level": "giver", "giver": NODE}},
                {"tool": "jawa/order", "at": 40, "id": R.req("raw"), "args": {"actor": "rA", "level": "raw", "jobDef": "Goto", "target": "%d,%d" % goto}}]
        rep2 = R.run(R.at_tick(t0 + 120), 320, acts=acts)
        trace2 = W.read_trace({"recordDir": st.get("recordDir"), "session": st.get("writerSession") or st.get("session"), "run": rep2.get("run")}, 15) if rep2.get("run") else []
        rn = ((rep2.get("acts") or [{}, {}])[0] or {}).get("reply") or {}
        rr = ((rep2.get("acts") or [{}, {}])[-1] or {}).get("reply") or {}
        r4.append(judge_tap(trace2, "rA", rn, NODE))
        r4.append(judge_tap(trace2, "rA", rr, None))
        force = (W.call("jawa/session", action="state").get("force")) or {}
        r4.append(judge_force(force, ("rA", A), [3, 3, 4]))
        r4_info.append("node: via %s job %s; raw: via %s job %s; tap givers %s" % (
            rn.get("via"), rn.get("job"), rr.get("via"), rr.get("job"), [(r.get("def"), r.get("giver")) for r in trace2 if r.get("rec") == "job_start" and r.get("alias") == "rA"][:5]))
        r4_info.append("force record %s" % short(force, 400))
        fails4 = [x for x in r4 if x]
        rows.append(("R4 the job tap's giver agrees with the receipt's level (giver: named; raw: not)", "; ".join(fails4) if fails4 else None, "; ".join(r4_info)))

        # R3: a hostile with no lord
        hp = W.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=min(ax + 12, sx - 3), z=az, faction="hostile", count=1)
        hid = hp.get("id") or hp.get("pawnId") or ((hp.get("pawns") or [{}])[0] or {}).get("id")
        cen = [p for p in W.call("jawa/pawn_census", faction="hostile").get("pawns") or [] if isinstance(p, dict) and p.get("id") == hid]
        lord = (cen[0].get("lord") if cen else "unread")
        r3 = W.call("jawa/motive", actor=hid, lordJob="LordJob_AssaultColony") if hid else {"error": "no hostile spawned: %s" % short(hp)}
        if hid:
            W.call("jawa/pawn_force_incapacitate", pawn=hid, action="vanish")
        bad = None
        if not hid:
            bad = "NO STAGE: %s" % r3["error"]
        elif lord not in (None, {}, "") and lord != "unread":
            bad = "the staged hostile has a lord (%s): the scene is wrong" % short(lord, 120)
        elif r3.get("success") is not False or r3.get("refused") != "NO_LORD":
            bad = "the motive was not refused NO_LORD: %s" % short(r3)
        rows.append(("R3 jawa/motive on a hostile with no lord is refused NO_LORD", bad,
                     "hostile %s, lord %s; refused %s: %s" % (hid, lord, r3.get("refused"), str(r3.get("message"))[:160])))
    finally:
        R.end_session("close")

    fails = 0
    for name, bad, info in sorted(rows):
        fails += bad is not None
        log("%s %s: %s" % ("PASS" if bad is None else "FAIL", name, info if bad is None else "%s | %s" % (bad, info)))
    log("prove_ordered_rescue: %d of %d rows held, %d failed" % (len(rows) - fails, len(rows), fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
