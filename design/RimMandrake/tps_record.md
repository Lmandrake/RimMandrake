# The TPS record — TPS is measured all the time

Item: `BRIDGE_TPS_REGULAR_REPORT_1`. Owner, 2026-10-10: he regularly sees very slow (and fast) TPS,
and agents asked to investigate later say they cannot reproduce it. So TPS is a standing
measurement, not an investigation.

## Where it lives

| what | where |
|---|---|
| the record (rolling JSONL, outside git) | `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\tps\tps.jsonl` |
| older half | `...\JawaBench\tps\tps.1.jsonl` (rotated at 1 MB, so 2 MB total at most, roughly 2 × 3,500 samples ≈ 10 hours of play) |
| sampler | `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTpsSampler.cs` (JawaBench companion) |
| maths | `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTpsMath.cs`, with a Python port in `src/RimMandrake/Utils/tps_record.py` |
| offline selftest | `python3 src/RimMandrake/Utils/selftest_tps_record.py`: Python checks, then the production C# built via winbuild (`bridgetools/TpsMathSelfTest`), with every answer compared line for line |
| live tool | `jawa/tps_report` (`last` = N samples, default 60 = 5 min, max 720 = 1 h in memory) |
| watchdog line | `python3 src/RimMandrake/Utils/belt_watchdog.py` prints a `tps` signal |

## How to read it

```
python3 src/RimMandrake/Utils/tps_record.py              # verdict over the last 5 minutes
python3 src/RimMandrake/Utils/tps_record.py --last 60    # plus the last 60 samples
python3 src/RimMandrake/Utils/tps_record.py --window 3600 --json
```

It runs from WSL and reads the file directly, so it needs no bridge and works with the game down.
That makes it the right instrument for "he said it was slow an hour ago".

One sample is one line, written every **5 real seconds** while a game is being **played**
(nothing is written at the main menu or during a long event):

| field | meaning |
|---|---|
| `utc`, `session` | sample time; `session` changes per game process |
| `tg` | `TicksGame` at the end of the window |
| `dReal`, `dTicks` | the window: real seconds, game ticks |
| `tps` | `dTicks / dReal` |
| `speed` | `TimeSpeed` setting at window end (`Paused`, `Normal`, `Fast`, `Superfast`, `Ultrafast`) |
| `mult` | the **effective** `TickManager.TickRateMultiplier` (1 / 3 / 6, or 12 when superfast and nothing is happening, 15 / 150 for Ultrafast, 1 under forced-normal-speed, 0 paused) |
| `target` | `60 × mult`: what the engine is trying to reach |
| `ratio` | `tps / target`. **This is the number to judge** |
| `state` | `run`, `paused` (≥ 50 % of frames paused, or mult 0), or `mixed` (the speed setting changed inside the window) |
| `pausedFrac`, `frames`, `fps` | paused share, frame count, frames per real second |
| `frameMaxMs` | the worst single frame in the window (`Time.unscaledDeltaTime`): hitches show here |
| `tickMs` | `TickManager.MeanTickTime`, the engine's own smoothed ms per tick |
| `gc0` | gen-0 garbage collections in the window. A collection can pause the main thread, so a burst of them beside a fat `frameMaxMs` is a lead on a hitch |

🔑 **Judge `ratio`, never `tps` against 60.** 170 TPS is healthy at speed 3 (target 180) and
dire at speed 4 (target 900). Only `state: run` samples are judged. `paused` and `mixed` are
recorded and never called slow.

⚠️ The engine caps ticks per frame at `2 × mult` and stops ticking after ~45 ms of tick work per
frame (`TickManager.TickManagerUpdate`). So at high speeds `ratio` falls when the **frame rate**
falls, not only when ticks get expensive. Read `fps` and `tickMs` next to it: low `fps` with
small `tickMs` points at rendering, while large `tickMs` points at simulation cost.

## Judgement (watchdog and tool)

- **SUSTAINED LOW**: the last 6 run samples (30 s) all have `ratio < 0.6`. The watchdog shows WARN.
- **SUSTAINED HIGH**: the last 6 run samples all have `ratio > 1.15`. Ticks are being produced faster
  than the setting asks for, so suspect a mod or a misread multiplier. The watchdog shows WARN.
- The `tps` line **never changes the watchdog's overall verdict**, because slow is not hung.
- `UNKNOWN`: no record at all. `INFO`: there is a record but no sample in the last 5 minutes (the
  game is not being played, or the sampler has not started).

## Trap: the sampler starts lazily

The companion's code first runs on the **first `jawa/` call of a session**
(`JAWABENCH_INIT_LINE_IS_LAZY_1`). Play before that call is **not sampled**. `jawa/tps_report`
returns `samplerStartedUtc`. The watchdog's bridge probe calls `jawa/tps_report`, so any watchdog
run with the bridge up starts the sampler. A gap in the record means the sampler was not running.
It never means "TPS was fine".

## Cost

Sampling is a Harmony postfix on `TickManager.TickManagerUpdate`, the once-per-frame play update on
the main thread. Each frame costs a few field reads and one compare. The sample maths runs once
per 5 s, and the file append goes to the thread pool. If the postfix throws, it disables itself
and reports `runtimeError` through the tool instead of retrying every frame.
