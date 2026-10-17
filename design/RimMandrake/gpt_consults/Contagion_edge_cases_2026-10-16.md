# Contagion edge-case hunt, graded (2026-10-16)

Model: gpt-6.1-sol, reasoning high. Slices: Contagion_A (14 findings, C# in `src/RimMandrake/Contagion/Source/`), Contagion_B (5 findings, XML in `Defs/` and `Patches/`).
Raw answers: `design/RimMandrake/gpt_consults/raw/Contagion_{A,B}_2026-10-16.md`. Graded by reading the real code (RimSage used for vanilla facts). No game, bridge or git was used.
Counts: VERIFIED 9, PLAUSIBLE 4, REFUTED 6 (19 findings: A 14, B 5).

## Question used

(Identical for both slices apart from the slice name.)

```
SUBJECT: Contagion (RimWorld 1.6 mod, C# + XML defs). Restate this subject on the first line of your answer so we can detect crossed answers. This is slice "Contagion_A".

You are a hostile, senior RimWorld modder and Harmony expert reviewing this mod. Find UNUSUAL bugs and edge cases, not style. Probe in particular: save/load round trips (ExposeData, Scribe_Collections, null lists after load, fields not saved, PostLoadInit ordering, loading a save that has the mod's data but the mod now disabled, savegame removal safety); tick-rate/pause/speed-3/ultrafast behaviour (Tick vs TickRare vs TickLong, intervals skipping, catch-up after map load); multiple maps and caravans, temporary/pocket/space maps, world-map tiles and biome changes mid-game; pawns arriving/leaving/spawning/despawning mid-effect; death/despawn/destroy/discard during effects (stale references, Thing.Destroyed vs Spawned, map == null, Position invalid); null and out-of-bounds cells (InBounds, CellIndices, edge-of-map, off-by-one in grids, negative or overflow indices, integer overflow, float NaN/Inf, division by zero); mod-setting toggles mid-game (turning a feature off while state exists, on again); Harmony patch ordering and conflicts with vanilla and the DLCs (Biotech, Anomaly, Odyssey, Royalty, Ideology) and other common mods (prefix returning false skipping other mods, __result misuse, transpiler fragility, patching generic/overloaded methods); performance spikes and long ticks (per-tick allocations, O(N^2) scans, LINQ in hot paths, whole-map scans, unbounded caches/dictionaries, static state leaking across games/maps); determinism and RNG (Rand without seeding, Rand.PushState misuse, order-dependent dictionary/hashset iteration, thread-unsafe statics); minified/strange defs (missing fields, MayRequire, ThingDefs without comps, defs with odd stack/size, def names referenced from C# that may not exist, XML patch xpaths that silently match nothing); static caches not cleared on game load / new game; GameComponent/MapComponent lifetime.

Output format: RANKED findings, most severe first. For EACH finding give: (1) a short title, (2) severity (crash / data loss / wrong behaviour / perf / cosmetic), (3) the exact file path and line number (or method name) it implicates, quoting the 1-3 offending lines, (4) a concrete step-by-step repro a tester could follow in-game or with a script, (5) your confidence (high/medium/low) and why. Do not pad: skip anything you cannot tie to code you can SEE in the files below. Review ONLY against the code you can see; when a claim depends on code not in this slice, put it under a final heading "Outside this slice" rather than guessing. Give at least 10 findings if that many real ones exist, but never invent one to reach a count.
```

Inlined files: slice A = the 38 C# files of `Contagion/Source/` (incl. `Kernel/`) with no XML and no Harmony; slice B = Contagion XML defs and patches (hediffs, ThingDefs, fauna, biome, `Patches/*.xml`) with no C#. Neither saw the other half, which is why several B guesses about C# are unanswerable from the slice.

## Verified

**V1. Cancelling an injection still injects (A1). Severity: wrong behaviour / lost item.**
`Source/JobDriver_RM_InjectGenomeSample.cs:48-65`. The gestation start and sample destroy sit in `inject.AddFinishAction`. Toil finish actions run on every end (success, interrupt, `FailOn`), not just success. The host-eligible `FailOn` is the only filter, so a player re-ordering the colonist mid-delay (or any job interrupt) starts gestation and consumes the sample with the 180-tick delay unfinished.
Repro: order injection, wait for the progress bar, order the colonist elsewhere; host has `RM_AmoebaGestation`, sample gone.
Fix: move the body to a following `ToilCompleteMode.Instant` toil's `initAction` (exactly as `JobDriver_RM_SampleDraftprint` does at lines 45-62).

**V2. Injection ignores range (A5). Severity: wrong behaviour (low).**
Same file, delay toil lines 44-47 has no `FailOnCannotTouch` (the draftprint scan toil has one at line 37). The host is a wandering wild animal, so it can drift away during the 180 ticks, and gestation still starts remotely. No script needed.
Fix: `inject.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);`.

**V3. Setting off does not stop a running injection (A7). Severity: wrong behaviour (low).**
Same file. `RM_ContagionSettings.genomeOrganGrowingEnabled` is read only in `FloatMenuOptionProvider_InjectGenomeSample.cs:28`; neither `MakeNewToils` nor `TryBeginGestation` checks it.
Fix: `this.FailOn(() => !RM_ContagionSettings.genomeOrganGrowingEnabled);` in `MakeNewToils` (one line, pairs with V1/V2).

**V4. Four unreachable shelter cells starve the dive forever (A10). Severity: wrong behaviour.**
`RM_GameCondition_ContagionBurn.cs:88-96` collects the first 5 sheltered radial cells; `Kernel/RM_SkyKernel.cs:242-251` `PickDive` tries only the first 4. `RadialCellsAround` order is fixed, so every 250-tick pulse retries the same 4. A UV-shy native next to a sealed roofed room (the nearest 4 sheltered cells are inside it) never gets a dive job while a reachable roof sits 6-14 cells away; it takes Burn damage each pulse until dead.
Repro: native beside a walled, roofed room with no animal-passable door, reachable canopy farther out, start a Burn, watch no Goto job issue.
Fix: collect up to ~16 cells, `sheltered.Shuffle()` (or rotate by `TicksGame / Interval`) before `PickDive`; keep the 4-try budget. Update `ContagionFuzz` pick family expectation.

**V5. Loading mid-tell resets the sink animation (A13). Severity: cosmetic.**
`RM_MapComponent_ContagionSky.cs:107-109`. `wasTellsBegun` and `tellsBeganTick` are unsaved (comment line 29: "so not saved"), but `tellsBegun` is saved. First poll after load sees `tellsBegun && !wasTellsBegun`, sets `tellsBeganTick = now`, so `SinkFraction` jumps from the window-start fallback (e.g. 1.0) back to ~0 and re-settles over 250 ticks.
Fix: in `ExposeData` add `if (Scribe.mode == LoadSaveMode.PostLoadInit) wasTellsBegun = tellsBegun;` (leaves `tellsBeganTick = -1`, which the kernel already handles as "from window start").

**V6. Wombpod sac never hatches (B2). Severity: wrong behaviour (the sac is the intended Wombpod harvest -> host path).**
`Defs/ThingDefs/RM_WombpodSac.xml:32`. Parent `ResourceBase` (Core `Items_Resource_Base.xml`) sets no `tickerType`, so it is `Never`; `CompHatcher` ticks via `CompTickRare`. Vanilla egg defs set `<tickerType>Rare</tickerType>` (Items_Resource_AnimalProduct.xml:88). Nothing in the repo adds a ticker to this def (grep of `RM_WombpodSac` outside the def file).
Repro: spawn a sac outside any container, advance 4 days, still a sac.
Fix: add `<tickerType>Rare</tickerType>` after `<thingClass>`.

**V7. Three Unfinished attack hediffs name an abstract verb class (B1). Severity: crash (exception on verb init).**
`Defs/HediffDefs/RM_UnfinishedHediffs.xml:47,68,89` (`RM_UnfinishedClaw/Spike/Fang`) use `Verb_MeleeAttack`, which is `public abstract class` in Core (`Source/RimWorld/Verb_MeleeAttack.cs:8`). Every Core melee verb def uses `Verb_MeleeAttackDamage`. `VerbTracker` instantiates `verbClass` through its creator (lines 208/230), which throws for an abstract type. `CompRandomizeUnfinished` and `validation.py` LIMB_POOL pick these hediffs, so a fraction of spawned Unfinished carry them. (Not confirmed in game; the abstractness and the call site are.)
Fix: change the class to `Verb_MeleeAttackDamage` in three places. Caveat: the hediff verb may also need a `tools` shape (as the grown limbs use) for a working melee attack; that part needs one bridge/quicktest look.

**V8. Unraveling (the mandatory lifespan) is curable by item (B3). Severity: wrong behaviour (breaks the "short-lived by law" ban 3).**
`Defs/HediffDefs/RM_UnfinishedHediffs.xml:166-195` sets `tendable=false` only. `everCurableByItem` defaults true (`HediffDef.cs:64`); `HealthUtility` line 736 selects any visible `isBad`, `everCurableByItem`, can-kill hediff for the healer-mech-serum path. `RM_ContagionTouched.xml:85` already sets the flag false, so the mod knows the pattern.
Fix: add `<everCurableByItem>false</everCurableByItem>` to `RM_UnfinishedUnraveling` (one line).

**V9. Monstrous `MaxHitPoints` offset does nothing (B5). Severity: wrong behaviour (cosmetic effect, stat is dead weight).**
`RM_UnfinishedHediffs.xml:150`. Part health is `BodyPartDef.hitPoints x Pawn.HealthScale` (`Pawn.cs:2501`, `GetMaxHealth`); the `MaxHitPoints` stat feeds `Thing.MaxHitPoints` (`Thing.cs:105`), not pawn parts. Delete the line (or pick a real lever such as an `IncomingDamageFactor` offset if toughness was intended; that is a design call).

(V1-V3 are one job file; they may be filed as one item with three fixes.)

## Plausible

- **P1. Caravan completion leaves a spent living host (A2).** `Hediff_AmoebaGestation.cs:113-114` sets `completed = true` before `AmoebaHostUtility.CompleteGestation`, which returns at `AmoebaHostUtility.cs:125` when `MapHeld == null`. Code is as described and the latch persists. Reachability: needs the host unspawned off-map with hediffs ticking; `RM_BloodyMess` is Wildness 0.98 and `trainability None`, so caravan carriage is unlikely but not excluded (e.g. pod/transport). Fix if wanted: set `completed` only after the map check, or return a bool.
- **P2. Failed surgery over an existing prosthetic could still grant the match bonus (A4).** `Recipe_InstallGrownBodyPart.cs:56` tests `PartIsMissing`, which is false for a part carrying an added part, so a failed natural-over-bionic install passes. Needs the vanilla failure path to leave the prosthetic in place (engine behaviour) and a self-donor match. Safer check: compare hediff set before/after (`HasDirectlyAddedPartFor(part)` false after).
- **P3. Shaking rattlers vanish if the biome extension disappears mid-shake (A9).** `RM_MapComponent_ContagionSky.cs:111-113`: `lastShaking` flips false, then returns before dirtying the mesh when `ext == null`. Code real; trigger (map biome changing under a live map) is nearly unreachable outside dev tools.
- **P4. Organ patch replaces another mod's explicit `workerClass` (B4).** `Patches/OrganInstallGenomeMatch.xml` `match` branch does an unconditional Replace. The file header says the match branch only fires if a mod added an explicit worker earlier; vanilla fires `nomatch`. So it clobbers only a rare pre-patching mod and is a deliberate defensive branch; consider guarding with `PatchOperationFindMod` or dropping `match` entirely. Low.

## Refuted

- A3 stackLimit 0 mulch loop: shipped `RM_ContagionMulch.xml:27` sets `stackLimit` 75; needs hostile external def data.
- A6 touched ignores `burnEnabled`/`burnDamageFactor`: true that they are not read, but touched has its own `touchedEnabled` and `touchedExposureFactor` settings and the item explicitly ("Bloom time, stronger in burn") ties exposure to the Burn weather; the slider label promises no *damage*, not no exposure. Design call, not a code defect. (If the owner wants it gated, one `&& RM_ContagionSettings.burnEnabled` at `RM_ContagionTouched.cs:298`; the Repulsor-held Burn with `burnEnabled` off is the only reachable divergence.)
- A8 camera-dependent `Rand` use: RimWorld's sim RNG is not replay-deterministic (reseeded on load, vanilla fleck code does the same). Not a bug.
- A11 contact cross-product perf: `OccupiedRect` is a struct, no allocation, 250-tick poll; hundreds x hundreds is ~1e5 cheap checks. Negligible.
- A12 growth floor 0.15: behaviour exists (`CompZhoolHaze.cs:167`) and contradicts the header's "keeping its growth", but a visible-seedling floor looks intentional and harmless. Doc/intent mismatch at most.
- A14 haze message cooldown static: `RM_ZhoolHazeKernel.MessageDue` already resets when the clock runs backwards; worst case is one extra or missed cosmetic message after a process restart/cross-game load. By design (header line 74).
- (Outside-slice A note on `AllowStackWith` for sample comps and B note on duplicate parent comps) not graded; see leftovers.
- (B has no further numbered findings.)

## Outside this slice (leftovers worth a look)

- Stacking: `CompGenomeSample`, `CompGenomeMatched`, `CompDraftprint` hold per-item state; check the item defs' `stackLimit` (if 1, moot) before worrying about `AllowStackWith`/`PostSplitOff`.
- `HediffComp_RM_ContagionTouched.CompPostTickInterval` always rolls `MTBEventOccurs(..., Interval)` regardless of `delta`; harmless unless world/caravan pawns tick with large deltas.
- Removal safety (hediff/building classes in saves with the mod removed) not examined.
- B asked about the Bulloo brainless bodies, `GU_*` terrain / `AB_OcularForest` dependencies, and the `mandrake.rm.biomes` vs `mandrake.rm.therot` gate: all need the unseen halves; not graded here.
