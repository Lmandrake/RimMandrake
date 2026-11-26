#!/usr/bin/env python3
"""selftest_preflight_enforce.py — the ticket preflight's stop at claim and start (spec
design/specs/2026-11-12-ticket-preflight-before-any-token.md section 7 ticket 4). Page:
design/specs/2026-11-26-preflight-stops-at-pickup/boundary.md; each promise there has a test of its own name here.

The in-process tests drive ticket_preflight.Shadow with planted indexes and a timing file of their own. The last test
runs the acceptance test, which drives the real `rimflow file / claim / start / preflight --timing` in a sandbox ledger
(RIMFLOW_LEDGER, RIMFLOW_ITEMS, RIMFLOW_PREFLIGHT_RUNS). Nothing reaches the real ledger or the real timing file.
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ticket_preflight as TP  # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest-preflight-enforce-")
RUNS = os.path.join(TMP, "runs.jsonl")
ITEM = "RIMMANDRAKE_NO_SUCH_SELFTEST_ITEM"
HELPER = {"RIMFLOW_SEAT": "BENCH", "RM_ROLE_UNIT": "rm-detached-selftest-preflight-enforce"}
CONDUCTOR = {"RIMFLOW_SEAT": "BENCH"}
OWNER = {"RIMFLOW_SEAT": "OWNER"}
FAILS = []


def check(cond, what, detail=""):
    print(("ok    " if cond else "FAIL  ") + what + ("" if cond else "  [%s]" % str(detail)[-400:]))
    if not cond:
        FAILS.append(what)


def shadow(door, refs=None, kind="build"):
    """A Shadow whose new checks ran over a planted ticket: `refs` is the `## refs` body (None: no section)."""
    sh = TP.Shadow(door, ITEM, "BENCH", runs_path=RUNS)
    text = "## spec\nplanted\n" + ("\n## refs\n%s\n" % refs if refs is not None else "")
    rep = TP.run_text(text, item_id=ITEM, paths=["src/x.py"], defs={}, src={}, tiers={}, items={}, kind=kind,
                      record=False, inline=True)
    sh.checks = rep["checks"]
    return sh


def stop(sh, env):
    """-> (exit code or None, stderr, returned note)."""
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            note = sh.enforce("BENCH" if env is not OWNER else "OWNER", env=env)
        return None, err.getvalue(), note
    except SystemExit as e:
        return e.code, err.getvalue(), None


def last_line():
    with open(RUNS) as f:
        return json.loads(f.read().splitlines()[-1])


def t_claim_and_start_stop_a_launched_run_on_a_failed_declared_fact():
    for door in ("claim", "start"):
        code, err, _ = stop(shadow(door, "file: src/missing_on_purpose.py"), HELPER)
        check(code == 2 and "B1" in err, "%s: a helper's pickup of a ticket naming a missing path exits 2 naming B1" % door,
              (code, err))
    code, err, _ = stop(shadow("claim", None), HELPER)
    check(code == 2 and "E12" in err, "claim: a build ticket with no `## refs` section stops on E12", (code, err))
    code, err, _ = stop(shadow("claim", "file: src/x.py\ntier: full"), HELPER)
    check(code == 2 and "C4" in err, "claim: a Full Mod ask with no `full-why:` stops on C4", (code, err))
    code, _, _ = stop(shadow("claim", None, kind="task"), HELPER)
    check(code is None, "claim: a task ticket owes no refs and is not stopped", code)


def t_the_refusal_carries_each_repair_and_the_repaired_ticket_passes():
    code, err, _ = stop(shadow("claim", None), HELPER)
    check(code == 2 and "FIX:" in err and "## refs" in err and "rimflow preflight" in err,
          "the stop prints each FIX and the command that re-checks", err)
    code, _, _ = stop(shadow("claim", "file: src/x.py"), HELPER)
    check(code is None, "the same ticket with a real declared path is not stopped", code)
    code, _, _ = stop(shadow("claim", "none: it names nothing checkable"), HELPER)
    check(code is None, "a `none: <why>` line satisfies E12", code)


def t_the_conductor_and_the_owner_pass_with_a_note():
    for env, who in ((CONDUCTOR, "conductor"), (OWNER, "owner")):
        sh = shadow("claim", "file: src/missing_on_purpose.py")
        code, err, note = stop(sh, env)
        check(code is None and note and "B1" in note and "NOTE" in err and sh.override == who,
              "the %s's claim goes on with a NOTE naming B1" % who, (code, err, note))
        sh.finish()
        ln = last_line()
        check(ln["override"] == who and ln["verdict"].startswith("passed by %s" % who),
              "the %s's pass is recorded on its timing line" % who, ln)


def t_filing_and_the_launch_door_never_stop():
    for door in ("file", "helper_launch"):
        sh = shadow(door, "file: src/missing_on_purpose.py")
        code, _, note = stop(sh, HELPER)
        check(code is None and note is None and not sh.refused, "%s: a failed declared fact stops nothing" % door,
              (code, sh.refused))


def t_a_check_that_cannot_look_stops_nothing():
    sh = TP.Shadow("claim", ITEM, "BENCH", runs_path=RUNS)
    sh.crash = "RuntimeError: planted"
    check(stop(sh, HELPER)[0] is None, "a preflight that did not run stops nothing")
    sh = TP.Shadow("claim", ITEM, "BENCH", runs_path=RUNS)
    sh.checks = [{"id": "B4", "ref": "X", "status": "UNMEASURED", "evidence": "no def index"},
                 {"id": "B1", "ref": "src/y.py", "status": "FAIL", "evidence": "the tool's guess", "origin": "auto"}]
    check(stop(sh, HELPER)[0] is None, "an UNMEASURED check and a tool's (auto) guess stop nothing")
    sh = shadow("claim", "file: src/x.py")
    sh.gates.append({"id": "E1", "ref": None, "status": "FAIL", "evidence": "missing ## spec", "fix": "", "ms": 0.0,
                     "origin": "gate"})
    check(stop(sh, HELPER)[0] is None, "an existing gate's FAIL keeps its own authority: the preflight adds no stop")
    root = os.path.join(TMP, "unreadable")
    os.makedirs(os.path.join(root, "infrastructure", "state", "items", ITEM + ".md"))    # a prose path that open() refuses
    sh = TP.Shadow("claim", ITEM, "BENCH", runs_path=RUNS)
    sh.run(root=root, kind="build", needs="offline", items={}, paths=["src/x.py"], defs={}, src={}, tiers={})
    code = stop(sh, HELPER)[0]
    check(code is None and not sh.refused, "a prose file that cannot be read is could-not-look, never `no refs` (%s, %s)"
          % (code, sh.verdict()))


def t_every_attempt_is_a_timing_line_and_timing_reads_them():
    open(RUNS, "w").close()
    sh = shadow("claim", "file: src/missing_on_purpose.py")
    stop(sh, HELPER)
    ln = last_line()
    check(ln["door"] == "claim" and ln["verdict"].startswith("refused") and isinstance(ln["total_ms"], (int, float)),
          "a refused pickup still writes its timing line, verdict refused", ln)
    ok = shadow("start", "file: src/x.py")
    stop(ok, HELPER)
    ok.finish()
    t = TP.timing(runs_path=RUNS)
    c, s = t["doors"].get("claim", {}), t["doors"].get("start", {})
    check(c.get("refused") == 1 and c.get("p95_ms") is not None and s.get("n") == 1 and s.get("refused") == 0,
          "timing: count, p95 and refusals per door", t)
    txt = TP.render_timing(t)
    check("p95" in txt and "claim" in txt and "added p95" in txt, "render_timing prints the per-door table", txt)
    t = TP.timing(runs_path=os.path.join(TMP, "no_such_runs.jsonl"))
    check(t.get("error") and "no timing lines read" in TP.render_timing(t), "a missing timing file is said, not raised", t)


def t_the_real_doors_in_a_sandbox_ledger():
    p = subprocess.run([sys.executable, os.path.join(HERE, "acceptance", "preflight_enforce_accept.py")],
                       capture_output=True, text=True,
                       timeout=600)  # budget: danger=a hung sandbox door holds ./publish; evidence=a door waits on the dispatch lock; longest=5s (one measured run, 2026-11-26)
    last = (p.stdout.strip().splitlines() or ["(no output)"])[-1]
    check(p.returncode == 0 and last.startswith("PASS"), "the sandbox doors: %s" % last, p.stdout[-1500:] + p.stderr[-500:])


def main():
    tests = [t_claim_and_start_stop_a_launched_run_on_a_failed_declared_fact,
             t_the_refusal_carries_each_repair_and_the_repaired_ticket_passes,
             t_the_conductor_and_the_owner_pass_with_a_note, t_filing_and_the_launch_door_never_stop,
             t_a_check_that_cannot_look_stops_nothing, t_every_attempt_is_a_timing_line_and_timing_reads_them,
             t_the_real_doors_in_a_sandbox_ledger]
    try:
        for t in tests:
            try:
                t()
            except Exception as e:  # noqa: BLE001  a test that raises is a FAIL with its cause
                check(False, "%s raised" % t.__name__, "%s: %s" % (type(e).__name__, e))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
