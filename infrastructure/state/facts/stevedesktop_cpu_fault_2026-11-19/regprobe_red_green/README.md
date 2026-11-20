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

## The first live fault (2026-11-20 20:13Z, the probe's second live cycle)

`live_first_fault_20261120T201337Z.log` holds its 32 RPFAULT lines [measured]. Boot 20:05:07Z, 0.14 h up, game lane running
(RimWorldWin64, WSL2 `vmmem`); no Prime95, no `stevecheck` at that moment. The watch flagged the same CPU first
(`watch.log` 20:13:01Z `bad_cpus=[0]`, `watch-chk.log` mismatches from 20:11:46Z, vcore max 1.302 V on that cycle).

- `RPCYCLE ... result=fault cpus_measured=18/18 holds=396 bad_holds=16 bad=[0:upper_half_loss]`: every one of the 16 AVX holds
  on logical CPU 0 was wrong, steady holds (14 ms, 0 churn wakes) and churn holds (16 ms, 10 wakes) alike; the other 17 CPUs
  and every SSE and scalar hold on CPU 0 were right.
- In each logged hold, all 16 YMM registers kept bits 0-127 exactly and read 0 in bits 128-255 (`detail=zero`): the shape
  appendix C of `REPORT.md` inferred from the watch's wrong results, now seen in the registers themselves.
- That every 14 ms hold lost all 16 upper halves means the zeroing happened at least once per ~14 ms on that CPU while the
  probe thread ran, without the probe's own context switches [measured]; it suggests something that runs on CPU 0 often
  (interrupt or deferred-call work, or a state restore on return to the thread) rather than wrong arithmetic [guess ~60%].
