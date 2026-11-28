#!/usr/bin/env python3
r"""focus_probe.py - does a game that we launch take the foreground, or sit above his windows? The probe is the test.

RIMMANDRAKE_LAUNCH_GAME_BEHIND_HIS_WINDOWS_IT_STEALS_FOCUS. A hidden Windows process (launch_behind.CS, RmWin.Probe)
samples ten times a second, and also logs each foreground event (SetWinEventHook), from before the launch command to
after one map load:
  - the foreground window (handle, process, title);
  - each window of a watched process (RimWorldWin64, steam, steamwebhelper): its z position, whether it is new (it did
    not exist at the probe's start), and how many windows that were on screen at the start sit below it.

    python3 src/RimMandrake/Utils/focus_probe.py run --game ArchSmall [--no-map] [--out DIR]
        stop the game if it runs, start the probe, game_instance.launch(wait), wait for the main menu, load a quicktest
        map, take one screenshot through the bridge, stop the probe, judge.
    python3 src/RimMandrake/Utils/focus_probe.py judge <probe.jsonl> [--marks marks.json]   judge a record again

Take the game first: game_lock.py run <game> --for "<what>" -- python3 .../focus_probe.py run --game <game>

The verdict, the last line:
  PROBE GREEN   no sample had a new watched window in the foreground, and no foreground event of one lasted over
                FLICKER_MS (a shorter one is counted beside the verdict); no sample had a new watched window above a
                window that was on screen at the start; the screenshot after the map load has content.
  PROBE RED     a steal or a window above his windows, with the phase of the launch at which it came (fired, process
                seen, bridge up, main menu, map load, after the map); or a blank or missing screenshot.
  COULD NOT LOOK  the probe wrote no samples, or the launch failed: no verdict about the game.
Exit 0 GREEN, 1 RED, 2 COULD NOT LOOK.

A foreground change to a window that is not a new watched window (his own click) is counted as `other`, never as a steal.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import launch_behind  # noqa: E402

PERIOD_MS = 100
# A foreground event of the game that the next row (event or sample) shows already undone within this time is a
# flicker, reported beside the verdict, not a steal. 50 ms is three frames of a 60 Hz screen: a window that comes and
# goes in that time is not seen to come to the front. Danger of a larger value: a steal that he sees, read as a flicker.
# A keystroke that lands in those milliseconds still reaches the game; the verdict line counts the flickers.
FLICKER_MS = 50
# The probe's own life bound. Danger: a probe left sampling forever if this script dies before its stop file. The
# longest record is one launch and one map load: ArchSmall's small list measured about 90 s to the menu plus about 90 s
# for a quicktest map (CLAUDE.md, Facts you cannot guess); the full list's cold load about 25 min. 3 h is past 10 x the
# small run and covers the full list.
PROBE_S = 10800


def _read(path):
    rows = []
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    try:
                        rows.append(json.loads(ln))
                    except ValueError:
                        pass
    except OSError:
        pass
    return rows


def _phase(t, marks):
    ph = "before the launch"
    for name, at in sorted(((k, v) for k, v in marks.items() if v), key=lambda kv: kv[1]):
        if t >= at:
            ph = name
    return ph


def _timeline(rows, most=40):
    """Each change of the foreground, as 'seconds after the probe started: process pid title' (the first `most`)."""
    t0, last, out = rows[0]["t"], None, []
    for r in rows:
        if r.get("k") in ("s", "event"):
            fg = r.get("fg") or {}
            key = (fg.get("h"), fg.get("title"))
            if key != last:
                out.append("%.1f %s %s %s %s" % ((r["t"] - t0) / 1000.0, r["k"], fg.get("name"), fg.get("pid"),
                                                 fg.get("title")))
                last = key
    return out[:most]


def judge(rows, marks=None, shot=None):
    """rows of a probe record -> dict with verdict GREEN / RED / COULD NOT LOOK and each fault."""
    marks = marks or {}
    start = [r for r in rows if r.get("k") == "start"]
    samples = [r for r in rows if r.get("k") == "s"]
    if not start or not samples:
        return {"verdict": "COULD NOT LOOK", "why": "the probe record has %s start line and %d samples" % (
            "a" if start else "no", len(samples))}
    on0 = set(start[0].get("existed") or [w["h"] for w in start[0].get("onscreen", [])])    # every window at the start
    watch = {n.lower() for n in launch_behind.WATCH}

    def thief(fg):          # a new window of a watched process, or the game's "Not Responding" ghost (a dwm window)
        if not fg or fg.get("h") in on0 or not fg.get("h"):
            return False
        return (fg.get("name") or "").lower() in watch or (fg.get("title") or "").lower().startswith("rimworld by ludeon")

    steals, above, others = [], [], 0
    for r in samples:
        fg = r.get("fg") or {}
        if thief(fg):
            steals.append({"t": r["t"], "how": "sample", "phase": _phase(r["t"], marks), "fg": fg})
        elif fg.get("h") != (start[0].get("fg") or {}).get("h"):
            others += 1
        for w in r.get("watched", []):
            if w.get("new") and w.get("start_below", 0) > 0 and not w.get("iconic"):
                above.append({"t": r["t"], "phase": _phase(r["t"], marks), "win": w})
    seq = [r for r in rows if r.get("k") in ("s", "event", "b")]     # b: the 5 ms burst after each event
    flickers = []
    for i, r in enumerate(seq):
        if r.get("k") == "event" and thief(r.get("fg")):
            if "now" in r and not thief(r["now"]):
                ms = 0          # the event came, and the foreground was already not the game when it was read
            else:
                back = next((x["t"] for x in seq[i + 1:] if not thief(x.get("now") or x.get("fg"))), None)
                ms = (back - r["t"]) if back is not None else None
            item = {"t": r["t"], "how": "event", "phase": _phase(r["t"], marks), "fg": r["fg"], "ms": ms}
            if ms is not None and ms <= FLICKER_MS:
                flickers.append(item)
            else:
                steals.append(item)
    seen_new = any(w.get("new") for r in samples for w in r.get("watched", []))
    out = {"samples": len(samples), "span_s": round((samples[-1]["t"] - samples[0]["t"]) / 1000.0, 1),
           "steal_samples": sum(1 for s in steals if s["how"] == "sample"),
           "steal_events": sum(1 for s in steals if s["how"] == "event"),
           "above_samples": len(above), "other_fg_samples": others, "game_window_seen": seen_new,
           "flickers": len(flickers), "flicker_ms_max": max([f["ms"] for f in flickers] or [0]),
           "first_steals": sorted(steals, key=lambda s: s["t"])[:4], "first_above": above[:2],
           "timeline": _timeline(rows),
           "steal_phases": sorted({s["phase"] for s in steals}), "above_phases": sorted({a["phase"] for a in above}),
           "marks": marks, "shot": shot}
    faults = []
    if steals:
        faults.append("the game took the foreground (%d samples, %d events; phases %s)" % (
            out["steal_samples"], out["steal_events"], ", ".join(out["steal_phases"])))
    if above:
        faults.append("a new game window sat above a window of his (%d samples; phases %s)" % (
            len(above), ", ".join(out["above_phases"])))
    if not seen_new:
        out.update(verdict="COULD NOT LOOK", why="the probe never saw a new game window")
        return out
    if shot is not None and not shot.get("ok"):
        faults.append("the screenshot behind his windows has no content: %s" % shot.get("why"))
    out["verdict"] = "RED" if faults else "GREEN"
    out["why"] = "; ".join(faults) or "the game stayed behind and took no focus"
    if flickers:
        out["why"] += "; %d activation flicker(s) seen by the event hook, put back within %d ms (no sample saw one)" % (
            len(flickers), out["flicker_ms_max"])
    return out


def _shot(B):
    """One bridge screenshot -> {ok, path, bytes, why}. Content: a PNG over 50 kB (a black 1280x720 PNG is about 4 kB)."""
    try:
        r = B.call("rimworld/take_screenshot", fileName="focus_probe", suppressMessage=True) or {}
    except Exception as e:      # noqa: BLE001
        return {"ok": False, "why": "take_screenshot: %s" % e}
    p = r.get("path") or ""
    lp = p
    if os.name != "nt" and len(p) > 2 and p[1] == ":":      # under Windows Python the path is already native
        lp = "/mnt/%s/%s" % (p[0].lower(), p[3:].replace("\\", "/"))
    for _ in range(20):
        if os.path.exists(lp):
            break
        time.sleep(0.5)
    try:
        n = os.path.getsize(lp)
    except OSError:
        return {"ok": False, "path": p, "why": "no file at %s" % lp}
    return {"ok": n > 50000, "path": p, "bytes": n, "why": "%d bytes" % n}


def bridge_steps(do_map=True):
    """Under Windows Python (the bridge binds Windows loopback): wait for the main menu, load one quicktest map, take
    one screenshot -> {marks, shot}. Times are epoch ms."""
    import validation_core as vc
    marks = {}
    B = vc.Bridge()
    t0 = time.time()
    # The wait for the menu. Danger: a game whose bridge answers and never reaches the menu holds the run; the bridge's
    # start line comes with the menu (STARTUP_TIMING), so 900 s is far past 10 x any measured gap between them.
    while time.time() - t0 < 900:
        if (B.call("rimworld/get_ui_state") or {}).get("programState") == "Entry":
            break
        time.sleep(1)
    marks["main menu"] = int(time.time() * 1000)
    time.sleep(15)          # dialogs at the menu
    shot = None
    if do_map:
        marks["map load"] = int(time.time() * 1000)
        B.call("rimworld/start_debug_game_ready", timeoutMs=900000, readiness="mapData", pauseIfNeeded=True)
        marks["after the map"] = int(time.time() * 1000)
        time.sleep(10)
        shot = _shot(B)
        time.sleep(5)
    return {"marks": marks, "shot": shot}


def _bridge_steps_windows(letter, do_map):
    import subprocess
    import game_instance as gi
    env = dict(os.environ)
    out = subprocess.run([sys.executable, os.path.join(HERE, "game_instance.py"), "env", letter], capture_output=True,
                         text=True, timeout=60)
    for ln in out.stdout.splitlines():
        if ln.startswith("export ") and "=" in ln:
            k, v = ln[7:].split("=", 1)
            env[k] = v.strip("'\"")
    env["PYTHONIOENCODING"] = "utf-8"
    env["WSLENV"] = env.get("WSLENV", "") + ":PYTHONIOENCODING"
    me = subprocess.run(["wslpath", "-w", os.path.abspath(__file__)], capture_output=True, text=True,
                        timeout=60).stdout.strip()
    # Danger: a game that never answers holds the run; the steps' own waits end at 900 s each (menu, map), so 3600 s.
    r = subprocess.run(["python.exe", me, "bridge-steps"] + ([] if do_map else ["--no-map"]), env=env,
                       capture_output=True, text=True, timeout=3600, stdin=subprocess.DEVNULL)
    for ln in reversed((r.stdout or "").splitlines()):
        if ln.startswith("STEPS "):
            return json.loads(ln[6:])
    raise RuntimeError("bridge steps exit %d: %s" % (r.returncode, (r.stderr or r.stdout)[-2000:]))  # cut-ok: the tail of a failed run's own output


def run(game, out_dir, do_map=True):
    import game_instance as gi
    letter = gi.check_name(game)
    os.environ[gi.INSTANCE_ENV] = letter
    os.makedirs(out_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    rec = os.path.join(out_dir, "probe_%s_%s.jsonl" % (gi._n(letter), stamp))
    stop = rec + ".stop"
    marks = {}
    log = lambda m: print("focus_probe: %s" % m, flush=True)   # noqa: E731
    if gi.pid(letter):
        rc, text = gi.stop(name=letter, purpose="focus_probe: a cold launch to measure", wait_s=120)
        log("stop: %s" % text)
        if gi.pid(letter):
            return {"verdict": "COULD NOT LOOK", "why": "the game would not stop: %s" % text}
    pid = launch_behind._spawn_hidden(launch_behind.ps_argv("probe", launch_behind.win_path(rec), PROBE_S, PERIOD_MS,
                                                            launch_behind.win_path(stop), ",".join(launch_behind.WATCH)))
    for _ in range(300):
        if _read(rec):
            break
        time.sleep(0.2)
    if not _read(rec):
        return {"verdict": "COULD NOT LOOK", "why": "the probe (pid %s) wrote nothing to %s" % (pid, rec)}
    log("probe pid %s -> %s" % (pid, rec))
    shot, steps_error = None, None
    try:
        marks["launch fired"] = int(time.time() * 1000)
        rc, text = gi.launch(letter, wait=True)
        log("launch rc %d: %s" % (rc, text))
        marks["bridge up"] = int(time.time() * 1000)
        if rc != 0:
            return {"verdict": "COULD NOT LOOK", "why": "launch failed: %s" % text, "record": rec}
        try:
            steps = _bridge_steps_windows(letter, do_map)
        except (RuntimeError, OSError, ValueError) as e:     # the record so far still judges; the map part is unseen
            steps_error = str(e)
            log("bridge steps: %s" % e)
        else:
            marks.update(steps.get("marks") or {})
            shot = steps.get("shot")
            log("screenshot: %s" % shot)
    finally:
        with open(stop, "w") as f:
            f.write("stop")
        for _ in range(100):
            if any(r.get("k") == "end" for r in _read(rec)):
                break
            time.sleep(0.2)
    res = judge(_read(rec), marks, shot)
    res["record"] = rec
    if steps_error:
        res["steps_error"] = steps_error
        if res.get("verdict") == "GREEN":
            res.update(verdict="COULD NOT LOOK", why="the launch stayed behind, but the bridge steps failed (%s): the "
                       "main menu and the map load were not seen" % steps_error[:300])  # cut-ok: the full text is in steps_error
    with open(rec + ".marks.json", "w") as f:
        json.dump({"marks": marks, "shot": shot}, f)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--game", required=True)
    r.add_argument("--no-map", action="store_true")
    r.add_argument("--out", default=None)
    b = sub.add_parser("bridge-steps")
    b.add_argument("--no-map", action="store_true")
    j = sub.add_parser("judge")
    j.add_argument("record")
    j.add_argument("--marks", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "bridge-steps":
        print("STEPS " + json.dumps(bridge_steps(not a.no_map)))
        return 0
    if a.cmd == "run":
        res = run(a.game, a.out or os.path.join(launch_behind._storage(), "probe"), not a.no_map)
    else:
        m = {}
        if a.marks:
            with open(a.marks) as f:
                m = json.load(f)
        res = judge(_read(a.record), m.get("marks"), m.get("shot"))
    print(json.dumps(res, indent=1, default=str))
    v = res.get("verdict")
    print("PROBE %s: %s" % (v, res.get("why")))
    return {"GREEN": 0, "RED": 1}.get(v, 2)


if __name__ == "__main__":
    sys.exit(main())
