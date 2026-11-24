#!/usr/bin/env python3
"""Classify one local game from its TPS heartbeat and process list. No bridge and no writes."""
import argparse
from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path
import time

import game_instance as games
from tps_record import HB_FRESH_SECONDS, PROC_START_TOLERANCE_S, _epoch, loads_strict

BROKEN = {"frames_stopped", "frame_exceptions", "stuck_load"}
# budget: danger=a stalled main thread read as healthy; ends no work: a silence this long reads STALLED and a dump is written;
# budget: the game goes on
STALL_S = 60       # stall dump threshold; known long events can recover, see boundary LIMITS
# budget: danger=a stuck load read as a slow load (MapInitializing stall, 2026-10-26); ends no work: a load this old reads
# budget: stuck_load; the game goes on
LOAD_S = 600      # scene settle threshold after the 2026-10-26 MapInitializing stall
CADENCE_S = 5     # writer cadence; a shorter exception streak can come from one bad moment (boundary LIMITS)
CONFIRM_S = 2 * CADENCE_S    # beyond the watchdog's immediate warm-up pair (boundary LIMITS)


@dataclass(frozen=True)
class Reading:
    state: str
    detail: str
    pid: int = None
    start: float = None
    heartbeat: dict = None


def record_dir(game):
    if game == games.DEFAULT:
        import game_paths
        root = game_paths.LOCALLOW if games.current() == games.DEFAULT else os.path.dirname(games.a_player_log())
    else:
        root = games.data_dir(game)
    return Path(root) / "JawaBench" / "tps"


def _heartbeat(directory, proc):
    """Read bytes and mtime from the same open file, even across atomic replacement."""
    matches, errors = [], []
    for path in Path(directory).iterdir():
        if not (path.name.startswith("hb_") and path.suffix == ".json"):
            continue
        try:
            with path.open(encoding="utf-8") as fh:
                mtime = os.fstat(fh.fileno()).st_mtime
                hb = loads_strict(fh.read())
            if not isinstance(hb, dict):
                raise ValueError("expected an object")
        except (OSError, ValueError) as e:
            errors.append("%s: %s" % (path, e))
            continue
        start = _epoch(hb.get("procStartUtc"))
        if hb.get("pid") == proc["pid"] and start is not None and abs(start - proc["start"]) <= PROC_START_TOLERANCE_S:
            matches.append((hb, mtime, path))
    if len(matches) == 1:
        return matches[0]
    if matches:
        raise ValueError("multiple heartbeats match pid %s in %s" % (proc["pid"], directory))
    raise ValueError("no matching heartbeat for pid %s in %s%s" % (proc["pid"], directory,
                     " (%s)" % "; ".join(errors) if errors else ""))


def _number(v):
    return type(v) in (int, float) and 0 <= v < math.inf


def _state(hb):
    scene, phase, paused = hb.get("scene"), hb.get("phase"), hb.get("paused")
    if (scene not in ("map", "menu", "no_map", "loading") or not isinstance(phase, str)
            or not isinstance(hb.get("session"), str) or not hb["session"]
            or any(type(hb.get(k)) is not int or hb[k] < 0 for k in ("hbSeq", "frames", "frameFaultStreak", "ticksGame"))
            or any(not _number(hb.get(k)) for k in ("silentS", "watchdogMono", "mainBeatMono", "sceneSinceMono"))
            or hb["frameFaultStreak"] > hb["frames"]):
        return "could_not_look", "incomplete heartbeat fields"
    silent = min(hb["silentS"], hb["watchdogMono"] - hb["mainBeatMono"])
    if scene == "loading" or phase == "load":
        age = hb["watchdogMono"] - hb["sceneSinceMono"] if scene == "loading" else silent
        return ("stuck_load" if age >= LOAD_S else "loading"), "load evidence %.1fs (main thread silent %.1fs)" % (age, silent)
    if silent >= STALL_S:
        if phase in ("save", "longEvent"):
            return "could_not_look", "main thread silent %.1fs during %s" % (silent, phase)
        return "frames_stopped", "main thread silent %.1fs in %s" % (silent, phase)
    if silent >= HB_FRESH_SECONDS or not hb["frames"]:
        return "could_not_look", "no recent completed frame (main thread silent %.1fs)" % silent
    if hb["frameFaultStreak"]:
        since = hb.get("frameFaultSinceMono")
        if not _number(since) or since > hb["watchdogMono"]:
            return "could_not_look", "missing frame exception timing"
        if hb["frameFaultStreak"] > 1 and hb["watchdogMono"] - since >= CADENCE_S:
            return "frame_exceptions", "%d consecutive throwing frames" % hb["frameFaultStreak"]
    if scene != "map":
        return scene, "%d frames completed, phase %s" % (hb["frames"], phase)
    if paused is True:
        return "paused", "paused at tick %d" % hb["ticksGame"]
    last = hb.get("lastTickMono")
    if paused is False and _number(last) and 0 <= hb["watchdogMono"] - last <= HB_FRESH_SECONDS:
        return "ticking", "recent progress, tick %d" % hb["ticksGame"]
    return "could_not_look", "no pause or recent tick progress at tick %d" % hb["ticksGame"]


def read(game, directory=None, *, now=None):
    game = games.check_name(game)
    try:
        procs = games.procs(game)
        if not procs:
            return Reading("process_gone", "no process in the measured list")
        if len(procs) != 1 or procs[0]["start"] is None:
            return Reading("could_not_look", "could not identify one process with a start time: %s" % procs)
        proc = procs[0]
        hb, mtime, path = _heartbeat(directory if directory is not None else record_dir(game), proc)
    except (games.Blind, OSError, ValueError) as e:
        return Reading("could_not_look", str(e))
    age = (time.time() if now is None else now) - mtime
    state, detail = _state(hb) if 0 <= age <= HB_FRESH_SECONDS else (
        "could_not_look", "heartbeat timestamp outside freshness window (age %.1fs)" % age)
    return Reading(state, "%s: %s" % (path, detail), proc["pid"], proc["start"], hb)


def _same_episode(state, a, b):
    if (b["session"] != a["session"] or b["hbSeq"] <= a["hbSeq"]
            or b["watchdogMono"] - a["watchdogMono"] < CADENCE_S):
        return False
    if state == "frames_stopped":
        return b["mainBeatMono"] == a["mainBeatMono"]
    if state == "stuck_load":
        if a["scene"] == b["scene"] == "loading":
            return b["sceneSinceMono"] == a["sceneSinceMono"]
        return a["phase"] == b["phase"] == "load" and b["mainBeatMono"] == a["mainBeatMono"]
    frames = b["frames"] - a["frames"]
    return frames > 0 and b["frameFaultStreak"] == a["frameFaultStreak"] + frames


def confirm(game):
    first = read(game)
    if first.state not in BROKEN:
        return first, False
    at = time.monotonic()
    time.sleep(CONFIRM_S)
    second = read(game)
    confirmed = (time.monotonic() - at >= CONFIRM_S
                 and second.state == first.state and (second.pid, second.start) == (first.pid, first.start)
                 and _same_episode(first.state, first.heartbeat, second.heartbeat))
    return second, confirmed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("game")
    args = ap.parse_args(argv)
    try:
        game = games.check_name(args.game)
    except games.InstanceError as e:
        ap.exit(games.EX_REFUSED, "REFUSED: %s\n" % e)
    r = read(game)
    print(json.dumps(dict(asdict(r), game=games.game_names.show(game)), sort_keys=True))
    if r.state == "could_not_look":
        return games.EX_BLIND
    return int(r.state in BROKEN or r.state == "process_gone")


if __name__ == "__main__":
    raise SystemExit(main())
