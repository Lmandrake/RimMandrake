#!/usr/bin/env python3
"""selftest_criteria_fixer.py - the neutral criteria fixer and its guard (RIMMANDRAKE_BUILD_NEUTRAL_CRITERIA_FIXER_WITH_GUARD,
T5 of design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md section 2).

diffguard classifies a criterion change (tighten / clarify / replace / fixture / loosen), refuses a loosen with no card
or second read, refuses any touch of an owner bar (a north-star or L4 clause), and refuses a repair after which the
known-bad case passes. repair builds the fixer's packet from roles/criteria_fixer.md WITHOUT the builder's arguments or
the item's stakes, launches it (stubbed here), guards its answer and records it whole. No model, no network."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import refusal_contract as RC  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


OLD = {"wall_stop": "a thrown item stops at a wall; at least 3 trials, each with a control blast and no wall",
       "throw_range": "steel lands at most 4 cells out from a frag grenade",
       "ns_root": "North star: knockback never kills a pawn by itself"}
BARS = ["ns_root"]


def classes(res):
    return {c["clause"]: c["class"] for c in res["changes"]}


def main():
    g = RC.diffguard(OLD, dict(OLD), owner_bars=BARS)
    check("no change -> ok, nothing classed", g["ok"] and g["changes"] == [], g)
    new = dict(OLD, wall_stop=OLD["wall_stop"].replace("at least 3", "at least 5"))
    g = RC.diffguard(OLD, new, owner_bars=BARS)
    check("a lower bound raised is tighten, allowed", g["ok"] and classes(g) == {"wall_stop": "tighten"}, g)
    new = dict(OLD, wall_stop=OLD["wall_stop"].replace("at least 3", "at least 2"))
    g = RC.diffguard(OLD, new, owner_bars=BARS)
    check("a lower bound lowered is loosen, refused without a card or second read",
          not g["ok"] and classes(g) == {"wall_stop": "loosen"} and "loosen" in " ".join(g["errors"]), g)
    g = RC.diffguard(OLD, new, owner_bars=BARS, second_read="gpt_consult 2026-11-12 wall_stop: agrees")
    check("the same loosen with a second-read reference is allowed", g["ok"], g)
    new = dict(OLD, throw_range=OLD["throw_range"].replace("at most 4", "at most 6"))
    check("an upper bound raised is loosen", classes(RC.diffguard(OLD, new, owner_bars=BARS)) == {"throw_range": "loosen"})
    new = dict(OLD, wall_stop="a thrown item stops at a wall; at least 3 trials")
    g = RC.diffguard(OLD, new, owner_bars=BARS)
    check("a dropped control is loosen", classes(g) == {"wall_stop": "loosen"} and not g["ok"], g)
    new = {k: v for k, v in OLD.items() if k != "throw_range"}
    check("a removed clause is loosen", classes(RC.diffguard(OLD, new, owner_bars=BARS)) == {"throw_range": "loosen"})
    new = dict(OLD, ns_root="North star: knockback never kills a pawn by itself, except in deep water")
    g = RC.diffguard(OLD, new, owner_bars=BARS, card="any")
    check("an owner bar touched is refused even with a card reference: it goes to him",
          not g["ok"] and "owner bar" in " ".join(g["errors"]), g)
    new = dict(OLD, throw_range="steel lands at most 4 cells out from a frag grenade (cells counted from the blast centre)")
    check("wording added with the same numbers and controls is clarify",
          classes(RC.diffguard(OLD, new, owner_bars=BARS)) == {"throw_range": "clarify"})
    new = dict(OLD, wall_stop="a thrown item never crosses a wall cell; at least 3 trials, each with a control blast")
    check("a rewritten clause keeping its numbers and controls is replace",
          classes(RC.diffguard(OLD, new, owner_bars=BARS)) == {"wall_stop": "replace"})
    new = dict(OLD, throw_range=OLD["throw_range"] + "; at least 2 trials")
    check("a new clause or added bound is tighten",
          classes(RC.diffguard(OLD, dict(new, extra="the steel stack keeps its count")))["extra"] == "tighten")
    g = RC.diffguard(OLD, dict(OLD, wall_stop=OLD["wall_stop"] + " at zoom 1"), owner_bars=BARS, bad_passes=True)
    check("a repair after which the known-bad case passes is refused", not g["ok"]
          and "known-bad" in " ".join(g["errors"]), g)
    g = RC.diffguard(OLD, dict(OLD, wall_stop=OLD["wall_stop"] + " at zoom 1"), owner_bars=BARS, good_passes=False)
    check("a repair after which the known-good case fails is refused", not g["ok"]
          and "known-good" in " ".join(g["errors"]), g)

    with tempfile.TemporaryDirectory() as root:
        os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "store"), RM_OPS_WATCH_DIR=os.path.join(root, "ops"),
                          RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
        os.makedirs(os.path.join(root, "ops"))
        refusal = {"clause": "wall_stop", "observed": "no scene has a wall", "would_pass": "a scene with a wall",
                   "criterion_verdict": "unattainable", "criterion_why": "walls cannot be spawned on the test map here"}
        case = {"item": "FOO", "clause": "wall_stop", "criteria": OLD, "owner_bars": BARS,
                "source": "owner 2026-11-01: thrown things must not pass walls",
                "refusals": [refusal], "evidence": ["scenes.json: sc_throw has no wall"],
                "calibration": {"good": "sc_wall: steel stops west of the wall", "bad": "sc_none: steel crosses"},
                "builder_says": "THIS SHOULD PASS, the scene is fine", "priority": "urgent ship blocker"}
        seen = []

        def runner(prompt, timeout):
            seen.append(prompt)
            return {"new_text": "a thrown item never crosses a wall cell the scene builds itself; at least 3 "
                                "trials, each with a control blast and no wall",
                    "class": "replace", "why": "walls are built by the scene, not spawned", "second_read": ""}
        res = RC.repair(case, runner=runner, now=1794550000)
        p = seen[0] if seen else ""
        check("the fixer is given the clause, its source line, the refusals, the evidence and the calibration cases",
              all(w in p for w in ("wall_stop", "thrown things must not pass walls", "no scene has a wall",
                                   "sc_throw has no wall", "sc_wall")), p[-500:])
        check("the fixer is NOT given the builder's arguments or the item's stakes",
              "THIS SHOULD PASS" not in p and "urgent ship blocker" not in p, p[-300:])
        check("the fixer's brief is roles/criteria_fixer.md and frames no pass as success",
              "known-bad case fails and the known-good case passes" in p, p[:400])
        check("a guarded replace is accepted, class replace, and a rejudge is due by a fresh instance of the same brief",
              res["ok"] and res["class"] == "replace" and res["rejudge"] == "fresh instance, same brief", res)
        check("the repair is recorded whole in the store with the note text for the item",
              res.get("pointer") and "criteria repair wall_stop: replace" in res["note"], res)
        rows = [json.loads(x) for x in open(os.path.join(root, "store", "refusals.jsonl"))]
        check("the store row holds the old and new text whole",
              any(r.get("kind") == "repair" and r["old"] == OLD["wall_stop"] and r["new"].startswith("a thrown item never crosses")
                  for r in rows), rows[-1:])

        def loosener(prompt, timeout):
            return {"new_text": "a thrown item stops at a wall", "class": "clarify", "why": "simpler", "second_read": ""}
        res = RC.repair(case, runner=loosener, now=1794550001)
        check("a fixer that loosens while calling it clarify is refused by the guard, and nothing is rejudged",
              not res["ok"] and res["class"] == "loosen" and not res.get("rejudge"), res)
        res = RC.repair(dict(case, clause="ns_root"), runner=runner, now=1794550002)
        check("an owner-bar clause is never sent to the fixer: it is a card for him",
              not res["ok"] and res.get("card") and len(seen) == 1, res)
    print("selftest_criteria_fixer: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
