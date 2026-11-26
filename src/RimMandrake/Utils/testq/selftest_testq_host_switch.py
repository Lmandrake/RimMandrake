#!/usr/bin/env python3
"""selftest_testq_host_switch.py - the test lane obeys the host work switch, and a harness repair re-runs only what held.

Item RIMMANDRAKE_VET_WORK_BOUND_FOR_STEVEDESKTOP_HE_SAW_FIREHAWK_AGAIN. Failures that happened, 2026-11-24/25:
- the owner's order (SteveDesktop works pipeline improvements only; since his card of 2026-11-25 its Claude work only, its
  games run test jobs of live mods) lived in testq/fill.stop; the steward aged that file
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


LIVE = "LiveMod"
LIVE_MODS = "LiveMod,Heldmod,OffMod"      # the pipeline's advancing list for this test (control.known_mods reads it)
KINDS = (("commission", {"chains": ["c_x"]}, "BENCH"), ("fix", {"chains": ["c_x"]}, "BENCH"),
         ("guard", {"chains": ["c_x"]}, "BENCH"), ("guard", {"chains": ["c_x"]}, "BENCH.filler"),
         ("guard", {"checks": ["sc_x"]}, "BENCH"), ("commission", {"rows": ["r_x"]}, "BENCH"),
         ("guard", {"full": True}, "BENCH"))


def live_job(mod, purpose, sel, by, lane="stevedesktop"):
    return {"mod": mod, "selector": sel, "purpose": purpose, "requested_by": by, "lane": lane}


def plant():
    """The switch on, one held mod, one mod switched off by `pipe off`, and the pipeline's advancing list LIVE_MODS."""
    switch(True)
    with open(HOLDS, "w") as f:
        json.dump({"holds": [{"mod": "Heldmod", "date": "2026-11-16", "said": "hold it"}]}, f)
    os.environ["RM_CONTROL_MODS"] = LIVE_MODS
    P._moh()
    C = sys.modules["control"]
    C.switch("mod:OffMod", True, "pipe off for the test", p=C.db_path())


def t_live_mod_admitted():
    """Item RIMMANDRAKE_ADMIT_LIVE_MOD_TESTS_STEVEDESKTOP_GAMES_SAT_IDLE (owner's card 2026-11-25): while SteveDesktop is
    switched to pipeline work, its games take the test jobs of a mod that is switched on in the pipeline."""
    plant()
    for purpose, sel, by in KINDS:
        r = P.switch_refusal(live_job(LIVE, purpose, sel, by))
        check(r is None, "live mod admitted on the switched host: %s %s by %s%s" % (
            purpose, sorted(sel), by, "" if r is None else " REFUSED: " + r["text"][:150]))
        check(T.hold_refusal(live_job(LIVE, purpose, sel, by)) is None,
              "  and testq's queueing door admits it (%s by %s)" % (purpose, by))
    check(P.switch_refusal(live_job(LIVE, "guard", {"chains": ["x"]}, "BENCH", lane="any")) is None,
          "lane any of a live mod is admitted too")


def t_not_live_stays_refused():
    plant()
    for mod, why in (("Heldmod", "a mod the owner holds"), ("OffMod", "a mod that pipe show reads OFF"),
                     ("Nowhere", "a mod that is not in the Maturation Pipeline")):
        for by in ("BENCH", "BENCH.filler"):
            r = P.switch_refusal(live_job(mod, "guard", {"chains": ["x"]}, by))
            check(bool(r), "refused on the switched host: %s by %s" % (why, by))
    r = P.switch_refusal(live_job("Nowhere", "guard", {"chains": ["x"]}, "BENCH.filler"))
    check(bool(r) and "not live" in r["text"] and "Nowhere" in r["text"] and "--lane archmagi" in r["text"],
          "a filler guard job of a mod that is not live is refused and the refusal says why: %s" % (r or {}).get("text"))
    r = P.switch_refusal(live_job("OffMod", "guard", {"chains": ["x"]}, "BENCH"))
    check(bool(r) and "OFF" in r["text"], "the refusal of an OFF mod says it is OFF: %s" % (r or {}).get("text"))
    check(P.switch_refusal(live_job("Heldmod", "guard", {"chains": ["x"]}, "Operations.canary")) is None,
          "an Ops job of a held mod still passes this switch (the hold gate is the one that binds it)")


def t_unreadable_state_refused():
    plant()
    job = live_job(LIVE, "guard", {"chains": ["x"]}, "BENCH")
    os.environ["RM_OWNER_HOLD_FILE"] = os.path.join(TMP, "absent_hold.json")
    r = P.switch_refusal(job)
    check(bool(r) and "could not look" in r["text"] and "absent_hold.json" in r["text"],
          "an unreadable hold list refuses a live mod with 'could not look' and the cause: %s" % (r or {}).get("text"))
    os.environ["RM_OWNER_HOLD_FILE"] = HOLDS
    os.environ["RM_CONTROL_MODS"] = ""
    r = P.switch_refusal(job)
    check(bool(r) and "could not look" in r["text"],
          "an empty pipeline list is could-not-look, never 'not in the pipeline': %s" % (r or {}).get("text"))
    os.environ["RM_CONTROL_MODS"] = LIVE_MODS
    with open(SW, "w") as f:
        f.write("{torn")
    r = P.switch_refusal(job)
    check(bool(r) and "could not look" in r["text"],
          "an unreadable switch file refuses even a live mod, with 'could not look': %s" % (r or {}).get("text"))
    switch(False)
    os.environ.pop("RM_CONTROL_MODS", None)


def t_filler_live_mods():
    plant()
    T.ensure_dirs()
    p = T.fill_plan(LIVE, 4, 200, now=1795640000.0)
    check(p["verdict"] != "switched", "fill_plan: the filler may pick for a live mod on the switched host: %s" % p["verdict"])
    p = T.fill_plan("Nowhere", 4, 200, now=1795640000.0)
    check(p["verdict"] == "switched" and "not live" in p["text"],
          "fill_plan: the filler queues nothing for a mod that is not live: %s" % p)
    p = T.fill_plan("OffMod", 4, 200, now=1795640000.0)
    check(p["verdict"] in ("switched", "held"), "fill_plan: nothing for an OFF mod: %s" % p["verdict"])
    # the steward: only when EVERY filler mod is refused is the lane SWITCHED (settled); a live mod's gap is its own state
    import steward as ST
    ST.tick_timer_state = lambda: "active"
    ls = ST.lane_state(1795640000.0, mods=["Nowhere"])
    check(ls["state"] == "SWITCHED" and ls["settled"], "the steward: a lane whose mods are all refused is SWITCHED: %s" % ls["state"])
    ls = ST.lane_state(1795640000.0, mods=["Nowhere", LIVE])
    check(ls["state"] != "SWITCHED", "the steward: a live mod beside a refused one keeps its own state: %s" % ls["state"])
    switch(False)
    os.environ.pop("RM_CONTROL_MODS", None)

def main():
    t_admission()
    t_filler()
    t_rerun_line()
    t_live_mod_admitted()
    t_not_live_stays_refused()
    t_unreadable_state_refused()
    t_filler_live_mods()
    print("FAILED %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
