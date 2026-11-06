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
    if (any(_under(p, c) for c in list(carved) + relentless_wall.read_always(prof))
            or relentless_wall.through_reachable(p, prof)):
        return False            # a named path under a read_through root is bound read only (CHECKER_REACH_FIX_NAMED_SCRATCH_READ_ONLY)
    whole, kids = hidden_roots(prof)
    return any(_under(p, r) for r in whole) or any(p.startswith(r.rstrip("/") + "/") for r in kids)


def host_only_rows(rules):
    """-> [(test path, why)] from relentless_rules.json reach_host_only: selftests whose truth is the host's own layout."""
    rows = (rules or {}).get("reach_host_only") or []
    return [(str(x["path"]), str(x.get("why") or "")) for x in rows if isinstance(x, dict) and x.get("path")]


def git_tool_rows(rules):
    """-> [(tool path, why)] from relentless_rules.json reach_git_tools: tools that run git themselves, so naming one is a
    git history need though the proof text holds no git verb (OPS_CHURN_DIAGNOSE_RELENTLESS_HFDA_UHRX)."""
    rows = (rules or {}).get("reach_git_tools") or []
    return [(str(x["path"]), str(x.get("why") or "")) for x in rows if isinstance(x, dict) and x.get("path")]


def git_granted_rows(rules):
    """-> [(tool path, why)] from relentless_rules.json reach_git_granted: tools that read git at HEAD only, which the
    git_history box grant serves (OPS_CHURN_DIAGNOSE_GRAFFITI_LOVJ_IMIL)."""
    rows = (rules or {}).get("reach_git_granted") or []
    return [(str(x["path"]), str(x.get("why") or "")) for x in rows if isinstance(x, dict) and x.get("path")]


_PY_PATH = re.compile(r"(?<![\w./-])((?:[\w.-]+/)*[\w.-]+\.py)(?![\w.-])")


def box_grants(contract, rules, root):
    """-> the box grants the contract's proof earns at check launch: git_history when the proof names a reach_git_granted
    tool, or names a file under `root` (the candidate's clean clone) whose source names one. No regex over the proof sees a
    selftest that shells out to dll_source_stamp.py (GRAFFITI_V1_LIVE_PROOF_1: red in every git-less box, five checkers
    git-inited a copy by hand). One level only; a file that cannot be read earns nothing."""
    rows = git_granted_rows(rules)
    t = _COMMENT.sub("", (contract or {}).get("proof") or "")
    if not rows or not t:
        return []
    texts = [t]
    for rel in dict.fromkeys(_PY_PATH.findall(t)):
        f = os.path.join(str(root), rel)
        if os.path.isabs(rel) or ".." in rel.split("/") or not os.path.isfile(f):
            continue
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                texts.append(fh.read(2 << 20))
        except OSError:
            continue
    if any(_names(path, x) for path, _ in rows for x in texts):
        return [relentless_wall.GIT_GRANT]
    return []


def _names(path, t):
    return re.search(r"(?<![\w./-])(?:\S*/)?%s(?![\w.-])" % re.escape(os.path.basename(path)), t)


# CHECKBOX_BUILD_BUILDER_TOOLCHAIN: what every box now carries (relentless_box.json reach_served) is no need. History verbs
# read the candidate's ancestry in the default git_history grant; these need refs or a remote, which no box has.
_GIT_REFS = ("fetch", "pull", "branch", "for-each-ref", "reflog")


def served(cfg=None):
    """-> the reach kinds every box carries (relentless_box.json reach_served), so needs() leaves them out."""
    cfg = relentless_wall.box_config() if cfg is None else cfg
    got = set(cfg.get("reach_served") or [])
    if relentless_wall.GIT_GRANT in got and relentless_wall.GIT_GRANT not in relentless_wall.default_grants(cfg):
        got.discard(relentless_wall.GIT_GRANT)      # history is served only when every box is granted it
    return got


def needs(text, prof, carved=(), host_only=(), git_tools=(), serve=None):
    """-> ["kind: what", ...] the box cannot reach that `text` (a proof) names, once each, in order. Pure.
    `git_tools`: (path, why) rows; a proof naming one runs git inside the tool (code_review_since.py's merge-base), which
    no regex over the proof's own verbs sees: RELENTLESS_REVIEW_FINISH_TOO_BIG_TO_SKIM's gate passed one, five returns.
    `host_only`: (path, why) rows; a proof naming one (NIGHTLY_COP_REACH_FIX_ARENA_STAYS_DARK: the arena sandbox pair read
    bwrap, retired-trees git refs and the host's own DENY layout, which no read-only bind makes honest) is a need too."""
    out = []
    serve = served() if serve is None else set(serve)

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
        if relentless_wall.GIT_GRANT in serve and m.group(1) not in _GIT_REFS:
            continue
        add("git history: `git %s` (the box is an export with no .git)" % m.group(1)
            if relentless_wall.GIT_GRANT not in serve else
            "git refs: `git %s` (the box's history has HEAD at the candidate and no ref or remote)" % m.group(1))
    for m in _REMOTE.finditer(t):
        add("another machine: `%s` (the box has no ssh keys)" % m.group(1))
    for m in _WINDOWS.finditer(t):
        if "windows_build" in serve and os.path.basename(m.group(1)).lower() == "winbuild.py":
            continue
        add("a Windows program: `%s` (no Windows interop in the box)" % m.group(1))
    for path, why in git_tools:
        if _names(path, t):
            add("git history: %s runs git itself (%s; the box is an export with no .git)" % (path, why or "reads history"))
    for path, why in host_only:
        if _names(path, t):
            add("a host-only test: %s (%s)" % (path, why or "reads the host itself"))
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
    return needs(c.get("proof"), prof, carved_of(prof), host_only_rows(rules), git_tool_rows(rules))


def refusal(found, adapter_names):
    return ("the proof needs what the walled Marker's box cannot reach, so a Marker would be paid only to say CANNOT REACH "
            "(CHECKER_REACH_PROBE_BEFORE_PAYING_TWICE): %s. Rewrite the proof to run on the exported tree (relative paths, "
            "a selftest with its own fixture), or add --offbox NAME with a supervisor adapter that reads it outside (%s), "
            "or --reach-ok \"why the box can still show it\"" % ("; ".join(found), ", ".join(sorted(adapter_names)) or "none yet"))


HOLDS, DOES_NOT_HOLD, UNREAD = "holds", "does_not_hold", "unread"


def live_reading(line, check=None, now=None):
    """-> {line, state, holds, why, at}: the contract's live line checked here, by the supervisor, outside the wall.
    Three states (CHECKER_VERDICT_BUILD_CAUSE_BEFORE_RETURN, plan step 5; GPT A4): HOLDS, DOES NOT HOLD (the check read
    it and it failed), and COULD NOT READ (the reader itself raised: the supervisor's instrument failed, which says nothing
    of the work). `holds` stays True only for HOLDS."""
    now = time.time() if now is None else now
    if check is None:
        import live_line
        check = live_line.check
    try:
        why = check(line, now=now)
        state = HOLDS if why is None else DOES_NOT_HOLD
    except Exception as e:      # noqa: BLE001 - a broken reader is a reading that failed, never a dead tick
        why = "the supervisor's live check raised %s: %s" % (type(e).__name__, e)
        state = UNREAD
    return {"line": line, "state": state, "holds": state == HOLDS, "why": why, "at": now}


def write_live(box, got):
    """-> the file. Read only: the Marker reads a measurement, never edits it."""
    f = Path(box, "live.txt")
    f.write_text("live line: %s\nmeasured_at=%s outside the box by the supervisor\n%s\n" % (
        got["line"], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(got["at"])),
        "HOLDS" if got["holds"] else
        "COULD NOT READ (the supervisor's reader failed; this says nothing of the work): %s" % got["why"]
        if got.get("state") == UNREAD else "DOES NOT HOLD: %s" % got["why"]), encoding="utf-8")
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
            "does not hold. Judge whether the line is the promise the item needs. COULD NOT READ means the supervisor's "
            "own reader failed: it is no defect of the work and no --unreached of yours." % (live, box)]


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
