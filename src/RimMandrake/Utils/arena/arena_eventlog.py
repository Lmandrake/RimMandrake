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
  - report() FAILS CLOSED: an arm with records but no anchor at all (local store deleted) is refused UNMEASURED, and
    an arm is `trusted` only when a ledger-published (external) anchor covers its whole accepted log.
RESIDUAL SAME-UID RISK, NOT CLOSED: an agent running as uid 1000 that reads the token can call _sign() directly (or
copy this file and delete the checks) and write any record, `prov` included, with a valid signature; it can ptrace
or read /proc of a live harness process. The capability, prov and cwd/RM_ARM checks stop the casual path (library
use from an arm) and leave forensic traces; they are not a boundary. Only a separate OS user (or a signer outside
the arm's machine) closes this. Ledger-published anchors bound what it can rewrite: history before the newest
external anchor; events forged AFTER it pass every check here. Publish anchors at every pass end. An agent can also
post a bogus ARENA_ANCHOR note: that can only make report() refuse an honest arm (loud, investigated).

Event record: {ts, arm, lane, run_id, task, event, sha?, verdict?, ite?, minutes?, rule?, detail?, prov, sig}.
ts is ISO-8601 WITH a zone (Z or +hh:mm), compared in UTC. Analysis orders records by event time across the whole
log (stable on file order), never by append order, so a late import of an earlier event is placed where it happened.
Different-agent rule: build_end.detail.builder, test_start.detail.tester; a test_start targets ONE build: the latest
earlier build_end of the same task with the same build id (detail.build_id, else sha) when the test names one, else
the latest earlier build_end of the task. It is FLAGGED when its tester is that build's builder (recomputed; the
stamped rule="tester_is_builder" is a convenience, never trusted). A test_start earlier than every matching build
is reported as `test_before_build`. Agent ids are compared NORMALISED (strip + casefold); a builder/tester id that
is not a string, is blank, or is all digits is refused at write; an id starting `unattributed:` never counts as a
different agent.
Owner minutes: `card` (minutes = rm-pulse dwell, detail.card_id, detail.unblocked = tasks the answer unblocked) and
`owner_touch` (minutes); minutes are finite, >= 0, never bool; card_id a non-empty string, unblocked a list of
non-empty strings. A card_id seen twice counts once. Reported per arm, and output (each task by its LAST judge
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
import secrets
import sys
import tempfile
import time
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


def _entrypoint() -> str:
    """Real path of the running __main__ script ('' for -c, a REPL or an embedded interpreter)."""
    f = getattr(sys.modules.get("__main__"), "__file__", None)
    return os.path.realpath(f) if f else ""


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
            "cwd": cwd, "entry": os.path.basename(_entrypoint()) or None,
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
    e = _entrypoint()
    name = os.path.basename(e)
    if not e or os.path.dirname(e) != str(HERE):
        raise Rejected("signing needs a harness entrypoint run from %s as __main__ (got %r): library use from "
                       "another script, -c or a REPL is refused" % (HERE, e or None))
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
                           "entry": os.path.basename(_entrypoint()), "cap_id": self.cap_id,
                           "nonce_sha": hashlib.sha256(self._nonce.encode()).hexdigest()}, sort_keys=True).encode()
        self._fd = os.open(str(self.path), os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(self._fd, body)
        self._body = body
        self.closed = False

    def check(self):
        if self.closed:
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
        if (on_disk.st_ino, on_disk.st_dev) != (held.st_ino, held.st_dev) or on_disk.st_mode & 0o077:
            raise Rejected("pass capability file %s was replaced or opened up" % self.path)
        if os.pread(self._fd, len(self._body) + 1, 0) != self._body or \
                json.loads(self._body)["nonce_sha"] != hashlib.sha256(self._nonce.encode()).hexdigest():
            raise Rejected("pass capability file %s content changed" % self.path)

    def close(self):
        if self.closed:
            return
        self.closed = True
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
    e = os.path.basename(_entrypoint())
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
    """An agent id for comparison: strip + casefold. None for anything that is not a usable id."""
    if not isinstance(x, str):
        return None
    n = x.strip().casefold()
    return n if n and not n.isdigit() else None


def _minutes_ok(m) -> bool:
    return isinstance(m, (int, float)) and not isinstance(m, bool) and math.isfinite(m) and m >= 0


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


def _read_lines(f: Path) -> list[str]:
    return [l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()] if f.exists() else []


def verify(p: dict, arm: str, token: str | None = None) -> dict:
    """-> {"accepted": [rec], "rejected": [(lineno, raw)], "recoverable": [(lineno, rec)]}. Needs the token."""
    v = verify_lines(_read_lines(arm_file(p, arm)), token or _read_token(p), arm)
    return {k: v[k] for k in ("accepted", "rejected", "recoverable")}


# ---------------------------------------------------------------- anchors

def _anchor_sign(token: str, a: dict) -> str:
    return hmac.new(token.encode(), ("anchor:" + _canon(a)).encode(), hashlib.sha256).hexdigest()


def make_anchor(arm: str, accepted: list[dict], token: str, ts: str | None = None) -> dict:
    a = {"ts": ts or now_ts(), "arm": arm, "n": len(accepted), "head": accepted[-1]["sig"] if accepted else GENESIS}
    a["sig"] = _anchor_sign(token, a)
    return a


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
    """One `rimflow note --text` body publishing the current head of each arm (external, git-ledger anchor)."""
    return NOTE_PREFIX + " " + " ".join("%s:%d:%s" % (a["arm"], a["n"], a["head"]) for a in anchors)


def parse_anchor_note(text: str) -> list[dict]:
    if not isinstance(text, str) or not text.startswith(NOTE_PREFIX + " "):
        return []
    out = []
    for tok in text[len(NOTE_PREFIX) + 1:].split():
        try:
            arm, n, head = tok.split(":")
            out.append({"arm": arm, "n": int(n), "head": head, "external": True})
        except ValueError:
            continue
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
            for a in parse_anchor_note(ev.get("text")):
                err = anchor_error(a)
                if err:
                    a["error"] = "%s (note %s)" % (err, ev.get("tsn", ev.get("id", "?")))
                by.setdefault(a["arm"], []).append(a)
    return by


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
            if event == "test_start":
                seq = ordered(tail["accepted"] + [rec])
                j = _target_build(seq, next(i for i, x in enumerate(seq) if x is rec))
                b = norm_id((seq[j].get("detail") or {}).get("builder")) if j is not None else None
                if b and b == norm_id((rec.get("detail") or {}).get("tester")):
                    rec["rule"] = FLAG_SAME_AGENT
            rec["sig"] = _sign(self._token, tail["prev"], rec)
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush(); os.fsync(fh.fileno())
            append_anchor(self.p, make_anchor(arm, tail["accepted"] + [rec], self._token))
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


def _target_build(seq: list[dict], i: int) -> int | None:
    """Index in time-ordered `seq` of the build the test_start at i tests: the latest earlier build_end of the
    same task with the same build id when the test names one, else the latest earlier build_end of the task."""
    t = seq[i]
    want = build_id(t)
    for j in range(i - 1, -1, -1):
        r = seq[j]
        if r["event"] == "build_end" and r.get("task") == t.get("task") and (want is None or build_id(r) == want):
            return j
    return None


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
    return bool(tester and builder and not tester.startswith(UNATTRIBUTED) and tester != builder)


def flagged_same_agent(recs: list[dict]) -> list[dict]:
    """test_start records whose tester is the builder of the build they test (per task AND build id)."""
    seq = ordered(recs)
    return [seq[i] for i, j in _tests(seq) if j is not None and _builder(seq[j]) and _builder(seq[j]) == _tester(seq[i])]


def test_before_build(recs: list[dict]) -> list[dict]:
    """test_start with no earlier matching build_end although a matching one exists LATER in time."""
    seq, out = ordered(recs), []
    for i, j in _tests(seq):
        if j is None:
            t, want = seq[i], build_id(seq[i])
            if any(r["event"] == "build_end" and r.get("task") == t.get("task") and (want is None or build_id(r) == want)
                   for r in seq[i + 1:]):
                out.append(t)
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
    """Cards deduped by card_id (first record wins); a card whose minutes, card_id or unblocked list is malformed
    (pre-validation line) is skipped and counted in `malformed`, never crashes the report."""
    cards, seen, malformed = [], set(), 0
    for r in recs:
        if r["event"] != "card":
            continue
        d = r.get("detail") or {}
        cid, un = d.get("card_id"), d.get("unblocked")
        if not (_minutes_ok(r.get("minutes")) and isinstance(cid, str) and isinstance(un, list)
                and all(isinstance(t, str) for t in un)):
            malformed += 1
            continue
        if cid in seen:
            continue
        seen.add(cid); cards.append(r)
    touch = [r for r in recs if r["event"] == "owner_touch" and _minutes_ok(r.get("minutes"))]
    unblocked = sorted({t for r in cards for t in r["detail"]["unblocked"]})
    cm = sum(r["minutes"] for r in cards)
    tm = sum(r["minutes"] for r in touch)
    return {"cards": len(cards), "card_minutes": cm, "touch_minutes": tm, "minutes": cm + tm,
            "unblocked_tasks": unblocked, "malformed_cards": malformed}


def accepted_tasks(recs: list[dict]) -> set:
    """Tasks whose LAST judge verdict (event time) is 'accept'."""
    last = {}
    for r in ordered(recs):
        if r["event"] == "judge" and isinstance(r.get("task"), str):
            last[r["task"]] = r.get("verdict")
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
    base = {"owner_minutes": om["minutes"], "malformed_cards": om["malformed_cards"], "ledger_done": ld}
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
      - an arm whose log contradicts a usable anchor (local store, or `external` = ledger_anchors()) is REFUSED;
      - an arm with accepted records but NO usable anchor at all (local store deleted, nothing published) is
        REFUSED as UNMEASURED: its history cannot be told from a re-signed one;
      - `trusted` is True only when a ledger-published anchor covers the arm's WHOLE accepted log (n == accepted);
        `_trust` summarises: trusted only if every arm is.
    Unusable anchors (negative count, bad head) are listed in `anchor_errors`, never applied, never a crash."""
    token = token or _read_token(p)
    an = read_anchors(p, token)
    external = external or {}
    arms = {f.stem for f in p["events"].glob("*.jsonl")} | set(an["by_arm"]) | set(external)
    arms.discard("harness")
    out = {}
    for arm in sorted(arms):
        try:
            v = verify(p, arm, token)
        except Rejected:
            continue                        # not an arm name (stray file); never a reason to drop a real arm
        recs = v["accepted"]
        loc, ext = an["by_arm"].get(arm, []), external.get(arm, [])
        errors = []
        bad = check_anchors(recs, loc + ext, errors)
        usable_ext = [a for a in ext if not (a.get("error") or anchor_error(a))]
        usable_loc = [a for a in loc if not anchor_error(a)]
        upto = max((a["n"] for a in usable_ext), default=0)
        base = {"accepted": len(recs), "rejected": len(v["rejected"]), "recoverable": len(v["recoverable"]),
                "anchors": len(usable_loc) + len(usable_ext), "external_anchored_upto": upto,
                "trusted": bool(not bad and recs and usable_ext and upto == len(recs))}
        if errors:
            base["anchor_errors"] = errors
        if not bad and recs and not usable_loc and not usable_ext:
            bad = ["UNMEASURED: %d accepted record(s) and no anchor at all (local anchor store missing or emptied, "
                   "none published): history cannot be told from a re-signed one" % len(recs)]
        if bad:
            out[arm] = dict(base, refused=bad, trusted=False)
            continue
        if recs and not base["trusted"]:
            base["trust_note"] = ("local anchors only: a token holder can rewrite them; publish with `anchor-note` and "
                                  "report --ledger-anchors for a trusted report" if not usable_ext else
                                  "records %d..%d are after the newest ledger anchor" % (upto + 1, len(recs)))
        out[arm] = dict(base, flagged_same_agent=len(flagged_same_agent(recs)),
                        untested_builds=len(untested_builds(recs)), latency_min=latency_minutes(recs),
                        test_before_build=len(test_before_build(recs)), out_of_order=out_of_order(recs),
                        unprovenanced=unprovenanced(recs), **output_report(recs))
    if an["bad"]:
        out["_anchor_store"] = {"bad_anchor_lines": len(an["bad"])}
    arms_out = [k for k in out if not k.startswith("_")]
    out["_trust"] = {"trusted": bool(arms_out) and all(out[k]["trusted"] for k in arms_out),
                     "external_anchors": bool(external),
                     "untrusted_arms": sorted(k for k in arms_out if not out[k]["trusted"])}
    return out


def anchor_note_command(p: dict, item: str = "ARENA_EVENTLOG_BUILD_AGENTS_MAY_NOT_WRITE") -> str | None:
    """The `rimflow note` that publishes every arm's current head into the git ledger. PRINTED, never run here."""
    token = _read_token(p)
    heads = [make_anchor(f.stem, verify(p, f.stem, token)["accepted"], token)
             for f in sorted(p["events"].glob("*.jsonl")) if f.stem != "harness"]
    if not heads:
        return None
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
