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
import hashlib
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
    ok('"utf-8", "replace"' in inspect.getsource(B.capture), "6c. the box's capture decodes with errors replaced")
    got = B.capture(["python3", "-c", "import sys; sys.stdout.buffer.write(b'\\xff'); sys.exit(1)"], 60)
    ok(got["exit"] == 1 and "\ufffd" in got["out"], "6d. capture() of a non-UTF-8 byte is a red exit, not a crash: %r" % got)


def t_hardening():
    # RELENTLESS_BOXRUN_HARDEN_PARTIAL_PROOF (REVIEW 2026-11-06)
    for proof in ("python3 a/check_one.py && python3 b/check_two.py > result.txt",
                  "python3 a/selftest_a.py && rimflow show X",
                  "python3 a/selftest_a.py && python3 notascript",
                  "python3 a/selftest_a.py run now please && python3 b/selftest_b.py"):
        cmd, why = B.extract(proof)
        ok(cmd is None and why, "8a. a later && part that cannot run makes %r unrunnable, never a prefix: %r (%s)"
           % (proof, cmd, why))
    # blind check 2026-11-06: prose BEFORE a later part used to cut the whole proof, so only the prefix ran
    for proof in ("python3 a/x.py exits 0 && python3 b/y.py > r.txt",
                  "python3 a/x.py; python3 b/y.py",
                  "python3 a/x.py prints PASS; then python3 b/y.py prints PASS",
                  "python3 a/x.py prints PASS, then bash b/y.sh",
                  "python3 a/x.py prints PASS && b/y.py prints PASS",
                  "python3 a/x.py; b/y.sh",
                  # second review 2026-11-06 (Opus): each returned a prefix
                  "python3 a/x.py\npython3 b/y.py",
                  "python3 a/x.py foo bar python3 b/y.py",
                  "python3 a/x.py x.json and python3 b/y.py",
                  "python3 a/x.py prints PASS and `python3 b/y.py` prints PASS",
                  "python3 a/x.py prints PASS, then python3.11 b/y.py",
                  "python3 a/x.py prints PASS, then /usr/bin/python3 b/y.py",
                  "python3 a/x.py, then ./b.sh",
                  "python3 a/x.py prints PASS, then pytest tests/",
                  "python3 a/x.py prints PASS && ! grep -n x b/y.py",
                  "python3 a/x.py prints PASS; canon_census.py --lint",
                  # third blind check 2026-11-06: a plain command word after prose was read as prose
                  "python3 a.py prints PASS && grep -c foo b.txt prints 3",
                  "python3 a.py prints PASS && make test exits 0",
                  "python3 a.py exits 0 && dotnet build x.csproj",
                  "python3 a.py && python3 b.py prints PASS && npm test",
                  "python3 a.py prints PASS && test -f out.txt",
                  "python3 a.py prints PASS && cargo test",
                  "python3 a.py prints PASS && rimflow show X",
                  "python3 a/selftest_z.py prints RESULT: PASS, including 8a (a later && part extract() cannot run)"):
        cmd, why = B.extract(proof)
        ok(cmd is None and why, "8a. a later command after prose makes %r unrunnable, never a prefix: %r (%s)"
           % (proof, cmd, why))
    for proof, want in (("python3 a/x.py prints PASS && python3 b/y.py prints PASS", "python3 a/x.py && python3 b/y.py"),
                        ("python3 a/x.py exits 0 && ! python3 b/y.py --strict exits 1",
                         "python3 a/x.py && ! python3 b/y.py --strict"),
                        ("python3 pass.py && python3 fail.py", "python3 pass.py && python3 fail.py"),
                        # prose ABOUT a script is not a command (stored proofs, 2026-11-06)
                        ("python3 a/run_selftests.py --only selftest_d.py exits 0; selftest_d.py shows: a harvest",
                         "python3 a/run_selftests.py --only selftest_d.py"),
                        ("python3 a/x.py exits 0 (drives ./bridge with a flag, and handoff.py --wake, as subprocesses)",
                         "python3 a/x.py")):
        cmd, why = B.extract(proof)
        ok(cmd == want, "8a. %r runs every command part, prose && is prose: %r (%s)" % (proof, cmd, why))
    cmd, why = B.extract("python3 a/selftest_a.py && python3 b/selftest_b.py --only x exits 0")
    ok(cmd == "python3 a/selftest_a.py && python3 b/selftest_b.py --only x", "8a. two runnable parts still run whole: %r (%s)"
       % (cmd, why))
    # 8b: a slow box export (make_box) is not counted against the command's timeout
    import relentless_wall as W
    saved = (W.profile, W.make_box, W.through, W.props, W.unit_env, W.remove_box, B.CAPTURE)
    tmp = tempfile.mkdtemp(prefix="boxrun8b-")
    seen = {}
    try:
        W.profile = lambda rules: {"box_root": tmp}
        def slow_box(prof, source, sha, nonce, base=None, item=None):
            time.sleep(2.5)
            os.makedirs(os.path.join(tmp, "b", "tree"), exist_ok=True)
            return os.path.join(tmp, "b")
        W.make_box = slow_box
        W.through = lambda prof, texts: []
        W.props = lambda prof, box, binds, thru: []
        W.unit_env = lambda prof, box: {}
        W.remove_box = lambda box: None
        def cap(argv, timeout_s):
            seen["timeout"] = timeout_s
            time.sleep(1.0)
            return {"exit": 1, "out": "FAIL\n", "out_sha256": "x" * 64, "out_bytes": 5, "secs": 1.0, "timed_out": False}
        B.CAPTURE = cap
        got = B.run_in_box("python3 x.py", "0" * 40, tmp, tmp, {}, 3)
    finally:
        W.profile, W.make_box, W.through, W.props, W.unit_env, W.remove_box, B.CAPTURE = saved
        shutil.rmtree(tmp, ignore_errors=True)
    ok(got.get("exit") == 1 and not got.get("box_error") and got.get("setup_secs", 0) >= 2.5 and got.get("secs") == 1.0,
       "8b. 2.5 s of setup + a 1 s red under a 3 s timeout is a red, setup reported apart: %r" % got)
    # 8c: output is streamed into a bounded tail; the hash covers every byte
    n = 3 * 1024 * 1024
    got = B.capture(["python3", "-c", "import sys\nfor i in range(%d): sys.stdout.write('ab' * 512)\nsys.stdout.write('END')"
                     % (n // 1024)], 120, cap=4096)
    want = hashlib.sha256(b"ab" * 512 * (n // 1024) + b"END").hexdigest()
    ok(got["exit"] == 0 and got["out_bytes"] == n + 3 and len(got["out"]) == 4096 and got["out"].endswith("END")
       and got["out_sha256"] == want, "8c. 3 MiB of output keeps a 4096-byte tail, counts and hashes every byte: %r"
       % {k: got[k] for k in ("exit", "out_bytes", "out_sha256")})
    got = B.capture(["python3", "-c", "import sys, time\nprint('started', flush=True)\ntime.sleep(30)"], 1)
    ok(got["timed_out"] and got["exit"] is None and "started" in got["out"], "8c. capture kills at its timeout, keeps output: %r" % got)
    import inspect
    src = inspect.getsource(B.run_in_box)
    ok("subprocess.run(argv" not in src and "Popen" not in src and "CAPTURE(argv" in src, "8c. run_in_box reads output only through the bounded capture")


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
    # BOXRUN_FIX_SHOW_VERB_CUT_AS_PROSE: right after the script a bare verb is the sub-command; bare `cli.py` could go green
    # for a check that never ran. A described result (`shows`, `exit 0`, `both`) is still prose, anywhere.
    for proof, want in (
            ("python3 a/cli.py show X_Y && python3 b.py (x)", "python3 a/cli.py show X_Y && python3 b.py"),
            ("python3 a/cli.py show X_Y", "python3 a/cli.py show X_Y"),
            ("python3 a/cli.py show", "python3 a/cli.py show"),
            ("python3 a/cli.py show X_Y exits 0", "python3 a/cli.py show X_Y"),
            ("python3 a/cli.py show X_Y shows PASS", "python3 a/cli.py show X_Y"),
            ("python3 a/x.py report --json exits 0", "python3 a/x.py report --json"),
            ("! LABEL=a python3 a/cli.py show X_Y", "! LABEL=a python3 a/cli.py show X_Y"),
            ("python3 -m a.cli show X_Y exits 0", "python3 -m a.cli show X_Y"),
            ("python3 a.py && python3 a/cli.py show X_Y", "python3 a.py && python3 a/cli.py show X_Y"),
            ("python3 a/x.py shows PASS", "python3 a/x.py"),
            ("python3 a/x.py reports PASS", "python3 a/x.py"),
            ("python3 a/x.py exit 0: fine", "python3 a/x.py"),
            ("python3 a/x.py exit code 0", "python3 a/x.py"),
            ("python3 a/x.py both exit 0", "python3 a/x.py"),
            ("python3 a/x.py show: the row", "python3 a/x.py"),
            ("python3 a/x.py --only a show the row", "python3 a/x.py --only a"),
            ("python3 a/cli.py show X_Y | grep -c PASS", None),
            ("python3 a/cli.py show X_Y && grep -c PASS b.txt", None)):
        cmd, why = B.extract(proof)
        ok(cmd == want if want else cmd is None and why, "5b. extract(%r) -> %r (%s)" % (proof, cmd, why))


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
    try:    # the mirror's files stay unreadable; since read_always carves its game inventory out, their names show
        got = REAL_RUN("python3 src/RimMandrake/rimflow/selftest_x.py && ! head -c 1 /mnt/d/Luke/dev/RimMandrake/CLAUDE.md "
                       "2>/dev/null", sha, d, store_root,
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
        for t in (t_red, t_tick_not_blocked, t_refence, t_green_and_gate, t_extract, t_review_fixes, t_hardening, t_verb,
                  t_real_box):
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
