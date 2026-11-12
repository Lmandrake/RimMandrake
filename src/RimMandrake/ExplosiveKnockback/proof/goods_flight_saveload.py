#!/usr/bin/env python3
"""Flying goods survive a save taken mid-flight (RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD step 1). PROOF BUILD ONLY.

Stages the goods_fly_lands scene (75 steel beside a mortar-sized blast, flight speed 6 cells/s so it is in the air for
about 30 ticks), steps a few ticks, reads the carrier with RM_KnockbackProof.Flights, saves, reloads that save, reads
again, steps until it lands. Every row can fail alone:
  FS_IN_FLIGHT          one carrier holds Steel x75 a few ticks after the blast (before the save)
  FS_RELOADED_CARRIER   after the reload the same stack (same ThingID, x75, same destination) is still in a carrier
  FS_LANDED_NO_CARRIER  once the flight ends, no carrier is left on the map
  FS_STACK_ON_DEST      that ThingID is spawned on the carrier's destination cell with stackCount 75
The save (EK_GOODS_FLIGHT_MIDAIR_<stamp>) is a throwaway on a scratch map; delete it after reading the evidence.

Usage (python.exe from WSL, bridge held, a SCRATCH map current, proof build deployed):
  goods_flight_saveload.py [--ticks-before 4] [--out evidence.json]
Prints one PASS/FAIL/UNMEASURED table. Exit 0 only if every row passes; 3 = PROOF BUILD REQUIRED."""
import argparse, datetime, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "FlowWorks", "northstar"))
sys.path.insert(0, os.path.join(HERE, ".."))
import proof_hose as PH  # noqa: E402
from proof_build_gate import require_proof_build  # noqa: E402

KP = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"
ap = argparse.ArgumentParser()
ap.add_argument("--ticks-before", type=int, default=4, help="ticks between the blast and the save (flight ~30)")
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


def flights():
    """Carriers on the current map -> list of dicts (Flights() lines)."""
    out = []
    for line in kp("Flights").splitlines():
        if not line or line.startswith("NONE"):
            continue
        parts = line.split(" ")
        d = {"id": parts[0]}
        for p in parts[1:]:
            if "=" in p:
                k, v = p.split("=", 1)
                d[k] = v
            elif p.startswith("x") and p[1:].isdigit():
                d["count"] = int(p[1:])
        out.append(d)
    return out


def steps(n):
    c("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=60000)


def same_id(listed, thing_id):
    """list_things may give the ThingID ("Steel1234") or the number: match either."""
    num = "".join(ch for ch in thing_id if ch.isdigit())
    return str(listed) in (thing_id, num)


require_proof_build(c("jawa/static_call", type=KP, method="Names", args="x"))
c("rimworld/set_time_speed", speed=0)
kp("Clear")
origin = kp("Origins", "1").split(";")[0]
staged = kp("Stage", "goods_fly_lands,%s" % origin)
ev["staged"] = staged
if not staged.startswith("STAGED"):
    for rid in ("FS_IN_FLIGHT", "FS_RELOADED_CARRIER", "FS_LANDED_NO_CARRIER", "FS_STACK_ON_DEST"):
        row(rid, "UNMEASURED", "stage: " + staged[:160])
else:
    steps(a.ticks_before)
    f0 = [f for f in flights() if f.get("inner") == "Steel"]
    ev["before"] = f0
    row("FS_IN_FLIGHT", len(f0) == 1 and f0[0].get("count") == 75,
        "%d steel carrier(s) at +%d ticks: %s" % (len(f0), a.ticks_before, f0[:1]))
    if len(f0) != 1:
        for rid in ("FS_RELOADED_CARRIER", "FS_LANDED_NO_CARRIER", "FS_STACK_ON_DEST"):
            row(rid, "UNMEASURED", "no single carrier in the air to save")
    else:
        want = f0[0]
        name = "EK_GOODS_FLIGHT_MIDAIR_" + datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        ev["save"] = name
        sv = c("rimworld/save_game", saveName=name)
        c("rimworld/load_game", saveName=name)
        PH.V._wait_playing(B, leave_s=3)
        c("rimworld/set_time_speed", speed=0)
        f1 = [f for f in flights() if f.get("innerId") == want.get("innerId")]
        ev["after_load"] = f1
        row("FS_RELOADED_CARRIER", len(f1) == 1 and f1[0].get("count") == 75 and f1[0].get("dest") == want.get("dest"),
            "save %s -> %s; after reload %s" % (name, str(sv)[:80], f1[:1] or "no carrier with " + str(want.get("innerId"))))
        left = max(int(want.get("left") or 30), 1) + 10
        steps(left)
        rest = flights()
        ev["after_land"] = rest
        row("FS_LANDED_NO_CARRIER", not rest, "%d carrier(s) left after %d more ticks" % (len(rest), left))
        dx, dz = (int(v) for v in want["dest"].split(","))
        things = c("jawa/list_things", rect="%d,%d,1,1" % (dx, dz), limit=50).get("things") or []
        hit = [t for t in things if same_id(t.get("id"), want.get("innerId", ""))]
        ev["dest_cell"] = things
        row("FS_STACK_ON_DEST", len(hit) == 1 and hit[0].get("stackCount") == 75,
            "dest %d,%d holds %s" % (dx, dz, hit[:1] or [(t.get("def"), t.get("stackCount")) for t in things]))
    kp("Verdict", "goods_fly_lands")   # runs the scene restore (its settings back); the verdict itself is stale here
out = a.out or os.path.join(os.environ.get("RM_SCRATCH", r"D:\ClaudeWork\rimmandrake"), "ek_proof",
                            "goods_flight_saveload_%s.json" % datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as fh:
    json.dump({"rows": rows, "ev": ev}, fh, indent=1, default=str)
print("%-24s %-10s %s" % ("ROW", "STATUS", "DETAIL"))
for rid, st, det in rows:
    print("%-24s %-10s %s" % (rid, st, det))
print("evidence:", out)
sys.exit(0 if rows and all(r[1] == "PASS" for r in rows) else 1)
