#!/usr/bin/env python3
"""Codex (ChatGPT-auth) rate-limit history from codex rollout files (C-suite evidence, 2026-10-26).

Every codex rollout-*.jsonl records `rate_limits` events: primary (short window) and secondary
(weekly) used_percent, window_minutes, resets_at. This prints, per day: number of readings,
max primary/secondary used %, the distinct secondary reset times seen, and the used % at the
last reading before each secondary reset (idle quota thrown away at the reset).
Dirs: ~/.codex/sessions and the Windows user's .codex/sessions (override: args).
"""
import collections, datetime as dt, glob, json, math, os, sys, time

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


def _parse(fh, recs):
    """Append every rate_limits reading on the lines of `fh` to `recs`."""
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


def _load_cache(path):
    try:
        with open(path, encoding="utf-8") as fh:
            c = json.load(fh)
        return c if isinstance(c, dict) and c.get("v") == CACHE_V and isinstance(c.get("files"), dict) else None
    except (OSError, ValueError):
        return None


def _save_cache(path, files):
    tmp = path + ".tmp"     # one fixed name: a writer killed mid-dump leaves one file, overwritten next time
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"v": CACHE_V, "files": files}, fh, separators=(",", ":"))
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


CACHE_V = 2
CHECKPOINT_S = 4.0


def _entry_ok(e):
    """A cache entry this code wrote: anything else (a hand edit, an older layout) is read again from the file."""
    return (isinstance(e, dict) and isinstance(e.get("mt"), int) and isinstance(e.get("sz"), int)
            and isinstance(e.get("off"), int) and isinstance(e.get("head"), str)
            and all(isinstance(e.get(k), list) and all(isinstance(r, list) for r in e[k]) for k in ("recs", "tail")))


def _read_file(f, st, old):
    """(records, entry) for rollout file `f` with stat `st`. `old` is its cache entry or None: an unchanged
    file costs nothing, a grown one whose first 256 bytes are unchanged is read only past the last whole line
    already parsed (rollouts are append-only); any other change is read again whole. A last line without its
    newline is parsed as the plain read parses it, and kept apart ("tail"), so it is parsed again once it grows."""
    old = old if _entry_ok(old) else None
    if old and old["mt"] == st.st_mtime_ns and old["sz"] == st.st_size:
        return [tuple(r) for r in old["recs"] + old["tail"]], old
    recs, start = [], 0
    try:
        fh = open(f, "rb")
    except OSError:
        return None, None
    with fh:
        head = fh.read(256).hex()
        if old and 0 < old["off"] <= st.st_size and old["sz"] < st.st_size and old["head"] == head:
            recs, start = [tuple(r) for r in old["recs"]], old["off"]     # grown, same head: an append
        fh.seek(start)
        data = fh.read()
    cut = data.rfind(b"\n") + 1
    _parse(data[:cut].decode("utf-8", errors="replace").splitlines(), recs)
    tail = []
    _parse([data[cut:].decode("utf-8", errors="replace")] if cut < len(data) else [], tail)
    return recs + tail, {"mt": st.st_mtime_ns, "sz": st.st_size, "off": start + cut, "head": head,
                         "recs": recs, "tail": tail}


def readings(dirs=None, newer_than=None, cache=None):
    """Every rate_limits reading in the rollout files under `dirs`, oldest first, plus the file count.

    Each reading is a tuple (ts, prim_used%, prim_window_min, prim_resets_at, sec_used%, sec_window_min,
    sec_resets_at, plan_type). `newer_than` (epoch s) skips files last modified before it, so a caller
    that wants only the latest reading need not open the whole history (ops_watch.py does this).
    `cache` (a JSON path) keeps each file's readings keyed by its mtime and size, so a repeat call reads
    only what was appended since (ops_watch's sense beat: ~1 GB of rollouts took 22 s uncached)."""
    recs = []
    nfiles = 0
    old = (_load_cache(cache) or {}).get("files", {}) if cache else {}
    keep = {}
    saved = time.monotonic()
    for d in (dirs or DIRS):
        for f in glob.glob(os.path.join(d, "**", "rollout-*.jsonl"), recursive=True):
            try:
                st = os.stat(f)
            except OSError:
                continue
            if newer_than is not None and st.st_mtime < newer_than:
                continue
            nfiles += 1
            if cache:
                got, entry = _read_file(f, st, old.get(f))
                if got is None:
                    continue
                keep[f] = entry
                recs.extend(got)
                if entry is not old.get(f) and time.monotonic() - saved > CHECKPOINT_S:
                    _save_cache(cache, dict(old, **keep))     # a cold read killed at its limit still leaves its progress
                    saved = time.monotonic()
                continue
            try:
                fh = open(f, encoding="utf-8", errors="replace")
            except OSError:
                continue
            with fh:
                _parse(fh, recs)
    if cache:
        _save_cache(cache, keep)
    recs.sort(key=lambda r: str(r[0]))  # timestamps only: a None field later in a tuple must not be compared
    return recs, nfiles


def weekly(r):
    """(used%, resets_at) of the reading's window identified as 10080 minutes, else (None, None): a short window's
    percentage is never reported as weekly, and a reset on a nonweekly window is not a weekly reset."""
    if r[5] == 10080:
        return r[4], r[6]
    if r[2] == 10080:
        return r[1], r[3]
    return None, None


def fmt(v):
    return "unavailable" if v is None else f"{v:.1f}"


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
        secs = [x[4] for x in rs if x[4] is not None]
        print(f"{d} {len(rs):5d} {max(x[1] for x in rs):8.1f} {fmt(max(secs) if secs else None):>8s}")
    # weekly resets: group readings by secondary resets_at (rounded to the hour)
    def hr(v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return dt.datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:00")
        return str(v)[:13]
    wk = collections.OrderedDict()
    for r in recs:
        wk.setdefault(hr(weekly(r)[1]), []).append(r)
    print("weekly window (resets_at local)   readings  first_seen(UTC)       last_seen(UTC)        weekly% at last reading")
    for k, rs in wk.items():
        pcts = [weekly(x)[0] for x in rs if weekly(x)[0] is not None]
        print(f"{'no weekly window' if k is None else str(k):32s} {len(rs):8d}  {rs[0][0][:19]}  {rs[-1][0][:19]}  "
              f"{fmt(weekly(rs[-1])[0])}  max {fmt(max(pcts) if pcts else None)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
