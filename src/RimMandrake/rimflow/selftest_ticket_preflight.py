#!/usr/bin/env python3
"""Selftest for ticket_preflight (spine): each check has one planted bad input it must FAIL and one good it must PASS,
a cut-off and a failed instrument read UNMEASURED, prose is never read. python3 src/RimMandrake/rimflow/selftest_ticket_preflight.py"""
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ticket_preflight as TP  # noqa: E402

FAILS = []
RUNS = os.path.join(tempfile.mkdtemp(prefix="pf_selftest_"), "runs.jsonl")
DEFS = {"capture": "T", "mods": ["pkg.a", "pkg.b"], "defs": [["ThingDef", "RM_On", 1, "pkg.a"], ["ThingDef", "RM_Off", 2, "pkg.b"]]}
KW = dict(paths=["src/x.py"], defs=DEFS, src={}, tiers={"small": ["pkg.a"], "wide": ["pkg.a", "pkg.zz"]}, runs_path=RUNS)


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def st(text, cid, ref, proof="", **kw):
    r = TP.run_text("## refs\n" + text + "\n", proof, **dict(KW, **kw))
    return [c["status"] for c in r["checks"] if c["id"] == cid and c["ref"] == ref], r


check(st("file: src/x.py", "B1", "src/x.py")[0] == ["PASS"], "B1 good: tracked path passes")
check(st("file: src/nope.py", "B1", "src/nope.py")[0] == ["FAIL"], "B1 bad: untracked path fails")
check(st("tier: small", "C1", "small")[0] == ["PASS"] and st("tier: nosuch", "C1", "nosuch")[0] == ["FAIL"], "C1 good and bad")
check(st("def: RM_On\ntier: small", "C2", "RM_On")[0] == ["PASS"], "C2 good: def on the list")
check(st("def: RM_Off\ntier: small", "C2", "RM_Off")[0] == ["FAIL"], "C2 bad: def off the list")
check(st("def: RM_Gone\ntier: small", "B4", "RM_Gone")[0] == ["FAIL"], "B4 bad: def known nowhere")
check(st("def: RM_Gone\ntier: wide", "B4", "RM_Gone")[0] == ["UNMEASURED"], "C10 bad: undumped mod makes 'missing' UNMEASURED")
check(st("def: RM_Ours\ntier: small", "B5", "RM_Ours", src={"RM_Ours": [["ThingDef", "pkg.a"]]})[0] == ["PASS"], "B5 src-only def is ours")
check(st("def: RM_Off", "C2", "RM_Off", proof="live-mods: pkg.a\n")[0] == ["FAIL"], "proof file live-mods is read")
check(st("this is prose", "P0", "line 2")[0] == ["FAIL"], "a malformed refs line is reported")
r = TP.run_text("## spec\nsrc/gone.py RM_Gone tier: nosuch\n", **KW)
check(not r["checks"], "prose is never read")


def stuck():
    time.sleep(30)


t = time.monotonic()
s, r = st("file: src/x.py", "B1", "src/x.py", paths=stuck, deadline_s=1.0)
check(s == ["UNMEASURED"] and r["cut_off"] and time.monotonic() - t < 6, "a stuck instrument is cut off, UNMEASURED")
n0 = len(open(RUNS).read().splitlines())
check(TP.run_text("", **KW)["checks"] == [] and len(open(RUNS).read().splitlines()) == n0 + 1, "an empty ticket is clean; every run logged")
# core (ticket 2): one planted bad and one good each; the full matrix is acceptance/preflight_core_accept.py
e = [c for c in TP.run_text("## refs\ndfe: RM_On\n", **KW)["checks"] if c["id"] == "E11"]
check(e and e[0]["status"] == "FAIL" and "`def:`" in e[0]["evidence"], "E11 bad: a typo'd key FAILs naming the nearest key")
check(not [c for c in TP.run_text("## refs\ndef: RM_On\n", **KW)["checks"] if c["id"] == "E11"], "E11 good: a clean block is silent")
a = [c for c in TP.run_text("## refs\nfile: src/x.py (auto)\n", **KW)["checks"] if c["id"] == "B1"]
check(a and a[0]["origin"] == "auto", "an (auto) line carries origin auto")
check([c["status"] for c in TP.run_text("## spec\nx\n", kind="build", **KW)["checks"] if c["id"] == "E12"] == ["FAIL"], "E12 bad: a build ticket with no refs")
check([c["status"] for c in TP.run_text("## refs\nnone: names nothing\n", kind="fix", **KW)["checks"] if c["id"] == "E12"] == ["PASS"], "E12 good: none: <why>")
check([c["status"] for c in TP.run_text("## refs\ntier: full\n", **KW)["checks"] if c["id"] == "C4"] == ["FAIL"], "C4 bad: Full with no reason")
# the tier a repair proposes must be one C1 accepts, and `tier: full`, as C4 asks for it, is not "no tier"
# (RIMMANDRAKE_FIX_PREFLIGHT_TIER_FULL_ITS_OWN_REPAIR_FAILS: there is no small, wide or full tier in modset_builder)
check(st("tier: full", "C1", "full")[0] == ["PASS"], "C1 good: `tier: full` names the Full list, not an unknown tier")
check(st("tier: Full\nfull-why: performance: only at scale", "C4", None)[0] == ["PASS"], "C4 good: Full with a reason")
real = TP._real_tiers()
c4 = [c for c in TP.run_text("## refs\ntier: full\n", **KW)["checks"] if c["id"] == "C4"][0]["fix"]
named = [t for fx in (TP.E12_FIX, c4) for m in re.findall(r"tier: (<[^>]*>|[a-z_0-9|]+)", fx)
         if " " not in m for t in m.strip("<>").split("|")]        # a `<a tier from ...>` placeholder names none
check(all(t == "full" or real.get(t) is not None for t in named), "a repair proposes only real tiers (%s)" % ", ".join(named))

# the doors (ticket 3 shadow): never raise, record every attempt
import io  # noqa: E402
import json  # noqa: E402
import contextlib  # noqa: E402
SRUNS = os.path.join(os.path.dirname(RUNS), "shadow_runs.jsonl")
sh = TP.Shadow("claim", "RIMMANDRAKE_NO_SUCH_SELFTEST_ITEM", "BENCH", runs_path=SRUNS)
sh.run(paths=["src/x.py"], defs=DEFS, src={}, tiers=KW["tiers"], items={}, kind="build")
sh.gate("E1", lambda: ["spec"], judge=lambda g: ("FAIL", "missing %s" % g) if g else ("PASS", ""))
f = sh.fields()
txt = sh.finish()
ln = json.loads(open(SRUNS).read().splitlines()[-1])
check(ln["door"] == "claim" and ln["run_id"] == f["preflight_run"] and {"E1", "E12"} <= {c["id"] for c in ln["checks"]},
      "shadow: one line per run, door and run id as on the event, gates and new checks both")
check("E1" in txt and "pickup stops a wrong declared fact" in txt and f["preflight"].startswith("fail"),
      "shadow: the FAILs print, the door's mode is said, verdict on the event")

# ticket 4 (the stop at claim and start) is tested in selftest_preflight_enforce.py
os.environ["RIMFLOW_PREFLIGHT_BREAK"] = "1"
sb = TP.Shadow("start", "X", runs_path=SRUNS).run()
del os.environ["RIMFLOW_PREFLIGHT_BREAK"]
check(sb.verdict() == "did not run" and "preflight did not run" in sb.finish(), "shadow bad: a raising runner says it did not run")
err = io.StringIO()
with contextlib.redirect_stderr(err):
    TP.Shadow("file", "X", runs_path=os.path.dirname(RUNS)).finish()      # a directory: the line cannot be written
check("timing" in err.getvalue(), "shadow bad: an unwritable timing file is reported, not raised")
n0 = len(open(SRUNS).read().splitlines())
try:
    TP.Shadow("claim", "X", runs_path=SRUNS).gate("I2", sys.exit, 2)
    check(False, "shadow: a refusing gate's SystemExit is re-raised")
except SystemExit:
    last = json.loads(open(SRUNS).read().splitlines()[-1])
    check(len(open(SRUNS).read().splitlines()) == n0 + 1 and last["checks"][0] == {"id": "I2", "ms": last["checks"][0]["ms"],
          "status": "FAIL", "origin": "gate"}, "shadow: a gate's refusal is re-raised unchanged, and its attempt is a line")
saved = {k: os.environ.pop(k, None) for k in ("RIMFLOW_PREFLIGHT_RUNS", "RIMFLOW_LEDGER")}
os.environ["RIMFLOW_LEDGER"] = os.path.join(os.path.dirname(RUNS), "sandbox", "events.jsonl")
check(TP.runs_file() == os.path.join(os.path.dirname(RUNS), "sandbox", "preflight_runs.jsonl"),
      "a sandbox ledger's doors write beside it, never into the real timing file")
del os.environ["RIMFLOW_LEDGER"]
check(TP.runs_file() == TP.DEFAULT_RUNS, "the real ledger's doors write the real timing file")
os.environ.update({k: v for k, v in saved.items() if v is not None})
print("PASS" if not FAILS else "FAILED %d" % len(FAILS))
sys.exit(1 if FAILS else 0)
