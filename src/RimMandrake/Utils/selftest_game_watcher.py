#!/usr/bin/env python3
"""Offline game watcher acceptance. Every process, bridge, stop and clock is faked."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import call, patch

import game_instance as GI
import selftest_scene_library as scenes

try:
    import game_watcher as W
except ModuleNotFoundError as e:
    if e.name != "game_watcher":
        raise
    W = None

NOW = 1795470000.0
START = NOW - 3600
PID = 73
PROC = {"pid": PID, "start": START}
HB = dict(pid=PID, session="abc", procStartUtc="2026-11-23T20:40:00.000Z", hbSeq=42,
          watchdogMono=3600, mainBeatMono=3599, silentS=1, phase="frame-rest", ticksGame=58,
          scene="map", sceneSinceMono=3300, paused=False, lastTickMono=3599,
          frames=2000, frameFaultStreak=0)
# WriteHeartbeat and HealthFields as of 267b0888a4, before the watcher fields.
DEPLOYED_SESSION = "0123456789abcdef0123456789abcdef"
DEPLOYED_HB = dict(pid=PID, session=DEPLOYED_SESSION, procStartUtc="2026-11-23T20:40:00.000Z", hbSeq=42,
                   utc="2026-11-23T21:40:00.000Z", mono=3600, watchdogUtc="2026-11-23T21:40:00.000Z",
                   watchdogMono=3600, mainBeatUtc="2026-11-23T21:39:59.000Z", mainBeatMono=3599,
                   silentS=1, phase="frame-rest", ticksGame=58,
                   segment="tps_20261123T204100Z_%s_%d_000.jsonl" % (DEPLOYED_SESSION, PID),
                   hbErrors=0, hbLastError=None, wq=0, wfly=0, wdrop=0, wdropCrit=0, werr=0, wtorn=0)


def write(d, hb, age=0):
    p = Path(d) / ("hb_%s.json" % hb["session"])
    p.write_text(json.dumps(hb), encoding="utf-8")
    os.utime(p, (NOW - age, NOW - age))
    return p


def read(d, state, why):
    assert W is not None, why + ": game_watcher is missing"
    r = W.read("a", d, now=NOW)
    assert r.state == state, "%s: expected %s, got %s (%s)" % (why, state, r.state, r.detail)
    return r


def writing_site(path):
    return (Path(__file__).resolve().parent.parent / "bridgetools" / "JawaBench.BridgeTools" / path).read_text()


def t_ticking(d):
    write(d, HB)
    read(d, "ticking", "recent tick progress")
    write(d, dict(HB, lastTickMono=0))
    read(d, "could_not_look", "an unpaused map with no recent tick progress")
    assert 'lastTickMono' in writing_site("JawaBenchTpsWatchdog.cs"), "the disk writer does not publish tick progress"


def t_paused(d):
    hb = dict(HB, paused=True, ticksGame=0, lastTickMono=None)
    write(d, hb)
    read(d, "paused", "a healthy pause at tick zero")
    write(d, hb, age=90)
    read(d, "could_not_look", "a stale paused heartbeat must never be paused")


def t_ordinary_stop_matches_parent():
    """CLI bytes captured on 267b0888a4, with a fixed terminal width."""
    def cli(*args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = GI.main(["stop", *args])
            except SystemExit as e:
                rc = e.code
        return rc, out.getvalue().encode(), err.getvalue().encode()

    usage = (b"usage: game_instance.py stop [-h] [--force] [--instance INSTANCE]\n"
             b"                             [--for PURPOSE] [--despite-hold DESPITE]\n"
             b"                             [pid]\n")
    help_text = usage + (
        b"\npositional arguments:\n  pid\n\noptions:\n"
        b"  -h, --help            show this help message and exit\n"
        b"  --force\n  --instance INSTANCE\n"
        b"  --for PURPOSE         what the stop is for (the bridge check records it)\n"
        b"  --despite-hold DESPITE\n                        act on a held game on purpose: why\n")
    unknown = (b"usage: game_instance.py [-h]\n"
               b"                        {env,pid,prepare,install,launch,stop,status,free,leftovers} ...\n"
               b"game_instance.py: error: unrecognized arguments: --b\n")
    with patch.dict(os.environ, COLUMNS="80", NO_COLOR="1", RM_GAME_INSTANCE="a"), \
         patch.object(W, "confirm", return_value=(W.Reading("paused", "fake reading"), False)) as confirm, \
         patch.object(GI, "hold_refusal", return_value=None) as hold, \
         patch.object(GI, "bridge_refusal", return_value=None) as bridge, \
         patch.object(GI, "_exe", return_value="taskkill.exe"), \
         patch.object(GI, "_run", return_value=SimpleNamespace(returncode=7, stdout="first\n", stderr="second\n")) as kill:
        help_observed, alias_observed = cli("--help"), cli("--b")
        assert (help_observed, alias_observed) == ((0, help_text, b""), (2, b"", unknown)), (
            "ordinary stop help or --b differs from parent (help exit %d, --b exit %d)" %
            (help_observed[0], alias_observed[0]))
        for arg, label in ((["xyz"], b"'xyz'"), (["--", "--broken"], b"'--broken'")):
            err = usage + b"game_instance.py stop: error: argument pid: invalid int value: " + label + b"\n"
            assert cli(*arg) == (2, b"", err), "ordinary stop parse error differs from parent: %r" % arg
        assert cli() == (7, b"first\nsecond\n", b""), "ordinary stop result differs from parent"
        kill.assert_called_once_with(["taskkill.exe", "/PID", str(PID)])
        kill.reset_mock()
        assert cli(str(PID), "--force", "--for", "a reason", "--despite-hold", "permission") == (7, b"first\nsecond\n", b"")
        hold.assert_called_with("a", "permission")
        bridge.assert_called_with("a", "a reason", seat=None, despite="permission")
        kill.assert_called_once_with(["taskkill.exe", "/F", "/PID", str(PID)])
        kill.reset_mock()
        hold.return_value = "held"
        assert cli() == (3, b"", b"REFUSED: held\n")
        hold.return_value, bridge.return_value = None, "busy"
        assert cli() == (3, b"", b"REFUSED: busy\n")
        with patch.object(GI, "procs", return_value=[]):
            assert cli("--instance", "b", str(PID)) == (3, b"", b"REFUSED: pid 73 is not ArchSmall's (ArchSmall: not running)\n")
            assert cli("--instance", "b") == (0, b"ArchSmall is not running\n", b"")
        with patch.object(GI, "procs", side_effect=GI.Blind("probe failed")):
            assert cli() == (2, b"", b"BLIND: probe failed\n")
        kill.assert_not_called()
        confirm.assert_not_called()


def t_frames_stopped(d):
    hb = dict(HB, paused=True, mainBeatMono=3500, silentS=100)
    write(d, hb)
    first = read(d, "frames_stopped", "a fresh writer sees stopped frames despite the last pause flag")
    write(d, dict(hb, hbSeq=43, watchdogMono=3610, silentS=110))
    second = read(d, "frames_stopped", "the same main-thread stall still holds")
    too_early = 1
    recovered = SimpleNamespace(state="paused", detail="frames recovered")
    for name, latest, elapsed, proc, code in (
        ("ArchBig", first, 10, PROC, 3),
        ("ArchBig", second, too_early, PROC, 3),
        ("ArchBig", recovered, 10, PROC, 3),
        ("ArchBig", second, 10, dict(PROC, start=START + 60), 3),
        ("ArchBig", second, 10, PROC, 0),
        ("ArchSmall", second, 10, PROC, 1),
    ):
        output = io.StringIO()
        answer = SimpleNamespace(returncode=2 if code == 1 else code, stdout="fake taskkill result", stderr="")
        with patch.object(W, "read", side_effect=[first, latest]) as sample, \
             patch.object(W.time, "sleep"), patch.object(W.time, "monotonic", side_effect=[0, elapsed]), \
             patch.object(GI, "procs", return_value=[proc]), patch.object(GI, "_exe", return_value="taskkill.exe"), \
             patch.object(GI, "_run", return_value=answer) as kill, \
             patch.object(GI, "hold_refusal", side_effect=AssertionError("confirmed emergency must reach any game")), \
             patch.object(GI, "bridge_refusal", side_effect=AssertionError("watcher contacted the bridge")), \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            rc = GI.main(["stop", "--broken", "--instance", name])
        assert rc == code and sample.call_count == 2, output.getvalue()
        if code == 3:
            kill.assert_not_called()
        else:
            kill.assert_called_once_with(["taskkill.exe", "/F", "/PID", str(PID)])
            report = output.getvalue()
            assert name in report and "frames_stopped" in report and "hb_abc.json" in report, report
            assert ("FAILED" if code else "STOPPED") in report, report
    output = io.StringIO()
    with patch.object(W, "confirm", return_value=(second, True)), patch.object(GI, "_exe", return_value="taskkill.exe"), \
         patch.object(GI, "_run", side_effect=OSError("taskkill unavailable")), contextlib.redirect_stdout(output):
        try:
            rc = GI.main(["stop", "--broken", "--instance", "ArchBig"])
        except OSError as e:
            raise AssertionError("a stop launch failure went unreported: %s" % e) from e
    assert rc == 1 and "STOP FAILED ArchBig" in output.getvalue(), output.getvalue()
    t_ordinary_stop_matches_parent()


def t_frame_exceptions(d):
    write(d, dict(HB, frames=2100, frameFaultStreak=1, frameFaultSinceMono=3599))
    read(d, "ticking", "an isolated throwing frame is not an exception on every frame")
    write(d, dict(HB, frames=2100, frameFaultStreak=100, frameFaultSinceMono=3590))
    first = read(d, "frame_exceptions", "every completed frame has thrown since the last good one")
    for streak, expected in ((150, True), (2, False)):
        write(d, dict(HB, hbSeq=44, watchdogMono=3610, mainBeatMono=3609, frames=2150, frameFaultStreak=streak,
                      frameFaultSinceMono=3590 if expected else 3603))
        second = read(d, "frame_exceptions", "a frame exception streak is still visible")
        with patch.object(W, "read", side_effect=[first, second]), patch.object(W.time, "sleep"), \
             patch.object(W.time, "monotonic", side_effect=[0, 10]):
            assert W.confirm("a")[1] is expected, "a good frame between readings must break confirmation"
    assert "WD.FrameEnded(__exception != null);" in writing_site("JawaBenchTpsSampler.cs"), "Root.Update does not report its result"
    assert "JawaBenchTpsWatchdog.NoteRootException(text);" in writing_site("JawaBenchFirstException.cs"), (
        "the measured Root.Update exception caught by Verse never reaches the watcher")


def t_stuck_load(d):
    write(d, dict(HB, scene="loading", sceneSinceMono=3550))
    read(d, "loading", "a recent load can still finish")
    write(d, dict(HB, scene="loading", sceneSinceMono=2950))
    first = read(d, "stuck_load", "frames advance but map initialization has not ended")
    write(d, dict(HB, scene="loading", sceneSinceMono=2950, hbSeq=44, watchdogMono=3610, mainBeatMono=3609))
    second = read(d, "stuck_load", "a new heartbeat shows the same load")
    with patch.object(W, "read", side_effect=[first, second]), patch.object(W.time, "sleep"), \
         patch.object(W.time, "monotonic", side_effect=[0, 10]):
        assert W.confirm("a")[1], "the same stuck load must confirm"
    write(d, dict(HB, phase="load", mainBeatMono=2950, silentS=650))
    read(d, "stuck_load", "the main thread is stuck within the load")


def t_menu(d):
    write(d, dict(HB, scene="menu"))
    read(d, "menu", "the menu has no map but is responsive")
    src = writing_site("JawaBenchTpsSampler.cs")
    assert "WD.SetScene(" in src and "ProgramState.Entry" in src and "game.CurrentMap" in src, "Root.Update does not sample the actual scene"


def t_no_map(d):
    write(d, dict(HB, scene="no_map"))
    read(d, "no_map", "a responsive game world has no current map")


def t_process_gone(d):
    write(d, HB)
    with patch.object(GI, "procs", return_value=[]):
        read(d, "process_gone", "the measured list is empty despite a heartbeat on disk")


def t_never_start_on_a_broken_game(d):
    f = scenes.world()
    health = SimpleNamespace(state="frames_stopped", detail="main thread stopped")
    with patch.object(f, "game_health", return_value=health, create=True), \
         patch.object(f, "connect", side_effect=AssertionError("scene.open connected to a broken game")):
        scenes.refused("GAME_BROKEN", scenes.scene.open, "ArchSmall")
    assert f.lock is None
    f.game.fail["tools/list"] = "fake tool list failure"
    with patch.object(f, "game_health", return_value=W.Reading("could_not_look", "no heartbeat")):
        scenes.faulted("COULD_NOT_LOOK", scenes.scene.open, "ArchSmall")
    del f.game.fail["tools/list"]
    _, s = scenes.opened(f)
    with patch.object(f, "game_health", return_value=health, create=True):
        before = list(f.game.log)
        scenes.refused("GAME_BROKEN", s.run, until=scenes.c.ticks(1), limit=1)
        assert f.game.log == before, "s.run contacted the broken game"
    s.close()


def admission_snapshot(open_dir, run_dir):
    f = scenes.world()
    # Keep ids fixed so the receipts, trace and bridge arguments compare directly.
    with patch.object(scenes.scene.uuid, "uuid4", return_value=SimpleNamespace(hex="0123456789abcdef")), \
         patch.object(f, "game_health", scenes.scene_world.RealWorld().game_health), \
         patch.object(W, "record_dir", side_effect=[open_dir, run_dir]) as sample, \
         patch.object(GI, "bridge_refusal", side_effect=AssertionError("admission asked the bridge")), \
         patch.object(scenes.scene_world, "RealBridge", side_effect=AssertionError("admission built a bridge")), \
         patch.object(W.time, "time", return_value=NOW):
        with scenes.scene.open("ArchSmall") as s:
            r = s.run(until=scenes.c.ticks(1), limit=1)
            raw = f.files.pop(s.run_dir + "/receipts.jsonl")
            receipts = [s.receipt.as_dict(), r.receipt.as_dict()]
            assert [json.loads(line) for line in raw.splitlines()] == receipts, "saved and returned receipts differ"
            assert sample.call_args_list == [call("b"), call("b")], "expected one disk reading per entry point"
            return receipts, (s.opened, repr(r), list(f.game.log), dict(f.files))


def t_blind_admission_records_once(d):
    healthy = Path(d) / "healthy"
    healthy.mkdir()
    write(healthy, dict(HB, paused=True))
    control, control_effects = admission_snapshot(healthy, healthy)
    failures = []
    for fixture in ("deployed", "missing", "unreadable"):
        blind = Path(d) / fixture
        blind.mkdir()
        if fixture == "deployed":
            write(blind, DEPLOYED_HB)
        if fixture == "unreadable":
            write(blind, HB).write_bytes(b"\xff")
        reading = read(blind, "could_not_look", fixture)
        for i, entry in enumerate(("scene.open", "s.run")):
            dirs = [healthy, healthy]
            dirs[i] = blind
            try:
                receipts, effects = admission_snapshot(*dirs)
            except scenes.scene.Fault as e:
                failures.append("%s %s raised %s" % (fixture, entry, e.name))
                continue
            assert effects == control_effects, "%s %s changed scene behavior" % (fixture, entry)
            notes = receipts[i]["could_not_look"]
            note = "ArchSmall game watcher: " + reading.detail
            assert notes.count(note) == 1, "%s %s did not record one watcher line: %r" % (fixture, entry, notes)
            notes.remove(note)
            assert receipts == control, "%s %s changed other receipt fields" % (fixture, entry)
    assert not failures, "; ".join(failures)


def t_could_not_look(d):
    p = write(d, HB)
    p.write_bytes(b"\xff")
    read(d, "could_not_look", "an unreadable heartbeat must never be ticking")
    p.unlink()
    read(d, "could_not_look", "the heartbeat directory is measured empty")
    write(d, dict(HB, scene=None))
    read(d, "could_not_look", "legacy or incomplete heartbeat fields")
    write(d, HB)
    with patch.object(GI, "procs", return_value=[dict(PROC, start=START + 60)]):
        read(d, "could_not_look", "a heartbeat from a reused PID")
    with patch.object(GI, "procs", side_effect=GI.Blind("process probe failed")):
        read(d, "could_not_look", "a failed process probe is not process gone")
    out = io.StringIO()
    with patch.object(W, "record_dir", return_value=d), patch.object(W.time, "time", return_value=NOW), \
         contextlib.redirect_stdout(out):
        assert W.main(["ArchBig"]) == 0
    assert json.loads(out.getvalue())["state"] == "ticking", out.getvalue()
    t_blind_admission_records_once(d)


def main():
    passed = 0
    for check in (t_ticking, t_paused, t_frames_stopped, t_frame_exceptions, t_stuck_load, t_menu,
                  t_no_map, t_process_gone, t_never_start_on_a_broken_game, t_could_not_look):
        with tempfile.TemporaryDirectory() as d, patch.object(GI, "procs", return_value=[PROC]), \
             patch.dict(os.environ, RM_HOST="archmagi"):
            try:
                check(d)
            except AssertionError as e:
                print("FAIL %s: %s" % (check.__name__, e))
            else:
                passed += 1
                print("PASS %s" % check.__name__)
    print("selftest_game_watcher: %d checks passed" % passed)
    return int(passed != 10)


if __name__ == "__main__":
    raise SystemExit(main())
