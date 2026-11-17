#!/usr/bin/env python3
"""A thrown pawn survives a save taken mid-flight, and still breaks the cover it comes down on (Explosive Knockback;
RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX). PROOF BUILD ONLY.

Leaf walk_storeroom_raid's red is "a build whose thrown things duplicate or vanish across a reload"; leaf
thrown_into_pit_falls says a pawn thrown onto a covered pit cell falls through and leaves the cover broken. Until 2026-11-17
the explosion that threw a pawn was remembered in a static dictionary a load forgets, and the code's own comment said a
reloaded flight "breaks nothing": the colonist stood on the cover. It rides in the map component's save now. Two lanes, each
staged with RM_KnockbackProof.MapCase, saved a few ticks into the flight, reloaded, stepped to rest and read by cell:
  PF_PLAIN_IN_FLIGHT        the colonist is in the air at the save
  PF_PLAIN_LANDS            after the reload it stands on the planned cell, 3 cells straight away from the blast, nothing in the air
  PF_COVER_IN_FLIGHT        the same, thrown at a covered pit the blast does not reach
  PF_COVER_BREAKS           after the reload it is on the pit cell, the cover is gone and nothing is in the air
  PF_NO_TICK_EXCEPTIONS     Player.log gained no "Exception ticking" and no "TweenedPosRoot" line over the run
The saves (EK_PAWN_FLIGHT_MIDAIR_<stamp>_<lane>) are throwaways on a scratch map.

Usage (python.exe from WSL, bridge held, a SCRATCH map current, proof build deployed, FlowWorks loaded):
  pawn_flight_saveload.py [--ticks-before 5] [--out evidence.json]
Exit 0 only if every row passes; 3 = PROOF BUILD REQUIRED."""
import argparse, datetime, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "FlowWorks", "northstar"))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Utils"))
import proof_hose as PH  # noqa: E402
from proof_build_gate import require_proof_build  # noqa: E402
from game_paths import PLAYER_LOG  # noqa: E402
KP = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"
ap = argparse.ArgumentParser()
ap.add_argument("--ticks-before", type=int, default=5, help="ticks between the blast and the save (a throw flies 18 or more)")
ap.add_argument("--out", default=None)
a = ap.parse_args()
B = PH.PB()
rows, ev = [], {}


def c(tool, **kw):
    try:
        return B.call(tool, **kw) or {}
    except Exception as e:  # noqa: BLE001
        return {"success": False, "exc": repr(e)[:300]}


def kp(method, arg="x"):
    return str(c("jawa/static_call", type=KP, method=method, args=arg).get("result") or "")


def row(rid, ok, det):
    rows.append((rid, ok if isinstance(ok, str) else ("PASS" if ok else "FAIL"), det))


def cell(x, z):
    t = kp("CellRead", "%d,%d" % (x, z))
    return dict(p.split("=") for p in t.split(" ")[1:]) if t.startswith("CELL") else {"error": t}


def log_lines():
    try:
        with open(PLAYER_LOG, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        return text.count("Exception ticking") + text.count("TweenedPosRoot")
    except OSError as e:
        return "unreadable: %s" % e


require_proof_build(c("jawa/static_call", type=KP, method="Names", args="x"))
c("rimworld/set_time_speed", speed=0)
before_log = log_lines()
origins = kp("Origins", "4").split(";")
stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
# lane -> (spec, the cell the colonist must end on relative to the blast, must the cell's cover be gone)
LANES = [("PLAIN", "t:a:col:1:0;b:bomb:2.9", (4, 0), False), ("COVER", "c:cover:3:0;t:a:col:1:0;b:bomb:1.9", (3, 0), True)]
for n, (lane, spec, (ex, ez), covered) in enumerate(LANES):
    kp("Clear")
    ox, oz = (int(v) for v in origins[n % len(origins)].split(","))
    staged = kp("MapCase", "%d,%d@%s" % (ox, oz, spec))
    ev[lane] = {"staged": staged, "origin": [ox, oz]}
    fly, land = "PF_%s_IN_FLIGHT" % lane, "PF_%s_%s" % (lane, "BREAKS" if covered else "LANDS")
    if not staged.startswith("STAGED"):
        row(fly, "UNMEASURED", "stage: " + staged[:160])
        row(land, "UNMEASURED", "not staged")
        continue
    c("rimworld/step_game_ticks", ticks=a.ticks_before, pauseFirst=True, timeoutMs=60000)
    read = kp("MapRead")
    start = cell(ox + 1, oz)
    ev[lane]["mid"] = read
    in_air = "a=?,?,0,air" in read and start.get("pawns") == "0"
    row(fly, in_air, "at +%d ticks: %s; start cell %s" % (a.ticks_before, read[:80], start))
    if not in_air:
        row(land, "UNMEASURED", "nothing in the air to save")
        continue
    name = "EK_PAWN_FLIGHT_MIDAIR_%s_%s" % (stamp, lane)
    ev[lane]["save"] = name
    sv = c("rimworld/save_game", saveName=name)
    c("rimworld/load_game", saveName=name)
    PH.V._wait_playing(B, leave_s=3)
    c("rimworld/set_time_speed", speed=0)
    c("rimworld/step_game_ticks", ticks=120, pauseFirst=True, timeoutMs=60000)
    end, was = cell(ox + ex, oz + ez), cell(ox + 1, oz)
    ev[lane]["end"], ev[lane]["start_after"] = end, was
    ok = end.get("pawns") == "1" and was.get("pawns") == "0" and end.get("flyers") == "0"
    if covered:
        ok = ok and end.get("superdeep") == "True" and end.get("cover") == "False"
    row(land, ok, "save %s (%s); 120 ticks after the reload the end cell reads %s, the start cell %s" % (name, str(sv)[:60], end, was))
after_log = log_lines()
row("PF_NO_TICK_EXCEPTIONS", isinstance(before_log, int) and after_log == before_log,
    "Player.log 'Exception ticking' + 'TweenedPosRoot' lines: %s before, %s after" % (before_log, after_log))
out = a.out or os.path.join(os.environ.get("RM_SCRATCH", r"D:\ClaudeWork\rimmandrake"), "ek_proof", "pawn_flight_saveload_%s.json" % stamp)
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as fh:
    json.dump({"rows": rows, "ev": ev}, fh, indent=1, default=str)
print("%-24s %-10s %s" % ("ROW", "STATUS", "DETAIL"))
for rid, st, det in rows:
    print("%-24s %-10s %s" % (rid, st, det))
print("evidence:", out)
sys.exit(0 if rows and all(r[1] == "PASS" for r in rows) else 1)
