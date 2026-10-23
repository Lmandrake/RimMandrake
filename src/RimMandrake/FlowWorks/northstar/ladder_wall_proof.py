"""LADDER OVER A WALL live proof (LADDER_PARITY_BUILD_NO_KEYS_REQUIRED, owner by card 2026-10-23: "Ladders should work to
climb one-way over single walls without roofs as well."; design design/RimMandrake/ladder_parity_2026-10-23.md).

  python.exe src/RimMandrake/FlowWorks/northstar/ladder_wall_proof.py [out.json] [--fresh-map]

Run from the repo root with python.exe; the bridge must be held. Scene (map centre c, a cleared 21x21 site): a single
granite wall line north-south at x = c+3 (z = c-3..c+3), no roof; the PLAYER's portable ladder on (c+2, c) facing east (the
wall); one colonist on the ladder's square (a quicktest colonist wears no climbing gear; "climb:" reports byLadder). Acts through RM_LadderParity.ProofLadderParity.

Rows:
  LADDER_PARITY_WALL_LADDER_PLACED   PASS/FAIL  the ladder stands on undug ground facing the wall (its inspect reads the
                                                 over-the-wall line; read back with "may:").
  LADDER_PARITY_OVER_WALL            PASS/FAIL  "climb:" orders the colonist over; after 900 ticks it stands east of the wall.
  LADDER_PARITY_ONE_WAY              PASS/FAIL  from the far side (no ladder there, no gear) "climb:" finds NO_CROSSING.
  LADDER_PARITY_DOUBLE_WALL_REFUSED  PASS/FAIL  a second wall line at x = c+4 makes the crossing two squares thick: NO_CROSSING.
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

    def pos(pid):
        lp = B.call("jawa/list_pawns", includeHealth=False, limit=500) or {}
        p = next((p_ for p_ in lp.get("pawns") or [] if str(p_.get("id")) == str(pid)), None)
        return None if p is None else (p.get("x"), p.get("z"))

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
    B.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % (wx, z) for z in range(c[1] - 3, c[1] + 4)), stuff="BlocksGranite")
    foot = (c[0] + 2, c[1])
    res["build"] = str(B.call("jawa/build_batch", ops="RM_LadderPortable:%d,%d,1" % foot, wipeExisting=False) or {})[:300]
    adv(60)
    cols = B.probe_of(HPROBE, "colonists").get("pawns") or []
    if not cols:
        row("LADDER_PARITY_OVER_WALL", "UNMEASURED", {"why": "no colonist on the map"})
        return 2
    pid = cols[0]["id"]
    B.probe_of(HPROBE, "pawn:%d=tp:%d,%d" % (pid, foot[0], foot[1]))
    adv(30)
    may = parity(B, "may:%d,%d,%d" % (pid, foot[0], foot[1]))
    row("LADDER_PARITY_WALL_LADDER_PLACED", "PASS" if "ladder=RM_LadderPortable" in may else "FAIL",
        {"may": may, "build": res["build"]})
    order = parity(B, "climb:%d,%d,%d" % (pid, wx, c[1]))
    adv(900)
    p1 = pos(pid)
    over = p1 is not None and p1[0] is not None and p1[0] > wx
    row("LADDER_PARITY_OVER_WALL", "PASS" if over else "FAIL", {"order": order, "after": p1, "wallX": wx})
    if over:
        back = parity(B, "climb:%d,%d,%d" % (pid, wx, p1[1]))
        row("LADDER_PARITY_ONE_WAY", "PASS" if back.startswith("NO_CROSSING") else "FAIL",
            {"back": back, "bar": "no ladder on the far side and no gear: no crossing back"})
    else:
        row("LADDER_PARITY_ONE_WAY", "UNMEASURED", {"why": "never got over"})
    # a double wall: a second line east of the first; teleport back to the ladder and ask again
    B.probe_of(HPROBE, "pawn:%d=tp:%d,%d" % (pid, foot[0], foot[1]))
    adv(10)
    B.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % (wx + 1, z) for z in range(c[1] - 3, c[1] + 4)), stuff="BlocksGranite")
    adv(30)
    dbl = parity(B, "climb:%d,%d,%d" % (pid, wx, c[1]))
    row("LADDER_PARITY_DOUBLE_WALL_REFUSED", "PASS" if dbl.startswith("NO_CROSSING") else "FAIL", {"read": dbl})
    save()
    say("result: %s" % os.path.relpath(a.out, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
