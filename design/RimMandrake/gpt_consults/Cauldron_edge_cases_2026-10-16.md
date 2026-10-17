# Cauldron edge cases - graded GPT bug hunt

- Date: 2026-10-16. Model: gpt-6.1-sol, reasoning high. Slices: Cauldron_A, Cauldron_B (source `src/RimMandrake/Cauldron/`).
- Raw answers: `design/RimMandrake/gpt_consults/raw/Cauldron_{A,B}_2026-10-16.md` (10 + 8 findings). Graded against the repo by reading code, callers and XML; nothing was run.
- Grades: VERIFIED (traced, would stake the repro), PLAUSIBLE (code is as described, impact depends on engine/design), REFUTED.
- Totals (by finding id, A1-10 + B1-8): 8 VERIFIED rows (V8 merges A7+B3), 3 PLAUSIBLE rows (P2 merges A2+B2), 7 REFUTED.

## Question used

Identical for both slices apart from the slice name on line 1; the `{EXTRA}`-free prompt. Each slice inlined a subset of the Cauldron Source/ Kernel/ and Defs/ files.

```
SUBJECT: Cauldron (RimWorld 1.6 mod, C# + XML defs). Restate this subject on the first line of your answer so we can detect crossed answers. This is slice "Cauldron_A" (or "Cauldron_B").

You are a hostile, senior RimWorld modder and Harmony expert reviewing this mod. Find UNUSUAL bugs and edge cases, not style. Probe in particular: save/load round trips (ExposeData, Scribe_Collections, null lists after load, fields not saved, PostLoadInit ordering, loading a save that has the mod's data but the mod now disabled, savegame removal safety); tick-rate/pause/speed-3/ultrafast behaviour (Tick vs TickRare vs TickLong, intervals skipping, catch-up after map load); multiple maps and caravans, temporary/pocket/space maps, world-map tiles and biome changes mid-game; pawns arriving/leaving/spawning/despawning mid-effect; death/despawn/destroy/discard during effects (stale references, Thing.Destroyed vs Spawned, map == null, Position invalid); null and out-of-bounds cells (InBounds, CellIndices, edge-of-map, off-by-one in grids, negative or overflow indices, integer overflow, float NaN/Inf, division by zero); mod-setting toggles mid-game (turning a feature off while state exists, on again); Harmony patch ordering and conflicts with vanilla and the DLCs (Biotech, Anomaly, Odyssey, Royalty, Ideology) and other common mods (prefix returning false skipping other mods, __result misuse, transpiler fragility, patching generic/overloaded methods); performance spikes and long ticks (per-tick allocations, O(N^2) scans, LINQ in hot paths, whole-map scans, unbounded caches/dictionaries, static state leaking across games/maps); determinism and RNG (Rand without seeding, Rand.PushState misuse, order-dependent dictionary/hashset iteration, thread-unsafe statics); minified/strange defs (missing fields, MayRequire, ThingDefs without comps, defs with odd stack/size, def names referenced from C# that may not exist, XML patch xpaths that silently match nothing); static caches not cleared on game load / new game; GameComponent/MapComponent lifetime.

Output format: RANKED findings, most severe first. For EACH finding give: (1) a short title, (2) severity (crash / data loss / wrong behaviour / perf / cosmetic), (3) the exact file path and line number (or method name) it implicates, quoting the 1-3 offending lines, (4) a concrete step-by-step repro a tester could follow in-game or with a script, (5) your confidence (high/medium/low) and why. Do not pad: skip anything you cannot tie to code you can SEE in the files below. Review ONLY against the code you can see; when a claim depends on code not in this slice, put it under a final heading "Outside this slice" rather than guessing. Give at least 10 findings if that many real ones exist, but never invent one to reach a count.
```

## Verified

Paths relative to `src/RimMandrake/Cauldron/`.

**V1 (B5) Roasted tsevrix still gives "ate raw food" mood.** wrong behaviour, medium. `Defs/ThingDefs_Items/RM_CauldronFloraItems.xml:53` sets `<tasteThought>AteRawFood</tasteThought>`; and the def inherits it anyway from Core `PlantFoodRawBase` (Items_Resource_RawPlant.xml:21). Repro: roast pulp, eat it, read memories. Fix: replace the line with `<tasteThought IsNull="True"/>`; offline provable.

**V2 (B6) Description promises a campfire route that does not exist.** wrong behaviour (text), low. `Defs/ThingDefs_Items/RM_CauldronFloraItems.xml:7` says "at a stove or campfire"; `Defs/RecipeDefs/RM_TsevrixRoast.xml:22-25` lists only FueledStove and ElectricStove. Core meal recipes are also stove-only and Campfire has no bill table, so the recipe is right and the text is wrong. Fix: change the description to "at a stove".

**V3 (B4) Biome still weights vanilla DryThunderstorm.** wrong behaviour, low-medium. `Defs/BiomeDefs/RM_Cauldron.xml:134` `<DryThunderstorm>1</DryThunderstorm>` while the comment at lines 125-127 says the four ruled weathers replace the donor block and Fog/Clear/Rain/Snow are zeroed. No Cauldron doc or comment justifies it (looks like a donor leftover). Repro: log selected weather over many transitions on a Cauldron map. Fix: set to 0 (confirm with owner that lightning is not wanted).

**V4 (A5) Vent gardens at mapgen call TryPlant on out-of-bounds cells.** wrong behaviour / error log, medium. `Source/RM_CondensateGardens.cs:107-108` iterates `RadialCellsAround(vent.Position, ext.ventRadius)` with no InBounds check, and `TryPlant` (line 158) starts with `c.GetPlant(map)`; the ongoing path (line 145) does check. Vents are placed with an 8-cell margin (`RM_CauldronVents.cs` EnsureGenerated, `Rand.RangeInclusive(8, size-8)`) but `RM_GiantToxicFlower` has `ventRadius` 9 (`Defs/ThingDefs_Plants/RM_CauldronFlora.xml:441`, RecentBlowout, and placed[0] is always given a recent blowout). So a vent near an edge reaches x/z -1 or size+1. What Verse does with the cell (error log vs wrapped index) is engine behaviour; the missing guard is not. Fix: first line of TryPlant `if (!c.InBounds(map)) return false;`.

**V5 (A1) Gas drift crosses sealed diagonal corners.** wrong behaviour, low. `Source/Kernel/RM_VentGasKernel.cs:229-230` `Drift` checks only the destination `canMoveTo(j)`; heading dx/dz include diagonals (lines 40-41); caller `RM_VentGas.cs:110` runs it whenever wind is up. Kernel-only repro: 3x3 grid, Add(0,100), Drift(0,1, i=>i!=1&&i!=3) moves 25 into cell 4. Fix: for diagonal headings also require `canMoveTo` of at least one (vanilla-like: both) of the two cardinal cells `Neighbour(i,dx,0)` and `Neighbour(i,0,dz)`. About 5 lines.

**V6 (A8) RM_VentGasCells.Add overflows int before clamping.** wrong behaviour, latent. `Source/Kernel/RM_VentGasKernel.cs:188` `Adjusted(Density[i] + amount, ...)`; `Add(0, int.MaxValue)` wraps negative, cell becomes 0. No production caller passes more than a few hundred (emit <=~50, debug 200, overflow <=255), so it only bites the fuzz or future callers. Fix: `int v = Adjusted((int)Math.Min((long)Density[i] + amount, int.MaxValue), out overflow)`.

**V7 (B8) hushedThisFalter is not saved.** cosmetic. `Source/RM_CauldronVents.cs` `RM_MapComponent_CauldronVents.ExposeData` (line ~274) saves `generated` and `falterNotified` only; the vent inspect string (line 221) reads the count. After save/load mid-falter it reads 0 and renewals do not recount (line 340 skips pawns already on Wait_MaintainPosture). Fix: `Scribe_Values.Look(ref hushedThisFalter, "rmVentHushed", 0);`.

**V8 (A7 + B3) Disabling a setting does not stop a job already issued.** wrong behaviour, trivial. A7: `RM_CompVexxissBehaviour.cs:99,216-220` gate only job creation; an AttackMelee job lasts up to `attackJobExpiryTicks` 2500. B3: `RM_CauldronVents.cs` drink driver puts `AddFailCondition(!vexxissDrinksVentsEnabled)` on the drink toil only (line ~160), not on the GotoThing toil. Bounded and self-healing; low value. Fix: B3 is one line, `this.FailOn(() => !RM_CauldronSettings.vexxissDrinksVentsEnabled);` at the top of MakeNewToils; A7 would need a job-driver wrapper, skip.

## Plausible

- **P1 (B1) Metal load can kill an already-impaired pawn.** `Defs/HediffDefs/RM_VentMetalLoad.xml:83-92`: top stage offsets Breathing -0.15, BloodFiltration -0.3, Consciousness -0.1. Capacity offsets are additive and Breathing/BloodFiltration are vanilla lethal capacities, so a pawn with other lung/kidney damage can hit zero; healthy pawns cannot. Contradicts the file header's "cripples, does not kill" only for already-damaged pawns. Needs a live capacity check (bridge) to prove.
- **P2 (A2 + B2, same finding) Displaced drinker keeps suppressing/prying remotely.** `RM_CauldronVents.cs` drink `tickAction` (lines ~140-153) never rechecks adjacency after GotoThing. True in code, but vanilla displacement (knockback, carrying, teleport) ends the job; only a script that moves the pawn without ending the job triggers it. Fix if wanted: `drink.FailOn(() => !pawn.Position.AdjacentTo8WayOrInside(job.targetA.Thing))`.
- **P3 (A4) Vent-gas burning chain stops at water.** `RM_VentGas.cs:158` skips spawning a Fire on water terrain, and BurnScan propagates only from fires, so a gas cloud over a pond burns only its shore ring. Comment (lines 155-157) shows the water exclusion is deliberate (fire cannot live on water), so this is a design gap not a defect; owner ruling needed (e.g. burn the whole connected cloud in one scan).

## Refuted

- **A3 Poisoning own cell disables further poisoning**: true that a toxic centre cell returns early (`RM_CompVexxissBehaviour.cs:154`), but the patch is 3x3 around the first pulse, so after at most two steps the animal stands on clean water and pulses again. The "trigger is standing on named clean water" rule is the documented design (file header). No disable.
- **A6 Long-lived print blocks later short ones**: only one def (vexxiss, `Defs/ThingDefs_Races/RM_CauldronFauna.xml:322`) uses the comp and `printLifetimeTicks` is fixed at 60000 (`RM_CompProperties_VexxissBehaviour`), so insertion order is expiry order. Latent only if a second lifetime is ever added.
- **A9 BurnScan work unbounded**: per 30 ticks a list copy and 9 integer-cell checks per fire, and only while NonZero > 0; negligible even at thousands of fires.
- **A10 Quadratic RemoveAt(0) in the print ledger**: cap is 1500 references; worst full-burst shift is about 1.1M pointer moves (sub-millisecond), and expiry is spread over time.
- **B7 Hush jobs outlive the falter / setting**: designed. Comment above HushFauna says "hold still for a few seconds, renewed every 240 ticks"; `hushJobTicks` is 300 (`Defs/ThingDefs_Buildings/RM_CauldronVent.xml:66`), so leftovers last at most 5 s.
- **B outside-slice "RemeshAllMaps skips cleanup"**: `RM_AssayFlecks.Active` and `RM_DewfallSaturation.Active` are `table.Count > 0` / `dewGraphics.Count > 0` (def tables), not the toggles, so the early return only triggers when no def uses the feature. Not a bug.
- **A5 second half, "radius is configurable so any radius..."**: subsumed by V4 (only radius 9 on one plant triggers it).

## Outside this slice

- Save-removal safety, Harmony conflicts, reflection API drift against CreatureBehaviors (`RM_TrackGridBridge`, signatures not validated, no try/catch around Invoke), Suush `explodeOnKilled`, Odyssey toxic-water terrain refs without MayRequire (Every DLC is assumed, so not a defect per CLAUDE.md), `GU_`/`AB_` strings in CrystalMit: unexamined by this grading.
- `RM_TrackGridBridge.Surface` caches per props in a static dictionary keyed by def props: harmless across games (same defs), noted only.
