#!/usr/bin/env python3
"""Acceptance test: the ticket preflight STOPS a launched run at pickup on a failed declared fact (spec
design/specs/2026-11-12-ticket-preflight-before-any-token.md section 7 ticket 4; the owner's card answers of 2026-11-13
in section 9: Q1 filing warns, pickup stops; Q3 a build, fix or live ticket with no declared refs is stopped at pickup;
Q4 a Full Mod ask with no reason is stopped at pickup; Q5 only the Conductor passes a refusal; Q6 a check that cannot
look lets the work through). Item RIMMANDRAKE_PREFLIGHT_TICKETS_BEFORE_ANY_TOKEN_IS_SPENT.

    python3 src/RimMandrake/rimflow/acceptance/preflight_enforce_accept.py     # exit 0 and "PASS n/n" when built

It runs the real `rimflow file / claim / start / preflight` in a sandbox ledger (RIMFLOW_LEDGER, RIMFLOW_ITEMS,
RIMFLOW_PREFLIGHT_RUNS), never the real one. A helper is seat BENCH WITH RM_ROLE_UNIT; the Conductor window is seat
BENCH without it (principal.py). The refusal is a fault returned to the same agent with its repair (root CLAUDE.md
§A fault of form is repaired where it is found): the agent repairs the ticket and claims again in the same run.
Exit 0 when every clause holds, 1 when one does not.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
CLI = os.path.join(RIMFLOW, "cli.py")
RESULTS = []
MISSING = "RIMMANDRAKE_PLANT_MISSING_PATH_FOR_ENFORCE_RUN"
NOREFS = "RIMMANDRAKE_PLANT_NO_REFS_FOR_ENFORCE_RUN"
FULL = "RIMMANDRAKE_PLANT_FULL_NO_WHY_FOR_ENFORCE_RUN"
CONDUCTOR = "RIMMANDRAKE_PLANT_CONDUCTOR_PASSES_ENFORCE_RUN"
TASK = "RIMMANDRAKE_PLANT_TASK_NO_REFS_ENFORCE_RUN"
BROKEN = "RIMMANDRAKE_PLANT_BROKEN_RUNNER_ENFORCE_RUN"
DROP = ("RM_ROLE_UNIT", "RM_DETACHED_UNIT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")
HELPER_UNIT = "rm-detached-acceptance-preflight-enforce"


def check(ok, what):
    RESULTS.append((bool(ok), what))
    print(("ok    " if ok else "FAIL  ") + what)


def lines(path):
    return [json.loads(l) for l in open(path) if l.strip()] if os.path.isfile(path) else []


def prose(refs):
    return "## spec\nA planted ticket.\n\n%s## verify\ntrue\n\n## criteria\n- A1: planted.\n" % (
        ("## refs\n%s\n\n" % refs) if refs else "")


def main():
    tmp = tempfile.mkdtemp(prefix="preflight_enforce_")
    items = os.path.join(tmp, "items")
    os.makedirs(items)
    runs = os.path.join(tmp, "runs.jsonl")
    plant = {MISSING: "file: src/A/missing_on_purpose.py", NOREFS: "", FULL: "file: src/RimMandrake/rimflow/cli.py\ntier: full",
             CONDUCTOR: "file: src/A/missing_on_purpose.py", TASK: "", BROKEN: "file: src/A/missing_on_purpose.py"}
    for i, refs in plant.items():
        open(os.path.join(items, i + ".md"), "w").write(prose(refs))
    base = {k: v for k, v in os.environ.items() if not k.startswith("RIMFLOW_") and k not in DROP}
    base.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=items, RIMFLOW_SEAT="BENCH",
                RIMFLOW_PROBE="no-reading", RIMFLOW_PREFLIGHT_RUNS=runs, PYTHONDONTWRITEBYTECODE="1")

    def cli(*a, helper=True, **env):
        e = dict(base, **env)
        if helper:
            e["RM_ROLE_UNIT"] = HELPER_UNIT
        why = [] if a[0] == "preflight" else ["--why", "acceptance sandbox"]
        return subprocess.run([sys.executable, CLI] + list(a) + why, cwd=REPO, env=e, capture_output=True, text=True,
                              timeout=300)

    def events(verb, iid):
        out = []
        for f in glob.glob(os.path.join(tmp, "events", "*.jsonl")) + [base["RIMFLOW_LEDGER"]]:
            out += [e for e in lines(f) if e.get("event") == verb and e.get("id") == iid]
        return out

    def last_run(door, iid):
        rs = [l for l in lines(runs) if l.get("door") == door and l.get("item") == iid]
        return rs[-1] if rs else {}

    try:
        for i in plant:
            f = cli("file", i, "--for", "BENCH", "--title", "planted", "--kind", "task" if i == TASK else "build",
                    helper=False)
            if i == MISSING:
                check(f.returncode == 0, "filing warns only: a build ticket that names a missing path still files")

        c = cli("claim", MISSING)
        out = c.stdout + c.stderr
        check(c.returncode != 0, "a helper's claim of a ticket naming a missing path is refused (exit %s)" % c.returncode)
        check("B1" in out and "missing_on_purpose" in out, "the refusal names the check (B1) and the path")
        check("FIX" in out or "repair" in out.lower(), "the refusal carries its repair")
        check(not events("claim", MISSING) and not events("start", MISSING), "a refused claim writes no claim or start event")
        r = last_run("claim", MISSING)
        check(r and "refused" in str(r.get("verdict")), "the refused claim still writes its timing line, verdict refused (%s)"
              % r.get("verdict"))
        check(isinstance(r.get("total_ms"), (int, float)), "the refused claim's timing line carries total_ms")

        open(os.path.join(items, MISSING + ".md"), "w").write(prose("file: src/RimMandrake/rimflow/cli.py"))
        c = cli("claim", MISSING)
        check(c.returncode == 0 and events("claim", MISSING), "after the repair the same helper's claim goes through")

        s = cli("start", NOREFS)
        out = s.stdout + s.stderr
        check(s.returncode != 0 and "E12" in out and "## refs" in out,
              "a helper's start of a build ticket with no declared refs is refused with E12 and the refs block to add")
        open(os.path.join(items, NOREFS + ".md"), "w").write(prose("none: planted, it names nothing checkable"))
        s = cli("start", NOREFS)
        check(s.returncode == 0 and events("start", NOREFS), "after a `none: <why>` line the start goes through")

        c = cli("claim", FULL)
        out = c.stdout + c.stderr
        check(c.returncode != 0 and "C4" in out and "full-why" in out,
              "a helper's claim of a Full Mod ask with no reason is refused with C4 and the `full-why:` repair")

        c = cli("claim", CONDUCTOR, helper=False)
        out = c.stdout + c.stderr
        check(c.returncode == 0 and events("claim", CONDUCTOR), "the Conductor window's claim of the same fault goes through")
        check("NOTE" in out and "B1" in out, "the Conductor's pass prints a NOTE that names the check")
        r = last_run("claim", CONDUCTOR)
        check(r and r.get("override") == "conductor", "the timing line records the Conductor's pass (override=%s)"
              % r.get("override"))

        c = cli("claim", TASK)
        check(c.returncode == 0, "a task ticket with no refs is not refused (E12 is owed by build, fix and live only)")

        c = cli("claim", BROKEN, RIMFLOW_PREFLIGHT_BREAK="1")
        out = c.stdout + c.stderr
        check(c.returncode == 0 and "preflight did not run" in out,
              "a preflight that cannot run lets the claim through and says so")

        t = cli("preflight", "--timing")
        out = t.stdout
        check(t.returncode == 0 and "claim" in out and "p95" in out and "start" in out,
              "`rimflow preflight --timing` prints count, p50, p95 and max per door from the timing lines")
        check("refused" in out, "the timing report counts refusals")
    except Exception as e:
        check(False, "sandbox doors crashed: %s: %s" % (type(e).__name__, e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n = sum(1 for ok, _ in RESULTS if ok)
    print("PASS %d/%d" % (n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
