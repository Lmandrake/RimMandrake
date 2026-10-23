#!/usr/bin/env python3
"""Sum a subagent transcript's turns and token use: helper_cost.py <task.output|session.jsonl>...
Prints one line per file. Cost ~ turns x context, so cache_read is the number to watch."""
import collections, json, sys


def tally(path):
    t = collections.Counter()
    turns = 0
    for line in open(path, errors="ignore"):
        try:
            msg = json.loads(line).get("message")
        except ValueError:
            continue
        usage = msg.get("usage") if isinstance(msg, dict) else None
        if isinstance(usage, dict):
            turns += 1
            for k in ("output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
                t[k] += usage.get(k, 0) or 0
    return turns, t


for p in sys.argv[1:]:
    n, t = tally(p)
    print(f"{p}: turns={n} out={t['output_tokens']//1000}k cache_read={t['cache_read_input_tokens']//1000000}M "
          f"cache_write={t['cache_creation_input_tokens']//1000000}M")
