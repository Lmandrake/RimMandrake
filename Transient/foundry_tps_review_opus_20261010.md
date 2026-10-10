# TPS record review (Opus, 2026-10-10)

Reviewer: independent, read-only. Subject: BRIDGE_TPS_REGULAR_REPORT_1 (3e0322c4e, f43276f47).
Engine facts below are from the decompiled 1.6 source via RimSage (`Verse/TickManager.cs`,
`Verse/Root_Play.cs`, `Verse/Prefs*.cs`), not from the doc.

## Verdict

**Not yet meeting the owner's goal.** The maths is tidy and the reader works, but three things
defeat "capture the slow TPS he sees in play":

1. **His solo play is not sampled at all** unless an agent happens to call a `jawa/` tool that session.
2. **The worst events are thrown away**: a stall over 60 s is dropped, and a hang or crash leaves no record.
3. **`ratio` is misjudged in common play**: Superfast flips between 6x and 12x, combat forces normal
   speed, and partial pauses dilute the window. Each of these produces false SUSTAINED LOW/HIGH
   readings, and the selftest locks in one of them.

The doc cannot answer "was it slow at 21:30, and why". There is no time query, it is UTC only, and
the record holds no context columns. Record not yet deployed (`...\JawaBench\tps\` does not exist),
so nothing here was measured live.

## Findings, ranked

### 1. HIGH: the owner's own play is never sampled (design misses the goal)
- **Where:** `JawaBenchTpsSampler.cs:13-16, 71-103`. Install is called only from `JawaBenchInit.Announce`
  (first `jawa/` call) and `TpsReport` (`:303`). `bridgetools/build.py:6-9`: the companion is
  "Not a mod... RimBridgeServer loads it late". Discovery is metadata reflection, so no code runs at load.
- **Scenario:** He launches and plays for an evening, no agent touches the bridge, and TPS crawls.
  The record is empty, and the watchdog says `UNKNOWN`/`INFO`. This is exactly the "cannot reproduce" case
  the item exists to end. `belt_watchdog.py` is the only automatic starter, and it runs only inside
  agent belt sessions (`infrastructure/agents/FOUNDRY.md:170-178`), not on a timer.
- **Fix (any one, in order of robustness):**
  (a) Move the sampler (with `JawaBenchTpsMath.cs`) into a real always-loaded RimMandrake mod assembly
  and install it from `[StaticConstructorOnStartup]`, so it runs from load with no bridge.
  (b) Check the RimBridgeServer SDK for a companion startup or registration hook that executes code.
  (c) Stopgap: have the game-up path (`./game ... up`, `launch_and_wait.sh`, or a pulse timer)
  call `jawa/tps_report` via `python.exe` as soon as the bridge answers, and stamp the ledger.
  Whichever is chosen, the doc's "Trap" section must then state what starts it.

### 2. HIGH: stalls are silently dropped; a hang or crash is never recorded
- **Where:** `JawaBenchTpsMath.cs:24, 76-79` (`dReal <= 60`). `JawaBenchTpsSampler.cs:128-133`
  (dropped window → `WindowsDropped++`, held in memory only, `:55`). A sample is emitted only on the
  first frame after the cadence elapses (`:125-126`).
- **Scenario:** The main thread freezes for 90 s (pathing storm, a mod deadlock, GC thrash). The next
  frame sees `dReal` ≈ 95 and drops it. The record shows a gap, and the reader reports nothing.
  `verdict` only knows newest-sample age, and it treats in-window gaps as fine. If the game hangs
  for good or crashes, the open window (up to 5 s) and the hang itself never reach disk. These are the
  "very slow" events he is complaining about. The 60 s rule was meant to exclude loads and menus,
  but those are already handled by `game == null` / `ReferenceEquals(game,_game)` (`:111, 114`).
- **Fix:** Never drop. Emit the window with `state: "stall"` (or `gap`), its real `dReal`, and the
  inter-frame gap (see #5). Add a background heartbeat thread: the postfix writes a volatile
  `lastFrameRealtime` (Stopwatch based, since Unity time APIs are main-thread only), and the thread
  appends `{"state":"hung","silentS":N}` once the main thread has been silent for more than 10 s.
  Then a hang that ends in a crash is still on disk. Persist `windowsDropped` in each line.
  The reader should flag gaps between consecutive same-session samples larger than 3× the cadence.

### 3. HIGH: the multiplier is read once at window end, so the effective speed flips go undetected
- **Where:** `JawaBenchTpsSampler.cs:121` (only `CurTimeSpeed` change → mixed), `:158`
  (`mult = tm.TickRateMultiplier` at emit). Engine `TickRateMultiplier`: Superfast is **6 or 12**,
  depending on the cached `NothingHappeningInGame()`. **18** applies with no maps, which the doc omits.
  `slower.ForcedNormalSpeed` forces **1** during combat. Neither changes `CurTimeSpeed`.
- **Scenario:** At Superfast, a raid starts 4 s into a quiet window. The window ran at 12x for 4 s and
  6x for 1 s, so tps ≈ 600. At emit mult is 1 (forced normal), so target is 60, ratio ≈ 10, and the
  sample is judged "high". The reverse case is also common: mostly 6x, then 12x at the end, giving
  ratio ≈ 0.5, judged "low". Six such windows in a row give a false SUSTAINED LOW/HIGH WARN.
  The selftest vector `selftest_tps_record.py:55` names this "12x jump" but feeds it as ordinary data.
- **Fix:** Integrate the target per frame. In the postfix, for each unpaused frame, do
  `_expectedTicks += 60f * tm.TickRateMultiplier * dt`, then `ratio = dTicks / _expectedTicks`.
  Also record `multMin`/`multMax`, and set state `mixed` when they differ. This fixes #4 at the
  same time. The cost per frame is one property read, and `NothingHappeningInGame` is cached.

### 4. MEDIUM: partial pauses dilute the ratio, and the selftest locks it in
- **Where:** `JawaBenchTpsMath.cs:65-71`: `tps = dTicks / dReal` over the whole window, with `run`
  whenever `pausedFrac < 0.5`. `pausedFrac` is weighted by frames, not time (`:68`). Paused frames
  usually render at a different rate, so the share is skewed.
- **Scenario:** He pauses for 2 s of a 5 s window to issue orders. That is 40 % paused, so the
  sample is judged `run` with ratio ≈ 0.6 even though the game was healthy. A play style with frequent
  short pauses, which is normal RimWorld play, produces a steady stream of "slow" samples.
  `selftest_tps_record.py:52` asserts that 33 % paused is a valid run sample, which enshrines the bias.
- **Fix:** Use #3's integrated target, accumulated over unpaused frames only. Also, or instead,
  measure paused share by real time (`Σdt` over paused frames), not by frame count.

### 5. MEDIUM: long events (autosave, map generation) land inside "run" windows. The doc says they do not
- **Where:** `Root_Play.Update` returns early when `LongEventHandler.ShouldWaitForEvent`, so
  `Game.UpdatePlay` and the postfix do not run. The window's `_t0` keeps running regardless.
  `tps_record.md:31` claims "nothing is written... during a long event". That is false for any event
  shorter than 60 s, and an autosave is one.
- **Scenario:** A 12 s autosave on a large colony falls inside one window, producing a 17 s window
  with ratio ≈ 0.3 that is judged `run`. That is a real hitch, but it is misattributed to TPS, and a
  longer one is dropped under #2.
- **Fix:** Track the realtime gap between consecutive postfix calls. Emit `gapMaxMs` and `gapTotalS`.
  Optionally, time `GameDataSaveLoader.SaveGame` with a prefix/postfix and emit `saveMs`. Exclude
  `gapTotalS` from the expected-tick denominator, and label the sample `state: "gap"` when it is
  large. Correct the doc sentence.

### 6. MEDIUM: `tickMs` cannot tell you why; it is a lagged snapshot
- **Where:** `JawaBenchTpsSampler.cs:177`. Engine: `MeanTickTime => smoothedTickTimeAverage`, an EMA (α
  0.1) of a **720-tick** SMA, sampled once at window end. It is not updated while paused.
- **Scenario:** A 3 s spike in tick cost is invisible, and after a pause the value is stale. The doc's
  "low fps + small tickMs ⇒ rendering" reasoning (`tps_record.md:53-56`) then leads to the wrong
  conclusion.
- **Fix:** Add a Harmony prefix that starts a Stopwatch, and stop it in the existing postfix. Emit
  `simMs` (total tick work in the window) and `simShare = simMs / (dReal·1000)`. Also emit
  `capFrames` (frames where `TicksThisFrame == 2·mult`, meaning the frame rate was the limit) and
  `budgetFrames` (frames whose tick work exceeded 45.45 ms, meaning simulation was the limit). These
  three numbers answer "why" directly.

### 7. MEDIUM: `frameMaxMs` may be clamped (UNMEASURED)
- **Where:** `JawaBenchTpsSampler.cs:122-123` uses `Time.unscaledDeltaTime`. If Unity clamps it to
  `Time.maximumDeltaTime` (≈ 333 ms by default) as it does `deltaTime`, a 5 s hitch is reported as
  333 ms. I did not verify this.
- **Fix:** Derive the frame gap from the difference between consecutive `realtimeSinceStartup`
  readings, which is unclamped. This is the same measurement #5 needs. Consider
  `realtimeSinceStartupAsDouble` for long sessions.

### 8. MEDIUM: the doc and reader cannot answer "was TPS slow at time T, and why"
- **Where:** `tps_record.py:130-133, 180-186`. The window is always relative to now (`--window`). There
  is no `--at`/`--since`/`--until`. Times are UTC only, while he will say "around 9 pm" in Pacific time.
  The record holds no colony context. Retention is two 1 MB files, about 10 h of play
  (`JawaBenchTpsMath.cs:33`), so last night is gone after one long session. The `session` id is not
  in the Player.log install line (`JawaBenchTpsSampler.cs:94`), so a session cannot be joined to a log.
- **Fix:** Add `--at "2026-10-10 21:30" --span 10m` (local time, converted to UTC) that prints the
  samples, gaps and stalls around T. Add cheap context columns each sample: `maps`
  (`Find.Maps.Count`), `pawns` (spawned pawns on the current map), and heap size
  (`GC.GetTotalMemory(false)`). Keep more history: daily files or 5 rotations. Put `session` in the
  install log line. Add a doc section, "Answering 'was it slow at T'", with the exact command and a
  decision table: the gap/stall/hung states, simShare against capFrames, and heap growth.

### 9. LOW: `sustained` is not time-bounded, and the summary mixes speeds
- `JawaBenchTpsSampler.cs:186-190, 265`: `RunRatios` spans the whole hour in memory. The last 6 run
  samples can be separated by long pauses or a game reload, which is not "30 s sustained".
  `tps_record.py:148, 166-168` prints "tps median X vs target Y", where Y is only the last sample's
  target. With speed-1 and speed-3 samples in one 5-minute window, this reads "median 120 vs target
  180" while the ratio is 1.0.
- **Fix:** Require the 6 samples to be contiguous (same session, each at most 2× the cadence apart).
  Print the ratio median and give TPS per speed.

### 10. LOW: GC counting is labelled wrong and may undercount
- `JawaBenchTpsSampler.cs:148, 160`: Unity Mono uses Boehm, which has no generations, so
  `CollectionCount(0)` counts all collections; it is not "gen-0" as `tps_record.md:47` says. If
  incremental GC is on, pauses are sliced across frames and the count says little.
- **Fix:** Rename it to `gc`, and add a heap-size column (#8). Heap growth is the better "why" signal.

### 11. LOW: rotation can lose a line
- `JawaBenchTpsSampler.cs:203-208`: `File.Move` throws if a reader holds `tps.jsonl` open without
  delete sharing. WSL's `tps_record.py` reads through drvfs. The line is lost, and `WriteError` is
  set until the next success. This is rare.
- **Fix:** On a failed move, still append to `tps.jsonl` and retry rotation next time.

### 12. LOW: the selftest proves only the pure maths
- `selftest_tps_record.py` covers `JawaBenchTpsMath`. It does not cover the postfix windowing
  (`Open`/reset on a new Game, frame counting, the speed-change flag), the JSON emit, or the rotation
  I/O. Those are where findings #2-#5 live. The parity harness targets **net8.0**
  (`TpsMathSelfTest.csproj:14`), but production runs on Mono/net472, so `Math.Round` and formatting
  parity on Mono is assumed, not shown.
- **Fix:** Factor the window accumulator into `JawaBenchTpsMath`. Make it a pure `FrameAccumulator`
  that takes `(now, dt, paused, timeSpeed, mult, ticksGame, ticksThisFrame, tickWorkMs)` and returns
  an optional sample. Then the selftest can replay frame traces: a partial pause, a Superfast flip,
  forced normal speed, an autosave gap, and a 90 s stall.

### 13. LOW / latent: alt-tab
- With `Prefs.RunInBackground` off, Unity stops `Update` while the game is unfocused, and the window
  spans the unfocused time, giving a false low sample. His current `Prefs.xml` has `True`, so this is
  latent. #5's gap tracking covers it.

### Not a problem
Main-thread cost per frame is trivial: a few property reads, and `Paused` is something the engine
already evaluates. The file append runs on the thread pool. Lazy Harmony patching from a tool call
has precedent in five other JawaBench patches. Session and new-Game reset are correct, and JSON
`null` for NaN is valid.

## Doc: can a future agent answer "was TPS slow at T and why"

**Partly "was", not "why".**

- **"Was" works** only if all three hold: the sampler was running (usually not, #1), T is within
  roughly the last 10 h of play (#8), and the agent converts local time to UTC by hand and widens
  `--window` until T is included.
- **Gaps are ambiguous.** The doc says a gap "never means TPS was fine", which is correct. But it
  cannot tell an unstarted sampler from a dropped stall (#2) or a long event (#5).
- **"Why" rests on `fps` against `tickMs`.** `tickMs` is a lagged EMA (#6), so it cannot carry that.
  There is also no colony context and no save timing.

**Wrong statements in the doc:**

- `tps_record.md:31` says long events write nothing.
- `:40` omits the Superfast 18x case with no maps.
- `:47` calls the GC count "gen-0".

**Recommended doc additions:**

- A "slow at T" recipe built on the `--at` command (#8).
- The state vocabulary: run, paused, mixed, gap, stall, hung.
- How to tell simulation-bound from frame-bound using `simShare`/`capFrames`/`budgetFrames` (#6).
- What starts the sampler, once #1 is fixed.
