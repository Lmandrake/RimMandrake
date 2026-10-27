#!/usr/bin/env python3
"""selftest_close_evidence.py -- the close-evidence recorder and lookup (CLOSE_EVIDENCE_BUILD_GATES_CAN_DECIDE).

Offline, fixture git repos under a temp dir; RM_CLOSE_EVIDENCE_DIR points every write at the temp dir, so the real
evidence store is never touched. Checks: a clean run is found by sha (prefix) and item; a dirty-tree run is recorded
but never returned as evidence; session transcripts do not make a tree dirty; a write error never raises; a tool run
inside a selftest writes nothing unless redirected; summarize lets FAIL win; validate_patch, run_selftests and
modcheck each write their line (or, for a redirected modcheck registry, do not).
Review Z (v2), one check group per finding: F1 24 concurrent writers on D: keep every line, an unreadable line reads
UNMEASURED; F2 start/end drift and v1 lines are not evidence; F3 modcheck is live-only; F4 python.exe records via WSL;
F5 lookup(paths=) and DROPPED -> UNMEASURED; F6 validate_patch unread target -> UNMEASURED, static variant; F7 winbuild
stage snapshots and rsync failure; F8 --no-optional-locks; F9 per-clone selftest lines; F10 AGENT_SEAT; WHO seat/session/agent per line.
Review AA (v3): only sealed v3 lines with an in-process origin are evidence (no-v, v2, edited, typed-in start/end and
record-CLI lines are not); a missing key raises; 24 writers on D: with a looping reader keep all 960 lines.
"""
import io
import json
import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import close_evidence as CE  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


def make_repo(root):
    repo = Path(root) / "clone"
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("x = 1\n")
    git(repo, "add", "src/a.py")
    git(repo, "commit", "-q", "-m", "one")
    return repo, git(repo, "rev-parse", "HEAD")


def main():
    with tempfile.TemporaryDirectory() as td:
        store = Path(td) / "evidence"
        os.environ[CE.ENV_DIR] = str(store)
        os.environ[CE.KEY_ENV] = str(Path(td) / "close_evidence.key")     # never the user's real key
        os.environ.pop("RIMFLOW_ITEM", None)
        repo, sha = make_repo(td)

        # clean tree: found by full sha, by 12-char prefix, by item; a 6-char prefix is too short to match
        r1 = CE.record("selftest", "PASS", [repo / "src" / "a.py"], clone=repo, item="ITEM_ONE", start=CE.snapshot(repo))
        check(r1 is not None and r1["sha"] == sha and r1["dirty"] is False, "clean record carries HEAD, dirty False")
        check(r1["paths"] == ["src/a.py"], "paths are clone-relative: %r" % (r1 and r1["paths"],))
        check(len(CE.lookup(sha=sha)) == 1, "lookup by sha finds the clean run")
        check(len(CE.lookup(sha=sha[:12])) == 1, "lookup by 12-char prefix finds it")
        check(CE.lookup(sha=sha[:6]) == [], "a 6-char prefix matches nothing")
        check(len(CE.lookup(item="ITEM_ONE")) == 1 and CE.lookup(item="OTHER") == [], "lookup by item")
        check(len(CE.lookup(sha=sha, item="ITEM_ONE")) == 1 and CE.lookup(sha=sha, item="OTHER") == [],
              "sha and item together must both match")

        # transcripts are not dirt
        (repo / "conversations").mkdir()
        (repo / "conversations" / "t.md").write_text("chat\n")
        r2 = CE.record("selftest", "PASS", [repo / "src"], clone=repo)
        check(r2["dirty"] is False, "an untracked conversations/ file leaves the tree clean")

        # dirty tree: recorded, never evidence
        (repo / "src" / "a.py").write_text("x = 2\n")
        r3 = CE.record("validate_patch", "PASS", [repo / "src" / "a.py"], clone=repo)
        check(r3["dirty"] is True and r3["dirty_paths"] == ["src/a.py"], "a modified tracked file marks it dirty")
        check(all(r["tool"] == "selftest" for r in CE.lookup(sha=sha)), "lookup excludes the dirty-tree run")
        check(any(r["tool"] == "validate_patch" for r in CE.lookup(sha=sha, include_dirty=True)),
              "include_dirty (audit) still sees it")
        git(repo, "checkout", "-q", "--", "src/a.py")
        (repo / "src" / "new.py").write_text("y = 1\n")
        r4 = CE.record("winbuild", "PASS", [repo / "src"], clone=repo)
        check(r4["dirty"] is True, "an untracked source file marks it dirty")
        (repo / "src" / "new.py").unlink()

        # no clone: sha None, never evidence
        loose = Path(td) / "loose.xml"
        loose.write_text("<Patch/>")
        r5 = CE.record("validate_patch", "PASS", [loose])
        check(r5["sha"] is None and not CE.counts_as_evidence(r5), "a file in no clone is never evidence")

        # result vocabulary is closed, and a bad value is a loud no-op, not an exception
        err = io.StringIO()
        with redirect_stderr(err):
            r6 = CE.record("selftest", "GREEN", [repo], clone=repo)
        check(r6 is None and "CLOSE-EVIDENCE WRITE FAILED" in err.getvalue(), "a non-vocabulary result is refused loudly")

        # write error never raises
        blocker = Path(td) / "blocker"
        blocker.write_text("not a dir")
        os.environ[CE.ENV_DIR] = str(blocker / "sub")
        err = io.StringIO()
        with redirect_stderr(err):
            r7 = CE.record("selftest", "PASS", [repo], clone=repo)
        check(r7 is None and "CLOSE-EVIDENCE WRITE FAILED" in err.getvalue(), "an unwritable store prints, never raises")
        os.environ[CE.ENV_DIR] = str(store)

        # nested under the selftest runner without a redirect: nothing written (fixtures are not evidence)
        os.environ.pop(CE.ENV_DIR)
        old = os.environ.get("RM_SELFTEST_NESTED")
        os.environ["RM_SELFTEST_NESTED"] = "1"
        check(CE.record("selftest", "PASS", [repo], clone=repo) is None, "nested tool run writes nothing")
        if old is None:
            os.environ.pop("RM_SELFTEST_NESTED")
        os.environ[CE.ENV_DIR] = str(store)

        # summarize: latest per path set, FAIL beats UNMEASURED beats PASS
        recs = [{"tool": "selftest", "paths": ["a"], "result": "FAIL", "ts": "1"},
                {"tool": "selftest", "paths": ["a"], "result": "PASS", "ts": "2"},
                {"tool": "selftest", "paths": ["b"], "result": "UNMEASURED", "ts": "3"},
                {"tool": "winbuild", "paths": ["c"], "result": "PASS", "ts": "1"},
                {"tool": "winbuild", "paths": ["d"], "result": "FAIL", "ts": "1"}]
        check(CE.summarize(recs) == {"selftest": "UNMEASURED", "winbuild": "FAIL"}, "summarize: %r" % CE.summarize(recs))

        # every line on disk is one JSON object with the fixed fields
        lines = [json.loads(ln) for f in store.glob("*.jsonl") for ln in f.read_text().splitlines()]
        want = {"v", "ts", "tool", "clone", "sha", "dirty", "dirty_n", "dirty_paths", "start", "paths", "covers",
                "result", "item", "seat", "who", "origin", "live_only", "variant", "detail", "mac"}
        check(lines and all(set(l) == want for l in lines), "%d lines, each with exactly the schema fields" % len(lines))

        # validate_patch end to end: a run on a file in the fixture clone writes one validate_patch line
        (repo / "Patches").mkdir()
        (repo / "Patches" / "p.xml").write_text('<?xml version="1.0"?><Patch><Operation Class="PatchOperationAdd">'
                                                 '<xpath>Defs/ThingDef[defName="X"]</xpath><value><a/></value>'
                                                 '</Operation></Patch>')
        git(repo, "add", "Patches/p.xml")
        git(repo, "commit", "-q", "-m", "patch")
        sha2 = git(repo, "rev-parse", "HEAD")
        vp = REPO / "skills" / "rimworld-modding" / "scripts" / "validate_patch.py"
        env = dict(os.environ)
        env.pop("RM_SELFTEST_NESTED", None)
        p = subprocess.run([sys.executable, str(vp), "--quiet", "--mods-config", str(Path(td) / "none.xml"),
                            str(repo / "Patches" / "p.xml")], capture_output=True, text=True, env=env, timeout=120)
        vrec = CE.lookup(sha=sha2, tool="validate_patch")
        expect = {0: "PASS", 1: "FAIL"}.get(p.returncode, "UNMEASURED")
        check(len(vrec) == 1 and vrec[0]["result"] == expect and vrec[0]["paths"] == ["Patches/p.xml"],
              "validate_patch (exit %d) wrote one %s line for HEAD: %r" % (p.returncode, expect,
                                                                          [(r["result"], r["paths"]) for r in vrec]))

        # run_selftests: the outer run records the verdict-reaching tests, not the SKIPPED ones
        import run_selftests as RS
        RS._OUTER[0] = True
        os.environ.pop("RM_SELFTEST_REPO_ROOT", None)
        ran = [(REPO / "src/RimMandrake/Utils/selftest_close_evidence.py", "PASS", 1.0, ""),
               (REPO / "src/RimMandrake/Utils/close_evidence.py", "SKIPPED", 0.0, "unchanged")]
        before = len(CE.read_all(folder=store))
        RS._evidence_start([r[0] for r in ran])
        RS._record_evidence(ran)
        RS._record_evidence([ran[0], (ran[1][0], "FAIL", 1.0, "boom")])
        check(all(r["start"] and r["start"]["sha"] for r in CE.read_all(folder=store)[before:]),
              "F2 the runner stores the start snapshot it took before running")
        RS._OUTER[0] = None
        RS._record_evidence(ran)                     # not an outer run: nothing
        new = CE.read_all(folder=store)[before:]
        check([(r["tool"], r["result"], len(r["paths"])) for r in new] == [("selftest", "PASS", 1), ("selftest", "FAIL", 2)],
              "run_selftests records one line per outer run: %r" % [(r["tool"], r["result"]) for r in new])

        # modcheck: a registry redirected by a test writes no evidence
        sys.path.insert(0, str(HERE / "modcheck"))
        import status as ST
        real = ST.LOG_PATH
        ST.LOG_PATH = str(Path(td) / "status.json")
        before = len(CE.read_all(folder=store))
        ST._record_evidence("Demo", str(repo), {"status": "RED"}, False, "")
        check(len(CE.read_all(folder=store)) == before, "modcheck with a redirected registry records nothing")
        ST.LOG_PATH = real
        ST._record_evidence("Demo", str(repo / "src"), {"status": "GREEN", "run_id": "r", "hash": "h"}, True, "")
        last = CE.read_all(folder=store)[-1]
        check(last["tool"] == "modcheck" and last["result"] == "PASS" and last["detail"]["status"] == "GREEN",
              "modcheck records the machine verdict beside the registry status")
        # F3: the running game holds what it loaded at launch -> live-only, never sha evidence
        check(last["live_only"] is True and not CE.counts_as_evidence(last), "F3 modcheck line is live-only, not evidence")
        check(not CE.lookup(sha=last["sha"], tool="modcheck", include_dirty=True)
              and CE.lookup(sha=last["sha"], tool="modcheck", include_live=True),
              "F3 lookup hides modcheck unless include_live")

        review_z(td, store, repo, sha2)
        review_aa(Path(td) / "aa")

    print("RESULT: %s (%d failure(s))" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


# ------------------------------------------------------------------ review AA

def _reader(args):
    """Reads the store in a loop while writers append (review AA1: an unlocked reader cost writers lines on drvfs)."""
    store, stop_file = args
    n = 0
    while not os.path.exists(stop_file):
        CE.read_all(days=2, folder=store, bad_out=[])
        n += 1
    return n


def review_aa(root):
    """Review AA: v3 lines only (schema + origin + mac), the record CLI is never evidence, a missing key is an error,
    readers hold a shared lock. THE LIMIT: these stop accidental and lazy forgery, not a same-user forger."""
    root.mkdir()
    repo, sha = make_repo(root)
    store = root / "store"
    os.environ[CE.ENV_DIR] = str(store)
    good = CE.record("selftest", "PASS", [repo / "src" / "a.py"], clone=repo, start=CE.snapshot(repo))
    check(good and good["v"] == CE.V and not CE.schema_problems(good) and good["origin"]["via"] == "inproc"
          and good["origin"]["start"] == "snapshot" and good["origin"]["end"] == "git" and good["mac"],
          "AA a real run is a v3 line, origin inproc/snapshot/git, sealed: %r" % (good and good.get("origin"),))
    check(len(CE.lookup(sha=sha, tool="selftest")) == 1, "AA the real run is evidence")
    day = next(store.glob("*.jsonl"))

    def append(rec):
        with day.open("a") as f:
            f.write(json.dumps(rec, sort_keys=True, default=str) + "\n")

    # NOV: a hand-written line with no v, a v2 line, an edited sealed line
    append({"tool": "novtool", "sha": sha, "dirty": False, "result": "PASS", "paths": ["src/a.py"], "ts": good["ts"]})
    check(CE.lookup(sha=sha, tool="novtool") == [], "AA-NOV a line with no v is not evidence")
    v2 = {k: v for k, v in good.items() if k not in ("origin", "mac")}
    append(dict(v2, v=2, tool="v2tool"))
    check(CE.lookup(sha=sha, tool="v2tool") == [], "AA-NOV a v2 line is not evidence")
    bad = CE.record("edittool", "FAIL", [repo / "src" / "a.py"], clone=repo, start=CE.snapshot(repo))
    append(dict(bad, result="PASS", ts=bad["ts"][:-6] + "9" + bad["ts"][-6:]))
    check([r["result"] for r in CE.lookup(sha=sha, tool="edittool")] == ["FAIL"],
          "AA-NOV a sealed line edited FAIL->PASS fails its mac; the FAIL stands")
    check(not CE.mac_ok(dict(good, seat="RUNNER"), CE._key()), "AA a changed seat breaks the mac")
    # FORGE: typed-in start/end in process; a record CLI payload asserting sha, clean tree and seat
    st = {"sha": sha, "dirty": False, "dirty_n": 0}
    f1 = CE.record("typedtool", "PASS", [repo / "src" / "a.py"], clone=repo, start=st, end=st)
    check(f1["origin"]["start"] == "caller" and f1["origin"]["end"] == "caller" and not CE.counts_as_evidence(f1)
          and CE.lookup(sha=sha, tool="typedtool") == [], "AA-FORGE a typed-in start/end is not evidence")
    tok = CE.snapshot(repo)
    f2 = CE.record("tamptool", "PASS", [repo / "src" / "a.py"], clone=repo, start=dict(tok, dirty_n=0, sha="0" * 40))
    check(f2["origin"]["start"] == "caller", "AA-FORGE a minted snapshot edited after minting is the caller's word")
    pay = {"tool": "clitool", "result": "PASS", "paths": [str(repo / "src" / "a.py")], "clone": str(repo),
           "start": st, "end": st, "who": {"seat": "RUNNER", "seat_from": "RIMFLOW_SEAT"}, "evidence_dir": str(store)}
    cp = subprocess.run([sys.executable, str(HERE / "close_evidence.py"), "record"], input=json.dumps(pay),
                        capture_output=True, text=True, timeout=120)
    cli = json.loads(cp.stdout.strip().splitlines()[-1]) if cp.returncode == 0 and cp.stdout.strip() else {}
    check(cli.get("origin", {}).get("via") == "cli" and cli.get("who", {}).get("seat_from") == "shipped:RIMFLOW_SEAT"
          and CE.lookup(sha=sha, tool="clitool") == [],
          "AA-FORGE the record CLI writes a via=cli line that is never evidence: rc=%s %s" % (cp.returncode,
                                                                                              cp.stderr[-200:]))
    # a missing key: lookup raises (UNMEASURED), the writer creates it
    kp = os.environ[CE.KEY_ENV]
    os.environ[CE.KEY_ENV] = str(root / "nokey" / "k")
    try:
        CE.lookup(sha=sha)
        check(False, "AA lookup with no key raises")
    except RuntimeError:
        check(True, "AA lookup with no key raises")
    os.environ[CE.KEY_ENV] = kp
    check(len(CE.lookup(sha=sha, tool="selftest")) == 1, "AA sanity: with the key back the real run is found again")
    # AA1: 24 writers x 40 lines x 2 KB on D: WITH a reader looping on read_all -- every line survives
    dbase = Path("/mnt/d/ClaudeWork/rimmandrake/selftest_tmp")
    if Path("/mnt/d/ClaudeWork").is_dir():
        dbase.mkdir(parents=True, exist_ok=True)
        dst = tempfile.mkdtemp(prefix="ce_aa1_", dir=str(dbase))
        stop = os.path.join(dst, "stop.flag")
        try:
            ctx = multiprocessing.get_context("fork")
            with ctx.Pool(1) as rp, ctx.Pool(24) as pool:
                reads = rp.map_async(_reader, [(dst, stop)])
                pool.map(_writer, [(dst, k, 40) for k in range(24)])
                Path(stop).write_text("x")
                nreads = reads.get(timeout=120)[0]
            got = set()
            for ln in (ln for f in Path(dst).glob("*.jsonl") for ln in f.read_text().splitlines()):
                try:
                    d = json.loads(ln)["detail"]
                    got.add((d["w"], d["j"]))
                except (ValueError, KeyError):
                    pass
            check(len(got) == 960 and nreads > 0, "AA1 24 writers + a looping reader on D: kept %d/960 lines "
                                                   "(reader made %d reads)" % (len(got), nreads))
        finally:
            shutil.rmtree(dst, ignore_errors=True)
    else:
        print("AA1 drvfs reader probe: no /mnt/d here -- UNMEASURED, not a pass or a fail")


# ------------------------------------------------------------------ review Z

def _writer(args):
    store, k, n = args
    os.environ[CE.ENV_DIR] = store
    pad = "x" * 2000
    for j in range(n):
        CE.record("selftest", "PASS", [], detail={"w": k, "j": j, "pad": pad})


def review_z(td, store, repo, sha):
    # F1: 24 writers x 40 lines x 2 KB on D: (drvfs, where O_APPEND alone kept 41 of 960) -- every line survives
    dbase = Path("/mnt/d/ClaudeWork/rimmandrake/selftest_tmp")
    if Path("/mnt/d/ClaudeWork").is_dir():
        dbase.mkdir(parents=True, exist_ok=True)
        dst = tempfile.mkdtemp(prefix="ce_f1_", dir=str(dbase))
        try:
            with multiprocessing.get_context("fork").Pool(24) as pool:
                pool.map(_writer, [(dst, k, 40) for k in range(24)])
            lines = [ln for f in Path(dst).glob("*.jsonl") for ln in f.read_text().splitlines()]
            good = set()
            for ln in lines:
                try:
                    d = json.loads(ln)["detail"]
                    good.add((d["w"], d["j"]))
                except (ValueError, KeyError):
                    pass
            check(len(lines) == 960 and len(good) == 960,
                  "F1 24 concurrent writers on D: kept %d/960 lines, %d distinct intact" % (len(lines), len(good)))
        finally:
            shutil.rmtree(dst, ignore_errors=True)
    else:
        print("F1 drvfs probe: no /mnt/d here -- UNMEASURED, not a pass or a fail")
    # F1: an unreadable line that may hold this sha is UNMEASURED, never silently absent
    fx = Path(td) / "f1store"
    fx.mkdir()
    os.environ[CE.ENV_DIR] = str(fx)
    st = CE.snapshot(repo)
    CE.record("selftest", "PASS", [repo / "src"], clone=repo, start=st)
    day = next(fx.glob("*.jsonl"))
    with day.open("a") as f:
        f.write('{"result": "FAIL", "sha": "%s", "tool": "self\n' % sha)
    hits = CE.lookup(sha=sha)
    check(CE.summarize(hits).get("close_evidence") == "UNMEASURED" and len(hits) == 2,
          "F1 a torn line naming this sha adds an UNMEASURED marker: %r" % CE.summarize(hits))
    with day.open("a") as f:
        f.write('{"sha": "%s", "torn\n' % ("f" * 40))
    check(len(CE.lookup(sha=sha)) == 2, "F1 a torn line naming only another sha is not ours")
    os.environ[CE.ENV_DIR] = str(store)

    # F2: a commit landing mid-run, a dirty start, and a v1 line are not evidence
    st = CE.snapshot(repo)
    (repo / "src" / "a.py").write_text("x = 3\n")
    git(repo, "commit", "-q", "-am", "mid-run")
    sha3 = git(repo, "rev-parse", "HEAD")
    r = CE.record("selftest", "PASS", [repo / "src" / "a.py"], clone=repo, start=st)
    check(r["start"]["sha"] == sha and r["sha"] == sha3 and not CE.counts_as_evidence(r),
          "F2 start sha != end sha -> not evidence")
    check(not CE.lookup(sha=sha3, tool="selftest") and not any(x["ts"] == r["ts"] and x["sha"] == sha3
                                                               for x in CE.lookup(sha=sha)),
          "F2 neither the start nor the end sha gets the mid-run PASS")
    r = CE.record("selftest", "PASS", [repo / "src"], clone=repo)
    check(r["start"] is None and not CE.counts_as_evidence(r), "F2 a record without a start snapshot is not evidence")
    check(not CE.counts_as_evidence(dict(r, v=1, start={"sha": sha3, "dirty": False})), "F2 a v1 line is not evidence")
    good = CE.record("selftest", "PASS", [repo / "src"], clone=repo, start=CE.snapshot(repo))
    check(CE.counts_as_evidence(good), "F2 same sha clean at start and end is evidence")
    (repo / "junk.txt").write_text("j")
    dst = CE.snapshot(repo)
    (repo / "junk.txt").unlink()
    check(not CE.counts_as_evidence(CE.record("selftest", "PASS", [repo / "src"], clone=repo, start=dst)),
          "F2 dirty at start, clean at end -> not evidence")

    # F4: under Windows python.exe the line is shipped to WSL and carries the clone's sha
    pyexe, distro = shutil.which("python.exe"), os.environ.get("WSL_DISTRO_NAME")
    if pyexe and shutil.which("wsl.exe") and distro:
        def w(p):
            return "\\\\wsl.localhost\\%s%s" % (distro, str(p).replace("/", "\\"))
        wstore = Path(td) / "winstore"
        script = Path(td) / "win_probe.py"
        script.write_text("import os, sys\nsys.path.insert(0, sys.argv[1])\nimport close_evidence as CE\n"
                          "os.environ[CE.ENV_DIR] = sys.argv[2]\n"
                          "r = CE.record('modcheck', 'PASS', [sys.argv[3]], clone=sys.argv[3], live_only=True)\n"
                          "print('OSNAME', os.name, 'SHA', r and r.get('sha'))\n")
        p = subprocess.run([pyexe, w(script), w(HERE), w(wstore), w(repo)], capture_output=True, text=True, timeout=180)
        recs = CE.read_all(folder=wstore)
        check("OSNAME nt" in p.stdout and len(recs) == 1 and recs[0]["sha"] == sha3 and recs[0]["live_only"],
              "F4 python.exe recorder wrote via WSL: %s %r" % (p.stdout.strip()[-120:] or p.stderr.strip()[-200:],
                                                               [(x["tool"], x["sha"]) for x in recs]))
    else:
        print("F4 python.exe probe: no python.exe/wsl.exe here -- UNMEASURED, not a pass or a fail")

    # F5: a partial run counts only for the paths it covered; a DROPPED suite is UNMEASURED
    (repo / "src" / "selftest_a.py").write_text("print('ok')\n")
    (repo / "src" / "b.py").write_text("z = 1\n")
    git(repo, "add", "src")
    git(repo, "commit", "-q", "-m", "tests")
    sha4 = git(repo, "rev-parse", "HEAD")
    CE.record("selftest", "PASS", [repo / "src" / "selftest_a.py"], clone=repo, start=CE.snapshot(repo))
    check(len(CE.lookup(sha=sha4, paths=["src/a.py"])) == 1, "F5 selftest_a.py covers src/a.py")
    check(CE.lookup(sha=sha4, paths=["src/b.py"]) == [], "F5 it does not cover src/b.py")
    check(CE.uncovered(CE.lookup(sha=sha4), ["src/a.py", "src/b.py"]) == ["src/b.py"], "F5 uncovered names src/b.py")
    check(len(CE.lookup(sha=sha4, paths=[str(repo / "src" / "a.py")])) == 1, "F5 an absolute path is matched too")
    import run_selftests as RS
    RS._OUTER[0] = True
    t = repo / "src" / "selftest_a.py"
    RS._evidence_start([t])
    before = len(CE.read_all(folder=store))
    RS._record_evidence([(t, "PASS", 1.0, "")], discovered=3)
    new = CE.read_all(folder=store)[before:]
    check([x["result"] for x in new] == ["UNMEASURED"] and new[0]["detail"]["dropped"]["discovered"] == 3,
          "F5 DROPPED (1 of 3 came back) records UNMEASURED: %r" % [x["result"] for x in new])
    # F9: that line is keyed to the fixture clone, not this repo
    check(new and new[0]["clone"] == os.path.realpath(repo) and new[0]["sha"] == sha4 and new[0]["start"]["sha"] == sha4,
          "F9 a selftest in another clone is recorded under that clone's sha")
    RS._OUTER[0] = None

    # F6: an unreadable target makes the run UNMEASURED; paths are only the files validated; no --defs = static
    vp = REPO / "skills" / "rimworld-modding" / "scripts" / "validate_patch.py"
    env = dict(os.environ)
    env.pop("RM_SELFTEST_NESTED", None)
    (repo / "Patches" / "q.xml").write_text('<?xml version="1.0"?><Patch/>')
    git(repo, "add", "Patches/q.xml")
    git(repo, "commit", "-q", "-m", "q")
    sha5 = git(repo, "rev-parse", "HEAD")
    p = subprocess.run([sys.executable, str(vp), "--quiet", "--mods-config", str(Path(td) / "none.xml"),
                        str(repo / "Patches" / "q.xml"), str(repo / "Patches" / "typo.xml")],
                       capture_output=True, text=True, env=env, timeout=120)
    v = CE.lookup(sha=sha5, tool="validate_patch")
    check(len(v) == 1 and v[0]["result"] == "UNMEASURED" and v[0]["paths"] == ["Patches/q.xml"]
          and v[0]["variant"] == "static" and v[0]["detail"]["unreadable"],
          "F6 exit %d with a typo target -> UNMEASURED over the read file only: %r"
          % (p.returncode, [(x["result"], x["paths"], x["variant"]) for x in v]))
    check(list(CE.summarize(v)) == ["validate_patch:static"], "F6 a static run is summarized apart")

    # F7: winbuild keys a staged build by its stage snapshots (copy-back DLLs do not dirty it); rsync failure UNMEASURED
    import winbuild as W
    old_root = W.ROOT
    W.ROOT = os.path.realpath(repo)
    try:
        s0 = W._ce_snapshot(["src/"])
        s1 = W._ce_snapshot(["src/"])
        (repo / "src" / "Assemblies").mkdir()
        (repo / "src" / "Assemblies" / "x.dll").write_bytes(b"MZ")          # the copy-back
        before = len(CE.read_all(folder=store))
        W.evidence_report(str(repo / "src" / "a.csproj"), 0, "Release",
                          {"staged": True, "ev_start": s0, "ev_end": s1, "ev_scope": ["src/"]})
        W.evidence_report(str(repo / "src" / "a.csproj"), 23, "Release", {"staged": False})
        new = CE.read_all(folder=store)[before:]
        check([x["result"] for x in new] == ["PASS", "UNMEASURED"] and CE.counts_as_evidence(new[0])
              and new[0]["sha"] == sha5, "F7 staged build is evidence despite copy-back; rsync failure UNMEASURED: %r"
              % [(x["result"], x["dirty"]) for x in new])
        check(CE.covered(new[0], ["src/b.py"]) == ["src/b.py"], "F7 a build covers its staged dirs")
    finally:
        W.ROOT = old_root
        shutil.rmtree(repo / "src" / "Assemblies", ignore_errors=True)

    # F8: git never takes optional locks (a shared clone's index.lock)
    seen = []
    real_run = CE.subprocess.run

    def spy(cmd, **kw):
        seen.append(list(cmd))
        return real_run(cmd, **kw)
    CE.subprocess.run = spy
    try:
        CE.tree_state(repo)
    finally:
        CE.subprocess.run = real_run
    check(seen and all("--no-optional-locks" in c for c in seen), "F8 every git call passes --no-optional-locks")

    # F10 + WHO: seat in rimflow's order (RIMFLOW_SEAT, AGENT_SEAT, this session's role file), validated, never guessed
    keys = ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "AI_AGENT")
    saved = {k: os.environ.pop(k, None) for k in keys}
    real_sr = CE._seats_and_root
    try:
        os.environ.update(AGENT_SEAT="foundry", CLAUDE_CODE_SESSION_ID="sess-z", AI_AGENT="agent-z")
        r = CE.record("selftest", "PASS", [repo / "src"], clone=repo, start=CE.snapshot(repo))
        w = r.get("who") or {}
        check(r["seat"] == "FOUNDRY" and w.get("seat_from") == "AGENT_SEAT" and w.get("session") == "sess-z"
              and w.get("agent") == "agent-z", "F10/WHO seat+session+agent from AGENT_SEAT: %r" % w)
        os.environ["RIMFLOW_SEAT"] = "RUNNER"
        w = CE.whoami()
        check(w["seat"] == "RUNNER" and w["seat_from"] == "RIMFLOW_SEAT", "WHO RIMFLOW_SEAT outranks AGENT_SEAT: %r" % w)
        os.environ["RIMFLOW_SEAT"] = "ZSEAT"
        w = CE.whoami()
        check(w["seat"] is None and w["seat_raw"] == "ZSEAT" and w["seat_from"] == "RIMFLOW_SEAT",
              "WHO a non-rimflow seat is kept raw, seat stays None (no fallthrough guess): %r" % w)
        for k in ("RIMFLOW_SEAT", "AGENT_SEAT"):
            os.environ.pop(k)
        roles = Path(td) / "root" / ".claude" / "session_roles"
        roles.mkdir(parents=True)
        (roles / "sess-z").write_text("dispatcher seat for the night\n", encoding="utf-8")
        (roles / "sess-other").write_text("BENCH\n", encoding="utf-8")
        CE._seats_and_root = lambda: (real_sr()[0], str(Path(td) / "root"))
        w = CE.whoami()
        check(w["seat"] == "DISPATCHER" and w["seat_from"] == "session role file",
              "WHO seat from THIS session's role file: %r" % w)
        os.environ["CLAUDE_CODE_SESSION_ID"] = "sess-none"
        w = CE.whoami()
        check(w["seat"] is None and w["seat_from"] is None and w["session"] == "sess-none",
              "WHO no source -> seat None, never another session's file: %r" % w)
        # the Windows ship carries the CALLER's who (wsl.exe does not forward the environment)
        os.environ["AGENT_SEAT"] = "BENCH"
        sent = []

        class _R:
            returncode, stderr = 0, ""
            stdout = '{"ok": 1}\n'
        real_run = CE.subprocess.run
        CE.subprocess.run = lambda cmd, **kw: (sent.append(json.loads(kw["input"])), _R())[1]
        try:
            CE._ship_to_wsl({"tool": "modcheck", "result": "PASS", "paths": []})
        finally:
            CE.subprocess.run = real_run
        check(sent and sent[0].get("who", {}).get("seat") == "BENCH", "WHO shipped to WSL in the payload: %r"
              % (sent[0].get("who") if sent else None))
        # old lines (seat only, or no seat at all) stay readable
        day = store / ("%s.jsonl" % r["ts"][:10])
        old_line = dict(r)
        old_line.pop("who"); old_line.pop("seat"); old_line["tool"] = "oldseatless"
        with open(day, "a", encoding="utf-8") as f:
            f.write(json.dumps(old_line) + "\n")
        got = [x for x in CE.read_all(folder=store) if x.get("tool") == "oldseatless"]
        check(len(got) == 1 and got[0].get("seat") is None and CE.summarize(got) == {"oldseatless": "PASS"},
              "WHO a line without seat/who still reads and summarizes: %d %r" % (len(got), CE.summarize(got)))
    finally:
        CE._seats_and_root = real_sr
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v

if __name__ == "__main__":
    sys.exit(main())
