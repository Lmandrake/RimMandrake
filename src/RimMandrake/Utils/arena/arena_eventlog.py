#!/usr/bin/env python3
"""arena_eventlog.py - the arena's ONE event log, one JSONL per arm, written only by harness code.

ARENA_EVENTLOG_BUILD_AGENTS_MAY_NOT_WRITE; design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.7,
testpilot_merged_2026-10-29.md §2.3. Paths come from arena_tasks.arena_root()/paths() (agent_storage, `$ARENA_ROOT`
in selftests): `<arena>/events/<arm>.jsonl`. arena_tasks's own `events/harness.jsonl` (freeze events) is a
different, unsigned file; this module reads only per-arm files and never touches it.

WHO MAY WRITE. The events dir is arm-READABLE (arena_tasks.arm_readable_roots), so a file permission cannot keep an
agent out of it; the rule is cryptographic. Every record carries `sig` = HMAC-SHA256(token, prev_sig + canonical
record). An agent that appends a line by hand cannot sign it, and cannot re-sign a line it deleted or edited (the
chain breaks); `verify()` lists every such line as rejected and every report here counts only accepted records.

THE TOKEN, AND WHAT IT CANNOT DO (residual risk, stated plainly). Every seat and every arm agent runs as the SAME
OS user (uid 1000; seats differ only by systemd cgroup scope). No file the harness can read is unreadable to an arm
agent that goes looking for it, so the token is a speed bump, not a secret. What is done:
  - it lives OUTSIDE every arm-readable root and OUTSIDE D: (default `~/.local/state/rimmandrake/arena_harness/
    event_token` on the WSL ext4 home, dir 0700, file 0600; `$ARENA_EVENT_TOKEN_FILE` overrides). A token on /mnt/*
    (drvfs: a 0600 file stats 777) or with any group/other mode bit is refused;
  - the token is read only by harness processes: refused when `$RM_ARM` is set or the cwd is inside an arm clone
    root (defence in depth - an agent can unset a variable);
  - tampering is made DETECTABLE even if the token leaked: every write appends an ANCHOR (arm, accepted count, head
    sig) to `<token dir>/anchors.jsonl` (`$ARENA_ANCHOR_FILE`), and `anchor-note` prints a `rimflow note` that
    publishes the current heads into the git ledger, which arms cannot rewrite once pushed. report() refuses an arm
    whose log is shorter than any anchor or whose record at an anchored position has a different sig (tail
    deletion, whole-file deletion, a re-signed history).
  - (fix round 2) only a harness ENTRYPOINT signs: HarnessWriter needs a live per-pass capability (PassCapability /
    harness_pass()), which may be opened only when `__main__` is one of ENTRYPOINTS in this directory (importing the
    library from an agent script, `python3 -c`, a REPL: refused). The capability is a 0600 file under
    `<token dir>/pass_caps/` (0700; no arm cwd or PATH is there) holding only a hash of a nonce that lives in the
    opening process's memory; every emit re-checks it through the process's own fd (same pid + pid start time, file
    still the same inode, not expired, not closed). It is deleted at pass end. A selftest_arena_*.py entrypoint may
    open one only with a temp token that is not the default token.
  - every signed record carries `prov`: pid, pid start time, the parent chain (pid, start time, comm), uid, cwd,
    entrypoint and an environment fingerprint, so a forged line written by some other process shape can be told
    apart forensically. report() counts records with no or non-entrypoint prov as `unprovenanced`.
  - (fix round 3) the entrypoint is the process's REAL script: /proc/self/cmdline (argv as exec'd; -c / -m / stdin
    refused), resolved against the exec-time PWD from /proc/self/environ, and the main thread's outermost frame must
    run that file with the same bytecode shape as compiling it fresh, so `__main__.__file__ = ...` or `sys.argv[0] =
    ...` changes nothing. A closed capability forgets its nonce and remembers its file's inode + ctime.
  - (fix round 3) WITNESS: every anchor and roster entry is also sent, HMAC-signed, to systemd journald
    (SYSLOG_IDENTIFIER rm_arena_witness, field RM_ARENA_ROOT = hash of the arena root). The journal files are root
    owned: uid 1000 can append but not delete or edit, so a tail deleted AFTER the newest ledger anchor is still
    witnessed. `$ARENA_WITNESS` = journal (default) | off | a file path (selftests only: same-uid editable).
  - (fix round 3) ROSTER: `<token dir>/roster.jsonl`, a signed append-only chain naming every arm at its first write
    (witnessed, and published as the `@roster` token of anchor-note). report() reports every rostered arm and refuses
    one whose log is gone; a roster that lost a line (chain break, or an arm the witness/ledger knows) is untrusted.
  - (fix round 3) ledger anchor tokens are `arm:n:head:lsig`, lsig = HMAC(token, "ledger-anchor:arm:n:head"); a note
    from any seat/item is accepted ONLY if lsig verifies. Unsigned, forged or malformed tokens (5.0, 5e0, non-ASCII
    digits, extra fields) are listed in `anchor_errors` with the note's tsn/seat/item, never applied.
  - report() FAILS CLOSED: an arm with records but no anchor at all (local store and witness gone) is refused
    UNMEASURED, and an arm is `trusted` only when a SIGNED ledger anchor covers its whole accepted log AND the witness
    is readable and its newest anchor for that arm is the same count. Witness off/unreadable: never trusted.
RESIDUAL SAME-UID RISK, NOT CLOSED: an agent running as uid 1000 that reads the token can call _sign() directly (or
copy this file and delete the checks) and write any record, `prov` included, with a valid signature; it can ptrace
or read /proc of a live harness process. The capability, prov and cwd/RM_ARM checks stop the casual path (library
use from an arm) and leave forensic traces; they are not a boundary. Only a separate OS user (or a signer outside
the arm's machine) closes this. Ledger-published anchors bound what it can rewrite: history before the newest
external anchor; events forged AFTER it pass every check here. Publish anchors at every pass end. A token holder can
also mint signed ledger notes and witness lines. The entrypoint check is beaten by an exec with a spoofed PWD AND an
identical copy of an allowlisted file, by PYTHONPATH/site/.pth injection or ptrace (same uid). A TOKENLESS attacker
can flood the journal so journald rotates the witness lines away (then the witness reads short: untrusted, not a
false trust, unless the log was cut to exactly the surviving witness count) and can make report() refuse an honest
arm by deleting its files (loud, investigated).

Event record: {ts, arm, lane, run_id, task, event, sha?, verdict?, ite?, minutes?, rule?, detail?, prov, sig}.
ts is ISO-8601 WITH a zone (Z or +hh:mm), compared in UTC. Analysis orders records by event time across the whole
log (stable on file order), never by append order, so a late import of an earlier event is placed where it happened.
Different-agent rule: build_end.detail.builder, test_start.detail.tester; a test_start targets ONE build: the latest
earlier build_end of the same task with the same build id (detail.build_id, else sha) when the test names one, else
the latest earlier build_end of the task (fix round 3: a test MATCHES a build when it names no id or shares one of
the build's ids {build_id, sha}; only a matched build is credited as tested). It is FLAGGED when its tester is the
builder of any build it may be testing: the matched one, the latest earlier build when the id it names matches
nothing, the first later matching build, or any matching build at/after it within SKEW_S (recomputed; the stamped
rule="tester_is_builder" is a convenience, never trusted). A test_start earlier than every matching build is
reported as `test_before_build`, one within SKEW_S of a matching build as `ambiguous_order`. Agent ids are compared
NORMALISED (NFKC, Unicode format chars dropped, whitespace collapsed, casefold); a builder/tester id that
is not a string, is blank, or is all digits is refused at write; an id starting `unattributed:` never counts as a
different agent.
Owner minutes: `card` (minutes = rm-pulse dwell, detail.card_id, detail.unblocked = tasks the answer unblocked) and
`owner_touch` (minutes); minutes are finite, >= 0, never bool; card_id a non-empty string, unblocked a list of
non-empty strings. A card_id seen twice (normalised as ids are) counts once, the earliest by event time; a duplicate
with other values is counted in `card_conflicts`. Reported per arm, and output (each task by its LAST judge
verdict) reported with and without owner-unblocked work. An arm with NO judge events but ledger done transitions
(the v3 adapter) reports points as None and output_comparable False: a self-closed ledger item is not a
judge-accepted point (run arena_judge on its tasks to make it comparable).
A partial final line (no newline: a crashed writer or a hand edit) is newline-terminated before the next write, so
it stays one rejected line and never swallows the next record. After a gap (a deleted line), later lines that still
chain to each other are reported as `recoverable` (valid signatures, not counted).
"""
from __future__ import annotations

import atexit
import datetime as dt
import fcntl
import hashlib
import hmac
import json
import math
import os
import re
import secrets
import socket
import subprocess
import sys
import tempfile
import threading
import time
import types
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_tasks as A  # noqa: E402

EVENTS = ("freeze", "assign", "pass_start", "pass_end", "build_end", "test_start", "test_end", "gate", "judge",
          "critic_round", "live_take", "live_release", "reload", "canary", "card", "owner_touch", "defect",
          "invalid", "switch", "stop")
FIELDS = ("ts", "arm", "lane", "run_id", "task", "event", "sha", "verdict", "ite", "minutes", "rule", "detail",
          "prov")
REQUIRED = ("ts", "arm", "lane", "run_id", "event")
STR_FIELDS = ("arm", "lane", "run_id", "task", "event", "sha", "verdict", "rule")
GENESIS = "0" * 64
FLAG_SAME_AGENT = "tester_is_builder"
UNATTRIBUTED = "unattributed:"
# the only scripts that may open a pass capability (run as __main__ from THIS directory)
ENTRYPOINTS = ("arena_eventlog.py", "arena_v3_adapter.py", "arena_gate.py", "arena_judge.py")
SELFTEST_ENTRY_PREFIX = "selftest_arena_"
CAP_TTL_S = 12 * 3600


class EventLogError(Exception):
    pass


class Rejected(EventLogError):
    """A write refused: no/invalid token, bad schema, or a token path an arm can read."""


def now_ts() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ts_epoch(ts) -> float:
    """ISO-8601 with an explicit zone -> UTC epoch seconds. A naive or unparseable ts raises ValueError."""
    if not isinstance(ts, str):
        raise ValueError("ts must be a string, got %r" % (ts,))
    t = dt.datetime.fromisoformat(ts)
    if t.tzinfo is None:
        raise ValueError("ts %r has no time zone" % ts)
    return t.timestamp()


# ---------------------------------------------------------------- provenance and the per-pass capability

def _proc_stat(pid: int):
    """-> (ppid, start_ticks, comm) from /proc/<pid>/stat, or None."""
    try:
        raw = Path("/proc/%d/stat" % pid).read_text()
    except OSError:
        return None
    comm = raw[raw.index("(") + 1:raw.rindex(")")]
    rest = raw[raw.rindex(")") + 2:].split()
    return int(rest[1]), int(rest[19]), comm          # fields 4 (ppid) and 22 (starttime)


def _initial_pwd() -> str:
    """PWD as the process was EXECUTED (/proc/self/environ is the exec-time environment; os.environ edits do not
    change it). '' if absent."""
    try:
        for kv in Path("/proc/self/environ").read_bytes().split(b"\0"):
            if kv.startswith(b"PWD="):
                return os.fsdecode(kv[4:])
    except OSError:
        pass
    return ""


def _cmdline_script() -> str:
    """The script the interpreter was EXECUTED with, from /proc/self/cmdline and /proc/self/exe - never from a
    module attribute (`__main__.__file__`, sys.argv: both one assignment away from a lie). '' for -c, -m, stdin, a
    REPL, a non-python executable or a relative path with no exec-time PWD."""
    try:
        raw = Path("/proc/self/cmdline").read_bytes()
        exe = os.path.basename(os.path.realpath("/proc/self/exe"))
    except OSError:
        return ""
    if not exe.startswith("python"):
        return ""
    args = [os.fsdecode(a) for a in raw.split(b"\0")]
    if args and args[-1] == "":
        args.pop()
    i = 1
    while i < len(args):
        a = args[i]
        if a == "--":
            i += 1
            break
        if a == "-" or not a.startswith("-"):
            break
        if a.startswith("--"):
            i += 2 if a == "--check-hash-based-pycs" else 1
            continue
        skip_next = False
        for k, ch in enumerate(a[1:]):
            if ch in "cm":
                return ""                       # -c CODE / -m MODULE: no script file
            if ch in "XW":
                skip_next = k == len(a) - 2     # the option's value is the next argument
                break
        i += 2 if skip_next else 1
    if i >= len(args) or args[i] == "-":
        return ""
    s = args[i]
    if not os.path.isabs(s):
        base = _initial_pwd()
        if not base:
            return ""
        s = os.path.join(base, s)
    return os.path.realpath(s)


_ENTRY = None


def _entrypoint() -> str:
    """Real path of the script this process was executed with ('' for -c, -m, a REPL). Cached: cmdline is fixed."""
    global _ENTRY
    if _ENTRY is None:
        _ENTRY = _cmdline_script()
    return _ENTRY


def _gate_runner_sel(cmdline=None, env=None) -> str | None:
    """arena_gate's say-so that this process is its harness runner step: the selftest path it runs, else None. Lazy
    import (arena_gate imports this module). Needs the real /proc/self/cmdline and the runner-sha env marker."""
    try:
        if cmdline is None:
            raw = Path("/proc/self/cmdline").read_bytes().split(b"\0")
            if raw and raw[-1] == b"":
                raw.pop()
            cmdline = [os.fsdecode(a) for a in raw]
        import arena_gate
        return arena_gate.gate_runner_selftest(cmdline, env)
    except (OSError, ImportError, AttributeError):
        return None


def _entry_name() -> str:
    """Basename recorded as the entry: the gate runner's selftest when running under it, else the entry script."""
    sel = _gate_runner_sel()
    return os.path.basename(sel) if sel else os.path.basename(_entrypoint())


def _code_shape(co) -> tuple:
    return (co.co_code, co.co_names, tuple(_code_shape(c) if isinstance(c, types.CodeType) else repr(c)
                                           for c in co.co_consts))


def _main_code_ok(entry: str) -> str | None:
    """None when the main thread's outermost frame runs code compiled from `entry` itself, else why not. Catches a
    .pyc (or any code object) carrying a spoofed co_filename: its bytecode is not the entrypoint's."""
    frame = sys._current_frames().get(threading.main_thread().ident)
    while frame is not None and frame.f_back is not None:
        frame = frame.f_back
    if frame is None:
        return "no main-thread frame"
    co = frame.f_code
    if os.path.realpath(co.co_filename) != entry:
        return "the main frame runs %s, not %s" % (co.co_filename, entry)
    try:
        want = compile(Path(entry).read_bytes(), co.co_filename, "exec", dont_inherit=True)
    except (OSError, SyntaxError, ValueError) as e:
        return "cannot compile %s: %s" % (entry, e)
    if _code_shape(want) != _code_shape(co):
        return "the main frame's bytecode is not %s's (a code object with a borrowed filename)" % entry
    return None


def provenance(cap=None) -> dict:
    """Who is emitting: pid + start time, parent chain, uid, cwd, entrypoint, env fingerprint. Signed with the
    record, so it is evidence of the process shape that wrote a line, not proof (a token holder can write any)."""
    chain, pid = [], os.getpid()
    for _ in range(8):
        st = _proc_stat(pid)
        if st is None or pid <= 1:
            break
        chain.append([pid, st[1], st[2]])
        pid = st[0]
    env = "\n".join("%s=%s" % kv for kv in sorted(os.environ.items()))
    try:
        cwd = os.getcwd()
    except OSError:
        cwd = None
    return {"pid": os.getpid(), "pid_start": (chain[0][1] if chain else None), "chain": chain, "uid": os.getuid(),
            "cwd": cwd, "entry": _entry_name() or None,
            "env_sha": hashlib.sha256(env.encode()).hexdigest()[:16],
            "cap": cap.cap_id if cap is not None else None}


def token_path(p: dict) -> Path:
    env = os.environ.get("ARENA_EVENT_TOKEN_FILE", "").strip()
    return Path(env) if env else _default_token_path()


def anchor_path(p: dict) -> Path:
    env = os.environ.get("ARENA_ANCHOR_FILE", "").strip()
    return Path(env) if env else token_path(p).parent / "anchors.jsonl"


def _check_token_location(tp: Path, p: dict):
    for root in A.arm_readable_roots(p) + [p["root"]]:
        if A._inside(tp, root):
            raise Rejected("token file %s is inside arm-readable root %s" % (tp, root))
    if os.path.realpath(tp).startswith("/mnt/"):
        raise Rejected("token file %s is on a Windows drive (drvfs ignores file modes): keep it on the ext4 home" % tp)


def _check_harness_process(p: dict):
    """Defence in depth, not a boundary: an arm agent's environment carries RM_ARM and its cwd is its clone."""
    if os.environ.get("RM_ARM", "").strip():
        raise Rejected("RM_ARM=%s is set: this is an arm process, it may not hold the harness token"
                       % os.environ["RM_ARM"])
    clones = A.arm_readable_roots(p)[-1]
    try:
        cwd = os.getcwd()
    except OSError:
        cwd = "/"
    if A._inside(cwd, clones):
        raise Rejected("cwd %s is inside the arm clone root %s: run the harness from its own directory" % (cwd, clones))


def init_token(p: dict | None = None) -> Path:
    """Create the token once (harness setup). Never overwrites: a new token would orphan every signed line."""
    p = p or A.paths()
    tp = token_path(p)
    _check_token_location(tp, p)
    _check_harness_process(p)
    if tp.exists():
        return tp
    tp.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(tp.parent, 0o700)
    fd = os.open(str(tp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(secrets.token_hex(32))
    return tp


def _default_token_path() -> Path:
    state = os.environ.get("XDG_STATE_HOME", "").strip() or str(Path.home() / ".local" / "state")
    return Path(state) / "rimmandrake" / "arena_harness" / "event_token"


def _check_entrypoint(p: dict):
    """Only a harness entrypoint run as __main__ from this directory opens a pass. A selftest_arena_* entrypoint
    only with a temp token that is not the default token (path, inode and content all differ)."""
    sel = _gate_runner_sel()
    if sel:     # arena_gate's runner step: the main frame runs the (verified) runner, the selftest is the entry
        name = os.path.basename(sel)
        if os.path.dirname(sel) != str(HERE) or not name.startswith(SELFTEST_ENTRY_PREFIX):
            raise Rejected("gate runner entry %r is not a %s* selftest in %s" % (sel, SELFTEST_ENTRY_PREFIX, HERE))
        e = _entrypoint()
        why = _main_code_ok(e)
        if why:
            raise Rejected("entrypoint check: %s" % why)
    else:
        e = _entrypoint()
        name = os.path.basename(e)
        if not e or os.path.dirname(e) != str(HERE):
            raise Rejected("signing needs a harness entrypoint run from %s as __main__ (got %r): library use from "
                           "another script, -c or a REPL is refused" % (HERE, e or None))
        why = _main_code_ok(e)
        if why:
            raise Rejected("entrypoint check: %s" % why)
        if name in ENTRYPOINTS:
            return
    if name.startswith(SELFTEST_ENTRY_PREFIX) and name.endswith(".py"):
        tp, dflt = token_path(p), _default_token_path()
        if not A._inside(tp, tempfile.gettempdir()):
            raise Rejected("selftest entrypoint %s may sign only with a token under %s (token %s)"
                           % (name, tempfile.gettempdir(), tp))
        if dflt.exists():
            same = os.path.realpath(tp) == os.path.realpath(dflt)
            try:
                same = same or os.path.samefile(tp, dflt) or tp.read_text().strip() == dflt.read_text().strip()
            except OSError:
                same = True                     # cannot prove it differs: refuse
            if same:
                raise Rejected("selftest entrypoint %s may not sign with the real harness token" % name)
        return
    raise Rejected("entrypoint %s is not a harness entrypoint %s" % (name, ENTRYPOINTS))


class PassCapability:
    """A short-lived signing capability for ONE harness pass. Open it at pass start (harness_pass()), close at pass
    end. File `<token dir>/pass_caps/<pid>-<rand>` (0600, dir 0700) holds pid, pid start time, expiry and a HASH of
    a nonce kept only in this object; check() re-reads it through the fd this process holds."""

    def __init__(self, p: dict | None = None, ttl_s: float = CAP_TTL_S):
        self.p = p or A.paths()
        tp = token_path(self.p)
        _check_token_location(tp, self.p)
        _check_harness_process(self.p)
        _check_entrypoint(self.p)
        d = tp.parent / "pass_caps"
        d.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(d, 0o700)
        self._nonce = secrets.token_hex(32)
        self.cap_id = hashlib.sha256(("id:" + self._nonce).encode()).hexdigest()[:16]
        self.pid = os.getpid()
        st = _proc_stat(self.pid)
        self.pid_start = st[1] if st else None
        self.expires = time.time() + ttl_s
        self.path = d / ("%d-%s" % (self.pid, secrets.token_hex(8)))
        body = json.dumps({"pid": self.pid, "pid_start": self.pid_start, "expires": self.expires,
                           "entry": _entry_name(), "cap_id": self.cap_id,
                           "nonce_sha": hashlib.sha256(self._nonce.encode()).hexdigest()}, sort_keys=True).encode()
        self._fd = os.open(str(self.path), os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(self._fd, body)
        held = os.fstat(self._fd)
        self._ident = (held.st_ino, held.st_dev, held.st_ctime_ns)   # THIS pass's file (inode numbers get reused)
        self._body = body
        self.closed = False
        self.last_anchor = {}                        # arm -> newest anchor of this pass, re-witnessed at close

    def check(self):
        if self.closed or not self._nonce:
            raise Rejected("pass capability %s is closed (pass ended)" % self.cap_id)
        if os.getpid() != self.pid:
            raise Rejected("pass capability %s belongs to pid %d, not %d" % (self.cap_id, self.pid, os.getpid()))
        st = _proc_stat(self.pid)
        if self.pid_start is not None and (st is None or st[1] != self.pid_start):
            raise Rejected("pass capability %s: process start time changed (pid reused)" % self.cap_id)
        if time.time() > self.expires:
            raise Rejected("pass capability %s expired" % self.cap_id)
        try:
            on_disk, held = os.stat(self.path), os.fstat(self._fd)
        except OSError:
            raise Rejected("pass capability file %s is gone" % self.path)
        if (on_disk.st_ino, on_disk.st_dev) != (held.st_ino, held.st_dev) or on_disk.st_mode & 0o077 \
                or (held.st_ino, held.st_dev, held.st_ctime_ns) != self._ident:
            raise Rejected("pass capability file %s was replaced or opened up" % self.path)
        if os.pread(self._fd, len(self._body) + 1, 0) != self._body or \
                json.loads(self._body)["nonce_sha"] != hashlib.sha256(self._nonce.encode()).hexdigest():
            raise Rejected("pass capability file %s content changed" % self.path)

    def close(self):
        if self.closed:
            return
        self.closed = True
        self._nonce = None                           # the secret dies with the pass: no later check() can succeed
        for a in list(self.last_anchor.values()):    # a witness line dropped mid-pass (rate limit) is re-sent here
            witness_append(self.p, dict(a, kind="anchor"))
        try:
            os.close(self._fd)
        except OSError:
            pass
        try:
            self.path.unlink()
        except OSError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        _ACTIVE.discard(self)


_ACTIVE: set = set()


def harness_pass(p: dict | None = None, ttl_s: float = CAP_TTL_S) -> PassCapability:
    """`with harness_pass(p):` - open the pass capability; HarnessWriter(p) inside the block uses it."""
    cap = PassCapability(p, ttl_s)
    _ACTIVE.add(cap)
    return cap


def _active_cap(p: dict):
    live = [c for c in _ACTIVE if not c.closed and c.pid == os.getpid()
            and os.path.realpath(c.p["root"]) == os.path.realpath(p["root"])]
    if live:
        return live[-1]
    e = _entry_name()
    if e.startswith(SELFTEST_ENTRY_PREFIX):     # selftests: an implicit pass, only with a temp non-default token
        cap = harness_pass(p)
        atexit.register(cap.close)
        return cap
    raise Rejected("no open harness pass: the harness entrypoint must open `with arena_eventlog.harness_pass(p):` "
                   "before building a HarnessWriter")


def _read_token(p: dict) -> str:
    tp = token_path(p)
    _check_token_location(tp, p)
    _check_harness_process(p)
    try:
        mode = os.stat(tp).st_mode & 0o777
        tok = tp.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise Rejected("no harness token (%s): %s" % (tp, e))
    if mode & 0o077:
        raise Rejected("harness token %s has mode %o (group/other bits): the filesystem does not keep it private"
                       % (tp, mode))
    if len(tok) < 32:
        raise Rejected("harness token at %s is too short to be a token" % tp)
    return tok


def arm_file(p: dict, arm: str) -> Path:
    if not arm or not all(c.isalnum() or c in "_-" for c in arm) or arm == "harness":
        raise Rejected("bad arm name %r" % (arm,))
    return p["events"] / (arm + ".jsonl")


def _canon(rec: dict) -> str:
    return json.dumps({k: v for k, v in rec.items() if k != "sig"}, sort_keys=True, separators=(",", ":"))


def _sign(token: str, prev: str, rec: dict) -> str:
    return hmac.new(token.encode(), (prev + _canon(rec)).encode(), hashlib.sha256).hexdigest()


def norm_id(x) -> str | None:
    """An id for comparison: NFKC (fullwidth -> ASCII), format characters (Cf: zero-width space/joiner, BOM, bidi
    marks) dropped, whitespace collapsed, casefold. None for anything that is not a usable id."""
    n = _fold(x)
    return n if n and not n.isdigit() else None


def _fold(x) -> str | None:
    if not isinstance(x, str):
        return None
    n = unicodedata.normalize("NFKC", x)
    n = "".join(c for c in n if unicodedata.category(c) != "Cf")
    return unicodedata.normalize("NFKC", " ".join(n.split()).casefold()) or None


def _norm_key(x) -> str | None:
    """norm_id's folding for build ids / card ids, where an all-digit value IS a usable key."""
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        x = str(x)
    return _fold(x)


def _minutes_ok(m) -> bool:
    if not isinstance(m, (int, float)) or isinstance(m, bool):
        return False
    try:
        f = float(m)                    # an int too large for a float (10**309) is refused, not a crash
    except OverflowError:
        return False
    return math.isfinite(f) and f >= 0


def validate_record(rec: dict):
    if not isinstance(rec, dict):
        raise Rejected("record is not an object")
    extra = set(rec) - set(FIELDS) - {"sig"}
    if extra:
        raise Rejected("unknown field(s) %s" % sorted(extra))
    missing = [k for k in REQUIRED if not rec.get(k)]
    if missing:
        raise Rejected("missing %s" % missing)
    for k in STR_FIELDS:
        if k in rec and rec[k] is not None and not (isinstance(rec[k], str) and rec[k].strip()):
            raise Rejected("%s must be a non-empty string (got %r)" % (k, rec[k]))
    try:
        ts_epoch(rec["ts"])
    except ValueError as e:
        raise Rejected("bad ts: %s" % e)
    if rec["event"] not in EVENTS:
        raise Rejected("unknown event %r" % rec["event"])
    ev = rec["event"]
    if rec.get("minutes") is not None and not _minutes_ok(rec["minutes"]):
        raise Rejected("minutes must be finite, non-negative, numeric (got %r)" % (rec["minutes"],))
    if "detail" in rec and rec["detail"] is not None and not isinstance(rec["detail"], dict):
        raise Rejected("detail must be an object")
    if "prov" in rec and not isinstance(rec["prov"], dict):
        raise Rejected("prov must be an object")
    d = rec.get("detail") or {}
    if "build_id" in d and not (isinstance(d["build_id"], str) and d["build_id"].strip()):
        raise Rejected("detail.build_id must be a non-empty string (got %r)" % (d["build_id"],))
    try:
        json.dumps(rec, allow_nan=False)
    except (TypeError, ValueError) as e:
        raise Rejected("record is not strict JSON: %s" % e)
    if ev == "build_end" and not (rec.get("task") and norm_id(d.get("builder"))):
        raise Rejected("build_end needs task and a string, non-blank, non-numeric detail.builder (got %r)"
                       % (d.get("builder"),))
    if ev in ("test_start", "test_end") and not (rec.get("task") and norm_id(d.get("tester"))):
        raise Rejected("%s needs task and a string, non-blank, non-numeric detail.tester (got %r)"
                       % (ev, d.get("tester")))
    if ev in ("card", "owner_touch") and not _minutes_ok(rec.get("minutes")):
        raise Rejected("%s needs finite, non-negative, numeric (non-bool) minutes (got %r)" % (ev, rec.get("minutes")))
    if ev == "card":
        cid, un = d.get("card_id"), d.get("unblocked")
        if not (isinstance(cid, str) and cid.strip()) or not isinstance(un, list):
            raise Rejected("card needs a non-empty string detail.card_id and a detail.unblocked list (may be empty); "
                           "got card_id=%r unblocked=%r" % (cid, un))
        bad = [t for t in un if not (isinstance(t, str) and t.strip())]
        if bad:
            raise Rejected("card detail.unblocked must hold non-empty task-id strings (bad: %r)" % (bad[:3],))


def _read_lines_bad(f: Path) -> tuple[list[str], int]:
    """(non-blank lines, number of lines that were not valid UTF-8). Read as BYTES and decode per line, so one bad
    append (invalid UTF-8) costs only its own line: it is kept as a U+FFFD-replaced line, which can never verify
    (rejected, counted) instead of aborting the whole read."""
    if not f.exists():
        return [], 0
    out, bad = [], 0
    for b in f.read_bytes().splitlines():
        try:
            t = b.decode("utf-8")
        except UnicodeDecodeError:
            t, bad = b.decode("utf-8", errors="replace"), bad + 1
        if t.strip():
            out.append(t)
    return out, bad


def _read_lines(f: Path) -> list[str]:
    return _read_lines_bad(f)[0]


def verify(p: dict, arm: str, token: str | None = None) -> dict:
    """-> {"accepted": [rec], "rejected": [(lineno, raw)], "recoverable": [(lineno, rec)]}. Needs the token."""
    lines, bad = _read_lines_bad(arm_file(p, arm))
    v = verify_lines(lines, token or _read_token(p), arm)
    return dict({k: v[k] for k in ("accepted", "rejected", "recoverable")}, undecodable=bad)


# ---------------------------------------------------------------- anchors

def _anchor_sign(token: str, a: dict) -> str:
    return hmac.new(token.encode(), ("anchor:" + _canon(a)).encode(), hashlib.sha256).hexdigest()


def _ledger_sig(token: str, arm: str, n: int, head: str) -> str:
    """The HMAC a published (ledger note) anchor token carries: only a token holder can mint a note that counts."""
    return hmac.new(token.encode(), ("ledger-anchor:%s:%d:%s" % (arm, n, head)).encode(), hashlib.sha256).hexdigest()


def make_anchor(arm: str, accepted: list[dict], token: str, ts: str | None = None) -> dict:
    a = {"ts": ts or now_ts(), "arm": arm, "n": len(accepted), "head": accepted[-1]["sig"] if accepted else GENESIS}
    a["lsig"] = _ledger_sig(token, arm, a["n"], a["head"])
    a["sig"] = _anchor_sign(token, a)
    return a


# ---------------------------------------------------------------- witness (append-only store the arm uid cannot edit)
WITNESS_ID = "rm_arena_witness"
JOURNAL_SOCKET = "/run/systemd/journal/socket"


def _witness_mode() -> str:
    """ARENA_WITNESS: `journal` (default: systemd journald; its files are root-owned, uid 1000 can append through
    the socket but cannot delete or edit), `off`, or a file path (selftests only: a file the same uid CAN edit)."""
    return (os.environ.get("ARENA_WITNESS") or "journal").strip() or "journal"


def _root_key(p: dict) -> str:
    return hashlib.sha256(os.path.realpath(str(p["root"])).encode()).hexdigest()[:16]


def witness_append(p: dict, entry: dict) -> bool:
    """Send one signed anchor/roster entry to the witness. Never raises (a missing witness makes report() untrusted,
    it never stops the harness)."""
    mode = _witness_mode()
    if mode == "off":
        return False
    key = _root_key(p)
    line = json.dumps(dict(entry, root=key), sort_keys=True)
    try:
        if mode == "journal":
            msg = "SYSLOG_IDENTIFIER=%s\nRM_ARENA_ROOT=%s\nMESSAGE=%s\n" % (WITNESS_ID, key, line)
            with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as s:
                s.sendto(msg.encode(), JOURNAL_SOCKET)
        else:
            with open(mode, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        return True
    except OSError:
        return False


def witness_read(p: dict, token: str) -> dict:
    """-> {"status": "ok" | "off" | "unreadable: ...", "anchors": {arm: [anchor]}, "roster": [entry], "bad": n}.
    Entries whose sig fails (written without the token) are counted in `bad`, never used."""
    mode, key = _witness_mode(), _root_key(p)
    out = {"status": "ok", "anchors": {}, "roster": [], "bad": 0}
    if mode == "off":
        return dict(out, status="off")
    try:
        if mode == "journal":
            cp = subprocess.run(["journalctl", "-t", WITNESS_ID, "RM_ARENA_ROOT=" + key, "-o", "cat", "--no-pager",
                                 "-q"], capture_output=True, text=True, timeout=60)
            if cp.returncode != 0:
                return dict(out, status="unreadable: journalctl exit %d %s" % (cp.returncode, cp.stderr.strip()[:120]))
            lines = cp.stdout.splitlines()
        else:
            lines = _read_lines(Path(mode))
    except (OSError, subprocess.SubprocessError) as e:
        return dict(out, status="unreadable: %s" % e)
    for raw in lines:
        try:
            e = json.loads(raw)
            if e.get("root") != key:
                continue
            kind = e.pop("kind", None)
            e.pop("root", None)
            if kind == "anchor" and hmac.compare_digest(str(e.get("sig")), _anchor_sign(token, e)):
                out["anchors"].setdefault(e["arm"], []).append(dict(e, witness=True))
            elif kind == "roster" and hmac.compare_digest(str(e.get("sig")), _roster_sign(token, e)):
                out["roster"].append(e)
            else:
                out["bad"] += 1
        except (ValueError, AttributeError, TypeError, KeyError):
            out["bad"] += 1
    return out


# ---------------------------------------------------------------- arm roster (every arm ever written to)

def roster_path(p: dict) -> Path:
    return anchor_path(p).parent / "roster.jsonl"


def _roster_sign(token: str, e: dict) -> str:
    return hmac.new(token.encode(), ("roster:" + str(e.get("prev")) + _canon(e)).encode(), hashlib.sha256).hexdigest()


def read_roster(p: dict, token: str) -> dict:
    """-> {"arms": [arm], "n": entries in the unbroken chain, "head": last sig, "bad": [raw]}. Append-only chain:
    removing or editing a middle line breaks it (listed in `bad`); removing the LAST line is caught by the witness
    and by a published `@roster` anchor."""
    arms, prev, bad = [], GENESIS, []
    for raw in _read_lines(roster_path(p)):
        try:
            e = json.loads(raw)
            ok = e.get("prev") == prev and hmac.compare_digest(str(e.get("sig")), _roster_sign(token, e))
        except (ValueError, AttributeError, TypeError):
            ok = False
        if ok and not bad:
            arms.append(e["arm"]); prev = e["sig"]
        else:
            bad.append(raw)
    return {"arms": arms, "n": len(arms), "head": prev, "bad": bad}


def _roster_add(p: dict, token: str, arm: str):
    """Roster `arm` (idempotent). Called by emit at the arm's first write, under the roster file lock."""
    f = roster_path(p)
    f.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with open(f, "a+", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        r = read_roster(p, token)
        if arm in r["arms"]:
            return
        e = {"ts": now_ts(), "arm": arm, "seq": r["n"] + 1, "prev": r["head"]}
        e["sig"] = _roster_sign(token, e)
        fh.write(json.dumps(e, sort_keys=True) + "\n")
        fh.flush(); os.fsync(fh.fileno())
    witness_append(p, dict(e, kind="roster"))


def roster_anchor(p: dict, token: str) -> dict:
    r = read_roster(p, token)
    return {"arm": "@roster", "n": r["n"], "head": r["head"], "lsig": _ledger_sig(token, "@roster", r["n"], r["head"])}


def append_anchor(p: dict, a: dict):
    f = anchor_path(p)
    f.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with open(f, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(a, sort_keys=True) + "\n")
        fh.flush(); os.fsync(fh.fileno())


def read_anchors(p: dict, token: str) -> dict:
    """-> {"by_arm": {arm: [anchor]}, "bad": [raw]}. An anchor line whose sig fails is listed, never used."""
    by, bad = {}, []
    f = anchor_path(p)
    for raw in _read_lines(f):
        try:
            a = json.loads(raw)
            ok = hmac.compare_digest(str(a.get("sig")), _anchor_sign(token, a))
        except (ValueError, AttributeError, TypeError):
            ok = False
        if ok:
            by.setdefault(a["arm"], []).append(a)
        else:
            bad.append(raw)
    return {"by_arm": by, "bad": bad}


NOTE_PREFIX = "ARENA_ANCHOR"


def anchor_note_text(anchors: list[dict]) -> str:
    """One `rimflow note --text` body publishing the current head of each arm (external, git-ledger anchor).
    Token `arm:n:head:lsig`, lsig = HMAC(token, "ledger-anchor:arm:n:head"); the roster is token `@roster:...`."""
    return NOTE_PREFIX + " " + " ".join("%s:%d:%s:%s" % (a["arm"], a["n"], a["head"], a.get("lsig") or "unsigned")
                                        for a in anchors)


_NOTE_TOKEN = re.compile(r"(@roster|[A-Za-z0-9_-]+):([0-9]+):([0-9a-f]{64}):([0-9a-f]{64})", re.ASCII)


def parse_anchor_note(text: str) -> list[dict]:
    """Strict: every token must be `arm:<ASCII digits>:<64 lowercase hex>:<64 lowercase hex>`. A token that is not
    (5.0, 5e0, a non-ASCII digit, an extra field, no signature) is RETURNED with an `error`, never dropped."""
    if not isinstance(text, str) or not text.lstrip().startswith(NOTE_PREFIX):
        return []
    body = text.lstrip()[len(NOTE_PREFIX):]
    if body and not body[0].isspace():
        return []                                      # ARENA_ANCHORX...: some other note
    out = []
    for tok in body.split():
        m = _NOTE_TOKEN.fullmatch(tok)
        if m:
            out.append({"arm": m.group(1), "n": int(m.group(2)), "head": m.group(3), "lsig": m.group(4),
                        "external": True})
            continue
        arm = tok.split(":", 1)[0]
        arm = arm if re.fullmatch(r"@roster|[A-Za-z0-9_-]+", arm, re.ASCII) else "?"
        parts = tok.split(":")
        why = ("unsigned anchor token (no harness HMAC)" if len(parts) == 3 else "malformed anchor token")
        out.append({"arm": arm, "external": True, "error": "%s %r" % (why, tok[:100])})
    return out


def anchor_error(a) -> str | None:
    """Why an anchor cannot be used (refused, never applied), or None. n is a non-negative int (not bool), head a
    64-hex sig, or GENESIS iff n == 0."""
    if not isinstance(a, dict):
        return "anchor is not an object"
    n, head = a.get("n"), a.get("head")
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        return "anchor count %r is not a non-negative integer" % (n,)
    if not (isinstance(head, str) and len(head) == 64 and all(c in "0123456789abcdef" for c in head)):
        return "anchor head %r is not a 64-hex sig" % (head,)
    if (n == 0) != (head == GENESIS):
        return "anchor n=%d with head %s is inconsistent" % (n, head[:12])
    return None


def ledger_anchors(events) -> dict:
    """Anchors published as rimflow notes (text starting ARENA_ANCHOR) -> {arm: [anchor]}. An unusable anchor
    (negative count, bad head) is kept with an `error` key: check_anchors() refuses it, report() lists it."""
    by = {}
    for ev in events:
        if ev.get("event") == "note":
            src = "note tsn=%s seat=%s item=%s" % (ev.get("tsn", "?"), ev.get("seat") or ev.get("who") or "?",
                                                   ev.get("id", "?"))
            for a in parse_anchor_note(ev.get("text")):
                err = a.get("error") or anchor_error(a)
                a["note"] = src
                if err:
                    a["error"] = "%s (%s)" % (err, src)
                by.setdefault(a["arm"], []).append(a)
    return by


def verify_ledger_anchors(external: dict, token: str) -> dict:
    """Copy of `external` in which every anchor whose lsig is not the harness HMAC carries an `error` (forged or
    unsigned: listed, never applied, confers no trust)."""
    out = {}
    for arm, lst in (external or {}).items():
        for a in lst:
            a = dict(a)
            if not a.get("error") and not anchor_error(a):
                want = _ledger_sig(token, arm, a["n"], a["head"])
                if not (isinstance(a.get("lsig"), str) and hmac.compare_digest(a["lsig"], want)):
                    a["error"] = "anchor note signature invalid: not minted with the harness token (%s)" % a.get(
                        "note", "ledger")
            out.setdefault(arm, []).append(a)
    return out


def check_anchors(accepted: list[dict], anchors: list[dict], errors: list | None = None) -> list[str]:
    """Violations: the log is shorter than an anchor, or the record at an anchored position has another sig.
    An unusable anchor is not applied: its reason goes to `errors` (it can neither refuse nor clear an arm)."""
    out = []
    for a in anchors:
        err = a.get("error") if isinstance(a, dict) else None
        err = err or anchor_error(a)
        if err:
            if errors is not None:
                errors.append(err)
            continue
        n = a["n"]
        if n > len(accepted):
            out.append("log has %d accepted record(s), anchor of %s says %d (deleted tail or file)"
                       % (len(accepted), a.get("ts", "ledger"), n))
        elif n and accepted[n - 1]["sig"] != a["head"]:
            out.append("record %d sig differs from anchor of %s (history rewritten)" % (n, a.get("ts", "ledger")))
    return out


class HarnessWriter:
    """The only write path. Construct with the arena paths inside an open harness_pass() (or pass `cap=`); it reads
    the token itself, so only a harness entrypoint process that can read the token file (and is not an arm process)
    can build one. `token=` is for selftests that plant a wrong token. Every emit re-checks the capability, stamps
    `prov` and appends an anchor (see module doc)."""

    def __init__(self, p: dict | None = None, token: str | None = None, cap: PassCapability | None = None):
        self.p = p or A.paths()
        _check_token_location(token_path(self.p), self.p)
        _check_harness_process(self.p)
        self._cap = cap or _active_cap(self.p)
        self._cap.check()
        if token is None:
            token = _read_token(self.p)
        self._token = token

    def accepted(self, arm: str) -> list[dict]:
        return verify(self.p, arm, self._token)["accepted"]

    def emit(self, arm: str, event: str, *, lane: str, run_id: str, ts: str | None = None, **fields) -> dict:
        self._cap.check()
        if "prov" in fields:
            raise Rejected("prov is stamped by the writer, never passed in")
        rec = {"ts": ts or now_ts(), "arm": arm, "lane": lane, "run_id": run_id, "event": event}
        rec.update({k: v for k, v in fields.items() if v is not None})
        rec["prov"] = provenance(self._cap)
        validate_record(rec)
        f = arm_file(self.p, arm)
        f.parent.mkdir(parents=True, exist_ok=True)
        with open(f, "a+", encoding="utf-8") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            fh.seek(0)
            body = fh.read()
            if body and not body.endswith("\n"):
                fh.write("\n")      # quarantine a partial last line as its own (rejected) line
            lines = [l for l in body.splitlines() if l.strip()]
            tail = verify_lines(lines, self._token, arm)
            # forged lines already in the file are tolerated (they stay REJECTED on read; refusing to write would
            # let an agent stop the harness by appending junk); the chain continues from the last accepted line
            if event == "test_start" and any(x is rec for x in flagged_same_agent(tail["accepted"] + [rec])):
                rec["rule"] = FLAG_SAME_AGENT
            _roster_add(self.p, self._token, arm)        # rostered BEFORE its first record exists
            rec["sig"] = _sign(self._token, tail["prev"], rec)
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush(); os.fsync(fh.fileno())
            a = make_anchor(arm, tail["accepted"] + [rec], self._token)
            append_anchor(self.p, a)
            witness_append(self.p, dict(a, kind="anchor"))
            self._cap.last_anchor[arm] = a
        return rec


def verify_lines(lines: list[str], token: str, arm: str) -> dict:
    """Accepted = the unbroken chain from GENESIS. After a break, a line whose sig chains from the previous RAW line's
    sig is `recoverable` (genuinely signed data stranded behind a gap); it is still rejected and never counted."""
    acc, rej, rec_ok, prev, seen, raw_prev = [], [], [], GENESIS, set(), None
    for n, raw in enumerate(lines, 1):
        rec, ok, resync = None, False, False
        try:
            rec = json.loads(raw)
            sig = rec.get("sig")
            if isinstance(sig, str) and rec.get("arm") == arm and sig not in seen:
                ok = hmac.compare_digest(sig, _sign(token, prev, rec))
                resync = not ok and raw_prev is not None and hmac.compare_digest(sig, _sign(token, raw_prev, rec))
        except (ValueError, AttributeError, TypeError):
            rec = None
        if ok:
            seen.add(sig); prev = sig; acc.append(rec)
        else:
            rej.append((n, raw))
            if resync:
                rec_ok.append((n, rec)); seen.add(sig)
        raw_prev = rec.get("sig") if isinstance(rec, dict) and isinstance(rec.get("sig"), str) else None
    return {"accepted": acc, "rejected": rej, "recoverable": rec_ok, "prev": prev}


# ---------------------------------------------------------------- analysis (pure functions over accepted records)

def _t(r: dict) -> float:
    try:
        return ts_epoch(r.get("ts"))
    except ValueError:
        return float("inf")             # an unparseable ts (pre-round-2 line) sorts last, never first


def ordered(recs: list[dict]) -> list[dict]:
    """Records by event time (UTC) across the whole log, ties in file order. Every analysis below uses this, so a
    late import of an earlier event lands where it happened, not where it was appended."""
    return [r for _, r in sorted(enumerate(recs), key=lambda x: (_t(x[1]), x[0]))]


def out_of_order(recs: list[dict]) -> int:
    """Records (file order) whose ts is earlier than a record appended before them: late imports."""
    n, hi = 0, float("-inf")
    for r in recs:
        t = _t(r)
        if t < hi:
            n += 1
        hi = max(hi, t)
    return n


def build_id(r: dict):
    """The build a build_end produced / a test names: detail.build_id, else sha, else None."""
    return (r.get("detail") or {}).get("build_id") or r.get("sha")


SKEW_S = 300        # a build of the task at or up to 5 min AFTER a test_start is ambiguous (clock skew, equal ts)


def _task_key(x):
    """A task id for matching: stripped (as card `unblocked` tasks are). Non-strings pass through unchanged."""
    return x.strip() if isinstance(x, str) else x


def build_ids(r: dict) -> set:
    """Every id a record names for its build: detail.build_id and sha (normalised)."""
    return {n for n in (_norm_key((r.get("detail") or {}).get("build_id")), _norm_key(r.get("sha"))) if n}


def _matches(test: dict, build: dict) -> bool:
    """A test of the same task matches a build when it names no id, or shares one of the build's ids (a test that
    names the sha of a build that also has a build_id is still that build)."""
    if build["event"] != "build_end" or _task_key(build.get("task")) != _task_key(test.get("task")):
        return False
    want = build_ids(test)
    return not want or bool(want & build_ids(build))


def _target_build(seq: list[dict], i: int) -> int | None:
    """Index in time-ordered `seq` of the build the test_start at i tests: the latest earlier build_end of the
    same task that matches it (see _matches). Only a matched build is ever credited as tested."""
    for j in range(i - 1, -1, -1):
        if _matches(seq[i], seq[j]):
            return j
    return None


def _suspect_builds(seq: list[dict], i: int) -> list[int]:
    """Builds the test at i may really be testing, for the SAME-AGENT FLAG only (never credit): the matched build;
    when the test names an id no build has, the latest earlier build of the task; when nothing earlier matches, the
    first later matching build (test_before_build); and every matching build at/after the test within SKEW_S
    (ambiguous order)."""
    t, out = seq[i], []
    j = _target_build(seq, i)
    if j is not None:
        out.append(j)
    elif build_ids(t):
        k = next((k for k in range(i - 1, -1, -1) if seq[k]["event"] == "build_end"
                  and _task_key(seq[k].get("task")) == _task_key(t.get("task"))), None)
        if k is not None:
            out.append(k)
    later = [k for k in range(i + 1, len(seq)) if _matches(t, seq[k])]
    if j is None and later:
        out.append(later[0])
    out += [k for k in later if _t(seq[k]) - _t(t) <= SKEW_S and k not in out]
    return out


def ambiguous_order(recs: list[dict]) -> list[dict]:
    """test_start records with a matching build of the task at or up to SKEW_S after them: which came first cannot
    be told from the clocks (skew, equal ts)."""
    seq = ordered(recs)
    return [seq[i] for i, r in enumerate(seq) if r["event"] == "test_start"
            and any(_matches(r, seq[k]) and _t(seq[k]) - _t(r) <= SKEW_S for k in range(i + 1, len(seq)))]


def _tests(seq: list[dict]):
    """-> [(i, target index or None)] for every test_start in time-ordered seq."""
    return [(i, _target_build(seq, i)) for i, r in enumerate(seq) if r["event"] == "test_start"]


def _tester(r: dict) -> str | None:
    return norm_id((r.get("detail") or {}).get("tester"))


def _builder(r: dict) -> str | None:
    return norm_id((r.get("detail") or {}).get("builder"))


def _different(tester: str | None, builder: str | None) -> bool:
    """A test counts as by a different agent only when both ids are usable, the tester is attributed, and they
    differ after normalisation."""
    return bool(tester and builder and not tester.startswith(UNATTRIBUTED) and not builder.startswith(UNATTRIBUTED)
                and tester != builder)


def flagged_same_agent(recs: list[dict]) -> list[dict]:
    """test_start records whose tester is the builder of a build they may be testing (_suspect_builds: the matched
    build, the build behind a non-matching id, a later or clock-ambiguous build of the task)."""
    seq = ordered(recs)
    return [seq[i] for i, r in enumerate(seq) if r["event"] == "test_start" and _tester(r)
            and any(_builder(seq[k]) == _tester(r) for k in _suspect_builds(seq, i))]


def test_before_build(recs: list[dict]) -> list[dict]:
    """test_start with no earlier matching build_end although a matching one exists LATER in time."""
    seq, out = ordered(recs), []
    for i, j in _tests(seq):
        if j is None and any(_matches(seq[i], r) for r in seq[i + 1:]):
            out.append(seq[i])
    return out


def _first_different_test(seq: list[dict]) -> dict:
    """{build index: index of the first test_start of THAT build by a different agent}."""
    first = {}
    for i, j in _tests(seq):
        if j is not None and j not in first and _different(_tester(seq[i]), _builder(seq[j])):
            first[j] = i
    return first


def untested_builds(recs: list[dict]) -> list[dict]:
    """build_end with no later test_start of the same (task, build) by a DIFFERENT agent."""
    seq = ordered(recs)
    first = _first_different_test(seq)
    return [r for j, r in enumerate(seq) if r["event"] == "build_end" and j not in first]


def latency_minutes(recs: list[dict]) -> list[float]:
    """build_end -> first different-agent test_start of that build, minutes, per tested build (time order)."""
    seq = ordered(recs)
    first = _first_different_test(seq)
    return [(_t(seq[i]) - _t(seq[j])) / 60.0 for j, i in sorted(first.items())]


def owner_minutes(recs: list[dict]) -> dict:
    """Cards deduped by NORMALISED card_id (NFKC, format chars dropped, whitespace collapsed, casefold): the
    EARLIEST by event time wins; a duplicate with other minutes or another unblocked list is counted in
    `card_conflicts`. unblocked task ids are stripped. A card whose minutes, card_id or unblocked list is malformed
    (pre-validation line) is skipped and counted in `malformed`, never crashes the report."""
    cards, seen, malformed, conflicts = [], {}, 0, 0
    for r in ordered(recs):
        if r["event"] != "card":
            continue
        d = r.get("detail") or {}
        cid, un = d.get("card_id"), d.get("unblocked")
        key = _norm_key(cid)
        if not (_minutes_ok(r.get("minutes")) and key and isinstance(un, list)
                and all(isinstance(t, str) and t.strip() for t in un)):
            malformed += 1
            continue
        c = (float(r["minutes"]), sorted({t.strip() for t in un}))
        if key in seen:
            conflicts += seen[key] != c
            continue
        seen[key] = c; cards.append(c)
    touch = [r for r in recs if r["event"] == "owner_touch" and _minutes_ok(r.get("minutes"))]
    unblocked = sorted({t for c in cards for t in c[1]})
    cm = sum(c[0] for c in cards)
    tm = sum(float(r["minutes"]) for r in touch)
    return {"cards": len(cards), "card_minutes": cm, "touch_minutes": tm, "minutes": cm + tm,
            "unblocked_tasks": unblocked, "malformed_cards": malformed, "card_conflicts": conflicts}


def accepted_tasks(recs: list[dict]) -> set:
    """Tasks whose LAST judge verdict (event time) is 'accept'."""
    last = {}
    for r in ordered(recs):
        if r["event"] == "judge" and isinstance(r.get("task"), str):
            last[r["task"].strip()] = r.get("verdict")
    return {t for t, v in last.items() if v == "accept"}


def ledger_done(recs: list[dict]) -> int:
    """Adapter records (build_end/test_end) that moved a v3 ledger item into done."""
    return sum(1 for r in recs if r["event"] in ("build_end", "test_end") and (r.get("detail") or {}).get("done") is True)


def output_report(recs: list[dict], points: dict | None = None) -> dict:
    """Accepted output (last judge verdict 'accept', default 1 point a task), with and without owner-unblocked tasks.
    No judge event at all but ledger done transitions: NOT COMPARABLE (points None), never a silent zero."""
    points = points or {}
    acc = accepted_tasks(recs)
    om = owner_minutes(recs)
    un = set(om["unblocked_tasks"])
    judged = any(r["event"] == "judge" for r in recs)
    ld = ledger_done(recs)
    base = {"owner_minutes": om["minutes"], "malformed_cards": om["malformed_cards"],
            "card_conflicts": om["card_conflicts"], "ledger_done": ld}
    if not judged and ld:
        return dict(base, output_comparable=False, points_with_unblocked=None, points_without_unblocked=None,
                    owner_unblocked_accepted=[], minutes_per_point_with=None, minutes_per_point_without=None,
                    output_note="%d ledger done transition(s), 0 judge events: a self-closed v3 item is not a "
                                "judge-accepted point; run arena_judge on these tasks to compare" % ld)
    pts = lambda ts: sum(points.get(t, 1) for t in ts)
    withall, without = pts(acc), pts(acc - un)
    return dict(base, output_comparable=True, points_with_unblocked=withall, points_without_unblocked=without,
                owner_unblocked_accepted=sorted(acc & un),
                minutes_per_point_with=(om["minutes"] / withall) if withall else None,
                minutes_per_point_without=(om["minutes"] / without) if without else None)


def unprovenanced(recs: list[dict]) -> int:
    """Records with no prov, or whose prov names no harness entrypoint (selftests allowed). Forensic only."""
    ok = lambda e: isinstance(e, str) and (e in ENTRYPOINTS or e.startswith(SELFTEST_ENTRY_PREFIX))
    return sum(1 for r in recs if not (isinstance(r.get("prov"), dict) and ok(r["prov"].get("entry"))))


def report(p: dict, token: str | None = None, external: dict | None = None) -> dict:
    """Per arm. FAILS CLOSED:
      - an arm whose log contradicts a usable anchor (local store, witness, or `external` = ledger_anchors()) is
        REFUSED;
      - an arm with accepted records but NO usable anchor at all (local store deleted, nothing published) is
        REFUSED as UNMEASURED: its history cannot be told from a re-signed one;
      - every ROSTERED arm (roster file, witness, published @roster) is reported; a rostered arm whose log is gone
        or empty is REFUSED, and a roster that lost entries makes `_trust` False;
      - `trusted` is True only when a SIGNED ledger anchor covers the arm's WHOLE accepted log (n == accepted) AND
        the witness is readable and its newest anchor for the arm is that same n (a tail deleted after the newest
        ledger anchor is still in the witness); `_trust` summarises: trusted only if every arm is.
    Unusable anchors (negative count, bad head, malformed or unsigned token, forged signature) are listed in
    `anchor_errors`, never applied, never a crash."""
    token = token or _read_token(p)
    an = read_anchors(p, token)
    external = verify_ledger_anchors(external or {}, token)
    wit = witness_read(p, token)
    ros = read_roster(p, token)
    wit_roster = {e.get("arm") for e in wit["roster"]}
    rostered = set(ros["arms"]) | wit_roster | set(wit["anchors"])
    arms = {f.stem for f in p["events"].glob("*.jsonl")} | set(an["by_arm"]) | set(external) | rostered
    non_arm = {k for k in arms if not re.fullmatch(r"[A-Za-z0-9_-]+", str(k), re.ASCII) or k == "harness"}
    arms -= non_arm
    out = {}
    for arm in sorted(arms):
        try:
            v = verify(p, arm, token)
        except Rejected:
            continue                        # not an arm name (stray file); never a reason to drop a real arm
        recs = v["accepted"]
        loc, ext, wan = an["by_arm"].get(arm, []), external.get(arm, []), wit["anchors"].get(arm, [])
        errors = []
        bad = check_anchors(recs, loc + ext + wan, errors)
        usable_ext = [a for a in ext if not (a.get("error") or anchor_error(a))]
        usable_loc = [a for a in loc if not anchor_error(a)]
        usable_wit = [a for a in wan if not anchor_error(a)]
        upto = max((a["n"] for a in usable_ext), default=0)
        wmax = max((a["n"] for a in usable_wit), default=0)
        witness_ok = wit["status"] == "ok" and wmax == len(recs)
        base = {"accepted": len(recs), "rejected": len(v["rejected"]), "recoverable": len(v["recoverable"]),
                "undecodable_lines": v["undecodable"],
                "anchors": len(usable_loc) + len(usable_ext), "external_anchored_upto": upto,
                "witness_anchored_upto": wmax, "rostered": arm in rostered,
                "trusted": bool(not bad and recs and usable_ext and upto == len(recs) and witness_ok)}
        if errors:
            base["anchor_errors"] = errors
        if arm in rostered and not recs:
            bad = bad or ["rostered arm has no accepted record (log deleted or emptied)"]
        if not bad and recs and not usable_loc and not usable_ext and not usable_wit:
            bad = ["UNMEASURED: %d accepted record(s) and no anchor at all (local anchor store missing or emptied, "
                   "none published): history cannot be told from a re-signed one" % len(recs)]
        if bad:
            out[arm] = dict(base, refused=bad, trusted=False)
            continue
        if recs and not base["trusted"]:
            base["trust_note"] = (
                "local anchors only: a token holder can rewrite them; publish with `anchor-note` and "
                "report --ledger-anchors for a trusted report" if not usable_ext else
                "records %d..%d are after the newest ledger anchor" % (upto + 1, len(recs)) if upto != len(recs) else
                "witness %s, newest witness anchor n=%d of %d" % (wit["status"], wmax, len(recs)))
        if arm not in rostered:
            base["trusted"] = False
            base["trust_note"] = "arm log exists but the arm is not in the roster"
        out[arm] = dict(base, flagged_same_agent=len(flagged_same_agent(recs)),
                        untested_builds=len(untested_builds(recs)), latency_min=latency_minutes(recs),
                        test_before_build=len(test_before_build(recs)), ambiguous_order=len(ambiguous_order(recs)),
                        out_of_order=out_of_order(recs), unprovenanced=unprovenanced(recs), **output_report(recs))
    if an["bad"]:
        out["_anchor_store"] = {"bad_anchor_lines": len(an["bad"])}
    roster_problems = ["roster line(s) unverifiable or out of chain: %d" % len(ros["bad"])] if ros["bad"] else []
    lost = sorted(a for a in (wit_roster | set(wit["anchors"])) if a not in ros["arms"])
    if lost:
        roster_problems.append("witness knows arm(s) missing from the roster file: %s" % lost)
    rerrs = []
    for ra in external.get("@roster", []):
        err = ra.get("error") or anchor_error(ra)
        if err:
            rerrs.append(err)
        elif ra["n"] > ros["n"] or (ra["n"] and ra["n"] == ros["n"] and ra["head"] != ros["head"]):
            roster_problems.append("published roster anchor n=%d contradicts the roster file (n=%d)" % (ra["n"], ros["n"]))
    other = [a.get("error") or "anchor for non-arm %r" % k for k in non_arm - {"@roster"} for a in external.get(k, [])]
    arms_out = [k for k in out if not k.startswith("_")]
    out["_trust"] = {"trusted": bool(arms_out) and all(out[k]["trusted"] for k in arms_out) and not roster_problems,
                     "external_anchors": bool(external), "witness": wit["status"], "witness_bad_entries": wit["bad"],
                     "rostered_arms": sorted(rostered),
                     "untrusted_arms": sorted(k for k in arms_out if not out[k]["trusted"])}
    if roster_problems:
        out["_trust"]["roster_problems"] = roster_problems
    if rerrs + other:
        out["_trust"]["ledger_anchor_errors"] = rerrs + other
    return out


def anchor_note_command(p: dict, item: str = "ARENA_EVENTLOG_BUILD_AGENTS_MAY_NOT_WRITE") -> str | None:
    """The `rimflow note` that publishes every arm's current head into the git ledger. PRINTED, never run here."""
    token = _read_token(p)
    heads = [make_anchor(f.stem, verify(p, f.stem, token)["accepted"], token)
             for f in sorted(p["events"].glob("*.jsonl")) if f.stem != "harness"]
    if not heads:
        return None
    heads.append(roster_anchor(p, token))
    return ("python3 src/RimMandrake/rimflow/cli.py note %s --seat FOUNDRY --why 'arena harness anchor: event-log "
            "heads published so a deleted or forged event is caught at report time' --text '%s'"
            % (item, anchor_note_text(heads)))


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=("init-token", "report", "anchor-note"))
    ap.add_argument("--ledger-anchors", action="store_true", help="also check ARENA_ANCHOR notes in the rimflow ledger")
    a = ap.parse_args(argv)
    p = A.paths()
    if a.cmd == "init-token":
        print(init_token(p))
    elif a.cmd == "anchor-note":
        print(anchor_note_command(p) or "no arm logs")
    else:
        ext = None
        if a.ledger_anchors:
            sys.path.insert(0, str(HERE.parent.parent))
            from rimflow import model
            ext = ledger_anchors(model.read())
        print(json.dumps(report(p, external=ext), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
