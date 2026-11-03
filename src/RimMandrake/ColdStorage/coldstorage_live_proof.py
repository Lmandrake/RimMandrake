"""Live proofs of COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE, one clause per call (design/RimStarWars/cold_storage_line_2026-10-26.md §9.9):

    python.exe src/RimMandrake/ColdStorage/coldstorage_live_proof.py A1|A2|A3|A4|A5|A6

Calls RimMandrake.ColdStorage.RM_ColdStorageProof.Run(<clause>) through jawa/static_call on the current (quicktest) map;
the probe stages, hand-ticks a day in a 25 C room, cleans up and returns one "COLDPROOF <clause> key=value ..." line.
Exit 0 = the clause holds, 1 = it answered and something is wrong, 2 = UNMEASURED (no bridge, REFUSED, no line).
  A1 chill    RSW_CryoUnit: floor meat rots a day's worth, held meat < 10 % of it and sits below 0 C
  A2 stasis   RM_AncientStasisLocker_Original: held meat rot 0 while floor meat rots
  A3 sealed   RM_ResinSealedMeat: rot 0 while floor meat rots
  A4 aging    a seal one tick short stays sealed; past due it becomes RM_AmberAgedMeat, stack and ingredients kept
  A5 wall     RSW_CoolingUnit_Wall in a wall: room still closed (25 cells), prisoner inside may eat from it, one
              outside may not, inside reach by Touch
  A6 gravship RSW_CryoUnit + meat lifted by GenerateGravship and set down 12 cells east on the same map (no flight):
              carried, landed, meat still on it, unit re-registered, custom setpoint kept, meat still below -20 C
verdict() is pure and is exercised offline by selftest_coldstorage.py.
"""
import json
import os
import re
import sys

PROBE = "RimMandrake.ColdStorage.RM_ColdStorageProof"
CLAUSES = ("A1", "A2", "A3", "A4", "A5", "A6")
AGED = "RM_AmberAgedMeat"   # what RM_ResinSealedMeat must age into, named here, not read from the def
DAY_ROT_MIN = 50000.0
SEED_TEMP = -28.0       # RM_ColdStorageProof A6 sets the cryo unit to this before the lift   # a day at 25 C is 60000 rot ticks; below this the room did not hold and nothing is compared


def parse(text, clause):
    """-> dict of key=value from the COLDPROOF line for clause, or None."""
    m = re.search(r"COLDPROOF %s ((?:[A-Za-z]+=[^ \"\\]*\s*)+)" % clause, str(text))
    if not m:
        return None
    return dict(kv.split("=", 1) for kv in m.group(1).split())


def _f(d, k):
    try:
        return float(d.get(k, "nan"))
    except ValueError:
        return float("nan")


def _t(d, *keys):
    return all(d.get(k) == "True" for k in keys)


def verdict(clause, text):
    """-> (exit code, reason) for the probe's reply text."""
    s = str(text)
    d = parse(s, clause)
    if d is None:
        if "REFUSED" in s:
            return 2, "probe refused: " + s[s.find("REFUSED"):][:300]
        return 2, "no COLDPROOF %s line: %s" % (clause, s[:300])
    floor, held = _f(d, "floorRot"), _f(d, "heldRot")
    fails = []
    if clause in ("A1", "A2", "A3"):
        if not floor >= DAY_ROT_MIN:
            return 2, "floor meat rotted %s in a day (want >= %d): the room did not hold 25 C" % (floor, DAY_ROT_MIN)
        if clause == "A1":
            if not held < 0.1 * floor:
                fails.append("held rot %s not < 10%% of floor %s" % (held, floor))
            if not _f(d, "heldAmbient") <= 0:
                fails.append("held meat at %s C, not below 0" % d.get("heldAmbient"))
            if d.get("mode") != "Chill" or not _t(d, "active", "holding"):
                fails.append("unit mode/active/holding %s/%s/%s" % (d.get("mode"), d.get("active"), d.get("holding")))
        elif clause == "A2":
            if held != 0:
                fails.append("stasis held rot %s, want 0" % held)
            if d.get("mode") != "Stasis" or not _t(d, "holding"):
                fails.append("unit mode/holding %s/%s" % (d.get("mode"), d.get("holding")))
        else:
            if held != 0 or not _t(d, "sealed"):
                fails.append("sealed rot %s sealed=%s, want 0/True" % (held, d.get("sealed")))
    elif clause == "A4":
        if not _t(d, "earlyHeld", "oldGone", "ingredientsKept"):
            fails.append("earlyHeld/oldGone/ingredientsKept %s/%s/%s" % (d.get("earlyHeld"), d.get("oldGone"),
                                                                        d.get("ingredientsKept")))
        if d.get("aged") != AGED or d.get("want") != AGED or d.get("stack") != "10":
            fails.append("aged into %s x%s (def agesInto %s), want %s x10" % (d.get("aged"), d.get("stack"), d.get("want"), AGED))
    elif clause == "A5":
        if not _t(d, "roomIntact", "roomSide", "holding", "insideProper", "insideReach"):
            fails.append("roomIntact/roomSide/holding/insideProper/insideReach %s" % "/".join(
                d.get(k, "?") for k in ("roomIntact", "roomSide", "holding", "insideProper", "insideReach")))
        if d.get("outsideProper") != "False":
            fails.append("a prisoner outside the room may eat from the wall unit (outsideProper=%s)" % d.get("outsideProper"))
    elif clause == "A6":
        keys = ("carried", "despawnedInFlight", "landed", "foodOnUnit", "registered", "setpointKept")
        if not _t(d, *keys):
            fails.append(" ".join("%s=%s" % (k, d.get(k)) for k in keys))
        if d.get("stack") != "10":
            fails.append("stack %s, want 10" % d.get("stack"))
        # the probe seeds the unit at -28 C; landing takes no game time, so it must still read -28 and the meat with it
        # (an outdoor map below -20 C cannot pass a unit that lost its temperature)
        if not (abs(_f(d, "unitTemp") - SEED_TEMP) <= 0.5 and abs(_f(d, "foodAmbient") - SEED_TEMP) <= 0.5):
            fails.append("unit %s C / carried meat %s C, want both %s" % (d.get("unitTemp"), d.get("foodAmbient"), SEED_TEMP))
    line = " ".join("%s=%s" % kv for kv in d.items())
    return (1, "; ".join(fails) + " | " + line) if fails else (0, line)


def main(argv):
    if len(argv) != 2 or argv[1] not in CLAUSES:
        print(__doc__)
        return 2
    clause = argv[1]
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
    try:
        import rimbridge_client as R
        host, port, token = R.resolve_endpoint()
        if not token:
            print("UNMEASURED: no bridge token")
            return 2
        with R.RimBridge(host, port, token, timeout=120) as rb:
            out = rb.call("jawa/static_call", {"type": PROBE, "method": "Run", "args": clause})
    except Exception as ex:  # any transport failure means the proof could not see
        print("UNMEASURED: bridge call failed: %s" % str(ex)[:300])
        return 2
    code, why = verdict(clause, json.dumps(out))
    print("%s %s: %s" % (clause, {0: "PASS", 1: "FAIL", 2: "UNMEASURED"}[code], why))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
