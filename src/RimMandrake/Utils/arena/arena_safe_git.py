#!/usr/bin/env python3
"""arena_safe_git.py - git calls on a clone whose .git a build helper (an untrusted builder) may have written.

ONE definition: ralph_a_loop (and through it trio_loop, ralph_c_loop), arena_gate and ralph_c_runner all import
this module; none keeps a copy of the env, config pins, git_run, no_filter_cfg or net_cfg (RALPHA_GIT_DEDUPE_SAFE_GIT_COPY).

What the builder can plant in a .git and what each knob does:
  replace ref / graft   GIT_NO_REPLACE_OBJECTS=1, GIT_GRAFT_FILE=/dev/null: sha A is read as A, not as commit B
  system/global config  GIT_CONFIG_NOSYSTEM, GIT_CONFIG_GLOBAL=/dev/null (except where the user's ssh config is needed)
  attributes file       core.attributesFile=/dev/null (the in-tree .gitattributes is part of the sha and stays)
  fsmonitor / hooks     core.fsmonitor=false, core.hooksPath=/dev/null
  diff driver           diff.external= and GIT_EXTERNAL_DIFF=; diff calls also pass --no-ext-diff --no-textconv
  filter drivers        filter.<name>.clean/smudge/process in .git/config are rewritten to `cat` / nothing
  ssh / proxy / remote  core.sshCommand, core.gitProxy, remote.origin.uploadpack/receivepack, protocol.ext
No `git archive` here: export-ignore / export-subst change what it writes.
"""
import hashlib
import os
import subprocess
import tempfile
from pathlib import Path

GIT_SAFE_ENV = {"GIT_NO_REPLACE_OBJECTS": "1", "GIT_GRAFT_FILE": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": os.devnull, "GIT_EXTERNAL_DIFF": "", "GIT_PAGER": "cat",
                "GIT_TERMINAL_PROMPT": "0"}
GIT_SAFE_CFG = ["-c", "core.fsmonitor=false", "-c", "core.hooksPath=" + os.devnull, "-c", "diff.external=",
                "-c", "core.attributesFile=" + os.devnull, "-c", "protocol.ext.allow=never",
                # a commit starts `git maintenance run --auto --detach`, which outlives it with its cwd in the clone
                # and trips ralph_a's "no process beside a build pass" refusal (ARENA_DRILL_SYNC_FLAKY_PENDING_MAIN)
                "-c", "maintenance.auto=false", "-c", "gc.auto=0"]
NO_DRIVER = ("--no-ext-diff", "--no-textconv")
# a transport call (fetch/clone) reaches a remote: a repo-local core.sshCommand/gitProxy/uploadpack would run the
# builder's command as the harness. Override them; the user's own GLOBAL ssh command (if any) is passed back in.
# remote.<name>.uploadpack is multi-valued ("using the first": the repo's wins over -c), so a fetch must also pass
# --upload-pack=git-upload-pack on its own command line (an option beats config).
TRANSPORT_CFG = ["-c", "core.gitProxy="]


# a rebase / pull re-commits: no builder-chosen signing program may run
GPG_OFF = ["-c", "commit.gpgSign=false", "-c", "gpg.program=false", "-c", "gpg.openpgp.program=false",
           "-c", "gpg.ssh.program=false", "-c", "gpg.x509.program=false"]


def safe_env(keep_user_config=False):
    env = dict(os.environ, **GIT_SAFE_ENV)
    if keep_user_config:
        for k in ("GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL"):
            env.pop(k, None)
            if k in os.environ:
                env[k] = os.environ[k]
    return env


def no_filter_cfg(root):
    """`-c` overrides turning every filter.<name> clean/smudge into `cat` and process into nothing."""
    r = subprocess.run(["git", "-C", str(root), "config", "-z", "--get-regexp", r"^filter\..*\.(clean|smudge|process)$"],
                       env=safe_env(), capture_output=True)
    out = []
    for kv in r.stdout.split(b"\0"):
        key = kv.split(b"\n", 1)[0].decode("utf-8", "replace")
        if key:
            out += ["-c", key + ("=" if key.endswith(".process") else "=cat")]
    return out


class CloneRefused(OSError):
    """The clone's own config or layout is something a harness call must not trust (an OSError so callers that already
    catch a failed git run treat it as one)."""


def _owner_lines(argv):
    """git config read from outside any repo: only the owner's global/system config."""
    r = subprocess.run(["git"] + argv, env=dict(os.environ), capture_output=True, cwd=tempfile.gettempdir())
    return [x for x in r.stdout.split(b"\0") if x] if r.returncode == 0 else []


def user_ssh_cfg():
    """The user's own (global) core.sshCommand, read with the repo-local config out of the picture; plain `ssh` when
    the owner has none (an empty value would make every ssh origin fail)."""
    vals = _owner_lines(["config", "--get-all", "-z", "core.sshCommand"])
    return ["-c", "core.sshCommand=" + (vals[-1].decode("utf-8", "replace") if vals else "ssh")]


def _clone_lines(root, argv):
    """NUL-separated config output of the clone itself (its own file plus what it includes; the owner's global/system
    config is out of the picture)."""
    r = subprocess.run(["git", "-C", str(root)] + argv, env=safe_env(), capture_output=True)
    return [x for x in r.stdout.split(b"\0") if x]


def merge_drivers(root):
    """{`merge.<name>.driver`: command} the clone's config defines (a builder-set driver would run as the harness)"""
    out = {}
    for kv in _clone_lines(root, ["config", "-z", "--get-regexp", r"^merge\..*\.driver$"]):
        k, _, v = kv.decode("utf-8", "replace").partition("\n")
        out[k] = v
    return out


def net_cfg(root, url=None):
    """Transport pins: signing off, core.sshCommand/core.askPass and every credential*.helper the OWNER's value or
    nothing (the clone's own are overridden: a reset then the owner's list), every merge.<name>.driver the clone
    defines pinned to `false` (a rebase would run it). Raises CloneRefused for a clone that redirects URLs with
    url.*.insteadOf, or (with `url`, the pinned remote) defines a remote section named like it (its url/uploadpack/
    proxy would replace the pin)."""
    out = list(GPG_OFF)
    if root is not None:
        if _clone_lines(root, ["config", "-z", "--name-only", "--get-regexp", r"^url\..*\.(push)?insteadof$"]):
            raise CloneRefused("%s redirects URLs (url.*.insteadOf in its config): refused" % root)
        if url and any(k.startswith(b"remote." + url.encode() + b".") for k in
                       _clone_lines(root, ["config", "-z", "--name-only", "--get-regexp", r"^remote\."])):
            raise CloneRefused("%s defines a remote section named like the pinned url %s: refused" % (root, url))
    vals = _owner_lines(["config", "--get-all", "-z", "core.askPass"])
    out += ["-c", "core.askPass=" + (vals[-1].decode("utf-8", "replace") if vals else "")]
    rx = r"^credential\..*helper$"
    keys = {}
    for kv in _owner_lines(["config", "-z", "--get-regexp", rx]):
        k, _, v = kv.decode("utf-8", "replace").partition("\n")
        keys.setdefault(k, []).append(v)
    if root is not None:
        for kv in _clone_lines(root, ["config", "-z", "--get-regexp", rx]):
            keys.setdefault(kv.decode("utf-8", "replace").partition("\n")[0], [])
    for k, vs in keys.items():
        out += ["-c", k + "="]                        # an empty value resets the list
        for v in vs:
            out += ["-c", "%s=%s" % (k, v)]
    if root is not None:
        for k in merge_drivers(root):
            out += ["-c", k + "=false"]
    return out


# keys that change what a checkout writes or where: pinned on every call that has a worktree
WORKTREE_CFG = ["-c", "core.sparseCheckout=false", "-c", "core.sparseCheckoutCone=false", "-c", "core.autocrlf=false",
                "-c", "core.eol=lf", "-c", "core.safecrlf=false", "-c", "core.symlinks=true", "-c", "core.ignoreStat=false"]


def git_argv(root, *a, transport=False, url=None):
    """The argv for a safe git call on `root` (root=None: no -C, e.g. a clone whose dest does not exist yet)."""
    head = ["git"] + (["-C", str(root)] if root is not None else []) + GIT_SAFE_CFG
    if transport:
        head += TRANSPORT_CFG + user_ssh_cfg() + net_cfg(root, url)
    if root is not None:
        head += no_filter_cfg(root)
        if (Path(root) / ".git").exists():
            head += WORKTREE_CFG
    return head + list(a)


def _env(root, transport):
    env = safe_env(keep_user_config=transport)
    if transport:
        env["GIT_ALLOW_PROTOCOL"] = "file:https:ssh"   # no ext:: or helper protocol, whatever the clone's config says
        env.pop("GIT_ASKPASS", None)
    if root is not None and (Path(root) / ".git").exists():
        env["GIT_WORK_TREE"] = str(root)               # beats a planted core.worktree (checkout/clean would hit another tree)
    return env


def git_run(root, *a, transport=False, url=None, **kw):
    """subprocess.run of git on the clone with the safe env and config. transport=True keeps the user's global
    config (credential helpers) but not the clone's ssh/proxy/uploadpack/askpass/credential commands."""
    return subprocess.run(git_argv(root, *a, transport=transport, url=url), env=_env(root, transport), **kw)


def check_clone(root):
    """-> '' when `root` is a plain clone a harness may check out in, else why not: .git must be a directory (a
    `gitdir:` file points the clone anywhere), info/attributes empty (it changes what a checkout writes), no
    core.worktree/core.bare override."""
    root = Path(root)
    gd = root / ".git"
    if gd.is_symlink() or not gd.is_dir():
        return "refused: %s is not a real directory (gitdir file or missing)" % gd
    attr = gd / "info" / "attributes"
    if attr.exists() and attr.stat().st_size:
        return "refused: %s is non-empty (it changes what a checkout writes)" % attr
    for k in ("core.worktree", "core.bare"):
        r = subprocess.run(["git", "-C", str(root), "config", "--local", "--get", k], env=safe_env(), capture_output=True, text=True)
        if r.returncode == 0 and not (k == "core.bare" and r.stdout.strip().lower() in ("false", "no", "off", "0")):
            return "refused: %s sets %s=%s" % (root, k, r.stdout.strip())
    return ""


def verify_tree(root, rev):
    """-> (ok, text): every object of `rev` (the commit, all its trees and blobs) hashes to its own name. A builder who
    can write .git/objects can store other content under a sha; neither a local clone nor checkout re-hashes it.
    (fsck --connectivity-only does not either, and fsck --full re-hashes the whole store: minutes.)"""
    r = git_run(root, "rev-parse", "--verify", "-q", rev + "^{commit}", capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return False, "no commit %s" % rev
    commit = r.stdout.strip()
    r = git_run(root, "ls-tree", "-r", "-t", "-z", commit, capture_output=True, timeout=300)
    if r.returncode != 0:
        return False, "ls-tree failed"
    want = [commit]
    for ent in r.stdout.split(b"\0"):
        if ent:
            meta = ent.split(b"\t", 1)[0].split()
            if meta[1] != b"commit":                  # a gitlink names a commit in another repo
                want.append(meta[2].decode())
    r = git_run(root, "rev-parse", "--verify", "-q", commit + "^{tree}", capture_output=True, text=True, timeout=60)
    want.append(r.stdout.strip())
    p = subprocess.Popen(git_argv(root, "cat-file", "--batch"), env=_env(root, False), stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        import threading
        feeder = threading.Thread(target=lambda: (p.stdin.write(("\n".join(want) + "\n").encode()), p.stdin.close()))
        feeder.start()
        for oid in want:
            hdr = p.stdout.readline().split()
            if len(hdr) != 3:
                return False, "object %s missing" % oid
            typ, size = hdr[1], int(hdr[2])
            body = p.stdout.read(size)
            p.stdout.read(1)
            h = hashlib.sha1(typ + b" " + str(size).encode() + b"\0" + body).hexdigest()
            if h != hdr[0].decode() or h != oid:
                return False, "object %s is stored with content hashing to %s (forged)" % (oid, h)
        feeder.join()
    finally:
        p.kill()
        p.wait()
    return True, "%d objects verified" % len(want)
