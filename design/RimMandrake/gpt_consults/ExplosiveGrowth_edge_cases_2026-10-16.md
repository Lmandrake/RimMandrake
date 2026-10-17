# ExplosiveGrowth edge cases: GPT bug-hunt, graded against the code

- Date: 2026-10-16
- Model: gpt-6.1-sol, high effort
- Slices: `ExplosiveGrowth_A` (18 findings), `ExplosiveGrowth_B` (14 findings). Raw answers:
  `design/RimMandrake/gpt_consults/raw/ExplosiveGrowth_{A,B}_2026-10-16.md`.
- Graded against `src/RimMandrake/ExplosiveGrowth/` (Source/, Kernel/, Defs/) and the campaign roster
  `src/RimUtinni/UtinniPatches/Defs/ExplosiveGrowth/`, which GPT never saw. Rulings:
  `design/RimMandrake/explosive_growth_rulings_2026-10-16.md` and `..._ruled_spec_2026-10-16.md`.
- Tally by raw finding: 18 VERIFIED, 5 PLAUSIBLE, 9 REFUTED (32 total). By distinct issue (A and B overlap heavily): 11, 4, 7.
- All line numbers are in the current foundry clone. Nothing was run; no source edited.

## Question used

Both slices got the same text (only the slice name differs), verbatim:

```
SUBJECT: ExplosiveGrowth (RimWorld 1.6 mod, C# + XML defs). Restate this subject on the first line of your answer so we can detect crossed answers. This is slice "ExplosiveGrowth_A".

You are a hostile, senior RimWorld modder and Harmony expert reviewing this mod. Find UNUSUAL bugs and edge cases, not style. Probe in particular: save/load round trips (ExposeData, Scribe_Collections, null lists after load, fields not saved, PostLoadInit ordering, loading a save that has the mod's data but the mod now disabled, savegame removal safety); tick-rate/pause/speed-3/ultrafast behaviour (Tick vs TickRare vs TickLong, intervals skipping, catch-up after map load); multiple maps and caravans, temporary/pocket/space maps, world-map tiles and biome changes mid-game; pawns arriving/leaving/spawning/despawning mid-effect; death/despawn/destroy/discard during effects (stale references, Thing.Destroyed vs Spawned, map == null, Position invalid); null and out-of-bounds cells (InBounds, CellIndices, edge-of-map, off-by-one in grids, negative or overflow indices, integer overflow, float NaN/Inf, division by zero); mod-setting toggles mid-game (turning a feature off while state exists, on again); Harmony patch ordering and conflicts with vanilla and the DLCs (Biotech, Anomaly, Odyssey, Royalty, Ideology) and other common mods (prefix returning false skipping other mods, __result misuse, transpiler fragility, patching generic/overloaded methods); performance spikes and long ticks (per-tick allocations, O(N^2) scans, LINQ in hot paths, whole-map scans, unbounded caches/dictionaries, static state leaking across games/maps); determinism and RNG (Rand without seeding, Rand.PushState misuse, order-dependent dictionary/hashset iteration, thread-unsafe statics); minified/strange defs (missing fields, MayRequire, ThingDefs without comps, defs with odd stack/size, def names referenced from C# that may not exist, XML patch xpaths that silently match nothing); static caches not cleared on game load / new game; GameComponent/MapComponent lifetime.

Output format: RANKED findings, most severe first. For EACH finding give: (1) a short title, (2) severity (crash / data loss / wrong behaviour / perf / cosmetic), (3) the exact file path and line number (or method name) it implicates, quoting the 1-3 offending lines, (4) a concrete step-by-step repro a tester could follow in-game or with a script, (5) your confidence (high/medium/low) and why. Do not pad: skip anything you cannot tie to code you can SEE in the files below. Review ONLY against the code you can see; when a claim depends on code not in this slice, put it under a final heading "Outside this slice" rather than guessing. Give at least 10 findings if that many real ones exist, but never invent one to reach a count.
```

Inlined files: the question text is followed by the mod source split across two slices (the map component, kernel,
top resolver, registry, patches, settings/mod class, soak sources, incident worker, API, proof/debug hooks, the
roster and BloomCrop XML). Slice B's own raw answer says it saw essentially the same set; GPT did NOT see the
shared `PatchApplier`, `FlowWorksIrrigationRead`, the Utinni roster, the design rulings as authority, or the
ruled-spec owed-work list. That gap explains most refutations below.

## Verified (real, traced)

Severity words: S1 wrong-and-visible, S2 minor/exploitable only on odd input, S3 cosmetic.

1. **Burst's "never downs or kills" is not enforced** (S1). A2 / B1.
   `RM_TopResolver.cs:170-173`: `if (p.health.summaryHealth.SummaryHealthPercent > 0.5f) p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, amount));`
   The settings tooltip (`ExplosiveGrowthMod.cs:257`) and the method summary (`:152-154`) promise the hit is skipped
   if it would down the pawn; the only guard is aggregate health. `DamageInfo` has no `hitPart`, so the hit lands on
   a random part, 2-5 damage. Small wild animals (rat, squirrel-class bodies) and pawns with a crippled vital
   part above 50% summary health can be killed or downed.
   Repro: spawn a rat-class animal and a pawn with a nearly destroyed head part beside a Burst plant, `DebugSetCharge`
   to 0.99, advance one pass, repeat over seeds; look for Dead/Downed afterwards.
   Evidence: line 170 is the only check; line 174 only skips the stun after the fact.
   Fix: choose an outside non-vital leaf part (the `Mutate` filter at `:274-276` already does) and cap `amount`
   below that part's remaining health; or skip pawns whose body size is under a floor. Needs bridge to prove.

2. **Reload fabricates one pass of charge time** (S2 exploit). A3 / B3.
   `RM_MapComponent_ExplosiveGrowth.cs:70-71` `nextPassTick = -1`, `lastPassTick = -1`, neither in `ExposeData`
   (`:357-375`); `RM_ExplosiveGrowthKernel.cs:74` `PassDelta` returns 250 when `lastPassTick < 0`.
   After every load the first tick runs a pass with dt = 250 even if the previous pass was 1 tick ago. Per reload
   that is up to 250/(chargeTicks x clock) of charge (1.7% at the 6 h default); decay is advanced the same way.
   Repro: charge a plant to 0.94, save, load and advance 2 ticks, repeat about four times: it fires.
   Fix: `Scribe_Values.Look(ref nextPassTick,"nextPassTick",-1); Scribe_Values.Look(ref lastPassTick,"lastPassTick",-1);`
   in ExposeData (old saves read -1 = today's behaviour). Offline reasoning suffices; proof needs one save round trip.

3. **A new rupture exposes pawns twice on its creation tick** (S2). A6 / B5.
   `RM_TopResolver.cs:237-238` adds the zone and pulses; the same `Pass` then runs `TickRuptures(now)`
   (`RM_MapComponent_ExplosiveGrowth.cs:249`) after `ledger.Pass` (`:246`) fired it, and the new zone has
   `untilTick = now + 3600`, so it pulses again. Default 8% per roll becomes 15.36% for that tick.
   The gamble path (`RM_ExplosiveGrowthPatches.cs:229`) pulses once, so the two routes disagree.
   Fix: in `Pass`, move `if (ruptures.Count > 0) TickRuptures(now);` above `ledger.Pass(...)` (3 lines), or drop
   the pulse call in `Rupture`. Provable by reading; a counter on `RuptureExposurePulse` confirms.

4. **Master switch does not stop the ambient bands** (S2). A7 / B8.
   `ExplosiveGrowthMod.cs:45` `BandsOn => bandsEnabled && Enabled(RosterKey)`, no `enabled`; the band postfix
   (`RM_ExplosiveGrowthPatches.cs:63`) reads only `BandsOn`, and its `[PatchFeature]` gates on `bandsEnabled`, not
   `enabled`. The comments at `ExplosiveGrowthMod.cs:20-22` and the tooltip at `:161` say off means "every patch
   no-ops" and plants revert to the ambient rate. (Line 35 reads as the bands being their own switch, so intent is
   slightly ambiguous; the master-switch text is the stronger claim.)
   Fix: `BandsOn => On && bandsEnabled;` (one line). Bridge or fuzz row to prove a banded plant's rate with `enabled=false`.

5. **Existing suppression ignores the suppression toggle** (S2). A13 / B9.
   `RM_MapComponent_ExplosiveGrowth.cs:141` gates only the write; `:150-153` `IsSuppressed`, kernel `:154`,
   `TrySoak` `:168` and the charge pass `:286` read the ledger regardless. The settings group is tagged "changes apply
   to what is on the map now".
   Fix: make `comp.IsSuppressed` return `suppressionEnabled && ledger.IsSuppressed(...)`, and pass an
   `honourSuppression` bool into the kernel `TrySoak`/`Pass` (about 6 lines; update the fuzz callers).

6. **Leaving scope freezes charges; the gamble ignores scope** (S2). A4 (B10 is the sibling, see Plausible).
   `RM_MapComponent_ExplosiveGrowth.cs:230-234` returns before `ledger.Pass`, so charges neither advance, decay
   nor clear; `RM_ExplosiveGrowthPatches.cs:218-221` (`PlantCollected` prefix) checks `On` and `Spawned` but not
   `BiomeInScope`, so a retained charge can still fire on a cut or harvest, and the Print/Yield patches keep
   showing swollen plants. Reachable only by turning the unsupported `applyInOtherBiomes` off mid-game, or
   a campaign-roster change.
   Fix: in the out-of-scope branch, `OnDirty` each charge cell and `ledger.charges.Clear()` (about 5 lines).

7. **Duration overflow in soak and suppression deadlines** (S2). A14 / B7.
   Kernel `:169` and `:177` `int until = now + Math.Max(1, ticks)`. Public `ExplosiveGrowthAPI.Soak/SoakCells/Suppress`
   accept any int; `int.MaxValue` wraps negative, `TrySoak` returns true and `IsSoaked` is immediately false.
   Internal callers are bounded (settings max 96 h = 240000), so this is public-API hardening only.
   Fix: `int until = (int)Math.Min((long)now + Math.Max(1, ticks), int.MaxValue);` at both sites; add a fuzz row
   in `SelfTest/ExplosiveGrowthFuzz.cs`. Fully offline-provable.

8. **Tell stage is a one-way ratchet** (S3). A15 / B11.
   Kernel `:297-303` only raises `rec.stage`; `:303` keeps emitting Tremble/Creak puffs while the charge has
   decayed below the rung, and a plant that reached Silence and was re-wetted never creaks again. The fuzz spec
   mirrors the same ratchet (`ExplosiveGrowthFuzz.cs:152-157`), so it was written that way on purpose; the visible
   result is still wrong.
   Fix: when `want < rec.stage`, set `rec.stage = want` (no creak, no dirty). Update the fuzz mirror at line 152.

9. **BloomBurst treats expired soak entries as a live footprint** (S3). A16.
   `RM_MapComponent_ExplosiveGrowth.cs:104` returns `soakUntil.Keys` unfiltered; `RM_IncidentWorker_BloomBurst.cs:53`
   uses it. Expired cells persist until the next 250-tick `PruneExpired`, so the incident can re-soak and sow a stale
   footprint and skip the fallback blob. Window is at most 250 ticks.
   Fix: `SoakedCells` yields only `IsSoaked(c)`; or filter at line 53 (1 line).

10. **Turning the engine off leaves swollen, tinted meshes baked** (S3). B13.
    `MapComponentTick` early return (`:215-219`) and `WriteSettings` (`ExplosiveGrowthMod.cs:355-359`) rebuild the
    registry but never dirty map sections; the Print/Graphic guards only apply on the next regeneration. Same for
    `hueShiftEnabled` and `groundTellEnabled` toggles.
    Fix: in `WriteSettings`, mark `MapMeshFlagDefOf.Things` dirty on every `Find.Maps` mesh (needs a loop over cells
    or `mapDrawer.RegenerateEverythingNow()`). Needs bridge.

11. **Static component cache pins the last map** (S3, negligible). A17.
    `RM_MapComponent_ExplosiveGrowth.cs:84-99` strong static refs, cleared only in `PostLoadInit` (`:372-373`); one
    abandoned map stays reachable until the next `For` call. Not unbounded, not a correctness issue. No item proposed.

## Plausible (depends on unseen engine behaviour, or latent)

- **Zero/negative `stackLimit` hangs `SpawnNear`** (A1). `RM_TopResolver.cs:329-338`: `count -= t.stackCount` makes
  no progress when `def.stackLimit <= 0`. The code is right, but `ThingDef.stackLimit` defaults to 1 and no vanilla
  harvestedThingDef has 0; needs an abnormal modded def. Hardening: `int lim = Math.Max(1, def.stackLimit);`.
- **Rupture exposure is a flat disc** (A5 / B4). `RM_TopResolver.cs:253` iterates `RadialCellsAround`, no wall, gas
  or LOS test. Design text (`explosive_growth_deep_dive_2026-10-16.md:139-141`) says "pawns in the cloud", so a disc
  is arguably the spec; whether walls should block is a design call. Gas dissipation does not end the zone (1 h fixed).
- **`SoakedCells` aliased into `SoakCells` can throw** (B2). `soakUntil[c] = until` on an existing key bumps the
  enumerator version in Framework-profile Mono. No in-repo caller does it (`BloomBurst` calls `.ToList()` first;
  FloodedCanyon and the debug action pass their own cells). Latent API trap; fix by returning a snapshot.
- **Existing soak survives a no-soak biome carve-out** (B10). `Pass` (`:230`) and the soak postfix (`Patches:96`)
  check scope, not `BiomeRefusesSoak`'s `noSoakBiomes` half. Needs a roster change mid-save; leftover soaks lapse
  within their stored duration (at most the 96 h cap).
- *(B10 sibling)* see Verified 6.

## Refuted

- A8 hydroponics get bonus and cycle: not a code bug, it is the ruled H1 work still owed (`ruled_spec` §3 row "basins / pots ... nothing reads the grower ... build").
- A9 stacked rate model still live: the ruled ×10/×0.1/×4 model is the owed D1/D3 rewrite (`ruled_spec` §10 D-list); code matches the pre-ruling design it was built to.
- A10 irrigation lasts a day after the source goes: W3 presence model is owed (D3/D5); current timed behaviour is the old, documented one (`RM_SoakSources.cs:38-40`).
- A11 slime fluids water every species: T2 per-plant adaptation is owed (`ruled_spec` §2.4 says so explicitly, "Today the accepted set is one global list").
- A12 / B6 BloomCrop resolves to Churn: `RUT_ExplosiveGrowthRoster.xml:33` has `<plant>RM_BloomCrop</plant><top>Burst</top>`; the incident that sows it lives in the same campaign layer. (Baroque Biomes alone, without Utinni, would give Churn, but nothing sows it there.)
- A18 / B12 `TestScopeAll` leaks across games: a TEST-ONLY hook (`RM_ExplosiveGrowthProof.cs:154-173`) with an explicit Off counterpart; "off at every game start" holds at process start; no player path sets it.
- B14 wobble at max scale 1: `VisualScale` (`Kernel:88`) applies the ±3.5% tremble tell separately from the swell on purpose; the maximum-scale slider governs swell only.

## Outside this slice (leftovers worth a probe)

- **Scribe working lists shared across dictionaries** (`ExposeData` `:360-362`, one `tmpKeys` for three dicts,
  `tmpInts` for two). Both GPT slices flagged it as unproven. For value-mode dictionaries RimWorld builds the dict
  in the load pass, so it is probably safe; `charges` uses `LookMode.Deep` and is the one that could differ. There
  is no save round-trip row in `ExplosiveGrowth/validation.py` for soak, suppression, charges and ruptures. Cheapest
  proof: bridge save/load with distinct populated dictionaries, compare `Count`s and one record. Worth a rimflow item.
- Gamble prefix vs other mods' `PlantCollected` prefixes and double yield on a fired top: needs the vanilla caller.
- `PatchApplier` gating of `[PatchFeature]` (does `enabled=false` unpatch live?), relevant to Verified 4.
- Removal safety (deep-saved `RM_ChargeRecord`/`RM_RuptureZone` types) and DLC prerequisites: not examinable here.
- Shared `visualSizeRange` mutation in the Print prefix/finalizer is main-thread and restored in a finalizer; no trigger found.
