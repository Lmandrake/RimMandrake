# EmpirePursuit validation (Approach B), 2026-10-07 - DONE, nothing committed

## Kernel (Verse-free, called by the mod with the same expressions)
`src/RimUtinni/EmpirePursuit/Source/Kernel/EmpireLadderKernel.cs` (+ the pre-existing pure `EmpireLadderMath.cs`)
- `EmpireLadderState`: the scalar half of `MapComponent_EmpireSearch` - `EnsureInit`, `NextRungIndex` (first enabled, defined rung at/above nextRung; cordon / bombardment / probe gates), `FireGate` (live or terminal: nothing; inside the 2-day storyteller spacing: postpone n; else go), `Begin`, `Resolve` (climb/hold with floor, top success => terminal, returns "schedule next"), the five contact steps (`ProbeStep`, `SpotterStep`, `CordonStep`, `StrikeStep`, `BombardmentDue/Landed`, each returning Continue / EmpireSucceeds / EmpireFails and the Visibility delta), `ApplyFloor`, `LowerRung`, `RaisedFloor`, `RememberedRung`, `ShouldRecordDeparture`, `BlockStorytellerRaid`, `NextIntervalFactor`.
- `EmpireLadderTimers`: the scenario part's hourly arithmetic - `TimerIntervalTick`, `TimerInterval`, `Schedule` (raid / warning timers), `ShouldWarn`, `ShouldFire`, `ShouldEndless`.
- `EmpireRungKind` moved here from `RUT_EmpireRungDef.cs`. The map component keeps the same field names as properties over `st` (Scribe goes through `ref st.x`); contacts, pawns, letters, lords and the Aftermath/Visibility reflection bridges are untouched.
- Call-site edits: `EmpireLadder.cs`, `RuthlessPursuingMechanoids.cs` (ScheduleLadder, TickLadder, timer helpers), `RUT_EmpireRungDef.cs`, `EmpirePursuit.csproj` (1 Compile line). Files were clean in `git status` before the edit.
- Not extracted (engine calls): pawn generation / drop pods / lords / raids (`FireProbe`, `FireSpotter`, `FireRaidRung`, `FireBombardment`), `SeesColony` (LOS and glow reads), `IonVolley`, the old pursuit's `FireRaid_NewTemp` wave arithmetic in `RuthlessPursuingMechanoids.cs` (ScenPart state + RaidIncident calls).

## Defect fixed
- A TERMINAL ladder that is lowered back below the top (`EmpireSearch.LowerRung`, the Ishko Unseen Berth hook) cleared `terminal` but scheduled nothing: `Resolve` schedules only while not terminal, so the old raid timer is in the past, `ShouldFire` (`now == ceil-hour(raidTimer)`) can never be true again and the endless waves (terminal only) stop too - the pursuit is silently dead for good. `LowerRung` now reports `revived` and the component calls `ScenPart.ScheduleLadder(map)` when no contact is live.

## Observations, not changed
- `LowerRung` during a LIVE contact is overwritten when that contact resolves (`NextRungAfter(firedRung,...)` ignores the lowered value). Possibly intended; a design call.
- Setting `ionVolleyIntervalHours` is Scribed and read but has no control in the settings window (lint WARN).

## Fuzz
`python3 src/RimMandrake/Utils/selftest_empirepursuit_fuzz.py [--fuzz-scale F] [--fuzz-seed N] [--fuzz-only ladder|timers|math]`
Project `Source/SelfTest/Fuzz/EmpirePursuitFuzz.csproj` (net8.0; pulls the kernel + EmpireLadderMath only). The older example check `selftest_empire_ladder.py` still passes 42/42.
- ladder (seeds 1..8000; 40-200 actions, 3 maps, random rung table with holes / other kinds, half the cases with 250-tick contact bursts so thresholds are hit exactly): Arrive / Leave / Hours (incl. exactly 48 h) / Fire / Contact / Aftermath / ProbeDied / Storyteller / RaiseFloor / Lower / Gates / Settings vs an independent spec of the design text. Full per-map state, active rung, timers, tile memory and floor equal after every action; FireGate, NextRungIndex, every contact outcome and Visibility delta, ion volley decision, schedule flag and timers equal; invariants: nextRung in [max(1,floor),6], no firing inside the storyteller spacing or below nextRung, idle ladder carries no contact state, a revived ladder always gets a future timer.
- timers (3000): raid >= now+1 h, warning in [now+1 h, raid], fires on exactly ONE hour tick (the next boundary), warning strictly earlier or absent when it would share the raid tick, never both, blocked by live/terminal, a postponed rung always lands on a later hour tick, endless cadence exact.
- math (5000): Clamp idempotent / bounded, climb and hold exact vs closed form, StartingRung >= floor and >= probe/strike start and honours a remembered rung, decay monotone, band multiplier non-increasing, 60% rule exact, sighting monotone in distance, floor only rises.
- Seeds: default 8000 / 3000 / 5000 (1.0 s, 16k cases, 2.9M steps). `--fuzz-scale 30`: 240,000 ladder + 90,000 timers + 150,000 math seeds, 86.8M steps, 22 s, 0 failures; fires 214,434, climbs 30,775, holds 110,410, terminal 32,803, postponed 40,645, storyteller refusals 55,861, remembered tiles 77,840 (blind guard fails the run if any is zero).

## Mutation (35 planted, 35 caught, files restored byte-identical)
`python3 src/RimMandrake/Utils/mutate_empirepursuit_fuzz.py [substring]` (kernel x31, EmpireLadderMath x4): spacing `<=` and 1-day, fires while terminal / live, Resolve ignores floor, top success not terminal, failure climbs, Resolve leaves progress, Begin forgets fire tick, disabled cordon / probe still fire, table walk short, probe `>`, blind flag, probe timeout day, spotter timeout `>=`, cordon volley without a standing cordon, cordon success early, aftermath verdict inverted, bombardment not terminal, lower ignores floor / keeps terminal / never revives, floor can fall, memory ignores setting, storyteller block ignores live contact, timer under an hour, warning after raid, tick rounding floors, warn on the raid tick, EnsureInit re-rolls; 60% rule, climb past top, decay ceil, remembered tile ignored. Two harness gaps found by early MISSED runs and closed (threshold scale, hourly EnsureInit, exact 48 h spacing edge); the mutator now also waits after restoring (rsync --modify-window=2 served a stale mutated copy once).

## Lint
`python3 src/RimMandrake/Utils/lint_empirepursuit_defs.py [--quiet] [--mod-dir D] [--plant-check]` = generic `lint_mod_defs.py` + ladder data checks: 6 rungs, top 6, 21 translate keys all keyed, 0 ERROR, 1 WARN.
- WARN `ionVolleyIntervalHours` has no control in the settings window.
- Known false positive handled in the wrapper (counted, 2 lines): the generic settings scan reads `RFPMod.settings` (static instance field after the ModSettings class) as a settings field.
- `--plant-check`: 10 planted defects (kind typo, unknown child, rung index gap, instant probe, probe that can never win, missing Keyed string, Verse import in the kernel, tick-constant drift, stale spacing alias, kernel missing from csproj) all caught.

## Build
`winbuild.py src/RimUtinni/EmpirePursuit/Source/EmpirePursuit.csproj` -> 0 warnings 0 errors; `Assemblies/RuthlessPursuingMechanoids.dll` + `.srchash` rebuilt, UNCOMMITTED. Not wired into run_selftests.py.
