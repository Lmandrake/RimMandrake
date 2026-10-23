#!/usr/bin/env python3
"""Sum a subagent transcript's turns and token use: helper_cost.py <task.output|session.jsonl>...
Transcripts repeat one API message as several streamed records, so usage is taken once per message id (the
largest record). Counts messages, not true turns; excludes plain input and external judge calls.
Cost ~ messages x context, so cache_read is the number to watch."""
import collections, json, sys

KEYS = ("output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


def tally(path):
    best, anon = {}, []
    for line in open(path, errors="ignore"):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        msg = rec.get("message") if isinstance(rec, dict) else None
        usage = msg.get("usage") if isinstance(msg, dict) else None
        if not isinstance(usage, dict):
            continue
        row = {k: usage.get(k, 0) or 0 for k in KEYS}
        mid = msg.get("id")
        if not mid:
            anon.append(row)
        elif mid not in best or row["output_tokens"] >= best[mid]["output_tokens"]:
            best[mid] = row
    rows = list(best.values()) + anon
    t = collections.Counter()
    for r in rows:
        t.update(r)
    return len(rows), t


for p in sys.argv[1:]:
    n, t = tally(p)
    print(f"{p}: messages={n} out={t['output_tokens']//1000}k cache_read={t['cache_read_input_tokens']//1000000}M "
          f"cache_write={t['cache_creation_input_tokens']//1000000}M")
