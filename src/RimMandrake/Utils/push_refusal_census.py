#!/usr/bin/env python3
"""push_refusal_census.py - how often a push to origin/main is refused or retried, per day and per writer.

WHY (PUSH_REFUSALS_MEASURE_BEFORE_BUYING_GITLAB, owner 2026-11-04: "don't take action on the result, just make sure
I find out"): before anyone argues for a different git host, measure what the current one costs.

SOURCE
    ./publish (publish.py), land.sh and seat_sync keep NO persistent log of their pushes; their output lives only in
    the Claude transcripts that ran them (~/.claude/projects/**/*.jsonl). This pairs every Bash tool_use whose
    command lands work (./publish, publish.py, land.sh, ./sync, seat_sync.py, git push) with its tool_result and
    reads the markers those tools print:
        publish.py  "origin moved (attempt N); rebasing and retrying"   one non-fast-forward rejection each
                    "REFUSED: origin kept moving: ..."                   gave up (its last rejection printed above)
                    "REFUSED: ... stopped on a conflict ..."             rebase conflict
                    "REFUSED: could not take the publish lock ..."       same-clone lock contention
                    "push failed (...); retrying"                         a non-nff push error, retried
                    "PUBLISHED <sha>"                                     landed
        land.sh     "land.sh: origin moved during the push ..."          one rejection each
                    "push rejected N times: origin keeps moving"         gave up (+1 rejection: not echoed)
        git push    "[rejected]" / "non-fast-forward" / "fetch first"    a raw push refused
    Tool calls are deduplicated by tool_use id (a resumed session copies its history into a new file).
    Programs that push without a transcript (the Relentless supervisor's books publish, timers) are not seen
    here; the user journal is read separately by --journal for their refusal markers.

TIME LOST
    A call's duration is tool_result.timestamp - tool_use.timestamp. Time lost by a call with >=1 rejection =
    its duration - the median duration of clean landings (PUBLISHED, no rejection) in the same window, floored
    at 0; a call that gave up loses its whole duration. Writer = the clone family of the session's cwd.

USE
    python3 src/RimMandrake/Utils/push_refusal_census.py --days 7 --out <report.md> [--json <rows.json>]
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import statistics
import subprocess
import sys
from collections import defaultdict

try:
    from zoneinfo import ZoneInfo
    LOCAL = ZoneInfo("America/Los_Angeles")
except Exception:                       # pragma: no cover - zoneinfo is stdlib on 3.9+
    LOCAL = dt.timezone.utc

PUSH_CMD = re.compile(r"(\./publish\b|publish\.py|land\.sh|\./sync\b|seat_sync\.py|\bgit\b[^|;&\n]*\bpush\b)")
SKIP_CMD = re.compile(r"run_selftests|python3?\s+\S*selftest\S*\.py|push_refusal_census")   # RUNNING a test prints the markers on purpose
RM_CWD = re.compile(r"(/rm/|/walled/|RimMandrake)")
MOVED = re.compile(r"^origin moved \(attempt \d+\)", re.M)
LAND_MOVED = re.compile(r"^land\.sh: origin moved during the push", re.M)
LAND_GAVEUP = re.compile(r"^REFUSED: push rejected \d+ times: origin keeps moving", re.M)
KEPT_MOVING = re.compile(r"^REFUSED: origin kept moving", re.M)
# Every refusal is anchored at a line start: a call that greps publish.py's source prints the same words mid-line.
CONFLICT = re.compile(r"^REFUSED: (replaying .* stopped on a conflict|conflict replaying)", re.M)
SUBMISSION = re.compile(r"^REFUSED: .* already holds a submission this one does not contain", re.M)
OVERLAP = re.compile(r"^REFUSED: .*(really overlap|changed a file (with|you have) uncommitted edits)", re.M)
LOCKWAIT = re.compile(r"^REFUSED: could not take the publish lock", re.M)
AUTH = re.compile(r"Permission denied \(publickey\)|Could not read from remote|incorrect old value provided")
NOOP = re.compile(r"^REFUSED: nothing to (publish|land)", re.M)
PUSHFAIL_RETRY = re.compile(r"^push failed( \(.*\); retrying)?$", re.M)   # publish.py prints a bare "push failed" when git said nothing
PUSHFAIL_FINAL = re.compile(r"^REFUSED: push failed", re.M)
RAW_REJECT = re.compile(r"^ ?! \[rejected\].*\((non-fast-forward|fetch first)\)", re.M)
PUBLISHED = re.compile(r"^PUBLISHED [0-9a-f]{7,40}\b", re.M)
REFUSED = re.compile(r"^(REFUSED: |fatal: |error: )", re.M)


def writer_of(cwd, path):
    """-> the clone family that ran the call; '(subagent)' when the transcript is a subagent's."""
    c = cwd or ""
    if "/rm/relentless/clones/" in c:
        w = "relentless worker"
    elif "/walled/" in c:
        w = "relentless checker"
    elif re.search(r"/rm/bench\b", c):
        w = "bench seat clone"
    elif re.search(r"/rm/foundry\b", c):
        w = "foundry clone"
    elif "/rm/scratch" in c or "/rm/pool" in c:
        w = "scratch/pool clone"
    elif "RimMandrake" in c:
        w = "D: mirror/other"
    else:
        m = re.search(r"/rm/([^/]+)", c)
        w = ("rm/" + m.group(1)) if m else "other"
    if "/subagents/" in path:
        w += " (subagent)"
    return w


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(text_of(x.get("text", x.get("content", ""))) if isinstance(x, dict) else str(x)
                         for x in content)
    return ""


def ts_of(s):
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def classify(cmd, out):
    """-> dict of counters for one landing call. Pure: the selftest drives it."""
    moved = len(MOVED.findall(out)) + len(LAND_MOVED.findall(out))
    gaveup = bool(KEPT_MOVING.search(out) or LAND_GAVEUP.search(out))
    raw = len(RAW_REJECT.findall(out)) if not moved and not gaveup else 0   # a bare `git push` refused
    rejections = moved + (1 if LAND_GAVEUP.search(out) else 0) + raw + (1 if SUBMISSION.search(out) else 0)
    if PUBLISHED.search(out):
        outcome = "landed"
    elif gaveup:
        outcome = "gave up (origin kept moving)"
    elif PUSHFAIL_FINAL.search(out):
        outcome = "origin: push error (not non-fast-forward), gave up"
    elif SUBMISSION.search(out):
        outcome = "origin: submit ref already holds another submission"
    elif CONFLICT.search(out):
        outcome = "origin: rebase conflict"
    elif OVERLAP.search(out):
        outcome = "origin: upstream overlaps a dirty file"
    elif raw:
        outcome = "origin: raw git push rejected"
    elif NOOP.search(out):
        outcome = "no-op (nothing to publish)"
    elif REFUSED.search(out) and AUTH.search(out):
        outcome = "auth/transport failure"
    elif LOCKWAIT.search(out):
        outcome = "local: publish lock busy"
    elif REFUSED.search(out):
        outcome = "local refusal (paths, message, state)"
    else:
        outcome = "no verdict"
    m = re.search(r"^(?:REFUSED: |fatal: |error: | ?! \[rejected\]).*", out, re.M)
    return {"rejections": rejections, "retried_errors": len(PUSHFAIL_RETRY.findall(out)), "outcome": outcome,
            "gaveup": gaveup, "why": m.group(0)[:200] if m else ""}


def scan(files, since, until):
    uses, results, here = {}, {}, {}
    for path in files:
        try:
            fh = open(path, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            cwd = None
            for line in fh:
                if '"tool_use' not in line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                cwd = e.get("cwd") or cwd
                msg = e.get("message") or {}
                content = msg.get("content")
                if not isinstance(content, list):
                    continue
                t = ts_of(e.get("timestamp", ""))
                for c in content:
                    if not isinstance(c, dict):
                        continue
                    if c.get("type") == "tool_use" and c.get("name") == "Bash":
                        cmd = (c.get("input") or {}).get("command", "")
                        if PUSH_CMD.search(cmd) and not SKIP_CMD.search(cmd) and c.get("id") not in uses:
                            uses[c["id"]] = (cmd, t, cwd, path)
                    elif c.get("type") == "tool_result":
                        r = (text_of(c.get("content")), t)
                        results.setdefault(c.get("tool_use_id"), r)
                        here.setdefault((path, c.get("tool_use_id")), r)    # pair a use with ITS file's result
    rows = []
    for uid, (cmd, t0, cwd, path) in uses.items():
        if uid not in results or t0 is None or not (since <= t0 < until):
            continue
        if not RM_CWD.search((cwd or "") + " " + cmd):
            continue
        out, t1 = here.get((path, uid)) or results[uid]
        r = classify(cmd, out)
        if r["outcome"] == "no verdict" and not r["rejections"]:
            continue                                        # a read (git log, sync --status ...), not a landing
        r.update(id=uid, ts=t0.isoformat(), day=t0.astimezone(LOCAL).date().isoformat(),
                 writer=writer_of(cwd, path), dur=(t1 - t0).total_seconds() if t1 and t1 >= t0 else None)
        rows.append(r)
    return rows


def journal_rows(since):
    """Refusal markers from programs that push without a transcript (the user journal)."""
    try:
        out = subprocess.run(["journalctl", "--user", "--since", since.astimezone(LOCAL).strftime("%Y-%m-%d %H:%M"),
                              "--no-pager", "-o", "short-iso"], capture_output=True, text=True, timeout=300).stdout
    except Exception as e:
        return None, "UNMEASURED: journalctl: %s" % e
    hits = [l for l in out.splitlines() if "systemd[" not in l and
            re.search(r"origin moved \(attempt|origin kept moving|push rejected \d+ times|\[rejected\]|"
                      r"non-fast-forward|push failed", l)]
    return hits, None


def lost(rows):
    clean = [r["dur"] for r in rows if r["outcome"] == "landed" and not r["rejections"]
             and not r["retried_errors"] and r["dur"] is not None]
    base = statistics.median(clean) if clean else 0.0
    for r in rows:
        if r["dur"] is None:
            r["lost"] = 0.0
        elif r["gaveup"]:
            r["lost"] = r["dur"]
        elif r["rejections"] or r["retried_errors"] or r["outcome"].startswith("origin: push error"):
            r["lost"] = max(0.0, r["dur"] - base)
        else:
            r["lost"] = 0.0
    return base, len(clean)


def table(rows, key):
    agg = defaultdict(lambda: defaultdict(float))
    for r in rows:
        a = agg[r[key]]
        a["calls"] += 1
        a["landed"] += r["outcome"] == "landed"
        a["retried"] += r["rejections"] > 0
        a["rejections"] += r["rejections"]
        a["errcalls"] += r["retried_errors"] > 0
        a["errs"] += r["retried_errors"]
        a["gaveup"] += r["gaveup"]
        a["other_refused"] += r["outcome"].startswith("origin:")
        a["lost"] += r["lost"]
    lines = ["| %s | landing calls | landed | calls with ≥1 rejection | non-fast-forward rejections | calls "
             "retrying a push error | push errors retried (not non-ff) | gave up "
             "(origin kept moving) | other origin refusals (conflict, overlap, raw push) | time lost (min) |" % key, "|" + "---|" * 10]
    tot = defaultdict(float)
    for k in sorted(agg):
        a = agg[k]
        for f in a:
            tot[f] += a[f]
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d | %.1f |" % (
            k, a["calls"], a["landed"], a["retried"], a["rejections"], a["errcalls"], a["errs"], a["gaveup"],
            a["other_refused"], a["lost"] / 60))
    lines.append("| **total** | %d | %d | %d | %d | %d | %d | %d | %d | %.1f |" % (
        tot["calls"], tot["landed"], tot["retried"], tot["rejections"], tot["errcalls"], tot["errs"], tot["gaveup"],
        tot["other_refused"], tot["lost"] / 60))
    return lines


def report(rows, since, until, nfiles, base, nclean, jhits, jerr):
    days = (until - since).total_seconds() / 86400 or 1
    since, until = since.astimezone(dt.timezone.utc), until.astimezone(dt.timezone.utc)
    retried = [r for r in rows if r["rejections"]]
    L = ["# Push refusals to origin/main, %s → %s (%g days)" % (since.strftime("%Y-%m-%d %H:%MZ"),
                                                                 until.strftime("%Y-%m-%d %H:%MZ"), days),
         "",
         "Item `PUSH_REFUSALS_MEASURE_BEFORE_BUYING_GITLAB` — measurement only, as asked: no design, no filing, "
         "no change made on the result.",
         "",
         "**Source.** `./publish`, `land.sh` and `./sync` keep no log of their own pushes, so this reads their "
         "output where it survives: %d Claude transcripts touched in the window (`~/.claude/projects`), each "
         "landing call paired with its result and deduplicated by tool-call id. Made by "
         "`src/RimMandrake/Utils/push_refusal_census.py`." % nfiles,
         "",
         "## Time lost",
         "",
         "Median clean landing (PUBLISHED, no rejection, n=%d): **%.1f s**. A call with rejections loses its "
         "duration minus that median; a call that gave up loses all of it." % (nclean, base),
         "",
         "- landing calls: **%d**; with ≥1 non-fast-forward rejection: **%d** (%.1f%%)" % (
             len(rows), len(retried), 100.0 * len(retried) / len(rows) if rows else 0),
         "- rejections in total: **%d**; gave up after the retry budget: **%d**" % (
             sum(r["rejections"] for r in rows), sum(r["gaveup"] for r in rows)),
         "- calls that retried a push ERROR that was not a non-fast-forward: **%d** (%d retries; %d of them "
         "landed in the end). `publish.py` prints only git's last line (`error: failed to push some refs`), so "
         "the cause is not in the record: a local pre-push guard (`infrastructure/githooks/pre-push`) refusing "
         "and a GitHub-side error look the same." % (
             sum(1 for r in rows if r["retried_errors"]), sum(r["retried_errors"] for r in rows),
             sum(1 for r in rows if r["retried_errors"] and r["outcome"] == "landed")),
         "- refused because origin moved under the work: rebase conflict **%d**, upstream overlaps a dirty file "
         "**%d** (each needs the writer to act again; not counted in time lost)" % (
             sum(r["outcome"] == "origin: rebase conflict" for r in rows),
             sum(r["outcome"] == "origin: upstream overlaps a dirty file" for r in rows)),
         "- time lost inside landing calls to retries: **%.1f min** over %g days (%.1f min/day): %.1f min on "
         "non-fast-forward rejections, %.1f min on push-error retries" % (
             sum(r["lost"] for r in rows) / 60, days, sum(r["lost"] for r in rows) / 60 / days,
             sum(r["lost"] for r in rows if r["rejections"] and not r["retried_errors"]) / 60,
             sum(r["lost"] for r in rows if r["retried_errors"] or r["outcome"].startswith("origin: push error")) / 60),
         "- time in all landing calls: %.1f min" % (sum(r["dur"] or 0 for r in rows) / 60),
         "",
         "## Per day", "", "(Pacific calendar days)", ""]
    L += table(rows, "day")
    L += ["", "## Per writer", "", "(clone family of the session's working directory; subagent transcripts "
          "marked)", ""]
    L += table(rows, "writer")
    oc = defaultdict(int)
    for r in rows:
        oc[r["outcome"]] += 1
    L += ["", "## Outcomes", ""] + ["- %s: %d" % (k, v) for k, v in sorted(oc.items(), key=lambda x: -x[1])]
    L += ["", "## Pushers without a transcript (user journal)", ""]
    if jerr:
        L.append(jerr)
    else:
        L.append("%d refusal/failure lines in the window (unit start lines excluded):" % len(jhits))
        L += ["- `%s`" % h[:200].replace("`", "'") for h in jhits[:20]]
    L += ["", "## Blind spots", "",
          "- The Relentless supervisor's own books `./publish` and other timer pushes log no retry lines; only "
          "their failures reach the journal (above).",
          "- A transcript deleted or not yet flushed is not counted; a landing run through a wrapper whose "
          "command line names none of the landing tools is not seen.",
          "- A result Claude saved to a file (output too large) carries no markers in the transcript: such a call "
          "reads 'no verdict' and is dropped, an undercount.",
          "- The clean-landing median is taken over every landing command (a build chained before ./publish, "
          "./sync) and a retried call's duration includes publish.py's back-off sleeps: time lost is an "
          "approximation, likely an understatement.",
          "- Time lost counts the waiting inside the landing call only, not an agent's later re-run by hand "
          "(those appear as separate calls)."]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--days", type=float, default=7)
    ap.add_argument("--until", help="ISO time (default now)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--json")
    ap.add_argument("--no-journal", action="store_true")
    a = ap.parse_args(argv)
    until = ts_of(a.until) if a.until else dt.datetime.now(dt.timezone.utc)
    since = until - dt.timedelta(days=a.days)
    files = [p for p in glob.glob(os.path.join(a.root, "**", "*.jsonl"), recursive=True)
             if os.path.getmtime(p) >= since.timestamp()]
    if not files:
        print("UNMEASURED: no transcripts under %s since %s" % (a.root, since), file=sys.stderr)
        return 2
    rows = scan(files, since, until)
    base, nclean = lost(rows)
    jhits, jerr = ([], "skipped (--no-journal)") if a.no_journal else journal_rows(since)
    with open(a.out, "w") as f:
        f.write(report(rows, since, until, len(files), base, nclean, jhits or [], jerr))
    if a.json:
        with open(a.json, "w") as f:
            json.dump(rows, f, indent=0)
    print("%d landing calls, %d with rejections, %d rejections; report %s" % (
        len(rows), sum(1 for r in rows if r["rejections"]), sum(r["rejections"] for r in rows), a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
