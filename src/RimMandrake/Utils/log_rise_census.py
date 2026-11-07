#!/usr/bin/env python3
"""log_rise_census.py -- which source wrote each big rise of Verse.Log's message count in one session?

    python3 src/RimMandrake/Utils/log_rise_census.py --session ee0fbaa8 --log <archived Player.log> --record <tps dir> [--check]

A scan-to-scan rise of `logMsgs` at or over Verse.Log's 1000-entry queue proves an eviction between two scans
(game_health_check.py, log.errors_lower_bound), but the tps record does not say who wrote the lines and Player.log has
no timestamps. This joins them (LOVIN_LOGSPAM_DIAGNOSE_IN_PLAY_EVICTIONS):

  count -> line   Verse.Log stops at 10000 messages and prints "Reached max messages limit" there, so an epoch that
                  capped is anchored exactly: count c sits (10000 - c) messages back from its cap line. A rise in an
                  epoch that never capped is anchored on the "Loading game from file <save>" line of a game row inside
                  it, or it is UNANCHORED and says so.
  message walk    A line that Unity wrote itself or that continues the message above never bumped the count
                  (NOT_A_MESSAGE). The walk is checked: an epoch begun by a Log.Clear must hold about 10000 messages
                  (session ee0fbaa8: 10027 and 9997). The session's first epoch is not checked, because the cold load's
                  Unity lines precede its first read.
  counterfactual  Each rise is replayed without the SPAM sources: `after` is the rise had those lines not been written.

--check exits 0 when every big rise is explained (spam at MAJORITY or more of its lines, or errors and warnings at
MAJORITY or more of the rise, per the record or per the log's known error lines, since the record reads a queue that
evicts) and no rise that was spam stays at the queue size once the spam is gone;
1 when a rise is unexplained or spam-dominated rises survive; 2 UNMEASURED (a missing input, no big rise found, a cap
line count that disagrees with the record, a message walk that misses its cap, or an unanchored rise it cannot explain).
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

PASS, FAIL, UNMEASURED = 0, 1, 2
QUEUE_MAX = 1000       # Verse.LogMessageQueue.maxMessages (decompiled 1.6, JawaBenchSessionHealth.cs header)
LOG_CAP = 10000        # the count at which Verse.Log stops (JawaBenchTpsTier.cs header: "10,000-message cap")
WALK_TOLERANCE = 0.01  # an epoch begun by a Log.Clear must walk to within 1% of LOG_CAP, or the alignment is not trusted
MAJORITY = 0.5
CAP_LINE = "Reached max messages limit"
LOAD_LINE = "Loading game from file %s "

NOT_A_MESSAGE = re.compile(
    r"^(\s|$|\(Filename|UnityEngine\.|Verse\.|RimWorld\.|System\.|at |\(wrapper|\[Ref |--- End|Rethrow"
    r"|[A-Za-z_][\w`\.<>+]*:[\w<>\.`]+\s*\("
    r"|Unloading |Total: |UnloadTime|\[PhysX\]|Internal: JobTempAlloc|To Debug, run app|Fallback handler|gridId:"
    r"|Possible Matches|Trying to |Allocation of |TLS |d3d11|PlayerConnection|Initialize engine|<RI>|Mono path|Mono config"
    r"|Uploading Crash|WARNING: Shader|Unsupported|ERROR: Shader|Curl error)")

INTIMACY = "Intimacy (LovelyDovey.Sex.WithEuterpe)"
MOODCHAIN = "Mood Chain Reaction (acutus.moodchainreaction)"
SPAM = (INTIMACY, MOODCHAIN)
SAVE_LOAD = "save-load errors"
BEER = "Beer policy errors"
ERROR_SOURCES = (SAVE_LOAD, BEER)     # real errors a rise may be made of; the queue-limited logErr undercounts them
SOURCES = (
    (INTIMACY, re.compile(r"IntimacyGiver|\bdo lovin'|engage in lovin'|doing lovin'|engaging in lovin'"
                          r"|mutually attracted|recently tried to seduce|moved to vacuum")),
    (MOODCHAIN, re.compile(r"^\[MCR\]\[MoodChain\]")),
    (SAVE_LOAD, re.compile(r"^Could not (load reference|resolve)|^Tried loading non-compressible|^Null key while loading"
                           r"|^Failed to find|^Could not find|^Cannot register|^Exception (loading|resolving)")),
    (BEER, re.compile(r"^AllowedToTakeScheduledEver on non-drug")),
)


def source_of(line):
    for name, rx in SOURCES:
        if rx.search(line):
            return name
    return "other: " + re.sub(r"\d+", "#", line.strip())[:48]


def read_rows(record_dir, session):
    """-> (context rows carrying logMsgs, game rows), in record order; a torn last line of a segment is skipped."""
    ctx, games = [], []
    for p in sorted(glob.glob(os.path.join(record_dir, "tps_*%s*.jsonl" % session))):
        with open(p, errors="replace") as f:
            for l in f:
                try:
                    r = json.loads(l)
                except ValueError:
                    continue
                if r.get("kind") == "context" and r.get("logMsgs") is not None:
                    ctx.append(r)
                elif r.get("kind") == "game":
                    games.append(r)
    return ctx, games


def epochs_of(rows):
    """Context rows split at each drop of the count: a Log.Clear began a new epoch."""
    out = []
    for r in rows:
        if out and r["logMsgs"] >= out[-1][-1]["logMsgs"]:
            out[-1].append(r)
        else:
            out.append([r])
    return out


def message_index(lines, lo, hi):
    return [i for i in range(lo, hi) if not NOT_A_MESSAGE.match(lines[i])]


def census(lines, line_ids):
    c = collections.Counter()
    for i in line_ids:
        c[source_of(lines[i])] += 1
    return c


def _align_epochs(lines, epochs):
    """[(epoch, message line ids or None, walk-check problem or None)]; message ids only for an epoch that capped."""
    caps = [i for i, x in enumerate(lines) if x.startswith(CAP_LINE)]
    capped = [i for i, e in enumerate(epochs) if any(r["logMsgs"] >= LOG_CAP for r in e)]
    if len(caps) != len(capped):
        return None, "%d cap lines in the log but %d capped epochs in the record" % (len(caps), len(capped))
    out, cap_at, start = [], dict(zip(capped, caps)), 0
    for i, e in enumerate(epochs):
        if i not in cap_at:
            out.append((e, None, None))
            continue
        idx = message_index(lines, start, cap_at[i])
        problem = None
        if i > 0 and abs(len(idx) - LOG_CAP) > LOG_CAP * WALK_TOLERANCE:
            problem = "the epoch ending at line %d walks to %d messages, not %d" % (cap_at[i] + 1, len(idx), LOG_CAP)
        out.append((e, idx, problem))
        start = cap_at[i] + 1
    return out, None


def _window(idx, a, b):
    """Line ids of the messages between counts a and b, walking back from the epoch's cap line."""
    n = len(idx)
    lo = max(0, n - (LOG_CAP - min(a, LOG_CAP)))
    hi = max(0, n - (LOG_CAP - min(b, LOG_CAP)))
    return idx[lo:hi]


def analyse(lines, ctx, games):
    """-> (rises, problems). A rise: utc, before, after, rise, errors, warnings, census or None, first and last line,
    anchor (cap | load | None), spam lines, top source, verdict, after_spam."""
    epochs = epochs_of(ctx)
    aligned, problem = _align_epochs(lines, epochs)
    if aligned is None:
        return [], [problem]
    problems, rises = [p for _, _, p in aligned if p], []
    search_from = 0
    for e, idx, _ in aligned:
        for a, b in zip(e, e[1:]):
            d = b["logMsgs"] - a["logMsgs"]
            if d < QUEUE_MAX:
                continue
            err = (b.get("logErr") or 0) - (a.get("logErr") or 0)
            warn = (b.get("logWarn") or 0) - (a.get("logWarn") or 0)
            win, anchor = None, None
            if idx is not None:
                win, anchor = _window(idx, a["logMsgs"], b["logMsgs"]), "cap"
            else:
                g = next((g for g in games if a["utc"] < g["utc"] <= b["utc"] and g.get("save")), None)
                at = None
                if g:
                    needle = LOAD_LINE % g["save"]
                    at = next((i for i in range(search_from, len(lines)) if lines[i].startswith(needle)), None)
                if at is not None:
                    win, anchor = message_index(lines, at, len(lines))[:d], "load"
                    search_from = at + 1
            r = {"utc": b["utc"], "before": a["logMsgs"], "after": b["logMsgs"], "rise": d, "errors": err,
                 "warnings": warn, "anchor": anchor, "census": None, "first": None, "last": None, "spam": 0}
            if win:
                c = census(lines, win)
                r.update(census=c, first=win[0] + 1, last=win[-1] + 1, spam=sum(c[s] for s in SPAM))
            r["after_spam"] = d - r["spam"]
            r["verdict"] = verdict(r)
            rises.append(r)
    return rises, problems


def verdict(r):
    """SPAM | ERRORS | UNEXPLAINED | UNANCHORED: errors and warnings are the record's own numbers, so an unanchored rise
    they explain is still explained; a spam verdict needs the log window."""
    if r["census"] and r["spam"] >= MAJORITY * sum(r["census"].values()):
        return "SPAM"
    logged = sum(r["census"][s] for s in ERROR_SOURCES) if r["census"] else 0
    if max(r["errors"] + r["warnings"], logged) >= MAJORITY * r["rise"]:
        return "ERRORS"
    return "UNEXPLAINED" if r["census"] else "UNANCHORED"


def judge(rises, problems):
    if problems:
        return UNMEASURED, ["UNMEASURED: %s" % p for p in problems]
    if not rises:
        return UNMEASURED, ["UNMEASURED: no scan-to-scan rise at or over %d in this session" % QUEUE_MAX]
    out = []
    for r in rises:
        if r["verdict"] == "UNEXPLAINED":
            out.append("FAIL rise %d at %s is explained by no source and no error count" % (r["rise"], r["utc"]))
        elif r["verdict"] == "UNANCHORED":
            out.append("UNMEASURED: rise %d at %s has no line anchor and the record's errors do not explain it"
                       % (r["rise"], r["utc"]))
        elif r["verdict"] == "SPAM" and r["after_spam"] >= QUEUE_MAX:
            out.append("FAIL rise %d at %s stays at %d without the spam" % (r["rise"], r["utc"], r["after_spam"]))
    if any(x.startswith("FAIL") for x in out):
        return FAIL, out
    return (UNMEASURED if out else PASS), out


def table(rises):
    out = []
    for r in rises:
        out.append("%s  %5d -> %5d  rise %5d  new errors %4d  new warnings %4d  anchor %-4s  %-11s  without spam %5d" % (
            r["utc"][11:19], r["before"], r["after"], r["rise"], r["errors"], r["warnings"], r["anchor"] or "none",
            r["verdict"], r["after_spam"]))
        if r["census"]:
            tot = sum(r["census"].values())
            out.append("    lines %d-%d" % (r["first"], r["last"]))
            for k, v in r["census"].most_common(3):
                out.append("    %5d %5.1f%%  %s" % (v, 100.0 * v / tot, k))
    return out


def totals(lines):
    """The session's plain census, so a source that wrote few lines in big rises but many overall is still seen."""
    c = census(lines, range(len(lines)))
    return ["whole log, %d lines: %s %d, %s %d" % (len(lines), INTIMACY, c[INTIMACY], MOODCHAIN, c[MOODCHAIN])]


def replay(lines, ctx):
    """Each capped epoch without the spam: would Verse.Log have stopped at all?"""
    aligned, _ = _align_epochs(lines, epochs_of(ctx))
    out = []
    for e, idx, _ in aligned or []:
        if idx is None:
            continue
        win = _window(idx, e[0]["logMsgs"], LOG_CAP)
        c = census(lines, win)
        spam = sum(c[s] for s in SPAM)
        out.append("epoch from %s (count %d) capped at %d; without the spam it reaches %d" % (
            e[0]["utc"][11:19], e[0]["logMsgs"], LOG_CAP, e[0]["logMsgs"] + len(win) - spam))
    return out


def run(log_path, record_dir, session):
    """-> (code, lines). Never raises on a missing input: that is UNMEASURED."""
    if not os.path.isfile(log_path):
        return UNMEASURED, ["UNMEASURED: no archived log at %s" % log_path]
    ctx, games = read_rows(record_dir, session)
    if not ctx:
        return UNMEASURED, ["UNMEASURED: no context rows with logMsgs for session %s under %s" % (session, record_dir)]
    with open(log_path, errors="replace", newline="\n") as f:
        lines = [x.rstrip("\r") for x in f.read().split("\n")]
    rises, problems = analyse(lines, ctx, games)
    code, verdicts = judge(rises, problems)
    head = "VERDICT %s" % {PASS: "PASS", FAIL: "FAIL", UNMEASURED: "UNMEASURED"}[code]
    return code, table(rises) + totals(lines) + replay(lines, ctx) + verdicts + [head]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--session", required=True, help="session id or a unique prefix of it")
    ap.add_argument("--log", required=True, help="the session's archived Player.log")
    ap.add_argument("--record", required=True, help="directory holding its tps_*.jsonl segments")
    ap.add_argument("--check", action="store_true", help="exit with the verdict instead of 0")
    a = ap.parse_args(argv)
    code, lines = run(a.log, a.record, a.session)
    print("\n".join(lines))
    return code if a.check else 0


if __name__ == "__main__":
    sys.exit(main())
