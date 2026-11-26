#!/usr/bin/env python3
"""helper_start_share.py — do real detached helpers read their start from the prompt cache? Read-only.

The outcome check of RIMMANDRAKE_SHARE_HELPER_START_ONE_STATUS_LINE_REWRITES_IT. It reads the detached run records
(detached_helper.state_dir), takes the NEWEST fresh start (no --resume, this machine) and the start before it on the same
model, at most --window-s earlier (the cache lives an hour), and reads the first API request of the newer one's
transcript: what share of its prompt came from the cache. The measure is design/experiments/2026-11-19-night-hypotheses/
tools/first_request_share.py's, on the pipeline's own launches instead of two named files.

    helper_start_share.py [--min-share 0.7] [--window-s 1800] [--last 40] [--model opus|sonnet|fable|any]

--model (default opus, the model the pipeline launches its helpers on): only starts on that model count, so a pair of
probe launches on another model never stands in for the pipeline's own.

Exit 0  PASS: the newer start read at least min-share of its first request from the cache.
Exit 1  FAIL: it read less (it wrote its start new).
Exit 3  COULD NOT LOOK: the records or a transcript could not be read.
Exit 4  EMPTY: no two fresh starts on one model within the window among the last N records (not a pass).
Prints one VERDICT line last.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rimflow"))


def first_usage(path):
    """-> (model, usage) of the first assistant turn with usage, or None."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") == "assistant" and not d.get("isSidechain"):
                m = d.get("message") or {}
                if m.get("usage"):
                    return m.get("model"), m["usage"]
    return None


def fresh_starts(recs):
    """-> the records of fresh starts on this machine, oldest first: a resume reads its own old transcript, and a run on
    another host has its transcript there."""
    out = [r for r in recs if isinstance(r, dict) and r.get("at") and r.get("model") and r.get("clone")
           and not r.get("resume_session") and not r.get("host")
           and r.get("status") not in ("launching", "launch_failed", "refused")]
    return sorted(out, key=lambda r: r["at"])


def pick_pair(starts, window_s):
    """-> (older, newer): the newest start and the start before it on its model, at most window_s apart; or None."""
    if not starts:
        return None
    new = starts[-1]
    for old in reversed(starts[:-1]):
        if new["at"] - old["at"] > window_s:
            return None
        if old["model"] == new["model"]:
            return old, new
    return None


def transcript(rec, DH):
    """-> the run's session transcript path, or None."""
    sid = rec.get("session") or rec.get("session_id")
    if not sid:
        sid, _ctx, _how = DH.run_session(rec["unit"])
    return DH.find_transcript(sid) if sid else None


def main(argv=None, records=None, DH=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--min-share", type=float, default=0.7)
    ap.add_argument("--window-s", type=float, default=1800)
    ap.add_argument("--last", type=int, default=40, help="read only the newest N records")
    ap.add_argument("--model", default="opus", help="only starts on this model tier count; any: every model")
    a = ap.parse_args(argv)
    if DH is None:
        import detached_helper as DH
    try:
        recs = records if records is not None else DH.all_records()
    except OSError as e:
        print("VERDICT could-not-look: the run records: %s" % e)
        return 3
    if not recs:
        print("VERDICT could-not-look: the run records read empty (a blind instrument, not zero runs)")
        return 3
    starts = [r for r in fresh_starts(recs) if a.model == "any" or r["model"] == a.model][-a.last:]
    pair = pick_pair(starts, a.window_s)
    if not pair:
        print("VERDICT empty: the newest start (%s) has no earlier fresh start on its model within %d s" % (
            starts[-1]["unit"] if starts else "none", a.window_s))
        return 4
    old, new = pair
    t = transcript(new, DH)
    if not t:
        print("VERDICT could-not-look: no transcript for %s" % new["unit"])
        return 3
    try:
        got = first_usage(t)
    except OSError as e:
        print("VERDICT could-not-look: %s: %s" % (t, e))
        return 3
    if not got:
        print("VERDICT empty: %s holds no assistant turn with usage yet" % t)
        return 4
    _model, u = got
    r = u.get("cache_read_input_tokens") or 0
    w = u.get("cache_creation_input_tokens") or 0
    i = u.get("input_tokens") or 0
    share = r / float(r + w + i) if (r + w + i) else 0.0
    print("pair: %s then %s, %d s apart, model %s; shared start: %s, %s" % (
        old["unit"], new["unit"], new["at"] - old["at"], new["model"], bool(old.get("shared_start")),
        bool(new.get("shared_start"))))
    print("newer start, first request: read %d, wrote %d, uncached %d; read share %.3f" % (r, w, i, share))
    if share >= a.min_share:
        print("VERDICT pass: read share %.3f >= %.2f" % (share, a.min_share))
        return 0
    print("VERDICT fail: read share %.3f < %.2f" % (share, a.min_share))
    return 1


if __name__ == "__main__":
    sys.exit(main())
