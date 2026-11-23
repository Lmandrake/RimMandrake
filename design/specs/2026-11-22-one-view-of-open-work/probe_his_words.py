#!/usr/bin/env python3
"""probe_his_words.py: a one-time probe. Which messages that the owner typed into the Conductor window have a home
in the ledger?

A probe for design/specs/2026-11-22-one-view-of-open-work/proposal.md, not pipeline machinery. No model call.

Inputs:
  - the Conductor window's transcripts, ~/.claude/projects/-home-mandrake-rm-bench/*.jsonl (Archmagi only);
  - every ledger shard, infrastructure/state/ledger/events/*.jsonl.

A typed message is a `user` entry that is not a sidechain, not meta, holds text (not a tool result), and is not
machine text (a task notification, a seat-restart or wake prompt, a steward prompt). Card answers are tool results,
so they are not typed messages here; card_capture.py records them.

Homes, from strongest to weakest:
  QUOTED   - a ledger event's ownerSaid field holds the message's words: word 5-gram cover >= 0.5; or a quote of
             5+ words lies wholly inside the message (the operative part was quoted); or, for a message under five
             words, the whole normalised message;
  ECHOED   - some ledger field (text, why, title, byCard, ownerSaid, reason) holds >= 0.25 of its 5-grams, or
             shares 8 consecutive words with it;
  NO HOME  - neither.
Only events from one hour before the message to 72 hours after it count.

Output: a JSON summary on stdout; with --rows, one row per message to the given path.
Exit 0 = answered; 2 = could not read a source (named on stderr, no summary written).
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timedelta

TRANSCRIPTS = os.path.expanduser("~/.claude/projects/-home-mandrake-rm-bench/")
LEDGER = "infrastructure/state/ledger/events/"
MACHINE = re.compile(r"^(wake\.|\[RimFlow|You are a |DETACHED RUN|<task-notification>|<command-|<local-command|"
                     r"Caveat:|# Resume|Resume:|\[Request interrupted)", re.I)
FIELDS = ("ownerSaid", "text", "why", "title", "byCard", "reason")


def ts(s):
    return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")


def norm(s):
    s = re.sub(r"<system-reminder>.*?</system-reminder>", " ", s, flags=re.S)
    s = re.sub(r"\[Image #\d+\]", " ", s)
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    return re.findall(r"[a-z0-9']+", s.lower())


def grams(w, n=5):
    return {tuple(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def messages(since, until):
    out, seen = [], set()
    files = glob.glob(TRANSCRIPTS + "*.jsonl")
    if not files:
        raise OSError("no transcripts under %s" % TRANSCRIPTS)
    for f in files:
        for line in open(f, errors="replace"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") != "user" or e.get("isMeta") or e.get("isSidechain"):
                continue
            t = e.get("timestamp", "")
            if not (since <= t < until):
                continue
            if (e.get("promptSource") or "") == "sdk" or (e.get("entrypoint") or "") == "sdk-cli":
                continue
            c = (e.get("message") or {}).get("content")
            if isinstance(c, list):
                if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
                    continue
                c = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
            if not isinstance(c, str):
                continue
            c = c.strip()
            if not c or MACHINE.match(c):
                continue
            w = norm(c)
            if not w:
                continue
            key = " ".join(w)
            if key in seen:
                continue
            seen.add(key)
            out.append({"ts": t, "session": os.path.basename(f)[:8], "text": c, "words": w})
    return out


def ledger_events(since, until):
    lo, hi = (ts(since) - timedelta(hours=1)).isoformat(), (ts(until) + timedelta(hours=72)).isoformat()
    ev = []
    files = glob.glob(LEDGER + "*.jsonl")
    if not files:
        raise OSError("no ledger shards under %s" % LEDGER)
    for f in files:
        for line in open(f, errors="replace"):
            if '"ts"' not in line:
                continue
            try:
                e = json.loads(line)
            except ValueError:
                continue
            t = e.get("ts", "")
            if lo <= t <= hi:
                ev.append(e)
    return ev


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--until", required=True)
    ap.add_argument("--rows")
    a = ap.parse_args(argv)
    try:
        msgs = messages(a.since, a.until)
        ev = ledger_events(a.since, a.until)
    except OSError as x:
        print("COULD NOT READ: %s" % x, file=sys.stderr)
        return 2
    said, anyf = [], []
    for e in ev:
        t = ts(e["ts"])
        if e.get("ownerSaid"):
            said.append((t, grams(norm(str(e["ownerSaid"]))), " ".join(norm(str(e["ownerSaid"])))))
        blob = " ".join(str(e.get(k, "")) for k in FIELDS)
        anyf.append((t, grams(norm(blob)), " ".join(norm(blob))))
    rows = []
    for m in msgs:
        t = ts(m["ts"])
        lo, hi = t - timedelta(hours=1), t + timedelta(hours=72)
        g, flat, n = grams(m["words"]), " ".join(m["words"]), len(m["words"])

        def cover(pool):
            best = 0.0
            union = set()
            for et, eg, ef in pool:
                if not (lo <= et <= hi):
                    continue
                if n < 5:
                    if flat and re.search(r"(^| )%s( |$)" % re.escape(flat), ef):
                        return 1.0
                    continue
                union |= (g & eg)
            return len(union) / len(g) if g else best
        q, e2 = cover(said), cover(anyf)
        g8 = grams(m["words"], 8)
        inside = any(lo <= et <= hi and len(eg) >= 1 and len(eg & g) >= 0.8 * len(eg) for et, eg, ef in said)
        shared8 = any(lo <= et <= hi and (g8 & grams(ef.split(), 8)) for et, eg, ef in anyf) if g8 else False
        home = "QUOTED" if (q >= 0.5 or inside) else ("ECHOED" if (e2 >= 0.25 or shared8) else "NO HOME")
        rows.append({"ts": m["ts"], "session": m["session"], "words": n, "quoted_cover": round(q, 2),
                     "any_cover": round(e2, 2), "home": home, "text": m["text"][:600]})
    buckets = {}
    for r in rows:
        b = "under 8 words" if r["words"] < 8 else ("8-30 words" if r["words"] <= 30 else "over 30 words")
        buckets.setdefault(b, {"QUOTED": 0, "ECHOED": 0, "NO HOME": 0})[r["home"]] += 1
    summary = {"window": [a.since, a.until], "typed_messages": len(rows), "ledger_events_read": len(ev),
               "ownerSaid_events": len(said),
               "home": {h: sum(1 for r in rows if r["home"] == h) for h in ("QUOTED", "ECHOED", "NO HOME")},
               "by_length": buckets}
    if a.rows:
        json.dump(rows, open(a.rows, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
