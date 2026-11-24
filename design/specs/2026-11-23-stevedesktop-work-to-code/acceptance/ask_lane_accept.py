#!/usr/bin/env python3
"""Contract: `testq.py ask`, and the host facts file it reads first.

  src/RimMandrake/Utils/testq/host_facts.py
    read(path, now) -> {"age_s", "stale", "facts"}; older than MAX_AGE_S (2 h) is stale; a missing file reads {"stale": True, "facts": None}.
    lacks(need, facts, stale) -> [(kind, name, word)] with word "absent" or "could not look". need: {"mods": [packageIds],
        "saves": [names], "python": [modules], "companion": srchash}. facts: {"mods": [..], "saves": [..], "python": {module: bool},
        "companions": [srchash], "free_gb": n, "logins": {account: seconds left}}. Stale or missing facts give "could not look" only.
  src/RimMandrake/Utils/testq/ask.py
    plan(item, facts, stale, live_proofs, table, tiers) -> {"verdict": "ASK"|"CANNOT"|"COULD NOT LOOK", "argv": [...], "why": [...]}
        argv is the whole `submit` command line for the item, with nothing left for the agent but --purpose.
        A chain the lane has no driver for (its check says "live check owed" or needs a proof build the lane cannot make) is CANNOT.
    exit codes of `testq.py ask`: 0 asked, 3 the lane cannot run it (named), 4 could not look.
"""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kit

FACTS = {"mods": ["a.b"], "saves": ["NS_x"], "python": {"numpy": True, "lxml": False}, "companions": ["h1"], "free_gb": 800, "logins": {"lukas": 9}}


def H():
    import host_facts
    return host_facts


def A():
    import ask
    return ask


def age():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "f.json")
    json.dump({"at": 1000, "facts": FACTS}, open(p, "w"))
    a, b, c = H().read(p, 1000 + 60), H().read(p, 1000 + H().MAX_AGE_S + 1), H().read(os.path.join(d, "no"), 5)
    return (a["stale"], b["stale"], c["stale"], c["facts"]) == (False, True, True, None)


def plan(**kw):
    base = dict(item="SOME_ITEM", facts=FACTS, stale=False, live_proofs={"A1": "python.exe x.py"}, table={}, tiers={"mods__base": ["a.b"]})
    base.update(kw)
    return A().plan(**base)


def help_has_ask():
    r = subprocess.run([sys.executable, os.path.join(_kit.TESTQ, "testq.py"), "ask", "--help"], capture_output=True, text=True, timeout=60)
    return r.returncode == 0


sys.exit(_kit.run([
    ("an old or absent reading is stale, never facts", age),
    ("a mod that is not there is absent", lambda: H().lacks({"mods": ["c.d"]}, FACTS, False) == [("mods", "c.d", "absent")]),
    ("a save that is not there is absent", lambda: H().lacks({"saves": ["NS_y"]}, FACTS, False) == [("saves", "NS_y", "absent")]),
    ("a python package that is not there is absent", lambda: H().lacks({"python": ["lxml"]}, FACTS, False) == [("python", "lxml", "absent")]),
    ("everything there lacks nothing", lambda: H().lacks({"mods": ["a.b"], "saves": ["NS_x"], "python": ["numpy"], "companion": "h1"}, FACTS, False) == []),
    ("stale facts could not look, and never say absent", lambda: {x[2] for x in H().lacks({"mods": ["c.d"], "saves": ["NS_x"]}, FACTS, True)} == {"could not look"}),
    ("an item with a proof line is asked whole", lambda: plan()["verdict"] == "ASK" and "--for-item" in plan()["argv"] and "--sha" in plan()["argv"] and "--proofs" in plan()["argv"]),
    ("a tier mod the host lacks is CANNOT, named", lambda: plan(tiers={"mods__base": ["a.b", "c.d"]})["verdict"] == "CANNOT" and "c.d" in str(plan(tiers={"mods__base": ["a.b", "c.d"]})["why"])),
    ("a check with no driver is CANNOT, not sent", lambda: plan(live_proofs={}, table={"P": {"live_check_owed": True}})["verdict"] == "CANNOT"),
    ("stale facts are COULD NOT LOOK, not CANNOT", lambda: plan(stale=True)["verdict"] == "COULD NOT LOOK"),
    ("`testq.py ask` exists", help_has_ask),
]))
