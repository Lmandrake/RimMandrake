#!/usr/bin/env python3
"""Selftest: vv_laws.py, the written laws of the shipped-settings fuzz matrix (RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS).
Offline, no build, no game. Proves:
  L1  the committed FlowWorks and EmpirePursuit law lists lint clean, and each has laws and families
  L2  lint refuses each way a law can stop being checkable: assertion text gone, unknown matrix family, a family with
      no planted break, a source plant found 0 or 2 times, an unknown hook plant or mutation, a duplicate or bad id,
      a family with no law, no laws at all
  L3  an assertion text's {placeholders} match the real message, and a different message does not
  L4  name_failures names the law a red record's examples show; no examples -> [] (looked, none named)
  L5  judge: PROVEN only with a green baseline and a red planted run naming one of THIS family's laws; a red baseline,
      a green planted run, or a red by another family's law is NOT_PROVEN; a missing or timed-out record is UNMEASURED
Run: python3 src/RimMandrake/Utils/selftest_vv_laws.py
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vv_laws as V  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else detail))
    if not ok:
        FAILS.append(name)


SRC = {"a.cs": 'return $"pulse {p}: total volume {in0}->{in1}";\nreturn x > y;\nreturn $"pulse {p}: 0<=F<=D<=4 broken at {i}";\n', "b.cs": "dup;\ndup;\n",
       V.PROBE: 'Plant == "volume"'}


def read(rel):
    if rel not in SRC:
        raise OSError(rel)
    return SRC[rel]


GOOD = {"mod": "Mock", "laws": [
    {"id": "volume_in_equals_out", "family": "conservation", "matrix_family": "kernel_fuzz", "sentence": "Water is conserved.",
     "check": {"file": "a.cs", "text": "total volume {in0}->{in1}"}},
    {"id": "order_is_strict", "family": "order", "matrix_family": "seq_orders", "sentence": "Strict.",
     "check": {"file": "a.cs", "text": "return x > y;"}},
    {"id": "fill_within_depth", "family": "order", "matrix_family": "kernel_fuzz", "sentence": "Bounded.",
     "check": {"file": "a.cs", "text": "0<=F<=D<=4 broken at {i}"}}],
    "families": {"conservation": {"plant": {"kind": "hook", "name": "volume"}},
                 "order": {"plant": {"kind": "source", "file": "a.cs", "find": "return x > y;", "replace": "return x >= y;"}}}}
FAMS = ["kernel_fuzz", "seq_orders"]


def lint(doc, mutations=frozenset({"spacing off by a tick"})):
    return V.lint(doc, read=read, fams=FAMS, mutations=mutations)


def broken(f):
    d = copy.deepcopy(GOOD)
    f(d)
    return lint(d)


def main():
    probs = V.lint_all()
    check("L1 the committed law lists lint clean", probs == [], probs)
    for mod in V.LAW_FILES:
        d = V.load(mod)
        check("L1 %s has laws and families" % mod, len(d["laws"]) >= 4 and len(d["families"]) >= 3, (len(d["laws"]), len(d["families"])))
    check("L2 the mock lints clean (so each case below fails for its own reason)", lint(GOOD) == [], lint(GOOD))
    cases = {
        "assertion text gone": lambda d: d["laws"][0]["check"].__setitem__("text", "volume went somewhere"),
        "unknown matrix family": lambda d: d["laws"][0].__setitem__("matrix_family", "made_up"),
        "family with no planted break": lambda d: d["laws"][0].__setitem__("family", "nowhere"),
        "source plant found twice": lambda d: d["families"]["order"]["plant"].update(file="b.cs", find="dup;"),
        "source plant found nowhere": lambda d: d["families"]["order"]["plant"].update(find="return z;"),
        "unknown hook plant": lambda d: d["families"]["conservation"]["plant"].update(name="teleport"),
        "unknown mutation": lambda d: d["families"].__setitem__("conservation", {"plant": {"kind": "mutation", "name": "no such"}}),
        "duplicate id": lambda d: d["laws"][1].__setitem__("id", "volume_in_equals_out"),
        "bad id": lambda d: d["laws"][1].__setitem__("id", "Law 2"),
        "family with no law": lambda d: d["families"].__setitem__("extra", {"plant": {"kind": "hook", "name": "volume"}}),
        "no laws": lambda d: d.__setitem__("laws", []),
        "check file unreadable": lambda d: d["laws"][0]["check"].__setitem__("file", "gone.cs"),
    }
    for what, f in cases.items():
        check("L2 lint refuses: " + what, broken(f) != [], "accepted")
    rx = V.text_re("total volume {in0}->{in1}, +{ext} in")
    check("L3 placeholders match the real message", rx.search("pulse 7: total volume 12.5->13.5, +0 in, -0 sunk") is not None)
    check("L3 a different message does not match", rx.search("pulse 7: total mass 12.5->13.5") is None)
    rec = {"family": "kernel_fuzz", "failures": 3, "completed": 100, "examples": ["seed 4: pulse 2: total volume 1->2"]}
    check("L4 name_failures names the law", V.name_failures(rec, {"FlowWorks": GOOD}) == ["volume_in_equals_out"], V.name_failures(rec, {"FlowWorks": GOOD}))
    check("L4 no examples: looked, none named", V.name_failures(dict(rec, examples=[]), {"FlowWorks": GOOD}) == [])
    green = [{"failures": 0, "completed": 300, "exceptions": 0}]
    red_mine = [{"family": "kernel_fuzz", "failures": 9, "completed": 300, "examples": ["seed 1: total volume 3->4"]}]
    red_other = [{"family": "kernel_fuzz", "failures": 9, "completed": 300, "examples": ["seed 1: 0<=F<=D<=4 broken at 3"]}]
    GOOD["mod"] = "FlowWorks"
    check("L5 PROVEN: green baseline, red planted run by its own law", V.judge(GOOD, "conservation", green, red_mine)[0] == "PROVEN",
          V.judge(GOOD, "conservation", green, red_mine))
    check("L5 a red baseline proves nothing", V.judge(GOOD, "conservation", red_mine, red_mine)[0] == "NOT_PROVEN")
    check("L5 a green planted run is NOT_PROVEN", V.judge(GOOD, "conservation", green, green)[0] == "NOT_PROVEN")
    check("L5 a red by another law is never counted", V.judge(GOOD, "conservation", green, red_other)[0] == "NOT_PROVEN",
          V.judge(GOOD, "conservation", green, red_other))
    check("L5 no record is UNMEASURED", V.judge(GOOD, "conservation", [], red_mine)[0] == "UNMEASURED")
    check("L5 a timed-out run is UNMEASURED", V.judge(GOOD, "conservation", green, [dict(red_mine[0], timed_out=True)])[0] == "UNMEASURED")
    print("vv laws: %d failed" % len(FAILS) if FAILS else "vv laws: all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
