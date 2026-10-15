#!/usr/bin/env python3
"""spike.early-load (design/RimMandrake/game_health_record.md): where did a cold load go quiet BEFORE the
JawaBench companion existed?

The companion registers only after play data has loaded, so nothing inside the game can time the cold load.
This reader works from what the external observer (health_observer.py) already records - the Player.log size
every sample, the game process identity, and the startup milestones - and adds no probe of its own:

  * a SILENCE is a run of observer samples, with a RimWorld process alive and the log readable, in which
    Player.log did not grow, lasting at least --min-silence seconds;
  * an unavailable or failed log.growth sample is a COVERAGE GAP, never a silence (unavailable is never zero);
  * each silence is placed in a load PHASE by the last startup milestone before it (within the same launch);
  * the last complete line written before the silence is quoted from Player.log at the size the observer saw.

Wording rule: the last line is where the log STOPPED, not proven to be where the load stalled. No mod is blamed.
A verbose load (Prefs.LogVerbose) is a diagnostic load: compare it only with other verbose loads.

    python3 src/RimMandrake/Utils/health_earlyload.py [--dir D] [--log Player.log] [--min-silence 60] [--since UTC]

Status: written, not deployed or run against a real load (2026-10-14); cost UNMEASURED (on demand, offline).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

PHASES = [  # milestone id -> the phase that FOLLOWS it
    ("engine.mono", "engine start (Mono up, before the engine initialised)"),
    ("engine.init", "mod and def loading (after engine start, before RimBridge startup)"),
    ("game.version", "mod and def loading (after engine start, before RimBridge startup)"),
    ("rimbridge.startup", "after RimBridge startup, before the JawaBench companion registered"),
    ("bridge.token", "after RimBridge startup, before the JawaBench companion registered"),
    ("jawabench.ready", "companion present: the TPS record covers this stretch"),
    ("unity.memstats", "shutdown (Unity printed memory statistics)"),
]
PHASE_OF = dict(PHASES)


def _covered(r):
    """(log size or None, process alive) for a sample; size None = coverage gap."""
    src = r.get("sources") or {}
    lg = src.get("log.growth") or {}
    gi = src.get("game.identity") or {}
    alive = gi.get("status") == "ok" and bool(((gi.get("value") or {}).get("procs")))
    if lg.get("status") != "ok":
        return None, alive
    v = lg.get("value") or {}
    if v.get("missing") or v.get("size") is None:
        return None, alive
    return v["size"], alive


def silences(rows, min_s=60.0):
    """Runs of no log growth, process alive, log readable; each {fromT, toT, durS, open, sizeAt}."""
    out = []
    anchor_t = anchor_size = quiet_since = None
    last_t = None
    for r in sorted((r for r in rows if r.get("kind") == "sample"), key=lambda r: r["_t"]):
        t = r["_t"]
        size, alive = _covered(r)
        if size is None or not alive:                    # gap or no game: what happened is unknown, end any run
            anchor_t = anchor_size = quiet_since = None
            continue
        last_t = t
        if anchor_size is None or size != anchor_size:
            if quiet_since is not None and t - quiet_since >= min_s:
                out.append({"fromT": quiet_since, "toT": t, "durS": round(t - quiet_since, 3), "open": False, "sizeAt": anchor_size})
            anchor_t, anchor_size, quiet_since = t, size, None
        elif quiet_since is None:
            quiet_since = anchor_t
    if quiet_since is not None and last_t is not None and last_t - quiet_since >= min_s:
        out.append({"fromT": quiet_since, "toT": last_t, "durS": round(last_t - quiet_since, 3), "open": True, "sizeAt": anchor_size})
    return out


def coverage_gaps(rows, min_s=60.0):
    """Spans where log.growth was not ok: the observer could not see, so nothing is said about them."""
    out, start = [], None
    for r in sorted((r for r in rows if r.get("kind") == "sample"), key=lambda r: r["_t"]):
        st = ((r.get("sources") or {}).get("log.growth") or {}).get("status")
        if st != "ok":
            if start is None:
                start = r["_t"]
        elif start is not None:
            if r["_t"] - start >= min_s:
                out.append({"fromT": start, "toT": r["_t"], "durS": round(r["_t"] - start, 3)})
            start = None
    return out


def phase_at(milestones, t):
    """Phase from the last phase milestone at or before t, within the launch that began at the last engine.mono."""
    ms = sorted((m for m in milestones if m.get("id") in PHASE_OF and m["_t"] <= t), key=lambda m: m["_t"])
    launches = [i for i, m in enumerate(ms) if m["id"] == "engine.mono"]
    if launches:
        ms = ms[launches[-1]:]
    if not ms:
        return "unknown (no startup milestone seen before it)"
    return PHASE_OF[ms[-1]["id"]]


def last_line(data, offset):
    """The last COMPLETE line in data[:offset] (a partial trailing line is not quoted), or None."""
    chunk = data[:offset]
    k = chunk.rfind(b"\n")
    if k < 0:
        return None
    body = chunk[:k]
    j = body.rfind(b"\n")
    line = body[j + 1:].decode("utf-8", "replace").rstrip("\r")
    return line if line or j >= 0 else None


def read_last_line(path, offset, window=65536):
    try:
        with open(path, "rb") as f:
            start = max(0, offset - window)
            f.seek(start)
            data = f.read(offset - start)
        return last_line(data, len(data))
    except OSError:
        return None


def describe(sil, phase, line, fmt):
    tail = " and still silent at the last sample" if sil["open"] else ""
    ln = ("'%s'" % line[:300]) if line is not None else "unavailable (Player.log not readable at that size, or rotated since)"
    return ("log silent from %s to %s (%s s%s) during %s; last line written before the silence: %s. "
            "The last line is where the log stopped, not proven to be where the load stalled."
            % (fmt(sil["fromT"]), fmt(sil["toT"]), sil["durS"], tail, phase, ln))


def main(argv=None):
    import health_observer as HO
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", default=None)
    ap.add_argument("--log", default=None, help="Player.log to quote (default: the live one; valid only for the same launch)")
    ap.add_argument("--min-silence", type=float, default=60.0)
    ap.add_argument("--since", default=None, help="UTC ISO time; ignore samples before it")
    a = ap.parse_args(argv)
    st = HO.read_stream(a.dir)
    rows = st["rows"]
    if a.since:
        t0 = HO.epoch(a.since)
        rows = [r for r in rows if r["_t"] >= t0]
    if not [r for r in rows if r.get("kind") == "sample"]:
        print("NO OBSERVER COVERAGE (%s, %d files): say nothing about where a load stalled" % (st["dir"], st["files"]))
        return 1
    log = a.log or HO.default_log()
    ms = [r for r in rows if r.get("kind") == "event" and r.get("event") == "milestone"]
    for s in silences(rows, a.min_silence):
        print(describe(s, phase_at(ms, s["fromT"]), read_last_line(log, s["sizeAt"]), HO.utc))
    for g in coverage_gaps(rows, a.min_silence):
        print("observer could not read the log from %s to %s (%s s): nothing is said about that stretch" % (HO.utc(g["fromT"]), HO.utc(g["toT"]), g["durS"]))
    print("observations only; no cause is established (malformed rows: %d)" % st["malformed"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
