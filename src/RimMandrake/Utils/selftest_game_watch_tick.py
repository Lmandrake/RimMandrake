#!/usr/bin/env python3
"""Offline tests of game_watch_tick.py. Every read, stop, switch, signal and log is faked."""
import contextlib
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

import game_instance as GI
import game_watch_tick as T
import game_watcher as W

NOW = 1795470000.0
HB = dict(scene="map", silentS=0, watchdogMono=5000, mainBeatMono=5000, sceneSinceMono=100, frameFaultSinceMono=None)


def broken(state, age):
    hb = dict(HB)
    if state == "frames_stopped":
        hb.update(silentS=age, mainBeatMono=5000 - age)
    elif state == "frame_exceptions":
        hb.update(frameFaultSinceMono=5000 - age)
    else:
        hb.update(scene="loading", sceneSinceMono=5000 - age)
    return W.Reading(state, "hb_x.json: evidence", 73, NOW - 9000, hb)


OK = W.Reading("paused", "fine", 74, NOW - 9000, HB)


@contextlib.contextmanager
def world(d, big=OK, small=OK, stop=(0, "STOPPED"), off=None, signal=None):
    """-> (stopped games, signals). `big`/`small`: a Reading, or an exception to raise."""
    stopped, signals = [], []

    def read(game):
        got = {"a": big, "b": small}[game]
        if isinstance(got, Exception):
            raise got
        return got

    def fake_stop(name=None, broken=False, **kw):
        assert broken and not kw, "the tick must use the confirmed emergency stop"
        stopped.append(name)
        if isinstance(stop, Exception):
            raise stop
        return stop

    def fake_signal(why, now):
        signals.append(why)
        if signal:
            raise signal

    log = Path(d) / "src_Player.log"
    log.write_text("the log of the dead game")
    with patch.dict(os.environ, RM_GAME_WATCH_DIR=str(Path(d) / "out"), RM_GAME_INSTANCES="a,b"), \
         patch.object(W, "read", side_effect=read), patch.object(GI, "stop", side_effect=fake_stop), \
         patch.object(T, "off", return_value=off), patch.object(T, "_signal", side_effect=fake_signal), \
         patch.object(GI, "a_player_log", return_value=str(log)), patch.object(GI, "log_path", return_value=str(log)):
        yield stopped, signals


def rows(d):
    p = Path(d) / "out" / "stops.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def t_a_broken_game_is_stopped(d):
    for state in sorted(W.BROKEN):
        for age, want in ((T.STOP_AGE_S, ["a"]), (T.STOP_AGE_S - 1, [])):
            with world(d, big=broken(state, age)) as (stopped, _):
                _, got = T.tick(NOW)
            assert stopped == want, "%s at %s s: stopped %r" % (state, age, stopped)
            assert got["games"]["ArchBig"]["age_s"] == age
    with world(d, small=broken("frames_stopped", 5000)) as (stopped, _):
        T.tick(NOW)
    assert stopped == ["b"], stopped


def t_a_healthy_or_blind_game_is_never_stopped(d):
    for state in ("ticking", "paused", "menu", "no_map", "loading", "process_gone", "could_not_look"):
        with world(d, big=W.Reading(state, "x", 73, NOW, dict(HB, silentS=9000, mainBeatMono=0))) as (stopped, signals):
            rc, _ = T.tick(NOW)
        assert (rc, stopped, signals, rows(d)) == (0, [], [], []), state
    blind = W.Reading("could_not_look", "old companion", 73)
    with world(d, big=blind):
        T.tick(NOW)
        _, got = T.tick(NOW + 500)
    assert got["games"]["ArchBig"]["blind_since"] == NOW, got


def t_a_stop_is_reported(d):
    for n, (stop, outcome, told, code) in enumerate((((0, "STOPPED x"), "stopped", 1, 0), ((1, "STOP FAILED x"), "failed", 1, 1),
                                        (GI.Refused("not confirmed"), "refused", 0, 0),
                                        (GI.Blind("no list"), "could_not_look", 0, 0), (OSError("boom"), "failed", 1, 1))):
        with world(d, big=broken("frames_stopped", 2000), stop=stop) as (_, signals):
            rc, got = T.tick(NOW + n)
        row = rows(d)[-1]
        assert len(rows(d)) == n + 1 and row["outcome"] == outcome == got["games"]["ArchBig"]["stop"], row
        assert (rc, len(signals)) == (code, told), (outcome, rc, signals)
        if told:
            assert "ArchBig" in signals[0] and "frames_stopped" in signals[0] and "stops.jsonl" in signals[0], signals
            assert Path(row["log"]).read_text() == "the log of the dead game", row
    with world(d, big=broken("frames_stopped", 2000), signal=OSError("ledger gone")) as (stopped, _):
        rc, _ = T.tick(NOW + 99)
    assert rc == 1 and stopped == ["a"] and "ledger gone" in rows(d)[-1]["signal_error"], rows(d)[-1]
    import incident
    table = incident.load_table()
    route = incident.route_of(table, T.SIGNAL)
    assert route and route["route"] == "role" and route["reader"] == "Conductor", "no route wakes the Conductor: %r" % route


def t_one_game_never_stops_the_other(d):
    with world(d, big=RuntimeError("probe"), small=broken("stuck_load", 2000)) as (stopped, _):
        rc, got = T.tick(NOW)
    assert rc == 1 and stopped == ["b"] and "probe" in got["games"]["ArchBig"]["detail"], got


def t_off_looks_and_does_not_stop(d):
    with world(d, big=broken("frames_stopped", 2000), off="family:game_watch OFF") as (stopped, _):
        _, got = T.tick(NOW)
    assert not stopped and got["games"]["ArchBig"]["not_stopped"] == "family:game_watch OFF", got
    with world(d, big=broken("frames_stopped", 2000)) as (stopped, _):
        _, got = T.tick(NOW + 5, dry=True)
        assert not stopped and T._last(T.state_dir())["at"] == NOW, "a dry tick stops and writes nothing"
    import control
    with patch.object(control, "blocked", side_effect=control.Unreadable("torn")):
        assert "torn" in T.off(), "an unreadable switch store reads off"
    with patch.object(control, "blocked", return_value=None):
        assert T.off() is None


def t_check_tells_the_cases_apart(d):
    gone = W.Reading("process_gone", "none")
    with world(d, small=gone):
        assert T.check(NOW)[0] == 1 and "no reading" in T.check(NOW)[1]
        T.tick(NOW)
        rc, text = T.check(NOW + 60)
        assert rc == 1 and "ArchSmall" in text and "ArchBig" not in text, text
    with world(d, big=gone):
        T.tick(NOW + 120)
        assert T.check(NOW + 180)[0] == 0, "a game seen before and gone now was seen"
        assert T.check(NOW + 120 + T.FRESH_S + 1)[0] == 1
        (T.state_dir() / "reading.json").write_text("{torn")
        assert T.check(NOW + 180)[0] == 2


def main():
    failed = 0
    for check in (t_a_broken_game_is_stopped, t_a_healthy_or_blind_game_is_never_stopped, t_a_stop_is_reported,
                  t_one_game_never_stops_the_other, t_off_looks_and_does_not_stop, t_check_tells_the_cases_apart):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, RM_HOST="archmagi"):
            try:
                check(d)
                print("PASS %s" % check.__name__)
            except AssertionError as e:
                failed += 1
                print("FAIL %s: %s" % (check.__name__, e))
    print("selftest_game_watch_tick: %d of 6 checks passed" % (6 - failed))
    return int(failed > 0)


if __name__ == "__main__":
    raise SystemExit(main())
