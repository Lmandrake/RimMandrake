#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_HARDEN_PROMISE_TESTS_SEVEN_BREAKS_SLIPPED_PAST.

Every promise on `design/specs/2026-11-18-pipeline-control-surface/boundary.md` is owed a test of its name in
`selftest_control.py` (`boundary_check.py`). This holds one deliberately broken stand-in of `control.py` (or of `mod_owner_hold.py`, for his hold's mirror) per promise
(the breaks of `promise_tests_broken_on_purpose.md`, RIMMANDRAKE_BREAK_EACH_PROMISE_DOES_ITS_NAMED_TEST_FAIL) and
runs that promise's named test against it, in a private copy of src/RimMandrake/{rimflow,Utils,contracts} (temp dir):
the real files are never edited. First the unbroken copy must pass every named test (else a test that always
fails would read as a catch). Then each break must turn its named test red.

  exit 0  PASS: every break rejected by its named test
  exit 1  FAIL: a break slipped past (its named test passed), each named
  exit 3  COULD NOT LOOK: a break no longer matches its file exactly once, the copy failed, or the unbroken copy
          does not pass a named test (cause named); not a verdict about the tests

`--only <promise> ...` runs those promises alone. A real `rm-probe` unit left by one break (a disabled kill leaves
`sleep 300` running) is stopped after its test, or its name collides in the next test: only a unit (or escalation
timer) whose systemd commands name that test's own temp store, never another run's (a machine-wide `rm-probe` sweep
killed a sibling's real-agent drill, 2026-11-19, RIMMANDRAKE_SPARE_OTHER_RUNS_PROBE_UNITS_SWEEP_KILLED_DRILL)."""
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
import shutil, subprocess, sys
sys.path.insert(0, ".")
import selftest_control as S


def own_units(tmp):
    # this test's leftovers: rm-probe units and escalation timers whose commands name its own store, no others
    r = subprocess.run(["systemctl", "--user", "list-units", "--all", "--no-legend", "--plain"], capture_output=True,
                       text=True, timeout=30)
    mine = []
    for ln in r.stdout.replace("\u25cf", " ").splitlines():
        w = ln.split()
        if not w or not ("rm-probe" in w[0] or "rm-control-escalate" in w[0]):
            continue
        q = w[0][:-len(".timer")] + ".service" if w[0].endswith(".timer") else w[0]
        props = subprocess.run(["systemctl", "--user", "show", "-p", "ExecStart", "-p", "ExecStopPost", "-p",
                                "ExecCondition", q], capture_output=True, text=True, timeout=10).stdout
        if tmp in props:
            mine.append(w[0])
    return mine


try:
    getattr(S, sys.argv[1])()
except Exception as e:      # noqa: BLE001  a test that raises is red, as in selftest_control.main()
    S.check(False, "%s raised %s: %s" % (sys.argv[1], type(e).__name__, e))
try:
    left = own_units(S.TMP)
    if left:
        subprocess.run(["systemctl", "--user", "stop"] + left, capture_output=True, timeout=60)
        subprocess.run(["systemctl", "--user", "reset-failed"] + left, capture_output=True, timeout=60)
except (OSError, subprocess.SubprocessError):
    pass
shutil.rmtree(S.TMP, ignore_errors=True)
if S.FAILS:
    print("RED %s" % " | ".join(S.FAILS[:3])); sys.exit(1)
if S.UNRUN:
    print("UNRUN %s" % "; ".join(S.UNRUN)); sys.exit(2)
print("GREEN"); sys.exit(0)
"""

BREAKS = {}     # promise -> (the break in one line, [(text in control.py, its replacement)]); an edit of another rimflow
#                 file is (that file's name, text, replacement)


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
    ('        return P.could_not_look("systemctl show failed (rc %d): %s" % (rc, out.strip())), ""',
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
    ('    if _tp.under_test() or os.environ.get("RM_OWNER_HOLD_FILE"):\n        return True',
     '    if False:\n        return True'),
    ('DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".local", "state", "rimmandrake", "control", "control.db")',
     'DEFAULT_DB = os.path.join(os.path.dirname(HERE), "decoy-live-store", "control.db")'))
brk("a-test-process-starts-no-real-unit", "launch_unit() lets a test process reach systemd-run with no runner of its own",
    ('    if runner is None and subprocess.run is _REAL_RUN and spec.get("family") != "probe" and test_process():', '    if False:'))
brk("a-test-process-never-writes-the-real-ledger", "model.append() takes a test process's write to this checkout's ledger "
    "(the test's writer is a recorder, so the break writes nothing)",
    ("model.py", '.startswith(REAL_LEDGER + os.sep):', '.startswith(REAL_LEDGER + os.sep) and False:'))
brk("ended-run-is-recorded-ended", "hook_cmd() does not fall through to the seat clones' control.py",
    ("[os.path.abspath(__file__)] + \\\n        [os.path.join(c, rel) for c in wrapup.seat_clones()]",
     "[os.path.abspath(__file__)]"))
brk("permit-never-ghosts", "switch() leaves the permit alone when the all-switch moves",
    ('        if scope == "all":      # the containment permit follows the all-switch from every caller, not only `pipe`',
     '        if False:'))
brk("before-is-read", "undo() of an OFF ignores its before and always leaves the scope ON",
    ('            prior = json.loads(a["before"] or "null")     # the switch row this off replaced (before-is-read)',
     '            prior = None'))
brk("hold-file-mirrors-the-store", "mod_owner_hold.mirror() learns no file row the store lacks",
    ("mod_owner_hold.py", "    def change(doc):\n        C.import_owner(load_file(p))\n", "    def change(doc):\n"))
brk("his-hold-lifts-by-him-or-the-conductor", "`pipe on` removes the switch rows of every layer, his included",
    ('old = c.execute("SELECT * FROM switches WHERE scope=? AND layer=?", (scope, layer)).fetchone()',
     'old = c.execute("SELECT * FROM switches WHERE scope=? AND (layer=? OR 1)", (scope, layer)).fetchone()'),
    ('c.execute("DELETE FROM switches WHERE scope=? AND layer=?", (scope, layer))',
     'c.execute("DELETE FROM switches WHERE scope=? AND (layer=? OR 1)", (scope, layer))'))
brk("conductor-lift-only-from-its-window", "conductor_window() takes every process for the Conductor window",
    ("mod_owner_hold.py", "    env = os.environ if env is None else env\n", "    return True, \"broken\"\n"))
brk("conductors-lift-is-its-own-act", "the store records the Conductor's reason as his words (owner_said)",
    ('{"per_ruling": CONDUCTOR_LIFT}', '{"owner_said": why.strip()}'))
brk("mirror-failure-is-an-alarm", "a mirror that cannot be written is swallowed: no alarm, exit 0",
    ("mod_owner_hold.py", "        raise MirrorFailed(why)\n", "        return None\n"))
brk("held-stays-held-across-the-mirror", "the mirror drops his design allowance from every row",
    ("mod_owner_hold.py", '        if rows[m].get("design_allowed"):\n            r["design_allowed"]',
     '        if False:\n            r["design_allowed"]'))
brk("reused-name-runs-again", "_admit() never treats a reuse_name run as over",
    ('again = spec.get("reuse_name") and old is not None and old["state"] not in LIVE_STATES', "again = False"))
brk("permit-never-ghosts", "launch_unit() no longer re-writes the permit after an admission",
    ("    permit_sync(p=p)    # admitted means `all` is on", "    pass    # admitted means `all` is on"))
brk("deadline-is-wall-clock", "schedule_escalation() sets a monotonic --on-active timer again",
    ('"--on-calendar=" + due,', '"--on-active=%d" % int(deadline_s),'))
brk("undo-disarms-escalation", "undo() leaves the withdrawn order's timer armed",
    ('    for unit, order in r.pop("timers", ()):', '    for unit, order in ():'))
brk("next-fits-a-screen", "forecast_brief() gives each waiting mod's whole reason its own line",
    ('groups.setdefault((b.get("decision"), _reason_head(b.get("why"))), []).append(str(b.get("mod")))',
     'groups.setdefault((b.get("decision"), b.get("why"), b.get("mod")), []).append(str(b.get("mod")))'))


def run_test(rimflow, test):
    """-> ("GREEN"|"RED"|"UNRUN"|"ERROR", line)."""
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
        files = {}      # name -> its unbroken text
        for n in names:
            for e in BREAKS[n][1]:
                name = e[0] if len(e) == 3 else "control.py"
                if name not in files:
                    with open(os.path.join(rimflow, name), encoding="utf-8") as f:
                        files[name] = f.read()
        blind = []
        for n in names:     # the control: the unbroken copy passes every named test
            word, line = run_test(rimflow, B.test_name(n))
            if word != "GREEN":
                blind.append("%s: unbroken, %s is %s (%s)" % (n, B.test_name(n), word, line))
        for n in names:
            for e in BREAKS[n][1]:
                name, old = (e[0], e[1]) if len(e) == 3 else ("control.py", e[0])
                if files[name].count(old) != 1:
                    blind.append("%s: its break no longer matches %s exactly once" % (n, name))
        if blind:
            print("COULD NOT LOOK control_promise_breaks: %s" % "; ".join(blind))
            return 3
        slipped = []
        for n in names:
            what, edits = BREAKS[n]
            src = dict(files)
            for e in edits:
                name, old, new = e if len(e) == 3 else ("control.py",) + tuple(e)
                src[name] = src[name].replace(old, new)
            for name in files:
                with open(os.path.join(rimflow, name), "w", encoding="utf-8") as f:
                    f.write(src[name])
            try:
                word, line = run_test(rimflow, B.test_name(n))
            finally:
                for name in files:
                    with open(os.path.join(rimflow, name), "w", encoding="utf-8") as f:
                        f.write(files[name])
            for name in files:
                with open(os.path.join(rimflow, name), "rb") as f:
                    if hashlib.sha256(f.read()).hexdigest() != hashlib.sha256(files[name].encode("utf-8")).hexdigest():
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
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
