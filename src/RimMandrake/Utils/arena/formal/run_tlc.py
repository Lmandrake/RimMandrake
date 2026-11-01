#!/usr/bin/env python3
"""run_tlc.py — model-check Handoff.tla with TLC over the fixed protocol and its forced-failure mutants.

ARENA_HANDOFF_PROVE_MODEL_FINDS_KNOWN_RACE, reconciled with the code by ARENA_HANDOFF_RECONCILE_MODEL_WITH_CODE
(the one model: LiveHandoff.tla + check_models.py were deleted, their deaths and mutants ported here). One spec
(Handoff.tla) covers the goodbye restart, the TestPilot handoff and the arena switch. Each row is an expectation:

  known_race   Mode goodbye, Bugs {dead_session_drop}: TLC must find the known goodbye interleaving, i.e. an S5
               violation whose trace sends an owner message while the handoff is in phase `killed` (old window
               dead, fresh one not yet up: conductor_briefing_2026-10-28 B4 row 2).
  fixed_*      Bugs {} in each mode, hazard dequeue_gap on: S1-S6 hold at BOUNDS (goodbye: L2 too).
  live_*       Bugs {} in testpilot and arena: S1-S6 and L1, L2 hold under weak fairness with one candidate.
  d_*          Bugs {}, one process death allowed (old_alone, dispatcher, wake): must pass, except d_old_alone_gap,
               the residual (a window dying alone between dequeue and persist loses that prompt).
  m_*          one planted defect per property: TLC must report exactly that property violated (a property that
               cannot fail proves nothing). m_S5_no_recheck is the re-check proved load-bearing.
  h_*          an UNMEASURED environment assumption negated (hazard term_drop): S5 must break, so S5 rests on it.
  w_*          witnesses: an invariant the fixed protocol must violate (it reaches the state the rows pass over).

Usage:  run_tlc.py [--only NAME[,NAME]] [--out DIR] [--list]
Exit 0 only when every row met its expectation. Evidence (cfgs, TLC logs, summary.json) goes to --out
(default D:/ClaudeWork/rimmandrake/formal/handoff/<utc>).

Workers: $RM_TLC_WORKERS (an integer or "auto"), default 4, so a busy machine can cap TLC.
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

# Bounds: 2 owner messages, 2 candidates, 2 fixes, 1 crash, 1 owner return, 1 failed relaunch, any number of
# cancels and aborts, MaxHandoffs consecutive handoffs (goodbye 2; game modes 1, the h=2 game row is f_testpilot).
# Liveness rows check one candidate (LIVE): with two, the fair-cycle search exceeds the row budget.
BOUNDS = {"Msgs": ["m1", "m2"], "Cands": ["c1", "c2"], "MaxFix": 2, "MaxHandoffs": 1,
          "Hazards": ["dequeue_gap"], "Deaths": []}
LIVE = {"Cands": ["c1"]}
GB = {"MaxHandoffs": 2}
NOMSG = {"Msgs": []}                     # arena arms are headless: no owner messages reach them
ALL_DEATHS = ["old_alone", "dispatcher", "wake"]

# name: (mode, bugs, invariants, properties, expect[, overrides]) ; expect = "pass" or the property TLC must report
MATRIX = {
    "known_race":         ("goodbye",   ["dead_session_drop"], INVS, [], "S5", GB),
    "fixed_goodbye":      ("goodbye",   [], INVS, ["L2"], "pass", GB),   # no candidates in goodbye: L1 is vacuous
    "fixed_testpilot":    ("testpilot", [], INVS, [], "pass"),
    "fixed_arena":        ("arena",     [], INVS, [], "pass", NOMSG),
    "f_testpilot":        ("testpilot", [], INVS, [], "pass", {"MaxHandoffs": 2, "Cands": ["c1"], "MaxFix": 1}),
    "live_testpilot":     ("testpilot", [], INVS, PROPS, "pass", LIVE),
    "live_arena":         ("arena",     [], INVS, ["L1"], "pass", {**LIVE, **NOMSG}),   # no messages: L2 vacuous
    "d_goodbye":          ("goodbye",   [], INVS, ["L2"], "pass", {**GB, "Hazards": [], "Deaths": ALL_DEATHS}),
    "d_dispatcher_wake":  ("goodbye",   [], INVS, ["L2"], "pass", {**GB, "Deaths": ["dispatcher", "wake"]}),
    "d_testpilot":        ("testpilot", [], INVS, PROPS, "pass", {**LIVE, "Hazards": [], "Deaths": ALL_DEATHS}),
    "d_old_alone_gap":    ("goodbye",   [], ["S5"], [], "S5", {"Deaths": ["old_alone"]}),
    "no_claim_recheck":   ("goodbye",   ["no_claim_recheck"], INVS, ["L2"], "pass", GB),
    "m_S5_no_recheck":    ("goodbye",   ["no_recheck"], ["S5"], [], "S5"),
    "m_S5_no_fence":      ("goodbye",   ["no_fence"], ["S5"], [], "S5"),
    "m_S5_wake_skips":    ("goodbye",   ["wake_skips_old"], ["S5"], [], "S5"),
    "m_S5_closeout":      ("goodbye",   ["closeout_skips_queue"], ["S5"], [], "S5"),
    "m_S5_wake_once":     ("goodbye",   ["wake_once"], ["S5"], [], "S5", {"Deaths": ["wake"]}),
    "m_L2_no_adopt":      ("goodbye",   ["no_adopt"], [], ["L2"], "L2", {"Deaths": ["old_alone"], "Hazards": []}),
    "m_S1_overlap":       ("arena",     ["overlap"], ["S1"], [], "S1", NOMSG),
    "m_S1_survive":       ("goodbye",   ["relaunch_after_survive"], ["S1"], [], "S1"),
    "m_S2_stale":         ("testpilot", ["stale_verdict"], ["S2"], [], "S2"),
    "m_S3_cs_up":         ("testpilot", ["cs_while_up"], ["S3"], [], "S3"),
    "m_S4_no_rule":       ("testpilot", ["reload_no_rule"], ["S4"], [], "S4"),
    "m_S5_mem_queue":     ("testpilot", ["mem_queue"], ["S5"], [], "S5"),
    "m_S5_mem_forced":    ("arena",     ["mem_queue"], ["S5"], [], "S5", NOMSG),
    "m_S6_straggler":     ("arena",     ["straggler"], ["S6"], [], "S6", NOMSG),
    "m_L1_mem_queue":     ("testpilot", ["mem_queue"], [], ["L1"], "L1", LIVE),
    "m_L2_dead_session":  ("goodbye",   ["dead_session_drop"], [], ["L2"], "L2"),
    "h_term_drop":        ("goodbye",   [], ["S5"], [], "S5", {"Hazards": ["dequeue_gap", "term_drop"]}),
    "w_verified":         ("goodbye",   [], ["NotVerified"], [], "NotVerified"),
    "w_second_handoff":   ("goodbye",   [], ["NoSecondHandoff"], [], "NoSecondHandoff", GB),
    "w_gap":              ("goodbye",   [], ["NoGap"], [], "NoGap"),
    "w_new_drives":       ("testpilot", [], ["NewNeverDrives"], [], "NewNeverDrives"),
    "w_forced_kill":      ("arena",     [], ["NoForcedKill"], [], "NoForcedKill", NOMSG),
}

# Rows of a minute or more each (6.6M / 1.3M states at 4 workers): run_tlc.py runs them; the selftest skips them
# visibly unless RM_TLC_ALL=1, so it stays inside the runner's 240 s budget.
HEAVY = {"fixed_testpilot", "live_testpilot", "d_testpilot"}


def workers():
    w = (os.environ.get("RM_TLC_WORKERS") or "4").strip()
    if w != "auto" and not (w.isdigit() and int(w) > 0):
        raise SystemExit("RM_TLC_WORKERS must be a positive integer or 'auto', not %r" % w)
    return w


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


def row(name):
    """-> (mode, bugs, invariants, properties, expect, bounds) with the row's bound overrides applied."""
    r = MATRIX[name]
    return r[:5] + ({**BOUNDS, **(r[5] if len(r) > 5 else {})},)


def cfg_text(mode, bugs, invs, props, bounds=BOUNDS):
    def mset(xs):
        return "{" + ", ".join(xs) + "}"
    lines = ["SPECIFICATION Spec" if props else "INIT Init\nNEXT Next",
             "CONSTANTS",
             '  Mode = "%s"' % mode,
             "  Msgs = %s" % mset(bounds["Msgs"]),
             "  Cands = %s" % mset([] if mode == "goodbye" else bounds["Cands"]),
             "  MaxFix = %d" % bounds["MaxFix"],
             "  MaxHandoffs = %d" % bounds["MaxHandoffs"],
             "  Bugs = %s" % mset('"%s"' % b for b in bugs),
             "  Hazards = %s" % mset('"%s"' % h for h in bounds["Hazards"]),
             "  Deaths = %s" % mset('"%s"' % x for x in bounds["Deaths"])]
    lines += ["  %s = %s" % (v, v) for v in bounds["Msgs"] + ([] if mode == "goodbye" else bounds["Cands"])]
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


def msg_states(state_text: str) -> dict:
    """TLC prints msg as (m1 :> "inOld" @@ m2 :> "unsent"): key -> state."""
    return dict(re.findall(r'(\w+) :> "(\w+)"', var_of(state_text, "msg") or ""))


def is_taken_then_lost(trace) -> bool:
    """Some message is takenOld in a claimed/killing state and that same message is lost later in the trace."""
    taken = set()
    for s in trace:
        ms = msg_states(s)
        if any(ms.get(k) == "lost" for k in taken):
            return True
        if var_of(s, "phase") in ('"claimed"', '"killing"'):
            taken |= {k for k, v in ms.items() if v == "takenOld"}
    return False


def run_row(name, java, jar, out_dir: Path, timeout_s=480):
    mode, bugs, invs, props, expect, bounds = row(name)
    d = out_dir / name
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(SPEC, d / "Handoff.tla")
    (d / "Handoff.cfg").write_text(cfg_text(mode, bugs, invs, props, bounds))
    # TLC's state files on a drvfs mount (D:) slow it 30x or more: they go to a local temp dir, deleted after
    meta = Path(tempfile.mkdtemp(prefix="tlc_%s_" % name))
    cmd = [java, "-XX:+UseParallelGC", "-cp", jar, "tlc2.TLC", "-deadlock", "-workers", workers(),
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
    elif ok and name == "m_S5_no_recheck":
        # the re-check is load-bearing only if the loss is the dequeued-not-persisted prompt dying with the kill:
        # the SAME message is takenOld while claimed/killing and later lost
        ok = is_taken_then_lost(r["trace"])
        why = "a prompt dequeued after the claim dies with the kill" if ok else "loss is not the re-check's case"
    elif ok and name == "m_L2_no_adopt":
        ok = any(var_of(s, "phase") == '"orphaned"' for s in r["trace"])
        why = "the orphaned window is never adopted" if ok else "counter-example is not the orphan: wrong cause"
    elif ok and expect in PROPS:
        # a liveness mutant must fail BECAUSE something was lost, not through some other unfair loop
        lost = any('"lost"' in (var_of(s, "msg") or "") + (var_of(s, "cand") or "") for s in r["trace"])
        ok, why = lost, ("counter-example loses an input" if lost else "counter-example loses nothing: wrong cause")
    return {"name": name, "mode": mode, "bugs": bugs, "invariants": invs, "properties": props, "expect": expect,
            "bounds": bounds,
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
            print("%-18s mode=%-9s bugs=%-22s expect=%-15s cands=%s" % (k, v[0], ",".join(v[1]) or "-", v[4],
                  len(row(k)[5]["Cands"])))
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
        print("%-5s %-18s expect=%-15s got=%s%s states=%s %s" % ("ok" if r["ok"] else "FAIL", n, r["expect"], r["result"],
              "(%s)" % r["violated"] if r["violated"] else "", r["states"], r["why"]), flush=True)
    (out / "summary.json").write_text(json.dumps({"bounds": BOUNDS, "rows": rows}, indent=1))
    print("evidence: %s" % out)
    return 0 if all(r["ok"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
