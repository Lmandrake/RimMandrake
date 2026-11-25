#!/usr/bin/env python3
"""game_watch_tick.py: looks at each local game every 2 minutes and stops one that is broken (rm-game-watch.timer).

Page: design/specs/2026-11-24-game-watch-tick/boundary.md. The states are game_watcher.py's; the stop is
game_instance.stop(broken=True), which confirms again. No bridge call, no model.

    game_watch_tick.py tick [--dry]   one look. exit 0 looked; 1 a stop failed or a look raised
    game_watch_tick.py check          exit 0 the watcher runs and has seen each local game; 1 not; 2 could not look
    game_watch_tick.py show           the last reading

Reading: <RM_DISPATCHER_STATE>/game_watch/reading.json (RM_GAME_WATCH_DIR overrides); stops.jsonl and the kept
Player.log of each stop are beside it.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.join(os.path.dirname(HERE), "rimflow")
for _p in (HERE, RIMFLOW):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import game_instance as games  # noqa: E402
import game_watcher as W  # noqa: E402

FAMILY = "game_watch"
SIGNAL = "game_watcher.stopped"
# budget: danger=a game that would recover is stopped (107.4 s silent and back, 2026-11-20); ten times the longest that
# budget: recovered in the heartbeat records of 2026-11-20 to 24; longest=107.4s (TPS records, page LIMITS)
STOP_AGE_S = 1080
# budget: danger=a dead timer reads alive; ends no work: `check` answers 1
FRESH_S = 900


def state_dir():
    d = os.environ.get("RM_GAME_WATCH_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), FAMILY)
    return Path(d)


def episode_age(r):
    """Seconds the broken episode of this reading has lasted."""
    hb = r.heartbeat
    silent = min(hb["silentS"], hb["watchdogMono"] - hb["mainBeatMono"])
    if r.state == "frame_exceptions":
        return hb["watchdogMono"] - hb["frameFaultSinceMono"]
    if r.state == "stuck_load" and hb["scene"] == "loading":
        return hb["watchdogMono"] - hb["sceneSinceMono"]
    return silent


def off():
    """-> why the tick may not stop a game now, or None."""
    try:
        import control
        return control.blocked({"family": FAMILY})
    except Exception as e:  # noqa: BLE001  an unreadable switch is never "on"
        return "could not read the switches: %s: %s" % (type(e).__name__, e)


def _signal(why, now):
    import incident
    import refusal_contract
    with open(refusal_contract.SCHEDULE, encoding="utf-8") as fh:
        if not incident.signal(json.load(fh), SIGNAL, why, now):
            raise RuntimeError("the incident ledger is off or the route contains it")


def _keep_log(game, where, now):
    src = games.a_player_log() if game == games.DEFAULT else games.log_path(game)
    dst = where / ("%s_%d_Player.log" % (games.game_names.show(game), now))
    shutil.copyfile(src, dst)
    return str(dst)


def _try(fn, *args):
    try:
        return fn(*args), None
    except Exception as e:  # noqa: BLE001  one fault of the report never hides the stop
        return None, "%s: %s" % (type(e).__name__, e)


def stop(game, r, where, now):
    """Stop one broken game and report it. -> the row of stops.jsonl."""
    row = {"at": now, "game": games.game_names.show(game), "state": r.state, "pid": r.pid, "age_s": episode_age(r),
           "evidence": r.detail}
    try:
        rc, text = games.stop(name=game, broken=True)
        row.update(outcome="failed" if rc else "stopped", text=text)
    except (games.Refused, games.InstanceError) as e:
        row.update(outcome="refused", text=str(e))
    except games.Blind as e:
        row.update(outcome="could_not_look", text=str(e))
    except Exception as e:  # noqa: BLE001
        row.update(outcome="failed", text="%s: %s" % (type(e).__name__, e))
    where.mkdir(parents=True, exist_ok=True)
    if row["outcome"] in ("stopped", "failed"):
        row["log"], row["log_error"] = _try(_keep_log, game, where, now)
        _, row["signal_error"] = _try(_signal, "%s %s by the game watcher: %s for %.0f s (%s). Evidence: %s" % (
            row["game"], row["outcome"], r.state, row["age_s"], row["text"], where / "stops.jsonl"), now)
    with (where / "stops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def _last(where):
    try:
        got = json.loads((where / "reading.json").read_text(encoding="utf-8"))
        return got if isinstance(got.get("games"), dict) else {"games": {}}
    except (OSError, ValueError, AttributeError):
        return {"games": {}}


def tick(now=None, dry=False):
    now = time.time() if now is None else now
    where, rc, rows = state_dir(), 0, {}
    before, held = _last(where)["games"], off()
    for game in games.instances():
        name, was = games.game_names.show(game), before.get(games.game_names.show(game)) or {}
        r, err = _try(W.read, game)
        if err:
            r, rc = W.Reading("could_not_look", err), 1
        row = {"state": r.state, "detail": r.detail, "pid": r.pid, "seen": was.get("seen")}
        if r.state not in ("could_not_look", "process_gone"):
            row["seen"] = {"state": r.state, "at": now}
        elif r.state == "could_not_look":
            row["blind_since"] = was.get("blind_since") if was.get("pid") == r.pid and was.get("blind_since") else now
        if r.state in W.BROKEN:
            row["age_s"] = episode_age(r)
            if row["age_s"] < STOP_AGE_S:
                row["not_stopped"] = "younger than %d s" % STOP_AGE_S
            elif held or dry:
                row["not_stopped"] = held or "dry"
            else:
                done = stop(game, r, where, now)
                row["stop"] = done["outcome"]
                rc = rc or int(done["outcome"] == "failed" or bool(done.get("signal_error")))
        rows[name] = row
    got = {"at": now, "off": held, "games": rows}
    if not dry:
        where.mkdir(parents=True, exist_ok=True)
        tmp = where / "reading.json.tmp"
        tmp.write_text(json.dumps(got, indent=1, sort_keys=True), encoding="utf-8")
        os.replace(tmp, where / "reading.json")
    return rc, got


def check(now=None):
    now = time.time() if now is None else now
    path = state_dir() / "reading.json"
    try:
        got = json.loads(path.read_text(encoding="utf-8"))
        age, rows = now - got["at"], got["games"]
        unseen = [games.game_names.show(g) for g in games.instances()
                  if not (rows.get(games.game_names.show(g)) or {}).get("seen")]
    except FileNotFoundError:
        return 1, "NOT RUNNING: no reading at %s" % path
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        return 2, "COULD NOT LOOK: %s: %s: %s" % (path, type(e).__name__, e)
    if not 0 <= age <= FRESH_S:
        return 1, "NOT RUNNING: the reading at %s is %.0f s old" % (path, age)
    if unseen:
        return 1, "NEVER SEEN in a named state: %s" % ", ".join(unseen)
    return 0, "RUNNING: " + "; ".join("%s %s" % (n, r["state"]) for n, r in sorted(rows.items()))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("tick").add_argument("--dry", action="store_true")
    sub.add_parser("check")
    sub.add_parser("show")
    a = ap.parse_args(argv)
    if a.cmd == "tick":
        rc, got = tick(dry=a.dry)
        print(json.dumps(got, sort_keys=True))
        return rc
    if a.cmd == "check":
        rc, text = check()
        print(text)
        return rc
    try:
        print((state_dir() / "reading.json").read_text(encoding="utf-8"))
        return 0
    except OSError as e:
        print("COULD NOT LOOK: %s" % e)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
