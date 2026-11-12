#!/usr/bin/env python3
"""selftest_deploy_memo.py - deploy_memo.py and its worker hooks (RIMMANDRAKE_TESTQ_DEPLOY_MEMO_SKIP_UNCHANGED), on a throwaway git
repo and game Mods folder. Proves: first job misses and records; the same job again HITS (plan skipped, attest record
reused); a commit touching a deployed mod's source misses; a commit touching only another mod still hits; a game file
changed / added / removed (stat signature) misses; a different attest set misses; the switch off (default) never hits
and never writes; TESTQ_CMD_DEPLOY lanes never memoise.
"""
import io
import os
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import worker as W  # noqa: E402
import deploy_memo as M  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


repo = tempfile.mkdtemp(prefix="memo_repo_")
home = tempfile.mkdtemp(prefix="memo_home_")
mods = tempfile.mkdtemp(prefix="memo_mods_")
G = ["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t"]


def git(*a):
    return subprocess.run(G + list(a), capture_output=True, text=True, check=True).stdout.strip()


def put(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


git("init", "-q", "-b", "main")
for m in ("ModA", "ModB"):
    put(os.path.join(repo, "src", "RimMandrake", m, "About", "About.xml"), "<a/>")
    put(os.path.join(repo, "src", "RimMandrake", m, "Defs", "d.xml"), "<Defs/>")
    put(os.path.join(mods, m, "About", "About.xml"), "<a/>")
    put(os.path.join(mods, m, "Defs", "d.xml"), "<Defs/>")
put(os.path.join(repo, "src", "RimMandrake", "Utils", "deploy_custom_mods.py"), "# tool\n")
git("add", "-A")
git("commit", "-q", "-m", "base")
sha0 = git("rev-parse", "HEAD")

W.RUNNER = W.CLONE = repo
W.HOME = home
os.environ["TESTQ_MODS_DIR"] = mods
os.environ.pop("TESTQ_CMD_DEPLOY", None)
os.environ["TESTQ_DEPLOY_MEMO"] = "1"
DEP = {"ModA": {"dll_sha256": "d", "defs_sha256": "e", "files": 2}}


class FakeAttempt(W.Attempt):
    def __init__(self, sha, mod="ModA", jid="J1"):
        self.job = {"id": jid, "item": "X", "mod": mod, "profile": "default", "source_sha": sha, "selector": {"chains": ["c"]}}
        self.res = {}
        self.log = io.StringIO()
        self.d = home
        self.aid = jid + ".a1"

    def say(self, m):
        self.log.write(m + "\n")


def attempt_cycle(sha, mod="ModA", jid="J1"):
    """deploy-side lookup, then (on a miss) the attest-side save. -> hit?"""
    a = FakeAttempt(sha, mod, jid)
    hit = a.memo_hit(a.deploy_mods())
    if not hit:
        a.memo_save({mod: DEP["ModA"]} if mod == "ModA" else {mod: {"dll_sha256": "x", "defs_sha256": "y", "files": 2}})
    return hit, a


h, a = attempt_cycle(sha0)
check(not h and os.path.isfile(os.path.join(home, "deploy_memo.json")), "first job: miss, memo written")
h, a = attempt_cycle(sha0, jid="J2")
check(h and a.res.get("deploy_memo", {}).get("since") == "J1" and "UNCHANGED" in a.log.getvalue(), "same job again: HIT, names the previous job")
check(a.memo_mods == {"ModA": DEP["ModA"]}, "hit reuses the previous attest record")

put(os.path.join(repo, "src", "RimMandrake", "ModB", "Defs", "d.xml"), "<Defs><x/></Defs>")
git("commit", "-q", "-am", "touch ModB only")
sha1 = git("rev-parse", "HEAD")
h, a = attempt_cycle(sha1, jid="J3")
check(h, "a commit that touched only another mod still hits")
put(os.path.join(repo, "src", "RimMandrake", "ModA", "Defs", "d.xml"), "<Defs><y/></Defs>")
git("commit", "-q", "-am", "touch ModA")
sha2 = git("rev-parse", "HEAD")
h, a = attempt_cycle(sha2, jid="J4")
check(not h, "a commit touching the deployed mod's source misses")
h, a = attempt_cycle(sha2, jid="J5")
check(h, "...and records, so the next identical job hits again")

# game folder changes the memo has to see
f = os.path.join(mods, "ModA", "Defs", "d.xml")
st = os.stat(f)
os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))
h, a = attempt_cycle(sha2, jid="J6")
check(not h, "a game file with a new mtime misses")
h, a = attempt_cycle(sha2, jid="J7")
check(h, "re-recorded: hits")
put(os.path.join(mods, "ModA", "extra.dll"), "x")
h, a = attempt_cycle(sha2, jid="J8")
check(not h, "a file added to the game folder misses")
os.remove(os.path.join(mods, "ModA", "extra.dll"))
h, a = attempt_cycle(sha2, jid="J9")
check(not h, "a file removed from the game folder misses")
h, a = attempt_cycle(sha2, jid="J10")
check(h, "settled: hits")

# a different mod, a different attest set
h, a = attempt_cycle(sha2, mod="ModB", jid="J11")
check(not h, "a different mod misses")
fa = FakeAttempt(sha2, "ModA", "J12")
M.save(os.path.join(home, "deploy_memo.json"), M.key_for(W.S, repo, sha2, ["ModA"], os.path.join(repo, "src")),
       M.game_sig(mods, ["ModA"]), {"ModA": DEP["ModA"], "Other": DEP["ModA"]}, "J0")
check(not fa.memo_hit(fa.deploy_mods()), "a memo whose attest record covers other mods than this job's misses")

# switches
os.environ["TESTQ_DEPLOY_MEMO"] = "0"
mp = os.path.join(home, "deploy_memo.json")
M.forget(mp)
h, a = attempt_cycle(sha2, jid="J13")
check(not h and not os.path.exists(mp), "switch off: no hit, nothing written (old behaviour)")
os.environ.pop("TESTQ_DEPLOY_MEMO")
h, a = attempt_cycle(sha2, jid="J13b")
check(not h and not os.path.exists(mp), "env unset and no deploy_memo.on file: off")
open(os.path.join(home, "deploy_memo.on"), "w").close()
h, a = attempt_cycle(sha2, jid="J13c")
h, a = attempt_cycle(sha2, jid="J13d")
check(h, "env unset, deploy_memo.on in the lane's home: on")
os.environ["TESTQ_DEPLOY_MEMO"] = "0"
h, a = attempt_cycle(sha2, jid="J13e")
check(not h, "env =0 beats the file")
os.remove(os.path.join(home, "deploy_memo.on"))
os.environ["TESTQ_DEPLOY_MEMO"] = "1"
M.forget(mp)
os.environ["TESTQ_CMD_DEPLOY"] = "echo"
h, a = attempt_cycle(sha2, jid="J14")
h, a = attempt_cycle(sha2, jid="J15")
check(not h and not os.path.exists(mp), "a TESTQ_CMD_DEPLOY lane never memoises")
os.environ.pop("TESTQ_CMD_DEPLOY")

# attest with a hit hashes nothing
a = FakeAttempt(sha2, "ModA", "J16")
a.companion_state = None
attempt_cycle(sha2, jid="J16")
a = FakeAttempt(sha2, "ModA", "J17")
a.companion_state = None
a.memo_hit(a.deploy_mods())
calls = []
orig = W.sha256_file
W.sha256_file = lambda x: calls.append(x) or orig(x)
a.attest()
W.sha256_file = orig
check(a.res["deployed"]["mods"] == {"ModA": DEP["ModA"]} and not [c for c in calls if c.startswith(mods)],
      "attest on a hit reuses the record and hashes no game file")

print("\n%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
