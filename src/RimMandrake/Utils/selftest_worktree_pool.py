#!/usr/bin/env python3
"""Selftest for worktree_pool.py + land_submissions.py, in a throwaway repo under
/home/mandrake/wt/p7test (ext4; never the real seat clones or pool).

Covers: seat derivation, 2-slot allocation, lock JSON fields, `git worktree lock`, pool-full exit 1,
clean recycle, PID-reuse defeat, busy-by-cwd, the KILL-MID-EDIT rescue (a real child process
SIGKILLed while writing in the slot: dirty tracked + staged + untracked + an unpushed commit +
a >5 MB file + an ignored file + a suspect secret), submit -> land_submissions -> clean recycle
of a rebased submission, already-landed cleanup, conflict refusal, remove, status, rescue-list.
"""
import json
import os
import shutil
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.join(HERE, "worktree_pool.py")
LAND = os.path.join(HERE, "land_submissions.py")
BASE = "/home/mandrake/wt/p7test"
FAILS = []


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def sh(cwd, *cmd, env=None, input=None, ok=True):
    p = subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True, env=env, input=input)
    if ok and p.returncode != 0:
        raise SystemExit("command failed %s: %s %s" % (cmd, p.stdout, p.stderr))
    return p


def main():
    if not os.path.isdir("/home/mandrake/wt"):
        print("no /home/mandrake/wt on this machine — UNMEASURED, not a pass or a fail")
        return 0
    root = os.path.join(BASE, "selftest-%d" % os.getpid())
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)
    remote, seats, pool = root + "/remote.git", root + "/rm", root + "/rm/pool"
    env = dict(os.environ, RM_SEAT_ROOT=seats, RM_POOL_ROOT=pool, RM_POOL_SLOTS="2",
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    env.pop("AGENT_SEAT", None)
    sh(root, "git", "init", "-q", "--bare", "-b", "main", remote)
    seed = root + "/seed"
    sh(root, "git", "clone", "-q", remote, seed, env=env)
    open(seed + "/a.txt", "w").write("one\n")
    open(seed + "/.gitignore", "w").write("obj/\n")
    sh(seed, "git", "add", "a.txt", ".gitignore", env=env)
    sh(seed, "git", "commit", "-qm", "seed", env=env)
    sh(seed, "git", "push", "-q", "origin", "HEAD:main", env=env)
    clone = seats + "/bench"
    sh(root, "git", "clone", "-q", remote, clone, env=env)
    owners = []

    def owner():
        p = subprocess.Popen(["sleep", "600"])
        owners.append(p)
        return p

    def create(name, own, cwd=clone, extra=None):
        e = dict(env, RM_POOL_OWNER_PID=str(own.pid), **(extra or {}))
        d = {"session_id": "s-" + name, "transcript_path": "/x/" + name + ".jsonl", "cwd": cwd,
             "hook_event_name": "WorktreeCreate", "name": name}
        return sh(clone, sys.executable, POOL, "create", env=e, input=json.dumps(d), ok=False)

    def lock(n):
        return json.load(open("%s/bench/slot%d.lock" % (pool, n)))

    try:
        # --- seat derivation
        o = owner()
        r = create("x", o, cwd=root)
        check(r.returncode == 1 and "cannot derive a seat" in r.stderr, "no seat -> exit 1 with clear message")
        r = create("x", o, cwd=root, extra={"AGENT_SEAT": "BENCH"})
        check(r.returncode == 0 and r.stdout.strip() == pool + "/bench/slot0", "AGENT_SEAT=BENCH -> slot0")
        o.kill(); o.wait()

        # --- allocation, lock JSON, worktree lock, .claude-free path
        o1, o2 = owner(), owner()
        r1 = create("a1", o1)
        check(r1.returncode == 0, "a1 allocates")
        s0 = r1.stdout.strip().splitlines()[0]
        check(s0 == pool + "/bench/slot0" and ".claude" not in s0.split("/"), "a1 -> slot0, .claude-free path")
        lk = lock(0)
        check(set(lk) >= {"pid", "pid_start", "session_id", "transcript_path", "name", "generation",
                          "base_sha", "started"} and lk["pid"] == o1.pid and lk["generation"] == 2,
              "lock JSON has every field, owner pid, generation increments (2nd alloc of slot0)")
        wl = sh(clone, "git", "worktree", "list", "--porcelain").stdout
        check("locked s-a1 gen 2" in wl, "git worktree lock --reason carries session + generation")
        check(sh(s0, "git", "symbolic-ref", "--short", "HEAD").stdout.strip() == "agent/a1", "slot on agent/a1")
        r2 = create("a2", o2)
        s1 = r2.stdout.strip()
        check(r2.returncode == 0 and s1 == pool + "/bench/slot1", "a2 -> slot1 while slot0 held")
        r3 = create("a3", owner())
        check(r3.returncode == 1 and r3.stderr.startswith("pool full") and str(o1.pid) in r3.stderr,
              "3rd with 2 busy -> exit 1 'pool full' naming holder pids")
        tel = [json.loads(l) for l in open(pool + "/telemetry.jsonl")]
        check(tel[-1]["outcome"] == "full" and tel[-1]["MemAvailable_kib"] and
              any(t["outcome"] == "alloc" for t in tel), "telemetry: alloc + full lines with MemAvailable")

        # --- PID reuse: alive pid but wrong start time is NOT busy
        lk = lock(0); lk["pid_start"] = 1; json.dump(lk, open("%s/bench/slot0.lock" % pool, "w"))
        o1.kill(); o1.wait()
        # --- busy by cwd: owner dead, but a descendant still sits in the slot
        squatter = subprocess.Popen(["sleep", "600"], cwd=s0)
        r = create("a4", owner())
        check(r.returncode == 1 and "cwd/fd under the slot" in r.stderr, "dead owner + process cwd in slot -> busy")
        squatter.kill(); squatter.wait()
        lk = lock(0); lk["pid"] = os.getpid(); lk["pid_start"] = 1   # live pid, wrong start
        json.dump(lk, open("%s/bench/slot0.lock" % pool, "w"))
        o4 = owner()
        r = create("a4", o4)
        check(r.returncode == 0 and r.stdout.strip() == s0, "pid alive with wrong start -> free; clean slot recycled")
        check(not os.path.exists(pool + "/rescues.jsonl"), "clean landed recycle makes no rescue")

        # --- KILL-MID-EDIT: a real writer in slot1, SIGKILLed mid-edit with its owner
        sh(s1, "git", "config", "user.email", "t@t", env=env); sh(s1, "git", "config", "user.name", "t", env=env)
        open(s1 + "/b.txt", "w").write("committed-but-unpushed\n")
        sh(s1, "git", "add", "b.txt", env=env); sh(s1, "git", "commit", "-qm", "unpushed", env=env)
        unpushed = sh(s1, "git", "rev-parse", "HEAD").stdout.strip()
        writer = subprocess.Popen([sys.executable, "-c", (
            "import os,time\n"
            "open('a.txt','w').write('EDITED tracked\\n')\n"
            "open('staged.txt','w').write('staged v1\\n')\n"
            "os.system('git add staged.txt')\n"
            "open('staged.txt','w').write('staged v2 worktree\\n')\n"
            "os.makedirs('newdir',exist_ok=True); open('newdir/untracked.cs','w').write('class X{}\\n')\n"
            "open('id_rsa','w').write('-----BEGIN OPENSSH PRIVATE KEY-----\\n')\n"
            "open('big.bin','wb').write(os.urandom(6*1024*1024))\n"
            "os.makedirs('obj',exist_ok=True); open('obj/out.dll','wb').write(b'MZ\\0')\n"
            "open('READY','w').write('1')\n"
            "f=open('streaming.log','w')\n"
            "i=0\n"
            "while True:\n f.write('line %d\\n'%i); f.flush(); i+=1; time.sleep(0.05)\n")],
            cwd=s1, env=env)
        for _ in range(100):
            if os.path.exists(s1 + "/READY"):
                break
            time.sleep(0.1)
        time.sleep(0.3)
        r = create("a5", owner())
        check(r.returncode == 1, "while the writer lives (owner alive too) the pool stays full")
        os.kill(writer.pid, signal.SIGKILL); writer.wait()
        os.kill(o2.pid, signal.SIGKILL); o2.wait()
        r = create("a5", owner())
        check(r.returncode == 0 and r.stdout.strip() == s1, "after SIGKILL, next allocation takes slot1")
        evs = [json.loads(l) for l in open(pool + "/rescues.jsonl")]
        ev = evs[-1] if evs else {}
        ref = ev.get("ref", "")
        check(ref.startswith("refs/rescue/bench/a2-") and ev.get("pushed") is False, "rescue event with local ref")
        show = lambda p: sh(clone, "git", "show", "%s:%s" % (ref, p), ok=False)
        check(show("a.txt").stdout == "EDITED tracked\n", "rescue holds the dirty tracked edit")
        check(show("staged.txt").stdout == "staged v2 worktree\n", "rescue holds the worktree version of a staged file")
        check(sh(clone, "git", "show", "%s^2:staged.txt" % ref, ok=False).stdout == "staged v1\n",
              "rescue's 2nd parent holds the staged (index) version")
        check(show("newdir/untracked.cs").stdout == "class X{}\n", "rescue holds the untracked file")
        check(show("streaming.log").stdout.startswith("line 0"), "rescue holds the file being written at kill time")
        check(sh(clone, "git", "merge-base", "--is-ancestor", unpushed, ref, ok=False).returncode == 0,
              "rescue keeps the unpushed commit reachable")
        check(show("big.bin").returncode != 0, ">5 MB untracked not stored")
        msg = sh(clone, "git", "log", "-1", "--format=%B", ref).stdout
        check("big.bin" in msg and "obj/" in msg, ">5 MB and ignored paths listed in the message")
        c = ev.get("classes", {})
        check(c.get("suspect-secret") == 1 and c.get("source", 0) >= 2 and c.get("generated", 0) >= 1
              and c.get("binary") == 1, "classification: secret/source/generated/binary (%s)" % c)
        check(sh(s1, "git", "status", "--porcelain").stdout == "", "slot1 came back clean")
        check(os.path.exists(s1 + "/obj/out.dll"), "ignored build cache kept warm")
        check(sh(clone, "git", "ls-remote", remote).stdout.count("rescue") == 0, "rescue ref never pushed")
        rl = sh(clone, sys.executable, POOL, "rescue-list", env=env).stdout
        check(ref in rl, "rescue-list shows the ref")

        # --- submit + land (rebased landing must still recycle clean)
        sh(s0, "git", "config", "user.email", "t@t"); sh(s0, "git", "config", "user.name", "t")
        open(s0 + "/c.txt", "w").write("helper work\n")
        sh(s0, "git", "add", "c.txt"); sh(s0, "git", "commit", "-qm", "helper c")
        sub = sh(s0, sys.executable, POOL, "submit", env=env, ok=False)
        check(sub.returncode == 0 and "SUBMITTED refs/heads/submit/bench/a4" in sub.stdout, "submit pushes submit ref")
        sh(seed, "git", "pull", "-q", "--rebase", "origin", "main", env=env)
        open(seed + "/d.txt", "w").write("main moved\n")
        sh(seed, "git", "add", "d.txt", env=env); sh(seed, "git", "commit", "-qm", "main moves", env=env)
        sh(seed, "git", "push", "-q", "origin", "HEAD:main", env=env)
        land = sh(clone, sys.executable, LAND, env=env, ok=False)
        check(land.returncode == 0 and "LANDED a4" in land.stdout, "land_submissions rebases + lands")
        heads = sh(clone, "git", "ls-remote", remote).stdout
        check("submit/bench/a4" not in heads, "submit ref deleted after landing")
        tree = sh(clone, "git", "ls-tree", "--name-only", "refs/remotes/origin/main").stdout.split()
        check({"c.txt", "d.txt"} <= set(tree), "origin/main has helper + concurrent work")
        o4.kill(); o4.wait()
        before = len(open(pool + "/rescues.jsonl").readlines())
        r = create("a6", owner())
        check(r.returncode == 0 and r.stdout.strip() == s0 and
              len(open(pool + "/rescues.jsonl").readlines()) == before,
              "rebased-landed slot recycles clean (refs/landed), no rescue")
        # finished subagent under a LIVE owner session (WorktreeRemove never fires — MEASURED)
        tp = root + "/parent.jsonl"
        open(tp, "w").write(json.dumps({"type": "user", "toolUseResult": {
            "status": "completed", "agentId": "abc123", "worktreePath": s0}}) + "\n")
        lk = lock(0); lk.update(name="agent-abc123", transcript_path=tp)
        json.dump(lk, open("%s/bench/slot0.lock" % pool, "w"))
        open(s0 + "/scratch.txt", "w").write("unsubmitted\n")
        r = create("a6x", owner())
        check(r.returncode == 1 and "finished but holds unlanded work" in r.stderr,
              "finished subagent with dirty slot stays held while its session lives")
        os.remove(s0 + "/scratch.txt")
        r = create("a6b", owner())
        check(r.returncode == 0 and r.stdout.strip() == s0,
              "finished subagent with clean landed slot is reused while its session lives")
        # already-landed submission: only cleanup
        sh(clone, "git", "push", "-q", "origin", "refs/remotes/origin/main:refs/heads/submit/bench/old")
        land = sh(clone, sys.executable, LAND, env=env, ok=False)
        check("already on origin/main" in land.stdout and "submit/bench/old" not in
              sh(clone, "git", "ls-remote", remote).stdout, "already-landed submit ref just deleted")
        # conflict: refused, ref kept
        open(s0 + "/a.txt", "w").write("slot side\n")
        sh(s0, "git", "commit", "-qam", "slot a"); sh(s0, "git", "push", "-q", "origin", "HEAD:refs/heads/submit/bench/a6")
        sh(seed, "git", "pull", "-q", "--rebase", "origin", "main", env=env)
        open(seed + "/a.txt", "w").write("main side\n")
        sh(seed, "git", "commit", "-qam", "main a", env=env); sh(seed, "git", "push", "-q", "origin", "HEAD:main", env=env)
        land = sh(clone, sys.executable, LAND, env=env, ok=False)
        check(land.returncode == 1 and "CONFLICT a6" in land.stderr and "submit/bench/a6" in
              sh(clone, "git", "ls-remote", remote).stdout, "conflicting submission refused, ref kept")

        # --- remove: dirty slot kept, clean landed slot released
        open(s0 + "/e.txt", "w").write("local only\n")
        sh(s0, "git", "add", "e.txt"); sh(s0, "git", "commit", "-qm", "unsubmitted")
        rm = sh(clone, sys.executable, POOL, "remove", env=env, input=json.dumps({"worktree_path": s0}))
        check(rm.returncode == 0 and not lock(0).get("released"), "remove keeps an unlanded slot")
        sh(s0, "git", "reset", "-q", "--hard", "refs/remotes/origin/main")
        rm = sh(clone, sys.executable, POOL, "remove", env=env, input=json.dumps({"worktree_path": s0}))
        check(lock(0).get("released") and "locked" not in
              sh(clone, "git", "worktree", "list", "--porcelain").stdout.split(s0)[1].split("worktree ")[0],
              "remove releases a clean landed slot and unlocks it")
        st = sh(clone, sys.executable, POOL, "status", env=env).stdout
        check("slot0" in st and "slot1" in st and "BUSY" in st, "status lists both slots")
    finally:
        for p in owners:
            try:
                p.kill(); p.wait()
            except Exception:
                pass
    if not FAILS:
        shutil.rmtree(root, ignore_errors=True)
    print("%s: %d failure(s)%s" % ("OK" if not FAILS else "FAILED", len(FAILS),
                                   "" if not FAILS else " — kept " + root))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
