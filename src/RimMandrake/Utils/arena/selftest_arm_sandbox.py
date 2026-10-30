#!/usr/bin/env python3
"""selftest_arm_sandbox: the arm sandbox (arm_sandbox.py) really hides the answer from every arm launch.

Item ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE. Each check launches REAL sandboxed processes (bubblewrap):
  S1  DENY covers arena_replay.sandbox_masks() (itself derived from arena_tasks.old_history_repos), the retired-trees
      root, the ClaudeWork root and ~/.claude transcripts; binds that overlap DENY (equal, ancestor, inside) are refused.
  S2  the seccomp program is well formed (x86_64 arch check first, every jump in range, ends in RET).
  S3  fail CLOSED: no bwrap, a foreign machine, HOME/cwd outside the rw dirs, a weakened sandbox at preflight.
  S4  the full attack probe (cat / ls / git -C / git --git-dir / for-each-ref / grep -r / python open / symlink /
      /proc/*/root / Windows PE) finds nothing, while the clone, scratch and tools work and the clone lacks the fix.
  S5  mutation: each protection removed -> the probe sees a leak AND the preflight refuses the launch.
  S6  every launch site (ralph_a build/test, ralph_c build/test, trio build/simplify, v3 build/test) runs its model
      sandboxed: the harness repos, retired trees, D:\\ mirror, ClaudeWork and transcripts are invisible and
      `git for-each-ref refs/arena/old/` in a retired tree fails (harness-side it lists refs); with no bwrap every one
      is refused before anything starts.
  S7  static: subprocess.Popen of a model happens only inside RA.CmdModel.spawn (the one sandboxed choke point).
"""
from __future__ import annotations

import glob
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arm_sandbox as AS  # noqa: E402
import arena_replay as R  # noqa: E402

FAILS: list[str] = []
RETIRED = "/home/mandrake/rm/retired-trees"
MIRROR = "/mnt/d/Luke/dev/RimMandrake"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)


def retired_with_refs():
    """(retired tree, harness-side count of refs/arena/old/*) for the tree holding the most pinned fixes."""
    best = (None, 0)
    for d in sorted(glob.glob(os.path.join(RETIRED, "*-git-*"))):
        n = len(git("-C", d, "for-each-ref", "refs/arena/old/").stdout.splitlines())
        if n > best[1]:
            best = (d, n)
    return best


def mk_clone(tmp, name):
    c = tmp / name
    c.mkdir()
    git("init", "-q", str(c))
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    tree = subprocess.run(["git", "-C", str(c), "write-tree"], capture_output=True, text=True, env=env).stdout.strip()
    sha = subprocess.run(["git", "-C", str(c), "commit-tree", tree, "-m", "base"], capture_output=True, text=True,
                         env=env).stdout.strip()
    git("-C", str(c), "update-ref", "refs/heads/master", sha)
    return c


# ------------------------------------------------------------------------------------------------ S1
def s1_deny():
    deny = AS.deny_paths()
    masks = [AS._real(m) for m in R.sandbox_masks()]
    check(all(m in deny for m in masks), "S1 DENY includes every arena_replay.sandbox_masks() entry (%d)" % len(masks))
    import arena_tasks as T
    old = [AS._real(str(p)) for p in T.old_history_repos()]
    check(old and all(any(AS._under(o, d) for d in deny) for o in old),
          "S1 every old_history_repos() entry (%d) is under DENY" % len(old))
    for p in (RETIRED, AS.CLAUDEWORK, str(Path.home() / ".claude" / "projects"), "/home/mandrake/rm/bench",
              "/home/mandrake/rm/foundry", MIRROR):
        check(AS._real(p) in deny, "S1 DENY holds %s" % p)
    refused = []
    for p in ("/home/mandrake/rm/bench", "/home/mandrake/rm/foundry", "/home/mandrake/rm", "/home/mandrake",
              "/", RETIRED + "/x", AS.CLAUDEWORK + "/foundry_arena", str(Path.home() / ".claude" / "projects" / "a"),
              "/mnt/d/Luke", "/mnt/d"):
        try:
            AS.check_bind(p, deny, "rw")
        except AS.SandboxRefused:
            refused.append(p)
    check(len(refused) == 10, "S1 check_bind refuses binds equal to / above / inside DENY (%d/10)" % len(refused))
    t = tempfile.mkdtemp(prefix="asb_ok_")
    try:
        AS.check_bind(t, deny, "rw")
        check(True, "S1 check_bind accepts a plain temp dir")
    except AS.SandboxRefused as e:
        check(False, "S1 check_bind accepts a plain temp dir (%s)" % e)
    finally:
        os.rmdir(t)


# ------------------------------------------------------------------------------------------------ S2
def s2_seccomp():
    ins = AS._resolve()
    prog = AS.seccomp_program()
    ok = (len(prog) == 8 * len(ins) and ins[0] == (0x20, 0, 0, 4) and ins[1][3] == 0xC000003E
          and ins[-1][0] == 0x06 and all(i[0] != 0x15 or i[1] + i[2] < len(ins) for i in ins))
    targets_ok = all(0 <= n + 1 + max(i[1], i[2]) < len(ins) for n, i in enumerate(ins) if i[0] in (0x15, 0x35))
    check(ok and targets_ok, "S2 seccomp program: arch check first, ends in RET, every jump lands inside")


# ------------------------------------------------------------------------------------------------ S3
def refused(fn):
    try:
        fn()
        return False
    except AS.SandboxRefused:
        return True


def s3_fail_closed(tmp):
    d = tmp / "fc"
    (d / "home").mkdir(parents=True)
    other = tmp / "elsewhere"
    other.mkdir()
    w = lambda **k: AS.wrap(["true"], dict(os.environ), **{"cwd": d, "rw": [d], "home": d / "home", **k})  # noqa
    bw = AS.BWRAP
    AS.BWRAP = str(tmp / "no-bwrap")
    try:
        check(refused(w), "S3 no bwrap -> refused")
    finally:
        AS.BWRAP = bw
    m = platform.machine
    platform.machine = lambda: "aarch64"
    try:
        check(refused(w), "S3 a non-x86_64 machine (seccomp is x86_64-only) -> refused")
    finally:
        platform.machine = m
    check(refused(lambda: w(home=other / "home")), "S3 private HOME outside the rw dirs -> refused")
    check(refused(lambda: w(cwd=other)), "S3 cwd outside the rw dirs -> refused")
    check(refused(lambda: w(rw=["/home/mandrake/rm/foundry"], cwd="/home/mandrake/rm/foundry",
                            home="/home/mandrake/rm/foundry")), "S3 the harness repo as rw -> refused")
    check(refused(lambda: w(_drop=("/home",))), "S3 preflight on a weakened sandbox (/home unmasked) -> refused")
    try:
        argv, env = w()
        r = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=60)
        check(r.returncode == 0 and env["HOME"] == str(d / "home") and "WSL_INTEROP" not in env,
              "S3 an honest launch is allowed (rc %s, private HOME, no WSL_INTEROP)" % r.returncode)
    except AS.SandboxRefused as e:
        check(False, "S3 an honest launch is allowed (%s)" % e)


# ------------------------------------------------------------------------------------------------ S4 / S5
def fixture(tmp):
    clone = mk_clone(tmp, "clone")
    scratch = tmp / "scratch"
    scratch.mkdir()
    pe = []
    who = "/mnt/c/Windows/System32/whoami.exe"
    if os.path.exists(who):
        shutil.copy(who, scratch / "w.exe")
        os.chmod(scratch / "w.exe", 0o755)
        pe = [str(scratch / "w.exe")]
    head = git("-C", str(HERE), "rev-parse", "HEAD").stdout.strip()
    return clone, scratch, pe, [head]


def s4_full(tmp):
    clone, scratch, pe, absent = fixture(tmp)
    res = AS.probe(clone=str(clone), scratch=str(scratch), absent=absent, pe=pe,
                   tools=[["git", "--version"], [AS.PY, "--version"]])
    att = res["info"].get("attempts", 0)
    check(res["n_masked"] > 40 and att > 1000, "S4 the probe can see: %d masked paths, %d attempts"
          % (res["n_masked"], att))
    check(not res["leaks"], "S4 full attack probe: no leak (%s)" % json.dumps(res["leaks"])[:400])
    check(not res["fails"], "S4 clone/scratch/tools work, clone lacks the harness HEAD (%s)"
          % json.dumps(res["fails"])[:400])
    check(bool(pe), "S4 a Windows PE was offered to the interop attack (whoami.exe present)")
    return clone, scratch, pe, absent


def s5_mutations(tmp, clone, scratch, pe, absent):
    for m in AS.MUTATIONS:
        res = AS.probe(clone=str(clone), scratch=str(scratch), absent=absent, pe=pe, _drop=(m,), full=False)
        check(len(res["leaks"]) > 0, "S5 mutation drop %-8s -> the probe sees %d leak(s)" % (m, len(res["leaks"])))
        d = tmp / ("mut" + re.sub(r"\W", "_", m))
        (d / "home").mkdir(parents=True)
        check(refused(lambda: AS.wrap(["true"], dict(os.environ), cwd=d, rw=[d], home=d / "home", _drop=(m,))),
              "S5 mutation drop %-8s -> preflight refuses the launch" % m)
    if pe:   # all three interop layers off: the PE really runs (the instrument can see interop)
        res = AS.probe(clone=str(clone), scratch=str(scratch), pe=pe, _drop=("/run", "env", "seccomp"))
        ran = [lk for lk in res["leaks"] if lk[0] == "interop exec"]
        check(bool(ran), "S5 /run+env+seccomp dropped -> the Windows PE runs (sanity: interop is observable)")


# ------------------------------------------------------------------------------------------------ S6
ARM_PROBE = r'''
import json, os, subprocess, sys
sys.stdin.read()
a = json.loads(sys.argv[1])
seen = [p for p in a["hidden"] if os.path.lexists(p)]
r = subprocess.run(["git", "-C", a["retired"], "for-each-ref", "refs/arena/old/"], capture_output=True, text=True)
refs = len(r.stdout.splitlines()) if r.returncode == 0 else -1
open(os.path.join(os.environ["HOME"], "w"), "w").write("x")
print(json.dumps({"seen": seen, "refs": refs, "home": os.environ["HOME"], "interop": "WSL_INTEROP" in os.environ}))
'''


def s6_launch_sites(tmp):
    import ralph_a_loop as RA
    import ralph_c_loop as RC
    import trio_loop as TL
    import v3_control as V3
    retired, n = retired_with_refs()
    check(n > 0, "S6 sanity: harness-side a retired tree lists %d refs/arena/old/ refs (%s)" % (n, retired))
    hidden = ["/home/mandrake/rm/bench", "/home/mandrake/rm/foundry", RETIRED, MIRROR, AS.CLAUDEWORK,
              str(Path.home() / ".claude" / "projects"), str(Path.home() / ".codex")]
    sanity = [p for p in hidden if os.path.exists(p)]
    check(len(sanity) >= 5, "S6 sanity: %d of the hidden paths exist harness-side" % len(sanity))
    pb = tmp / "probebin"            # bound read-only into every arm sandbox via RM_ARM_SANDBOX_RO
    pb.mkdir()
    script = pb / "armprobe.py"
    script.write_text(ARM_PROBE)
    os.environ["RM_ARM_SANDBOX_RO"] = str(pb)
    arg = json.dumps({"hidden": hidden, "retired": retired or RETIRED})
    cmd = "%s -I %s %s" % (AS.PY, script, shlex_quote(arg))
    sites = [("ralph_a", RA.CmdModel(cmd), ("build", "test")), ("ralph_c", RC.CmdModelC(cmd, "m1"), ("build", "test")),
             ("trio", TL.CmdModelT(cmd), ("build", "simplify")), ("v3", V3.CmdModel(cmd, "v3x"), ("build", "test"))]
    for name, m, roles in sites:
        for role in roles:
            d = tmp / ("site_%s_%s" % (name, role))
            clone = mk_clone(d.parent, d.name)
            root = tmp / ("troot_%s_%s" % (name, role))
            root.mkdir()
            log = tmp / ("%s_%s.out" % (name, role))
            sb = {"root": root} if role == "test" else None
            try:
                r = m(role, "P", cwd=clone if role != "test" else root, agent_id="x-%s-1" % role, run_id=0,
                      timeout_s=120, log=log, sandbox=sb)
                res = json.loads(r["text"].strip().splitlines()[-1])
            except Exception as e:  # noqa: BLE001
                check(False, "S6 %s %s launch probe crashed: %s: %s %r" % (name, role, type(e).__name__, e,
                                                                         log.read_text()[-300:] if log.exists() else ""))
                continue
            ok = (r["rc"] == 0 and res["seen"] == [] and res["refs"] == -1 and not res["interop"]
                  and res["home"] != str(Path.home()))
            check(ok, "S6 %s %-8s sandboxed: hidden paths invisible, for-each-ref refs/arena/old/ fails, private "
                      "HOME (%s)" % (name, role, res))
        with NoBwrap():
            for role in roles:
                d = tmp / ("nb_%s_%s" % (name, role))
                d.mkdir()
                log = d / "out"
                try:
                    m(role, "P", cwd=d, agent_id="x-%s-1" % role, run_id=0, timeout_s=30, log=log,
                      sandbox={"root": d})
                    check(False, "S6 %s %s with no bwrap is refused" % (name, role))
                except RA.Refused:
                    check(not log.exists(), "S6 %s %-8s with no bwrap is refused before anything starts" % (name, role))


class NoBwrap:
    def __enter__(self):
        self.bw = AS.BWRAP
        AS.BWRAP = "/nonexistent/bwrap"

    def __exit__(self, *a):
        AS.BWRAP = self.bw


def shlex_quote(s):
    import shlex
    return shlex.quote(s)


# ------------------------------------------------------------------------------------------------ S7
def s7_static():
    bad = []
    for f in ("ralph_a_loop.py", "ralph_c_loop.py", "trio_loop.py", "v3_control.py", "ralph_c_runner.py"):
        p = HERE / f
        if not p.exists():
            continue
        src = p.read_text()
        for m in re.finditer(r"subprocess\.Popen\(", src):
            line = src.count("\n", 0, m.start()) + 1
            fn = [x for x in re.finditer(r"^\s*def (\w+)", src[:m.start()], re.M)]
            where = fn[-1].group(1) if fn else "?"
            if not (f == "ralph_a_loop.py" and where == "spawn"):
                bad.append("%s:%d in %s" % (f, line, where))
    sp = (HERE / "ralph_a_loop.py").read_text()
    body = sp[sp.index("    def spawn("):sp.index("    def __call__(", sp.index("    def spawn("))]
    check("self.wrap(" in body and body.index("self.wrap(") < body.index("subprocess.Popen("),
          "S7 RA.CmdModel.spawn wraps before it Popens")
    check(not bad, "S7 no other model Popen in the arm loops (%s)" % bad)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_arm_sandbox_"))
    os.environ["RM_ARM_SANDBOX_SCRATCH"] = str(tmp / "armscratch")
    try:
        for fn, a in ((s1_deny, ()), (s2_seccomp, ()), (s3_fail_closed, (tmp,)), (s7_static, ())):
            try:
                fn(*a)
            except Exception as e:  # noqa: BLE001
                check(False, "%s crashed: %s: %s" % (fn.__name__, type(e).__name__, e))
        try:
            fx = s4_full(tmp)
            s5_mutations(tmp, *fx)
        except Exception as e:  # noqa: BLE001
            check(False, "s4/s5 crashed: %s: %s" % (type(e).__name__, e))
        try:
            s6_launch_sites(tmp)
        except Exception as e:  # noqa: BLE001
            check(False, "s6 crashed: %s: %s" % (type(e).__name__, e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
