#!/usr/bin/env python3
"""relentless_account.py — did the account kill this run, rather than the item? (RELENTLESS_STRIKES_FIX_EMPTY_ACCOUNT_BLAMED)

A run that ended with no receipt counted as worker_lost, a strike toward same_failure_limit, so an account change-over or
an empty account could flip an innocent item's approach. Two signs clear it; neither charges the item a strike:

  change_over    `claude-account use` closes every Claude process on the machine and logs op=use with changed=true once
                 it is done. A run started before that event and found dead after it was killed by it. Measured: the event
                 of 2026-11-02T01:37:52Z, then two worker_lost at 01:40:23Z with empty .json and .err. A run launched in
                 the switch's own minute reads the same if it later dies: one death forgiven, which costs nothing.
  account_error  the run's newest transcript ends on an API error of the account's own (rate_limit, authentication_failed),
                 or its result object says so. server_error is not one: that is the service, and it is rare enough to strike.

Nothing here names an account. Unreadable sources read as no sign: the death strikes, as it did before this module.
"""
import datetime
import glob
import json
import os
import re

import circling

ACCOUNT_LOG = "~/.claude-accounts/log.jsonl"
ACCOUNT_ERRORS = ("rate_limit", "authentication_failed")
# the words of role_launch.AUTH_RX's family and of the limit messages measured in transcripts, read only on is_error
RESULT_RX = re.compile(r"hit your .{0,40}limit|usage limit|failed to authenticate|oauth session expired|login expired|"
                       r"not logged in|please run /login", re.I)
TAIL = 1 << 17


def _epoch(ts):
    try:
        return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except (AttributeError, ValueError):
        return None


def _tail_records(path, size=TAIL):
    """-> the JSON records in the last `size` bytes of a jsonl; a torn first or last line is skipped."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        f.seek(max(0, end - size))
        lines = f.read().decode("utf-8", "replace").splitlines()
    if end > size:
        lines = lines[1:]
    out = []
    for ln in lines:
        try:
            rec = json.loads(ln)
        except ValueError:
            continue
        if isinstance(rec, dict):
            out.append(rec)
    return out


def change_over(since, path=None):
    """-> why, when the account log holds a real switch after `since`, else None."""
    try:
        recs = _tail_records(os.path.expanduser(path or ACCOUNT_LOG))
    except OSError:
        return None
    for rec in reversed(recs):
        if rec.get("op") == "use" and rec.get("changed") is True:
            at = _epoch(rec.get("ts"))
            if at is not None and at > since:
                return "account change-over at %s closed every Claude process" % rec["ts"]
    return None


def transcript_error(paths):
    """-> the error the newest of `paths` ends on, when it is the account's own, else None. Only the last main-thread turn
    counts: an error the run went on past is not what ended it."""
    try:
        newest = max(paths, key=os.path.getmtime)
        recs = _tail_records(newest)
    except (OSError, ValueError):       # ValueError: no paths
        return None
    last = None
    for rec in recs:
        if rec.get("type") in ("user", "assistant") and not rec.get("isSidechain"):
            last = rec
    if last and last.get("type") == "assistant" and last.get("isApiErrorMessage") and last.get("error") in ACCOUNT_ERRORS:
        return last["error"]
    return None


def result_error(out):
    """-> the words of a result object that says the account stopped the run, else None."""
    try:
        with open(out, encoding="utf-8", errors="replace") as f:
            rec = json.load(f)
    except (OSError, TypeError, ValueError):
        return None
    text = str(rec.get("result") or "") if isinstance(rec, dict) and rec.get("is_error") is True else ""
    return text[:200] if RESULT_RX.search(text) else None


def box_transcripts(box, since):
    """-> a walled run's transcripts: its ~/.claude/projects is bound from <box>/projects (relentless_wall.props)."""
    out = []
    for path in glob.glob(os.path.join(glob.escape(box), "projects", "*", "*.jsonl")):
        try:
            if os.path.getmtime(path) >= since:
                out.append(path)
        except OSError:
            continue
    return out


def loss(run, clone, since, log=None, box=None):
    """-> {"kind", "why"} when the account ended this dead run, else None. Reads files only, and only for a dead run."""
    run = run or {}
    start = run.get("at") if run.get("at") is not None else since
    if start is None:
        return None
    why = change_over(start, log)
    if why:
        return {"kind": "change_over", "why": why}
    paths = box_transcripts(box, start) if box else circling.transcript_paths(clone, start) if clone else []
    err = transcript_error(paths)
    point = resume_point(paths) if err else None
    if not err:
        err = result_error(run.get("out"))
        point = result_point(run.get("out")) if err else None
    if not err:
        return None
    out = {"kind": "account_error", "why": "%s: %s" % (ACCOUNT_MARK, err)}
    if point:
        out["session"] = point      # it did real work before the cut: resumed, not started over
    return out


# RELENTLESS_RESUME_BUILD_ACCOUNT_LOST_RUNS: a run the account cut after real work is resumed (`claude -p --resume`), so
# its context is not thrown away; one that died before any is a plain requeue, as there is nothing to resume.
ACCOUNT_MARK = "the run ended on the account's own error"
SESSION_RX = re.compile(r"^[0-9a-fA-F-]{8,64}$")


def _worked(rec):
    """An assistant turn that is not the error itself and wrote something: real usage."""
    m = rec.get("message") if isinstance(rec.get("message"), dict) else {}
    u = m.get("usage") if isinstance(m.get("usage"), dict) else {}
    out = u.get("output_tokens")
    return rec.get("type") == "assistant" and not rec.get("isApiErrorMessage") and type(out) is int and out > 0


def resume_point(paths):
    """-> the session id of the newest of `paths` (the transcript that ended on the error), when it holds real work."""
    try:
        newest = max(paths, key=os.path.getmtime)
    except (OSError, ValueError):
        return None
    sid = os.path.splitext(os.path.basename(newest))[0]
    if not SESSION_RX.match(sid):
        return None
    try:
        with open(newest, encoding="utf-8", errors="replace") as f:
            for ln in f:
                if '"usage"' not in ln:
                    continue
                try:
                    rec = json.loads(ln)
                except ValueError:
                    continue
                if isinstance(rec, dict) and not rec.get("isSidechain") and _worked(rec):
                    return sid
    except OSError:
        return None
    return None


def result_point(out):
    """-> the session id of an error result object that still records real output, else None."""
    try:
        with open(out, encoding="utf-8", errors="replace") as f:
            rec = json.load(f)
    except (OSError, TypeError, ValueError):
        return None
    if not isinstance(rec, dict):
        return None
    sid, u = rec.get("session_id"), rec.get("usage") if isinstance(rec.get("usage"), dict) else {}
    n = u.get("output_tokens")
    return sid if isinstance(sid, str) and SESSION_RX.match(sid) and type(n) is int and n > 0 else None


def breaker_on_account(br):
    """True when an open launch breaker was opened by the account's own error (account_lost's launch_failed)."""
    return ACCOUNT_MARK in str((br or {}).get("why") or "")
