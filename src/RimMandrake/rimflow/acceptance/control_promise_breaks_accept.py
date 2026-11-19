#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_HARDEN_PROMISE_TESTS_SEVEN_BREAKS_SLIPPED_PAST.

Every promise on `design/specs/2026-11-18-pipeline-control-surface/boundary.md` is owed a test of its name in
`selftest_control.py` (`boundary_check.py`). This holds one deliberately broken stand-in of `control.py` per promise
(the breaks of `promise_tests_broken_on_purpose.md`, RIMMANDRAKE_BREAK_EACH_PROMISE_DOES_ITS_NAMED_TEST_FAIL) and
runs that promise's named test against it, in a private copy of src/RimMandrake/{rimflow,Utils,contracts} (temp dir):
the real control.py is never edited. First the unbroken copy must pass every named test (else a test that always
fails would read as a catch). Then each break must turn its named test red.

  exit 0  PASS: every break rejected by its named test
  exit 1  FAIL: a break slipped past (its named test passed), each named
  exit 3  COULD NOT LOOK: a break no longer matches control.py exactly once, the copy failed, or the unbroken copy
          does not pass a named test (cause named); not a verdict about the tests

`--only <promise> ...` runs those promises alone. A real `rm-probe` unit left by one break (a disabled kill leaves
`sleep 300` running) is stopped before the next, or its name collides in the next test."""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
PAGE = os.path.join(REPO, "design", "specs", "2026-11-18-pipeline-control-surface", "boundary.md")
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import boundary_check as B  # noqa: E402

RUN_ONE = r"""
import shutil, sys
sys.path.insert(0, ".")
import selftest_control as S
try:
    getattr(S, sys.argv[1])()
except Exception as e:      # noqa: BLE001  a test that raises is red, as in selftest_control.main()
    S.check(False, "%s raised %s: %s" % (sys.argv[1], type(e).__name__, e))
shutil.rmtree(S.TMP, ignore_errors=True)
if S.FAILS:
    print("RED %s" % " | ".join(S.FAILS[:3])); sys.exit(1)
if S.UNRUN:
    print("UNRUN %s" % "; ".join(S.UNRUN)); sys.exit(2)
print("GREEN"); sys.exit(0)
"""

BREAKS = {}     # promise -> (the break in one line, [(text in control.py, its replacement)])


def brk(promise, what, *edits):
    BREAKS[promise] = (what, list(edits))


brk("off-blocks-starts", "switch() off cancels no unstarted run and condition() re-checks no switch",
    ("            cancelled = _cancel_in_scope(c, scope, why, now)\n        else:", "            cancelled = []\n        else:"),
    ('            rows = blocking(c, run_scopes(json.loads(r["spec"] or "{}")), now)\n            if rows:',
     '            rows = blocking(c, run_scopes(json.loads(r["spec"] or "{}")), now)\n            if False:'))
brk("one-admission-point", "call_sites() marks every systemd-run site routed",
    ('"routed": not why.startswith("UNROUTED"), "why": why})', '"routed": True, "why": why})'))
brk("his-hold-refuses-launch", "blocking() drops owner-layer rows",
    ("rows = [r for r in c.execute(q, scopes).fetchall() if _live(r, now)]",
     'rows = [r for r in c.execute(q, scopes).fetchall() if _live(r, now) and r["layer"] != "owner"]'))
brk("three-named-stops", "escalate() always finds nothing to do: a write-now order never becomes a kill",
    ("        if not s:   # a timer acts", "        if True:   # a timer acts"))
brk("stop-reaches-the-agent", "hook() returns exit 0 with the stop text (the agent is shown only exit-2 text)",
    ("    return 2, text\n", "    return 0, text\n"))
brk("kill-verified-dead", "_verdict() does not count a survivor (dead=False) as a failure",
    ('x["dead"] is False or (x["dead"] is None and "nothing was running" not in x["said"])]\n    return not bad, bad',
     '(x["dead"] is None and "nothing was running" not in x["said"])]\n    return not bad, bad'))
brk("kill-works-without-the-store", "stop() re-raises Unreadable for a unit kill too",
    ("        if not emergency:\n            raise\n", "        if True:\n            raise\n"))
brk("killed-run-needs-no-hand-step", "_finish_kill() never calls reap_detached()",
    ('row["bookkeeping"] = (reaper or reap_detached)(r, act, why) if r.get("family") == "detached" or',
     'row["bookkeeping"] = "no bookkeeping done" if r.get("family") == "detached" or'))
brk("stopped-run-spends-no-trial", "stop() charges a live run's held trials instead of releasing them",
    ('                if _release(c, "run=?", (r["id"],), "fail_system: stopped (%s): %s" % (mode, why), now, True):\n'
     '                    faulted.append(r["id"])\n'
     '                c.execute("UPDATE reservations SET state=\'voided\', settled_at=? WHERE run=? AND state=\'charged\'",\n'
     '                          (now, r["id"]))',
     '                c.execute("UPDATE reservations SET state=\'charged\', settled_at=? WHERE run=? AND state=\'held\'",\n'
     '                          (now, r["id"]))'))
brk("look-charged-only-on-a-verdict", "settle() charges the look whether or not the verdict is valid",
    ('        if valid:\n            if c.execute("SELECT 1 FROM voids', '        if True:\n            if c.execute("SELECT 1 FROM voids'))
brk("void-gives-back-once", "_account() adds the voided quantity back to available: one void gives back twice",
    ('"available": base + g - charged - held}', '"available": base + g - charged - held + voided}'))
brk("void-never-moves-a-stage", "_stage_advanced_on_voided() returns [] at once",
    ("def _stage_advanced_on_voided(c, mods=None):\n", "def _stage_advanced_on_voided(c, mods=None):\n    return []\n"))
brk("unreadable-store-launches-nothing", "launch_unit() runs systemd-run with the payload when the store is unreadable",
    ("    except Unreadable as e:\n        return _refusal(args, str(e), unreadable=True)",
     '    except Unreadable as e:\n        return runner(["systemd-run"] + args, **kw)'))
brk("probe-never-lies", "_cgroup_pids() reads a failed `systemctl show` as an empty cgroup",
    ('        return P.could_not_look("systemctl show failed (rc %d): %s" % (rc, out.strip()[:120])), ""',
     '        return P.empty(), ""'))
brk("same-command-twice", "_idem_hit() never finds an earlier act: a keyed command sent twice acts twice",
    ('    if not idem:\n        return None\n    r = c.execute("SELECT * FROM acts WHERE idem=?"',
     '    if True:\n        return None\n    r = c.execute("SELECT * FROM acts WHERE idem=?"'))
brk("every-change-is-an-act", "_act() records `before` as null on every act",
    ('"before": json.dumps(before, sort_keys=True, default=str),', '"before": json.dumps(None),'))
brk("binds-at-once-from-any-clone", "the pipe CLI suffixes the store path with a hash of its own folder",
    ("def main(argv=None):\n    av = list(sys.argv[1:] if argv is None else argv)\n",
     "def main(argv=None):\n    av = list(sys.argv[1:] if argv is None else argv)\n    if os.environ.get(\"RM_CONTROL_DB\"):\n"
     "        import hashlib\n        os.environ[\"RM_CONTROL_DB\"] += \".\" + hashlib.sha1(HERE.encode()).hexdigest()[:8]\n"))
brk("verbs-answer-in-a-second", "main() sleeps 1.1 s before every verb",
    ("def main(argv=None):\n    av = list(sys.argv[1:] if argv is None else argv)\n",
     "def main(argv=None):\n    av = list(sys.argv[1:] if argv is None else argv)\n    time.sleep(1.1)\n"))
brk("queue-order-is-the-store's", "queue_apply() returns the shipped order",
    ("        return _queue_order(_queue_rows(c), mods)\n", "        return [key(m) for m in mods]\n"))
brk("counts-and-limits-are-adjustments", "_used() freezes the count at the first adjustment's measured value",
    ('def _used(c, mod, res, measured):\n    off = sum(r["delta"] or 0 for r in _adj(c, mod, res, "count"))\n',
     'def _used(c, mod, res, measured):\n    rows = _adj(c, mod, res, "count")\n    off = sum(r["delta"] or 0 for r in rows)\n'
     '    if rows and _numeric(measured):\n'
     '        m0 = json.loads(c.execute("SELECT before FROM acts WHERE id=?", (rows[0]["act"],)).fetchone()["before"])'
     '.get("measured")\n'
     '        measured = m0 if _numeric(m0) else measured\n'))
brk("a-test-never-touches-the-live-store", "test_process() ignores RM_UNDER_SELFTEST and RM_OWNER_HOLD_FILE (the live "
    "path is a decoy in the copy, so the break cannot reach the live store)",
    ('    if os.environ.get("RM_UNDER_SELFTEST") or os.environ.get("RM_OWNER_HOLD_FILE"):\n        return True',
     '    if False:\n        return True'),
    ('DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".local", "state", "rimmandrake", "control", "control.db")',
     'DEFAULT_DB = os.path.join(os.path.dirname(HERE), "decoy-live-store", "control.db")'))
brk("ended-run-is-recorded-ended", "hook_cmd() does not fall through to the seat clones' control.py",
    ("[os.path.abspath(__file__)] + \\\n        [os.path.join(c, rel) for c in wrapup.seat_clones()]",
     "[os.path.abspath(__file__)]"))
brk("permit-never-ghosts", "switch() leaves the permit alone when the all-switch moves",
    ('        if scope == "all":      # the containment permit follows the all-switch from every caller, not only `pipe`',
     '        if False:'))
brk("before-is-read", "undo() of an OFF ignores its before and always leaves the scope ON",
    ('            prior = json.loads(a["before"] or "null")     # the switch row this off replaced (before-is-read)',
     '            prior = None'))
brk("reused-name-runs-again", "_admit() never treats a reuse_name run as over",
    ('again = spec.get("reuse_name") and old is not None and old["state"] not in LIVE_STATES', "again = False"))


def stop_probe_units():
    r = subprocess.run(["systemctl", "--user", "list-units", "--all", "--no-legend", "--plain"], capture_output=True,
                       text=True, timeout=30)
    units = [ln.split()[0] for ln in r.stdout.splitlines() if ln.split() and "rm-probe" in ln.split()[0]]
    if units:
        subprocess.run(["systemctl", "--user", "stop"] + units, capture_output=True, timeout=60)
        subprocess.run(["systemctl", "--user", "reset-failed"] + units, capture_output=True, timeout=60)


def run_test(rimflow, test):
    """-> ("GREEN"|"RED"|"UNRUN"|"ERROR", line)."""
    stop_probe_units()
    try:
        r = subprocess.run([sys.executable, "-c", RUN_ONE, test], cwd=rimflow, capture_output=True, text=True,
                           timeout=600)
    except subprocess.TimeoutExpired:
        return "ERROR", "timed out after 600 s"
    out = (r.stdout or "").strip().splitlines()
    word = {0: "GREEN", 1: "RED", 2: "UNRUN"}.get(r.returncode, "ERROR")
    return word, (out[-1] if out else (r.stderr or "").strip()[-200:])[:240]


def main(argv):
    only = argv[argv.index("--only") + 1:] if "--only" in argv else []
    try:
        names = B.promises(PAGE)
    except Exception as e:      # noqa: BLE001
        print("COULD NOT LOOK control_promise_breaks: the page cannot be read: %s" % e)
        return 3
    if sorted(names) != sorted(BREAKS):
        print("COULD NOT LOOK control_promise_breaks: the page's promises and this file's breaks differ: page only %s; "
              "breaks only %s" % (sorted(set(names) - set(BREAKS)), sorted(set(BREAKS) - set(names))))
        return 3
    names = [n for n in names if not only or n in only]
    tmp = tempfile.mkdtemp(prefix="control_promise_breaks_")
    try:
        for d in ("rimflow", "Utils", "contracts"):
            shutil.copytree(os.path.join(REPO, "src", "RimMandrake", d), os.path.join(tmp, "src", "RimMandrake", d),
                            symlinks=True, ignore=shutil.ignore_patterns("__pycache__"))
        rimflow = os.path.join(tmp, "src", "RimMandrake", "rimflow")
        target = os.path.join(rimflow, "control.py")
        with open(target, encoding="utf-8") as f:
            orig = f.read()
        want = hashlib.sha256(orig.encode("utf-8")).hexdigest()
        blind = []
        for n in names:     # the control: the unbroken copy passes every named test
            word, line = run_test(rimflow, B.test_name(n))
            if word != "GREEN":
                blind.append("%s: unbroken, %s is %s (%s)" % (n, B.test_name(n), word, line))
        for n in names:
            if any(orig.count(old) != 1 for old, _new in BREAKS[n][1]):
                blind.append("%s: its break no longer matches control.py exactly once" % n)
        if blind:
            print("COULD NOT LOOK control_promise_breaks: %s" % "; ".join(blind))
            return 3
        slipped = []
        for n in names:
            what, edits = BREAKS[n]
            src = orig
            for old, new in edits:
                src = src.replace(old, new)
            with open(target, "w", encoding="utf-8") as f:
                f.write(src)
            try:
                word, line = run_test(rimflow, B.test_name(n))
            finally:
                with open(target, "w", encoding="utf-8") as f:
                    f.write(orig)
            with open(target, "rb") as f:
                if hashlib.sha256(f.read()).hexdigest() != want:
                    print("COULD NOT LOOK control_promise_breaks: the copy did not restore after %s" % n)
                    return 3
            if word in ("UNRUN", "ERROR"):
                print("COULD NOT LOOK control_promise_breaks: %s under the break of %s: %s" % (word, n, line))
                return 3
            print("%-8s %s: %s (%s)%s" % ("REJECTED" if word == "RED" else "SLIPPED", n, what, B.test_name(n),
                                          "" if word == "RED" else ": the test passed"))
            if word == "GREEN":
                slipped.append(n)
        if slipped:
            print("FAIL control_promise_breaks: %d of %d breaks slipped past their named test: %s" % (
                len(slipped), len(names), ", ".join(slipped)))
            return 1
        print("PASS control_promise_breaks: %d of %d breaks rejected by their named test" % (len(names), len(names)))
        return 0
    finally:
        stop_probe_units()
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
