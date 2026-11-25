#!/usr/bin/env python3
"""selftest_testq_host_switch.py - the test lane obeys the host work switch, and a harness repair re-runs only what held.

Item RIMMANDRAKE_VET_WORK_BOUND_FOR_STEVEDESKTOP_HE_SAW_FIREHAWK_AGAIN. Failures that happened, 2026-11-24/25:
- the owner's order (SteveDesktop works pipeline improvements only) lived in testq/fill.stop; the steward aged that file
  into a fault after 60 min, a run gave it an expiry, a Conductor role run removed it, and at 12:00 PM PST 2026-11-25 the
  filler started a DivingInteraction guard job on SteveDesktop;
- HARNESS_REPAIR_CAUSE_6236AE26_2's verify line re-ran the whole job (firehawk_first_sighting_letter and
  embergrass_regrow) though only embergrass_regrow held the fault; the passed firehawk chain ran again each try.

  python3 selftest_testq_host_switch.py     every check; exit 1 on any failure

A temp queue, a temp switch file and a temp hold list stand in for the real ones; no ssh, ledger or game is touched.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
TMP = tempfile.mkdtemp(prefix="host_switch_")
os.environ["TESTQ_QUEUE"] = os.path.join(TMP, "q")
os.environ["RIMFLOW_ITEMS"] = os.path.join(TMP, "items")
HOLDS = os.path.join(TMP, "mod_owner_hold.json")
with open(HOLDS, "w") as f:
    json.dump({"holds": []}, f)
os.environ["RM_OWNER_HOLD_FILE"] = HOLDS
SW = os.path.join(TMP, "host_work_switch.json")
os.environ["RM_HOST_SWITCH_FILE"] = SW
SAID = "I'd like to have SteveDesktop working 100% on closing out non-mod work today please."

import pipeline_admit as P  # noqa: E402
import testq as T  # noqa: E402
import ingest  # noqa: E402

FAILS = []


def check(ok, what):
    print("%s  %s" % ("PASS" if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def switch(on):
    with open(SW, "w") as f:
        json.dump({"switches": [{"host": "SteveDesktop", "mode": "pipeline", "date": "2026-11-24", "said": SAID}]
                   if on else []}, f)


def job(sel, lane="stevedesktop", by="BENCH.filler"):
    return {"mod": "DivingInteraction", "selector": sel, "purpose": "guard", "requested_by": by, "lane": lane}


def t_admission():
    switch(True)
    r = P.switch_refusal(job({"chains": ["seabed_floor_generators"]}))
    check(bool(r) and "pipeline improvements only" in r["text"] and "--lane archmagi" in r["text"],
          "a mod chain job for SteveDesktop is refused while it is switched, and the refusal names its repair: %s"
          % (r or {}).get("text"))
    check(bool(T.hold_refusal(job({"chains": ["seabed_floor_generators"]}))),
          "testq's one queueing door (hold_refusal: submit and the fault-window rerun) refuses it too")
    check(bool(P.switch_refusal(job({"chains": ["x"]}, lane="any"))), "lane any can land on SteveDesktop: refused")
    check(P.switch_refusal(job({"proofs": ["A1"]})) is None, "a --proofs job (pipeline proof lines) passes")
    check(P.switch_refusal(job({"chains": ["x"]}, lane="archmagi")) is None, "the Archmagi lane passes")
    check(P.switch_refusal(job({"chains": ["x"]}, by="Operations.canary")) is None, "an Ops job passes")
    switch(False)
    check(P.switch_refusal(job({"chains": ["seabed_floor_generators"]})) is None, "no switch: the mod job passes")
    os.remove(SW)
    check(bool(P.switch_refusal(job({"chains": ["x"]}))), "an unreadable switch file refuses (could not look)")


def t_filler():
    switch(True)
    T.ensure_dirs()
    with open(T.q("fill.stop"), "w") as f:
        f.write("a hand stop beside the switch\n")
    p = T.fill_plan("DivingInteraction", 4, 200, now=1795640000.0)
    check(p["verdict"] == "switched" and "pipeline improvements only" in p["text"],
          "fill_plan: the switch outranks fill.stop and the filler queues nothing: %s" % p)
    os.remove(T.q("fill.stop"))
    p = T.fill_plan("DivingInteraction", 4, 200, now=1795640000.0)
    check(p["verdict"] == "switched", "with fill.stop removed the switch still stops the filler: %s" % p["verdict"])
    import steward as ST
    ST.tick_timer_state = lambda: "active"     # the host's real timer is not this test's
    ls = ST.lane_state(1795640000.0, mods=["DivingInteraction"])
    check(ls["state"] == "SWITCHED" and ls["fault_at"] is None and ls["settled"],
          "the steward reads the switch as intended and settled, never a fault: %s" % ls)
    switch(False)


def t_rerun_line():
    j = {"id": "J1", "mod": "Pyrelands", "purpose": "guard", "selector": {"chains": [
        "firehawk_first_sighting_letter", "embergrass_regrow"]}}
    line = ingest.rerun_line(j, ["embergrass_regrow"])
    check("--chains embergrass_regrow" in line and "firehawk" not in line,
          "a harness repair re-runs only the chain that held the fault: %s" % line)
    check("--chains firehawk_first_sighting_letter,embergrass_regrow" in ingest.rerun_line(j),
          "with no held chain known the whole selection re-runs (nothing is left unproved)")


def main():
    t_admission()
    t_filler()
    t_rerun_line()
    print("FAILED %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
