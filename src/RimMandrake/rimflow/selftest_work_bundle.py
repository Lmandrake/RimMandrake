#!/usr/bin/env python3
"""selftest_work_bundle.py - work bundles (work_bundle.py and its hooks in the two pipelines).

Item RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET; page
design/specs/2026-11-24-work-bundles/boundary.md (each t_ function is one promise of it, by name). Offline: fake items,
injected runners and a throwaway store; nothing launches, closes or publishes. Written before the code of each part and
seen failing on the base (work_bundle.py absent).
"""
import json
import os
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
TMP = tempfile.mkdtemp(prefix="selftest_work_bundle_")
os.environ["RM_WORK_BUNDLE_DIR"] = os.path.join(TMP, "store")
FAILS = []


def chk(fn, what):
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:300])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def WB():
    import work_bundle
    return work_bundle


def item(iid, state="proposed", effect=None, home=None, title=None, **kw):
    x = types.SimpleNamespace(id=iid, state=state, effect=effect, title=title or iid.lower(),
                              home={"home": home, "group": "g", "flag": "LOOKS CURRENT"} if home else None,
                              blocked=False, blocked_reason=None, blocked_on=None, blocked_also=(), wait_until=None,
                              wait_reason=None, lease=None, owner=None, history=[], caused_by=None)
    for k, v in kw.items():
        setattr(x, k, v)
    return x


# ---- part 1: the reality sort ---------------------------------------------------------------------------------------

def t_sort_runs_each_members_test_and_closes_only_green():
    W = WB()
    items = {"A_FIXED": item("A_FIXED", effect="cmd:exit-0-check"),
             "B_REAL": item("B_REAL", effect="cmd:exit-1-check"),
             "C_SCRIPT": item("C_SCRIPT", created_at="2026-11-20T00:00:00Z"),
             "D_NONE": item("D_NONE"),
             "E_BLIND": item("E_BLIND", effect="cmd:exit-2-check"),
             "F_SCRIPT_RED": item("F_SCRIPT_RED")}
    prose = {"C_SCRIPT": "## verify\npython3 src/RimMandrake/rimflow/acceptance/c_accept.py\n",
             "F_SCRIPT_RED": "## criteria\n- python3 src/RimMandrake/rimflow/selftest_f.py passes\n",
             "D_NONE": "## verify\nlook at it in game\n"}
    ran = []

    def run_effect(text, root):
        ran.append(text)
        return {"cmd:exit-0-check": ("holds", "ok"), "cmd:exit-1-check": ("fails", "red"),
                "cmd:exit-2-check": ("unmeasured", "exit 2")}[text]

    def run_script(path, root):
        ran.append(path)
        return ("holds", "") if "c_accept" in path else ("fails", "FAIL 1")
    exists = lambda p: True  # noqa: E731
    rows = W.sort(list(items), items, lambda i: prose.get(i, ""), run_effect, run_script, root=REPO, exists=exists,
                  added_at=lambda p: W._ts("2026-11-20T00:10:00Z"))
    by = {r["id"]: r for r in rows}
    chk(lambda: by["A_FIXED"]["verdict"] == "holds" and by["C_SCRIPT"]["verdict"] == "holds",
        "sort: a green outcome check and a green named script read holds")
    chk(lambda: by["B_REAL"]["verdict"] == "fails" and by["F_SCRIPT_RED"]["verdict"] == "fails",
        "sort: a red check and a red named script read fails")
    chk(lambda: by["D_NONE"]["verdict"] == "no_test" and "D_NONE" not in str(ran),
        "sort: a ticket with no runnable test reads no_test and nothing runs for it")
    chk(lambda: by["E_BLIND"]["verdict"] == "unmeasured" and by["E_BLIND"]["why"],
        "sort: a check that exits 2 reads unmeasured, with why")
    chk(lambda: len(ran) == 5, "sort: each test runs once (%d runs)" % len(ran))
    closed = []
    out = W.sort_apply(rows, "abc1234", lambda iid, sha, ev: (closed.append((iid, sha, ev)), (0, "closed"))[1])
    chk(lambda: sorted(c[0] for c in closed) == ["A_FIXED", "C_SCRIPT"],
        "sort apply: only the green members close (%s)" % [c[0] for c in closed])
    chk(lambda: all(c[1] == "abc1234" and "abc1234" in c[2] for c in closed),
        "sort apply: the close names the commit the test ran on, in --sha and in the evidence")
    chk(lambda: {r["id"]: r["act"] for r in out}["D_NONE"] == "listed no test",
        "sort apply: a no-test member is listed `no test`, never closed")
    # a vacuous check is never green
    rows2 = W.sort(["V"], {"V": item("V", effect="cmd:true")}, lambda i: "", run_effect, run_script, root=REPO)
    chk(lambda: rows2[0]["verdict"] == "unmeasured", "sort: a vacuous check (cmd:true) reads unmeasured, not holds")
    # a test path that does not exist is no test
    rows3 = W.sort(["N"], {"N": item("N")}, lambda i: "## verify\npython3 src/nope/x_accept.py\n", run_effect,
                   run_script, root=REPO, exists=lambda p: False)
    chk(lambda: rows3[0]["verdict"] == "no_test", "sort: a named script that does not exist is no test")
    # measured 2026-11-24 on RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION: its verify reads "Acceptance test:
    # none, a live systemd run (its offline twin is `python3 .../selftest_holder_resume.py`, ALL PASS)"
    none = "## verify\nAcceptance test: none, a live run (its offline twin is `python3 src/x/selftest_y.py`, ALL PASS).\n"
    rows4 = W.sort(["K"], {"K": item("K")}, lambda i: none, run_effect, run_script, root=REPO, exists=exists)
    chk(lambda: rows4[0]["verdict"] == "no_test", "sort: `Acceptance test: none` is no test, whatever script it names")
    # a named script that was there before the ticket was filed, and passes, was never seen failing on it
    old = {"O": item("O", created_at="2026-11-20T00:00:00Z")}
    rows5 = W.sort(["O"], old, lambda i: "## verify\npython3 src/a/c_accept.py\n", run_effect, run_script, root=REPO,
                   exists=exists, added_at=lambda p: W._ts("2026-11-01T00:00:00Z"))
    chk(lambda: rows5[0]["verdict"] == "holds_unproven", "sort: a green script older than the ticket reads holds_unproven")
    out5 = W.sort_apply(rows5, "abc1234", lambda *a: closed.append(a) or (0, ""))
    chk(lambda: not out5[0].get("closed") and "never seen failing" in out5[0]["act"],
        "sort apply: holds_unproven is kept for the worker, never closed (%s)" % out5[0]["act"])
    rows6 = W.sort(["O"], old, lambda i: "## verify\npython3 src/a/c_accept.py\n", run_effect, run_script, root=REPO,
                   exists=exists, added_at=lambda p: W._ts("2026-11-20T00:30:00Z"))
    chk(lambda: rows6[0]["verdict"] == "holds", "sort: a green script added with the ticket reads holds")


def t_sort_dry_closes_nothing():
    W = WB()
    rows = [{"id": "A", "verdict": "holds", "test": "cmd:x", "why": "ok"}]
    closed = []
    out = W.sort_apply(rows, "abc1234", lambda *a: closed.append(a) or (0, ""), dry=True)
    chk(lambda: not closed and out[0]["act"].startswith("would close"), "sort --dry: closes nothing, says would close")


def t_members_are_one_system():
    W = WB()
    items = {"P1_LEDGER": item("P1_LEDGER", home="pipeline:ledger"),
             "P2_LEDGER": item("P2_LEDGER", home="pipeline:ledger"),
             "Q_BRIDGE": item("Q_BRIDGE", home="pipeline:bridge"),
             "M_FLOW": item("M_FLOW", home="mod:FlowWorks"),
             "N_NOHOME": item("N_NOHOME"),
             "Z_DONE": item("Z_DONE", state="done", home="pipeline:ledger")}
    mods = {"FlowWorks", "Pyrelands"}
    reading = lambda it: {"mod": "FlowWorks" if it.id == "M_FLOW" else None, "unreadable": None}  # noqa: E731
    sysname, ids, why = W.resolve("pipeline:ledger", items, mods, reading)
    chk(lambda: sysname == "pipeline:ledger" and ids == ["P1_LEDGER", "P2_LEDGER"],
        "resolve: a home takes its open tickets (%s %s %s)" % (sysname, ids, why))
    sysname, ids, why = W.resolve("FlowWorks", items, mods, reading)
    chk(lambda: sysname == "mod:FlowWorks" and ids == ["M_FLOW"], "resolve: a mod name takes the mod's tickets")
    sysname, ids, why = W.resolve(["P1_LEDGER", "Q_BRIDGE"], items, mods, reading)
    chk(lambda: sysname is None and "pipeline:ledger" in why and "pipeline:bridge" in why,
        "resolve: ids of two systems are refused, naming each system (%s)" % why)
    sysname, ids, why = W.resolve(["N_NOHOME"], items, mods, reading)
    chk(lambda: sysname == "item:N_NOHOME" and ids == ["N_NOHOME"], "resolve: a ticket with no home is item:<ID>")
    chk(lambda: W.system_of(items["M_FLOW"], reading) == "mod:FlowWorks",
        "system_of: a mod ticket's system is mod:<Mod>")


def t_each_limit_names_its_danger():
    import re
    src = open(os.path.join(HERE, "work_bundle.py"), encoding="utf-8").read().splitlines()
    bad = []
    for n, line in enumerate(src):
        if re.match(r"^[A-Z][A-Z0-9_]*(?:_S|_MAX|_TOKENS|_MOST|_FRACTION)\s*=\s*[0-9]", line):
            near = " ".join(src[max(0, n - 4): n + 1])
            if "danger=" not in near and "class=" not in near:
                bad.append(line.strip())
    chk(lambda: not bad, "each number in work_bundle.py names its danger or its class (%s)" % bad)


def main():
    for t in [t_sort_runs_each_members_test_and_closes_only_green, t_sort_dry_closes_nothing, t_members_are_one_system,
              t_each_limit_names_its_danger]:
        print("-- %s" % t.__name__)
        try:
            t()
        except Exception as e:  # noqa: BLE001
            FAILS.append("%s raised %s: %s" % (t.__name__, type(e).__name__, e))
            print("FAIL %s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_work_bundle: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
