#!/usr/bin/env python3
"""Read-only: over session transcripts, how many characters each tool's results put into context, and how much
of that sits in results over 20,000 characters.   what_fills_context.py <since_epoch> <glob> [...]
Exit 0 measured, 3 could not look (no transcript with a tool result)."""
import glob, json, os, sys
from collections import Counter


def size(c):
    if isinstance(c, str):
        return len(c)
    if isinstance(c, list):
        return sum(len(x.get("text", "")) if isinstance(x, dict) and x.get("type") == "text" else 0 for x in c)
    return 0


def main(a):
    since = float(a[1])
    paths = sorted({p for g in a[2:] for p in glob.glob(os.path.expanduser(g)) if os.path.getmtime(p) >= since})
    by, n, big, first_user = Counter(), Counter(), Counter(), 0
    for p in paths:
        names = {}
        for line in open(p, errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("isSidechain"):
                continue
            c = (d.get("message") or {}).get("content")
            if not isinstance(c, list):
                continue
            for b in c:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    names[b.get("id")] = b.get("name")
                elif b.get("type") == "tool_result":
                    k = names.get(b.get("tool_use_id"), "?")
                    s = size(b.get("content"))
                    by[k] += s
                    n[k] += 1
                    if s > 20000:
                        big[k] += s
    tot = sum(by.values())
    if not tot:
        print("VERDICT could-not-look: %d files, no tool result found" % len(paths))
        return 3
    for k, v in by.most_common(8):
        print("%-10s results %6d  chars %6.1fM  %4.1f%%  in results over 20k chars: %4.1f%% of this tool's"
              % (k, n[k], v / 1e6, 100 * v / tot, 100 * big[k] / v if v else 0))
    print("VERDICT measured: %d files, %.1fM tool-result characters, %.1f%% of them in results over 20k characters"
          % (len(paths), tot / 1e6, 100 * sum(big.values()) / tot))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
