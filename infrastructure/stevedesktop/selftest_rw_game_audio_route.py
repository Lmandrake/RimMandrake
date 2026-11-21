#!/usr/bin/env python3
"""rw_game.sh up arms game_audio_route.ps1 BEFORE it starts the game, and prints the watcher's verdict
(RIMMANDRAKE_KEEP_STEVE_LANE_GAME_SOUND_OFF_SONIC_STUDIO_AT_LAUNCH). The watcher can only move a stream that exists, so
it must be compiled and polling when the game opens its audio; a watcher started after the game is a miss.
ps_q, pid_of, wait_for_pid, steam_up and the game_instance launch are stubbed; no game and no Windows are touched.
The watcher's own decision table is game_audio_route.ps1 -SelfTest (runs on Windows only)."""
import os, subprocess, sys, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SH = os.path.join(ROOT, "infrastructure/stevedesktop/rw_game.sh")
PS1 = os.path.join(ROOT, "infrastructure/stevedesktop/game_audio_route.ps1")


def fn(name):
    return subprocess.run(["sed", "-n", "/^%s() {/,/^}/p" % name, SH], capture_output=True, text=True, check=True).stdout


def run(watcher="ok", audio_to="Realtek Digital Output", named=False, result_s="3"):
    """watcher: ok (READY, then ROUTED once the game starts) | silent (never READY) | error (RESULT ERROR, no READY)
    | noresult (READY, never a RESULT). -> (stdout, exit, the order of events)."""
    bodies = [fn(n) for n in ("audio_arm", "audio_report", "up")]
    if not all(bodies):
        return "NO_FUNCTION " + " ".join(n for n, b in zip(("audio_arm", "audio_report", "up"), bodies) if not b), 99, []
    with tempfile.TemporaryDirectory() as d:
        ev = os.path.join(d, "events")
        open(os.path.join(d, "game_audio_route.ps1"), "w").write("# stub\n")
        script = f'''
HERE={d}; EV={ev}; AUDIO_TO="${{RW_GAME_AUDIO_TO-Realtek Digital Output}}"; AUDIO_LOG={d}/audio_route.log; AUDIO_PS1={d}/copy.ps1
EXE_WIN='D:\\Steam\\RimWorld\\RimWorldWin64.exe'; DIR_WIN='D:\\Steam\\RimWorld'; GI={d}/game_instance.py; NAMED={"b" if named else ""}
winpath() {{ echo "$1"; }}
named_exe_win() {{ echo 'D:\\inst\\b\\game\\RimWorldWin64.exe'; }}
ready_now() {{ grep -q ' READY ' $AUDIO_LOG 2>/dev/null && echo armed || echo unarmed; }}
game_started() {{ echo "GAME $(ready_now)" >> $EV; [ "{watcher}" = ok ] && echo "T RESULT ROUTED pid=777 t=4.2 s" >> $AUDIO_LOG; }}
ps_q() {{
  case "$1" in
    *rimmandrake*|*copy.ps1*) echo "WATCHER $1" >> $EV
       case "{watcher}" in ok|noresult) echo "T READY exe" >> $AUDIO_LOG ;; error) echo "T RESULT ERROR boom" >> $AUDIO_LOG ;; esac ;;
    *Start-Process*RimWorldWin64*) game_started ;;
  esac; }}
python3() {{ [ "$2" = launch ] && game_started; return 0; }}
pid_of() {{ echo ""; }}
wait_for_pid() {{ echo 777; }}
steam_up() {{ return 0; }}
status() {{ :; }}
sleep() {{ :; }}
{bodies[0]}
{bodies[1]}
{bodies[2]}
up; echo "rc=$?"
'''
        env = {**os.environ, "RW_AUDIO_READY_S": "3", "RW_AUDIO_RESULT_S": result_s}
        if audio_to is None:
            env["RW_GAME_AUDIO_TO"] = ""
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, env=env)
        events = open(ev).read().splitlines() if os.path.exists(ev) else []
        return r.stdout + r.stderr, r.returncode, events


fails = []
def check(name, cond, detail=""):
    if not cond:
        fails.append("%s %s" % (name, detail))

out, rc, ev = run()
check("armed before the game", [e.split()[0] + (" " + e.split()[1] if e.startswith("GAME") else "") for e in ev] == ["WATCHER", "GAME armed"], ev)
check("verdict printed", "audio route: ROUTED pid=777" in out, out)
check("up exits 0", "rc=0" in out, out)
check("watcher gets the game's exe and the endpoint", ev and "RimWorldWin64.exe" in ev[0] and "Realtek Digital Output" in ev[0], ev[:1])

out, rc, ev = run(audio_to=None)
check("off: no watcher", not any(e.startswith("WATCHER") for e in ev), ev)
check("off: says so, game still starts", "audio route: off" in out and "GAME unarmed" in ev and "rc=0" in out, out)

out, rc, ev = run(watcher="silent")
check("not armed: game still starts, says NOT ARMED, no wait for a verdict",
      "NOT ARMED" in out and "GAME unarmed" in ev and "rc=0" in out and "UNMEASURED" not in out, out)

out, rc, ev = run(watcher="error")
check("watcher error before READY: NOT ARMED with its reason", "NOT ARMED: ERROR boom" in out and "rc=0" in out, out)

out, rc, ev = run(watcher="noresult")
check("no verdict: UNMEASURED, not a pass", "audio route: UNMEASURED" in out and "ROUTED" not in out and "rc=0" in out, out)

out, rc, ev = run(named=True)
check("named game: armed before its launch, with its own exe", len(ev) == 2 and ev[1] == "GAME armed" and "inst" in ev[0], ev)
check("named game: verdict printed", "audio route: ROUTED" in out, out)

ps1 = open(PS1).read() if os.path.exists(PS1) else ""
check("watcher script exists and never clears every app's route", ps1 and "Route(" in ps1 and "ClearAll" not in ps1.replace("ClearAll...", ""),
      "(missing or calls ClearAll)")

if fails:
    print("FAIL\n" + "\n".join(fails)); sys.exit(1)
print("PASS 12 checks")
