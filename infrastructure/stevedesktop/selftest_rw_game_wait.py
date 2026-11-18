#!/usr/bin/env python3
"""rw_game.sh wait_for_pid polls for the game's pid instead of looking once at 5 s
(RIMMANDRAKE_WAIT_FOR_RIMWORLD_PAST_FIVE_SECONDS). pid_of is stubbed; no game is touched."""
import os, subprocess, sys, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SH = os.path.join(ROOT, "infrastructure/stevedesktop/rw_game.sh")

def run(stub, wait="6", poll="1"):
    with tempfile.TemporaryDirectory() as d:
        cnt = os.path.join(d, "n")
        body = subprocess.run(["sed", "-n", "/^wait_for_pid() {/,/^}/p", SH], capture_output=True, text=True, check=True).stdout
        if "wait_for_pid" not in body:
            return ["NO_FUNCTION"]
        script = f'CNT={cnt}; echo 0 > $CNT\nn() {{ local c=$(($(cat $CNT)+1)); echo $c > $CNT; echo $c; }}\n{stub}\n{body}\nwait_for_pid; echo "rc=$?"'
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                           env={**os.environ, "RW_START_WAIT_S": wait, "RW_START_POLL_S": poll})
        return r.stdout.split()

fails = []
def check(name, got, want):
    if got != want: fails.append(f"{name}: got {got} want {want}")

check("appears on 4th look", run('pid_of() { [ $(n) -ge 4 ] && echo 777; return 0; }'), ["777", "rc=0"])
check("never appears -> rc 1, no pid", run('pid_of() { n >/dev/null; return 0; }', wait="2"), ["rc=1"])
check("list unreadable -> rc 2", run('pid_of() { return 3; }'), ["rc=2"])
check("unreadable mid-poll -> rc 2", run('pid_of() { [ $(n) -ge 3 ] && return 3; return 0; }'), ["rc=2"])
if fails:
    print("FAIL\n" + "\n".join(fails)); sys.exit(1)
print("PASS 4 checks")
