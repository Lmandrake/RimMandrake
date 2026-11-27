#!/usr/bin/env python3
"""rand_trace_verdict.py - which Verse.Rand draws part runs that start from one save and one written-back random state.

Item RIMMANDRAKE_FIND_RAND_DRAWS_PARTING_RUNS_EVEN_STEP. Input: the JSON that rand_trace.py writes, one entry per run, each with
the `jawa/rand_trace` read of that run (ticks[] {t, i0, i1, hooked, reseeds, seen}, rows[] {t, ph, c, n}, anchorTick,
anchorState). Pure: no game, no bridge.

    python3 rand_trace_verdict.py check <runs.json>     exit 0: the STEP runs repeat, or the draws that part them are named
                                                        exit 1: not decided (the reason is printed)
    python3 rand_trace_verdict.py report <runs.json>    the same verdict, and the parting rows of every pair, as markdown

THE INSTRUMENT MUST SEE BEFORE IT NAMES (the four answers): a run is refused when
  - a traced tick reads seen=false (the hook counted fewer draws than the stream moved: an inlined draw), or
  - a gap between ticks (or the gap from the write-back to the first tick) moved the stream by a count other than the
    depth-0 draws the hook saw there, or
  - its trace is not whole: no ticks, rows cut, faults, or a window that never opened.
So a pass cannot rest on a trace that could not see.

Runs part only on depth-0 draws: a draw at a pushed state (`+pushed`, for example inside a method the tracer isolates) leaves
the global stream still, so it is reported nowhere as a parting. Runs that isolated different methods are not compared.
"""
import json
import sys
from collections import defaultdict

MIN_STEP_RUNS = 3      # the item's oracle: three STEP runs (its ## verify)


def _depth0(ph):
    return not ph.endswith("+pushed")


def blind(run):
    """Why this run's trace cannot speak, or None."""
    tr = run.get("trace") or {}
    if tr.get("success", True) is not True:
        return "the read failed: %s" % tr.get("message")
    if tr.get("anchorTick", -1) < 0:
        return "the window never opened (no random write-back reached the tracer)"
    ticks = tr.get("ticks") or []
    if not ticks:
        return "no tick was traced"
    if tr.get("rowsCut"):
        return "the rows were cut (%s rows): read again with a larger maxRows" % tr.get("rowCount")
    if tr.get("faults"):
        return "the tracer faulted %s times: %s" % (tr["faults"], tr.get("lastFault"))
    unseen = [t["t"] for t in ticks if not t.get("seen")]
    if unseen:
        return "ticks %s moved the stream by more draws than the hook saw (first: %s)" % (unseen[:5], _tick_why(ticks, unseen[0]))
    rows = tr.get("rows") or []
    by = defaultdict(int)
    for r in rows:
        if r["ph"] in ("pre", "frame"):
            by[r["t"]] += r["n"]
    anchor_iter = (int(tr["anchorState"]) >> 32) & 0xFFFFFFFF
    gaps = [(tr["anchorTick"], anchor_iter, ticks[0]["i0"])]
    for a, b in zip(ticks, ticks[1:]):
        gaps.append((a["t"], a["i1"], b["i0"]))
    for label, start, end in gaps:
        moved = (end - start) & 0xFFFFFFFF
        if moved != by.get(label, 0):
            return "the gap after tick %s moved the stream %s draws, the hook saw %s there" % (label, moved, by.get(label, 0))
    return None


def _tick_why(ticks, t):
    row = next(x for x in ticks if x["t"] == t)
    return "tick %s: stream %s, hooked %s, reseeds %s" % (t, (row["i1"] - row["i0"]) & 0xFFFFFFFF, row["hooked"], row["reseeds"])


def counts(run):
    """(tick, phase, caller) -> draws, the depth-0 rows only (a pushed draw moves no global stream)."""
    out = defaultdict(int)
    for r in (run.get("trace") or {}).get("rows") or []:
        if _depth0(r["ph"]):
            out[(r["t"], r["ph"], r["c"])] += r["n"]
    return out


def iterations(run):
    """tick -> Rand.iterations at the end of that tick (the item's track)."""
    return {t["t"]: t["i1"] for t in (run.get("trace") or {}).get("ticks") or []}


def part(a, b):
    """The first tick (by the run's own tick numbers) at which two runs' draws differ, and the rows that differ there.
    None when every row of the window agrees."""
    ca, cb = counts(a), counts(b)
    keys = set(ca) | set(cb)
    diff = sorted(k for k in keys if ca.get(k, 0) != cb.get(k, 0))
    if not diff:
        return None
    t0 = diff[0][0]
    return {"tick": t0, "rows": [{"t": k[0], "ph": k[1], "c": k[2], "a": ca.get(k, 0), "b": cb.get(k, 0)} for k in diff if k[0] == t0]}


def verdict(data):
    """-> (decided: bool, lines: [str], pairs: [(i, j, part)])"""
    runs = data.get("runs") or []
    step = [(i, r) for i, r in enumerate(runs) if r.get("arm") == "step"]
    lines = []
    if len(step) < MIN_STEP_RUNS:
        return False, ["NOT DECIDED: %d STEP runs, %d needed" % (len(step), MIN_STEP_RUNS)], []
    for i, r in step:
        why = blind(r)
        if why:
            return False, ["NOT DECIDED: run %d (%s) could not see: %s" % (i, r.get("arm"), why)], []
    anchors = {str(r["trace"].get("anchorState")) for _i, r in step}
    if len(anchors) != 1:
        return False, ["NOT DECIDED: the STEP runs started from different random states %s" % sorted(anchors)], []
    isos = {tuple(r["trace"].get("isolate") or ()) for _i, r in step}
    if len(isos) != 1:
        return False, ["NOT DECIDED: the STEP runs isolated different methods %s" % sorted(isos)], []
    iso = next(iter(isos))
    windows = {(r["trace"]["ticks"][0]["t"], r["trace"]["ticks"][-1]["t"]) for _i, r in step}
    if len(windows) != 1:
        return False, ["NOT DECIDED: the STEP runs traced different ticks %s" % sorted(windows)], []
    ref_i, ref = step[0]
    pairs = []
    unnamed = []
    for i, r in step[1:]:
        p = part(ref, r)
        pairs.append((ref_i, i, p))
        if p is not None and not any(x["c"] and x["c"] != "?" for x in p["rows"]):
            unnamed.append(i)
    if unnamed:
        return False, ["NOT DECIDED: runs %s part from run %d with no caller named" % (unnamed, ref_i)], pairs
    parted = [x for x in pairs if x[2] is not None]
    held = (", isolating %s" % ", ".join(iso)) if iso else ""
    if not parted:
        same_iter = all(iterations(r) == iterations(ref) for _i, r in step[1:])
        lines.append("DECIDED: the %d STEP runs drew the same count from the same callers on every traced tick%s; %s" % (
            len(step), held, "Rand.iterations equal on every traced tick" if same_iter else "Rand.iterations NOT equal (a draw the rows miss)"))
        if not same_iter:
            return False, ["NOT DECIDED: the rows agree and Rand.iterations does not: the instrument missed a draw"], pairs
    else:
        lines.append("DECIDED: %d of %d STEP runs part from run %d%s; the parting draws are named by caller and phase" % (
            len(parted), len(step) - 1, ref_i, held))
    return True, lines, pairs


def report(data):
    ok, lines, pairs = verdict(data)
    out = ["# Rand draws that part the runs", ""] + lines + [""]
    for a, b, p in pairs:
        if p is None:
            out.append("- run %d against run %d: equal on every traced tick" % (b, a))
            continue
        out.append("- run %d against run %d: first parting tick %d" % (b, a, p["tick"]))
        out.append("")
        out.append("| tick | phase | caller | run %d | run %d |" % (a, b))
        out.append("|---|---|---|---|---|")
        for x in p["rows"]:
            out.append("| %d | %s | `%s` | %d | %d |" % (x["t"], x["ph"], x["c"], x["a"], x["b"]))
        out.append("")
    return ok, "\n".join(out)


def main(argv):
    if len(argv) != 2 or argv[0] not in ("check", "report"):
        print(__doc__)
        return 2
    try:
        with open(argv[1]) as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        print("COULD NOT LOOK: %s: %s" % (argv[1], e))
        return 1
    if argv[0] == "check":
        ok, lines, _p = verdict(data)
        print("\n".join(lines))
    else:
        ok, text = report(data)
        print(text)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
