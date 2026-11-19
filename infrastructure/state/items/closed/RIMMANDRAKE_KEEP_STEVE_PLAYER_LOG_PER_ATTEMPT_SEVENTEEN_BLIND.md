# RIMMANDRAKE_KEEP_STEVE_PLAYER_LOG_PER_ATTEMPT_SEVENTEEN_BLIND

SteveDesktop's worker (`infrastructure/stevedesktop/worker.py`) keeps no `Player.log` in a finished attempt's directory,
and the result note it writes ("modcheck exit 1 and no sheet JSON: <...>") is the TAIL of modcheck's output. So the
first cause of an INVALID is lost once the next load overwrites the log. Measured in the
RIMMANDRAKE_STOP_STEVEDESKTOP_INVALID_RUNS_REPEATING_UNFIXED census (2026-11-14): 2 of the 96 INVALID attempts since
11-06 hold a Player.log; 17 "quicktest world start FAILED ... readiness 'mapData'" deaths have no recorded first cause
(two were traced to the HAR ctor only by a live sitting, RIMMANDRAKE_DIAGNOSE_HAR_CTOR_TOKEN_ZERO). Graffiti's three
`REFUSED: validated must-show lines ...` deaths read UNKNOWN from the queue because the tail cut the REFUSED line off.

## fix

1. On every non-DONE attempt, copy the game's Player.log (or its first 2000 lines plus every line from the first
   exception on) into the attempt dir before the next start.
2. Lead the result note with modcheck's first `REFUSED:` or exception line, then the tail.

## acceptance test

On SteveDesktop, for every INVALID attempt finished after the fix:

    ssh stevedesktop-wsl 'cd /mnt/d/RimTest/testq/attempts && for d in $(ls -t | head -40); do grep -q "\"outcome\": \"INVALID\"" $d/result.json 2>/dev/null && { [ -f $d/Player.log ] || echo MISSING $d; }; done'

prints no line for an attempt newer than the fix. Today it prints MISSING for nearly every one (watched 2026-11-14).
Offline: `python3 src/RimMandrake/Utils/testq/invalid_class.py --since <fix time>` shows no UNKNOWN row whose attempt's
modcheck.log carries a `REFUSED:` line.
