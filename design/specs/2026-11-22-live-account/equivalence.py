#!/usr/bin/env python3
"""equivalence.py - run every OLD reader of the live account and the one home on the same cases; print the table.

The old readers are taken verbatim from the base commit (default 9d0bc39906, the tree before the merge) with
`git show`; only the function bodies run, with their world seam (run / subprocess / env.run / sh / _ssh) replaced by
the case's recorded exit code and stdout. Cases: src/RimMandrake/Utils/fixtures/account_live_cases.json.
Each verdict is normalised to the account name, or UNMEASURED (None, {}, a raise and a missing key all read so).

    python3 equivalence.py [BASE]        exit 0 when every difference is in KNOWN (classed below), 1 otherwise
"""
import ast
import json
import os
import subprocess
import sys
import types

TOP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
UT = os.path.join(TOP, "src/RimMandrake/Utils")
sys.path[:0] = [UT, os.path.join(TOP, "src/RimMandrake/rimflow")]
import account_live as AL  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else "9d0bc39906"
U = "UNMEASURED"


def old_func(path, name):
    src = subprocess.run(["git", "-C", TOP, "show", "%s:%s" % (BASE, path)], capture_output=True, text=True,
                         check=True).stdout
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node)
    raise SystemExit("%s:%s has no def %s" % (BASE, path, name))


def world(c):
    """-> run(argv, ...) giving the case's (rc, stdout), raising its exception."""
    def run(*a, **k):
        if c["raises"] == "timeout":
            raise subprocess.TimeoutExpired("claude-account", 1)
        if c["raises"] == "notfound":
            raise FileNotFoundError("claude-account")
        if c["raises"] == "oserror":
            raise PermissionError("claude-account")
        return c["rc"], c["out"]
    return run


def build(path, name, extra):
    g = {"json": json, "os": os, "subprocess": subprocess}
    g.update(extra)
    exec(old_func(path, name), g)
    return g[name]


def norm(v):
    return v if isinstance(v, str) and v else U


def old_failover(c):
    # account_failover.run is switching_plan-like: (rc, out); a raise there is caught inside run(), not here
    def run(argv, full=False, timeout=600):
        try:
            return world(c)()
        except subprocess.TimeoutExpired:
            return 124, "timed out"
        except OSError:
            return 127, "could not run"
    return build("src/RimMandrake/Utils/account_failover.py", "live_account", {"run": run, "CA": "ca"})()


def old_switching_plan(c):
    def run(argv, full=False, timeout=600):
        try:
            return world(c)()
        except subprocess.TimeoutExpired:
            return 124, "timed out"
        except OSError:
            return 127, "could not run"
    return build("src/RimMandrake/Utils/switching_plan.py", "switcher_status", {"run": run, "CA": "ca"})().get("live")


def old_slot_allocator(c):
    def srun(argv, **k):
        rc, out = world(c)()
        return types.SimpleNamespace(returncode=rc, stdout=out)
    fake_sp = types.SimpleNamespace(run=srun, TimeoutExpired=subprocess.TimeoutExpired)
    env = {k: v for k, v in os.environ.items() if k != "RM_SLOT_LIVE_LOGIN"}
    fake_os = types.SimpleNamespace(environ=env, path=os.path)
    return build("src/RimMandrake/Utils/slot_allocator.py", "live_login_name", {"subprocess": fake_sp, "os": fake_os})()


class Unmeasured(Exception):
    pass


def old_running_now(c):
    f = build("src/RimMandrake/Utils/running_now.py", "collect_inuse",
              {"Unmeasured": Unmeasured, "CLAUDE_ACCOUNT": "ca"})
    try:
        return f(types.SimpleNamespace(run=world(c)))["live"]
    except Unmeasured:
        return None


def old_account_handover(c):
    # account_handover.py (main, `check`): live = json.loads(sh(CLAUDE_ACCOUNT, "--json", "status").stdout)["live"]
    # sh() is subprocess.run with no timeout; a raise ends the pass with a traceback.
    try:
        rc, out = world(c)()
        return json.loads(out)["live"]
    except Exception:  # noqa: BLE001
        return None


def old_remote_live(c):
    def _ssh(target, script, timeout=120):
        try:
            return world(c)()
        except (OSError, subprocess.TimeoutExpired) as e:
            return 124, type(e).__name__
    return build("src/RimMandrake/Utils/account_usage.py", "remote_live", {"_ssh": _ssh})("t")[1]


OLD = [("account_failover.live_account", old_failover), ("switching_plan.switcher_status", old_switching_plan),
       ("slot_allocator.live_login_name", old_slot_allocator), ("running_now.collect_inuse", old_running_now),
       ("account_handover check", old_account_handover), ("account_usage.remote_live", old_remote_live)]

# Every difference between an old reader and the one home, classed. (reader, case) -> why the new verdict stands.
OLD_WRONG_EXIT = "old was wrong: a non-zero exit is a failed status run, not an answer (the switcher exits 0 on success)"
OLD_WRONG_PREFIX = "old was wrong: a warning line before the JSON hid the account (json.loads of the whole stdout)"
OLD_WRONG_NOTOK = "old was wrong: \"ok\": false is the switcher's refusal; its live field is not a reading"
OLD_WRONG_NOOK = ("old was wrong: a status with no ok key (an older switcher, the test fakes) names its account; "
                  "only ok=false is a refusal")
OLD_WRONG_TYPE = "old was wrong: a non-string live is not an account name"
PREFIXED = ("warning-line-before", "login-banner-before-and-note-after", "acceptance-fake")
KNOWN = {}
for r in ("slot_allocator.live_login_name", "running_now.collect_inuse", "account_handover check",
          "account_usage.remote_live"):
    for cname in PREFIXED:
        KNOWN[(r, cname)] = OLD_WRONG_PREFIX
for r in ("slot_allocator.live_login_name", "account_handover check", "account_usage.remote_live"):
    KNOWN[(r, "rc3-with-a-live-name")] = OLD_WRONG_EXIT
for r in ("account_failover.live_account", "switching_plan.switcher_status", "slot_allocator.live_login_name",
          "account_handover check", "account_usage.remote_live"):
    KNOWN[(r, "not-ok-rc0")] = OLD_WRONG_NOTOK
for cname in ("no-ok-key", "long-padding-before"):
    KNOWN[("running_now.collect_inuse", cname)] = OLD_WRONG_NOOK
KNOWN[("running_now.collect_inuse", "live-not-a-string")] = OLD_WRONG_TYPE

def main():
    cases = json.load(open(os.path.join(UT, "fixtures/account_live_cases.json")))["cases"]
    rows, unexplained, diffs, raised, used = [], [], 0, {}, set()
    for c in cases:
        new = norm(AL.name_of(AL.read(run=world(c))))
        want = c["want"]["live"] if c["want"]["kind"] == "value" else U
        if new != want:
            unexplained.append("NEW WRONG %s: new %s, the case wants %s" % (c["name"], new, want))
        olds = []
        for rname, f in OLD:
            try:
                v = norm(f(c))
            except Exception as e:  # noqa: BLE001  an old reader that raises on this input
                raised.setdefault(rname, []).append(c["name"])
                v = "%s (raised %s)" % (U, type(e).__name__)
            olds.append(v)
            if v.split(" ")[0] != new:
                diffs += 1
                used.add((rname, c["name"]))
                if (rname, c["name"]) not in KNOWN:
                    unexplained.append("UNCLASSED %s on %s: old %s, new %s" % (rname, c["name"], v, new))
        rows.append((c["name"], c["source"].split(":")[0], new, olds))
    w = max(len(r[0]) for r in rows)
    print("cases %d (%d recorded, %d fixture); old readers %d; base %s" % (
        len(cases), sum(r[1] == "recorded" for r in rows), sum(r[1] != "recorded" for r in rows), len(OLD), BASE))
    print("%-*s  %-8s  %-10s  %s" % (w, "case", "source", "new", " | ".join(n.split(".")[0] for n, _ in OLD)))
    for name, src, new, olds in rows:
        print("%-*s  %-8s  %-10s  %s" % (w, name, src, new, " | ".join(olds)))
    for k in sorted(set(KNOWN) - used):  # a class with no difference behind it is a stale class: the table is wrong
        unexplained.append("STALE CLASS %s / %s: no difference there" % k)
    print("differences old vs new: %d; classed %d; unexplained %d" % (diffs, len(used & set(KNOWN)), len(unexplained)))
    for k, why in sorted(KNOWN.items()):
        print("  classed  %s / %s: %s" % (k[0], k[1], why))
    for rname, names in sorted(raised.items()):
        print("  raised   %s on %d cases: %s" % (rname, len(names), ", ".join(names)))
    for u in unexplained:
        print("  " + u)
    print("EQUIVALENCE %s" % ("PASS" if not unexplained else "FAIL"))
    return 0 if not unexplained else 1


if __name__ == "__main__":
    sys.exit(main())
