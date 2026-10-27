#!/usr/bin/env python3
"""review_identity.py -- WHO reviewed a file, in a form the Arbiter can check (CODE_REVIEW_WIRE_REVIEWER_SEAT).

A code-review clean mark used to carry only the seat whose shard it landed in: the RECORDING seat. The Arbiter read
that as the reviewer, so a BENCH helper recording a GPT review, or a FOUNDRY seat recording its own work, looked the
same. A mark-clean record now carries two things, kept apart:

  recorder  close_evidence.whoami() of the process that ran mark-clean (seat, where the seat came from, sessions)
  reviewer  {"kind": "self"}                       the recorder reviewed it (the default)
            {"kind": "agent", seat, session, agent} another agent reviewed it -- the recorder's word only
            {"kind": "external", "tool": "gpt_consult", "job", "model"}
                                                   a gpt_consult job reviewed it; mark-clean refuses unless the job's
                                                   receipt exists, was answered, and inlined these exact bytes

and `review_mac`, an HMAC under the close_evidence key over (path, sha256, reviewer, recorder), so a block edited or
transplanted by hand reads "unknown" (same key, same threat model as close_evidence lines: it stops hand edits, not a
process that holds the user's key -- gpt_review_isolated_evidence_2026-10-27.md).

gpt_consult writes one receipt per job (`receipts.jsonl`, append-only, mac'd): job id, model, whether it answered,
and the repo-relative path + sha256 of every file it inlined. The job dir is scratch and is deleted; the receipt is
what makes the job id durable.

identity(record, key, find) -> the tuple the Arbiter compares (arbiter_tiers.load_clean_hashes):
  ("unknown", seat, None)       an old record, or a review block that does not verify: never independent
  ("self", seat, bridge_session) recorder reviewed; its seat came from whoami's own sources
  ("asserted", seat, session)   a reviewer the recorder only named (kind agent, or a self with no sure seat)
  ("external", "gpt_consult:<job>", None)  the receipt re-verifies for this exact (path, sha256)
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import close_evidence as ce  # noqa: E402

RECEIPTS_ENV = "RM_CONSULT_RECEIPTS"
#: whoami() seat sources that name a seat the process itself read (mirrors arbiter_tiers.SEAT_SOURCES)
SEAT_SOURCES = ("RIMFLOW_SEAT", "AGENT_SEAT", "session role file")
KINDS = ("unknown", "self", "asserted", "external")


def receipts_path() -> Path:
    v = os.environ.get(RECEIPTS_ENV, "").strip()
    if v:
        return Path(v)
    from rmpaths import rm_path
    return rm_path("consult", "receipts.jsonl")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _mac(body: dict, key: bytes) -> str:
    return hmac.new(key, json.dumps(body, sort_keys=True, default=str).encode(), hashlib.sha256).hexdigest()


def write_receipt(job, model, answered, files, rc=None, key=None):
    """Append one receipt. files: [(repo-relative path or absolute path, bytes inlined)]. Returns the receipt."""
    key = key or ce._key(create=True)
    rec = {"job": str(job), "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "model": model, "rc": rc,
           "answered": bool(answered), "files": [{"path": p, "sha256": sha256_bytes(b)} for p, b in files],
           "who": ce.whoami()}
    rec = json.loads(json.dumps(rec, default=str))
    rec["mac"] = _mac(rec, key)
    p = receipts_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(p), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, (json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    return rec


def find_receipt(job, key=None):
    """The receipt for `job` whose mac verifies, else None (missing file, no such job, damaged line, no key)."""
    try:
        key = key or ce._key()
        lines = receipts_path().read_text(encoding="utf-8").splitlines()
    except (OSError, RuntimeError):
        return None
    hit = None
    for line in lines:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if not isinstance(r, dict) or r.get("job") != job:
            continue
        m = r.get("mac")
        body = {k: v for k, v in r.items() if k != "mac"}
        if isinstance(m, str) and len(m) == 64 and hmac.compare_digest(m.encode("ascii", "replace"),
                                                                         _mac(body, key).encode()):
            hit = r
    return hit


def receipt_covers(receipt, path, sha256) -> bool:
    """The receipt answered and inlined exactly these bytes of `path`."""
    return bool(receipt and receipt.get("answered") and any(
        isinstance(f, dict) and f.get("path") == path and f.get("sha256") == sha256
        for f in receipt.get("files") or []))


def review_mac(path, sha256, reviewer, recorder, key) -> str:
    return _mac({"path": path, "sha256": sha256, "reviewer": reviewer, "recorder": recorder}, key)


def review_block(path, sha256, reviewer, recorder=None, key=None) -> dict:
    """The fields a clean record carries: reviewer, recorder (whoami() when not given), review_mac (absent when no key
    can be had: the record then reads 'unknown')."""
    recorder = ce.whoami() if recorder is None else recorder
    out = json.loads(json.dumps({"reviewer": reviewer, "recorder": recorder}, default=str))
    try:
        key = key or ce._key(create=True)
    except (OSError, RuntimeError):
        return out
    out["review_mac"] = review_mac(path, sha256, out["reviewer"], out["recorder"], key)
    return out


def identity(rec, key=None, find=find_receipt):
    """(kind, who, session) for one clean record; see the module doc. Never raises."""
    seat = rec.get("seat") or "?"
    rv, rd, m = rec.get("reviewer"), rec.get("recorder"), rec.get("review_mac")
    if not isinstance(rv, dict) or not isinstance(rd, dict) or not isinstance(m, str) or key is None:
        return ("unknown", seat, None)
    try:
        good = hmac.compare_digest(m.encode("ascii", "replace"),
                                   review_mac(rec.get("path"), rec.get("sha256"), rv, rd, key).encode())
    except Exception:
        good = False
    if not good:
        return ("unknown", seat, None)
    kind = rv.get("kind")
    if kind == "external" and rv.get("tool") == "gpt_consult" and isinstance(rv.get("job"), str):
        who = "gpt_consult:%s" % rv["job"]
        try:
            ok = receipt_covers(find(rv["job"]), rec.get("path"), rec.get("sha256"))
        except Exception:
            ok = False
        return ("external", who, None) if ok else ("asserted", who, None)
    if kind == "self":
        if rd.get("seat") and rd.get("seat_from") in SEAT_SOURCES:
            return ("self", rd["seat"], rd.get("bridge_session"))
        return ("asserted", rd.get("seat") or rd.get("seat_raw") or seat, rd.get("bridge_session"))
    if kind == "agent":
        return ("asserted", rv.get("seat") or rv.get("agent") or "?", rv.get("session"))
    return ("unknown", seat, None)
