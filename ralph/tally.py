#!/usr/bin/env python3
"""tally.py <logs dir> [--per-pass]: weighted tokens over the Ralph loop's pass logs.
Weighted = input + output + cache writes + cache reads / 10. A pass still running has no result line yet, so its
assistant messages are summed, last usage per message id."""
import glob
import json
import os
import sys


def weight(u):
    return (u.get("input_tokens", 0) + u.get("output_tokens", 0) + u.get("cache_creation_input_tokens", 0)
            + u.get("cache_read_input_tokens", 0) // 10)


def one(path):
    per_msg, result = {}, None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") == "result" and d.get("usage"):
                result = weight(d["usage"])
            elif d.get("type") == "assistant":
                m = d.get("message") or {}
                if m.get("id") and m.get("usage"):
                    per_msg[m["id"]] = weight(m["usage"])
    return max(result or 0, sum(per_msg.values()))


def main():
    files = sorted(glob.glob(os.path.join(sys.argv[1], "pass_*.jsonl")))
    counts = [(os.path.basename(p), one(p)) for p in files]
    if "--per-pass" in sys.argv:
        for name, n in counts:
            print(name, n)
    print(sum(n for _, n in counts))


if __name__ == "__main__":
    main()
