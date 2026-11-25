#!/bin/bash
# Acceptance test for RIMMANDRAKE_STOP_FLOWWORKS_ORDERS_WAITING_OUT_A_PAUSED_CLOCK. Exit 0 = pass, 1 = fail, 2 = could not look,
# 3 = empty set (no FlowWorks order call in the window: no visit to read).
# Usage: bash <this file> [--since <local ISO time>]  |  --selftest
# The bar: FlowWorks order calls (jawa/ordered_job, jawa/order_pawn from concept_scenes.py, extension_proof.py,
# live_session.py) over 3 s whose 5 s tick windows show 0 ticks: limit 0. The reader joins the bridge log to the tick
# windows of the game that served each call (src/RimMandrake/Utils/telemetry/clock_still_waits.py).
# Readings (2026-11-25): visit 9 (ArchSmall, 2026-11-23 14:32 to 17:31) reads 32 calls / 614 s, exit 1 (red). From
# 2026-11-24 06:00 (FlowWorks visit 10 and later) it reads 0 of 192 long order calls, exit 0. The cause of the change is
# the C# wait (JawaBenchWaitCore.End, 7aa1752ee4): a wait ends after one poll when the clock stands paused.
# The old offline proxy (every call site passes waitTicks=0) is retired: the call-site literal no longer decides the bar.
cd "$(dirname "$0")/../../.." || exit 2
R=src/RimMandrake/Utils/telemetry/clock_still_waits.py
if [ "$1" = "--selftest" ]; then exec python3 "$R" --selftest; fi
SINCE=2026-11-24T06:00
if [ "$1" = "--since" ] && [ -n "$2" ]; then SINCE=$2; fi
exec python3 "$R" --since "$SINCE" --limit 0
