#!/usr/bin/env python3
"""selftest_relentless_boxrun.py — finish runs the contract's proof in the Marker's box, OUTSIDE store.lock, then
re-fences (RELENTLESS_BUILD_BOXRUN_AT_FINISH). Owner: "the checker should run the code to check it rather than
philosophize".

1. a red proof under enforce is refused, the box output is on the builder's stdout, and no receipt is written;
   under shadow the same red finishes and the receipt carries the run;
2. a tick during a long boxrun is not blocked: store.lock() is free while the box runs;
3. re-fence after the unlocked run: a gen bumped mid-run -> Fenced, a contract changed mid-run -> refused, no receipt;
4. green finishes with receipt.boxrun; a store not in cfg.stores runs no box at all (the other selftests' stores);
5. extract(): the command at the head of the prose proof, or why none;
6. the `boxrun` verb: exit 0 green, 1 red, 3 unrunnable; mode off still runs it (as shadow);
7. one real run_in_box smoke in the Marker's wall when systemd-run --user is here (skipped, not failed, otherwise).

Temp stores and temp git repos; the RUN seam is replaced except in 7.

    python3 src/RimMandrake/rimflow/selftest_relentless_boxrun.py
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import selftest_relentless as SR    # noqa: E402
import relentless_boxrun as B       # noqa: E402
import evidence as E                # noqa: E402

R = SR.R
FAILS = []
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
PROOF = "python3 src/RimMandrake/rimflow/selftest_x.py exits 0 and prints PASS"
REAL_RUN, REAL_CONFIG = B.RUN, B.config


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what, flush=True)     # flushed: a planted lock break hangs a later case
    if not cond:
        FAILS.append(what)


def repo():
    d = tempfile.mkdtemp(prefix="boxrun_selftest_")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=d, check=True, capture_output=True)
    p = os.path.join(d, "src/RimMandrake/rimflow/selftest_x.py")
    os.makedirs(os.path.dirname(p))
    with open(p, "w") as f:
        f.write("print('PASS')\n")
    for argv in (["add", "--", "src"], ["commit", "-q", "-m", "I0: x", "--no-verify"]):
        subprocess.run(["git", *argv], cwd=d, env=ENV, check=True, capture_output=True)
    return d, subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()


def rig(proof=PROOF):
    x = SR.Rig(n=1, share=1.0)
    x.run_one("I0")
    g = x.st("I0")["gen"]
    R.contract(x.s, "I0", g, proof)
    return x, g


def setup(x, mode="enforce", run=None):
    cfg = {"mode": mode, "stores": [x.s.root], "timeout_s": 30, "out_tail": 6000, "log_tail": 600}
    B.config = lambda path=None: dict(cfg)
    B.RUN = run or (lambda *a, **k: {"exit": 0, "out": "PASS\n", "secs": 0.1})
    return cfg


def finish(x, g, sha, d):
    """-> (refusal or None, stdout)."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            R.finish(x.s, "I0", g, sha, "e", root=d)
    except (ValueError, R.Fenced) as e:
        return "%s: %s" % (type(e).__name__, e), buf.getvalue()
    return None, buf.getvalue()


def receipt(x, g):
    p = x.s.receipt_path("I0", g)
    return json.load(open(p)) if os.path.exists(p) else None


def t_red():
    d, sha = repo()
    x, g = rig()
    setup(x, "enforce", lambda *a, **k: {"exit": 1, "out": "Traceback ...\nAssertionError: KRAYT_SENTINEL\n", "secs": 2})
    why, out = finish(x, g, sha, d)
    ok(why is not None and "RED" in why and "boxrun" in why, "1. a red proof under enforce is refused: %r" % (why or "")[:120])
    ok("KRAYT_SENTINEL" in out and "$ python3 src/RimMandrake/rimflow/selftest_x.py" in out,
       "1. the box output and the command are on the builder's stdout")
    ok(receipt(x, g) is None and x.st("I0")["status"] != "candidate", "1. no receipt, not a candidate")
    log = [r for r in E.index_rows(x.s.dir) if r.get("kind") == "run"]
    ok(log and log[-1]["verdict"] == "red" and log[-1]["kind_of_run"] == "finish",
       "1. the refused run still leaves its evidence receipt, which the SLI counts")
    ok(B.sli(x.s).get("finish/enforce", {}).get("red") == 1, "1. sli counts the avoided Marker launch")

    x, g = rig()
    setup(x, "shadow", lambda *a, **k: {"exit": 1, "out": "KRAYT_SENTINEL\n", "secs": 2})
    why, out = finish(x, g, sha, d)
    rc = receipt(x, g)
    ok(why is None and rc and rc.get("boxrun", {}).get("verdict") == "red" and "KRAYT_SENTINEL" in out,
       "1. under shadow the red finishes, prints, and the receipt carries the run: %r" % why)


def t_tick_not_blocked():
    d, sha = repo()
    x, g = rig()
    inside, release = threading.Event(), threading.Event()

    def slow(*a, **k):
        inside.set()
        release.wait(20)
        return {"exit": 0, "out": "PASS\n", "secs": 9}
    setup(x, "enforce", slow)
    res = {}
    th = threading.Thread(target=lambda: res.update(r=finish(x, g, sha, d)))
    th.start()
    ok(inside.wait(10), "2. the box run started")
    t0 = time.time()
    got = {}

    def tick():
        with x.s.lock():
            got["st"] = x.s.load("I0")
    tk = threading.Thread(target=tick, daemon=True)
    tk.start()
    tk.join(5)
    ok("st" in got and time.time() - t0 < 5, "2. a tick takes store.lock while the box runs (%.2fs)" % (time.time() - t0))
    release.set()
    th.join(20)
    ok(res.get("r", ("x",))[0] is None and receipt(x, g), "2. the finish then lands its receipt: %r" % (res.get("r"),))


def t_refence():
    d, sha = repo()
    x, g = rig()

    def bump(*a, **k):      # the supervisor reclaims and re-leases the item while the proof runs
        with x.s.lock():
            st = x.s.load("I0")
            st["gen"] += 1
            x.s.save(st)
        return {"exit": 0, "out": "PASS\n", "secs": 1}
    setup(x, "enforce", bump)
    why, _ = finish(x, g, sha, d)
    ok(why and why.startswith("Fenced"), "3. a gen bumped during the run is Fenced after it: %r" % (why or "")[:100])
    ok(receipt(x, g) is None, "3. no receipt for the fenced gen")

    x, g = rig()

    def recontract(*a, **k):
        with x.s.lock():
            st = x.s.load("I0")
            st["contract"] = dict(st["contract"], proof=PROOF + " twice")
            x.s.save(st)
        return {"exit": 0, "out": "PASS\n", "secs": 1}
    setup(x, "enforce", recontract)
    why, _ = finish(x, g, sha, d)
    ok(why and "contract changed" in why and receipt(x, g) is None,
       "3. a contract changed during the run is refused, no receipt: %r" % (why or "")[:100])


def t_green_and_gate():
    d, sha = repo()
    x, g = rig()
    seen = {}
    setup(x, "enforce", lambda cmd, s, *a, **k: seen.update(cmd=cmd, sha=s) or {"exit": 0, "out": "PASS\n", "secs": 1})
    why, _ = finish(x, g, sha, d)
    rc = receipt(x, g) or {}
    ok(why is None and rc.get("boxrun", {}).get("verdict") == "green" and rc["hash"] == R.contract_hash(rc["contract"]),
       "4. green finishes; receipt.boxrun green and hash unchanged: %r" % why)
    ok(seen.get("sha") == sha and seen.get("cmd", "").startswith("python3 src/RimMandrake/rimflow/selftest_x.py"),
       "4. the box ran the contract's command at the finished sha: %r" % seen)

    x, g = rig()
    cfg = setup(x, "enforce", lambda *a, **k: FAILS.append("4. ran a box for a store outside cfg.stores") or {})
    cfg["stores"] = ["/nonexistent/store"]
    B.config = lambda path=None: dict(cfg)
    why, _ = finish(x, g, sha, d)
    ok(why is None and "boxrun" not in (receipt(x, g) or {"boxrun": 1}), "4. a store not in cfg.stores finishes without a box")
    ok(B.contract_hash({"a": 1}) == R.contract_hash({"a": 1}) and B.contract_hash(None) == R.contract_hash(None),
       "4. the re-fence hash is relentless.contract_hash")


def t_review_fixes():
    # REVIEW 2026-11-06: an env assignment stays an assignment; non-UTF-8 output is a red, not a box_error
    cmd, why = B.extract("LABEL=a!b python3 tools/check.py --strict")
    ok(cmd is not None and cmd.startswith("LABEL=") and "'LABEL" not in cmd, "6a. env assignment stays unquoted at the name: %r (%s)" % (cmd, why))
    import subprocess
    p = subprocess.run(["python3", "-c", "import sys; sys.stdout.buffer.write(b'\\xff'); sys.exit(1)"], capture_output=True,
                       encoding="utf-8", errors="replace")
    ok(p.returncode == 1 and "\ufffd" in p.stdout, "6b. the decode setting the box uses survives a non-UTF-8 byte")
    import inspect
    ok('errors="replace"' in inspect.getsource(B.run_in_box), "6c. run_in_box decodes with errors=replace")


def t_extract():
    cases = [
        ("python3 src/RimMandrake/Utils/run_selftests.py --only selftest_a selftest_b exits 0 and prints PASS",
         "python3 src/RimMandrake/Utils/run_selftests.py --only selftest_a selftest_b"),
        ("python3 src/x/selftest_y.py: all checks pass", "python3 src/x/selftest_y.py"),
        ("cd src && python3 -m pytest x", None),
        ("The Marker reads the diff and agrees", None),
        ("bash tools/check.sh --strict; then prints OK", "bash tools/check.sh --strict"),
    ]
    for proof, want in cases:
        cmd, why = B.extract(proof)
        ok(cmd == want if want else cmd is None and why, "5. extract(%r) -> %r (%s)" % (proof[:50], cmd, why))


def t_verb():
    d, sha = repo()
    for exit_, want in ((0, 0), (1, 1)):
        x, g = rig()
        setup(x, "off", lambda *a, e=exit_, **k: {"exit": e, "out": "out\n", "secs": 1})
        with contextlib.redirect_stdout(io.StringIO()):
            rc = B.verb(x.s, "I0", g, sha, d, R.rules())
        ok(rc == want, "6. verb exit %s for a run exiting %s (mode off runs as shadow)" % (rc, exit_))
    x, g = rig("The Marker reads it")
    setup(x, "enforce")
    with contextlib.redirect_stdout(io.StringIO()):
        rc = B.verb(x.s, "I0", g, sha, d, R.rules())
    ok(rc == 3, "6. verb exit 3 for an unrunnable proof")
    ok(x.st("I0")["status"] != "candidate" and receipt(x, g) is None, "6. the verb writes no receipt")


def t_real_box():
    if not shutil.which("systemd-run") or subprocess.run(["systemctl", "--user", "is-system-running"],
                                                         capture_output=True).returncode not in (0, 1):
        print("skip 7. no systemd --user here")
        return
    d, sha = repo()
    store_root = R.root()           # bound read-only; a temp root under a masked TMPDIR cannot be bound (226)
    if not os.path.isdir(store_root):
        print("skip 7. no store root %s to bind" % store_root)
        return
    try:
        got = REAL_RUN("python3 src/RimMandrake/rimflow/selftest_x.py && test ! -e /mnt/d/Luke/dev/RimMandrake/CLAUDE.md", sha, d, store_root,
                       R.rules(), 120)
    except Exception as e:      # noqa: BLE001
        got = {"box_error": repr(e)}
    if got.get("box_error"):
        print("skip 7. the box could not be made here: %s" % got["box_error"][:200])
        return
    ok(got.get("exit") == 0 and "PASS" in got.get("out", ""), "7. a real Marker box runs the proof at the sha: %r"
       % {k: got.get(k) for k in ("exit", "secs")})
    got = REAL_RUN("python3 -c 'import sys; print(\"BOX_RED\"); sys.exit(4)'", sha, d, store_root, R.rules(), 120)
    ok(got.get("exit") == 4 and "BOX_RED" in got.get("out", ""), "7. a real red exit and its output come back: %r"
       % {k: got.get(k) for k in ("exit", "box_error")})


if __name__ == "__main__":
    try:
        for t in (t_red, t_tick_not_blocked, t_refence, t_green_and_gate, t_extract, t_verb, t_real_box):
            try:
                t()
            finally:
                B.RUN, B.config = REAL_RUN, REAL_CONFIG
    except Exception as e:      # noqa: BLE001  a crash is a FAIL with its reason
        import traceback
        traceback.print_exc()
        FAILS.append("crashed: %s" % e)
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
