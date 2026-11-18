#!/usr/bin/env python3
"""Selftest of the owner's hold (mod_owner_hold.py; item RIMMANDRAKE_HOLD_SIX_BIOME_MODS_ONLY_PYRELANDS_STAYS). The owner,
2026-11-16: "And stop the new biome mods work. Only Pyrelands as a biome mod right now." A held mod: the Dispatch tick
launches nothing on it (decide, the steward layer and the pilot holders never see it), the Designer chain sweep, the
harvest chain and a pending run-now skip it, the Designer stall reader and the idle reading leave it out, and status
prints HELD BY OWNER with his words, date and the lift command. Unheld mods are untouched. Pure: temp files, fakes."""
import json
import os
import stat
import sys
import tempfile
import time

import re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
FAILS = []
SIX = ("Contagion", "Cauldron", "FeverWood", "GelatinousSlime", "LeaningScrub", "Stillsand")
# the 2026-11-16 ruling names only Pyrelands as never held; any other mod he may hold later (Graffiti, 2026-11-18)
UNTOUCHED = ("Pyrelands", "PyrelandsMechanics")
WORDS = "And stop the new biome mods work. Only Pyrelands as a biome mod right now."


def check(ok, msg):
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def temp_holds(mods):
    p = os.path.join(tempfile.mkdtemp(prefix="owner_hold_"), "mod_owner_hold.json")
    with open(p, "w") as f:
        json.dump({"holds": [{"mod": m, "date": "2026-11-16", "said": WORDS} for m in mods]}, f)
    os.environ["RM_OWNER_HOLD_FILE"] = p
    return p


def test_the_shipped_list():
    import mod_owner_hold as OH
    os.environ.pop("RM_OWNER_HOLD_FILE", None)
    hs = OH.load()
    check(set(SIX) <= set(hs), "owner_hold.json holds the six biome mods: %s" % sorted(hs))
    check(not any(OH.held(m, hs) for m in UNTOUCHED), "Pyrelands, PyrelandsMechanics: not held")
    check(all("Only Pyrelands" in hs[m]["said"] and hs[m]["date"] == "2026-11-16" for m in SIX if m in hs),
          "each of the six carries his words and the date 2026-11-16")
    check(all(h.get("said") and re.fullmatch(r"\d{4}-\d\d-\d\d", h.get("date") or "") for h in hs.values()),
          "every hold carries his words and a date")
    check(OH.held("/home/x/design/concepts/Cauldron/", hs) and OH.held("RimMandrake/Stillsand", hs),
          "a concept path or a RimMandrake/ name matches by its last part")
    s = OH.status(hs["Cauldron"])
    check(s.startswith("HELD BY OWNER 2026-11-16") and "owner_hold.py lift Cauldron" in s, "status line: %s" % s)


def test_unreadable_raises():
    import mod_owner_hold as OH
    p = temp_holds([])
    with open(p, "w") as f:
        f.write("{not json")
    try:
        OH.load()
        check(False, "an unparsable hold file raises Unreadable")
    except OH.Unreadable:
        check(True, "an unparsable hold file raises Unreadable (never a calm 'no holds')")
    with open(p, "w") as f:
        json.dump({"holds": [{"mod": "X", "date": "2026-11-16"}]}, f)
    try:
        OH.load()
        check(False, "a hold without his words raises")
    except OH.Unreadable:
        check(True, "a hold without his words raises Unreadable")


def test_lift():
    import mod_owner_hold as OH
    p = temp_holds(["ModOne", "ModTwo"])
    OH.lift("ModOne", "lift it")
    hs = OH.load()
    check(sorted(hs) == ["ModTwo"] and json.load(open(p))["lifted"][0]["lifted_said"] == "lift it",
          "lift removes one mod and keeps the record of his lifting words")


def test_allow_design():
    """A design-only pass on a held mod (designer_cleanse.py run): his words on the hold row; the hold stays."""
    import mod_owner_hold as OH
    os.environ.pop("RM_OWNER_HOLD_FILE", None)
    hs = OH.load()
    check(all(OH.design_allowed(h) and "dispatch it on every remaining biome" in OH.design_allowed(h)["said"]
              and OH.design_allowed(h)["date"] == "2026-11-16" for m, h in hs.items() if m in SIX),
          "the six shipped holds carry his words allowing the design-only pass (2026-11-16)")
    p = temp_holds(["ModOne", "ModTwo"])
    row = OH.allow_design("ModOne", "design it", date="2026-11-16")
    hs = OH.load()
    check(row["design_allowed"] == {"said": "design it", "date": "2026-11-16"} and sorted(hs) == ["ModOne", "ModTwo"],
          "allow-design writes his words and date on the row and lifts nothing")
    check(OH.design_allowed(hs["ModOne"]) and not OH.design_allowed(hs["ModTwo"]), "only that row reads allowed")
    check(OH.main(["allow-design", "Nope", "--said", "x"]) == 1, "allow-design on an unheld mod exits 1")
    check(OH.main(["allow-design", "ModTwo", "--said", " "]) == 1, "allow-design with empty words exits 1")
    check(json.load(open(p))["holds"][1].get("design_allowed") is None, "a refused allow-design writes nothing")


def test_write_safety():
    """A malformed allowance or a twice-held mod is Unreadable; a failed write leaves the file whole; two writers at
    once lose neither change (the read-change-write step is under one lock)."""
    import threading
    import types
    import mod_owner_hold as OH
    p = temp_holds(["ModOne"])
    for bad, what in (({"said": "yes"}, "an allowance without a date"), ({"said": " ", "date": "2026-11-16"},
                      "an allowance with empty words"), ("yes", "an allowance that is not a row")):
        doc = json.load(open(p))
        doc["holds"][0]["design_allowed"] = bad
        json.dump(doc, open(p, "w"))
        try:
            OH.load()
            check(False, "%s raises Unreadable" % what)
        except OH.Unreadable:
            check(True, "%s raises Unreadable" % what)
    p = temp_holds(["Cauldron", "design/concepts/Cauldron"])
    try:
        OH.load()
        check(False, "one mod held twice (two spellings) raises Unreadable")
    except OH.Unreadable:
        check(True, "one mod held twice (two spellings) raises Unreadable")
    p = temp_holds(["ModOne", "ModTwo"])
    before = open(p).read()
    real = OH.json

    def boom(*a, **k):
        raise OSError("disk full")
    OH.json = types.SimpleNamespace(load=real.load, dump=boom)
    try:
        OH.allow_design("ModOne", "design it", date="2026-11-16")
        check(False, "a write that fails raises")
    except OSError:
        check(open(p).read() == before and not [f for f in os.listdir(os.path.dirname(p)) if f.startswith(".mod_")],
              "a write that fails mid-way leaves the file byte-identical and no temp file behind")
    finally:
        OH.json = real
    # GPT review 2026-11-17 (a_hold2): a blank date, or a change that leaves no hold list, never replaces the file;
    # the rename is fsynced in its folder
    p = temp_holds(["ModOne", "ModTwo"])
    before = open(p).read()
    for d in ("", "  ", 7):
        try:
            OH.allow_design("ModOne", "design it", date=d)
            check(False, "allow-design with date %r refuses" % (d,))
        except ValueError:
            check(open(p).read() == before, "allow-design with date %r refuses and writes nothing" % (d,))
    try:
        OH._rewrite(p, lambda doc: doc.update(holds="none"))
        check(False, "a change that leaves no hold list raises")
    except OH.Unreadable:
        check(open(p).read() == before and not [f for f in os.listdir(os.path.dirname(p)) if f.startswith(".mod_")],
              "a change that leaves no hold list raises Unreadable; the file is byte-identical, no temp file left")
    synced, real_fsync = [], os.fsync

    def spy(fd):
        # fstat, not /proc/self/fd: /proc exists only on Linux, so the old probe answered False for EVERY fd on a
        # Mac and this check read FAIL ([False, False]) while measuring nothing about the fsync order
        # (measured 2026-11-17 on the Desktop). An instrument that cannot see must not return a verdict.
        synced.append(stat.S_ISDIR(os.fstat(fd).st_mode))
        return real_fsync(fd)
    os.fsync = spy
    try:
        OH.allow_design("ModTwo", "design it", date="2026-11-16")
    finally:
        os.fsync = real_fsync
    check(synced == [False, True], "a write fsyncs the new file, then its folder after the rename (%s)" % synced)
    mods = ["Mod%d" % i for i in range(8)]
    temp_holds(mods)

    def slow_load(f):
        doc = real.load(f)
        time.sleep(0.05)        # widen the read-to-write window so an unlocked writer would lose updates every time
        return doc
    OH.json = types.SimpleNamespace(load=slow_load, dump=real.dump)
    try:
        ts = [threading.Thread(target=OH.allow_design, args=(m, "design " + m), kwargs={"date": "2026-11-16"})
              for m in mods]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
    finally:
        OH.json = real
    hs = OH.load()
    got = sum(1 for m in mods if OH.design_allowed(hs[m]))
    check(got == len(mods), "8 writers at once: %d of %d allowances kept (worst case read: 8 rows)" % (got, len(mods)))


def test_designer_chain():
    import selftest_designer_chain as DC
    RL = DC.RL
    temp_holds(["ModOne"])
    old = DC.T - 4 * 3600
    rows = [(DC.C1, {"stage": 2, "status": "ready"}, old)]
    st, acts, opened = DC.sweep_decide(rows)
    check(opened == [] and not st["roles"].get("Arbiter", {}).get("run_now")
          and not any(a.get("do") == "alarm" for a in acts),
          "the chain sweep asks no run on a held ready concept and raises no alarm: %r %r" % (
              opened, [(a.get("do"), a.get("kind")) for a in acts]))
    st, acts, opened = DC.sweep_decide([(DC.C2, {"stage": 2, "status": "ready"}, old)])
    check(opened == [DC.C2], "an unheld concept is still swept and launched (%r)" % opened)
    rej = [(DC.C1, {"stage": 3, "status": "ready", "results": [
        {"outcome": "rejected", "why": ["x: source path no/such/file.json does not exist"]}]}, old)]
    st, acts, opened = DC.sweep_decide(rej)
    check(not any("parked" in str(a.get("kind")) for a in acts), "a held rejected concept raises no parked alarm")
    # a run-now already pending on a held concept is refused at launch, said once, no alarm
    rs = {"done": {}, "runs": [], "run_now": {"at": DC.T, "by": "Dispatcher", "why": "chain", "mode": "run",
                                              "concept": DC.C1}}
    st, acts, opened = DC.sweep_decide([], {"Arbiter": rs})
    last = st["roles"]["Arbiter"].get("run_now_last") or {}
    check(opened == [] and "owner hold" in str(last.get("outcome")) and not any(a.get("do") == "alarm" for a in acts),
          "a pending run-now on a held concept is refused (owner hold), not launched: %r" % last.get("outcome"))
    # the harvest's chain: an accepted close leaving a held concept ready chains nothing
    rs = {"done": {}, "runs": []}
    acts = DC.harvest(rs, {"stage": 3, "status": "ready"})
    check(not rs.get("run_now") and not rs.get("run_now_queue"), "a harvested close on a held concept chains nothing")
    # an unreadable hold file: no concept is chained, one alarm per outage
    p = os.environ["RM_OWNER_HOLD_FILE"]
    with open(p, "w") as f:
        f.write("{")
    st, acts, opened = DC.sweep_decide([(DC.C2, {"stage": 2, "status": "ready"}, old)])
    check(opened == [] and any("owner_hold" in str(a.get("kind")) for a in acts),
          "an unreadable hold file chains nothing and alarms: %r" % [a.get("kind") for a in acts])
    del RL


def test_stall_reader():
    import ops_watch as OW
    root = tempfile.mkdtemp(prefix="owner_hold_concepts_")
    for m in ("ModOne", "ModTwo"):
        os.makedirs(os.path.join(root, m))
        with open(os.path.join(root, m, "stage.json"), "w") as f:
            json.dump({"stage": 2, "status": "ready", "history": [{"at": "2026-11-16T01:00:00Z"}]}, f)
    temp_holds(["ModOne", "ModTwo"])
    out = OW._q_designer({"root": root, "runs_dir": root}, 1794880000, {}, None)
    temp_holds(["ModOne"])
    out1 = OW._q_designer({"root": root, "runs_dir": root}, 1794880000, {}, None)
    temp_holds([])
    out0 = OW._q_designer({"root": root, "runs_dir": root}, 1794880000, {}, None)
    check(repr(out) != repr(out0) and repr(out1) != repr(out), "the Designer stall reader leaves held concepts out "
          "(all held %r; one held %r; none held %r)" % (out, out1, out0))


def test_dispatch_tick():
    import maturation_dispatch as MD
    import maturation_autonomy as AUT
    temp_holds(list(SIX))
    sd = tempfile.mkdtemp(prefix="owner_hold_dispatch_")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = sd
    seen = {}
    saved = (MD.decide, AUT.widen, AUT.resolve, MD.pilot_holders)

    def decide(cfg, st, facts, now, account=None, bridge=None, releases=None):
        seen["decide"] = list(cfg["advancing"])
        rows = [{"mod": m, "stage": "offline_build", "decision": "launch", "why": "fake: owed", "owed": "build"}
                for m in cfg["advancing"]]
        return rows, list(cfg["advancing"])

    def resolve(root, cfg, st, facts, rows, launches, now, fx):
        seen["resolve"] = [r["mod"] for r in rows]
        return rows, launches

    def holders(root, cfg, st, facts, rows, launches, now, fx=None):
        seen["holders"] = [r["mod"] for r in rows]
        return rows, launches
    every = list(SIX) + list(UNTOUCHED)
    try:
        MD.decide, MD.pilot_holders = decide, holders
        AUT.widen = lambda root, cfg, st, apply, fx=None: dict(cfg, advancing=every)
        AUT.resolve = resolve
        facts = {m: {"stage": "offline_build", "live_units": ["rm-detached-x-1"] if m == "Contagion" else []}
                 for m in every}
        fx = {"autonomy": True, "facts": lambda: facts, "account": lambda: (True, ""), "releases": lambda: [],
              "convergence": lambda root, rd: rd, "code": lambda: "tree"}
        # slots for all six beside Contagion's live run: this asks whether a hold stops the unheld, not how many slots
        # there are. The fake decide ignores max_live, and prioritise (RIMMANDRAKE_LAUNCH_PYRELANDS_FIRST_AT_ONE_SLOT)
        # enforces it after every layer, so at the shipped max_live 1 the held mod's live run fills the slot.
        rd = MD.tick(HERE, dict(MD.load_cfg(), advancing=["Pyrelands", "Contagion"], max_live=len(UNTOUCHED) + 1),
                     False, fx=fx, now=1794880000, page=False)
    finally:
        MD.decide, AUT.widen, AUT.resolve, MD.pilot_holders = saved
    check(sorted(seen.get("decide") or []) == sorted(UNTOUCHED),
          "decide sees only the unheld mods, the widened Designer concepts included: %r" % seen.get("decide"))
    check(sorted(seen.get("resolve") or []) == sorted(UNTOUCHED) and sorted(seen.get("holders") or [])
          == sorted(UNTOUCHED), "the steward layer and the pilot holders never see a held mod")
    m = rd["mods"]
    check(all(m[x]["decision"] == "owner_hold" and m[x].get("klass") == "held"
              and str(m[x].get("status")).startswith("HELD BY OWNER 2026-11-16") for x in SIX),
          "every held mod reads owner_hold / held / HELD BY OWNER 2026-11-16: %r" % {x: m.get(x, {}).get("decision")
                                                                                    for x in SIX})
    check("allowed to finish" in str(m["Contagion"].get("status")),
          "a held mod's live run is named as allowed to finish: %s" % m["Contagion"].get("status"))
    check(all(m[x]["decision"] == "would_launch" for x in UNTOUCHED), "the unheld six still launch (dry run): %r"
          % {x: m[x]["decision"] for x in UNTOUCHED})
    check(not any(x in str(rd.get("idle_owed_mods")) + str(rd.get("needs_conductor")) + str(rd.get("stalled"))
                  + str(rd.get("paused")) for x in SIX), "no held mod in the idle, Needs Conductor, stalled or paused "
          "lists")
    lines = MD.status_lines(rd, 1794880000, unit_state=lambda u: "active")
    held_lines = [ln for ln in lines if "HELD BY OWNER" in ln]
    check(len(held_lines) == 6 and all("Only Pyrelands" in ln and "lift" in ln for ln in held_lines),
          "status prints six HELD BY OWNER lines with his words and the lift command")


def main():
    for t in (test_the_shipped_list, test_unreadable_raises, test_lift, test_allow_design, test_write_safety, test_designer_chain, test_stall_reader,
              test_dispatch_tick):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    os.environ.pop("RM_OWNER_HOLD_FILE", None)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
