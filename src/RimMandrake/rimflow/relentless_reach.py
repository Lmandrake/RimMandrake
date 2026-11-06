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
import posixpath
import re
import time
from pathlib import Path

import relentless_wall

# a path-shaped word: absolute, home-relative, or a Windows drive path
_PATH = re.compile(r"(?<![\w.~$@+/\\-])(?:[A-Za-z]:[\\/]|~/|\$HOME/|/)[\w.~$@+-]*(?:[/\\][\w.~$@+-]*)*")
# a parenthesised aside is the worker's prose about the proof ("(the retry cases prove a dotnet.exe launch ...)"): a census of
# the store's 603 contracts found it the main false alarm. `$(...)` and `<(...)` are commands and stay, and so is a subshell:
# a group holding a shell operator, `(cd x && git log)`, or one that starts with a program, `(git log -1)`,
# `(python3 code_review_since.py ...)` (REACH_GATE_HARDEN_PARENS_HIDE_THE_TOOL: deleting those hid the tool from the gate).
_PROSE = re.compile(r"(?<![$\w<>])\(([^()]*)\)")
_SHELL_OP = re.compile(r"&&|\|\||[;|`]|\$\(")
_PROGRAMS = frozenset("""git python python3 bash sh zsh env sudo timeout nice xargs command exec cd cat test grep egrep rg ls
    find head tail wc jq sed awk echo printf true false ssh scp rsync sftp tailscale powershell pwsh wslpath cmd dotnet make
    diff cmp stat du df cp mv rm mkdir touch tee sort uniq cut tr curl wget readlink realpath file sha256sum md5sum [
    rimflow""".split())
_PROGRAM_FILE = re.compile(r"^(?:\.{0,2}/)?[\w./~$-]*\.(?:py|sh|exe|ps1|bat|cmd)$|^\.{1,2}/\S+$", re.I)
_VAR = re.compile(r"\$\{(\w+)\}|\$(\w+)")
# where a simple command ends (for $VAR scope): an operator, a newline, a subshell or command substitution opening or closing
_SEP = re.compile(r"\$\(|&&|\|\||[;&|\n()`]")
_ASSIGN = re.compile(r"([A-Za-z_]\w*)=('[^']*'|\"[^\"]*\"|[^\s;&|()`'\"]*)")
# what may stand before a persistent assignment: an inner shell's opening quote, a keyword, `export`/`declare`
_ASSIGN_LEAD = re.compile(r"^\s*(?:(?:bash|sh|zsh)\s+-l?c\s+)?['\"]?\s*(?:(?:then|do|else|!|\{)\s+)*"
                          r"(?:(?:export|declare|readonly|local|typeset)\s+(?:-\w+\s+)*)?")
# where a command starts: the line, a shell operator, a subshell, `!`, then any VAR=value and a timeout. Programs named in
# prose ("git grep shows ..." at a line's start is still a command a Marker would run) are matched only here.
_START = (r"(?:^|&&|\|\||[;|`(]|\$\(|!|\b(?:then|do|if|elif|while|until|else|time)\b)\s*"
          r"(?:(?:sudo|env|xargs|nice|command|exec|timeout\s+\S+)\s+|"
          r"(?:bash|sh|zsh)\s+-l?c\s+['\"]|[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*(?:\S*/)?")
# any git verb: without the history grant every one but these reads a .git the box lacks
_GIT = re.compile(_START + r"git\s+(?:(?:-C|-c)\s+\S+\s+|--\S+\s+)*([a-z][\w-]*)\b([^\n;&|)]*)", re.M)
_GIT_LOCAL = frozenset(("init", "version", "help", "hash-object"))
# git's own subcommands (`git help -a`, git 2.53): "git clones the tree" in prose names none
_GIT_VERBS = frozenset("""
    add am annotate apply archive backfill bisect blame branch bugreport bundle cat-file check-attr check-ignore
    check-mailmap check-ref-format checkout checkout-index cherry cherry-pick clean clone column commit 
    commit-graph commit-tree config count-objects credential crypt daemon describe diagnose diff diff-files diff-index
    diff-pairs diff-tree difftool fast-export fast-import fetch fetch-pack filter-branch fmt-merge-msg 
    for-each-ref for-each-repo fsck gc get-tar-commit-id grep hash-object help hook http-backend imap-send index-pack
    init interpret-trailers last-modified log ls-files ls-remote ls-tree mailinfo mailsplit maintenance merge
    merge-base merge-file merge-index merge-one-file merge-tree mergetool mktag mktree multi-pack-index mv 
    name-rev notes pack-objects pack-redundant pack-refs patch-id prune prune-packed pull push range-diff read-tree
    rebase reflog refs remote repack replace replay repo request-pull rerere reset restore rev-list rev-parse
    revert rm scalar send-email send-pack shortlog show show-branch show-index show-ref sparse-checkout stash
    status stripspace submodule switch symbolic-ref tag unpack-file unpack-objects update-index update-ref
    update-server-info var verify-commit verify-pack verify-tag version whatchanged worktree write-tree""".split())
_REMOTE = re.compile(_START + r"(ssh|scp|rsync|tailscale|sftp)\s", re.M)
_WINDOWS = re.compile(_START + r"(?:python3?\s+)?(\S*winbuild\.py|\S+\.exe|powershell|pwsh|wslpath)\b", re.M | re.I)
# a quote inside a word: `/sec""ret/x` is the shell's /secret/x
_CONCAT = re.compile(r"(?<=[\w/.~-])['\"]+(?=\S)|(?<=\S)['\"]+(?=[\w/.~-])")


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
    if p.startswith("/"):
        p = posixpath.normpath(p)       # `/tmp/../secret/x` is /secret/x
        p = "/" + p.lstrip("/")
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
    t = strip_comments((contract or {}).get("proof") or "")
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


_WORD_START = frozenset(" \t\n;&|()<>")


def strip_comments(t):
    """-> `t` with its shell comments removed, quoting respected (REACH_GATE_HARDEN_PARENS_HIDE_THE_TOOL): `#` opens one
    only at a word's start outside quotes, so `printf ' # x'; tool` keeps the tool and `true;# tool` drops it. `$(...)`
    and backticks open a fresh context inside double quotes, as in bash. An unclosed quote keeps the rest: text the gate
    keeps can only add a need, never hide one."""
    t = t or ""
    out, ctx, i, n, start = [], ["top"], 0, len(t), True
    while i < n:
        c, top = t[i], ctx[-1]
        if top == "'":
            if c == "'":
                ctx.pop()
            out.append(c)
            i, start = i + 1, False
            continue
        if c == "\\" and i + 1 < n:
            out.append(t[i:i + 2])
            i, start = i + 2, False
            continue
        if t.startswith("$(", i):
            ctx.append("(")
            out.append("$(")
            i, start = i + 2, True
            continue
        if c == "`":
            if top == "`":
                ctx.pop()
            else:
                ctx.append("`")
            out.append(c)
            i, start = i + 1, top != "`"
            continue
        if top == '"':
            if c == '"':
                ctx.pop()
            out.append(c)
            i, start = i + 1, False
            continue
        if c in "'\"":
            ctx.append(c)
        elif c == "(":
            ctx.append("(")
        elif c == ")" and top == "(":
            ctx.pop()
        elif c == "#" and start:
            j = t.find("\n", i)
            i = n if j < 0 else j
            continue
        start = c in _WORD_START
        out.append(c)
        i += 1
    return "".join(out)


def _is_command(body):
    """True when a parenthesised group's body is a subshell a Marker would run, not prose: it holds a shell operator, or
    opens with a command environment, a known program, a script or a path, or its second word is a flag (`(tar -cf ...)`)."""
    if _SHELL_OP.search(body):
        return True
    w = [x.strip("'\"") for x in body.split()]
    i = 0
    while i < len(w) and re.match(r"^[A-Za-z_]\w*=", w[i]):
        i += 1                  # `(X=1 tool)`: a command environment, then the program
    if i == len(w):
        return i > 0
    return (i > 0 or "/" in w[i] or os.path.basename(w[i]) in _PROGRAMS or bool(_PROGRAM_FILE.match(w[i]))
            or (i + 1 < len(w) and re.match(r"^--?[A-Za-z0-9]", w[i + 1]) is not None))


def _unprose(t):
    """-> `t` without its parenthesised prose asides, innermost first; a subshell stays (and so does any group around it)."""
    while True:
        u = _PROSE.sub(lambda m: m.group(0) if _is_command(m.group(1)) else " ", t)
        if u == t:
            return t
        t = u


def _variants(t, env):
    """-> [t expanded with each name's first value, then one text per other value a name may hold]. `env`: name -> tuple of
    the values it may hold at this point (an assignment the shell may skip leaves both)."""
    def sub(pick):
        return _VAR.sub(lambda v: pick.get(v.group(1) or v.group(2), env.get(v.group(1) or v.group(2), (v.group(0),))[0]), t)
    out = [sub({})]
    for v in dict.fromkeys(m.group(1) or m.group(2) for m in _VAR.finditer(t)):
        for alt in env.get(v, ())[1:]:
            x = sub({v: alt})
            if x not in out:
                out.append(x)
    return out


def _assign(seg, env, persist, maybe):
    """-> `seg`'s expansions, applying its assignments to `env` when `persist` and the segment holds nothing but
    assignments (after `export`): each value is read with the env left by the ones before it (`A=/x B=$A/y`). `X=1 tool $X`
    is a command environment: bash expands `$X` before X=1 exists and X=1 dies with the tool, so it changes nothing here.
    `maybe`: the shell may skip it (`false && X=1`), so X keeps its old values beside the new. A value the gate cannot know
    (`X=$(...)`, empty) leaves X as it was."""
    lead = _ASSIGN_LEAD.match(seg).end()
    got, pos = [], lead
    while True:
        while pos < len(seg) and seg[pos].isspace():
            pos += 1
        m = _ASSIGN.match(seg, pos)
        if not m:
            break
        got.append(m)
        pos = m.end()
        if pos < len(seg) and not seg[pos].isspace() and seg[pos] not in "'\"":
            return _variants(seg, env)  # `X=a$b...` or an odd word: not a plain assignment
    if not persist or not got or seg[pos:].strip(" \t'\"{}"):
        return _variants(seg, env)
    out, last = [seg[:lead]], lead
    for m in got:               # left to right: `A=/x B=$A/y` sees the new A
        k, v = m.group(1), m.group(2)
        vals = (v.strip("'"),) if v.startswith("'") else tuple(_variants(v.strip('"'), env))
        out.append(seg[last:m.start(2)] + (v if v.startswith("'") else _variants(v, env)[0]))
        last = m.end()
        if v and v not in ('""', "''"):
            env[k] = tuple(dict.fromkeys(vals + (env.get(k, ()) if maybe else ())))
    out.append(seg[last:])
    head = "".join(out)
    return [head] + [x for x in _variants(seg, env)[1:] if x != head]


_INNER_SHELL = re.compile(r"(?:^|[\s;&|(])(?:bash|sh|zsh)(?:\s+-\w+)*\s+-\w*c\s*$")


def expand_vars(t, env):
    """-> `t` with each `$VAR` replaced by its value AT THAT POINT (REACH_GATE_HARDEN_PARENS_HIDE_THE_TOOL): the box's env,
    then the proof's own persistent assignments in order. A later assignment, a command-local `X=1 tool`, a pipeline's
    and a subshell's (`(X=1)`, `$(...)`, backticks, `bash -c '...'`) never reach back or out; quoted text is no command.
    A name that may hold two values (an assignment after `&&`/`||`) gives each its own copy of the command, appended on
    its own line, so no path it may read goes unchecked. An unknown name stays `$NAME`."""
    t = t or ""
    env0 = {k: (v,) for k, v in (env or {}).items()}
    out, extra, seg = [], [], []
    ctx = [("top", False)]                      # (kind, whether it opened an env scope)
    envs = [env0]
    prev = [None]                               # the operator before the current segment

    def flush(op):
        text = "".join(seg)
        seg.clear()
        if not text:
            return
        piped = prev[0] == "|" or op == "|"
        got = _assign(text, envs[-1], persist=not piped, maybe=prev[0] in ("&&", "||"))
        out.append(got[0])
        extra.extend(got[1:])

    def boundary(op, kind=None, scope=False, close=False):
        flush(op)
        if close:
            k, sc = ctx.pop()
            if sc and len(envs) > 1:
                envs.pop()
        if kind:
            ctx.append((kind, scope))
            if scope:
                envs.append(dict(envs[-1]))
        out.append(op)
        prev[0] = op if op in ("&&", "||", "|") else None
    i, n = 0, len(t)
    while i < n:
        c, top = t[i], ctx[-1][0]
        quoted = top in ("'", '"')
        if top == "'" and c != "'":
            seg.append(c)
            i += 1
            continue
        if c == "\\" and i + 1 < n:
            seg.append(t[i:i + 2])
            i += 2
            continue
        if top == '"' and c not in '"$`':
            seg.append(c)
            i += 1
            continue
        if c in "'\"" and c == top:
            if ctx[-1][1]:
                boundary(c, close=True)         # an inner shell's script ends
            else:
                ctx.pop()
                seg.append(c)
            i += 1
            continue
        if c in "'\"" and not quoted:
            if _INNER_SHELL.search("".join(seg)):
                boundary(c, kind=c + "script", scope=True)
            else:
                ctx.append((c, False))
                seg.append(c)
            i += 1
            continue
        if t.startswith("$(", i):
            boundary("$(", kind="(", scope=True)
            i += 2
            continue
        if c == "`":
            if top == "`":
                boundary(c, close=True)
            else:
                boundary(c, kind="`", scope=True)
            i += 1
            continue
        if quoted:
            seg.append(c)
            i += 1
            continue
        if top.endswith("script") and c == top[0]:
            boundary(c, close=True)
            i += 1
            continue
        if c == "(":
            boundary(c, kind="(", scope=True)
            i += 1
            continue
        if c == ")":
            if top == "(":
                boundary(c, close=True)
            else:
                seg.append(c)
            i += 1
            continue
        op = next((o for o in ("&&", "||") if t.startswith(o, i)), None) or (c if c in ";&|\n" else None)
        if op:
            boundary(op)
            i += len(op)
            continue
        seg.append(c)
        i += 1
    flush(None)
    return "".join(out) + "".join("\n" + x for x in extra)


# CHECKBOX_BUILD_BUILDER_TOOLCHAIN: what every box now carries (relentless_box.json reach_served) is no need. History verbs
# read the candidate's ancestry in the default git_history grant; these need refs or a remote, which no box has.
_GIT_REFS = ("fetch", "pull", "push", "branch", "for-each-ref", "reflog", "ls-remote", "remote", "submodule", "clone",
             "worktree", "tag")
# an argument that names a ref the history grant does not carry (`git show origin/main`, `git log --all`)
_REF_ARG = re.compile(r"(?:^|\s)(?:origin|upstream)/\S*|@\{|--(?:all|branches|remotes|tags)\b|\brefs/\S*|"
                      r"\b(?:FETCH_HEAD|ORIG_HEAD|MERGE_HEAD)\b|(?:^|\s)(?:main|master)(?=\s|$|\.\.|~|\^)")


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
    t = strip_comments(text or "")      # a shell comment is the worker's prose about the proof, not what it runs
    t = expand_vars(t, prof.get("env") or {})  # "$RM_DATA_ROOT/x" is the masked root, read where it is used
    t = _unprose(t)
    for m in _PATH.finditer(_CONCAT.sub("", t)):
        w = m.group(0)
        if len(w) > 1 and hidden(w, prof, carved):
            add("hidden path: %s" % w.rstrip(".,;:)'\""))
    for m in _GIT.finditer(t):
        verb, args = m.group(1), m.group(2)
        if verb not in _GIT_VERBS:
            continue
        if relentless_wall.GIT_GRANT not in serve:
            if verb not in _GIT_LOCAL:
                add("git history: `git %s` (the box is an export with no .git)" % verb)
        elif verb in _GIT_REFS:
            add("git refs: `git %s` (the box's history has HEAD at the candidate and no ref or remote)" % verb)
        elif _REF_ARG.search(args):
            add("git refs: `git %s` names a ref (%s) (the box's history has HEAD at the candidate and no ref or remote)"
                % (verb, _REF_ARG.search(args).group(0).strip()))
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
