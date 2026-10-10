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

(next fixes below)

## C3 controlled-interruption matrix (minimal list)

(pending)

## Owed

- MUST 17 (full ~600-mod overhead A/B, autostart on the full list, overnight reconstruction, standing
  periodic observer): owed to a cold load of the full list.
