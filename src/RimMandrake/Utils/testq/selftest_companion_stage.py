#!/usr/bin/env python3
"""selftest_companion_stage.py - COMPANION_STAGE_FIX_JOBS_ARRIVE_STALE: a companion source commit is staged by itself, and
the filler holds rather than spend a job while it is not. A temp git repo, the real reader over a local fake ssh, a fake
build; no network and no dotnet."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []
BUILD = r'''
import os, sys
sys.path.insert(0, os.environ["BT_DIR"])
import companion_identity as CI
open(os.environ["BT_COUNT"], "a").write("x")
if os.path.exists(os.environ["BT_FAIL"]):
    print("CS0103"); sys.exit(1)
h = CI.srchash_worktree(os.environ["BT_REPO"])
if os.path.exists(os.environ["BT_WRONG"]):
    h = "0" * 64
CI.write_fixture(os.path.join(os.environ["BT_ART"], CI.DLL_NAME), h)
'''
FAKE_SSH = r'''
import os, subprocess, sys
if os.path.exists(os.environ["FAKE_SSH_DOWN"]):
    sys.stderr.write("ssh: no route\n"); sys.exit(255)
open(os.environ["FAKE_SSH_LOG"], "a").write("x")
sys.exit(subprocess.run(["bash", "-c", sys.argv[-1]]).returncode)
'''
NOTE_3B04B3 = ("companion STALE JawaBench.BridgeTools.dll not built from this job's sources (embedded d3ad4023cbcb, want "
               "1c4d3873ecae, staged copy STALE); fix: build.py --gm at the job's sha, then sync_test_mods.py --apply on "
               "Archmagi (stages it in TESTQ_HOME/companion/; the next job installs it with the game down)")


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t"] + list(args),
                          capture_output=True, text=True, check=True).stdout.strip()


def main():
    tmp = tempfile.mkdtemp(prefix="rf_cstage_")
    repo, art, steve, qh = (os.path.join(tmp, d) for d in ("repo", "art", "steve", "q"))
    bt_dir = os.path.abspath(os.path.join(HERE, "..", "..", "bridgetools"))
    flags = {k: os.path.join(tmp, k) for k in ("count", "fail", "wrong", "down", "sshlog")}
    build_py, ssh_py = os.path.join(tmp, "b.py"), os.path.join(tmp, "s.py")
    with open(build_py, "w") as f:
        f.write(BUILD)
    with open(ssh_py, "w") as f:
        f.write(FAKE_SSH)
    led, items, pulse = os.path.join(tmp, "ledger", "events.jsonl"), os.path.join(tmp, "items"), os.path.join(tmp, "pulse")
    for d in (os.path.dirname(led), items, pulse, art, qh):
        os.makedirs(d)
    open(led, "w").close()
    os.environ.update(
        TESTQ_QUEUE=qh, STEVE_TESTQ_HOME=steve + "/testq", STEVE_GAME_WSL=steve + "/game", STEVE_WSL="fake",
        TESTQ_SSH="%s %s" % (sys.executable, ssh_py), FAKE_SSH_DOWN=flags["down"], FAKE_SSH_LOG=flags["sshlog"],
        TESTQ_COMPANION_BUILD="%s %s" % (sys.executable, build_py), BT_DIR=bt_dir, BT_COUNT=flags["count"],
        BT_FAIL=flags["fail"], BT_WRONG=flags["wrong"], BT_REPO=repo, BT_ART=art, TESTQ_INGEST_PUSH="0",
        RIMFLOW_LEDGER=led, RIMFLOW_ITEMS=items, RM_PULSE_STATE=pulse, TESTQ_STEWARD_WAKE="0")
    for k in ("RIMFLOW_SEAT", "CLAUDE_PROJECT_DIR", "TESTQ_FILL_MODS"):
        os.environ.pop(k, None)
    sys.path.insert(0, HERE)
    import companion_stage as C
    import brake_release as BR
    import schema as S
    import steward as W
    T, M, CI = C.T, C.M, C.CI
    M.REPO, M.ARTIFACT, T.REPO = repo, art, repo
    W.tick_timer_state = lambda: "active"
    T.fill_rank = lambda mod, n, now, today=None, exclude=(): {"verdict": "pick", "pick": ["c1"], "purpose": "guard",
                                                               "row_items": {}, "text": "would queue c1", "dry": []}
    T.ensure_dirs()
    src = os.path.join(repo, *CI.SRC_REL.split("/"))
    os.makedirs(src)
    subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)

    def commit(name, text):
        path = os.path.join(repo, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "c")
        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        return git(repo, "rev-parse", "--short", "HEAD")

    def count(k):
        return os.path.getsize(flags[k]) if os.path.exists(flags[k]) else 0

    def state_file():
        return T.q(C.STATE)

    tool = CI.SRC_REL + "/Tools.cs"
    sha0 = commit(tool, "class A {}\n")

    # ---------------------------------------------- no stager yet: no hold, the worker's refusal stands
    check(T.companion_hold() is None, "no record: the stager never ran, no hold")
    check(T.companion_unready({"source_sha": sha0}) is None, "no record: no admission gate")

    # ---------------------------------------------- the staging itself
    rec = C.run_pass()
    inbox = os.path.join(steve, "testq", "companion", CI.DLL_NAME)
    check(rec["state"] == "staged" and rec["how"] == "built" and count("count") == 1, "first pass builds: %s" % rec)
    with open(inbox, "rb") as f:
        check(CI.embedded(f.read()) == C.wanted(), "the inbox DLL embeds origin/main's source hash")
    check(C.probe()["inbox"] == C.wanted() and C.probe()["game"] == "absent", "the remote reader sees inbox and game")
    check(T.companion_hold() is None, "staged: no hold")
    ssh_before = count("sshlog")
    rec = C.run_pass()
    check(rec["how"] == "unchanged" and count("count") == 1 and count("sshlog") == ssh_before,
          "unchanged sources: no build and no ssh on a tick: %s" % rec.get("how"))
    with open(state_file()) as f:
        check(json.load(f)["epoch"] >= rec["epoch"], "the reading is rewritten every pass")
    commit("docs/readme.txt", "not a companion source\n")
    rec = C.run_pass()
    check(rec["how"] == "unchanged" and count("count") == 1, "a commit elsewhere builds nothing")

    # ---------------------------------------------- the incident: a commit to the companion's sources
    sha1 = commit(tool, "class B {}\n")
    why = T.companion_hold()
    check(why and "companion hold" in why, "a source commit before the pass: held: %s" % why)
    now = time.time()
    plan = T.fill_plan("Mock", 1, 200, 3600, now)
    check(plan["verdict"] == "companion", "fill_plan says companion, not pick: %s" % plan["verdict"])
    r = T.cmd_fill(type("A", (), dict(mod="Mock", n=1, cap=200, day_s=3600))())
    check(r == 0 and not os.listdir(T.q("pending")), "the filler spends no job on it")
    rec = C.run_pass()
    check(rec["state"] == "staged" and rec["how"] == "built" and count("count") == 2, "the next pass stages it: %s" % rec)
    check(T.companion_hold() is None and T.fill_plan("Mock", 1, 200, 3600, now)["verdict"] == "pick",
          "and the filler picks again")

    # ---------------------------------------------- already there: the game copy is enough
    commit(tool, "class C {}\n")
    CI.write_fixture(os.path.join(steve, "game", "BridgeTools", "JawaBench", CI.DLL_NAME), C.wanted())
    rec = C.run_pass()
    check(rec["state"] == "staged" and rec["how"] == "present" and count("count") == 2,
          "a game copy already FRESH: nothing built or sent: %s" % rec)

    # ---------------------------------------------- failures hold, and say so
    commit(tool, "class D {}\n")
    open(flags["fail"], "w").close()
    rec = C.run_pass()
    check(rec["state"] == "failed" and "build.py exit 1" in rec["reason"] and count("count") == 3, "a failed build: %s" % rec)
    check("failed" in (T.companion_hold() or ""), "a failed build holds the filler")
    rec = C.run_pass()
    check(rec["state"] == "failed" and count("count") == 3, "not rebuilt every tick")
    since = rec["since"]
    ls = W.lane_state(time.time(), ["Mock"])
    check(ls["state"] == "IDLE_EMPTY" and "filler held" in ls["reason"] and ls["fault_at"] == since + W.COMPANION_GRACE_S,
          "the steward reads a held filler as a fault after a grace: %s" % ls["reason"][:60])
    rec = C.run_pass(time.time() + C.RETRY_S + 1)
    check(rec["state"] == "failed" and count("count") == 4, "retried after RETRY_S")
    os.remove(flags["fail"])
    open(flags["wrong"], "w").close()
    rec = C.run_pass(time.time() + 2 * C.RETRY_S + 2)
    check(rec["state"] == "failed" and "not fresh" in rec["reason"], "a build that is not fresh is never pushed: %s" % rec["reason"][:60])
    os.remove(flags["wrong"])
    rec = C.run_pass(time.time() + 3 * C.RETRY_S + 3)
    check(rec["state"] == "staged" and T.companion_hold() is None, "the fix clears the hold")

    commit(tool, "class E {}\n")
    open(flags["down"], "w").close()
    n = count("count")
    rec = C.run_pass()
    check(rec["state"] == "unread" and count("count") == n and T.companion_hold(), "ssh down: unread, not staged, no build")
    check(C.probe() is None, "the reader says None, never 'absent', when it cannot read")
    os.remove(flags["down"])
    with open(os.path.join(src, "Tools.cs"), "w") as f:
        f.write("class Dirty {}\n")
    rec = C.run_pass()
    check(rec["state"] == "behind" and count("count") == n, "a worktree off origin/main builds nothing: %s" % rec["state"])
    git(repo, "checkout", "-q", "--", tool)
    check(C.run_pass()["state"] == "staged", "level again: staged")

    # ---------------------------------------------- the admission gate
    sha_new = git(repo, "rev-parse", "--short", "HEAD")
    started = []
    T.remote = lambda args, stdin=None, timeout=180: (started.append(json.loads(stdin)["id"]), (0, {"attempt": "A1"}))[1]

    def pending(sha, by):
        j = S.make_job("Mock", {"chains": ["c1"]}, "guard", by, sha)
        S.dump(j, T.q("pending", j["id"] + ".json"))
        return j

    j = pending(sha1, T.FILLER)
    T.admit({})
    check(T.where(j["id"]) == "cancelled" and not started, "a filler job at a sha whose companion left is cancelled unspent")
    j = pending(sha1, "BENCH")
    T.admit({})
    check(started == [j["id"]], "a hand job is not the gate's: the worker judges it")
    os.remove(T.q("running", j["id"] + ".json"))
    started.clear()
    j = pending(sha_new, T.FILLER)
    T.admit({})
    check(started == [j["id"]], "a filler job at the staged sources runs")
    os.remove(T.q("running", j["id"] + ".json"))

    # ---------------------------------------------- the brake: a recorded cause, released only once staged
    def res(outcome, cause, note):
        return {"result": {"outcome": outcome, "cause": cause, "note": note}, "finished": S.utcnow()}
    check(T.nonfault_cause(res("INVALID", "DEPLOY", NOTE_3B04B3), []) == "companion_stale",
          "the worker's own stale note is a recorded cause")
    check(T.nonfault_cause(res("INVALID", "DEPLOY", "deploy failed: exit 1"), []) is None, "any other deploy death is a fault")
    check(T.nonfault_cause(res("INVALID", "CANARY", NOTE_3B04B3), []) is None, "that note on another cause excuses nothing")
    for k in ("MISSING", "UNSTAMPED"):
        check(T.nonfault_cause(res("INVALID", "DEPLOY", "companion %s JawaBench.BridgeTools.dll not" % k), []) == "companion_stale",
              "%s too" % k)

    for i in (0, 1):
        j = S.make_job("Mock", {"chains": ["c1"]}, "guard", T.FILLER, sha1)
        j["id"], j["submitted"] = "J%d" % i, "2026-11-03T1%d:00:00Z" % i
        S.dump({"job": j, "result": {"outcome": "INVALID", "cause": "DEPLOY", "note": NOTE_3B04B3},
                "finished": "2026-11-03T1%d:05:00Z" % i}, T.q("done", j["id"] + ".json"))
    sent = []
    BR.submit = lambda mod, req: (sent.append(req), (0, '{"job": "Jc"}'))[1]
    good = T.read_json(state_file())
    S.dump(dict(good, state="failed", reason="dotnet"), state_file())
    rec = BR.decide(time.time(), ["Mock"])
    check(rec["state"] == "wait" and "companion hold" in rec["reason"] and not sent, "no canary while not staged: %s" % rec["state"])
    S.dump(good, state_file())
    rec = BR.decide(time.time(), ["Mock"])
    check(rec["state"] == "released" and len(sent) == 1, "staged: the one canary goes: %s" % rec.get("reason"))

    # ---------------------------------------------- the proof reads the real shapes
    ok, _ = C.proof()
    check(not ok, "proof: no job passed deploy FRESH yet: FAIL")
    fin = "2030-01-01T00:00:00Z"
    j = S.make_job("Mock", {"chains": ["c1"]}, "guard", "Operations.canary", sha_new)
    j["id"] = "Jfresh"
    S.dump({"job": j, "finished": fin, "result": {"outcome": "DONE", "deployed": {"companion": {"state": "FRESH"}}}},
           T.q("done", "Jfresh.json"))
    S.dump({"state": "RUNNING", "reason": "x", "jobs": []}, T.q("steward.json"))
    check(not C.proof()[0], "proof: a canary alone is not the filler reaching the lane: FAIL")
    j = dict(j, requested_by=T.FILLER)
    S.dump({"job": j, "finished": fin, "result": {"outcome": "DONE", "deployed": {"companion": {"state": "FRESH"}}}},
           T.q("done", "Jfresh.json"))
    S.dump({"state": "BRAKED", "reason": "tail", "jobs": ["J0", "J1"]}, T.q("steward.json"))
    ok, lines = C.proof()
    check(not ok, "proof: the brake that began this still holds: FAIL: %s" % lines[-1][:40])
    S.dump({"state": "RUNNING", "reason": "x", "jobs": []}, T.q("steward.json"))
    ok, lines = C.proof()
    check(ok, "proof: fresh job, lane out of BRAKED, stager alive: PASS: %s" % lines)
    j2 = dict(j, id="Jnew")
    S.dump({"job": j2, "finished": "2031-01-01T00:00:00Z", "result": {"outcome": "INVALID", "cause": "CANARY"}}, T.q("done", "Jnew.json"))
    S.dump({"state": "BRAKED", "reason": "later", "jobs": ["Jnew"]}, T.q("steward.json"))
    check(C.proof()[0], "proof: a later brake on newer jobs is a new incident")
    S.dump({"state": "RUNNING", "reason": "x", "jobs": []}, T.q("steward.json"))
    check(not C.proof(time.time() + C.PROOF_MAX_AGE_S + 60)[0], "proof: a stager gone silent: FAIL")
    S.dump(dict(T.read_json(state_file()), state="failed"), state_file())
    check(not C.proof()[0], "proof: a failing stager: FAIL")

    # ---------------------------------------------- the unit
    unit = T.UNITS["testq-tick.service"]
    a, b, c = unit.index("pull -q"), unit.index("companion_stage.py run"), unit.index("testq.py tick")
    check(a < b < c and unit.index("testq.py fill") > c, "the tick unit stages after its pull, before admit and fill")
    check("ExecStart=-/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/companion_stage.py" in unit,
          "a stager crash does not stop the tick")

    shutil.rmtree(tmp, ignore_errors=True)
    print("RESULT: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
