#!/usr/bin/env python3
"""rw_game.sh down says what each stop did (RIMMANDRAKE_STOP_STEVE_GAME_FORCE_KILL_LEFT_IT_RUNNING).

2026-11-16 a Test Pilot sitting on SteveDesktop read "force stop left the game running"; a taskkill /F by hand then
killed it. down() threw away game_instance.py stop's output and exit code, and looked once, 3 s after /F. So a stop that
game_instance REFUSED (the bridge check), or that taskkill itself failed, read the same as a process that survived /F,
and a process still exiting at 3 s read as a survivor. Here down() is cut out of rw_game.sh; pid_of, sleep and the
game_instance call are stubbed and COUNTED. No game is touched."""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SH = os.path.join(ROOT, "infrastructure/stevedesktop/rw_game.sh")
FAILS = []


def run(gone_after_stops=None, gone_after_looks=None, stop_rc="0", force_rc="0", blind_at=None, wait="6"):
    """The game is gone once `gone_after_stops` stop calls were made AND `gone_after_looks` pid looks followed.
    -> (rc, stdout, number of stop calls, list of their argv)."""
    with tempfile.TemporaryDirectory() as d:
        body = subprocess.run(["sed", "-n", "/^down() {/,/^}/p", SH], capture_output=True, text=True,
                              check=True).stdout
        if "down()" not in body:
            return None, "NO_FUNCTION", 0, []
        helpers = subprocess.run(["sed", "-n", "/^gone() /p; /^look_gone() /p", SH], capture_output=True, text=True,
                                 check=True).stdout
        S, L, A = (os.path.join(d, x) for x in ("stops", "looks", "argv"))
        stub = f"""
GI=/stub/game_instance.py
echo 0 > {S}; echo 0 > {L}; : > {A}
inc() {{ local c=$(($(cat $1)+1)); echo $c > $1; echo $c; }}
sleep() {{ :; }}
pid_of() {{
    local l; l=$(inc {L})
    {"[ $l -ge %s ] && return 3" % blind_at if blind_at else ":"}
    local s; s=$(cat {S})
    if [ -n "{gone_after_stops or ''}" ] && [ "$s" -ge "{gone_after_stops or 0}" ]; then
        local since; since=$(cat {L}.mark 2>/dev/null || echo $l)
        [ -f {L}.mark ] || echo $l > {L}.mark
        [ $((l - since)) -ge {gone_after_looks or 0} ] && return 0
    fi
    echo 4242
}}
python3() {{
    [ "$1" = /stub/game_instance.py ] && [ "$2" = stop ] || {{ command python3 "$@"; return; }}
    echo "$*" >> {A}; inc {S} >/dev/null
    case " $* " in
        *" --force "*) [ "{force_rc}" = 0 ] && echo "SUCCESS: sent termination to pid 4242 (forced)" \
                       || echo "{"REFUSED: the bridge does not let this seat stop game a" if force_rc == "3" else "ERROR: Access is denied."}" >&2
                       return {force_rc} ;;
        *) [ "{stop_rc}" = 0 ] && echo "SUCCESS: sent termination to pid 4242" \
                       || echo "{"REFUSED: the bridge does not let this seat stop game a" if stop_rc == "3" else "ERROR: Access is denied."}" >&2
           return {stop_rc} ;;
    esac
}}
"""
        script = stub + helpers + body + "\ndown; echo \"rc=$?\""
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                           env={**os.environ, "RW_FORCE_WAIT_S": wait, "RW_DOWN_GRACE_S": "10"})
        out = r.stdout + r.stderr
        rc = None
        for ln in out.splitlines():
            if ln.startswith("rc="):
                rc = int(ln[3:])
        stops = int(open(S).read().strip() or 0)
        return rc, out, stops, open(A).read().splitlines()


def check(name, ok, detail):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else ": " + detail))
    if not ok:
        FAILS.append(name)


rc, out, n, argv = run(gone_after_stops=1)
check("a graceful stop that works: rc 0, one stop", rc == 0 and n == 1 and "graceful" in out, "%s %s %r" % (rc, n, out))

rc, out, n, argv = run(gone_after_stops=2, gone_after_looks=3)
check("a process still exiting a few looks after /F is waited for, not called a survivor",
      rc == 0 and n == 2 and "forced" in out, "%s %s %r" % (rc, n, out))

rc, out, n, argv = run(gone_after_stops=None, stop_rc="3")
check("a graceful stop game_instance REFUSED ends REFUSED, exit 2, with its reason, and sends no /F",
      rc == 2 and n == 1 and "REFUSED" in out and "bridge does not let" in out and "survives" not in out,
      "%s %s %r" % (rc, n, out))

rc, out, n, argv = run(gone_after_stops=None, force_rc="1")
check("a /F that taskkill itself failed names taskkill's words and its exit, not 'survives'",
      rc == 1 and n == 2 and "Access is denied" in out and "exit 1" in out, "%s %s %r" % (rc, n, out))

rc, out, n, argv = run(gone_after_stops=None)
check("a process that outlives a /F taskkill reported sent: FAILED survives, with taskkill's words",
      rc == 1 and n == 2 and "survives" in out and "SUCCESS: sent termination" in out, "%s %s %r" % (rc, n, out))

rc, out, n, argv = run(gone_after_stops=None, blind_at=4)
check("a game list that goes unreadable after the stop is UNMEASURED, never 'survives' or 'stopped'",
      rc == 2 and "UNMEASURED" in out and "survives" not in out and "stopped (" not in out, "%s %s %r" % (rc, n, out))

print("%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
