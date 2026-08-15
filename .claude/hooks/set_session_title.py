#!/usr/bin/env python3
"""SessionStart + UserPromptSubmit hook — name the CONVERSATION after the agent.

WHY
===
Rule 0 names the *terminal window*, which is what the owner reads off the
taskbar. It does nothing for the second namespace: the conversation list, where
four identical chats appear under auto-generated names (`rimworld-9f`,
`rimworld-4c`) that carry no role. Rule 6b is the standing note that agents can
tell each other apart only by address, never by name.

`/rename` fixes exactly this — but `/rename` is a SLASH COMMAND, i.e. user
input. An agent cannot type it. Writing "run /rename" into an agent definition
produces an instruction the agent cannot execute, which degrades to "ask the
owner to type it" — a keystroke per session, pushed onto the one person Rule 0
exists to stop doing this work.

Claude Code exposes the same capability to hooks. Verified 2026-08-12 against
the binary (version 2.1.229, not assumed): the `SessionStart` and
`UserPromptSubmit` hook-output schemas each carry a `sessionTitle` field,
described in the binary as "Set the session title". No other event has it.

So the agent runs ONE command — `src/RimMandrake/Utils/set_agent_window.sh BUILD` — and both
namespaces are named: the window by the OSC escape, the conversation by this
hook reading what that script recorded.

HOW THE ROLE IS FOUND
=====================
`set_agent_window.sh` writes the finished title to

    .claude/session_roles/<CLAUDE_CODE_SESSION_ID>

and this hook reads it back by the `session_id` on the hook payload. The two
agree because Claude Code exports the same id to the Bash tool that it puts on
the hook JSON.

FALLBACK: `AGENT_SEAT` FROM THE ENVIRONMENT
===========================================
The Windows Terminal seat profiles (`src/RimMandrake/Utils/install_wt_seat_profiles.py`) export
`AGENT_SEAT=<SEAT>` before launching Claude Code, so a tab opened from a profile
declares its seat with nothing typed. When no role file exists for this session
and `AGENT_SEAT` is set, this hook records the role itself — the same file
`set_agent_window.sh` would have written, same `AGENT <SEAT>` format — and then
proceeds normally, so title, identity, delta and lock check all follow.

Two rules keep it from doing harm:

  * **An existing role file always wins.** A seat that ran the script, or was
    changed to another role mid-session, must not be dragged back by a stale
    variable inherited from the tab that started it.
  * **The value is validated hard**: uppercase A-Z only, and it must name a real
    `infrastructure/agents/<SEAT>.md`. Anything else is ignored in silence — a typo gets the
    generated session name, never a wrong identity.

WHY BOTH EVENTS
===============
  UserPromptSubmit — a session that has just declared its role gets its title on
                     the next prompt. One turn of latency, unavoidable: the
                     declaration happens mid-turn and no post-tool event accepts
                     a sessionTitle.
  SessionStart     — a RESUMED session keeps its session id, so the role is
                     already on disk and the title is restored immediately, with
                     no latency and without the agent re-running anything.

Fails OPEN and SILENT. A session with no recorded role simply keeps its
generated name; this hook must never wedge a prompt or emit noise.

IDENTITY INJECTION (added 2026-08-13, owner's redesign)
=======================================================
The same recorded role also selects the seat's identity file, `infrastructure/agents/<SEAT>.md`,
which this hook injects as `additionalContext`. That replaces the owner typing
"become agent X" and, more importantly, means a RESUMED session cannot come back
wearing the wrong identity — the file is re-injected from the role on disk rather
than recalled from a summarised context.

Injected ONCE per session, tracked by a marker beside the role file:

  SessionStart      — resumed sessions already have a role, so identity lands
                      immediately, before the first prompt.
  UserPromptSubmit  — a NEW session declares its role mid-turn, so there is no
                      role to read at SessionStart. The marker lets the identity
                      land on the next prompt instead, exactly once.

Injection failure is silent and non-fatal: a missing or unreadable identity file
leaves the session running with the title set and no identity, which is the
pre-2026-08-13 behaviour.

DOCTRINE DELTA (added 2026-08-13)
=================================
Riding the SAME once-per-session injection, `src/RimMandrake/Utils/whats_new.py --seat <SEAT>`
appends what changed in the doctrine set since this seat last synced. Identity
answers "who am I"; the delta answers "what moved while I was away" — the second
question a resumed or long-running seat cannot answer for itself, because peers
commit rules and file queue items with no channel to say so.

It rides the injection rather than a separate hook because injection is the one
moment delivery is guaranteed, which is also what licenses the tool to advance
the seat's sync marker. A delta shown once and never again is only safe because
`whats_new.py --again` can replay it from `<SEAT>.sync.prev`.

Fails OPEN and SILENT like everything else here: a missing script, a git that
hangs, a non-zero exit or a timeout all leave the session with its identity and
no delta. A broken delta must never wedge a prompt.

STALE GIT LOCK (added, riding the same injection)
=================================================
A `.git\\index.lock` left by a git that died blocks every seat in the shared
tree, and the error it produces cannot tell a seat whether a peer is mid-commit
or the lock is orphaned. Five seats were silently unable to commit for 19
minutes on that ambiguity. `src/RimMandrake/Utils/check_git_locks.py` resolves it from evidence,
so this hook runs it once per session and appends its verdict — the seat learns
the tree is blocked at session start, instead of finding out by losing a commit.

SILENT when there is no lock, which is the common case and must cost nothing.
Timeout is deliberately tight (LOCK_TIMEOUT), because unlike the delta this runs
before the first prompt of every seat and buys a warning, not a capability.
"""
import json
import os
import re
import subprocess
import sys

MAX_TITLE = 120
MAX_IDENTITY_BYTES = 32_000        # a seat file is ~4 KB; this is a sanity bound
DELTA_TIMEOUT = 10                 # seconds; a CEILING, not a cost — see read_delta
MAX_DELTA_BYTES = 8_000            # whats_new caps itself at ~25 lines; belt and braces
LOCK_TIMEOUT = 3                   # seconds; a warning is not worth a stall
MAX_LOCK_BYTES = 2_000             # a handful of locks' evidence, no more


def agents_path(root, seat):
    """agents/<SEAT>.md, wherever it currently lives. Never raises.

    The tree moved 2026-08-13 (agents/ -> infrastructure/agents/) and this hook
    validates AGENT_SEAT by the file's existence, so the move silently disabled
    zero-typing startup for every seat: the variable was discarded, no error was
    raised, and two seats booted not knowing who they were. Both locations are
    tried so the next move cannot repeat it.
    """
    for parts in (("infrastructure", "agents"), ("agents",)):
        cand = os.path.join(root, *parts, seat + ".md")
        if os.path.isfile(cand):
            return cand
    return None


def role_dir():
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return os.path.join(root, ".claude", "session_roles")


def seat_of(title):
    """The seat named by a recorded title like "AGENT BUILD", or None.

    The seat is the last whitespace-separated token, so a future title format
    that adds a detail suffix simply stops matching and injects nothing.
    """
    seat = title.split()[-1].upper() if title.split() else ""
    return seat if re.fullmatch(r"[A-Z]{2,16}", seat) else None


def seat_from_env():
    """The seat named by `AGENT_SEAT`, or None. Never raises.

    Validated on both sides: the shape (uppercase A-Z, the same class `seat_of`
    accepts) and the existence of `infrastructure/agents/<SEAT>.md`. A variable that fails
    either is ignored silently, so a typo costs the generated session name and
    never a wrong identity.
    """
    seat = os.environ.get("AGENT_SEAT", "").strip()
    if not re.fullmatch(r"[A-Z]{2,16}", seat):
        return None
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        if not agents_path(root, seat):
            return None
    except OSError:
        return None
    return seat


def record_role(sid, title):
    """Write the role file exactly as set_agent_window.sh does. Never raises.

    Persisting it matters beyond this turn: a resume, and every later prompt,
    reads the file rather than the environment — and `set_agent_window.sh` can
    then overwrite it to change seat, with the file continuing to win.
    """
    try:
        os.makedirs(role_dir(), exist_ok=True)
        with open(os.path.join(role_dir(), sid), "w", encoding="utf-8") as fh:
            fh.write(title + "\n")
    except OSError:
        pass


def read_delta(title):
    """What changed in the doctrine set since this seat last synced, or None.

    Never raises, never blocks for long. DELTA_TIMEOUT is a ceiling, not a cost.
    Measured on this WSL mount: the normal case — a seat with a sync marker, a
    handful of commits behind — is under 1s. The ceiling is only approachable in
    one situation: a seat's VERY FIRST session, where no marker means the 24h
    fallback and `git log` must walk every commit of a busy day (109 of them on
    2026-08-13) against the doctrine pathspec. That walk alone measured 2.2s
    idle and 3.3s under load 12, and `-n` does not help because git pays the
    pathspec walk up front.

    So the ceiling is deliberately below the worst case rather than above it. If
    a heavily loaded machine blows through it, the run is abandoned, the session
    proceeds with identity and no delta, and the NEXT session gets it — the
    child only advances the marker after printing, so an abandoned run consumes
    nothing. A missed delta is cheap; a ten-second stall on every seat start is
    not.
    """
    seat = seat_of(title)
    if not seat:
        return None

    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    script = os.path.join(root, "src", "RimMandrake", "Utils", "whats_new.py")
    if not os.path.isfile(script):
        return None
    try:
        proc = subprocess.run(
            [sys.executable, script, "--seat", seat],
            cwd=root, capture_output=True, text=True, timeout=DELTA_TIMEOUT,
            env={**os.environ, "CLAUDE_PROJECT_DIR": root},
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None

    body = (proc.stdout or "")[:MAX_DELTA_BYTES].strip()
    # "up to date (<sha>)" is the whole output when nothing moved. Injecting it
    # spends context to say nothing, so the seat gets its identity and no delta.
    if not body or body.startswith("up to date"):
        return None
    return body


def read_locks():
    """The lock-check report when the tree is blocked, else None. Never raises.

    Exit 1 = stale, 2 = live: both are worth telling a seat about, because both
    mean "your next commit fails". 0 and anything unexpected are silence.
    """
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    script = os.path.join(root, "src", "RimMandrake", "Utils", "check_git_locks.py")
    if not os.path.isfile(script):
        return None
    try:
        proc = subprocess.run(
            [sys.executable, script, "--quiet"],
            cwd=root, capture_output=True, text=True, timeout=LOCK_TIMEOUT,
            env={**os.environ, "CLAUDE_PROJECT_DIR": root},
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode not in (1, 2):
        return None

    body = (proc.stdout or "")[:MAX_LOCK_BYTES].strip()
    if not body:
        return None
    return proc.returncode, body


def read_identity(title, sid):
    """Return the seat's identity file, or None. Never raises.

    `title` is what set_agent_window.sh recorded, e.g. "AGENT BUILD".
    """
    seat = seat_of(title)
    if not seat:
        return None

    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    path = agents_path(root, seat)
    if not path:
        return None
    try:
        if os.path.getsize(path) > MAX_IDENTITY_BYTES:
            return None
        with open(path, "r", encoding="utf-8") as fh:
            body = fh.read()
    except OSError:
        return None
    return body.strip() or None


def already_injected(sid):
    """Cheap read-only pre-check, so the EXPENSIVE work is not done to be thrown away.

    claim_injection() alone is correct but arrives too late: gathering the delta
    costs a subprocess and up to DELTA_TIMEOUT seconds of git, and without this
    guard that price is paid on every single UserPromptSubmit for the whole life
    of the session, to be discarded by a claim that always fails after the first.
    The O_EXCL claim below is still the authority; this is only an optimisation,
    so a false negative under a race costs nothing.
    """
    try:
        return os.path.exists(os.path.join(role_dir(), sid + ".identity"))
    except OSError:
        return False


def claim_injection(sid):
    """True exactly once per session. False if already injected, or on error."""
    marker = os.path.join(role_dir(), sid + ".identity")
    try:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return False
    except OSError:
        return False
    os.close(fd)
    return True


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0                                  # fail open

    event = payload.get("hook_event_name")
    if event not in ("SessionStart", "UserPromptSubmit"):
        return 0                                  # only these accept a title

    sid = payload.get("session_id") or ""
    # session ids are uuids; refuse anything that could escape the directory
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", sid):
        return 0

    path = os.path.join(role_dir(), sid)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            title = fh.read().strip()
    except OSError:
        title = ""                                # nothing declared yet

    # A recorded role ALWAYS wins over the environment: it is an explicit
    # declaration, and AGENT_SEAT is inherited from whatever tab launched this
    # process. Only when there is no role at all does the variable get a say.
    if not title:
        seat = seat_from_env()
        if not seat:
            return 0                              # no role declared yet
        title = "AGENT " + seat
        record_role(sid, title)                   # best effort; title stands either way

    title = title.splitlines()[0][:MAX_TITLE]

    out = {
        "hookEventName": event,
        "sessionTitle": title,
    }

    # Identity and the doctrine delta ride along together, once per session.
    # Both are gathered BEFORE the claim so that a session where neither is
    # available does not burn its one injection on an empty context — but only
    # if this session has not already been injected, because gathering the delta
    # is the slow part of this hook and every later prompt would pay for it.
    identity = delta = locks = None
    if not already_injected(sid):
        identity = read_identity(title, sid)
        delta = read_delta(title)
        locks = read_locks()

    if (identity or delta or locks) and claim_injection(sid):
        parts = []
        if identity:
            parts.append(
                "You are this session's seat. The following is your identity "
                "file, injected automatically from the role recorded by "
                "src/RimMandrake/Utils/set_agent_window.sh. It is authoritative about your scope, "
                "what you decline, and how you communicate. Follow it alongside "
                "CLAUDE.md and agents_def.md.\n\n" + identity
            )
        if delta:
            parts.append(
                "## What changed while you were away\n\n"
                "Doctrine that moved since this seat last synced — peers commit "
                "rules and file queue items with no channel to tell you. Headings "
                "only; open anything that bears on what you are about to do. This "
                "delta has now been marked as read; `python3 src/RimMandrake/Utils/whats_new.py "
                f"--seat {seat_of(title)} --again` replays it.\n\n"
                "```\n" + delta + "\n```"
            )
        if locks:
            rc, report = locks
            verdict = ("A STALE lock is blocking the shared tree. The report "
                       "prints the exact `rm`; run it, then commit normally."
                       if rc == 1 else
                       "A lock is present and looks LIVE — a peer is probably "
                       "mid-commit. WAIT and re-run the check. Do not delete it.")
            parts.append(
                "## Git lock warning — commits in this tree will fail\n\n"
                + verdict +
                " Re-check with `python3 src/RimMandrake/Utils/check_git_locks.py`.\n\n"
                "```\n" + report + "\n```"
            )
        out["additionalContext"] = "\n\n".join(parts)

    print(json.dumps({"hookSpecificOutput": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
