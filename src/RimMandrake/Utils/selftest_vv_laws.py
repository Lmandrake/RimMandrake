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
  L6  (Codex review 2026-11-18) zero work never proves: a baseline or planted run with no completed cases is UNMEASURED;
      examples are matched one at a time, so two unrelated messages never make one law's text; a no-op or missing
      source replacement and a family whose plant was removed are refused; a mutation run that times out is that
      family's UNMEASURED with its cause (the run still records); lint on an unreadable law file prints its problems
      and exits 1 instead of crashing
  L7  the clock: a run that answered nothing (no VERDICT line) exits non-zero and its reading says UNMEASURED; the reading
      is written after the runs; a timeout kills the child's whole process group
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
        "law in an undeclared family": lambda d: d["laws"][0].__setitem__("family", "nowhere"),
        "family whose plant was removed": lambda d: d["families"]["conservation"].pop("plant"),
        "no-op source plant": lambda d: d["families"]["order"]["plant"].update(replace="return x > y;"),
        "source plant without a replacement": lambda d: d["families"]["order"]["plant"].pop("replace"),
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
    # L6
    zero = [{"failures": 0, "completed": 0, "exceptions": 0}]
    check("L6 a baseline with no completed case is UNMEASURED", V.judge(GOOD, "conservation", zero, red_mine)[0] == "UNMEASURED",
          V.judge(GOOD, "conservation", zero, red_mine))
    check("L6 an empty baseline record is UNMEASURED", V.judge(GOOD, "conservation", [{}], red_mine)[0] == "UNMEASURED")
    check("L6 a planted red with no completed case is UNMEASURED",
          V.judge(GOOD, "conservation", green, [dict(red_mine[0], completed=0)])[0] == "UNMEASURED")
    split_ex = {"family": "kernel_fuzz", "failures": 2, "completed": 300, "examples": ["EXCEPTION total volume access", "pulse 3: {in0}->{in1} other"]}
    joined_doc = {"mod": "FlowWorks", "laws": [{"id": "volume_in_equals_out", "family": "conservation", "matrix_family": "kernel_fuzz",
                                                 "sentence": "x", "check": {"file": "a.cs", "text": "total volume {in0}->{in1}"}}]}
    split_ex["examples"] = ["seed 1: total volume access denied", "seed 2: 3->4 elsewhere"]
    check("L6 two unrelated examples never jointly match one law", V.name_failures(split_ex, {"FlowWorks": joined_doc}) == [],
          V.name_failures(split_ex, {"FlowWorks": joined_doc}))
    import subprocess as sp
    real_run = V.subprocess.run

    def boom(*a, **k):
        raise sp.TimeoutExpired(a[0] if a else "x", 1)
    V.subprocess.run = boom
    try:
        res = V.prove_ep({"mod": "EmpirePursuit", "laws": [], "families": {"fire_gate": {"plant": {"kind": "mutation", "name": "m"}}}}, log=lambda *a: None)
        check("L6 a mutation timeout is that family's UNMEASURED", res.get("fire_gate", {}).get("status") == "UNMEASURED"
              and "timed out" in res["fire_gate"]["why"], res)
    except Exception as ex:                              # noqa: BLE001 - an escape is the defect
        check("L6 a mutation timeout is that family's UNMEASURED", False, repr(ex))
    finally:
        V.subprocess.run = real_run
    import contextlib
    import io
    import tempfile
    keep = dict(V.LAW_FILES)
    bad = tempfile.mkdtemp()
    open(os.path.join(bad, "bad.json"), "w").write("{broken")
    V.LAW_FILES["FlowWorks"] = os.path.relpath(os.path.join(bad, "bad.json"), V.ROOT)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            code = V.main(["lint"])
        check("L6 lint on an unreadable law file prints the problem and exits 1", code == 1 and "unreadable" in buf.getvalue(), (code, buf.getvalue()[-200:]))
    except Exception as ex:                              # noqa: BLE001
        check("L6 lint on an unreadable law file prints the problem and exits 1", False, repr(ex))
    finally:
        V.LAW_FILES.clear()
        V.LAW_FILES.update(keep)
    # L7 the clock
    import vv_matrix_clock as C
    d7 = tempfile.mkdtemp()
    reading = os.path.join(d7, "last.json")
    real = (C.run, C.reading_path)
    calls = []

    def quiet(cmd, timeout):
        calls.append(cmd)
        assert not os.path.exists(reading), "reading written before the run"
        return 0, ""
    C.run, C.reading_path = quiet, (lambda: reading)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            code = C.main(["--prove"])
        import json as _j
        rd = _j.load(open(reading))
        check("L7 no answer: non-zero exit, UNMEASURED reading written after the runs", code != 0 and rd["matrix_verdict"].startswith("UNMEASURED")
              and rd["prove_line"].startswith("UNMEASURED") and len(calls) == 2, (code, rd))
    finally:
        C.run, C.reading_path = real
    import time as _t
    t0 = _t.time()
    rc, out = C.run(["sh", "-c", "sleep 30 & echo $! > %s/kid; sleep 30" % d7], 1)
    kid = int(open(os.path.join(d7, "kid")).read().strip())
    alive = True
    for _ in range(20):
        try:
            os.kill(kid, 0)
        except ProcessLookupError:
            alive = False
            break
        _t.sleep(0.1)
    check("L7 a timeout kills the whole process group", rc == 124 and not alive and _t.time() - t0 < 10, (rc, alive))
    esc = "import subprocess,time;p=subprocess.Popen(['sleep','30'],start_new_session=True);open(%r,'w').write(str(p.pid));time.sleep(30)" % os.path.join(d7, "esc")
    rc2, _ = C.run([sys.executable, "-c", esc], 2)
    epid = int(open(os.path.join(d7, "esc")).read().strip())
    gone = False
    for _ in range(20):
        try:
            os.kill(epid, 0)
        except ProcessLookupError:
            gone = True
            break
        _t.sleep(0.1)
    if not gone:
        try:
            os.kill(epid, 9)
        except ProcessLookupError:
            pass
    # (here an orphan is reaped by the host anyway, so the live case above cannot go red: the tree walk is checked directly)
    table = {10: 1, 11: 10, 12: 11, 13: 12, 20: 1, 21: 20}           # pid -> parent; 12 and 13 may sit in other sessions
    check("L7 the descendant walk finds the whole tree, other sessions included, and nothing else",
          sorted(C.descendants(10, table)) == [11, 12, 13], C.descendants(10, table))
    check("L7 a timeout kills a descendant that left the group", rc2 == 124 and gone, (rc2, gone))
    keep2 = dict(V.LAW_FILES)
    nolaws = os.path.join(bad, "nolaws.json")
    open(nolaws, "w").write('{"mod": "FlowWorks", "families": {}}')
    V.LAW_FILES["FlowWorks"] = os.path.relpath(nolaws, V.ROOT)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            code = V.main(["lint"])
        check("L6 lint on a law file with no laws prints its problem and exits 1", code == 1 and "no laws" in buf.getvalue(), (code, buf.getvalue()[-200:]))
    except Exception as ex:                              # noqa: BLE001
        check("L6 lint on a law file with no laws prints its problem and exits 1", False, repr(ex))
    finally:
        V.LAW_FILES.clear()
        V.LAW_FILES.update(keep2)
    print("vv laws: %d failed" % len(FAILS) if FAILS else "vv laws: all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
