# Register probe: RED and GREEN on SteveDesktop (2026-11-20)

Item `RIMMANDRAKE_BUILD_STEVE_REGISTER_PROBE_SEES_UPPER_HALF_LOSS`. Probe source: `src/RimMandrake/Utils/steve_cpu_retest/regprobe.c`
and `regprobe_asm.S`; reader: `src/RimMandrake/Utils/testq/regprobe_log.py`. Both runs: `regprobe.py once <build>` on
SteveDesktop, boot 2026-11-20 20:05:07Z, game lane running, into test logs (never the live log).

| file | build | result [measured] |
|---|---|---|
| `red_inject_vzeroupper.log` | `-DRP_FORCE_INJECT=1` (VZEROUPPER in every real AVX hold) | `result=fault cpus_measured=18/18 bad_holds=288`: every AVX hold on all 18 logical CPUs (16 per CPU, steady and churn), 576 RPFAULT lines, all `class=upper_half_loss detail=zero`, lower 128 bits right, upper 128 bits zero; exit 1 |
| `green_normal.log` | normal | `result=clean cpus_measured=18/18 holds=396 bad_holds=0`; exit 0 |

Both starts' CONTROL lines read `upper_seen=1 lower_seen=1 sse_seen=1 scalar_seen=1 clean_seen=1 ok=1`.
`selftest_regprobe.py` parses these two files as the reader's real-format fixtures.
