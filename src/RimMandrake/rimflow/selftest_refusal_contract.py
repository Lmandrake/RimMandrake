#!/usr/bin/env python3
"""selftest_refusal_contract.py - the refusal record, its check, the repeat cache and the counters
(RIMMANDRAKE_BUILD_REFUSAL_CONTRACT_CHECK_AND_CACHE, spec design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md).

Good: a well-formed verdict is stored whole and counted. Malformed: each defect class is refused with its reason and does
not count against the item; a second one from the same brief alarms the family. Repeat: the same refusal on unchanged
evidence at the same sha is answered from the cache and never counted; changed evidence is judged again. Counters: the
3rd refusal of one clause is due for repair, the 4th refused verdict alarms the item and stops judging; a family rate
trips at >70% of 20 and at all of 8 across 3 items, and a healthy family does not. Every write goes to a temp dir."""
import copy
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import incident  # noqa: E402
import refusal_contract as RC  # noqa: E402

FAILS = []
CRIT = {"C1": "the knockback scene pushes a pawn at least 3 cells", "C2": "the log holds no red error"}


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def given(root):
    return {"root": root, "criteria": dict(CRIT), "inputs": ["scene.log", "player.log"]}


def good(item="ITEM_A", family="scene_look", sha="abc123", ev="scene.log:2"):
    return {"item": item, "family": family, "sha": sha,
            "passed": [{"clause": "C2", "evidence": ["player.log"]}],
            "refusals": [{"clause": "C1", "criterion_hash": RC.criterion_hash(CRIT["C1"]), "evidence": [ev],
                          "observed": "pawn displaced 1 cell after the blast",
                          "would_pass": "scene.log shows displaced >= 3 cells for pawn Kira after BlastAt",
                          "smallest_fix": {"what": "raise KnockbackForce in RM_ExplosiveKnockback def to 6",
                                           "attainable": "yes", "cost": "edit"},
                          "criterion_verdict": "sound",
                          "criterion_why": "Three cells is what the owner's line asks and the scene can show it."}]}


def write(root, name, text):
    with open(os.path.join(root, name), "w") as f:
        f.write(text)


def malformed(root):
    g = given(root)
    cases = {
        ("a required field missing", "would_pass is missing"): lambda v: v["refusals"][0].pop("would_pass"),
        ("an empty phrase as would_pass", "says nothing checkable"): lambda v: v["refusals"][0].update(would_pass="does not pass, needs more work"),
        ("would_pass restating the clause", "restates the clause"): lambda v: v["refusals"][0].update(would_pass=CRIT["C1"]),
        ("evidence not among the given inputs", "not one of the inputs"): lambda v: v["refusals"][0].update(evidence=["other.log:1"]),
        ("evidence lines outside the file", "lines outside"): lambda v: v["refusals"][0].update(evidence=["scene.log:40"]),
        ("observed quoting nothing of the evidence", "quotes no token"): lambda v: v["refusals"][0].update(observed="seems wrong to me"),
        ("a stale criterion hash", "criterion_hash"): lambda v: v["refusals"][0].update(criterion_hash="0" * 16),
        ("a clause outside the criterion set", "not in the criterion set"): lambda v: v["refusals"][0].update(clause="C9"),
        ("a bad criterion_verdict enum", "criterion_verdict is not one of"): lambda v: v["refusals"][0].update(criterion_verdict="meh"),
        ("smallest_fix with no cost class", "cost is not one of"): lambda v: v["refusals"][0]["smallest_fix"].pop("cost"),
        ("a clause left unjudged (coverage)", "neither passed nor refused"): lambda v: v.update(passed=[]),
        ("a given input in no evidence (coverage)", "in no passed or refused"): lambda v: v["passed"][0].update(evidence=[]),
        ("a clause both passed and refused", "both passed and refused"): lambda v: v["passed"].append({"clause": "C1", "evidence": []}),
    }
    for (name, why), mut in cases.items():
        v = good()
        mut(v)
        errs = RC.check(v, g)
        check("malformed: %s is refused for that reason" % name, any(why in e for e in errs), errs)
    check("good: the well-formed verdict has no errors", RC.check(good(), g) == [], RC.check(good(), g))
    v = good()
    v["refusals"][0].pop("new_since", None)
    check("new_since: optional on the first refusal, required after", RC.check(v, g, prior=0) == []
          and any("new_since" in e for e in RC.check(v, g, prior=1)), RC.check(v, g, prior=1))
    v["refusals"][0]["new_since"] = "unfixed:C1"
    check("new_since: unfixed:<clause> accepted", RC.check(v, g, prior=1) == [], RC.check(v, g, prior=1))
    v["refusals"][0]["new_since"] = "maybe"
    check("new_since: an unknown tag refused", bool(RC.check(v, g, prior=1)))


def store_and_counts(root, ops):
    g = given(root)
    bad = good(item="ITEM_M")
    bad["refusals"][0]["would_pass"] = "insufficient"
    r1 = RC.submit(bad, g, now=1794000000)
    it = RC.counters()["items"]["ITEM_M"]
    check("a malformed verdict is stored but not counted against the item",
          not r1["ok"] and not r1["counted"] and it["refused"] == 0 and it["verdicts"] == 0 and not r1["alarms"],
          (r1, it))
    r2 = RC.submit(bad, g, now=1794000060)
    check("a second malformed verdict from one brief alarms the family (brief FAILED)",
          not r2["ok"] and [a["subject"] for a in r2["alarms"]] == ["family:scene_look"]
          and RC.counters()["items"]["ITEM_M"]["refused"] == 0, r2["alarms"])
    RC.clear("family:scene_look", "test reset")

    r = RC.submit(good(), g, now=1794001000)
    check("good: stored and counted, nothing cached, judging may go on",
          r["ok"] and r["counted"] and not r["cached"] and r["may_judge"] and not r["alarms"], r)
    with open(RC.records_path()) as f:
        rows = [json.loads(x) for x in f]
    whole = [x for x in rows if x.get("kind") == "refusal"]
    check("the record is stored whole (no cut), under a pointer", whole and whole[-1]["record"] == good()["refusals"][0]
          and RC.counters()["cache"][whole[-1]["key"]]["pointer"].startswith("refusals.jsonl:"))

    v2 = good()
    v2["refusals"][0]["new_since"] = "unfixed:C1"
    r = RC.submit(v2, g, now=1794002000)
    check("repeat: same clause, criterion, evidence and sha -> answered from the cache, not counted",
          r["ok"] and r["cached"] == ["C1"] and not r["counted"]
          and RC.counters()["items"]["ITEM_A"]["refused"] == 1, (r, RC.counters()["items"]["ITEM_A"]))
    pj = RC.prejudge("ITEM_A", "abc123", g)
    check("prejudge: the cached clause is not judged again", list(pj) == ["C1"], pj)
    check("prejudge: another sha has nothing cached", RC.prejudge("ITEM_A", "def456", g) == {})
    write(root, "scene.log", "BlastAt 10,10\npawn Kira displaced 2 cells\nend\n")
    check("prejudge: changed evidence content is judged again", RC.prejudge("ITEM_A", "abc123", g) == {})
    r = RC.submit(v2, g, now=1794003000)
    check("changed evidence: a new refusal, counted", r["counted"] and not r["cached"]
          and RC.counters()["items"]["ITEM_A"]["clauses"]["C1"] == 2, r)
    write(root, "scene.log", "BlastAt 10,10\npawn Kira displaced 2.5 cells\nend\n")
    r = RC.submit(v2, g, now=1794004000)
    check("the 3rd refusal of one clause: repair due and the item's alarm row",
          r["repair_due"] == ["C1"] and [a["subject"] for a in r["alarms"]] == ["item:ITEM_A"] and r["may_judge"] is False,
          r)
    RC.clear("item:ITEM_A", "criteria repaired")
    write(root, "scene.log", "BlastAt 10,10\npawn Kira displaced 2.7 cells\nend\n")
    v3 = copy.deepcopy(v2)
    v3["sha"] = "fff000"
    r = RC.submit(v3, g, now=1794005000)
    check("the 4th refused verdict on one item alarms it and stops judging",
          RC.counters()["items"]["ITEM_A"]["refused"] == 4 and "4 refused verdicts" in r["alarms"][0]["why"]
          and not RC.may_judge("ITEM_A"), r)
    told = [json.loads(x) for x in open(os.path.join(ops, "told.jsonl")) if RC.ALARM_ID in x]
    check("one told row per fresh trip (family, item, item after release)", len(told) == 3, len(told))
    ok = good(item="ITEM_P")
    ok["refusals"] = []
    ok["passed"] = [{"clause": "C1", "evidence": ["scene.log:2"]}, {"clause": "C2", "evidence": ["player.log"]}]
    r = RC.submit(ok, g, now=1794006000)
    check("a passing verdict counts as a verdict, not a refusal",
          r["ok"] and r["counted"] and RC.counters()["items"]["ITEM_P"] == {
              "refused": 0, "verdicts": 1, "clauses": {}, "malformed": {}}, RC.counters()["items"]["ITEM_P"])


def families(root):
    g = given(root)
    os.environ["RM_REFUSAL_DIR"] = os.path.join(root, "fam")
    for i in range(8):
        r = RC.submit(good(item="F_%d" % (i % 3), family="gate_x", sha="s%d" % i), g, now=1794100000 + i)
    check("a family refusing all of its last 8 across 3 items alarms", any(
        a["subject"] == "family:gate_x" for a in r["alarms"]), r["alarms"])
    trips = []
    for i in range(20):
        v = good(item="H_%d" % i, family="healthy", sha="h%d" % i)
        if i % 2:
            v["refusals"] = []
            v["passed"] = [{"clause": "C1", "evidence": ["scene.log:2"]}, {"clause": "C2", "evidence": ["player.log"]}]
        trips += [a for a in RC.submit(v, g, now=1794200000 + i)["alarms"] if a["subject"] == "family:healthy"]
    check("a family refusing 50% of its last 20 does not alarm", not trips, trips)
    hist = [{"item": "x%d" % (i % 2), "refused": i % 5 != 0} for i in range(20)]
    check("80% of the last 20 trips the rate even across 2 items", RC._family_trip(hist) is not None)
    hist = [{"item": "x", "refused": i % 10 >= 3} for i in range(20)]
    check("70% exactly does not trip (more than 70% does)", RC._family_trip(hist) is None, RC._family_trip(hist))
    rt = incident.route_of(incident.load_table(), RC.ALARM_ID)
    check("the alarm routes to the Conductor", rt and rt["reader"] == "Conductor" and rt.get("cause") == "refusals", rt)


def cli(root):
    p = os.path.join(root, "v.json")
    v = good()
    v["given"] = given(root)
    with open(p, "w") as f:
        json.dump(v, f)
    v["refusals"][0]["would_pass"] = "weak"
    q = os.path.join(root, "bad.json")
    with open(q, "w") as f:
        json.dump(v, f)
    check("cli: check exits 0 on a good verdict and 1 on a malformed one",
          RC.main(["check", p]) == 0 and RC.main(["check", q]) == 1)


def main():
    env = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE")}
    try:
        with tempfile.TemporaryDirectory() as root:
            ops = os.path.join(root, "ops")
            os.makedirs(ops)
            os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=ops,
                              RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
            write(root, "scene.log", "BlastAt 10,10\npawn Kira displaced 1 cell\nend\n")
            write(root, "player.log", "Loaded 13 mods\n")
            malformed(root)
            store_and_counts(root, ops)
            families(root)
            cli(root)
    finally:
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    print("selftest_refusal_contract: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
