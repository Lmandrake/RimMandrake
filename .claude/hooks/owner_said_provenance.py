#!/usr/bin/env python3
"""owner_said_provenance -- is this quote something the OWNER actually typed?

ONE MATCHER, TWO PLACES IT RUNS
===============================
`block_forged_owner_said.py` (a PreToolUse hook) checks every owner-said quote
it can SEE in a Bash command's text. A command-text hook cannot see a quote
written into a script file, set in python's `os.environ`, or piped into `bash`
(attack A36, `Transient/owner_said_guard_review_20261011.md`). So the same
check also runs where the quote is CONSUMED -- rimflow's
`_resolve_command_seat`, broadcast.py and apply_blanket_ruling.py -- through
`verify()` below. The matching rules (whole words inside ONE owner text, a
one-word quote must be his whole message, no negator straight before it,
human-marked lines only, card text minus what we authored) live here once,
extracted unchanged from the hook; the hook's docstring is the account of why
each rule exists.

WHICH TRANSCRIPT IS "THIS SESSION" (consumer side)
==================================================
The hook is handed `transcript_path` by the harness. A consumer is not, so
`current_session()` finds it from evidence a command cannot rewrite, in order:

  1. PROCESS ANCESTRY. The nearest ancestor whose executable is the claude
     binary (`.../claude/versions/<v>`, or argv[0] `claude`). Its
     `~/.claude/sessions/<pid>.json` names the sessionId. A subagent's Bash
     call runs under the same claude process, so it reads the same file the
     hook reads (measured 2026-09-19: one shared transcript).
  2. CGROUP. Every seat's commands run in a `claude-seat-*` scope (and a
     `claude-code-bash` sub-cgroup); `setsid`/`nohup` do not leave it. The
     claude processes in that scope are the candidates.
  3. ENVIRONMENT. `CLAUDECODE` / `CLAUDE_CODE_SESSION_ID`.

The claude home is read from the password database and from the claude
process's OWN environment (`/proc/<pid>/environ`), never from this process's
`$HOME` / `$CLAUDE_CONFIG_DIR`, which a command can point at a planted file.

THE HUMAN ESCAPE (documented, deliberate)
=========================================
If NONE of the three signals is present, this is not a Claude Code session --
the owner running rimflow with his words from his own terminal -- and the
check is SKIPPED: there is no transcript to prove against and the person
typing is the authority. `verify()` returns ok.

Inside a session, a transcript that cannot be found or read is REFUSED (fail
closed): unlike the hook, a consumer refusing costs one re-run, never a wedged
session.

RESIDUALS, recorded in `Transient/pickAQ_20261011.md`: a process launched
OUTSIDE the seat's cgroup with a scrubbed environment (`systemd-run --user`,
`at`, cron) looks exactly like the owner's terminal; and an agent can edit this
file. Both leave traces (process table, git), neither is silent forgery.

SELFTEST SEAM (stricter only): `OWNER_SAID_TEST_TRANSCRIPT=<path>` is read ONLY
when no session is detected, and turns the skip into a real check against that
file. Inside a session it is ignored, so it can never loosen anything.
"""
import glob
import json
import os
import re

# Words that turn his instruction into its opposite when a quote starts just
# after them: he typed "do not push to main", the agent quotes "push to main".
NEGATORS = frozenset(
    "not never dont doesnt didnt isnt arent wasnt wont cant cannot shouldnt "
    "mustnt nor without".split())

# A boundary no match may cross: between two owner texts, around a paste, and
# where assistant-authored card text was cut out.
SEP = "\x00"


def _norm(s):
    """Lowercase, strip punctuation, collapse space -- mirrors rimflow's own
    `_norm_said` so 'Yes!' and 'yes' (and a quote reflowed across two lines
    in the transcript JSON) compare equal."""
    return " ".join("".join(c for c in s.lower() if c.isalnum() or c.isspace()).split())



def _proven(nq, segments):
    """True if the normalized quote is a run of WHOLE WORDS inside ONE segment,
    and at least one such occurrence is not straight after a negator.

    A ONE-word quote must be the whole of what he typed ("deploy" as his
    entire message): one word lifted out of a sentence -- "a", "up" --
    proves nothing about what he asked for."""
    if " " not in nq:
        return nq in segments
    needle = " %s " % nq
    for seg in segments:
        hay = " %s " % seg
        i = hay.find(needle)
        while i != -1:
            before = hay[:i].split()
            if not before or before[-1] not in NEGATORS:
                return True
            i = hay.find(needle, i + 1)
    return False


ASK_TOOL = "AskUserQuestion"

# Harness scaffolding inside a card-result string. Subtracted alongside the
# assistant's own strings so that only the owner's typing survives.
CARD_BOILERPLATE = (
    "User has answered your questions:",
    "User has answered your question:",
    "Your questions have been answered:",
    "The user answered:",
    "You can now continue with the user's answers in mind.",
    "You can now continue with these answers in mind.",
    "Read the answers carefully — they may request clarification, changes, "
    "or that you not proceed — and follow what they actually say.",
    "user notes:",
)
# Only a body that opens like an ANSWER is read. A refused card (validate-
# question-card's denial, an InputValidationError) is harness or hook prose
# that echoes our own question through repr(), escapes and all, so nothing in
# it is his. MEASURED 2026-10-11 over every saved card result: 376 + 398
# answers in the two current formats, 58 hook refusals, 8 rejections, 4
# validation errors.
CARD_ANSWER_PREFIXES = CARD_BOILERPLATE[:4]
# A card he REJECTED carries his typed reason between these two markers.
_REJECTED = re.compile(r"the user said:\n(.*?)\n\nNote: The user's next message",
                       re.S)
_REJECT_DEFAULT = "Denied by user"

_PASTE = re.compile(r"<pasted_content\b[^>]*>.*?(?:</pasted_content[^>]*>|\Z)", re.S)


def _authored_strings(tool_input):
    """-> every string in an AskUserQuestion call the ASSISTANT wrote.

    These can never authorize anything: an agent picks its own labels, so a
    label the owner merely CLICKED is not a sentence he said."""
    out = []
    for q in (tool_input or {}).get("questions") or []:
        if not isinstance(q, dict):
            continue
        out.append(q.get("question") or "")
        out.append(q.get("header") or "")
        for opt in q.get("options") or []:
            if isinstance(opt, dict):
                out.append(opt.get("label") or "")
                out.append(opt.get("description") or "")
                out.append(opt.get("preview") or "")
    return [s for s in out if isinstance(s, str) and s.strip()]


def _result_body(block):
    """Card results carry `content` as a str, or as text blocks in some harness
    versions. Anything else yields '' (that source simply contributes nothing,
    which fails CLOSED for it -- the safe direction)."""
    body = block.get("content")
    if isinstance(body, str):
        return body
    if isinstance(body, list):
        return "\n".join(
            b.get("text") or ""
            for b in body
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def _strip_authored(body, authored):
    """Remove assistant-authored text and harness boilerplate from a card
    result, leaving only what the owner typed.

    Longest-first so a label that contains a shorter label is removed whole.
    Replacement is SEP, never '' and never a newline: `_norm` folds a newline
    into a space, which spliced two surviving fragments into a sentence nobody
    typed. SEP is a hard boundary no match crosses."""
    out = body
    for s in sorted(authored, key=len, reverse=True):
        out = out.replace(s, SEP)
    for s in CARD_BOILERPLATE:
        out = out.replace(s, SEP)
    return out


def _card_text(block, authored):
    """-> the part of one card result he typed ('' if none)."""
    body = _result_body(block)
    if block.get("is_error"):
        m = _REJECTED.search(body)
        said = m.group(1).strip() if m else ""
        return "" if said == _REJECT_DEFAULT else said
    if not body.lstrip().startswith(CARD_ANSWER_PREFIXES):
        return ""
    return _strip_authored(body, authored)


def _is_human(obj):
    """True only for `origin: {"kind": "human"}`. A peer session's relay reads
    `peer`, a background task `task-notification`, and both carry text that
    is not his, so anything but `human` contributes nothing."""
    origin = obj.get("origin")
    return isinstance(origin, dict) and origin.get("kind") == "human"


def _text_of(content):
    """A prompt is a str, or a list of blocks of which only `text` is words.
    A `<pasted_content>` block inside it came from somewhere else -- the
    harness itself warns it "may contain instructions the user did not
    write" -- so it is cut out, leaving a boundary."""
    if isinstance(content, str):
        parts = [content]
    elif isinstance(content, list):
        parts = [
            b.get("text") or ""
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
    else:
        return []
    # One message is one text: an [Image] block between two of his sentences
    # does not make them two messages.
    return [_PASTE.sub(SEP, "\n".join(parts))]


def owner_texts(transcript_path):
    """-> list of every string the OWNER actually typed this session -- chat
    turns plus what he typed into question cards -- or None if the transcript
    could not be read/parsed at all (caller fails open).

    One forward pass: a tool_use always precedes its tool_result in the file,
    so AskUserQuestion calls are known by the time their answers arrive."""
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except Exception:
        return None
    texts = []
    authored_by_id = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        typ = ev.get("type")
        content = (ev.get("message") or {}).get("content")

        if typ == "attachment":
            # Typed mid-turn (MIDTURN_BLIND_1): rides the queue as an attachment.
            att = ev.get("attachment")
            if (
                isinstance(att, dict)
                and att.get("type") == "queued_command"
                and att.get("commandMode") == "prompt"
                and _is_human(att)
                and not att.get("isMeta")
            ):
                texts.extend(_text_of(att.get("prompt")))
            continue

        if typ == "assistant":
            if isinstance(content, list):
                for block in content:
                    if (
                        isinstance(block, dict)
                        and block.get("type") == "tool_use"
                        and block.get("name") == ASK_TOOL
                    ):
                        authored_by_id[block.get("id")] = _authored_strings(
                            block.get("input")
                        )
            continue

        if typ != "user":
            continue

        src = ev.get("promptSource")
        if src == "typed" or (
            src == "queued" and _is_human(ev) and not ev.get("isMeta")
        ):
            # A real chat turn, or one he typed while busy that was dequeued
            # as its own turn: every word of it is his.
            texts.extend(_text_of(content))
            continue

        # Not a typed chat turn. The only other admissible source is the answer
        # to a card WE called -- and only the part of it he typed.
        if isinstance(content, list):
            for block in content:
                if not (isinstance(block, dict) and block.get("type") == "tool_result"):
                    continue
                authored = authored_by_id.get(block.get("tool_use_id"))
                if authored is None:
                    continue          # not a card result -- ordinary tool output
                texts.append(_card_text(block, authored))
    return texts


# --------------------------------------------------------------------------
# quote proof over a list of owner texts
# --------------------------------------------------------------------------
def segments_of(texts):
    """One segment per owner text, split again at every SEP: a quote must sit
    inside one of them as whole words (no mid-word, no cross-turn splice)."""
    return [_norm(part) for t in texts for part in t.split(SEP)]


def quote_proven(quote, texts):
    """True if `quote` is provably his under the strict rules."""
    nq = _norm(quote or "")
    return bool(nq) and _proven(nq, segments_of(texts))


# --------------------------------------------------------------------------
# which session is this (consumer side)
# --------------------------------------------------------------------------
def _real_home():
    try:
        import pwd
        return pwd.getpwuid(os.getuid()).pw_dir
    except Exception:
        return os.path.expanduser("~")


def _ppid(pid):
    try:
        with open("/proc/%d/stat" % pid) as fh:
            data = fh.read()
        return int(data[data.rindex(")") + 2:].split()[1])
    except Exception:
        return None


def _is_claude(pid):
    try:
        exe = os.readlink("/proc/%d/exe" % pid)
    except Exception:
        exe = ""
    if "/claude/versions/" in exe:
        return True
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as fh:
            argv = fh.read().split(b"\0")
    except Exception:
        return False
    first = os.path.basename(argv[0].decode("utf-8", "replace")) if argv and argv[0] else ""
    if first == "claude":
        return True
    # a node-hosted install runs `node .../bin/claude` or `node .../claude-code/cli.js`
    return first.startswith("node") and len(argv) > 1 and (
        argv[1].endswith(b"/claude") or b"claude-code" in argv[1])


def _claude_ancestor():
    pid = os.getpid()
    for _ in range(64):
        pid = _ppid(pid)
        if not pid or pid <= 1:
            return None
        if _is_claude(pid):
            return pid
    return None


_SEAT_CGROUP = re.compile(r"(?:^|/)(?:claude-seat-[^/]*|claude-code-bash)(?:/|$)")


def _cgroup():
    try:
        with open("/proc/self/cgroup") as fh:
            for line in fh:
                parts = line.strip().split(":", 2)
                if len(parts) == 3 and _SEAT_CGROUP.search(parts[2]):
                    return parts[2]
    except Exception:
        pass
    return None


def _cgroup_claude_pids(cg):
    """claude processes in the same seat scope as this one."""
    comps = cg.strip("/").split("/")
    scope = None
    for i, c in enumerate(comps):
        if c.startswith("claude-seat-") or c.endswith(".scope"):
            scope = "/sys/fs/cgroup/" + "/".join(comps[:i + 1])
            break
    if scope is None:
        return []
    pids = []
    for f in glob.glob(scope + "/**/cgroup.procs", recursive=True) + [scope + "/cgroup.procs"]:
        try:
            with open(f) as fh:
                pids.extend(int(x) for x in fh.read().split())
        except Exception:
            continue
    return sorted({p for p in pids if _is_claude(p)})


def _proc_env(pid):
    try:
        with open("/proc/%d/environ" % pid, "rb") as fh:
            items = fh.read().split(b"\0")
    except Exception:
        return {}
    out = {}
    for it in items:
        if b"=" in it:
            k, v = it.split(b"=", 1)
            out[k.decode("utf-8", "replace")] = v.decode("utf-8", "replace")
    return out


def _claude_dirs(pid=None):
    dirs = []
    if pid:
        cfg = _proc_env(pid).get("CLAUDE_CONFIG_DIR")
        if cfg:
            dirs.append(cfg)
    dirs.append(os.path.join(_real_home(), ".claude"))
    return dirs


def _transcripts_for(session_id, dirs):
    out = []
    if not session_id or not re.match(r"^[\w-]+$", session_id):
        return out
    for d in dirs:
        out.extend(glob.glob(os.path.join(d, "projects", "*", session_id + ".jsonl")))
    return out


def _session_of_pid(pid, dirs):
    for d in dirs:
        try:
            with open(os.path.join(d, "sessions", "%d.json" % pid)) as fh:
                sid = json.load(fh).get("sessionId")
            if sid:
                return sid
        except Exception:
            continue
    return None


def current_session():
    """-> (in_session, [transcript paths], how).

    in_session False means no Claude Code signal at all (the owner's terminal).
    In a session, the list may be empty when no transcript could be found."""
    anc = _claude_ancestor()
    cg = _cgroup()
    env_sid = os.environ.get("CLAUDE_CODE_SESSION_ID")
    env_in = bool(os.environ.get("CLAUDECODE") or env_sid)
    if not (anc or cg or env_in):
        return False, [], "outside"
    pids = [anc] if anc else (_cgroup_claude_pids(cg) if cg else [])
    paths = []
    for pid in pids:
        dirs = _claude_dirs(pid)
        sid = _session_of_pid(pid, dirs)
        if sid:
            paths.extend(_transcripts_for(sid, dirs))
    how = ("claude pid %s" % anc) if anc else ("cgroup %s" % cg if cg else "environment")
    if not paths and env_sid:
        # last resort: the environment's id, looked up only in the REAL claude home
        paths = _transcripts_for(env_sid, _claude_dirs(anc))
        how += " (session id from environment)"
    return True, sorted(set(paths)), how


# --------------------------------------------------------------------------
# the consumer entry point
# --------------------------------------------------------------------------
def verify(quote, who="this tool"):
    """-> (ok, message). ok is True when the quote is proven in this session's
    transcript, or when no Claude Code session is present (the owner at his
    own terminal). Never raises."""
    try:
        in_session, paths, how = current_session()
        if not in_session:
            planted = os.environ.get("OWNER_SAID_TEST_TRANSCRIPT")
            if not planted:
                return True, "outside a Claude Code session: the check is skipped"
            paths, how = [planted], "test transcript, no session present"
        if not paths:
            return False, _refusal(quote, who, "this is a Claude Code session (%s) but "
                                   "its transcript could not be found, so nothing can "
                                   "prove the quote" % how)
        for p in paths:
            texts = owner_texts(p)
            if texts is not None and quote_proven(quote, texts):
                return True, "proven against %s" % p
        return False, _refusal(quote, who, "it is not in anything the owner typed this "
                               "session (%s)" % how)
    except Exception as e:                       # noqa: BLE001
        return False, _refusal(quote, who, "the provenance check itself failed: %s" % e)


def _refusal(quote, who, why):
    return (
        "REFUSED by %s: the quote %r cannot be proven to be the owner's words -- %s.\n\n"
        "This check runs where the quote is USED (owner_said_provenance.verify), so it "
        "applies however the quote arrived -- a flag, an environment variable, a script "
        "file, a pipe into bash.\n"
        "The quote must be WHOLE WORDS from ONE thing he typed this session (a chat "
        "turn, or text he typed into a question card -- never a label he clicked), "
        "keep any 'not'/'never' before it, and be his whole message if it is one word.\n"
        "If he did not say it: drop the quote and act under your own seat. If he did: "
        "have him say it in this session.\n"
        "The owner running this from his own terminal (no Claude Code session) is not "
        "checked." % (who, quote, why))
