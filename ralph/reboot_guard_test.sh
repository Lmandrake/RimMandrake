#!/bin/bash
# Test for reboot_guard with `on` stubbed: no ssh, no reboot. Run: bash ralph/reboot_guard_test.sh
cd "$(dirname "$0")/.." || exit 1
. ralph/reboot_guard.sh
fail=0
t() { # name expected-rc
    local name=$1 want=$2; reboot_guard 2>/dev/null; local rc=$?
    if [ "$rc" = "$want" ]; then echo "ok   $name"; else echo "FAIL $name: rc $rc, wanted $want"; fail=1; fi
}
on() { printf 'a  running pid 111         port 5174\nb  running pid 222         port 5175\n'; }
unset STEVE_REBOOT_BOTH; t "other instance up -> refuses" 1
on() { printf 'a  running pid 111         port 5174\nb  stopped                port 5175\n'; }
t "other instance down -> allowed" 0
on() { printf 'a  stopped                port 5174\nb  running pid 222         port 5175\n'; }
t "own down, other up -> refuses" 1
RM_GAME_INSTANCE=b t "own is b, a stopped -> allowed" 0
on() { return 255; }
t "status read fails -> refuses" 1
on() { printf ''; }
t "empty status -> refuses" 1
on() { printf 'a  running pid 111         port 5174\nb  running pid 222         port 5175\n'; }
STEVE_REBOOT_BOTH=1 t "STEVE_REBOOT_BOTH=1 -> allowed" 0
exit $fail
