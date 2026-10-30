#!/usr/bin/env python3
"""run_tlc.py — model-check Handoff.tla with TLC over the fixed protocol and its forced-failure mutants.

ARENA_HANDOFF_PROVE_MODEL_FINDS_KNOWN_RACE. One spec (Handoff.tla) covers the goodbye restart, the TestPilot
handoff and the arena switch. The matrix below is the item's criteria, each row an expectation:

  known_race   Mode goodbye, Bugs {dead_session_drop}: TLC must find the known goodbye interleaving, i.e. an S5
               violation whose trace sends an owner message while the handoff is in phase `killed` (old window
               dead, fresh one not yet up: conductor_briefing_2026-10-28 B4 row 2).
  fixed_*      Bugs {} in each mode: S1-S6 hold and L1, L2 hold under weak fairness at the stated bounds.
  m_*          one planted defect per invariant / liveness property: TLC must report exactly that property
               violated (a property that cannot fail proves nothing).

Usage:  run_tlc.py [--only NAME[,NAME]] [--out DIR] [--list]
Exit 0 only when every row met its expectation. Evidence (cfgs, TLC logs, summary.json) goes to --out
(default D:/ClaudeWork/rimmandrake/formal/handoff/<utc>).

Java: $TLA_JAVA, else ~/.local/opt/jdk*/bin/java, else `java` on PATH. tla2tools: $TLA2TOOLS, else
~/.local/opt/tla2tools.jar. Missing either -> exit 2 (UNMEASURED, never a pass).
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE / "Handoff.tla"
INVS = ["S1", "S2", "S3", "S4", "S5", "S6"]
PROPS = ["L1", "L2"]

# Bounds: 2 owner messages, 2 candidates, 2 fixes, 1 crash, 1 owner return, any number of cancels.
BOUNDS = {"Msgs": ["m1", "m2"], "Cands": ["c1", "c2"], "MaxFix": 2}

# name: (mode, bugs, invariants, properties, expect) ; expect = "pass" or the property TLC must report violated
MATRIX = {
    "known_race":        ("goodbye",   ["dead_session_drop"], INVS, [], "S5"),
    "fixed_goodbye":     ("goodbye",   [], INVS, ["L2"], "pass"),     # no candidates in goodbye: L1 is vacuous
    "fixed_testpilot":   ("testpilot", [], INVS, PROPS, "pass"),
    "fixed_arena":       ("arena",     [], INVS, PROPS, "pass"),
    "m_S1_overlap":      ("arena",     ["overlap"], ["S1"], [], "S1"),
    "m_S2_stale":        ("testpilot", ["stale_verdict"], ["S2"], [], "S2"),
    "m_S3_cs_up":        ("testpilot", ["cs_while_up"], ["S3"], [], "S3"),
    "m_S4_no_rule":      ("testpilot", ["reload_no_rule"], ["S4"], [], "S4"),
    "m_S5_mem_queue":    ("testpilot", ["mem_queue"], ["S5"], [], "S5"),
    "m_S6_straggler":    ("arena",     ["straggler"], ["S6"], [], "S6"),
    "m_L1_mem_queue":    ("testpilot", ["mem_queue"], [], ["L1"], "L1"),
    "m_L2_dead_session": ("goodbye",   ["dead_session_drop"], [], ["L2"], "L2"),
}


def find_java():
    for c in [os.environ.get("TLA_JAVA")] + sorted(glob.glob(os.path.expanduser("~/.local/opt/jdk*/bin/java"))) \
            + [shutil.which("java")]:
        if c and os.access(c, os.X_OK):
            return c
    return None


def find_jar():
    for c in (os.environ.get("TLA2TOOLS"), os.path.expanduser("~/.local/opt/tla2tools.jar")):
        if c and os.path.isfile(c):
            return c
    return None


def cfg_text(mode, bugs, invs, props):
    def mset(xs):
        return "{" + ", ".join(xs) + "}"
    lines = ["SPECIFICATION Spec" if props else "INIT Init\nNEXT Next",
             "CONSTANTS",
             '  Mode = "%s"' % mode,
             "  Msgs = %s" % mset(BOUNDS["Msgs"]),
             "  Cands = %s" % mset([] if mode == "goodbye" else BOUNDS["Cands"]),
             "  MaxFix = %d" % BOUNDS["MaxFix"],
             "  Bugs = {%s}" % ", ".join('"%s"' % b for b in bugs)]
    lines += ["  %s = %s" % (v, v) for v in BOUNDS["Msgs"] + ([] if mode == "goodbye" else BOUNDS["Cands"])]
    lines += ["INVARIANT TypeOK"] + ["INVARIANT %s" % i for i in invs] + ["PROPERTY %s" % p for p in props]
    return "\n".join(lines) + "\n"


VIOL = re.compile(r"^Error: Invariant (\w+) is violated|^Error: Temporal propert(?:y|ies) ([\w ,]+?) (?:was|were) violated",
                  re.M)


def parse(log: str, props):
    """-> dict(result=pass|violated|error, prop=name|None, states=int|None, trace=[state dicts as text])."""
    out = {"result": "error", "prop": None, "states": None, "trace": []}
    m = re.findall(r"([\d,]+) distinct states found", log)     # progress lines too: the LAST is the total
    if m:
        out["states"] = int(m[-1].replace(",", ""))
    v = VIOL.search(log)
    if v:
        out["result"] = "violated"
        out["prop"] = v.group(1) or v.group(2).replace(" and ", ",").replace(" ", "")
        out["trace"] = [s.strip() for s in re.split(r"^State \d+: ", log, flags=re.M)[1:]]
    elif "Model checking completed. No error has been found." in log and \
            re.search(r"distinct states found, 0 states left on queue", log):
        out["result"] = "pass"
    return out


def var_of(state_text: str, name: str):
    m = re.search(r"^/\\ %s = (.*)$" % re.escape(name), state_text, re.M)
    return m.group(1).strip() if m else None


def is_known_goodbye_race(trace) -> tuple[bool, str]:
    """The known interleaving: a message goes from unsent to lost in a step taken while phase = "killed"."""
    prev = None
    for i, s in enumerate(trace):
        if prev is not None and var_of(prev, "phase") == '"killed"':
            before, after = var_of(prev, "msg") or "", var_of(s, "msg") or ""
            if after.count('"lost"') > before.count('"lost"'):
                return True, "step %d: phase killed, a message sent into the dead session was lost" % i
        prev = s
    return False, "no step in phase killed loses a message"


def run_row(name, java, jar, out_dir: Path, timeout_s=480):
    mode, bugs, invs, props, expect = MATRIX[name]
    d = out_dir / name
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(SPEC, d / "Handoff.tla")
    (d / "Handoff.cfg").write_text(cfg_text(mode, bugs, invs, props))
    # TLC's state files on a drvfs mount (D:) slow it 30x or more: they go to a local temp dir, deleted after
    meta = Path(tempfile.mkdtemp(prefix="tlc_%s_" % name))
    cmd = [java, "-XX:+UseParallelGC", "-cp", jar, "tlc2.TLC", "-deadlock", "-workers", "auto",
           "-metadir", str(meta), "-config", "Handoff.cfg", "Handoff.tla"]
    try:
        p = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=timeout_s)
        log = p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        log = (e.stdout or "") if isinstance(e.stdout, str) else ""
        log += "\nTIMEOUT after %ds" % timeout_s
    (d / "tlc.log").write_text(log)
    shutil.rmtree(meta, ignore_errors=True)
    r = parse(log, props)
    ok = (r["result"] == "pass") if expect == "pass" else (r["result"] == "violated" and r["prop"] == expect)
    why = ""
    if ok and name == "known_race":
        ok, why = is_known_goodbye_race(r["trace"])
    elif ok and expect in PROPS:
        # a liveness mutant must fail BECAUSE something was lost, not through some other unfair loop
        lost = any('"lost"' in (var_of(s, "msg") or "") + (var_of(s, "cand") or "") for s in r["trace"])
        ok, why = lost, ("counter-example loses an input" if lost else "counter-example loses nothing: wrong cause")
    return {"name": name, "mode": mode, "bugs": bugs, "invariants": invs, "properties": props, "expect": expect,
            "result": r["result"], "violated": r["prop"], "states": r["states"], "trace_len": len(r["trace"]),
            "ok": ok, "why": why, "log": str(d / "tlc.log")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    if a.list:
        for k, v in MATRIX.items():
            print("%-18s mode=%-9s bugs=%-22s expect=%s" % (k, v[0], ",".join(v[1]) or "-", v[4]))
        return 0
    names = [n for n in a.only.split(",") if n] or list(MATRIX)
    bad = [n for n in names if n not in MATRIX]
    if bad:
        print("unknown row(s): %s" % ", ".join(bad))
        return 2
    java, jar = find_java(), find_jar()
    if not java or not jar:
        print("UNMEASURED: java=%s tla2tools=%s (see the docstring for where they are looked up)" % (java, jar))
        return 2
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(a.out or "/mnt/d/ClaudeWork/rimmandrake/formal/handoff/%s" % stamp)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for n in names:
        r = run_row(n, java, jar, out)
        rows.append(r)
        print("%-5s %-18s expect=%-4s got=%s%s states=%s %s" % ("ok" if r["ok"] else "FAIL", n, r["expect"], r["result"],
              "(%s)" % r["violated"] if r["violated"] else "", r["states"], r["why"]), flush=True)
    (out / "summary.json").write_text(json.dumps({"bounds": BOUNDS, "rows": rows}, indent=1))
    print("evidence: %s" % out)
    return 0 if all(r["ok"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
