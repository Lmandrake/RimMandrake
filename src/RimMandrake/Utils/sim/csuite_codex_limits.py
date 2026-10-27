#!/usr/bin/env python3
"""Codex (ChatGPT-auth) rate-limit history from codex rollout files (C-suite evidence, 2026-10-26).

Every codex rollout-*.jsonl records `rate_limits` events: primary (short window) and secondary
(weekly) used_percent, window_minutes, resets_at. This prints, per day: number of readings,
max primary/secondary used %, the distinct secondary reset times seen, and the used % at the
last reading before each secondary reset (idle quota thrown away at the reset).
Dirs: ~/.codex/sessions and the Windows user's .codex/sessions (override: args).
"""
import collections, datetime as dt, glob, json, math, os, sys

DEFAULT_DIRS = [os.path.expanduser("~/.codex/sessions"), "/mnt/c/Users/Mandrake/.codex/sessions"]
DIRS = (sys.argv[1:] if __name__ == "__main__" else []) or DEFAULT_DIRS   # argv only when run as a script, never an importer's


def _num(v):
    """A finite number as float, else None (strings, bools, NaN, ints too big for a float)."""
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return None
    try:
        f = float(v)
    except OverflowError:
        return None
    return f if math.isfinite(f) else None


def readings(dirs=None, newer_than=None):
    """Every rate_limits reading in the rollout files under `dirs`, oldest first, plus the file count.

    Each reading is a tuple (ts, prim_used%, prim_window_min, prim_resets_at, sec_used%, sec_window_min,
    sec_resets_at, plan_type). `newer_than` (epoch s) skips files last modified before it, so a caller
    that wants only the latest reading need not open the whole history (ops_watch.py does this)."""
    recs = []
    nfiles = 0
    for d in (dirs or DIRS):
        for f in glob.glob(os.path.join(d, "**", "rollout-*.jsonl"), recursive=True):
            if newer_than is not None:
                try:
                    if os.path.getmtime(f) < newer_than:
                        continue
                except OSError:
                    continue
            nfiles += 1
            try:
                fh = open(f, encoding="utf-8", errors="replace")
            except OSError:
                continue
            with fh:
                for line in fh:
                    if '"rate_limits"' not in line:
                        continue
                    try:
                        r = json.loads(line)
                    except ValueError:
                        continue
                    pl = r.get("payload") if isinstance(r, dict) else None
                    rl = pl.get("rate_limits") if isinstance(pl, dict) else None
                    if not isinstance(rl, dict):
                        continue
                    p, s = rl.get("primary") or {}, rl.get("secondary") or {}
                    if not isinstance(p, dict) or not isinstance(s, dict):
                        continue
                    ts = r.get("timestamp")
                    up, sp = _num(p.get("used_percent")), _num(s.get("used_percent"))
                    if not ts or up is None:
                        continue
                    recs.append((ts, up, p.get("window_minutes"), p.get("resets_at"),
                                 sp, s.get("window_minutes"), s.get("resets_at"),
                                 rl.get("plan_type")))
    recs.sort(key=lambda r: str(r[0]))  # timestamps only: a None field later in a tuple must not be compared
    return recs, nfiles


def main():
    recs, nfiles = readings(DIRS)
    print(f"files {nfiles}, rate_limit readings {len(recs)}")
    if not recs:
        return 0
    print("plans:", collections.Counter(r[7] for r in recs).most_common(),
          "primary window min:", collections.Counter(r[2] for r in recs).most_common(3),
          "secondary window min:", collections.Counter(r[5] for r in recs).most_common(3))
    day = collections.defaultdict(list)
    for r in recs:
        day[r[0][:10]].append(r)
    print("day(UTC)    n   maxPrim%  maxSec%")
    for d, rs in sorted(day.items()):
        print(f"{d} {len(rs):5d} {max(x[1] for x in rs):8.1f} {max((x[4] or 0) for x in rs):8.1f}")
    # weekly resets: group readings by secondary resets_at (rounded to the hour)
    def hr(v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return dt.datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:00")
        return str(v)[:13]
    wk = collections.OrderedDict()
    for r in recs:
        weekly = r[6] if r[5] == 10080 or r[6] is not None else (r[3] if r[2] == 10080 else None)
        wk.setdefault(hr(weekly), []).append(r)
    print("weekly window (resets_at local)   readings  first_seen(UTC)       last_seen(UTC)        weekly% at last reading")
    for k, rs in wk.items():
        print(f"{str(k):32s} {len(rs):8d}  {rs[0][0][:19]}  {rs[-1][0][:19]}  {rs[-1][4] if rs[-1][5] == 10080 else rs[-1][1]}  max {max((x[4] if x[5] == 10080 else x[1]) or 0 for x in rs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
