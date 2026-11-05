"""LADDER OVER A WALL live proof (LADDER_PARITY_BUILD_NO_KEYS_REQUIRED, owner by card 2026-10-23: "Ladders should work to
climb one-way over single walls without roofs as well."; design design/RimMandrake/ladder_parity_2026-10-23.md).

  python.exe src/RimMandrake/FlowWorks/northstar/ladder_wall_proof.py [out.json] [--fresh-map]

Run from the repo root with python.exe; the bridge must be held. Scene (map centre c, a cleared 21x21 site): a single
granite wall line north-south at x = c+3 running the full site (z = c-10..c+10), no roof; the PLAYER's portable ladder on
(c+2, c) facing east (the wall); one DRAFTED colonist on the ladder's square (a quicktest colonist wears no climbing gear;
"climb:" reports byLadder). Drafted, it takes no work job, so it cannot walk off or round the wall after (or instead of) the
climb (LADDER_WALL_FIX_CLIMBER_WALKS_ROUND_WALL). Acts through RM_LadderParity.ProofLadderParity.

Rows:
  LADDER_PARITY_WALL_LADDER_PLACED   PASS/FAIL  the ladder stands on undug ground facing the wall (its inspect reads the
                                                 over-the-wall line; read back with "may:").
  LADDER_PARITY_OVER_WALL            PASS/FAIL  "climb:" orders the colonist over; its square and curJob are polled every
                                                 POLL ticks up to WAIT ticks, and the FIRST sample with x > wallX inside the
                                                 wall's z span is the verdict (a later walk-off cannot hide it). Never
                                                 crossing while drafted is FAIL with the job trace: refile as MOD on
                                                 RM_ClimbOverWall. No sample read is UNMEASURED.
  LADDER_PARITY_ONE_WAY              PASS/FAIL  from the far side (no ladder there, no gear) "climb:" finds NO_CROSSING, or
                                                 a crossing whose foot is on the LADDER side (walked round the wall's
                                                 ends; one_way_verdict). FAIL only on a foot east of the wall.
  LADDER_PARITY_DOUBLE_WALL_REFUSED  PASS/FAIL  a second wall line at x = c+4 makes the crossing two squares thick: NO_CROSSING.
  LADDER_PARITY_CLIMBER_CENSUS       PASS/FAIL  (A7) a colony dog (Husky), a wild Cobra, a wild Muffalo and a spawned colonist
                                                 on the ladder's square: "may:" reads mayClimb = CENSUS (dog no, cobra yes:
                                                 slithers, muffalo no: too big, colonist yes; design/RimMandrake/
                                                 ladder_climbers_2026-10-23.md). A refused spawn or read is UNMEASURED for
                                                 that pawn, never a pass. Written offline 2026-10-23 (area P); OWED live.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

PROOF_TYPE = "RimMandrake.FlowWorks.RM_NorthstarProofs"
HPROBE = "RimMandrake.FlowWorks.Hose.HoseProbe"
OUT = os.path.join(REPO, "Transient", "fw_scenes", "live")


POLL, WAIT = 30, 900
CENSUS = (("Husky", "player", False), ("Cobra", None, True), ("Muffalo", None, False), ("Colonist", "player", True))


def pawn_num(pid):
    """A spawn reply's id ('Thing_Husky1234' or 1234) -> 1234, or None. Pure."""
    import re
    m = re.search(r"(\d+)$", str(pid or ""))
    return int(m.group(1)) if m else None


def first_crossing(samples, wx, z_span):
    """samples: [(tick, x, z, job)] in order. -> (status, the first sample east of the wall inside z_span or None). Pure.
    UNMEASURED when no sample has a position."""
    seen = False
    for s_ in samples:
        t, x, z, _job = s_
        if x is None or z is None:
            continue
        seen = True
        if x > wx and z_span[0] <= z <= z_span[1]:
            return "PASS", s_
    return ("FAIL" if seen else "UNMEASURED"), None


def one_way_verdict(back, wx):
    """The far-side "climb:" reply -> (status, why). Pure. NO_CROSSING is PASS. An ORDERED crossing is FAIL only when
    it STARTS east of the wall (from.x > wx: climbing back from the far side, no ladder, no gear); one whose foot is
    on the ladder side (from.x < wx) is the pawn walking round the wall's ends to the ladder, correct one-way
    behaviour, PASS (LADDER_ONEWAY_FIX_WALK_ROUND_COUNTED: RM_WallClimb accepts any reachable foot). Anything else,
    or an unreadable from, is UNMEASURED."""
    import re
    txt = str(back or "")
    if txt.startswith("NO_CROSSING"):
        return "PASS", "no crossing from the far side"
    if not txt.startswith("ORDERED"):
        return "UNMEASURED", "unreadable reply"
    m = re.search(r"from=\((-?\d+),\s*-?\d+,\s*(-?\d+)\)", txt)
    if not m:
        return "UNMEASURED", "ORDERED with no readable from="
    fx = int(m.group(1))
    if fx > wx:
        return "FAIL", "crossing from the far side at x=%d (wall x=%d)" % (fx, wx)
    if fx < wx:
        return "PASS", "walk-round: the crossing starts on the ladder side at x=%d" % fx
    return "UNMEASURED", "from= on the wall line itself"


def census_verdict(reads):
    """reads: {kind: may-text or None}. -> (status, wrong). Pure."""
    wrong, unread = [], []
    for kind, _fac, want in CENSUS:
        txt = reads.get(kind)
        got = None
        for tok in str(txt or "").split():
            if tok.startswith("mayClimb="):
                got = {"True": True, "False": False}.get(tok[9:])
        if got is None:
            unread.append(kind)
        elif got != want:
            wrong.append("%s mayClimb=%s, census says %s" % (kind, got, want))
    if wrong:
        return "FAIL", wrong
    return ("UNMEASURED", unread) if unread else ("PASS", [])


def parity(B, arg):
    """RM_LadderParity.ProofLadderParity, as text; a refused or raising call is its own text, never a crash."""
    try:
        r = B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_LadderParity", method="ProofLadderParity", args=arg) or {}
        return str(r.get("result") or r.get("message") or r)[:600]
    except Exception as ex:  # noqa: BLE001
        return "ERROR %s: %s" % (type(ex).__name__, ex)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=os.path.join(OUT, "ladder_wall_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args(argv)
    import validation_core as V
    B = V.Bridge()
    rows, log = [], []
    res = {"script": "ladder_wall_proof.py", "mode": "live", "rows": rows, "log": log}

    def save():
        with open(a.out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(a.out + ".tmp", a.out)

    def say(s):
        print(s, flush=True)
        log.append(s)

    def row(rid, st, det):
        rows.append({"id": rid, "status": st, "detail": det})
        say("%-34s %-10s %s" % (rid, st, json.dumps(det, default=str)[:500]))
        save()

    def adv(n):
        r = B.call("jawa/safe_advance", ticks=n, stopOn="cancel", timeoutMs=max(60000, n * 100)) or {}
        if isinstance(r, dict) and r.get("content"):
            r = json.loads(r["content"][0]["text"])
        return r

    def prow(pid):
        lp = B.call("jawa/list_pawns", includeHealth=False, limit=500) or {}
        return next((p_ for p_ in lp.get("pawns") or [] if pawn_num(p_.get("id")) == pawn_num(pid)), None)

    def pos(pid):
        p = prow(pid)
        return None if p is None else (p.get("x"), p.get("z"))

    def job_of(pid):
        """(curJob, curJobTargetA) through the bridge's own pawn read, asked by list_pawns' ThingID (never the bare
        number); (None, why) when it cannot be read."""
        p = prow(pid)
        if p is None:
            return None, "not in list_pawns"
        try:
            r = B.call("jawa/attack_target_probe", pawn=str(p.get("id")), maxDist=1, _answer=True) or {}
            return r.get("curJob"), r.get("curJobTargetA") or r.get("message") or r.get("error")
        except Exception as ex:  # noqa: BLE001
            return None, "ERROR %s" % type(ex).__name__

    if a.fresh_map:
        if (B.call("rimworld/get_ui_state") or {}).get("programState") == "Playing":
            B.call("rimworld/go_to_main_menu")
            time.sleep(5)
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        ok, waited = V._wait_playing(B, leave_s=0)
        say("quicktest map up: %s (%s s)" % (ok, waited))
    say("threat structures: %s" % V.clear_threat_structures(B))
    B.call("rimworld/pause_game", pause=True)
    B.call("jawa/incident_queue_clear")
    res["sweep_start"] = V.sweep_at_start(B, made_map=a.fresh_map)
    B.call("rimworld/set_god_mode", enabled=True)
    mi = B.call("jawa/map_info") or {}
    c = (int(mi.get("sizeX", 250)) // 2, int(mi.get("sizeZ", 250)) // 2)
    res["centre"] = c
    rect = (c[0] - 10, c[1] - 10, 21, 21)
    B.call("jawa/static_call", type=PROOF_TYPE, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    V.prepare_site(B, rect, [], "ladder_wall_site")
    wx = c[0] + 3
    z_span = (c[1] - 10, c[1] + 10)   # the full site: no way round inside the cleared rect
    B.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % (wx, z) for z in range(z_span[0], z_span[1] + 1)), stuff="BlocksGranite")
    foot = (c[0] + 2, c[1])
    res["build"] = str(B.call("jawa/build_batch", ops="RM_LadderPortable:%d,%d,1" % foot, wipeExisting=False) or {})[:300]
    adv(60)
    cols = B.probe_of(HPROBE, "colonists").get("pawns") or []
    if not cols:
        row("LADDER_PARITY_OVER_WALL", "UNMEASURED", {"why": "no colonist on the map"})
        return 2
    pid = cols[0]["id"]
    B.probe_of(HPROBE, "pawn:%d=tp:%d,%d" % (pid, foot[0], foot[1]))
    res["draft"] = str(B.probe_of(HPROBE, "pawn:%d=draft" % pid))[:200]   # no work job: it cannot walk off or round
    adv(30)
    may = parity(B, "may:%d,%d,%d" % (pid, foot[0], foot[1]))
    row("LADDER_PARITY_WALL_LADDER_PLACED", "PASS" if "ladder=RM_LadderPortable" in may else "FAIL",
        {"may": may, "build": res["build"]})
    order = parity(B, "climb:%d,%d,%d" % (pid, wx, c[1]))
    samples, t = [], 0
    j0 = job_of(pid)
    samples.append((0, None, None, j0[0]))
    while t < WAIT:
        adv(POLL)
        t += POLL
        p_ = pos(pid)
        samples.append((t, p_[0] if p_ else None, p_[1] if p_ else None, job_of(pid)[0]))
        st, hit = first_crossing(samples, wx, z_span)
        if st == "PASS":
            break
    st, hit = first_crossing(samples, wx, z_span)
    p1 = (samples[-1][1], samples[-1][2]) if samples[-1][1] is not None else None
    over = st == "PASS"
    jobs = []
    for s_ in samples:
        if not jobs or jobs[-1][1] != s_[3]:
            jobs.append((s_[0], s_[3]))     # (tick, curJob) at each change: shows the climb job and when it ended
    row("LADDER_PARITY_OVER_WALL", st, {"order": order, "firstCrossing": hit, "after": p1, "wallX": wx, "zSpan": z_span,
        "drafted": res.get("draft"), "jobAtOrder": j0, "jobTrace": jobs, "samples": len(samples) - 1,
        "ifFail": "drafted and walled the full site: never crossing is MOD on RM_ClimbOverWall"})
    if over:
        back = parity(B, "climb:%d,%d,%d" % (pid, wx, p1[1]))
        ow, why = one_way_verdict(back, wx)
        row("LADDER_PARITY_ONE_WAY", ow, {"back": back, "why": why,
            "bar": "no ladder on the far side and no gear: no crossing STARTS east of the wall (a walk-round to the ladder is fine)"})
        if back.startswith("ORDERED"):
            B.probe_of(HPROBE, "pawn:%d=stop" % pid)   # the reply took a job: end the walk-round before the next row
    else:
        row("LADDER_PARITY_ONE_WAY", "UNMEASURED", {"why": "never got over"})
    # a double wall: a second line east of the first; teleport back to the ladder and ask again
    B.probe_of(HPROBE, "pawn:%d=tp:%d,%d" % (pid, foot[0], foot[1]))
    adv(10)
    B.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % (wx + 1, z) for z in range(z_span[0], z_span[1] + 1)), stuff="BlocksGranite")
    adv(30)
    dbl = parity(B, "climb:%d,%d,%d" % (pid, wx, c[1]))
    row("LADDER_PARITY_DOUBLE_WALL_REFUSED", "PASS" if dbl.startswith("NO_CROSSING") else "FAIL", {"read": dbl})
    # A7: who may climb, beside the same lowered ladder
    reads = {}
    for kind, fac, _want in CENSUS:
        kw = dict(kindDef=kind, x=foot[0], z=foot[1], count=1)
        if fac:
            kw["faction"] = fac
        sp = B.call("jawa/spawn_pawn", **kw) or {}
        n = pawn_num(((sp.get("pawns") or [{}])[0] or {}).get("id"))
        reads[kind] = parity(B, "may:%d,%d,%d" % (n, foot[0], foot[1])) if n is not None else None
    st, wrong = census_verdict(reads)
    row("LADDER_PARITY_CLIMBER_CENSUS", st, {"reads": reads, "wrongOrUnread": wrong,
        "census": [(k_, w_) for k_, _f, w_ in CENSUS]})
    save()
    say("result: %s" % os.path.relpath(a.out, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
