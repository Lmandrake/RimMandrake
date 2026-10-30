#!/usr/bin/env python3
"""arm_sandbox: the ONE choke point every arena arm agent process (builder, tester, simplify, ...) is launched through.

WHY. An arm agent runs as our own uid. Unsandboxed it can read the ANSWER: the live clones (/home/mandrake/rm/bench,
/foundry: future history), the retired pre-rewrite clones (/home/mandrake/rm/retired-trees: every replay task's fix,
pinned under refs/arena/old/), the D:\\ mirror (/mnt/d/Luke/dev/RimMandrake), D:\\ClaudeWork notes, the arena judge
dirs, ~/.claude transcripts of the agents that wrote the fixes, shell histories, old backups. Item
ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE.

HOW (allow-list, not deny-list). bubblewrap: the root read-only, then a tmpfs over every CONTAINER (/home, /mnt, /tmp,
/var/tmp, /run, /root, /srv, /opt, /media, /usr/lib/wsl/drivers), then only what the arm needs is bound back:
  rw   the arm clone and its scratch dir (caller-given; refused when one of them is, holds or sits inside a DENY path)
  ro   the agent CLI and user python (~/.local/bin, ~/.local/share/claude, ~/.local/lib, $RM_ARM_SANDBOX_RO), the
       resolver file /etc/resolv.conf points into /mnt/wsl, and a few $HOME seeds bound into a PRIVATE home
       (default only .gitconfig; $RM_ARM_SANDBOX_HOME_RO adds home-relative paths, e.g. .claude/skills)
Own user/pid/ipc/uts namespaces, nested user namespaces disabled, a fresh /proc (no /proc/<harness pid>/root),
--new-session, --die-with-parent. A seccomp filter refuses socket(AF_VSOCK) and io_uring (the raw channel to the
Windows host). /run is a tmpfs and WSL_INTEROP is dropped: Windows interop (binfmt -> /init -> /run/WSL/*_interop) is
dead, so no codex.exe / powershell.exe / dotnet.exe can be spawned to read D:\\ from the Windows side.

FAIL CLOSED. No bwrap, a non-x86_64 kernel ABI (the seccomp program is x86_64-only), a bind that touches a DENY path,
or a PREFLIGHT that finds anything visible that must not be (run inside the very same sandbox before every launch)
-> SandboxRefused. There is no unisolated override.

RESIDUALS (stated, not solved here):
  - NETWORK is shared (the model API needs it): loopback services are reachable (RimPulse :8765 serves the ledger
    unauthenticated; the account page :8790), the Windows host's ports and the internet too. No credentials are
    visible (~/.ssh, ~/.config/gh, git credential store are under the /home tmpfs).
  - Same uid outside the sandbox: a kernel/bwrap escape is out of scope.
  - Auth: the real ~/.claude/.credentials.json is NOT bound by default (an OAuth refresh inside could rotate the
    owner's token). Give the arm CLAUDE_CODE_OAUTH_TOKEN / ANTHROPIC_API_KEY in its env, or opt in with
    RM_ARM_SANDBOX_HOME_RO=.claude/.credentials.json (read-only).
  - No Windows build/deploy from inside (dotnet.exe needs interop; /mnt/c is masked): the gate builds, not the arm.
  - Windows-side reviewers (codex.exe via gpt_consult) are not sandboxable by this module at all.

API: wrap(argv, env, cwd=, rw=, home=) -> (argv, env) for subprocess.Popen; deny_paths(); probe(...) (the attack probe,
CLI `arm_sandbox.py probe`). Selftest: selftest_arm_sandbox.py (launches real sandboxed processes, mutation-checked).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

BWRAP = "/usr/bin/bwrap"
PY = "/usr/bin/python3"
CONTAINERS = ("/home", "/mnt", "/tmp", "/var/tmp", "/run", "/root", "/srv", "/opt", "/media", "/usr/lib/wsl/drivers")
TOOL_RO = (".local/bin", ".local/share/claude", ".local/lib")          # home-relative, bound at the same path
HOME_SEED_RO = (".gitconfig",)                                         # home-relative, bound into the private home
RM_ROOT = "/home/mandrake/rm"
RM_ROOT_KEEP = ("arena",)                     # every other child of RM_ROOT is DENY (bench, foundry, retired-trees...)
ARENA_KEEP = ("replay", "sandbox")            # every other child of the arena root is DENY (judge, probe dirs...)
CLAUDEWORK = "/mnt/d/ClaudeWork/rimmandrake"
HOME_DENY = (".claude/projects", ".claude/file-history", ".claude/history.jsonl", ".claude/sessions",
             ".claude/shell-snapshots", ".claude/todos", ".claude/paste-cache", ".claude/backups", ".claude/jobs",
             ".claude/.credentials.json", ".claude.json", ".codex", ".claude-accounts", ".config", ".ssh",
             ".local/state", "dev", "checkout", "src", "crash_backup_*", ".zsh_history",
             ".bash_history", ".remember", ".cache")
DROP_ENV = ("WSL_INTEROP", "XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS", "SSH_AUTH_SOCK", "DISPLAY",
            "WAYLAND_DISPLAY", "PULSE_SERVER", "GIT_DIR", "GIT_WORK_TREE", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
            "GIT_OBJECT_DIRECTORY", "GIT_COMMON_DIR", "GIT_INDEX_FILE", "OLDPWD")
AF_VSOCK = 40


class SandboxRefused(Exception):
    pass


def _home() -> Path:
    import pwd
    return Path(pwd.getpwuid(os.getuid()).pw_dir)


def _real(p) -> str:
    return os.path.realpath(os.path.expanduser(str(p)))


def _under(a: str, b: str) -> bool:
    """a equals b or lies inside b (both realpaths)"""
    return a == b or a.startswith(b.rstrip("/") + "/")


def deny_paths() -> list[str]:
    """Every path that must never be visible to an arm nor bound into its sandbox (realpaths, existing or not).
    arena_replay.sandbox_masks() (the answer holders, derived from arena_tasks.old_history_repos), the D:\\ClaudeWork
    notes root, every child of RM_ROOT but the arena root, every child of the arena root but replay/sandbox, and the
    $HOME leaks (transcripts, histories, credentials, old clones)."""
    import arena_replay as R
    out = list(R.sandbox_masks())
    out.append(CLAUDEWORK)
    for base, keep in ((RM_ROOT, RM_ROOT_KEEP), (str(R.arena_root()), ARENA_KEEP)):
        try:
            out += [os.path.join(base, n) for n in os.listdir(base) if n not in keep]
        except FileNotFoundError:
            pass
    h = str(_home())
    for rel in HOME_DENY:
        hits = glob.glob(os.path.join(h, rel)) if glob.has_magic(rel) else [os.path.join(h, rel)]
        out += hits
    seen = []
    for x in out:
        r = _real(x)
        if r not in seen:
            seen.append(r)
    return seen


def check_bind(path: str, deny: list[str], what: str) -> str:
    r = _real(path)
    if r in ("/", "") or not os.path.isabs(r):
        raise SandboxRefused("refused: %s bind %r is the root or relative" % (what, path))
    for d in deny:
        if _under(r, d) or _under(d, r):
            raise SandboxRefused("refused: %s bind %s overlaps the masked path %s (the arm would see the answer)"
                                 % (what, r, d))
    return r


# ------------------------------------------------------------------------------------------------ seccomp
def seccomp_program() -> bytes:
    """classic BPF for x86_64: KILL on a foreign ABI (i386 / x32: their socketcall would dodge the socket rule),
    EAFNOSUPPORT for socket(AF_VSOCK, ...) (family = low 32 bits of args[0], the kernel takes an int), ENOSYS for
    io_uring_setup/enter/register (425-427), allow the rest."""
    return b"".join(struct.pack("=HBBI", *i) for i in _resolve())


def _resolve():
    """Assemble the seccomp program from labels (jump offsets are computed, never hand-counted)."""
    LD, JEQ, JGE, RET = 0x20, 0x15, 0x35, 0x06
    ALLOW, KILL = 0x7FFF0000, 0x80000000
    code = [("ld", 4), ("jeq", 0xC000003E, None, "kill"),
            ("ld", 0), ("jge", 0x40000000, "kill", None),
            ("jeq", 425, "uring", None), ("jeq", 426, "uring", None), ("jeq", 427, "uring", None),
            ("jeq", 41, None, "allow"),
            ("ld", 16), ("jeq", AF_VSOCK, "noaf", None),
            ("L", "allow"), ("ret", ALLOW),
            ("L", "kill"), ("ret", KILL),
            ("L", "uring"), ("ret", 0x00050000 | 38),
            ("L", "noaf"), ("ret", 0x00050000 | 97)]
    labels, pc = {}, 0
    for c in code:
        if c[0] == "L":
            labels[c[1]] = pc
        else:
            pc += 1
    out, pc = [], 0
    for c in code:
        if c[0] == "L":
            continue
        if c[0] == "ld":
            out.append((LD, 0, 0, c[1]))
        elif c[0] == "ret":
            out.append((RET, 0, 0, c[1]))
        else:
            jt = labels[c[2]] - pc - 1 if c[2] else 0
            jf = labels[c[3]] - pc - 1 if c[3] else 0
            if not (0 <= jt < 256 and 0 <= jf < 256):
                raise SandboxRefused("seccomp program jump out of range")
            out.append((JEQ if c[0] == "jeq" else JGE, jt, jf, c[1]))
        pc += 1
    return out


def _bpf_file() -> str:
    fd, path = tempfile.mkstemp(prefix="arm_sandbox_", suffix=".bpf")
    with os.fdopen(fd, "wb") as f:
        f.write(seccomp_program())
    return path


# ------------------------------------------------------------------------------------------------ argv
def _prereq():
    if not (os.path.isfile(BWRAP) and os.access(BWRAP, os.X_OK)):
        raise SandboxRefused("refused: %s not found: an arm never runs unsandboxed" % BWRAP)
    if platform.machine() != "x86_64":
        raise SandboxRefused("refused: the seccomp program is x86_64-only (machine %s)" % platform.machine())
    if not os.access(PY, os.X_OK):
        raise SandboxRefused("refused: %s missing: the preflight cannot run" % PY)


def plan(*, cwd, rw, home, ro=(), _drop=()):
    """The mount plan: dict with the checked bind lists. `_drop` (selftest mutations only) omits named protections."""
    deny = deny_paths()
    rw_r = [check_bind(p, deny, "rw") for p in rw]
    if not rw_r:
        raise SandboxRefused("refused: no rw dir (the arm clone / scratch)")
    for p in rw_r:
        if not os.path.isdir(p):
            raise SandboxRefused("refused: rw dir %s does not exist" % p)
    home_r = _real(home)
    if not any(_under(home_r, p) for p in rw_r):
        raise SandboxRefused("refused: private home %s is not inside a rw dir" % home_r)
    cwd_r = _real(cwd)
    if not any(_under(cwd_r, p) for p in rw_r):
        raise SandboxRefused("refused: cwd %s is not inside a rw dir" % cwd_r)
    h = _home()
    extra = [x for x in os.environ.get("RM_ARM_SANDBOX_RO", "").split(os.pathsep) if x.strip()]
    tools = []
    for p in [str(h / t) for t in TOOL_RO] + list(ro) + extra:
        if os.path.exists(p):
            tools.append(check_bind(p, deny, "ro"))
    seeds = []
    rels = list(HOME_SEED_RO) + [x for x in os.environ.get("RM_ARM_SANDBOX_HOME_RO", "").split(os.pathsep) if x]
    for rel in rels:
        if os.path.isabs(rel) or ".." in Path(rel).parts:
            raise SandboxRefused("refused: home seed %r must be home-relative" % rel)
        src = h / rel
        if rel == ".claude/.credentials.json" and src.exists():   # the one HOME_DENY entry an operator may opt into
            seeds.append((_real(src), os.path.join(home_r, rel)))
            continue
        if src.exists():
            seeds.append((check_bind(str(src), deny, "home seed"), os.path.join(home_r, rel)))
    files = []
    for f in ("/etc/resolv.conf", "/etc/hosts"):
        r = _real(f)
        if r != f and os.path.exists(r) and any(_under(r, c) for c in CONTAINERS):
            files.append(check_bind(r, deny, "resolver"))
    return {"deny": deny, "rw": rw_r, "home": home_r, "cwd": cwd_r, "tools": tools, "seeds": seeds,
            "files": files, "drop": set(_drop)}


def bwrap_argv(pl, bpf_path=None) -> list[str]:
    d = pl["drop"]
    a = [BWRAP]
    a += ["--unshare-user", "--disable-userns"] if "userns" not in d else []
    a += ["--unshare-pid"] if "pidns" not in d else []
    a += ["--unshare-ipc", "--unshare-uts", "--die-with-parent", "--new-session",
          "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc"]
    for c in CONTAINERS:
        if c not in d and os.path.isdir(c):
            a += ["--tmpfs", c]
    for f in pl["files"]:
        a += ["--ro-bind", f, f]
    for t in pl["tools"]:
        a += ["--ro-bind", t, t]
    for r in pl["rw"]:
        a += ["--bind", r, r]
    for src, dst in pl["seeds"]:
        a += ["--ro-bind", src, dst]
    if bpf_path and "seccomp" not in d:
        a += ["--seccomp", "3"]
    a += ["--chdir", pl["cwd"]]
    if bpf_path and "seccomp" not in d:     # fd 3 = the filter, opened by sh, the file unlinked before bwrap runs
        a = ["/bin/sh", "-c", 'exec 3<"$1" && rm -f "$1" && shift && exec "$@"', "sh", bpf_path] + a
    return a + ["--"]


def sandbox_env(env, home, drop=()):
    e = {k: v for k, v in dict(env).items() if k not in DROP_ENV or ("env" in drop and k == "WSL_INTEROP")}
    e.update(HOME=home, TMPDIR="/tmp")
    return e


def _seed_home(home):
    Path(home).mkdir(parents=True, exist_ok=True)
    cj = Path(home) / ".claude.json"
    if not cj.exists():
        cj.write_text(json.dumps({"hasCompletedOnboarding": True, "autoUpdates": False}) + "\n")


# ------------------------------------------------------------------------------------------------ probe (runs INSIDE)
PROBE = r'''
import json, os, socket, subprocess, sys
spec = json.loads(sys.argv[1])
leaks, fails, info = [], [], {}
def vis(p):
    try:
        os.stat(p)
        return True
    except OSError:
        return False
def run(argv, **kw):
    try:
        r = subprocess.run(argv, capture_output=True, text=True, errors="replace", timeout=spec.get("t", 20), **kw)
        return r.returncode, (r.stdout + r.stderr)[:300]
    except (OSError, subprocess.SubprocessError) as e:
        return 127, repr(e)[:300]
masked = spec["masked"]
roots = ["/proc/self/root", "/proc/thread-self/root"]
for d in os.listdir("/proc"):
    if d.isdigit():
        roots.append("/proc/%s/root" % d)
        roots.append("/proc/%s/cwd/.." % d)
for p in masked:
    if os.path.lexists(p) or vis(p):
        leaks.append(["visible", p])
    for r in roots:
        if vis(r + p):
            leaks.append(["via " + r, p])
for d, allowed in spec.get("only", {}).items():
    try:
        extra = sorted(set(os.listdir(d)) - set(allowed))
    except OSError:
        extra = []
    if extra:
        leaks.append(["unexpected entries in " + d, extra[:20]])
if os.environ.get("WSL_INTEROP"):
    leaks.append(["env", "WSL_INTEROP"])
try:
    init = open("/proc/1/cmdline", "rb").read().split(b"\0")[0]
except OSError:
    init = b""
if os.path.basename(init) != b"bwrap":
    leaks.append(["host pid namespace", "/proc/1 is %r" % init[:60]])
if os.path.exists("/run/WSL"):
    leaks.append(["visible", "/run/WSL"])
try:
    socket.socket(40, socket.SOCK_STREAM).close()
    leaks.append(["socket", "AF_VSOCK creatable"])
except OSError:
    pass
for p in spec["rw"]:
    if not (os.path.isdir(p) and os.access(p, os.W_OK)):
        fails.append(["rw dir not writable", p])
if spec.get("full"):
    att = 0
    for p in masked:
        for argv in (["cat", p], ["ls", "-la", p], ["git", "-C", p, "log", "-1", "--oneline"],
                     ["git", "--git-dir", p, "log", "-1", "--oneline"],
                     ["git", "-C", p, "for-each-ref", "refs/arena/old/"], ["grep", "-r", "-l", "-m1", "e", p]):
            att += 1
            rc, out = run(argv)
            if rc == 0 or (argv[0] == "grep" and rc == 1):
                leaks.append([" ".join(argv[:2]), p, out[:120]])
        att += 1
        try:
            if os.path.isdir(p):
                os.listdir(p)
            else:
                open(p, "rb").read(1)
            leaks.append(["python open/listdir", p])
        except OSError:
            pass
        lnk = os.path.join(spec["scratch"], ".probe_lnk")
        try:
            os.unlink(lnk)
        except OSError:
            pass
        os.symlink(p, lnk)
        att += 1
        if vis(lnk):
            leaks.append(["symlink", p])
        os.unlink(lnk)
    for pe in spec.get("pe", []):
        for argv in ([pe], ["/init", pe]):          # a copied whoami.exe: rc 0 only if interop ran it
            att += 1
            rc, out = run(argv)
            if rc == 0:
                leaks.append(["interop exec", " ".join(argv[:2]), out[:120]])
    c = spec.get("clone")
    if c:
        rc, out = run(["git", "-C", c, "log", "--all", "--oneline"])
        info["clone_git_log_rc"] = rc
        info["clone_git_log_lines"] = len(out.splitlines())
        if rc != 0:
            fails.append(["git log in the clone failed", out[:200]])
        for s in spec.get("absent", []):
            att += 1
            rc, out = run(["git", "-C", c, "cat-file", "-e", s + "^{commit}"])
            if rc == 0:
                leaks.append(["future commit in the clone", s])
        f = os.path.join(c, ".probe_write")
        try:
            open(f, "w").write("x")
            os.unlink(f)
        except OSError as e:
            fails.append(["clone not writable", repr(e)])
    for tool in spec.get("tools", []):
        rc, out = run(tool)
        info["tool " + tool[0]] = [rc, out.strip()[:80]]
        if rc != 0:
            fails.append(["tool failed", tool, out[:200]])
    info["attempts"] = att
print("ARM_SANDBOX_PROBE " + json.dumps({"leaks": leaks, "fails": fails, "info": info, "n_masked": len(masked)}))
'''


def probe_spec(pl, full=False, **kw):
    """What the probe must NOT see: every DENY path, every child of /mnt but the resolver dir, every child of the real
    $HOME that is not on the way to a bind; and the rw dirs it MUST be able to write."""
    h = str(_home())
    binds = pl["rw"] + pl["tools"] + pl["files"] + [d for _, d in pl["seeds"]]
    masked = list(pl["deny"])
    for top in (h, "/mnt", RM_ROOT, "/run", "/tmp"):
        try:
            names = os.listdir(top)
        except OSError:
            continue
        for n in names:
            p = os.path.join(top, n)
            if not any(_under(b, p) for b in binds) and p not in masked:
                masked.append(p)
    spec = {"masked": masked, "rw": pl["rw"], "scratch": pl["home"], "full": full}
    spec.update(kw)
    return spec


def _run_probe(pl, spec, env, timeout=300):
    bpf = _bpf_file()
    try:
        argv = bwrap_argv(pl, bpf) + [PY, "-I", "-c", PROBE, json.dumps(spec)]
        r = subprocess.run(argv, capture_output=True, text=True, errors="replace",
                           env=sandbox_env(env, pl["home"], pl["drop"]),
                           timeout=timeout)
    finally:
        if os.path.exists(bpf):
            os.unlink(bpf)
    for line in r.stdout.splitlines():
        if line.startswith("ARM_SANDBOX_PROBE "):
            return json.loads(line[len("ARM_SANDBOX_PROBE "):])
    raise SandboxRefused("refused: the sandbox probe did not run (rc %s): %s" % (r.returncode,
                                                                              (r.stdout + r.stderr)[-600:]))


def preflight(pl, env):
    """Run inside the SAME sandbox the arm will get; any visible masked path, live interop, a creatable AF_VSOCK
    socket or an unwritable rw dir -> SandboxRefused."""
    res = _run_probe(pl, probe_spec(pl), env, timeout=120)
    if res["leaks"] or res["fails"]:
        raise SandboxRefused("refused: sandbox preflight failed: leaks=%s fails=%s"
                             % (json.dumps(res["leaks"])[:800], json.dumps(res["fails"])[:400]))
    return res


def wrap(argv, env, *, cwd, rw, home, ro=(), _drop=(), _preflight=True):
    """THE choke point: (argv, env) for subprocess.Popen that runs `argv` sandboxed. Raises SandboxRefused (the
    launch must not happen) on any doubt. `rw`: the arm clone and/or scratch dir(s); `home`: the private HOME (inside
    a rw dir, created and seeded here); `cwd` must be inside a rw dir. `_drop`/`_preflight` are selftest-only."""
    _prereq()
    _seed_home(home)
    pl = plan(cwd=cwd, rw=rw, home=home, ro=ro, _drop=_drop)
    if _preflight:
        preflight(pl, env)
    return bwrap_argv(pl, _bpf_file()) + list(argv), sandbox_env(env, pl["home"], pl["drop"])


def probe(*, clone, scratch, absent=(), pe=(), tools=(), _drop=(), env=None, full=True):
    """The ATTACK probe (selftest + CLI): launches a real sandboxed process exactly like wrap() and tries cat / ls /
    git -C / git --git-dir / grep -r / python open / symlink / /proc/*/root on every masked path, Windows interop on
    every PE given, and checks the clone (git log works, `absent` shas are not there) and `tools` still work."""
    _prereq()
    home = os.path.join(scratch, "home")
    _seed_home(home)
    pl = plan(cwd=clone, rw=[clone, scratch], home=home, _drop=_drop)
    spec = probe_spec(pl, full=full, clone=_real(clone), absent=list(absent), pe=list(pe),
                      tools=[list(t) for t in tools])
    return _run_probe(pl, spec, dict(os.environ if env is None else env))


def scratch_dir(cwd, role) -> Path:
    """A builder's persistent scratch (its private HOME lives here): $RM_ARM_SANDBOX_SCRATCH or <arena root>/sandbox,
    then <clone name>-<sha256(clone realpath)[:8]>/<role>, mode 0700. Never inside the clone (git status stays clean)."""
    import hashlib
    import arena_replay as R
    base = Path(os.environ.get("RM_ARM_SANDBOX_SCRATCH") or (R.arena_root() / "sandbox"))
    c = _real(cwd)
    d = base / ("%s-%s" % (os.path.basename(c), hashlib.sha256(c.encode()).hexdigest()[:8])) / str(role)
    d.mkdir(parents=True, exist_ok=True, mode=0o700)
    return d


MUTATIONS = ("/home", "/mnt", "/run", "/tmp", "pidns", "seccomp", "env")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe", help="attack-probe a real sandbox; exit 0 only when nothing leaks")
    p.add_argument("--clone", required=True)
    p.add_argument("--scratch", required=True)
    p.add_argument("--absent", action="append", default=[], help="a sha the clone must not hold")
    p.add_argument("--pe", action="append", default=[], help="a Windows PE (inside --scratch) to try to exec")
    p.add_argument("--drop", action="append", default=[], choices=MUTATIONS, help="mutation: omit a protection")
    sub.add_parser("deny", help="print the DENY list")
    a = ap.parse_args(argv)
    if a.cmd == "deny":
        print("\n".join(deny_paths()))
        return 0
    res = probe(clone=a.clone, scratch=a.scratch, absent=a.absent, pe=a.pe, _drop=a.drop,
                tools=[["git", "--version"], [PY, "--version"]])
    print(json.dumps(res, indent=1))
    return 1 if (res["leaks"] or res["fails"]) else 0


if __name__ == "__main__":
    sys.exit(main())
