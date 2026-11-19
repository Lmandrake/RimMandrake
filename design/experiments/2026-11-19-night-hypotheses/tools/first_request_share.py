#!/usr/bin/env python3
"""Acceptance check for RIMMANDRAKE_SHARE_HELPER_START_ONE_STATUS_LINE_REWRITES_IT. Read-only.

Two helper sessions started minutes apart on the same model: does the SECOND one read its starting context from the
prompt cache? Reads the first API request's usage of each session transcript (~/.claude/projects/<dir>/<id>.jsonl).

    first_request_share.py <first.jsonl> <second.jsonl> [--min-share 0.9]

Exit 0  PASS: the second session's first request read at least min-share of its prompt from the cache.
Exit 1  FAIL: it read less (it wrote its start new).
Exit 3  COULD NOT LOOK: a transcript is missing or unreadable.
Exit 4  EMPTY: a transcript holds no assistant turn with usage (not a pass).
Prints one VERDICT line last.
"""
import json, sys


def first_usage(path):
    for line in open(path):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") == "assistant":
            u = (d.get("message") or {}).get("usage")
            if u:
                return (d.get("message") or {}).get("model"), u
    return None


def main(a):
    share = 0.9
    if "--min-share" in a:
        i = a.index("--min-share")
        share = float(a[i + 1])
        a = a[:i] + a[i + 2:]
    if len(a) != 2:
        print(__doc__)
        print("VERDICT could-not-look: two transcript paths are needed")
        return 3
    got = []
    for p in a:
        try:
            got.append(first_usage(p))
        except OSError as e:
            print("VERDICT could-not-look: %s: %s" % (p, e))
            return 3
    if not all(got):
        print("VERDICT empty: no assistant turn with usage in %s" % ", ".join(p for p, g in zip(a, got) if not g))
        return 4
    (m1, _), (m2, u) = got
    r = u.get("cache_read_input_tokens") or 0
    w = u.get("cache_creation_input_tokens") or 0
    i = u.get("input_tokens") or 0
    total = r + w + i
    note = "" if m1 == m2 else " (models differ: %s, %s; no share is possible)" % (m1, m2)
    print("second session, first request: read %d, wrote %d, uncached %d; read share %.3f%s" % (r, w, i, r / total, note))
    if r >= share * total:
        print("VERDICT pass: read share %.3f >= %.2f" % (r / total, share))
        return 0
    print("VERDICT fail: read share %.3f < %.2f" % (r / total, share))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
