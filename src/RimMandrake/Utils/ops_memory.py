#!/usr/bin/env python3
"""ops_memory: Operations' trending memory, step 1 of design/RimMandrake/operations_metronome_strategy_2026-11-02.md (§3).

The owner, 2026-11-01: Operations is "about watching and trending everything to keep an overall understanding in
context". ops_watch already stores every reading (series/<family>.jsonl). This program gathers nothing new: it reads
those series and writes, beside today's digest, one generation of

  memory.json   for programs: per reading its value and observation time, normal band, 6 h and 24 h trend, state
                (normal | drifting | outside | blind) and how long, time to a signed limit, a kept step change
  memory.md     for the judge: only the readings that are not normal-and-flat, every blind one, a count per family

READ ONLY: nothing decides from it yet (build step 2 onward). The band is never an alarm limit; signed limits in
ops_watch_rules.json "targets" still ring through ops_watch as before and are only used here for time to limit.

Typed readings (each rule is a review counterexample, and a case in selftest_ops_memory.py):
  number   band = median +- k scaled MADs of HOURLY bucket medians over the last 7 days less the last hour, so a burst
           of samples cannot outvote a quiet day. The spread is floored (rules band: sigma_floor_rel x |median|,
           sigma_floor_abs), so 10,000 zeros and one 0.001 is not an outlier. (Not the gap between distinct values:
           a two-level reading would band itself as wide as its own step.)
           A reading whose hours of day differ more than its noise is banded against the same hours of earlier days.
  counter  only rises save for resets: read as a rate per hour; a drop is a reset, counted, never a collapse.
  flag     0/1 or true/false: read by dwell (how long in its value, how often it changed), never by slope.
  blind    never measured, stale (older than 3 of its family's intervals, at least 30 min), sparse (measured in under
           a quarter of its family's rows in 24 h) or learning (under 12 hours of history): never `normal`.
  step     a move to a new level that stays is kept as "stepped from A to B at T" for as long as the 7-day window
           holds both sides, whatever the band has learned since.

Usage:
  python3 ops_memory.py build [--now EPOCH] [--out DIR]     # write memory.json + memory.md (one generation)
  python3 ops_memory.py check [--max-age-min 30]            # 0 = one fresh generation; 1 = say why not
"""
import argparse
import json
import math
import os
import sys
import time
from fnmatch import fnmatchcase
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ops_watch as ow  # noqa: E402

HOUR = 3600.0
BASELINE_DAYS = 7
READ_DAYS = 8
MIN_BASELINE_BUCKETS = 12
K = 3.0
MAD_SCALE = 1.4826
STALE_MIN_FLOOR = 30.0
SPARSE_SHARE = 0.25
PAGE_MAX_LINES = 120
MAX_AGE_MIN = 30.0

# Kinds by name, where the name alone settles it. Anything else is inferred from its values and says so (kind_from).
KINDS = {
    "counter": ["*.week_used_pct", "*.days_since_advance"],
    "flag": [],
    "number": [],
}


# ================================================================================================== small numerics
def median(xs):
    s = sorted(xs)
    n = len(s)
    if not n:
        return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def mad(xs, c=None):
    if not xs:
        return None
    c = median(xs) if c is None else c
    return median([abs(x - c) for x in xs])


def buckets(pts, width=HOUR):
    """[(t, v)] -> [(bucket_start, median v, n)] oldest first. One vote per hour, however many samples it holds."""
    by = {}
    for t, v in pts:
        by.setdefault(math.floor(t / width) * width, []).append(v)
    return [(b, median(vs), len(vs)) for b, vs in sorted(by.items())]


def theil_sen(pts, max_n=120):
    """Robust slope per HOUR of [(t, v)], or None under 4 points. Subsampled evenly past max_n (O(n^2))."""
    if len(pts) < 4:
        return None
    if len(pts) > max_n:
        step = len(pts) / float(max_n)
        pts = [pts[int(i * step)] for i in range(max_n)]
    sl = [(b[1] - a[1]) / ((b[0] - a[0]) / HOUR) for i, a in enumerate(pts) for b in pts[i + 1:] if b[0] > a[0]]
    return median(sl)


def fmt(x):
    if x is None:
        return "?"
    if isinstance(x, bool):
        return str(x).lower()
    a = abs(x)
    if a >= 100:
        return "%.0f" % x
    if a >= 10:
        return "%.1f" % x
    if a >= 1:
        return "%.2f" % x
    return "%.3g" % x


# ===================================================================================================== reading kinds
def raw_value(p):
    """A point's value as float, booleans as 1.0/0.0 (ops_watch.num drops booleans; a flag must keep them)."""
    v = p.get("v") if isinstance(p, dict) else None
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    return ow.num(p)


def kind_of(key, vals, any_bool):
    for kind, pats in KINDS.items():
        if any(fnmatchcase(key, p) for p in pats):
            return kind, "named"
    if any_bool or (vals and set(vals) <= {0.0, 1.0} and len(set(vals)) == 2):
        return "flag", "inferred"
    return "number", "inferred"


def to_rates(pts):
    """Counter [(t, v)] -> ([(t, rate per hour)], resets). A drop is a reset: the interval is skipped, not read as a
    collapse, and counted."""
    out, resets = [], 0
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t1 <= t0:
            continue
        if v1 < v0:
            resets += 1
            continue
        out.append((t1, (v1 - v0) / ((t1 - t0) / HOUR)))
    return out, resets


# ============================================================================================================ band
def band(bvals, floors, hours=None, now_hour=None):
    """bvals: hourly bucket medians in the baseline. -> dict(center, lo, hi, spread, kind) or None under the minimum.
    hours: the hour of day of each bucket; with enough days the band becomes same-hour when the hours' own medians
    differ by more than a band built from the noise left after removing them (a two-level day can have a MAD of 0,
    so the pooled spread is no yardstick)."""
    if len(bvals) < MIN_BASELINE_BUCKETS:
        return None
    c = median(bvals)
    floor = max(floors[0] * abs(c), floors[1])
    spread = max(MAD_SCALE * mad(bvals, c), floor)
    out = {"center": c, "lo": c - K * spread, "hi": c + K * spread, "spread": spread, "kind": "7 d"}
    if hours is not None and now_hour is not None and len(bvals) >= 72:
        by = {}
        for h, v in zip(hours, bvals):
            by.setdefault(h, []).append(v)
        if sum(1 for vs in by.values() if len(vs) >= 3) >= 18:
            hod = {h: median(vs) for h, vs in by.items() if len(vs) >= 3}
            resid = [v - hod[h] for h, v in zip(hours, bvals) if h in hod]
            rs = max(MAD_SCALE * mad(resid, 0.0), floor)
            near = [hod[h] for h in ((now_hour - 1) % 24, now_hour, (now_hour + 1) % 24) if h in hod]
            if near and max(hod.values()) - min(hod.values()) > 2 * K * rs:     # the hours differ by more than a band
                hc = median(near)
                out = {"center": hc, "lo": hc - K * rs, "hi": hc + K * rs, "spread": rs, "kind": "same hour"}
    return out


def find_step(bk, floors):
    """bk: hourly buckets [(t, v, n)] of the window. Among splits with at least 6 buckets a side whose medians differ by
    over 4 noises and whose sides each hold 90% of their points near their median, the one where the sum of deviations from each side's median is least (the change point).
    The noise floor is relative to the SMALLER side's level, so it does not move as the band learns the new level.
    -> dict(from, to, at) or None."""
    vs = [b[1] for b in bk]
    best = None
    for i in range(6, len(vs) - 5):
        a, b = vs[:i], vs[i:]
        ma, mb = median(a), median(b)
        noise = max(MAD_SCALE * mad(a, ma), MAD_SCALE * mad(b, mb), floors[0] * min(abs(ma), abs(mb)), floors[1])
        gap = abs(mb - ma)
        if gap <= 4 * noise:
            continue
        # a MAD is 0 when over half a side sits on one level, so a daily 100/140 cycle would pass the noise test:
        # each side must also hold 90% of its points within a quarter gap of its own median
        if any(sum(1 for x in side if abs(x - m) <= gap / 4) < 0.9 * len(side) for side, m in ((a, ma), (b, mb))):
            continue
        cost = sum(abs(x - ma) for x in a) + sum(abs(x - mb) for x in b)    # medians alone tie on every split
        if best is None or cost < best[0]:
            best = (cost, ma, mb, bk[i][0])
    if best is None:
        return None
    return {"from": best[1], "to": best[2], "at": best[3]}


# ========================================================================================================= one key
def trend_word(slope, window_h, spread):
    if slope is None:
        return None
    if abs(slope) * window_h < spread:
        return "flat"
    return "rising" if slope > 0 else "falling"


def hours_to_limit(v, slope, targets, key):
    """Hours until v crosses the nearest signed limit at this slope; 0 when already past; None when never."""
    best = None
    for tg in targets:
        if not fnmatchcase(key, tg["key"]):
            continue
        x, op = tg["value"], tg["op"]
        if ow._cmp(v, op, x):
            h = 0.0
        elif slope is None or slope == 0:
            continue
        elif op in ("<", "<=") and slope < 0:
            h = (v - x) / -slope
        elif op in (">", ">=") and slope > 0:
            h = (x - v) / slope
        else:
            continue
        if best is None or h < best[0]:
            best = (h, tg.get("tag"), x, op)
    return None if best is None else {"h": best[0], "tag": best[1], "value": best[2], "op": best[3]}


def flag_reading(pts, now):
    """Dwell: the current value, since when, changes in 24 h, its share of the window and the longest earlier dwell
    in that value. outside = a dwell longer than any seen before in the rarer value; drifting = flapping."""
    v = pts[-1][1]
    runs, start = [], pts[0][0]
    for (t0, a), (t1, b) in zip(pts, pts[1:]):
        if a != b:
            runs.append((a, start, t1))
            start = t1
    since = start
    changes_24h = sum(1 for _x, _s, e in runs if e >= now - 24 * HOUR)       # a run ends where a change happens
    spans = [(a, t1 - t0) for (t0, a), (t1, _b) in zip(pts, pts[1:])]    # time held in each value, not samples taken
    total = sum(w for _a, w in spans)
    share = (sum(w for a, w in spans if a == v) / total) if total > 0 else 1.0
    longest = max([e - s for x, s, e in runs if x == v] or [0.0])
    dwell = now - since
    state = "normal"
    if share < 0.5 and runs and dwell > longest:
        state = "outside"
    elif changes_24h >= 6:
        state = "drifting"
    return {"v": v, "since": since, "dwell_h": dwell / HOUR, "changes_24h": changes_24h, "share": share,
            "longest_dwell_h": longest / HOUR, "state": state}


def reading(key, samples, fam_rows, now, floors, targets):
    """samples: [(t, mark, value|None, is_bool)] for every family row that carried the key, oldest first.
    fam_rows: the family's row times (for coverage and cadence)."""
    meas = [(t, v) for t, m, v, _b in samples if m == "MEASURED" and v is not None]
    any_bool = any(b for *_x, b in samples)
    vals = [v for _t, v in meas]
    kind, kind_from = kind_of(key, vals, any_bool)
    out = {"kind": kind, "kind_from": kind_from}
    gaps = [b - a for a, b in zip(fam_rows, fam_rows[1:]) if b > a]
    cadence = median(gaps[-200:]) if gaps else None
    stale_s = max(STALE_MIN_FLOOR * 60, 3 * cadence) if cadence else STALE_MIN_FLOOR * 60
    rows24 = [t for t in fam_rows if t >= now - 24 * HOUR]
    m24 = [t for t, _v in meas if t >= now - 24 * HOUR]
    out["coverage_24h"] = (len(m24) / float(len(rows24))) if rows24 else None
    if not meas:
        out.update(state="blind", why="never measured in %d d" % READ_DAYS)
        return out
    t_last, v_last = meas[-1]
    out.update(t=t_last, age_min=(now - t_last) / 60.0, last=v_last)
    if now - t_last > stale_s:
        out.update(state="blind", why="stale: last measured %.0f min ago, limit %.0f" % ((now - t_last) / 60.0,
                                                                                         stale_s / 60.0))
        return out
    if len(rows24) >= 3 and len(m24) / float(len(rows24)) < SPARSE_SHARE:
        out.update(state="blind", why="sparse: measured in %d of %d rows in 24 h" % (len(m24), len(rows24)))
        return out
    if kind == "flag":
        if meas[-1][0] - meas[0][0] < MIN_BASELINE_BUCKETS * HOUR:
            out.update(state="blind", why="learning: %.1f of %d hours of history" % (
                (meas[-1][0] - meas[0][0]) / HOUR, MIN_BASELINE_BUCKETS))
            return out
        out.update(flag_reading(meas, now))
        return out
    series = meas
    if kind == "counter":
        series, resets = to_rates(meas)
        out["resets_7d"] = resets
        out["unit"] = "per hour"
        out["level"] = meas[-1][1]      # the raw reading, which signed limits are written against
        if not series:
            out.update(state="blind", why="learning: no rate yet")
            return out
    base_from, base_to = now - BASELINE_DAYS * 24 * HOUR, now - HOUR
    bk_all = buckets([p for p in series if p[0] >= base_from])
    bk_base = [b for b in bk_all if b[0] < base_to]
    cur = bk_all[-1][1] if bk_all and bk_all[-1][0] >= now - HOUR else series[-1][1]
    out["v"] = cur
    hours = [int(time.localtime(b[0]).tm_hour) for b in bk_base]
    bd = band([b[1] for b in bk_base], floors, hours, int(time.localtime(now).tm_hour))
    if bd and min(v for _t, v in series) >= 0 and bd["lo"] < 0:
        bd["lo"] = 0.0          # a reading never seen below zero is not banded below it
    s6 = theil_sen([p for p in series if p[0] >= now - 6 * HOUR])
    s24 = theil_sen([(b[0], b[1]) for b in bk_all if b[0] >= now - 24 * HOUR])
    out.update(slope_6h=s6, slope_24h=s24)
    if bd is None:
        out.update(state="blind", why="learning: %d of %d hours of history" % (len(bk_base), MIN_BASELINE_BUCKETS))
        return out
    out["band"] = bd
    out["trend_6h"] = trend_word(s6, 6, bd["spread"])
    out["trend_24h"] = trend_word(s24, 24, bd["spread"])
    inside = bd["lo"] <= cur <= bd["hi"]
    if not inside:
        state = "outside"
    else:
        state = "normal"
        s = s24 if out["trend_24h"] not in (None, "flat") else None
        if s:
            edge = bd["hi"] if s > 0 else bd["lo"]
            if (edge - cur) / s <= 24:
                state = "drifting"
                out["band_edge_h"] = (edge - cur) / s
    out["state"] = state
    since = now
    for b in reversed(bk_all):
        if (bd["lo"] <= b[1] <= bd["hi"]) != inside:
            break
        since = b[0]
    out["side_h"] = (now - since) / HOUR       # hours on this side of the band (inside or out), not in the state
    st = find_step(bk_all, floors)
    if st:
        out["step"] = st
    if kind in ("number", "counter"):
        if kind == "counter":           # a counter's limit is on its level; its rate per hour is that level's slope
            ttl = hours_to_limit(out["level"], cur, targets, key)
        else:
            ttl = hours_to_limit(cur, s6 if s6 is not None else s24, targets, key)
        if ttl:
            out["limit"] = ttl
    return out


# ============================================================================================================ build
def family_rows(fam, since):
    return ow.read_series(fam, since)


def build(now=None, fams=None, rules=None):
    now = time.time() if now is None else now
    if rules is None:
        try:
            rules = ow.load_rules()
        except Exception as e:      # a broken rules file costs time to limit only; the memory is still worth having
            rules = {"_error": str(e)}
    b = rules.get("band") if isinstance(rules.get("band"), dict) else {}
    floors = (float(b.get("sigma_floor_rel", 0.05)), float(b.get("sigma_floor_abs", 0.5)))
    targets = ow.good_targets(rules) if isinstance(rules.get("targets"), list) else []
    since = now - READ_DAYS * 24 * HOUR
    mem = {"written_at": now, "families": {}, "readings": {}, "built_from": {}}
    for fam in (fams or ow.ORDER):
        recs = [r for r in family_rows(fam, since) if r.get("t", 0) <= now]    # build --now EPOCH sees no later row
        rows = [r["t"] for r in recs]
        mem["built_from"][fam] = {"rows": len(rows), "last_row_t": rows[-1] if rows else None}
        per = {}
        for r in recs:
            for k, p in (r.get("points") or {}).items():
                if not isinstance(p, dict):
                    continue
                per.setdefault(k, []).append((r["t"], p.get("m"), raw_value(p), isinstance(p.get("v"), bool)))
        counts = {}
        for k in sorted(per):
            rd = reading(k, per[k], rows, now, floors, targets)
            rd["family"] = fam
            mem["readings"][k] = rd
            counts[rd["state"]] = counts.get(rd["state"], 0) + 1
        mem["families"][fam] = counts
    return mem


def is_exception(rd):
    if rd["state"] != "normal":
        return True
    if rd.get("trend_6h") not in (None, "flat") or rd.get("trend_24h") not in (None, "flat"):
        return True
    if rd.get("step") or (rd.get("limit") and rd["limit"]["h"] <= 48):
        return True
    return False


def line(key, rd, now):
    if rd["state"] == "blind":
        return "%s blind: %s" % (key, rd.get("why"))
    if rd["kind"] == "flag":
        return "%s %s for %s h (longest before %s h), %d changes in 24 h, %s" % (
            key, fmt(rd["v"]), fmt(rd["dwell_h"]), fmt(rd["longest_dwell_h"]), rd["changes_24h"], rd["state"])
    bd = rd["band"]
    unit = " /h" if rd["kind"] == "counter" else ""
    s = "%s %s%s (normal %s to %s%s)" % (key, fmt(rd["v"]), unit, fmt(bd["lo"]), fmt(bd["hi"]),
                                         ", same hour" if bd["kind"] == "same hour" else "")
    use24 = rd.get("trend_24h") not in (None, "flat")
    tr = rd.get("trend_24h") if use24 else rd.get("trend_6h")
    if tr and tr != "flat":
        sl = rd["slope_24h"] if use24 else rd["slope_6h"]
        s += " %s %s/h" % (tr, fmt(sl))
    s += ", %s %s h" % ("outside" if rd["state"] == "outside" else "in band", "%.1f" % rd["side_h"])
    if rd["state"] == "drifting":
        s += ", drifting"
    if rd.get("band_edge_h") is not None:
        s += ", band edge in %s h" % fmt(rd["band_edge_h"])
    if rd.get("step"):
        st = rd["step"]
        s += "; stepped from %s to %s at %s" % (fmt(st["from"]), fmt(st["to"]),
                                                time.strftime("%m-%d %H:%M", time.localtime(st["at"])))
    if rd.get("limit"):
        lm = rd["limit"]
        s += "; limit %s %s %s" % (lm["op"], fmt(lm["value"]),
                                   "PAST" if lm["h"] == 0 else "in %s h" % fmt(lm["h"]))
    if rd.get("resets_7d"):
        s += "; %d resets in 7 d" % rd["resets_7d"]
    if rd.get("age_min") is not None and rd["age_min"] > 20:
        s += "; read %.0f min ago" % rd["age_min"]
    return s


def render(mem, generation, names=()):
    now = mem["written_at"]
    head = ["# Operations memory, generation %d" % generation,
            "written %s; read beside the digest, not instead of it. Exceptions only; every blind reading listed." %
            time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(now)), ""]
    exc, blind = [], []
    for k, rd in sorted(mem["readings"].items()):
        if rd["state"] == "blind":
            blind.append(line(k, rd, now))
        elif is_exception(rd) or any(fnmatchcase(k, n) for n in names):
            exc.append((0 if rd["state"] == "outside" else 1 if rd["state"] == "drifting" else 2, line(k, rd, now)))
    exc.sort(key=lambda x: x[0])
    cut = max(0, len(exc) + len(blind) - PAGE_MAX_LINES)
    if cut:
        # cut from the calm end of the exceptions, never a blind line and never an outside one (ranked by state,
        # not by searching the rendered text)
        keep_exc = max(sum(1 for r, _s in exc if r == 0), len(exc) - cut)
        cut = len(exc) - keep_exc
        exc = exc[:keep_exc]
    exc = [s for _r, s in exc]
    out = head + ["## Not normal and flat (%d)" % len(exc)] + ["- " + s for s in exc]
    if cut:
        out.append("- (%d calmer lines cut; all in memory.json)" % cut)
    out += ["", "## Blind (%d)" % len(blind)] + ["- " + s for s in blind]
    out += ["", "## Per family"]
    for fam, c in mem["families"].items():
        out.append("- %s: %s" % (fam, ", ".join("%d %s" % (n, s) for s, n in sorted(c.items())) or "no readings"))
    return "\n".join(out) + "\n"


def out_dir():
    return ow.ops_dir()


def publish(mem, outdir=None, names=()):
    """Write memory.md then memory.json, each whole and swapped in one step, both carrying the same generation."""
    d = Path(outdir) if outdir else out_dir()
    d.mkdir(parents=True, exist_ok=True)
    gen = 0
    try:
        gen = int(json.loads((d / "memory.json").read_text(encoding="utf-8")).get("generation", 0))
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    gen += 1
    mem["generation"] = gen
    md = render(mem, gen, names)
    tmp = d / "memory.md.tmp"
    tmp.write_text(md, encoding="utf-8")
    os.replace(tmp, d / "memory.md")
    ow.atomic_json(d / "memory.json", mem)
    return gen, md


def check(outdir=None, now=None, max_age_min=MAX_AGE_MIN):
    """-> (ok, why). One generation in both files, written within max_age_min."""
    d = Path(outdir) if outdir else out_dir()
    now = time.time() if now is None else now
    try:
        j = json.loads((d / "memory.json").read_text(encoding="utf-8"))
        first = (d / "memory.md").read_text(encoding="utf-8").split("\n", 1)[0]
    except (OSError, ValueError) as e:
        return False, "unreadable: %s" % e
    g_md = first.rsplit(" ", 1)[-1] if first.startswith("# Operations memory, generation ") else None
    if str(j.get("generation")) != g_md:
        return False, "two generations: memory.json %s, memory.md %s" % (j.get("generation"), g_md)
    age = (now - float(j.get("written_at", 0))) / 60.0
    if age > max_age_min:
        return False, "stale: generation %s written %.0f min ago (limit %.0f)" % (g_md, age, max_age_min)
    return True, "generation %s, %.0f min old" % (g_md, age)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--now", type=float)
    b.add_argument("--out")
    b.add_argument("--name", action="append", default=[], help="a key glob always shown on the page")
    c = sub.add_parser("check")
    c.add_argument("--out")
    c.add_argument("--max-age-min", type=float, default=MAX_AGE_MIN)
    a = ap.parse_args(argv)
    if a.cmd == "build":
        t0 = time.time()
        mem = build(a.now)
        gen, md = publish(mem, a.out, a.name)
        n = len(mem["readings"])
        blind = sum(1 for r in mem["readings"].values() if r["state"] == "blind")
        print("ops_memory: generation %d, %d readings (%d blind), page %d lines, %.1f s" % (
            gen, n, blind, md.count("\n"), time.time() - t0))
        return 0
    ok, why = check(a.out, None, a.max_age_min)
    print(("OK " if ok else "NOT OK ") + why)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
