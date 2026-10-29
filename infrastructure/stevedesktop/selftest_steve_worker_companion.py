#!/usr/bin/env python3
"""selftest_steve_worker_companion.py - the worker refuses a JawaBench companion not built from the job's sources.

STEVE_COMPANION_FIX_DLL_STALE_NO_PRIORITIES (2026-10-29): J20261029T211737Z-3af227 ran droid_dig on SteveDesktop with a
companion older than jawa/set_work_priority's manualPrioritiesOn; the attempt read DONE with both rows UNMEASURED,
because deploy and attest never looked at the companion. Offline, mock phases (as selftest_steve_worker.py):
  * companion_identity: the git-tree hash equals the worktree hash; CRLF folds; bin/obj and non-source files are
    outside it; the embedded AssemblyMetadata blob is read back; a changed .cs changes the hash
  * a FRESH companion -> DONE, deployed.companion attested FRESH
  * a STALE one, an UNSTAMPED (pre-stamp) one and a MISSING one, nothing staged -> INVALID/DEPLOY naming the DLL,
    before load: no game load, no modcheck run
  * STALE with a FRESH copy staged in TESTQ_HOME/companion -> game down, installed, DONE, attested installed_from
  * STALE with a stale copy staged -> INVALID/DEPLOY, the game copy untouched
  * the Archmagi lane (never deploys) -> REFUSED/DEPLOY even with a fresh copy staged, no game down
SELFTEST_WORKER=<path> runs the cases against another worker.py (the before-fix one: they must fail there).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER = os.path.abspath(os.path.join(HERE, "..", ".."))
WORKER = os.environ.get("SELFTEST_WORKER") or os.path.join(HERE, "worker.py")
sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "Utils", "testq"))
sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "bridgetools"))
import schema as S  # noqa: E402
import companion_identity as CI  # noqa: E402

FAILS = []
MOCK = r'''
import json, os, sys, time
open(os.path.join(os.environ["TESTQ_HOME"], "ran_modcheck"), "a").write("x\n")
sheet_dir = os.environ["TESTQ_SHEET_DIR"]
name = "Mock_%d" % int(time.time() * 1000)
summary = {"chains": [{"name": "c1", "components": [{"name": "r1", "verdict": "PASS", "detail": "ok"}]}]}
json.dump({"mod": "Mock", "summary": summary}, open(os.path.join(sheet_dir, name + ".json"), "w"))
open(os.path.join(sheet_dir, name + ".html"), "w").write("<html/>")
print("[modcheck] sheet \\\\wsl.localhost\\Ubuntu\\x\\Transient\\modcheck\\%s.html" % name)
'''


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def fake_dll(src_hash, commit="0" * 40):
    """PE-ish bytes carrying the two stamps the way the compiler writes them (AssemblyMetadata blob, UTF-16 version)."""
    blob = b"MZ\x90\x00" + b"\x00" * 60
    if src_hash:
        key = CI.META_KEY.encode()
        blob += b"\x01\x00" + bytes([len(key)]) + key + bytes([len(src_hash)]) + src_hash.encode() + b"\x00\x00"
    return blob + ("0.1.0+" + commit).encode("utf-16-le") + b"\x00" * 32


def identity_unit(tmp):
    repo = os.path.join(tmp, "irepo")
    src = os.path.join(repo, *CI.SRC_REL.split("/"))
    for d in ("", "Sub", "bin", "obj"):
        os.makedirs(os.path.join(src, d), exist_ok=True)
    files = {"A.cs": b"class A {}\r\n", "Sub/B.cs": b"class B {}\n", "J.csproj": b"<Project/>\n",
             "bin/X.cs": b"junk", "obj/Gen.cs": b"generated", "notes.md": b"not compiled"}
    for rel, data in files.items():
        with open(os.path.join(src, rel), "wb") as f:
            f.write(data)
    g = ["git", "-C", repo]
    subprocess.run(g + ["init", "-q"], check=True)
    subprocess.run(g + ["add", "-f", "."], check=True)
    subprocess.run(g + ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"], check=True)
    at, wt = CI.srchash_at(repo, "HEAD"), CI.srchash_worktree(repo)
    check(at and at == wt, "git-tree hash == worktree hash: %s %s" % (at and at[:12], wt and wt[:12]))
    want = CI.digest({"A.cs": b"class A {}\n", "Sub/B.cs": b"class B {}\n", "J.csproj": b"<Project/>\n"})
    check(at == want, "the hash covers .cs/.csproj only, bin/ obj/ and notes.md outside, CRLF folded")
    with open(os.path.join(src, "A.cs"), "ab") as f:
        f.write(b"// one more line\n")
    check(CI.srchash_worktree(repo) != at, "an edited .cs changes the worktree hash")
    check(CI.embedded(fake_dll(want)) == want and CI.embedded(fake_dll(None)) is None,
          "the embedded AssemblyMetadata value is read back; none when absent")
    check(CI.build_commit(fake_dll(want, "ab" * 20)) == "ab" * 20, "the build commit is read back (informational)")
    check(CI.srchash_at(repo, "no-such-rev") is None, "an unreadable rev hashes to None (UNMEASURED), never ''")


def main():
    tmp = tempfile.mkdtemp(prefix="rf_stevecompanion_")
    try:
        identity_unit(tmp)
        head = subprocess.run(["git", "-C", RUNNER, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        want = CI.srchash_at(RUNNER, head)
        check(bool(want), "the runner's companion sources at HEAD hash: %s" % (want or "")[:12])
        home, sheets, mods = (os.path.join(tmp, d) for d in ("home", "sheets", "mods"))
        comp = os.path.join(tmp, "BridgeTools", "JawaBench")       # the Mods folder's sibling: the default the worker derives
        for d in (home, sheets, os.path.join(mods, "Mock", "Defs"), comp, os.path.join(home, "companion")):
            os.makedirs(d, exist_ok=True)
        open(os.path.join(mods, "Mock", "Defs", "a.xml"), "w").write("<Defs/>")
        mock = os.path.join(tmp, "mock_modcheck.py")
        open(mock, "w").write(MOCK)
        mark = os.path.join(tmp, "calls.txt")
        env = {k: v for k, v in os.environ.items() if k not in ("RM_HOST_GUARD_GEN", "RIMFLOW_SEAT", "TESTQ_COMPANION_DIR")
               and not k.startswith("TESTQ_")}
        env.update(TESTQ_HOME=home, TESTQ_SHEET_DIR=sheets, TESTQ_MODS_DIR=mods, TESTQ_SKIP_PULL="1",
                   TESTQ_NO_SYSTEMD="1", TESTQ_CMD_DEPLOY="true",
                   TESTQ_CMD_LOAD="echo load >> %s" % mark, TESTQ_CMD_DOWN="echo down >> %s" % mark,
                   TESTQ_CMD_RUN="%s %s run" % (sys.executable, mock), RIMFLOW_DRIVER_LOCK=os.path.join(tmp, "lock.json"),
                   TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'", TESTQ_REPO=RUNNER,
                   RM_HOST="stevedesktop", RM_GAME_USERDATA=tmp, RIMFLOW_LEDGER=os.path.join(tmp, "ev.jsonl"))
        target, staged = os.path.join(comp, CI.DLL_NAME), os.path.join(home, "companion", CI.DLL_NAME)

        def put(path, data):
            if data is None:
                if os.path.exists(path):
                    os.remove(path)
                return
            with open(path, "wb") as f:
                f.write(data)

        def run(game, stage, **extra):
            put(target, game)
            put(staged, stage)
            for f in (mark, os.path.join(home, "ran_modcheck")):
                if os.path.exists(f):
                    os.remove(f)
            j = S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", head)
            r = subprocess.run([sys.executable, WORKER, "start"], input=json.dumps(j), env=dict(env, **extra),
                               capture_output=True, text=True, timeout=60)
            try:
                aid = json.loads(r.stdout.strip().splitlines()[-1])["attempt"]
            except (ValueError, IndexError, KeyError):
                return {"raw": r.stdout + r.stderr}, [], False
            path = os.path.join(home, "attempts", aid, "result.json")
            t = time.time()
            while time.time() - t < 40 and not os.path.exists(path):
                time.sleep(0.3)
            res = json.load(open(path)) if os.path.exists(path) else {}
            calls = open(mark).read().split() if os.path.exists(mark) else []
            return res, calls, os.path.exists(os.path.join(home, "ran_modcheck"))

        def oc(res):
            return (res.get("outcome"), res.get("cause"))

        fresh, other = fake_dll(want), fake_dll("f" * 64)
        res, calls, ran = run(fresh, None)
        comp_att = (res.get("deployed") or {}).get("companion") or {}
        check(oc(res) == ("DONE", None) and comp_att.get("state") == "FRESH" and comp_att.get("embedded") == want,
              "a FRESH companion -> DONE, attested FRESH: %s %s" % (oc(res), comp_att.get("state")))

        for label, game in (("STALE", other), ("UNSTAMPED", fake_dll(None)), ("MISSING", None)):
            res, calls, ran = run(game, None)
            note = res.get("note") or ""
            check(oc(res) == ("INVALID", "DEPLOY") and label in note and CI.DLL_NAME in note,
                  "%s companion, nothing staged -> INVALID/DEPLOY naming the DLL: %s %s" % (label, oc(res), note[:120]))
            check("load" not in calls and not ran and not res.get("rows"),
                  "%s: the attempt ends before load and modcheck (calls %s, modcheck ran %s)" % (label, calls, ran))

        res, calls, ran = run(other, fresh)
        comp_att = (res.get("deployed") or {}).get("companion") or {}
        same = os.path.exists(target) and open(target, "rb").read() == fresh
        check(oc(res) == ("DONE", None) and same and comp_att.get("installed_from") == staged
              and (comp_att.get("replaced") or {}).get("state") == "STALE",
              "STALE + a FRESH staged copy -> installed, DONE, attested: %s installed=%s" % (oc(res), same))
        check(calls[:1] == ["down"] and "load" in calls and calls.index("down") < calls.index("load"),
              "the staged companion goes in with the game DOWN, before load: %s" % calls)

        res, calls, ran = run(other, fake_dll("e" * 64))
        check(oc(res) == ("INVALID", "DEPLOY") and open(target, "rb").read() == other and "down" not in calls,
              "STALE + a stale staged copy -> INVALID/DEPLOY, game copy untouched, no game down: %s %s" % (oc(res), calls))

        res, calls, ran = run(other, fresh, TESTQ_WORKER_HOST="archmagi")
        check(oc(res) == ("REFUSED", "DEPLOY") and open(target, "rb").read() == other and "down" not in calls,
              "the Archmagi lane never installs: REFUSED/DEPLOY, no game down: %s %s" % (oc(res), calls))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
