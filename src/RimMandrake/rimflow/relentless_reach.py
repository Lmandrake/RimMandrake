#!/usr/bin/env python3
"""relentless_reach.py - what a contract's proof needs that the walled Marker's box cannot reach, found before a Marker is paid.

CHECKER_REACH_PROBE_BEFORE_PAYING_TWICE: a blind Marker cost ~1.5M weighted tokens to say CANNOT REACH, and the recheck paid
the same again on an unchanged box (32M, 11.1% of 24h spend, 2026-11-04). Store census that day, 60 unmeasured attempts:
36 named /mnt/d/ClaudeWork (33 of them the contract's --live reading), 18 git history (the box has no .git), 5 a Windows
program, 5 ssh, the rest other clones and /proc. Four answers, each pure here and wired in relentless.py:

  needs()        the proof text, read against the walls profile: a hidden path, a git history verb, a remote host, a
                 Windows program. `contract` refuses such a proof unless --offbox names an adapter or --reach-ok says why;
                 the candidate branch holds an old contract that still has one before any Marker launches.
  live_reading() the contract's live line, checked by the supervisor outside the wall at launch and written into the box,
                 so no Marker pays to find /mnt/d/ClaudeWork empty.
  fingerprint()  what a repair of the box would change (the walls profile, the adapters, the contract): an UNMEASURED
                 recheck on the same sha with the same fingerprint would buy the same answer, so it is held at once.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path

import relentless_wall

# a path-shaped word: absolute, home-relative, or a Windows drive path
_PATH = re.compile(r"(?<![\w.~$@+/\\-])(?:[A-Za-z]:[\\/]|~/|\$HOME/|/)[\w.~$@+-]*(?:[/\\][\w.~$@+-]*)*")
_COMMENT = re.compile(r"(?:^|(?<=\s))#.*$", re.M)
# a parenthesised aside is the worker's prose about the proof ("(the retry cases prove a dotnet.exe launch ...)"): a census of
# the store's 603 contracts found it the main false alarm. `$(...)` is a command and stays, and so is a subshell: a group
# holding a shell operator, `(cd x && git log)`.
_PROSE = re.compile(r"(?<![$\w])\((?![^()]*(?:&&|\|\||[;|`]|\$\())[^()]*\)")
_VAR = re.compile(r"\$\{(\w+)\}|\$(\w+)")
_ASSIGN = re.compile(r"(?:^|(?<=[\s;&|(]))([A-Za-z_]\w*)=([^\s;&|)]+)")
# where a command starts: the line, a shell operator, a subshell, `!`, then any VAR=value and a timeout. Programs named in
# prose ("git grep shows ..." at a line's start is still a command a Marker would run) are matched only here.
_START = (r"(?:^|&&|\|\||[;|`(]|\$\(|!|\bthen\b|\bdo\b)\s*(?:(?:sudo|env|xargs|nice|command|exec|timeout\s+\S+)\s+|"
          r"(?:bash|sh|zsh)\s+-l?c\s+['\"]|[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*")
_GIT = re.compile(_START + r"git\s+(?:(?:-C|-c)\s+\S+\s+|--\S+\s+)*(log|show|rev-parse|cat-file|diff|blame|rev-list|merge-base|status|"
                  r"ls-files|ls-tree|describe|branch|for-each-ref|reflog|fetch|pull|grep)\b", re.M)
_REMOTE = re.compile(_START + r"(ssh|scp|rsync|tailscale|sftp)\s", re.M)
_WINDOWS = re.compile(_START + r"(?:python3?\s+)?(\S*winbuild\.py|\S+\.exe|powershell|pwsh|wslpath)\b", re.M | re.I)


def _norm(p):
    """-> the word as a host path: ~ and $HOME expanded, a Windows drive path as /mnt/<drive>/..., no trailing slash."""
    p = p.rstrip(".,;:)'\"")
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", p)
    if m:
        p = "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/"))
    if p.startswith("~/"):
        p = relentless_wall.HOME + p[1:]
    elif p.startswith("$HOME/"):
        p = relentless_wall.HOME + p[5:]
    return p.rstrip("/") or "/"


def _under(p, root):
    root = root.rstrip("/")
    return p == root or p.startswith(root + "/")


def hidden_roots(prof):
    """-> (roots whose every path is hidden, roots whose children are hidden). Prefixes only: no filesystem read, so a clone
    made tomorrow is hidden too and the answer is the same inside a box."""
    whole = list(prof.get("deny") or ()) + list(prof.get("tmpfs") or ())
    return whole, list(prof.get("deny_children") or ())


def hidden(path, prof, carved=()):
    """True when the box cannot read `path` (a host path). `carved`: real paths the wall leaves readable (the skill targets)."""
    p = _norm(path)
    if any(_under(p, c) for c in carved):
        return False
    whole, kids = hidden_roots(prof)
    return any(_under(p, r) for r in whole) or any(p.startswith(r.rstrip("/") + "/") for r in kids)


def needs(text, prof, carved=()):
    """-> ["kind: what", ...] the box cannot reach that `text` (a proof) names, once each, in order. Pure."""
    out = []

    def add(x):
        if x not in out:
            out.append(x)
    t = _COMMENT.sub("", text or "")     # a shell comment is the worker's prose about the proof, not what it runs
    env = dict(prof.get("env") or {}, **{k: v.strip("'\"") for k, v in _ASSIGN.findall(t)})   # the box's env, then the proof's own
    t = _VAR.sub(lambda m: env.get(m.group(1) or m.group(2), m.group(0)), t)   # "$RM_DATA_ROOT/x" is the masked root
    while True:
        u = _PROSE.sub(" ", t)
        if u == t:
            break
        t = u
    for m in _PATH.finditer(t):
        w = m.group(0)
        if len(w) > 1 and hidden(w, prof, carved):
            add("hidden path: %s" % w.rstrip(".,;:)'\""))
    for m in _GIT.finditer(t):
        add("git history: `git %s` (the box is an export with no .git)" % m.group(1))
    for m in _REMOTE.finditer(t):
        add("another machine: `%s` (the box has no ssh keys)" % m.group(1))
    for m in _WINDOWS.finditer(t):
        add("a Windows program: `%s` (no Windows interop in the box)" % m.group(1))
    return out


def carved_of(prof):
    """The skill targets the wall carves out, or none when they cannot be listed (a box, a missing folder)."""
    try:
        return relentless_wall.skill_targets(prof)
    except OSError:
        return []


def uncovered(contract, rules):
    """-> the needs of the contract's proof that nothing routes: [] when the Marker is unwalled, when the contract names an
    offbox adapter (the supervisor reads it outside; the Marker judges the reading) or carries a reach_ok why."""
    prof = relentless_wall.profile(rules or {})
    c = contract or {}
    if not prof or not relentless_wall.enforced(rules) or c.get("offbox") or c.get("reach_ok"):
        return []
    return needs(c.get("proof"), prof, carved_of(prof))


def refusal(found, adapter_names):
    return ("the proof needs what the walled Marker's box cannot reach, so a Marker would be paid only to say CANNOT REACH "
            "(CHECKER_REACH_PROBE_BEFORE_PAYING_TWICE): %s. Rewrite the proof to run on the exported tree (relative paths, "
            "a selftest with its own fixture), or add --offbox NAME with a supervisor adapter that reads it outside (%s), "
            "or --reach-ok \"why the box can still show it\"" % ("; ".join(found), ", ".join(sorted(adapter_names)) or "none yet"))


def live_reading(line, check=None, now=None):
    """-> {line, holds, why, at}: the contract's live line checked here, by the supervisor, outside the wall."""
    now = time.time() if now is None else now
    if check is None:
        import live_line
        check = live_line.check
    try:
        why = check(line, now=now)
    except Exception as e:      # noqa: BLE001 - a broken reader is a reading that failed, never a dead tick
        why = "the supervisor's live check raised %s: %s" % (type(e).__name__, e)
    return {"line": line, "holds": why is None, "why": why, "at": now}


def write_live(box, got):
    """-> the file. Read only: the Marker reads a measurement, never edits it."""
    f = Path(box, "live.txt")
    f.write_text("live line: %s\nmeasured_at=%s outside the box by the supervisor\n%s\n" % (
        got["line"], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(got["at"])),
        "HOLDS" if got["holds"] else "DOES NOT HOLD: %s" % got["why"]), encoding="utf-8")
    os.chmod(f, 0o444)
    return str(f)


def live_lines(contract, box):
    """The Marker's words about the live line, when the contract has one."""
    live = (contract or {}).get("live")
    if not live:
        return []
    return ["", "Live line: the supervisor checked the contract's live line %r outside your box just before you started and "
            "wrote the result to %s/live.txt (read only). Its reading may sit on a path your box hides: do not try to reach it, "
            "and never call it --unreached; `rimflow close` checks the same line again and refuses a close on a line that "
            "does not hold. Judge whether the line is the promise the item needs." % (live, box)]


def fingerprint(rules, contract):
    """-> a short hash of what a repair of the box would change: the Marker's walls profile, the offbox adapters, the
    contract as the Marker sees it. Same fingerprint, same sha: a recheck buys the same answer."""
    r = rules or {}
    body = {"wall": relentless_wall.profile(r), "adapters": relentless_wall.adapters(r),
            "contract": {k: (contract or {}).get(k) for k in ("proof", "live", "offbox", "game", "reach_ok")}}
    return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]


def repays(st, rules):
    """True when this candidate's check would buy again what its last UNMEASURED said: the same sha, the same box, and no
    offbox reading (an adapter reads a remote now, so a later run of it can differ)."""
    b = st.get("blind") or {}
    c = st.get("contract") or {}
    return bool(b.get("box") and b.get("sha") == (st.get("candidate") or {}).get("sha") and not c.get("offbox")
                and b["box"] == fingerprint(rules, c))
