# BRIDGE_TPS_REVIEW2_FIXES_1 — fix log (2026-10-10, FOUNDRY)

Source: `Transient/foundry_tps_review_gpt2_20261010.md` section F. Each row: the selftest written first,
its FAIL output on the unfixed code, then the fix and the PASS. Selftest:
`python3 src/RimMandrake/Utils/selftest_tps_record.py` (Python checks, C#/Python parity, and the C# unit
group `U` run inside the production-file harness `bridgetools/TpsMathSelfTest`).

## Engine / Harmony facts verified (not guessed)

- **Harmony is 2.4.2.0** (`brrainz.harmony`, workshop 2009463077, `About/Manifest.xml`). Decompiled
  `HarmonyLib.MethodCreator` with ilspycmd (`D:\Luke\dev\_rmscratch\harmony\MethodCreator.cs`):
  - `AddPrefixes`: a prefix is skipped after an earlier prefix returned false **only if
    `AffectsOriginal(prefix)`** — it returns `bool`, or has an `out`/by-ref parameter that is NOT
    `__instance`, `__originalMethod` or `__state`. Our timer prefixes are `void` with only `out __state`
    (+ `__instance`), so on the installed Harmony they are **never** skipped while their postfix runs.
    GPT finding A5's fabricated-duration path does not occur on 2.4.2; the real exposure is an exception
    in our prefix (escapes into the tick) or in the original (postfix never runs). Fixed defensively anyway
    (a zero `__state` is refused), because the skip rule is Harmony-version behaviour.
  - Postfixes are not in a `finally`: an exception in the original or an earlier patch skips them.
  - Finalizers: a `void` finalizer leaves the exception local untouched and the emitted code then
    `rethrow`s it (`rethrowPossible` stays true) — so a void finalizer is observe-and-clean-up that
    **preserves the original exception**. Only a finalizer returning `Exception` replaces it.
  - `__runOriginal` injection exists (`InjectionType.RunOriginal`).
- **RimSage, decompiled 1.6**:
  - `GameDataSaveLoader.SaveGame(string fileName)` (public static; catches and `Log.Error`s its own
    exceptions); `LoadGame(string saveFileName)` only QUEUES an async long event and disposes the current
    game — so the name is a load REQUEST, not a success.
  - `Root.Update` (base, the method patched) runs `LongEventHandler.LongEventsUpdate` inside it;
    `Root_Play.Update` calls `base.Update()` and only then `Current.Game.UpdatePlay()` (which calls
    `TickManagerUpdate`). So per frame: RootPrefix → LongEventsUpdate → RootPostfix → TmuPrefix → ticks.
  - `TickManager.TickManagerUpdate` (1.6): returns early when paused; ticks while
    `realTimeToTickThrough > 0 && ticksThisFrame < mult*2`, breaks after 45.454544 ms; `DoSingleTick` is
    an instance method of `TickManager`.
  - `WorldPawns.AllPawnsAliveOrDead` COPIES every alive, mothballed and dead world pawn into a list on
    each call; `AllPawnsDead` is the HashSet itself.
  - `ModContentPack.ModMetaData` → `ModMetaData.ModVersion` exists (for the ordered mod manifest).

## Per fix

### Harness (prerequisite)
`TpsMathSelfTest` now also compiles the production `JawaBenchTpsWriter.cs` and `JawaBenchTpsWatchdog.cs`
(both Verse-free) plus `Units*.cs`; the `U` line runs every `T_*` method and prints `U name ok|FAIL`,
`J name <json>` production-composed rows that Python parses with `tps_record.loads_strict` (duplicate
keys and NaN refused). `CS_UNITS` in the selftest names every unit that must run.

### MUST 1 — duplicate envelope/context keys (verified a119858e4 = 87cd3a549: only `kind` was fixed)
- The `kind` duplicate was fixed in 87cd3a549, but **`mult` was still duplicated** (`GapFields` + the
  watchdog `ContextFields`), and nothing tested the production composition. Incident composition moved
  into `M.IncidentFields` (behaviour-identical) so the harness composes the real row.
- RED: `FAIL C# composed line incident does not parse strictly: duplicate key 'mult'`.
- FIX: `GapFields` emits `multAfter` (observed after the gap); the context's `mult` is the cached value from
  before it. Envelope keys reserved (comment). `render_row` prints `mult before->after`.
- GREEN: `C# units: 1 run, 0 failed`, selftest PASS.

### MUST 5 — an unexplained gap with a state change was removed from expected ticks
- RED (traces `stallflip`: 1 s at 1x, a 90 s gap, then 3x; `stallunpause`: paused, 90 s gap, running):
  `FAIL MUST 5: a 90 s gap across a speed change stays in expected ticks ... 'ratio': 1.102, 'expected': 59,
  'runS': 0.983, 'ambigS': 90` — the 90 s were only ambiguous, so the window read healthy.
- FIX (`FrameAccumulator.Pre`, C# + Python port): the gap stays in `runS`/`expected` at the HIGH end of the
  two states (before/after; paused = 0), `expectedLo` carries the low end, and `ratioHi = dTicks/expectedLo`
  (null when the low end is a pause). The seconds are still counted ambiguous.
- GREEN: python checks PASS; C# parity 57/57 identical (the new traces included).

### MUST 3 — sample duration, simulation timing and timestamp used different boundaries
- RED (trace `longtick`: a 40 s current invocation at the cadence boundary; `tickreset`; reader fixture):
  `FAIL MUST 3: ... (simShare <= 1): [('run', 5, 40598, 8.12), ('stall', 40.017, 2, 0), ...]`,
  `... the 40 s tick and the 40 s gap it caused are in the SAME window`, no `monoStart/monoEnd` on any
  window, `tickReset` absent (`[(130, None)]`), reader placed a window at its enqueue time
  (`[(None, 1791583200.0)]`) and missed an incident whose gap overlapped the query (`0`).
- FIX: a window is now `[monoStart, monoEnd]` between two PREFIX observations and is closed in `Pre()`
  (before that frame's tick work); `Post()` adds the invocation to the window open at that moment. So
  simS/attribution physically lie inside `dReal`, and the sampler emits (and takes attribution) in
  `TmuPrefix`. The first window starts at the first prefix with that frame's ticks/work included (review
  item 9's first-frame misalignment). A backwards tick counter is detected per frame (`tickReset`, ticks
  before it carried, never a silent clamp). Reader `place()`: windows at
  `utc-(mono-monoStart) .. utc-(mono-monoEnd)`; incidents span `gapS`, `resumed` spans `silentS`;
  timeline selects by overlap.
- GREEN: python checks PASS, C# parity 64/64, companion builds.

### MUST 2 (+ SHOULD 1, review item 12) — profiler timers skip-safe and exception-contained
- Seam: the accounting moved unchanged into the Verse-free `JawaBenchTpsStages.cs` (compiled by the
  harness); the Harmony hooks only read the clock and call in.
- RED (`T_StagesSkipSafe`, `T_StagesWorstTick`, `T_StagesInvalidNesting`):
  `FAIL C# unit StagesSkipSafe: an End with no recorded start fabricated 86400 s (tl:Normal) / 86400 s (tick)`;
  `FAIL SHOULD 1: ... {'tg': 777, 'ms': 50, 'top': 'tl:Normal 80%'}` (no numeric breakdown);
  children summing past their parent produced no validity flag.
- FIX: `End`/`TickEnd` refuse a zero start or a backwards clock and count `profSkipped`; one duration
  feeds both the tick total and the worst-tick record; worst ticks carry the tick id captured in the
  prefix (`TicksGame+1`, DoSingleTick increments first) and an exclusive per-stage `stages{}` breakdown in
  ms; every window states `attrValid` and `attrOverMs` when children exceed parents. Hooks: prefix +
  **void finalizer** (runs on throw, rethrows the original — see Harmony facts), each in try/catch that
  disables attribution (`attrError`, tool `attribution.runtimeError`) rather than escaping into the tick;
  hooks on a non-main thread are skipped and counted.
- Note (verified, see facts): on Harmony 2.4.2 our void `out __state` prefixes are never skipped, so the
  86400 s path needs a prefix that threw; the guard is kept because skip rules are version behaviour.
- GREEN: `C# units: 4 run, 0 failed`; companion builds.

### MUST 6 — game-scoped state reset, game identity persisted
- Seam: the sampler's menu/game transition logic moved unchanged into the Verse-free
  `JawaBenchTpsLifecycle.cs` (harness-compiled).
- RED (`T_LifecycleScopes`): `menu clears the game's save label: 'Ashkarr_A' | a NEW game never inherits the
  previous load's save name: 'Ashkarr_A' | cumulative save time is per game: 4.5 | attribution from game 1
  does not reach game 2's first window: 0.2 s carried | a stale (1 h old) load request does not label a new
  game: 'Broken_Save'`.
- FIX: `LoadGame` is a REQUEST (it only queues a long event — RimSage) consumed by the next game reaching
  Playing within 20 min; the menu clears the label; every game/menu boundary resets the save total, the
  profiler totals and worst ticks (`JawaBenchTpsStages.Reset`) and `WD.LastSave`; `game` (1, 2, … per
  process) rides on `game`, `sample` and `incident` rows.
- GREEN: `C# units: 5 run, 0 failed`; companion builds.

### MUST 7 — continuity, lifecycle resets, threshold consistency
- RED (reader fixtures with explicit boundaries; `Q` parity vectors = the sampler's streak):
  `FAIL MUST 7: ONE missing window (10 s apart) breaks the streak: 'low'`; `... three low windows before a game
  replacement and three after are NOT one streak`; `... an error row breaks the streak`; `... a seq gap (dropped
  rows) breaks the streak`; `C#/Python disagree on line 53: C# Q low / py Q ok` and `line 54: C# Q high / py Q ok`
  (0.5996 and 1.1504 classified differently live vs on disk).
- FIX: `contiguous` = same session AND same `game` AND `monoStart` within 0.5 s of the previous `monoEnd`
  (legacy rows: 1 s slack, not `dReal + 5`); `sustained_from_rows` walks ALL rows and breaks on
  game/menu/error/silence/resumed/shutdown/session rows and on a writer seq gap (`mark_seq_gaps` over the
  whole on-disk stream in `read_record`, so a time-filtered selection is not misread as loss;
  `seqMissing` counted). C#: the streak stores `M.StreakValue` = the 3-decimal disk value; the tool's
  `sustained` is `unknown` once its newest window is > 60 s old (`M.SustainedFresh`, green-only unit
  `T_SustainedStale`: the function is new).
- GREEN: python checks PASS, parity 67/67, `C# units: 6 run, 0 failed`.

### MUST 8 — sessions analysed separately
- RED (fixture: fresh healthy session B + stale low session A listed after it):
  `FAIL MUST 8: a fresh healthy session is judged on its OWN windows ...: ('WARN', 'SUSTAINED LOW TPS ...
  ratio median 1.00 (min 0.30) over 20 run windows ...')` — the stale session's streak decided a FRESH
  verdict; no per-session summary; timeline holes went backwards
  (`{'from': 1791588195.0, 'to': 1791587955.0}`) and the merged timeline was not chronological.
- FIX: `summarise` builds one summary per session (`_summarise_one`), the verdict is the session with the
  newest window, `sessions` lists each, and another FRESH session's sustained low/high is reported (WARN)
  rather than blended. `timeline` computes same-session holes per session and cross-session holes only
  where no session has a window, then merges rows chronologically; `sustainedBySession` is returned.
- GREEN: python checks PASS; reader smoke-run on the real record dir clean.

### MUST 13 — strict rows/settings, segments >= 1000
- Seam: `JawaBenchTpsSettings` moved unchanged out of the sampler into Verse-free `JawaBenchTpsSettings.cs`.
- RED: `FAIL MUST 13: read_record crashed on a malformed row: TypeError("cannot use 'list' as a dict key")`;
  `segment 1000 is listed and sorted after 999: [..._002.jsonl, ..._999.jsonl]` (1000 invisible);
  `a malformed heartbeat crashed the observer: TypeError(...)`; `C# unit SettingsStrict: duplicate key:
  expected REFUSED ... got note=null | nested key ... sampler=False | truncated document ...` (the regex read
  `sampler:false` out of a nested object and out of a truncated file).
- FIX: reader reads bytes, decodes each line STRICT utf-8, parses with `loads_strict` (dup keys / NaN
  refused), `_valid` checks kind ∈ known set, hex session, non-negative int seq, finite non-bool numbers,
  sample state ∈ the five, non-negative durations/rates; `SEGMENT_RE` takes `\d{3,}` and segments sort
  numerically; heartbeats must be objects; `observe` tolerates junk `silentS`. Settings: one strict flat
  JSON object (`ParseFlat`), any duplicate/nested/truncated/non-finite/wrong-type value → whole file
  refused, defaults used, reason in `note` (now on the `session` row as `settingsNote`); retention values
  only grow from the shipped defaults (16 MB was accepted before, contradicting the doc) and are capped;
  read once at launch (stated in `_doc`).
- Consequence, measured: the 2 build-2 incident rows on disk carry the duplicate `mult` and now count as
  `malformed` (173 rows read, 2 malformed) — exactly the rows MUST 1 says were wrong.
- GREEN: python checks PASS, `C# units: 7 run, 0 failed`, companion builds.

(next fixes below)

## C3 controlled-interruption matrix (minimal list)

(pending)

## Owed

- MUST 17 (full ~600-mod overhead A/B, autostart on the full list, overnight reconstruction, standing
  periodic observer): owed to a cold load of the full list.
