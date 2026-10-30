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
Not covered: an agent that has read the token can forge events AFTER the newest anchor it cannot also rewrite (the
local anchor store is same-user writable; only ledger-published anchors are out of its reach). Publish anchors at
every pass end to keep that window small. An agent can also post a bogus ARENA_ANCHOR note: that can only make
report() refuse an honest arm (loud, investigated), never hide a forgery.

Event record: {ts, arm, lane, run_id, task, event, sha?, verdict?, ite?, minutes?, rule?, detail?, sig}.
Different-agent rule: build_end.detail.builder, test_start.detail.tester; a test_start whose tester equals the
builder of the same task (latest preceding build_end) is FLAGGED (analyze() recomputes it; the stamped
rule="tester_is_builder" is a convenience, never trusted). Agent ids are compared NORMALISED (strip + casefold);
a builder/tester id that is not a string, is blank, or is all digits is refused at write.
Owner minutes: `card` (minutes = rm-pulse dwell, detail.card_id, detail.unblocked = tasks the answer unblocked) and
`owner_touch` (minutes); minutes are finite, >= 0, never bool. A card_id seen twice counts once. Reported per arm,
and output (each task by its LAST judge verdict) reported with and without owner-unblocked work.
A partial final line (no newline: a crashed writer or a hand edit) is newline-terminated before the next write, so
it stays one rejected line and never swallows the next record. After a gap (a deleted line), later lines that still
chain to each other are reported as `recoverable` (valid signatures, not counted).
"""
from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import hmac
import json
import math
import os
import secrets
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_tasks as A  # noqa: E402

EVENTS = ("freeze", "assign", "pass_start", "pass_end", "build_end", "test_start", "test_end", "gate", "judge",
          "critic_round", "live_take", "live_release", "reload", "canary", "card", "owner_touch", "defect",
          "invalid", "switch", "stop")
FIELDS = ("ts", "arm", "lane", "run_id", "task", "event", "sha", "verdict", "ite", "minutes", "rule", "detail")
REQUIRED = ("ts", "arm", "lane", "run_id", "event")
GENESIS = "0" * 64
FLAG_SAME_AGENT = "tester_is_builder"


class EventLogError(Exception):
    pass


class Rejected(EventLogError):
    """A write refused: no/invalid token, bad schema, or a token path an arm can read."""


def now_ts() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def token_path(p: dict) -> Path:
    env = os.environ.get("ARENA_EVENT_TOKEN_FILE", "").strip()
    if env:
        return Path(env)
    state = os.environ.get("XDG_STATE_HOME", "").strip() or str(Path.home() / ".local" / "state")
    return Path(state) / "rimmandrake" / "arena_harness" / "event_token"


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
    if rec["event"] not in EVENTS:
        raise Rejected("unknown event %r" % rec["event"])
    ev = rec["event"]
    d = rec.get("detail") or {}
    if not isinstance(d, dict):
        raise Rejected("detail must be an object")
    if ev == "build_end" and not (rec.get("task") and norm_id(d.get("builder"))):
        raise Rejected("build_end needs task and a string, non-blank, non-numeric detail.builder (got %r)"
                       % (d.get("builder"),))
    if ev in ("test_start", "test_end") and not (rec.get("task") and norm_id(d.get("tester"))):
        raise Rejected("%s needs task and a string, non-blank, non-numeric detail.tester (got %r)"
                       % (ev, d.get("tester")))
    if ev in ("card", "owner_touch") and not _minutes_ok(rec.get("minutes")):
        raise Rejected("%s needs finite, non-negative, numeric (non-bool) minutes (got %r)" % (ev, rec.get("minutes")))
    if ev == "card":
        if not d.get("card_id") or not isinstance(d.get("unblocked"), list):
            raise Rejected("card needs detail.card_id and a detail.unblocked list (may be empty)")


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


def ledger_anchors(events) -> dict:
    """Anchors published as rimflow notes (text starting ARENA_ANCHOR) -> {arm: [anchor]}."""
    by = {}
    for ev in events:
        if ev.get("event") == "note":
            for a in parse_anchor_note(ev.get("text")):
                by.setdefault(a["arm"], []).append(a)
    return by


def check_anchors(accepted: list[dict], anchors: list[dict]) -> list[str]:
    """Violations: the log is shorter than an anchor, or the record at an anchored position has another sig."""
    out = []
    for a in anchors:
        n = a["n"]
        if n > len(accepted):
            out.append("log has %d accepted record(s), anchor of %s says %d (deleted tail or file)"
                       % (len(accepted), a.get("ts", "ledger"), n))
        elif n and accepted[n - 1]["sig"] != a["head"]:
            out.append("record %d sig differs from anchor of %s (history rewritten)" % (n, a.get("ts", "ledger")))
    return out


class HarnessWriter:
    """The only write path. Construct with the arena paths; it reads the token itself, so only a process that can
    read the harness token file (and is not an arm process) can build one. `token=` is for selftests that plant a
    wrong token. Every emit appends an anchor (see module doc)."""

    def __init__(self, p: dict | None = None, token: str | None = None):
        self.p = p or A.paths()
        if token is None:
            token = _read_token(self.p)
        else:
            _check_token_location(token_path(self.p), self.p)
            _check_harness_process(self.p)
        self._token = token

    def accepted(self, arm: str) -> list[dict]:
        return verify(self.p, arm, self._token)["accepted"]

    def emit(self, arm: str, event: str, *, lane: str, run_id: str, ts: str | None = None, **fields) -> dict:
        rec = {"ts": ts or now_ts(), "arm": arm, "lane": lane, "run_id": run_id, "event": event}
        rec.update({k: v for k, v in fields.items() if v is not None})
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
                b = norm_id(_builder_of(tail["accepted"], rec.get("task")))
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

def _builder_of(recs: list[dict], task) -> str | None:
    for r in reversed(recs):
        if r["event"] == "build_end" and r.get("task") == task:
            return (r.get("detail") or {}).get("builder")
    return None


def _tester(r: dict) -> str | None:
    return norm_id((r.get("detail") or {}).get("tester"))


def _different(tester: str | None, builder: str | None) -> bool:
    """A test counts as by a different agent only when both ids are usable and differ after normalisation."""
    b = norm_id(builder)
    return bool(tester and b and tester != b)


def flagged_same_agent(recs: list[dict]) -> list[dict]:
    """test_start records whose tester is the builder of the latest preceding build_end for that task (normalised)."""
    out = []
    for i, r in enumerate(recs):
        if r["event"] == "test_start":
            b = norm_id(_builder_of(recs[:i], r.get("task")))
            if b and b == _tester(r):
                out.append(r)
    return out


def untested_builds(recs: list[dict]) -> list[dict]:
    """build_end with no later test_start by a DIFFERENT agent on the same task."""
    out = []
    for i, r in enumerate(recs):
        if r["event"] != "build_end":
            continue
        b = (r.get("detail") or {}).get("builder")
        if not any(x["event"] == "test_start" and x.get("task") == r.get("task") and _different(_tester(x), b)
                   for x in recs[i + 1:]):
            out.append(r)
    return out


def latency_minutes(recs: list[dict]) -> list[float]:
    """build_end -> first different-agent test_start, minutes, per tested build."""
    out = []
    for i, r in enumerate(recs):
        if r["event"] != "build_end":
            continue
        b = (r.get("detail") or {}).get("builder")
        for x in recs[i + 1:]:
            if x["event"] == "test_start" and x.get("task") == r.get("task") and _different(_tester(x), b):
                out.append((A._epoch(x["ts"]) - A._epoch(r["ts"])) / 60.0)
                break
    return out


def owner_minutes(recs: list[dict]) -> dict:
    """Cards deduped by card_id (first record wins); minutes that are not finite non-negative numbers are skipped."""
    cards, seen = [], set()
    for r in recs:
        if r["event"] == "card" and _minutes_ok(r.get("minutes")):
            cid = (r.get("detail") or {}).get("card_id")
            if cid in seen:
                continue
            seen.add(cid); cards.append(r)
    touch = [r for r in recs if r["event"] == "owner_touch" and _minutes_ok(r.get("minutes"))]
    unblocked = sorted({t for r in cards for t in (r.get("detail") or {}).get("unblocked") or []})
    cm = sum(r["minutes"] for r in cards)
    tm = sum(r["minutes"] for r in touch)
    return {"cards": len(cards), "card_minutes": cm, "touch_minutes": tm, "minutes": cm + tm,
            "unblocked_tasks": unblocked}


def accepted_tasks(recs: list[dict]) -> set:
    """Tasks whose LAST judge verdict is 'accept'."""
    last = {}
    for r in recs:
        if r["event"] == "judge" and r.get("task"):
            last[r["task"]] = r.get("verdict")
    return {t for t, v in last.items() if v == "accept"}


def output_report(recs: list[dict], points: dict | None = None) -> dict:
    """Accepted output (last judge verdict 'accept', default 1 point a task), with and without owner-unblocked tasks."""
    points = points or {}
    acc = accepted_tasks(recs)
    om = owner_minutes(recs)
    un = set(om["unblocked_tasks"])
    pts = lambda ts: sum(points.get(t, 1) for t in ts)
    withall, without = pts(acc), pts(acc - un)
    return {"owner_minutes": om["minutes"], "points_with_unblocked": withall, "points_without_unblocked": without,
            "owner_unblocked_accepted": sorted(acc & un),
            "minutes_per_point_with": (om["minutes"] / withall) if withall else None,
            "minutes_per_point_without": (om["minutes"] / without) if without else None}


def report(p: dict, token: str | None = None, external: dict | None = None) -> dict:
    """Per arm. An arm whose log contradicts an anchor (local store, or `external` = ledger_anchors()) is REFUSED:
    {"refused": [violations], ...counts} and no output metrics. Anchored arms whose file is gone are reported too."""
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
        base = {"accepted": len(recs), "rejected": len(v["rejected"]), "recoverable": len(v["recoverable"]),
                "anchors": len(an["by_arm"].get(arm, [])) + len(external.get(arm, []))}
        bad = check_anchors(recs, an["by_arm"].get(arm, []) + external.get(arm, []))
        if bad:
            out[arm] = dict(base, refused=bad)
            continue
        out[arm] = dict(base, flagged_same_agent=len(flagged_same_agent(recs)),
                        untested_builds=len(untested_builds(recs)), latency_min=latency_minutes(recs),
                        **output_report(recs))
    if an["bad"]:
        out["_anchor_store"] = {"bad_anchor_lines": len(an["bad"])}
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
