#!/usr/bin/env python3
"""work_bundle.py: work bundles. All ready tickets of one system, worked by one run in one context, restarted fresh from
its state file until each member has an outcome. No model and no tokens of its own.

Item RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET. Design
design/specs/2026-11-24-work-bundles/design.md (section 7: the owner's four decisions); page boundary.md beside it;
selftest selftest_work_bundle.py.

    python3 src/RimMandrake/rimflow/work_bundle.py sort <home | Mod | ID...> [--dry]   the reality sort (design step 0)

A system is a home of list_home.py (pipeline:<part>, game:<need>, machine:<name>), a mod (mod:<folder>), or item:<ID>
for a ticket with no home. The sort runs each open member's test on this clone's build: a green test closes the member
as already fixed, with that commit named; a member with no runnable test is listed `no test` and never closed.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ITEM = "RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET"
UNIT = "rm-work-bundle"
CLOSED = ("done", "dropped", "superseded")
SCRIPT_RX = re.compile(r"python3\s+((?:design|src|skills|infrastructure)/[^\s'\"`]+?\.py)(?=[\s'\"`]|$)")
NO_TEST_RX = re.compile(r"acceptance test:\s*none\b", re.I)
# A named script added this long before its ticket's filing still counts as written with it: the filing rule drafts the
# test first and files minutes later in the same run. budget: danger=a script written for another purpose shortly
# before the ticket reads as its acceptance test; longest=UNMEASURED (the gap between writing a test and filing)
WRITTEN_WITH_SLACK_S = 6 * 3600
TEST_SECTIONS = re.compile(r"^## (?:verify|criteria|acceptance)[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S | re.I)
# Hang guard for one `rimflow close` (a publish retries a push): list_effect.CLOSE_TIMEOUT_S, the class=publish.
CLOSE_TIMEOUT_S = 21600  # budget: class=publish


def _one(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def _g(x, k, default=None):
    return x.get(k, default) if isinstance(x, dict) else getattr(x, k, default)


# ---- systems --------------------------------------------------------------------------------------------------------

def system_of(it, reading):
    """-> the system of one ticket: its mod (mod:<Mod>, mod_work's one rule), else its home, else item:<ID>. None when
    its mod work could not be read."""
    r = reading(it)
    if not isinstance(r, dict) or r.get("unreadable"):
        return None
    if r.get("mod"):
        return "mod:%s" % r["mod"]
    home = _g(it, "home")
    h = home.get("home") if isinstance(home, dict) else None
    if h and h != "unplaced":
        return h
    return "item:%s" % _g(it, "id")


def resolve(target, items, mods, reading):
    """-> (system, [open member ids], why). target: a home, a mod name (or mod:<Mod>), or a list of ids. Ids of two
    systems are refused (system None), and why names each id's system."""
    if isinstance(target, (list, tuple)) and len(target) == 1 and not re.match(r"^[A-Z][A-Z0-9_]{7,}$", target[0]):
        target = target[0]
    if isinstance(target, (list, tuple)):
        got, sy = [], {}
        for i in target:
            x = items.get(i)
            if x is None:
                return None, [], "%s is not an item of the ledger" % i
            if _g(x, "state") in CLOSED:
                return None, [], "%s is %s" % (i, _g(x, "state"))
            s = system_of(x, reading)
            if s is None:
                return None, [], "could not look which system %s belongs to" % i
            sy[i] = s
            got.append(i)
        if len(set(sy.values())) > 1:
            return None, [], "two systems are never in one bundle: " + "; ".join("%s is %s" % kv for kv in sy.items())
        return next(iter(sy.values())), got, "the named tickets"
    t = str(target)
    if not t.startswith(("mod:", "pipeline:", "game:", "machine:", "item:")):
        m = next((m for m in mods if m.lower() == t.lower()), None)
        if not m:
            return None, [], "%r is not a home (pipeline:<part>, game:<need>, machine:<name>), a mod or ticket ids" % t
        t = "mod:%s" % m
    ids = sorted(i for i, x in items.items() if _g(x, "state") not in CLOSED and system_of(x, reading) == t)
    return t, ids, "the open tickets of %s" % t


# ---- part 1: the reality sort ---------------------------------------------------------------------------------------

def test_of(it, prose, exists=None):
    """-> ("effect", check) | ("script", repo path) | None: the ticket's outcome check, else the first existing
    `python3 <repo path>.py` in its ## verify, ## criteria or ## acceptance prose."""
    if _g(it, "effect"):
        return "effect", _g(it, "effect")
    exists = exists or (lambda p: os.path.isfile(os.path.join(REPO, p)))
    secs = TEST_SECTIONS.findall(prose or "")
    if any(NO_TEST_RX.search(sec) for sec in secs):     # the absence is a decision: a script named there is no test
        return None
    for sec in secs:
        for p in SCRIPT_RX.findall(sec):
            if exists(p):
                return "script", p
    return None


def run_script(path, root):
    """-> (holds|fails|unmeasured, output) of `python3 <path>` with no arguments, from root."""
    import list_effect as LE     # one named script is run as an outcome check is, under the checks' own hang guard
    try:
        r = subprocess.run([sys.executable, path], cwd=root, capture_output=True, text=True, errors="replace",
                           timeout=LE.CMD_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return "unmeasured", "it ran past its %ds hang guard" % LE.CMD_TIMEOUT_S
    except OSError as e:
        return "unmeasured", "it could not start: %s" % e
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if r.returncode in (0, 1):
        return ("holds" if r.returncode == 0 else "fails"), out
    return "unmeasured", "exit %d (only 0 holds and 1 fails)\n%s" % (r.returncode, out)


def _ts(iso):
    """-> the epoch of an ISO time; raises ValueError when it cannot be read (the caller says so)."""
    import datetime as dt
    return dt.datetime.fromisoformat(str(iso).replace("Z", "+00:00")).timestamp()


def added_at_git(path, root=REPO):
    """-> the epoch of the commit that first added `path`; raises when git cannot say (the caller says so)."""
    import time_budget as TB
    r = subprocess.run(["git", "-C", root, "log", "--diff-filter=A", "--format=%ct", "--", path], capture_output=True,
                       text=True, timeout=TB.CALL_S, stdin=subprocess.DEVNULL)
    ts = [int(x) for x in r.stdout.split()] if r.returncode == 0 else []
    if not ts:
        raise RuntimeError("git log names no commit that added %s (exit %d)" % (path, r.returncode))
    return min(ts)


def sort(ids, items, prose_of, run_effect, run_script_fn, root=REPO, exists=None, added_at=None):
    """-> one row per member: {id, test, verdict: holds|holds_unproven|fails|unmeasured|no_test, why}. Each test runs
    once. An outcome check was seen failing when it was attached (list_effect.attach_gate); a named script was not, so a
    green one counts only when it was added with or after its ticket (WRITTEN_WITH_SLACK_S), else holds_unproven."""
    added_at = added_at or (lambda p: added_at_git(p, root))
    import list_effect as LE
    rows = []
    for i in ids:
        it = items[i]
        t = test_of(it, prose_of(i), exists)
        if not t:
            rows.append({"id": i, "test": None, "verdict": "no_test",
                         "why": "no outcome check, and no existing python3 <repo path>.py in its ## verify, ## criteria or "
                                "## acceptance"})
            continue
        kind, what = t
        if kind == "effect":
            p = LE.parse(what)
            if p.get("kind") == "cmd" and LE.VACUOUS.match(p["cmd"]):
                rows.append({"id": i, "test": what, "verdict": "unmeasured",
                             "why": "the check %r is vacuous: it holds whatever the work" % what})
                continue
            verdict, out = run_effect(what, root)
        else:
            verdict, out = run_script_fn(what, root)
            if verdict == "holds":
                try:
                    filed, born, cause = _ts(_g(it, "created_at")), added_at(what), None
                except Exception as e:  # noqa: BLE001 - not dated: never proven, and the row says why
                    filed = born = None
                    cause = "could not be dated against the filing (%s: %s)" % (type(e).__name__, _one(e, 120))
                if cause or born < filed - WRITTEN_WITH_SLACK_S:
                    verdict = "holds_unproven"
                    out = ("it holds, but it %s, so it was never seen failing on this ticket: the worker classes it"
                           % (cause or "was there before the ticket was filed"))
            what = "python3 %s" % what
        rows.append({"id": i, "test": what, "verdict": verdict, "why": _one(out, 300) or "(no output)"})
    return rows


def close_member(iid, sha, evidence):
    """`rimflow close <iid> --no-code "already fixed: ... at <sha>" --evidence ...` as the pipeline's act. -> (rc, output).
    The build the test ran on is named in the text, not in --sha: that build is often a ledger-only commit, which
    `close --sha` refuses, and the commit that did the work is not known to the sort (list_effect.close_item's form)."""
    argv = [sys.executable, os.path.join(HERE, "cli.py"), "close", iid, "--no-code",
            "already fixed: its test holds on the build %s (work_bundle sort)" % sha, "--evidence", evidence,
            "--seat", "BENCH", "--why", "pipeline act (work_bundle sort): its test holds at %s, so it was already fixed"
            % sha, "--reason", "already fixed: its test holds at %s (work_bundle sort)" % sha, "--publish"]
    env = dict(os.environ, RM_ROLE_UNIT=os.environ.get("RM_ROLE_UNIT") or UNIT, RIMFLOW_SEAT="BENCH")
    try:
        r = subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True, errors="replace",
                           timeout=CLOSE_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, "%s: %s" % (type(e).__name__, e)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def sort_apply(rows, sha, closer=close_member, dry=False):
    """Close each `holds` row as already fixed at `sha`. -> rows with `act`."""
    out = []
    for r in rows:
        r = dict(r)
        if r["verdict"] == "holds":
            ev = "%s holds at %s (work_bundle sort): %s" % (r["test"], sha, _one(r.get("why"), 200))
            if dry:
                r["act"] = "would close as already fixed at %s" % sha
            else:
                rc, said = closer(r["id"], sha, ev)
                r["act"] = ("closed as already fixed at %s" % sha if rc in (0, 4) else
                            "close REFUSED (rc %s): %s" % (rc, _one(said, 300)))
                r["closed"] = rc in (0, 4)
        elif r["verdict"] == "holds_unproven":
            r["act"] = "kept: green, but never seen failing on this ticket"
        elif r["verdict"] == "no_test":
            r["act"] = "listed no test"
        elif r["verdict"] == "fails":
            r["act"] = "kept: its test fails"
        else:
            r["act"] = "kept: its test is unmeasured"
        out.append(r)
    return out


def build_sha(root=REPO):
    """-> (sha, None) when the clone stands level on origin/main with no tracked change, else (None, the fault and its
    repair): a close names a published commit, and a test run on local changes is not that commit's reading."""
    def git(*a):
        import time_budget as TB
        return subprocess.run(["git", "-C", root] + list(a), capture_output=True, text=True, timeout=TB.CALL_S,
                              stdin=subprocess.DEVNULL)
    head, main = git("rev-parse", "HEAD"), git("rev-parse", "origin/main")
    if head.returncode or main.returncode:
        return None, "could not read HEAD or origin/main in %s" % root
    dirty = git("status", "--porcelain", "--untracked-files=no").stdout.strip()
    if head.stdout.strip() != main.stdout.strip() or dirty:
        return None, ("the clone is not level with origin/main%s; run ./sync (or publish your changes), then sort again"
                      % (" and has tracked changes" if dirty else ""))
    return head.stdout.strip()[:10], None


# ---- reading the ledger ---------------------------------------------------------------------------------------------

def world():
    import list_effect as LE
    return LE._world()


def prose_reader():
    import model as LM

    def read(iid):
        for d in (LM.ITEMS, getattr(LM, "CLOSED", os.path.join(LM.ITEMS, "closed"))):
            p = os.path.join(d, iid + ".md")
            if os.path.isfile(p):
                with open(p, encoding="utf-8", errors="replace") as f:
                    return f.read()
        return ""
    return read


def mod_reader():
    import mod_work as MW
    import model as LM
    modset = MW.mods()
    return modset, (lambda it: MW.reading(it, modset, LM.ITEMS))


# ---- the command ----------------------------------------------------------------------------------------------------

def cmd_sort(o):
    import list_effect as LE
    w = world()
    modset, reading = mod_reader()
    system, ids, why = resolve(o.target if len(o.target) > 1 else o.target[0], w.items, modset, reading)
    if not system:
        print("REFUSED: %s" % why)
        return 2
    sha, fault = build_sha()
    if fault and not o.dry:
        print("REFUSED (a fault of form; the repair): %s" % fault)
        return 3
    rows = sort(ids, w.items, prose_reader(), LE.run, run_script, root=REPO)
    rows = sort_apply(rows, sha or "HEAD", dry=o.dry)
    for r in rows:
        print("%-66s %-10s %s | %s" % (r["id"], r["verdict"], r["act"], _one(r.get("test") or "-", 90)))
    n = {}
    for r in rows:
        n[r["verdict"]] = n.get(r["verdict"], 0) + 1
    print("work_bundle sort%s %s: %d member(s); %s" % (" --dry" if o.dry else "", system, len(rows),
                                                       ", ".join("%s %d" % kv for kv in sorted(n.items()))))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sort", help="the reality sort: run each member's test, close the green ones as already fixed")
    s.add_argument("target", nargs="+", help="a home (pipeline:ledger), a mod (FlowWorks) or ticket ids of one system")
    s.add_argument("--dry", action="store_true", help="print what it would close; write nothing")
    o = ap.parse_args(argv)
    return {"sort": cmd_sort}[o.cmd](o)


if __name__ == "__main__":
    sys.exit(main())
