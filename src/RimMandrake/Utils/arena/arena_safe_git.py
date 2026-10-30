#!/usr/bin/env python3
"""arena_safe_git.py - git calls on a clone whose .git a build helper (an untrusted builder) may have written.

DUPLICATION NOTE: this mirrors the helpers in ralph_a_loop.py (GIT_SAFE_ENV, GIT_SAFE_CFG, NO_DRIVER, git_run,
no_filter_cfg). They are copied, not imported, because another change was editing ralph_a_loop.py; once that lands,
ralph_a_loop.py should import this module and its copy be deleted so there is one definition.

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
import os
import subprocess

GIT_SAFE_ENV = {"GIT_NO_REPLACE_OBJECTS": "1", "GIT_GRAFT_FILE": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": os.devnull, "GIT_EXTERNAL_DIFF": "", "GIT_PAGER": "cat",
                "GIT_TERMINAL_PROMPT": "0"}
GIT_SAFE_CFG = ["-c", "core.fsmonitor=false", "-c", "core.hooksPath=" + os.devnull, "-c", "diff.external=",
                "-c", "core.attributesFile=" + os.devnull, "-c", "protocol.ext.allow=never"]
NO_DRIVER = ("--no-ext-diff", "--no-textconv")
# a transport call (fetch/clone) reaches a remote: a repo-local core.sshCommand/gitProxy/uploadpack would run the
# builder's command as the harness. Override them; the user's own GLOBAL ssh command (if any) is passed back in.
# remote.<name>.uploadpack is multi-valued ("using the first": the repo's wins over -c), so a fetch must also pass
# --upload-pack=git-upload-pack on its own command line (an option beats config).
TRANSPORT_CFG = ["-c", "core.gitProxy="]


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


def user_ssh_cfg():
    """The user's own (global) core.sshCommand, read with the repo-local config out of the picture."""
    r = subprocess.run(["git", "config", "--global", "--get", "core.sshCommand"], env=dict(os.environ),
                       capture_output=True, text=True, cwd=os.path.expanduser("~") or "/")
    return ["-c", "core.sshCommand=" + (r.stdout.strip() if r.returncode == 0 else "")]


def git_argv(root, *a, transport=False):
    """The argv for a safe git call on `root` (root=None: no -C, e.g. a clone whose dest does not exist yet)."""
    head = ["git"] + (["-C", str(root)] if root is not None else []) + GIT_SAFE_CFG
    if transport:
        head += TRANSPORT_CFG + user_ssh_cfg()
    if root is not None:
        head += no_filter_cfg(root)
    return head + list(a)


def git_run(root, *a, transport=False, **kw):
    """subprocess.run of git on the clone with the safe env and config. transport=True keeps the user's global
    config (credential helpers) but not the clone's ssh/proxy/uploadpack commands."""
    return subprocess.run(git_argv(root, *a, transport=transport), env=safe_env(keep_user_config=transport), **kw)
