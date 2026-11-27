#!/usr/bin/env python3
"""Live per-family collector seconds of the sense pass over 7 days, from each ops_watch series record's own
`collector_s`, for metronome_profile.md. Run on Archmagi:
    ssh mandrake@archmagi-wsl DAYS=7 python3 - < design/specs/2026-11-26-slow-actions/metronome_families.py
Prints one row per family; writes nothing."""
import glob, json, os, statistics as S, time
DAYS = int(os.environ.get("DAYS", "7"))   # DAYS=4: only since sense ran apart (2026-11-22 10:27 PM)
since = time.time() - DAYS * 86400
rows = []
for p in sorted(glob.glob("/mnt/d/ClaudeWork/rimmandrake/ops_watch/series/*.jsonl")):
    xs = []
    with open(p, "rb") as f:
        for ln in f:
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            t, c = r.get("t"), r.get("collector_s")
            if isinstance(t, (int, float)) and t >= since and isinstance(c, (int, float)):
                xs.append(c)
    if xs:
        xs.sort()
        rows.append((sum(xs), os.path.basename(p)[:-6], len(xs), S.median(xs), xs[int(.9 * len(xs))], xs[-1]))
tot = sum(r[0] for r in rows)
print("family | records | median / p90 / max s | total h | share")
for s, fam, n, med, p90, mx in sorted(rows, reverse=True):
    print("%s | %d | %.2f / %.2f / %.1f | %.2f | %.0f%%" % (fam, n, med, p90, mx, s / 3600, 100 * s / tot))
print("all collectors: %.2f h" % (tot / 3600))
