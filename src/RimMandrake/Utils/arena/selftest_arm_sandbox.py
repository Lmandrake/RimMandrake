#!/usr/bin/env python3
"""selftest_arm_sandbox: the arm sandbox (arm_sandbox.py) really hides the answer from every arm launch.

Item ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE. Each check launches REAL sandboxed processes (bubblewrap):
  S1  DENY covers arena_replay.sandbox_masks() (itself derived from arena_tasks.old_history_repos), the retired-trees
      root, the ClaudeWork root and ~/.claude transcripts; binds that overlap DENY (equal, ancestor, inside) are refused.
  S2  the seccomp program is well formed (x86_64 arch check first, every jump in range, ends in RET).
  S3  fail CLOSED: no bwrap, a foreign machine, HOME/cwd outside the rw dirs, a weakened sandbox at preflight.
  S4  the full attack probe (cat / ls / git -C / git --git-dir / for-each-ref / grep -r / python open / symlink /
      /proc/*/root / Windows PE) finds nothing, while the clone, scratch and tools work and the clone lacks the fix.
  S5  mutation: each protection removed (incl. the /var/log mask and the env allow-list) -> the probe sees a leak AND
      the preflight refuses the launch.
  S1+ a new OLD_HISTORY_DEFAULT / $ARENA_OLD_HISTORY entry is masked with no edit (drift guard).
  S6  every launch site (ralph_a build/test, ralph_c build/test, trio build/simplify, v3 build/test) runs its model
      sandboxed: the harness repos, retired trees, D:\\ mirror, ClaudeWork and transcripts are invisible and
      `git for-each-ref refs/arena/old/` in a retired tree fails (harness-side it lists refs); with no bwrap every one
      is refused before anything starts.
  S7  static: subprocess.Popen of a model happens only inside RA.CmdModel.spawn (the one sandboxed choke point).
  S8  network (ARENA_SANDBOX_HARDEN_LOOPBACK_STILL_OPEN, ARENA_SANDBOX_HARDEN_GITHUB_PUBLIC_FETCH): two host loopback
      servers stand in for the model API (allow-listed) and RimPulse (not); harness-side both answer (control).
      Inside wrap(net="model") only lo exists, neither is reachable directly, CONNECT to the API answers through the
      relay, CONNECT to the RimPulse stand-in / github.com is 403, and `git ls-remote` of the public repo fails;
      net="none" reaches nothing at all. The live RimPulse port and the REAL allow-list (a TLS handshake with the
      model API through the relay) are checked when harness-side they work.
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
    # drift guard: a NEW old-history entry (default list or $ARENA_OLD_HISTORY), anywhere, is masked with no edit here
    nd = tempfile.mkdtemp(prefix="asb_oldhist_")
    os.makedirs(os.path.join(nd, "new-git-1"))
    saved_def, saved_env = T.OLD_HISTORY_DEFAULT, os.environ.get("ARENA_OLD_HISTORY")
    try:
        T.OLD_HISTORY_DEFAULT = saved_def + (os.path.join(nd, "*-git-*"),)
        d2 = AS.deny_paths()
        check(AS._real(nd) in d2 and AS._real(os.path.join(nd, "new-git-1")) in d2,
              "S1 a new OLD_HISTORY_DEFAULT entry is masked (its glob root and the repo it matches)")
        T.OLD_HISTORY_DEFAULT = saved_def
        os.environ["ARENA_OLD_HISTORY"] = os.path.join(nd, "*-git-*")
        d3 = AS.deny_paths()
        check(AS._real(nd) in d3, "S1 an $ARENA_OLD_HISTORY glob root is masked")
        check(AS._real(nd) not in deny, "S1 sanity: the scratch old-history root was not masked before")
    finally:
        T.OLD_HISTORY_DEFAULT = saved_def
        if saved_env is None:
            os.environ.pop("ARENA_OLD_HISTORY", None)
        else:
            os.environ["ARENA_OLD_HISTORY"] = saved_env
        shutil.rmtree(nd, ignore_errors=True)
    for p in (RETIRED, AS.CLAUDEWORK, str(Path.home() / ".claude" / "projects"), "/home/mandrake/rm/bench",
              "/home/mandrake/rm/foundry", MIRROR):
        check(AS._real(p) in deny, "S1 DENY holds %s" % p)
    nref = []
    for p in ("/home/mandrake/rm/bench", "/home/mandrake/rm/foundry", "/home/mandrake/rm", "/home/mandrake",
              "/", RETIRED + "/x", AS.CLAUDEWORK + "/foundry_arena", str(Path.home() / ".claude" / "projects" / "a"),
              "/mnt/d/Luke", "/mnt/d"):
        try:
            AS.check_bind(p, deny, "rw")
        except AS.SandboxRefused:
            nref.append(p)
    check(len(nref) == 10, "S1 check_bind refuses binds equal to / above / inside DENY (%d/10)" % len(nref))
    for p in ("/mnt/d/Luke/dev/rimmandrake", "/mnt/D/Luke/dev/RimMandrake", "/mnt/c/Users"):
        check(refused(lambda: AS.check_bind(p, deny, "ro")),
              "S1 GPT r1: a Windows-filesystem bind (case alias of the mirror) is refused: %s" % p)
    t = tempfile.mkdtemp(prefix="asb_ok_")
    real_m = AS._mounts
    AS._mounts = lambda: real_m() + [(os.path.join(t, "sub"), "ext4")]
    try:
        check(refused(lambda: AS.check_bind(t, deny, "rw")), "S1 GPT r1: a bind with a mount inside it is refused")
    finally:
        AS._mounts = real_m
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


def s3_scratch_fresh(tmp):
    """GPT r1: a rebuilt clone (new .git) gets a fresh scratch HOME; an arm-written marker never steers the path."""
    c = mk_clone(tmp, "sfc")
    a = AS.scratch_dir(c, "build")
    (a / "home").mkdir(parents=True, exist_ok=True)
    (a / "home" / "old_transcript").write_text("x")
    check(AS.scratch_dir(c, "build") == a, "S3 the same clone keeps its scratch across passes")
    shutil.rmtree(c)
    c = mk_clone(tmp, "sfc")
    b = AS.scratch_dir(c, "build")
    check(b != a and not (b / "home" / "old_transcript").exists(), "S3 a rebuilt clone gets a fresh scratch")
    (c / ".git" / "arm_sandbox_id").write_text("../../../../etc\n")
    d = AS.scratch_dir(c, "build")
    base = Path(os.environ["RM_ARM_SANDBOX_SCRATCH"]).resolve()
    check(d.resolve().parent.parent == base and d != b, "S3 a junk marker is replaced, the scratch stays under base")
    sentinel = tmp / "sentinel_outside"
    sentinel.write_text("SECRET")
    mk = c / ".git" / "arm_sandbox_id"
    mk.unlink()
    mk.symlink_to(sentinel)
    e = AS.scratch_dir(c, "build")
    check(sentinel.read_text() == "SECRET" and not mk.is_symlink() and e != d,
          "S3 GPT r2: a planted marker symlink is replaced, its target untouched")
    hd = e / "home"
    hd.mkdir(exist_ok=True)
    (hd / ".claude.json").unlink(missing_ok=True)
    (hd / ".claude.json").symlink_to(sentinel)
    AS._seed_home(str(hd))
    check(sentinel.read_text() == "SECRET", "S3 GPT r2: seeding HOME never writes through a planted .claude.json link")
    w = tmp / "sfw"
    w.mkdir()
    (w / ".git").write_text("gitdir: /home/mandrake/rm/foundry/.git\n")
    check(refused(lambda: AS.scratch_dir(w, "build")), "S3 GPT r2: a worktree-style .git file is refused")
    n = tmp / "sfn"
    n.mkdir()
    f1 = AS.scratch_dir(n, "build")
    shutil.rmtree(n)
    n.mkdir()
    check(AS.scratch_dir(n, "build") != f1, "S3 GPT r2: a recreated non-git workspace gets a fresh scratch")
    mi = tmp / "mountinfo"
    mi.write_text(open("/proc/self/mountinfo").read() + "999 1 8:1 /home/mandrake/rm/foundry /usr/share/alias rw - "
                  "ext4 /dev/sdc rw\n")
    check(refused(lambda: AS.check_mounts(str(mi))), "S3 GPT r2: an inherited subtree bind outside the masked "
          "containers (alias of a masked tree) is refused")
    check(not refused(AS.check_mounts), "S3 this machine's own mounts pass check_mounts")
    check("/bin/rm -f" in " ".join(AS.bwrap_argv({"drop": set(), "files": [], "tools": [], "rw": [], "seeds": [],
                                                  "cwd": "/"}, "/x.bpf")),
          "S3 GPT r1: the pre-bwrap shell uses an absolute /bin/rm (no PATH lookup)")


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
    os.environ["ARM_SB_CANARY"] = "x"        # the env mutation must show even under a minimal launcher env
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
    os.environ.pop("ARM_SB_CANARY", None)


# ------------------------------------------------------------------------------------------------ S6
ARM_PROBE = r'''
import json, os, subprocess, sys
sys.stdin.read()
a = json.loads(sys.argv[1])
seen = [p for p in a["hidden"] if os.path.lexists(p)]
r = subprocess.run(["git", "-C", a["retired"], "for-each-ref", "refs/arena/old/"], capture_output=True, text=True)
refs = len(r.stdout.splitlines()) if r.returncode == 0 else -1
open(os.path.join(os.environ["HOME"], "w"), "w").write("x")
jr = subprocess.run(["journalctl", "-q", "--no-pager", "-n", "1", "-D", "/var/log/journal"], capture_output=True,
                    text=True) if os.path.exists("/usr/bin/journalctl") else None
print(json.dumps({"seen": seen, "refs": refs, "home": os.environ["HOME"], "interop": "WSL_INTEROP" in os.environ,
                  "env": sorted(os.environ), "journal": bool(jr and jr.returncode == 0 and jr.stdout.strip())}))
'''


def s6_launch_sites(tmp):
    import ralph_a_loop as RA
    import ralph_c_loop as RC
    import trio_loop as TL
    import v3_control as V3
    retired, n = retired_with_refs()
    check(n > 0, "S6 sanity: harness-side a retired tree lists %d refs/arena/old/ refs (%s)" % (n, retired))
    hidden = ["/home/mandrake/rm/bench", "/home/mandrake/rm/foundry", RETIRED, MIRROR, AS.CLAUDEWORK,
              str(Path.home() / ".claude" / "projects"), str(Path.home() / ".codex"), "/var/log/syslog",
              "/var/log/journal"]
    sanity = [p for p in hidden if os.path.exists(p)]
    check(len(sanity) >= 5, "S6 sanity: %d of the hidden paths exist harness-side" % len(sanity))
    check(os.access("/var/log/syslog", os.R_OK), "S6 sanity: harness-side /var/log/syslog is readable (the leak)")
    jr = subprocess.run(["journalctl", "-q", "--no-pager", "-n", "1", "-D", "/var/log/journal"], capture_output=True,
                        text=True)
    host_journal = jr.returncode == 0 and bool(jr.stdout.strip())
    print("info  S6 harness-side journalctl -D /var/log/journal reads: %s" % host_journal)
    canary = {"AGENT_SEAT": "BENCH", "CLAUDE_CODE_MESSAGING_TOKEN": "canary-msg", "CLAUDE_CODE_SESSION_ID": "canary-s",
              "GH_TOKEN": "canary-gh", "OPENAI_API_KEY": "canary-oa", "ARM_SB_CANARY": "x", "ARM_SB_KEPT_NAME": "k"}
    saved = {k: os.environ.get(k) for k in list(canary) + list(AS.ENV_KEEP_VARS)}
    os.environ.update(canary, **{v: "ARM_SB_KEPT_NAME" for v in AS.ENV_KEEP_VARS})   # builder keep / tester keep
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
                  and res["home"] != str(Path.home()) and not res["journal"])
            check(ok, "S6 %s %-8s sandboxed: hidden paths + syslog/journal invisible, for-each-ref refs/arena/old/ "
                      "fails, private HOME (%s)" % (name, role, {k: v for k, v in res.items() if k != "env"}))
            env = set(res["env"])
            leaked = sorted(env & (set(canary) - {"ARM_SB_KEPT_NAME"}))
            tag = "TESTER_ID" if role == "test" else ("V3_ROLE" if name == "v3" else "RALPH_A_ROLE")
            check(not leaked and "ARM_SB_KEPT_NAME" in env and tag in env and "PATH" in env,
                  "S6 %s %-8s env is the allow-list: no seat/session/messaging/GH/OpenAI canary (%s), the operator "
                  "keep and the harness tag %s cross%s" % (name, role, leaked, tag, "" if "ARM_SB_KEPT_NAME" in env and tag in env
                                                         else " (got %s)" % sorted(env)))
            stray = sorted(k for k in env if not AS.env_ok(k, AS.env_keep("model") | AS.ENV_SET | BRIDGE_SET))
            check(not stray, "S6 %s %-8s no env name outside the allow-list (%s)" % (name, role, stray))
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
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


BRIDGE_SET = {"HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"}


class NoBwrap:
    def __enter__(self):
        self.bw = AS.BWRAP
        AS.BWRAP = "/nonexistent/bwrap"

    def __exit__(self, *a):
        AS.BWRAP = self.bw


def shlex_quote(s):
    import shlex
    return shlex.quote(s)


# ------------------------------------------------------------------------------------------------ S8
NET_PROBE = r'''
import json, os, socket, ssl, subprocess, sys
sys.stdin.read()
a = json.loads(sys.argv[1])
out = {"nics": sorted(n for _, n in socket.if_nameindex()), "direct": {}, "connect": {}, "tls": {}}
def direct(port):
    try:
        s = socket.create_connection(("127.0.0.1", port), 3)
        s.settimeout(3)
        d = s.recv(64).decode("latin-1")
        s.close()
        return "OPEN " + d
    except OSError as e:
        return "closed " + type(e).__name__
proxy = os.environ.get("HTTPS_PROXY", "")
def connect(target):
    if not proxy:
        return None, "no proxy"
    host, port = proxy.rsplit("/", 1)[-1].rsplit(":", 1)
    s = socket.create_connection((host, int(port)), 5)
    s.settimeout(15)
    s.sendall(("CONNECT %s HTTP/1.1\r\nHost: %s\r\n\r\n" % (target, target)).encode())
    head = b""
    while b"\r\n\r\n" not in head:
        d = s.recv(4096)
        if not d:
            break
        head += d
    return s, head.split(b"\r\n", 1)[0].decode("latin-1")
for name, port in a["ports"].items():
    out["direct"][name] = direct(port)
for name, target in a["targets"].items():
    try:
        s, status = connect(target)
        body = ""
        if s is not None and " 200 " in status + " ":
            body = s.recv(64).decode("latin-1")
        if s is not None:
            s.close()
        out["connect"][name] = [status, body]
    except OSError as e:
        out["connect"][name] = ["error " + type(e).__name__, ""]
for target in a.get("tls", []):
    try:
        s, status = connect(target)
        if s is None or " 200 " not in status + " ":
            out["tls"][target] = "refused: " + status
            continue
        host = target.rsplit(":", 1)[0]
        t = ssl.create_default_context().wrap_socket(s, server_hostname=host)
        out["tls"][target] = "ok " + str(t.version())
        t.close()
    except (OSError, ssl.SSLError) as e:
        out["tls"][target] = "error %s: %s" % (type(e).__name__, str(e)[:80])
r = subprocess.run(["git", "ls-remote", a["repo"], "HEAD"], capture_output=True, text=True, timeout=60,
                   stdin=subprocess.DEVNULL)
out["git"] = [r.returncode, (r.stdout + r.stderr).strip()[-160:]]
out["proxy"] = bool(proxy)
print("NETPROBE " + json.dumps(out))
'''
PUBLIC_REPO = "https://github.com/Lmandrake/RimMandrake.git"
RIMPULSE_PORT = 8765


def _server(reply: bytes):
    import socket
    import threading
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(16)

    def serve():
        while True:
            try:
                c, _ = srv.accept()
            except OSError:
                return
            try:
                c.sendall(reply)
            except OSError:
                pass
            c.close()
    threading.Thread(target=serve, daemon=True).start()
    return srv, srv.getsockname()[1]


def _direct(port):
    import socket
    try:
        s = socket.create_connection(("127.0.0.1", port), 3)
        s.settimeout(3)
        d = s.recv(64)
        s.close()
        return "OPEN " + d.decode("latin-1")
    except OSError as e:
        return "closed " + type(e).__name__


def _tls_host(target):
    import socket
    import ssl
    host, port = target.rsplit(":", 1)
    try:
        with socket.create_connection((host, int(port)), 10) as s:
            with ssl.create_default_context().wrap_socket(s, server_hostname=host):
                return True
    except (OSError, ssl.SSLError):
        return False


def _netprobe(tmp, name, net, arg):
    d = tmp / ("net_" + name)
    (d / "home").mkdir(parents=True)
    pb = tmp / "netbin"
    pb.mkdir(exist_ok=True)
    (pb / "netprobe.py").write_text(NET_PROBE)
    old = os.environ.get("RM_ARM_SANDBOX_RO")
    os.environ["RM_ARM_SANDBOX_RO"] = str(pb)
    try:
        argv, env = AS.wrap([AS.PY, "-I", str(pb / "netprobe.py"), json.dumps(arg)], dict(os.environ), cwd=d,
                            rw=[d], home=d / "home", net=net)
    finally:
        if old is None:
            os.environ.pop("RM_ARM_SANDBOX_RO", None)
        else:
            os.environ["RM_ARM_SANDBOX_RO"] = old
    r = subprocess.run(argv, env=env, cwd=str(d), input="", capture_output=True, text=True, timeout=180)
    for line in r.stdout.splitlines():
        if line.startswith("NETPROBE "):
            return json.loads(line[len("NETPROBE "):])
    raise RuntimeError("netprobe %s did not report (rc %s): %s" % (name, r.returncode, (r.stdout + r.stderr)[-400:]))


def s8_network(tmp):
    import arena_critic_relay as RELAY
    api, api_port = _server(b"API-OK")
    pulse, pulse_port = _server(b"SECRET-LEDGER")
    try:
        check(_direct(api_port).startswith("OPEN API-OK") and _direct(pulse_port).startswith("OPEN SECRET"),
              "S8 control: harness-side both loopback stand-ins answer")
        real_allow = None
        try:
            saved = os.environ.pop(RELAY.ALLOW_ENV, None)
            real_allow = sorted(RELAY.allow_list())
        except RELAY.RelayRefused:
            pass
        finally:
            if saved is not None:
                os.environ[RELAY.ALLOW_ENV] = saved
        os.environ[RELAY.ALLOW_ENV] = "127.0.0.1:%d" % api_port
        arg = {"ports": {"api": api_port, "pulse": pulse_port, "rimpulse": RIMPULSE_PORT},
               "targets": {"api": "127.0.0.1:%d" % api_port, "pulse": "127.0.0.1:%d" % pulse_port,
                           "github": "github.com:443"}, "repo": PUBLIC_REPO}
        m = _netprobe(tmp, "model", "model", arg)
        check(m["nics"] == ["lo"], "S8 model: own network namespace, lo only (%s)" % m["nics"])
        check(all(v.startswith("closed") for v in m["direct"].values()),
              "S8 model: no host loopback port reachable directly (%s)" % m["direct"])
        check(m["proxy"] and m["connect"]["api"] == ["HTTP/1.1 200 Connection Established", "API-OK"],
              "S8 model: CONNECT to the allow-listed API answers through the relay (%s)" % m["connect"]["api"])
        check(m["connect"]["pulse"][0].startswith("HTTP/1.1 403") and m["connect"]["github"][0].startswith(
            "HTTP/1.1 403"), "S8 model: CONNECT to the RimPulse stand-in and github.com is 403 (%s)" % m["connect"])
        check(m["git"][0] != 0, "S8 model: git ls-remote of the public repo fails (%s)" % m["git"])
        rel = RELAY.relay(AS.relay_base())
        check("github.com:443" in rel.denied and "127.0.0.1:%d" % pulse_port in rel.denied,
              "S8 model: the relay recorded the refused targets (%s)" % rel.denied[-6:])
        n = _netprobe(tmp, "none", "none", arg)
        check(n["nics"] == ["lo"] and not n["proxy"] and all(v.startswith("closed") for v in n["direct"].values())
              and n["git"][0] != 0, "S8 none: lo only, no proxy, nothing reachable, git ls-remote fails (%s)" % n)
        if _direct(RIMPULSE_PORT).startswith("OPEN"):
            check(m["direct"]["rimpulse"].startswith("closed"),
                  "S8 live: RimPulse :%d answers harness-side, not from the sandbox" % RIMPULSE_PORT)
        else:
            print("  [unmeasured] S8 live RimPulse :%d is not up harness-side" % RIMPULSE_PORT)
        os.environ.pop(RELAY.ALLOW_ENV, None)
        keep, RELAY.ALLOW_FILE = RELAY.ALLOW_FILE, tmp / "no_allow_file"
        try:
            check(refused(lambda: _netprobe(tmp, "noallow", "model", arg)),
                  "S8 no allow-list (env unset, no file) -> the model sandbox is refused, never a shared network")
        finally:
            RELAY.ALLOW_FILE = keep
        if real_allow and not all(_tls_host(t) for t in real_allow):
            print("  [unmeasured] S8 live: harness-side TLS to the allow-listed model hosts fails (offline?)")
        elif not real_allow:
            print("  [unmeasured] S8 live: no machine allow-list configured")
        else:
            os.environ[RELAY.ALLOW_ENV] = ",".join(real_allow)
            t = _netprobe(tmp, "real", "model", dict(arg, tls=real_allow))
            check(all(v.startswith("ok") for v in t["tls"].values()),
                  "S8 live: TLS handshake with every allow-listed model host through the relay (%d hosts: %s)"
                  % (len(real_allow), sorted(set(v.split(":")[0] for v in t["tls"].values()))))
    finally:
        os.environ.pop(RELAY.ALLOW_ENV, None)
        api.close()
        pulse.close()


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
        for fn, a in ((s1_deny, ()), (s2_seccomp, ()), (s3_fail_closed, (tmp,)), (s3_scratch_fresh, (tmp,)),
                      (s7_static, ())):
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
            s8_network(tmp)
        except Exception as e:  # noqa: BLE001
            check(False, "s8 crashed: %s: %s" % (type(e).__name__, e))
        try:
            os.environ["ARENA_CRITIC_RELAY_ALLOW"] = "127.0.0.1:9"      # the launch sites need a model route
            s6_launch_sites(tmp)
        except Exception as e:  # noqa: BLE001
            check(False, "s6 crashed: %s: %s" % (type(e).__name__, e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
