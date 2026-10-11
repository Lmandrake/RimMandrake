#!/usr/bin/env python3
"""PreToolUse hook -- nothing but the ledger's own tools may WRITE a ledger shard.

WHY
===
Every owner-said check (`owner_said_provenance.verify`, wired into rimflow,
broadcast.py, apply_blanket_ruling.py, modcheck and art.py) runs inside the TOOL
that writes the event. A line appended to the shard directly --
`echo '{"event":"close",...,"ownerSaid":"..."}' >> infrastructure/state/ledger/events/FOUNDRY.jsonl`
-- never meets any of them (pickAS 2026-10-11, `Transient/pickAS_20261011.md`).

`queue_lint.py` already refuses the obvious forms for the rimflow ledger: a literal
path after `>`/`>>`, `tee`, `cp`, `mv`, `sed -i`, a python `open(<literal>, 'a')`,
and Write/Edit. It does NOT cover the art ledger or the code-review records, and it
reads the command as text, so a path in a variable, a `cd` into the events dir,
`Path(...).open('a')`, `write_text`, a python heredoc, `sh -c` or `find -exec` all
pass it. This hook reuses the shell/python write analyser of
`block_transcript_tamper.py` (variables, for-loops, cd, symlinks, globs, nested
shells, heredocs, inline python by `ast`) with a different protected set.

WHAT IS PROTECTED (in any clone, matched on the path, not on one repo root)
==========================================================================
  infrastructure/state/ledger/events.jsonl          frozen rimflow head
  infrastructure/state/ledger/events/**             rimflow shards
  infrastructure/state/art/events/**                art ledger shards + archive/
  infrastructure/state/code_review/**.jsonl         code-review records
A directory or glob that lands inside one of those counts (`mv x.jsonl events/`).

THE ALLOW-LIST (by command prefix)
==================================
The sanctioned writers: `rimflow` / `rimflow/cli.py`, `./game`, `ledger_sync.py`,
`art.py rotate`, `repair_torn_ledger.py`, `repair_torn_art_events.py`, `code_review_status.py`. A simple command
that IS one of them is not analysed -- their own writes take the lock and go through
the owner-said check. A redirect is still checked whoever runs it:
`rimflow show > …/FOUNDRY.jsonl` truncates the shard and is refused. In practice the
analyser never flags a script FILE anyway (see LIMITS), so the list chiefly
documents who may write.

NOT REFUSED: reading (`cat`, `grep`, `json.load(open(p))`), `git` (checkout,
pull, merge write shards through git's own machinery and are judged by the
pre-push lint), and commit pathspecs.

LIMITS / BACKSTOP
=================
A script FILE that appends (`python3 forge.py`) or a path assembled from fragments
is invisible here, exactly as for the transcript hook. The backstop is the pre-push
`ledger_lint.py` (`infrastructure/githooks/pre-push` + `block_ledger_lint.py`): it
refuses NOT_APPEND (a line on origin edited or removed) and torn lines for
`ledger/events/` and `code_review/` -- but an APPENDED forged line is the legal shape
and passes it, and it does not read `art/events/` at all.

Fails OPEN on any internal error. Selftest: `selftest_block_ledger_shard_write.py`.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import block_transcript_tamper as btt  # noqa: E402

_PROT_DIRS = ("ledger/events", "art/events", "code_review")
_PROT_RE = re.compile(
    r"/infrastructure/state/(?:ledger/events\.jsonl$|ledger/events(?:/|$)|art/events(?:/|$)"
    r"|code_review(?:/|$))")
_MENTION_RE = re.compile(
    r"(?:ledger[/\\]+events|art[/\\]+events|state[/\\]+code_review)", re.I)


def _is_protected_abs(p):
    p = p.replace("\\", "/")
    g = btt._GLOB.search(p)
    if g:
        prefix = p[:g.start()]
        # a glob whose literal part is already inside a protected dir ...
        if _PROT_RE.search(prefix):
            return True
        # ... or stops partway along the path TO one (`state/*/events/X.jsonl`)
        i = prefix.rfind("/infrastructure/state/")
        if i < 0:
            return False
        tail = prefix[i + len("/infrastructure/state/"):]
        last = os.path.basename(p)
        return (any(d.startswith(tail) for d in _PROT_DIRS)
                and (last.endswith((".jsonl", ".*", "*")) or "." not in last))
    m = _PROT_RE.search(p)
    if not m:
        return False
    rest = p[m.start():]
    if rest.endswith("/ledger/events.jsonl"):
        return True
    last = os.path.basename(p)
    return last.endswith(".jsonl") or "." not in last      # a shard, or a directory


def is_protected(p, cwd):
    a = btt._norm_path(p, cwd)
    if _is_protected_abs(a):
        return True
    try:
        r = os.path.realpath(a)
    except Exception:
        return False
    return r != a and _is_protected_abs(r)


def mentions(text):
    return bool(_MENTION_RE.search(text or ""))


def is_ancestor(p, cwd):
    """A tree copy/extract INTO infrastructure/state or its parents. Only flagged when
    the target dir actually holds a protected dir on disk -- a guess here would refuse
    every `tar -C <somewhere>`."""
    a = btt._norm_path(p, cwd)
    for d in _PROT_DIRS:
        for base in (a, os.path.join(a, "infrastructure", "state"),
                     os.path.join(a, "state")):
            if os.path.isdir(os.path.join(base, d)) and (base == a or base.startswith(a + "/")):
                return True
    return False


# The sanctioned writers. Matched on the simple command's words after wrappers
# (env, timeout, sudo ...) are stripped by the analyser.
_ALLOWED = (
    (re.compile(r"(?:^|/)rimflow$"), None),
    (re.compile(r"(?:^|/)game$"), None),
    (re.compile(r"(?:^|/)rimflow/cli\.py$"), None),
    (re.compile(r"(?:^|/)ledger_sync\.py$"), None),
    (re.compile(r"(?:^|/)repair_torn_ledger\.py$"), None),
    (re.compile(r"(?:^|/)repair_torn_art_events\.py$"), None),
    (re.compile(r"(?:^|/)code_review_status\.py$"), None),
    (re.compile(r"(?:^|/)art/art\.py$|^art\.py$"), "rotate"),
)


def allowed(words):
    """True if this simple command is one of the sanctioned ledger writers."""
    words = [w for w in words if isinstance(w, str)]
    if not words:
        return False
    w = words
    if btt._INTERP_PY.match(w[0]):
        w = [a for a in w[1:] if not a.startswith("-") or a == "-"]
        if not w or w[0] == "-":
            return False
    prog, rest = w[0], w[1:]
    for rx, verb in _ALLOWED:
        if rx.search(prog):
            return verb is None or (rest[:1] == [verb])
    return False


_real_simple = btt._simple
_real_target = btt._target
_real_ev = btt._PyEval._ev
# What a value nobody can resolve from the text becomes: a glob wildcard, so the
# literal parts around it still decide (`f".../events/{seat}.jsonl"` -> `.../events/*.jsonl`,
# protected; `f"/tmp/union_{name}"` -> `/tmp/union_*`, not).
_UNKNOWN = re.compile(r"\$\([^)]*\)|`[^`]*`|\$\{?\w+\}?|\{\}")


def _simple(words, ctx, depth):
    plain = [x for x in words if not isinstance(x, tuple)]
    while plain and re.match(r"^[A-Za-z_]\w*=", plain[0]):
        plain = plain[1:]
    if allowed(plain):
        return
    if plain and os.path.basename(plain[0]) in ("cd", "pushd"):
        # The transcript hook marks a cd to an ANCESTOR of its area as touching it;
        # every cd to a repo root is that here, so only a cd INTO a shard dir counts.
        saved = ctx.mention
        _real_simple(words, ctx, depth)
        ctx.mention = saved or (ctx.cwd_known and is_protected(ctx.cwd, "/"))
        return
    if plain and os.path.basename(plain[0]) == "find":
        # `find <shard dir> -exec sh -c '... >> "$1"' _ {} ;` -- the `{}` is a shard
        roots = []
        for a in plain[1:]:
            if a.startswith(("-", "(", "!")):
                break
            roots.append(a)
        if any(is_protected(r, ctx.cwd) for r in roots):
            saved, ctx.mention = ctx.mention, True
            try:
                return _real_simple(words, ctx, depth)
            finally:
                ctx.mention = saved
    return _real_simple(words, ctx, depth)


def _target(tok, ctx, why, ancestor_ok=False):
    """The transcript hook refuses ANY unresolvable target once the command mentions
    its area. Ledger paths are mentioned constantly (every commit pathspec, every
    census), so here an unresolvable target is refused only when the token itself
    names a shard, the cwd is inside a shard dir, or a `find` over a shard dir feeds
    it; otherwise its unknown parts become `*` and the literal rest is judged."""
    if btt._resolve(tok, ctx.vals) is not None and ctx.cwd_known:
        return _real_target(tok, ctx, why, ancestor_ok)
    if ctx.mention or mentions(tok):
        raise btt.Refuse("%s: target %r cannot be resolved from the command text, and "
                         "it names a ledger shard" % (why, tok))
    if not ctx.cwd_known and not tok.startswith(("/", "~", "$HOME", "${HOME}")):
        return
    glob_tok = _UNKNOWN.sub("*", tok)
    if glob_tok.strip("*/") and is_protected(glob_tok, ctx.cwd):
        raise btt.Refuse("%s writes %r" % (why, glob_tok))


# An unknown python value. A glob wildcard, so a path built around it is judged by its
# literal parts; it carries a `w` so that, used as an open() MODE, it still reads as a
# write (an unknown mode must never pass as read-only).
_UNK = "*w*"


def _ev(self, node):
    r = _real_ev(self, node)
    if r is not None:
        return r
    import ast
    if isinstance(node, ast.JoinedStr):
        out, lit = "", False
        for v in node.values:
            if isinstance(v, ast.Constant):
                out += str(v.value)
                lit = lit or bool(str(v.value).strip("/"))
            elif isinstance(v, ast.FormattedValue):
                out += self.ev(v.value) or _UNK
        return out if lit else _UNK
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.Add)):
        a, b = self.ev(node.left) or _UNK, self.ev(node.right) or _UNK
        return os.path.join(a, b) if isinstance(node.op, ast.Div) else a + b
    return _UNK


# Unparsable inline python: refused only when a write construct sits right next to a
# shard path (the transcript hook's "names the area AND writes anywhere" is far too
# broad for paths that every census and commit names).
_PY_FALLBACK = re.compile(
    r"(?:ledger/events|art/events|state/code_review)[^\n]{0,160}?"
    r"(?:['\"]\s*,\s*(?:mode\s*=\s*)?['\"](?=[rbt]*[wax+])[rwax+bt]{1,4}['\"]"
    r"|\.write_text\(|\.write_bytes\()")


def _install():
    """Point the shared analyser at the ledger set. This process only."""
    btt._PY_WRITE_FALLBACK = _PY_FALLBACK
    btt.is_protected = is_protected
    btt.mentions = mentions
    btt.is_ancestor_of_projects = is_ancestor
    btt._simple = _simple
    btt._target = _target
    btt._PyEval._ev = _ev


def offence(payload):
    _install()
    tool = payload.get("tool_name")
    ti = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or os.getcwd()
    try:
        if tool in btt.WRITE_TOOLS:
            p = ti.get("file_path") or ti.get("notebook_path") or ""
            if p and is_protected(p, cwd):
                return "%s targets %r" % (tool, p)
            return None
        if tool == "Bash":
            cmd = ti.get("command") or ""
            ctx = btt.Ctx(cwd, cmd)
            ctx.mention = False          # see _target: a mention alone refuses nothing
            btt.analyse_shell(cmd, ctx)
    except btt.Refuse as e:
        return str(e).replace("the transcript area", "a ledger shard")
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    try:
        why = offence(payload)
    except Exception:
        return 0                          # fail open
    if not why:
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Blocked: this writes a ledger shard directly (%s).\n\n"
            "infrastructure/state/ledger/events/*.jsonl, art/events/** and "
            "code_review/*.jsonl are append-only and written ONLY by their tools, which "
            "take the lock and prove any --owner-said quote:\n"
            "    rimflow <verb> ...          the work ledger\n"
            "    art.py install|purge|ingest|enact|rotate   the art ledger\n"
            "    code_review_status.py mark-clean           review records\n"
            "    ledger_sync.py / repair_torn_ledger.py / repair_torn_art_events.py   rescue and repair\n"
            "Reading a shard is fine; write a report to a path of its own. To restore a "
            "shard from git, `git checkout <rev> -- <shard>` (not `git show … > shard`).\n"
            "Pre-push, ledger_lint.py also refuses a shard line edited or removed in "
            "place. See block_ledger_shard_write.py." % why)}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
