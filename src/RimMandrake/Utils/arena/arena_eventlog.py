#!/usr/bin/env python3
"""arena_eventlog.py - the arena's ONE event log, one JSONL per arm, written only by harness code.

ARENA_EVENTLOG_BUILD_AGENTS_MAY_NOT_WRITE; design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.7,
testpilot_merged_2026-10-29.md §2.3. Paths come from arena_tasks.arena_root()/paths() (agent_storage, `$ARENA_ROOT`
in selftests): `<arena>/events/<arm>.jsonl`. arena_tasks's own `events/harness.jsonl` (freeze events) is a
different, unsigned file; this module reads only per-arm files and never touches it.

WHO MAY WRITE. The events dir is arm-READABLE (arena_tasks.arm_readable_roots), so a file permission cannot keep an
agent out of it; the rule is cryptographic. Every record carries `sig` = HMAC-SHA256(token, prev_sig + canonical
record). The token lives in a file OUTSIDE every arm-readable root (`<arena>/harness/event_token`, or
`$ARENA_EVENT_TOKEN_FILE`), which the writer refuses to use if it sits inside one. An agent that appends a line by
hand cannot sign it, and cannot re-sign a line it deleted or edited (the chain breaks); `verify()` lists every such
line as rejected and every report here counts only accepted records. The writer API has no unsigned path.

Event record: {ts, arm, lane, run_id, task, event, sha?, verdict?, ite?, minutes?, rule?, detail?, sig}.
Different-agent rule: build_end.detail.builder, test_start.detail.tester; a test_start whose tester equals the
builder of the same task (latest preceding build_end) is FLAGGED (analyze() recomputes it; the stamped
rule="tester_is_builder" is a convenience, never trusted).
Owner minutes: `card` (minutes = rm-pulse dwell, detail.card_id, detail.unblocked = tasks the answer unblocked) and
`owner_touch` (minutes). Reported per arm, and output reported with and without owner-unblocked work.
"""
from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import hmac
import json
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
    return Path(env) if env else p["root"] / "harness" / "event_token"


def _check_token_location(tp: Path, p: dict):
    for root in A.arm_readable_roots(p):
        if A._inside(tp, root):
            raise Rejected("token file %s is inside arm-readable root %s" % (tp, root))


def init_token(p: dict | None = None) -> Path:
    """Create the token once (harness setup). Never overwrites: a new token would orphan every signed line."""
    p = p or A.paths()
    tp = token_path(p)
    _check_token_location(tp, p)
    if tp.exists():
        return tp
    tp.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(tp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(secrets.token_hex(32))
    return tp


def _read_token(p: dict) -> str:
    tp = token_path(p)
    _check_token_location(tp, p)
    try:
        tok = tp.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise Rejected("no harness token (%s): %s" % (tp, e))
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
    if ev == "build_end" and not (rec.get("task") and d.get("builder")):
        raise Rejected("build_end needs task and detail.builder")
    if ev == "test_start" and not (rec.get("task") and d.get("tester")):
        raise Rejected("test_start needs task and detail.tester")
    if ev == "test_end" and not (rec.get("task") and d.get("tester")):
        raise Rejected("test_end needs task and detail.tester")
    if ev in ("card", "owner_touch") and not isinstance(rec.get("minutes"), (int, float)):
        raise Rejected("%s needs numeric minutes" % ev)
    if ev == "card":
        if not d.get("card_id") or not isinstance(d.get("unblocked", []), list):
            raise Rejected("card needs detail.card_id and a detail.unblocked list")


def _read_lines(f: Path) -> list[str]:
    return [l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()] if f.exists() else []


def verify(p: dict, arm: str, token: str | None = None) -> dict:
    """-> {"accepted": [rec], "rejected": [(lineno, raw)]}. Harness-side: needs the token."""
    v = verify_lines(_read_lines(arm_file(p, arm)), token or _read_token(p), arm)
    return {"accepted": v["accepted"], "rejected": v["rejected"]}


class HarnessWriter:
    """The only write path. Construct with the arena paths; it reads the token itself, so only a process that can
    read the harness token file can build one. `token=` is for selftests that plant a wrong token."""

    def __init__(self, p: dict | None = None, token: str | None = None):
        self.p = p or A.paths()
        if token is None:
            token = _read_token(self.p)
        else:
            _check_token_location(token_path(self.p), self.p)
        self._token = token

    def emit(self, arm: str, event: str, *, lane: str, run_id: str, ts: str | None = None, **fields) -> dict:
        rec = {"ts": ts or now_ts(), "arm": arm, "lane": lane, "run_id": run_id, "event": event}
        rec.update({k: v for k, v in fields.items() if v is not None})
        validate_record(rec)
        f = arm_file(self.p, arm)
        f.parent.mkdir(parents=True, exist_ok=True)
        with open(f, "a+", encoding="utf-8") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            fh.seek(0)
            lines = [l for l in fh.read().splitlines() if l.strip()]
            tail = verify_lines(lines, self._token, arm)
            # forged lines already in the file are tolerated (they stay REJECTED on read; refusing to write would
            # let an agent stop the harness by appending junk); the chain continues from the last accepted line
            if event == "test_start":
                b = _builder_of(tail["accepted"], rec.get("task"))
                if b and b == (rec.get("detail") or {}).get("tester"):
                    rec["rule"] = FLAG_SAME_AGENT
            rec["sig"] = _sign(self._token, tail["prev"], rec)
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush(); os.fsync(fh.fileno())
        return rec


def verify_lines(lines: list[str], token: str, arm: str) -> dict:
    acc, rej, prev, seen = [], [], GENESIS, set()
    for n, raw in enumerate(lines, 1):
        try:
            rec = json.loads(raw)
            sig = rec.get("sig")
            ok = isinstance(sig, str) and hmac.compare_digest(sig, _sign(token, prev, rec)) and rec.get("arm") == arm \
                and sig not in seen
        except (ValueError, AttributeError, TypeError):
            ok = False
        if ok:
            seen.add(sig); prev = sig; acc.append(rec)
        else:
            rej.append((n, raw))
    return {"accepted": acc, "rejected": rej, "prev": prev}


# ---------------------------------------------------------------- analysis (pure functions over accepted records)

def _builder_of(recs: list[dict], task) -> str | None:
    for r in reversed(recs):
        if r["event"] == "build_end" and r.get("task") == task:
            return (r.get("detail") or {}).get("builder")
    return None


def flagged_same_agent(recs: list[dict]) -> list[dict]:
    """test_start records whose tester is the builder of the latest preceding build_end for that task."""
    out = []
    for i, r in enumerate(recs):
        if r["event"] == "test_start":
            b = _builder_of(recs[:i], r.get("task"))
            if b and b == (r.get("detail") or {}).get("tester"):
                out.append(r)
    return out


def untested_builds(recs: list[dict]) -> list[dict]:
    """build_end with no later test_start by a DIFFERENT agent on the same task."""
    out = []
    for i, r in enumerate(recs):
        if r["event"] != "build_end":
            continue
        b = (r.get("detail") or {}).get("builder")
        if not any(x["event"] == "test_start" and x.get("task") == r.get("task")
                   and (x.get("detail") or {}).get("tester") != b for x in recs[i + 1:]):
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
            if x["event"] == "test_start" and x.get("task") == r.get("task") and (x.get("detail") or {}).get("tester") != b:
                out.append((A._epoch(x["ts"]) - A._epoch(r["ts"])) / 60.0)
                break
    return out


def owner_minutes(recs: list[dict]) -> dict:
    cards = [r for r in recs if r["event"] == "card"]
    touch = [r for r in recs if r["event"] == "owner_touch"]
    unblocked = sorted({t for r in cards for t in (r.get("detail") or {}).get("unblocked", [])})
    cm = sum(r["minutes"] for r in cards)
    return {"cards": len(cards), "card_minutes": cm, "touch_minutes": sum(r["minutes"] for r in touch),
            "minutes": cm + sum(r["minutes"] for r in touch), "unblocked_tasks": unblocked}


def output_report(recs: list[dict], points: dict | None = None) -> dict:
    """Accepted output (judge verdict 'accept', default 1 point a task), with and without owner-unblocked tasks."""
    points = points or {}
    acc = {r["task"] for r in recs if r["event"] == "judge" and r.get("verdict") == "accept" and r.get("task")}
    om = owner_minutes(recs)
    un = set(om["unblocked_tasks"])
    pts = lambda ts: sum(points.get(t, 1) for t in ts)
    withall, without = pts(acc), pts(acc - un)
    return {"owner_minutes": om["minutes"], "points_with_unblocked": withall, "points_without_unblocked": without,
            "owner_unblocked_accepted": sorted(acc & un),
            "minutes_per_point_with": (om["minutes"] / withall) if withall else None,
            "minutes_per_point_without": (om["minutes"] / without) if without else None}


def report(p: dict, token: str | None = None) -> dict:
    out = {}
    for f in sorted(p["events"].glob("*.jsonl")):
        arm = f.stem
        if arm == "harness":
            continue
        v = verify(p, arm, token)
        recs = v["accepted"]
        out[arm] = {"accepted": len(recs), "rejected": len(v["rejected"]),
                    "flagged_same_agent": len(flagged_same_agent(recs)), "untested_builds": len(untested_builds(recs)),
                    "latency_min": latency_minutes(recs), **output_report(recs)}
    return out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=("init-token", "report"))
    a = ap.parse_args(argv)
    p = A.paths()
    if a.cmd == "init-token":
        print(init_token(p))
    else:
        print(json.dumps(report(p), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
