#!/usr/bin/env python3
"""belt_watchdog.py - is the live-test belt HEALTHY, STALLED, WEDGED or DEAD, and what do I do about it?

    python3 src/RimMandrake/Utils/belt_watchdog.py              one line per signal + one overall verdict line
    python3 src/RimMandrake/Utils/belt_watchdog.py --json       the same as JSON
    python3 src/RimMandrake/Utils/belt_watchdog.py --watch 300  repeat every 300 s; full block only on a change
    python3 src/RimMandrake/Utils/belt_watchdog.py --run-output Transient/belt_rerun13_20261003.txt
                                                                judge one specific run-output file
    python3 src/RimMandrake/Utils/belt_watchdog.py --no-bridge  skip the python.exe bridge probe

Exit code = the overall verdict: 0 HEALTHY, 1 STALLED, 2 WEDGED, 3 DEAD.

WHY (owner, 2026-10-03: "Please engineer a system that is a bit more resistant to these kinds of hangs. We need to
get better at debugging.") One belt night lost minutes-to-hours to five hang classes, every one of which a poll of
"is the process alive" reports as fine. Runbook: design/RimMandrake/live_test_hang_runbook.md.

  1. run already dead     rerun13 died in <1 s ("could not bring RimWorld forward"); the agent polled it 5+ min
  2. frozen exception loop QuestNode_TradeRequest test-run loop, Player.log frozen at 14:59, noticed late
  3. per-frame exception   RealFoW IndexOutOfRange every Update; step_game_ticks failed on every map
  4. modal dialog          stale Dialog_ModSettings / colony-naming dialog tainted runs
  5. cold load stall / silent subagent

SIGNALS (each prints one line: LEVEL name: detail  -> remedy)
  game        RimWorldWin64 process (PowerShell Get-Process; tasklist.exe fallback), CPU seconds, Responding
  player_log  Player.log age; repeating-exception-loop detector over the tail (same normalised text N+ times)
  bridge      python.exe probe (WSL cannot reach the bridge): ping, programState, and a MAIN-THREAD call
  foreground  foreground window title vs RimWorld (RimWorld does not render unfocused -> bridge starves)
  modals      open dialogs from rimworld/get_ui_state that taint runs (naming, ModSettings, message boxes)
  runner      python processes running a live_queue job / situational_rerun (Windows + WSL)
  heartbeat   .belt_state/heartbeat_*.json (belt_heartbeat.py): stale = runner dead/frozen; finished = run OVER
  run_output  newest Transient/belt_rerun*.txt: a final UNMEASURED/MEASURED line means the run is over
  belt_logs   newest mtime of each Transient/belt_*_log_*.md (a silent subagent dies at 600 s)
  modcheck    age and status of the last live_queue result record

Read-only by construction: the bridge probe calls only ping, rimbridge/get_bridge_status and rimworld/get_ui_state.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PLAYER_LOG = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
TRANSIENT = os.path.join(ROOT, "Transient")
RESULTS = os.path.join(TRANSIENT, "modcheck", "live_queue_results.jsonl")

OK, INFO, UNKNOWN, STALLED, WEDGED, DEAD = "OK", "INFO", "UNKNOWN", "STALLED", "WEDGED", "DEAD"
RANK = {OK: 0, INFO: 0, UNKNOWN: 0, STALLED: 1, WEDGED: 2, DEAD: 3}
OVERALL = {0: "HEALTHY", 1: "STALLED", 2: "WEDGED", 3: "DEAD"}

LOG_FROZEN_S = 300          # Player.log silent this long while a run is active = suspicious
LOOP_MIN_REPEATS = 20       # same normalised error line this many times in the tail = a loop
BELT_LOG_SILENT_S = 20 * 60
RUN_RECENT_S = 3600         # a finished-UNMEASURED run older than this is history, not an alarm
NOT_RESPONDING_WEDGE_S = 240   # 'Not Responding' this long across watchdog calls = wedged, focused or not
LOAD_BUDGET_S = 25 * 60     # a cold load is ~15 min (MEASURED 2026-09-07); past this with no bridge = stalled

# Known loop signatures -> the remedy that worked (2026-10-03). First match wins.
KNOWN_LOOPS = [
    (re.compile(r"RealFoW|RealFogOfWar|nwnrealfogofwar", re.I),
     "per-frame RealFoW exception: close the game, remove mlie.nwnrealfogofwar from ModsConfig.xml, relaunch"),
    (re.compile(r"QuestNode_TradeRequest|QuestGen|TestRun", re.I),
     "quest test-run exception loop: kill RimWorld and relaunch (the game will not recover)"),
]


class Sig(object):
    def __init__(self, name, level, detail, remedy=""):
        self.name, self.level, self.detail, self.remedy = name, level, detail, remedy

    def line(self):
        return "%-7s %-10s %s%s" % (self.level, self.name, self.detail, ("  -> " + self.remedy) if self.remedy else "")

    def as_dict(self):
        return {"name": self.name, "level": self.level, "detail": self.detail, "remedy": self.remedy}


def _age(sec):
    if sec is None:
        return "?"
    sec = int(sec)
    if sec < 120:
        return "%ds" % sec
    if sec < 7200:
        return "%dm" % (sec // 60)
    return "%.1fh" % (sec / 3600.0)


# ---------------------------------------------------------------- pure analysers (selftested)

_SKIP_PREFIX = ("at ", "(Filename", "UnityEngine.", "Verse.Log:", "System.Environment:", "Rethrow as")
_ERRISH = re.compile(r"exception|error", re.I)


def normalise(line):
    s = re.sub(r"0x[0-9a-fA-F]+", "X", line.strip())
    s = re.sub(r"\d+", "N", s)
    return s[:220]


def exception_loop(text, min_repeats=LOOP_MIN_REPEATS, tail_lines=4000, recent_lines=300):
    """Find the most-repeated error-ish line in the tail. Returns dict(sig, count, share, loop, remedy) or None."""
    sigs, recent = [], set()
    lines = text.splitlines()[-tail_lines:]
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s or s.startswith(_SKIP_PREFIX) or not _ERRISH.search(s):
            continue
        if re.match(r"^[\w.`<>\[\]]+:[\w<>`.]+ ?\(", s):          # a bare stack frame "Ns.Type:Method (args)"
            continue
        sigs.append(normalise(s))
        if i >= len(lines) - recent_lines:
            recent.add(sigs[-1])
    if not sigs:
        return None
    sig, n = Counter(sigs).most_common(1)[0]
    # A loop is still going at the END of the log. A burst during the load (769x "Exception spawning loaded thing",
    # Player.log.prev) followed by normal lines is history, not a wedge.
    remedy = "kill RimWorld and relaunch; read the FIRST exception of the loop, not the loudest"
    for rx, r in KNOWN_LOOPS:
        if rx.search(sig):
            remedy = r
            break
    return {"sig": sig, "count": n, "share": round(n / float(len(sigs)), 2), "loop": n >= min_repeats and sig in recent,
            "remedy": remedy}


_VERDICT = re.compile(r"^(UNMEASURED|MEASURED (?:PASS|FAIL)) (\S+)(?: --)?(.*)$")


def run_output_state(text):
    """Parse a live_queue job's console output. Returns dict(finished, status, job, cause, last_line)."""
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    for l in reversed(lines[-12:]):
        m = _VERDICT.match(l.strip())
        if m:
            return {"finished": True, "status": m.group(1), "job": m.group(2), "cause": m.group(3).strip(),
                    "last_line": l.strip()[:300]}
    return {"finished": False, "status": None, "job": None, "cause": None,
            "last_line": (lines[-1].strip()[:300] if lines else "")}


def cause_remedy(cause):
    c = cause or ""
    if "FOCUS" in c or "bring RimWorld forward" in c:
        return "focus lost: run `python3 src/RimMandrake/Utils/game_focus.py` (or enable Options > Run in " \
               "background), then relaunch the rerun -- it is NOT running"
    if "timed out" in c and "bridge" in c:
        return "bridge main thread starved: check player_log for a loop and foreground for focus; then rerun"
    if "BUDGET" in c:
        return "a suite blew its wall-clock budget: read the heartbeat step, poke that suite alone"
    if "ClockLost" in c or "no bland map" in c:
        return "game not on a playable map: ensure_playing_map / check modals, then rerun"
    return "the run is OVER: read its cause, fix, relaunch -- stop polling it"


BAD_MODALS = re.compile(r"Dialog_NamePlayerFaction|Dialog_ModSettings|Dialog_MessageBox|Dialog_Confirm|"
                        r"Dialog_NodeTree|Dialog_Rename|Dialog_GiveName|Page_|Dialog_", re.I)
HARMLESS = re.compile(r"^(LudeonTK\.|Verse\.ImmediateWindow|RimWorld\.MainTabWindow|Verse\.EditWindow)")


def bad_windows(windows):
    out = []
    for w in windows or []:
        t = w.get("type") or ""
        if HARMLESS.search(t):
            continue
        if BAD_MODALS.search(t) or w.get("forcePause") or w.get("absorbInputAroundWindow"):
            out.append(t.split(".")[-1])
    return out


def compose(sigs):
    worst = max([RANK[s.level] for s in sigs] or [0])
    verdict = OVERALL[worst]
    lead = [s for s in sigs if RANK[s.level] == worst and worst > 0]
    if not lead:
        return verdict, "every signal OK", "carry on; re-run the watchdog in <=5 min while a run is live"
    s = lead[0]
    return verdict, "%s: %s" % (s.name, s.detail), s.remedy


# ---------------------------------------------------------------- probes (live)

_PS_PROBE = r'''
$o = @{}
$p = Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | Select-Object -First 1
if ($p) { $o.game = @{ pid = $p.Id; cpu = [math]::Round($p.TotalProcessorTime.TotalSeconds, 1);
  responding = $p.Responding; age = [int](New-TimeSpan $p.StartTime (Get-Date)).TotalSeconds;
  title = $p.MainWindowTitle; ws_mb = [int]($p.WorkingSet64 / 1MB) } }
$o.py = @(Get-CimInstance Win32_Process -Filter "Name like 'python%'" | ForEach-Object { @{ pid = $_.ProcessId; cmd = $_.CommandLine } })
$o.fg = (Get-Fg).title
$o | ConvertTo-Json -Depth 4 -Compress
'''


def probe_windows():
    """One PowerShell call: game process, python processes, foreground title. None on failure."""
    try:
        import game_focus
        raw = game_focus._ps(game_focus._PS_HELPER + _PS_PROBE)
        return json.loads(raw[raw.index("{"):])
    except Exception as e:                                      # noqa: BLE001
        try:
            out = subprocess.run(["tasklist.exe", "/FI", "IMAGENAME eq RimWorldWin64.exe", "/FO", "CSV", "/NH"],
                                 capture_output=True, text=True, timeout=30).stdout
            alive = "RimWorldWin64" in out
            return {"game": {"pid": None, "cpu": None, "responding": None, "age": None} if alive else None,
                    "py": [], "fg": None, "error": "powershell probe failed (%s); tasklist fallback" % e}
        except Exception as e2:                                 # noqa: BLE001
            return {"error": "no process probe worked: %s / %s" % (e, e2)}


def win_bridge_probe():
    """Runs UNDER python.exe (--win-probe). Prints one JSON line. Read-only tools only."""
    import rimbridge_client as rb
    out = {"ok": False}
    t0 = time.time()
    try:
        host, port, token = rb.resolve_endpoint()
        if not token:
            out["error"] = "no bridge token in Player.log"
            print(json.dumps(out))
            return
        c = rb.RimBridge(host=host, port=port, token=token, timeout=8.0, connect_timeout=4.0)
        c.connect()
        out["connect_ms"] = int((time.time() - t0) * 1000)
        out["ok"] = True

        def call(tool):
            r = c.call(tool, {})
            if isinstance(r, dict) and r.get("content"):
                try:
                    r = json.loads(r["content"][0]["text"])
                except Exception:                               # noqa: BLE001
                    pass
            return r
        try:
            st = call("rimbridge/get_bridge_status").get("state", {})
            out["state"] = {k: st.get(k) for k in ("programState", "longEventPending", "playable", "mapCount",
                                                   "paused", "automationReady")}
        except Exception as e:                                  # noqa: BLE001
            out["status_error"] = str(e)[:200]
        t1 = time.time()
        try:
            ui = call("rimworld/get_ui_state")
            out["main_ms"] = int((time.time() - t1) * 1000)
            out["windows"] = [{"type": w.get("type"), "forcePause": w.get("forcePause"),
                               "absorbInputAroundWindow": w.get("absorbInputAroundWindow")}
                              for w in ui.get("windows", [])]
        except Exception as e:                                  # noqa: BLE001
            out["main_error"] = str(e)[:200]
        try:
            c.close()
        except Exception:                                       # noqa: BLE001
            pass
    except Exception as e:                                      # noqa: BLE001
        out["error"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    print(json.dumps(out))


def probe_bridge():
    if not shutil.which("python.exe"):
        return {"error": "python.exe not on PATH (not WSL?)"}
    try:
        r = subprocess.run(["python.exe", os.path.relpath(os.path.abspath(__file__), ROOT), "--win-probe"],
                           cwd=ROOT, capture_output=True, text=True, timeout=45)
        line = [l for l in r.stdout.replace("\r", "").splitlines() if l.startswith("{")]
        return json.loads(line[-1]) if line else {"error": "no probe output: %s" % (r.stderr or "")[-200:]}
    except subprocess.TimeoutExpired:
        return {"error": "bridge probe timed out after 45 s"}
    except Exception as e:                                      # noqa: BLE001
        return {"error": "%s: %s" % (type(e).__name__, e)}


def wsl_runners():
    try:
        out = subprocess.run(["pgrep", "-af", "live_queue/|situational_rerun|modcheck.cli run"],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:                                           # noqa: BLE001
        return []
    me = str(os.getpid())
    keep = []
    for l in out.splitlines():
        parts = l.split(None, 1)
        if len(parts) < 2 or parts[0] == me or "belt_watchdog" in l or "pgrep" in l:
            continue
        m = re.match(r"^(?:/init\s+)?\S*python[\w.]*(?:\s+python[\w.]*)?\s+(.*)$", parts[1])
        if not m:                                                   # a zsh -c wrapper repeats its child: skip it
            continue
        keep.append("%s %s" % (parts[0], m.group(1)[:110]))
    return keep


def tail_text(path, nbytes=600000):
    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - nbytes))
        return f.read().decode("utf-8", "replace")


def short_cmd(cmd):
    m = re.search(r"([\w/\\.]*?(?:live_queue|modcheck)[\w/\\.]*\.py.*)$", cmd or "")
    return (m.group(1) if m else cmd or "")[-110:].replace("src/RimMandrake/Utils/", "")


def cpu_rate(game, now, state_dir=None):
    """(cores busy since the last watchdog call, seconds the window has been continuously 'Not Responding'),
    persisted in .belt_state/watchdog_last.json so one-shot calls 5 min apart still see a trend. Records this
    sample. Either value is None when there is no usable previous sample."""
    import belt_heartbeat
    d = state_dir or belt_heartbeat.STATE_DIR
    p = os.path.join(d, "watchdog_last.json")
    rate, nr_since, last = None, None, {}
    try:
        with open(p, encoding="utf-8") as f:
            last = json.load(f)
        dt = now - last["t"]
        if last.get("pid") == game.get("pid") and 5 < dt < 900 and game.get("cpu") is not None:
            rate = (float(game["cpu"]) - float(last["cpu"])) / dt
    except (OSError, ValueError, KeyError, TypeError):
        last = {}
    if game.get("responding") is False:
        nr_since = last.get("nr_since") if last.get("pid") == game.get("pid") and last.get("nr_since") else now
    try:
        os.makedirs(d, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"t": now, "pid": game.get("pid"), "cpu": game.get("cpu"), "nr_since": nr_since}, f)
    except OSError:
        pass
    return rate, (now - nr_since if nr_since else None)


# ---------------------------------------------------------------- assemble

def gather(run_output=None, bridge=True, player_log=PLAYER_LOG, now=None, win=None, br=None, hb_dir=None,
           transient=TRANSIENT, results=RESULTS, runners=None):
    now = time.time() if now is None else now
    sigs = []
    win = probe_windows() if win is None else win
    game = (win or {}).get("game")
    py = [p for p in (win or {}).get("py") or [] if p.get("cmd") and
          re.search(r"live_queue|situational_rerun|modcheck", p["cmd"]) and "belt_watchdog" not in p["cmd"]]
    if runners is None:
        runners = ["win:%s %s" % (p["pid"], short_cmd(p["cmd"])) for p in py] + ["wsl:" + l for l in wsl_runners()]

    # heartbeat
    import belt_heartbeat
    hbs = belt_heartbeat.read(state_dir=hb_dir)
    live_hb = [h for h in hbs if not h.get("finished") and h["age_s"] < belt_heartbeat.STALE_S]
    run_active = bool(runners or live_hb)

    # game process
    if not win or "error" in win and not game:
        sigs.append(Sig("game", UNKNOWN, (win or {}).get("error", "no probe"), "check Windows interop"))
    elif not game:
        sigs.append(Sig("game", DEAD, "RimWorldWin64 is NOT running",
                        "bridge holder relaunches (./game; launch via Steam); first read Player-prev.log's FIRST "
                        "exception"))
    else:
        bits = "pid %s up %s cpu %ss ws %sMB" % (game.get("pid"), _age(game.get("age")), game.get("cpu"),
                                                 game.get("ws_mb"))
        rate, nr_for = cpu_rate(game, now, hb_dir)
        if rate is not None:
            bits += " (%.2f cores since last check%s)" % (rate, ": BUSY" if rate > 0.7 else ": IDLE/FROZEN"
                                                          if rate < 0.05 else "")
        unfocused = "rimworld" not in ((win or {}).get("fg") or "rimworld").lower()
        loading = (game.get("age") or 0) < LOAD_BUDGET_S          # a cold load is legitimately unresponsive
        if game.get("responding") is False and nr_for is not None and nr_for > NOT_RESPONDING_WEDGE_S \
                and not loading:
            sigs.append(Sig("game", WEDGED, bits + " -- 'Not Responding' for %s straight%s" % (
                _age(nr_for), " at a full core: main thread in a tight loop" if (rate or 0) > 0.7 else ""),
                "hang class 2: read the Player.log tail for the last thing it did, then kill by PID and relaunch"))
        elif game.get("responding") is False and unfocused:
            sigs.append(Sig("game", STALLED, bits + " -- 'Not Responding' while UNFOCUSED",
                            "starved unless Options > Run in background is on: bring it forward (game_focus.py), "
                            "re-check in 2 min before killing anything"))
        elif game.get("responding") is False:
            sigs.append(Sig("game", WEDGED, bits + " -- window NOT RESPONDING while focused",
                            "Windows says hung: re-check in 2 min (a long event can do this), then kill by PID"))
        else:
            sigs.append(Sig("game", OK, bits))

    # player log
    try:
        log_age = now - os.path.getmtime(player_log)
        loop = exception_loop(tail_text(player_log))
        detail = "updated %s ago" % _age(log_age)
        if loop and loop["loop"]:
            # a loop that is still being written is a per-frame wedge; one in a frozen log is a hung main thread
            kind = "frozen log ending in a loop" if log_age > LOG_FROZEN_S else "repeating every frame"
            sigs.append(Sig("player_log", WEDGED, "%s; %s: %dx (%.0f%% of tail errors) %r" % (
                detail, kind, loop["count"], loop["share"] * 100, loop["sig"][:110]), loop["remedy"]))
        elif game and log_age > LOG_FROZEN_S and run_active:
            sigs.append(Sig("player_log", STALLED, detail + " while a run is active (frozen?)",
                            "probe the bridge main thread; if it times out, kill and relaunch"))
        else:
            top = (" top error %dx %r" % (loop["count"], loop["sig"][:80])) if loop else ""
            sigs.append(Sig("player_log", OK, detail + top))
    except OSError as e:
        sigs.append(Sig("player_log", UNKNOWN, "cannot read Player.log: %s" % e))

    # bridge + modals
    if bridge and game:
        br = probe_bridge() if br is None else br
    if br is None:
        sigs.append(Sig("bridge", INFO, "not probed" + ("" if game else " (no game)")))
    elif br.get("error") or not br.get("ok"):
        age = (game or {}).get("age")
        if age is not None and age < LOAD_BUDGET_S:
            sigs.append(Sig("bridge", INFO, "not answering, game up %s: still cold-loading? (%s)" % (
                _age(age), br.get("error", "")[:100]), "wait; a cold load is ~15 min"))
        else:
            sigs.append(Sig("bridge", STALLED, "not answering (%s)" % br.get("error", "")[:140],
                            "cold load stalled or bridge dead: check player_log tail, then kill and relaunch"))
    else:
        st = br.get("state") or {}
        bits = "ping %sms state %s%s" % (br.get("connect_ms"), st.get("programState") or
                                         ("? (%s)" % br.get("status_error", "")[:40]),
                                         " longEvent" if st.get("longEventPending") else "")
        if br.get("main_error"):
            sigs.append(Sig("bridge", STALLED, bits + "; MAIN THREAD call failed: %s" % br["main_error"][:100],
                            "main thread starved: fix focus, look for a loop/long event; kill if it persists >5 min"))
        else:
            sigs.append(Sig("bridge", OK, bits + "; main thread %sms" % br.get("main_ms")))
        bad = bad_windows(br.get("windows"))
        if bad:
            sigs.append(Sig("modals", WEDGED if run_active else STALLED, "open: %s" % ", ".join(bad),
                            "close them (jawa/window_list_close action=close typeName=<it>) before any run; "
                            "results taken with them open are tainted"))
        elif "windows" in br:
            sigs.append(Sig("modals", OK, "no run-tainting dialog open"))

    # foreground
    fg = (win or {}).get("fg")
    if game and fg is not None:
        if "rimworld" in fg.lower():
            sigs.append(Sig("foreground", OK, "RimWorld"))
        else:
            sigs.append(Sig("foreground", STALLED if run_active else INFO, "foreground is %r" % fg[:60],
                            "RimWorld does not render unfocused: game_focus.py, or Options > Run in background"))

    # runner + heartbeat
    sigs.append(Sig("runner", INFO, ("%d running: %s" % (len(runners), "; ".join(runners)[:200]))
                    if runners else "no live_queue runner process"))
    if not hbs:
        sigs.append(Sig("heartbeat", INFO, "no heartbeat files (runners before 2026-10-03 do not write one)"))
    for h in sorted(hbs, key=lambda h: h["age_s"])[:3]:
        name = "heartbeat"
        desc = "%s step %r" % (h.get("job"), h.get("step"))
        if h.get("finished"):
            lvl = DEAD if (h.get("status") == "UNMEASURED" and h["age_s"] < RUN_RECENT_S) else INFO
            sigs.append(Sig(name, lvl, "%s FINISHED %s %s ago: %s" % (desc, h.get("status"), _age(h["age_s"]),
                                                                       (h.get("cause") or "")[:120]),
                            cause_remedy(h.get("cause")) if lvl == DEAD else ""))
            continue
        if h["age_s"] > belt_heartbeat.STALE_S:
            sigs.append(Sig(name, DEAD if not runners else STALLED, "%s beat %s ago (stale)" % (desc, _age(h["age_s"])),
                            "runner process gone or frozen: it is NOT running; read its output, relaunch"))
            continue
        cause = belt_heartbeat.over_budget(h, now)
        step_age = now - float(h.get("step_started") or now)
        if cause:
            sigs.append(Sig(name, WEDGED, "%s; %s" % (desc, cause),
                            "the runner should have killed itself; kill it by PID and relaunch that suite alone"))
        else:
            sigs.append(Sig(name, OK, "%s for %s, beat %s ago" % (desc, _age(step_age), _age(h["age_s"]))))

    # run output
    path = run_output
    if not path:
        cands = sorted(glob.glob(os.path.join(transient, "belt_rerun*.txt")), key=os.path.getmtime)
        path = cands[-1] if cands else None
    if path and os.path.isfile(path):
        age = now - os.path.getmtime(path)
        ro = run_output_state(open(path, encoding="utf-8", errors="replace").read())
        rel = os.path.relpath(path, ROOT) if path.startswith(ROOT) else path
        if ro["finished"]:
            unm = ro["status"] == "UNMEASURED"
            lvl = DEAD if (unm and (age < RUN_RECENT_S or run_output)) else INFO
            sigs.append(Sig("run_output", lvl, "%s FINISHED %s ago: %s" % (rel, _age(age), ro["last_line"][:160]),
                            cause_remedy(ro["cause"]) if unm else "run is over; record it and start the next"))
        elif not run_active:
            sigs.append(Sig("run_output", DEAD, "%s has no verdict line and NO runner process (killed?); last: %r"
                            % (rel, ro["last_line"][:100]), "the run is dead: relaunch it -- stop polling"))
        else:
            sigs.append(Sig("run_output", OK, "%s in progress, written %s ago: %r" % (rel, _age(age),
                                                                                     ro["last_line"][:90])))
    else:
        sigs.append(Sig("run_output", INFO, "no run-output file"))

    # belt logs
    newest = {}
    for p in glob.glob(os.path.join(transient, "belt_*_log_*.md")):
        kind = os.path.basename(p).rsplit("_log_", 1)[0]
        m = os.path.getmtime(p)
        if kind not in newest or m > newest[kind][0]:
            newest[kind] = (m, p)
    for kind, (m, p) in sorted(newest.items()):
        age = now - m
        if age > 6 * 3600:
            continue
        lvl = STALLED if age > BELT_LOG_SILENT_S else OK
        sigs.append(Sig("belt_logs", lvl, "%s written %s ago" % (os.path.basename(p), _age(age)),
                        "that subagent is silent: check its notification / respawn it" if lvl != OK else ""))

    # last modcheck record
    try:
        last = None
        for line in tail_text(results, 200000).splitlines():
            if line.startswith("{"):
                try:
                    last = json.loads(line)
                except ValueError:
                    pass
        if last:
            t = time.mktime(time.strptime(last["finished"], "%Y-%m-%dT%H:%M:%S"))
            sigs.append(Sig("modcheck", INFO, "last record %s %s %s, %s ago" % (
                last.get("job"), last.get("status"), last.get("verdict") or (last.get("unmeasured_reason") or "")[:70],
                _age(now - t))))
    except (OSError, KeyError, ValueError):
        sigs.append(Sig("modcheck", INFO, "no live_queue result records"))
    return sigs


def report(sigs, as_json=False):
    verdict, cause, remedy = compose(sigs)
    if as_json:
        return json.dumps({"verdict": verdict, "cause": cause, "remedy": remedy, "when": time.strftime("%H:%M:%S"),
                           "signals": [s.as_dict() for s in sigs]}, indent=1)
    lines = [s.line() for s in sigs]
    lines.append("%s %s -- %s  -> %s" % (time.strftime("%H:%M:%S"), verdict, cause, remedy))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--watch", type=int, metavar="N", help="repeat every N seconds")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--run-output", help="judge this run-output file instead of the newest belt_rerun*.txt")
    ap.add_argument("--no-bridge", action="store_true", help="skip the python.exe bridge probe")
    ap.add_argument("--win-probe", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.win_probe:
        win_bridge_probe()
        return 0
    ro = os.path.abspath(a.run_output) if a.run_output else None
    prev = None
    while True:
        sigs = gather(run_output=ro, bridge=not a.no_bridge)
        verdict, cause, _ = compose(sigs)
        if not a.watch or a.json or (verdict, cause) != prev:
            print(report(sigs, a.json), flush=True)
        else:
            print("%s %s (unchanged)" % (time.strftime("%H:%M:%S"), verdict), flush=True)
        prev = (verdict, cause)
        if not a.watch:
            return {"HEALTHY": 0, "STALLED": 1, "WEDGED": 2, "DEAD": 3}[verdict]
        time.sleep(a.watch)


if __name__ == "__main__":
    sys.exit(main())
