# LeaningScrub edge-case consult, graded against the code

- Date: 2026-10-16
- Model: gpt-6.1-sol, high
- Slices: LeaningScrub_A (14 findings), LeaningScrub_B (12), LeaningScrub_C (2 + 3 "outside" notes)
- Raw answers: `design/RimMandrake/gpt_consults/raw/LeaningScrub_{A,B,C}_2026-10-16.md`
- Grader: Sonnet 5.5, read-only trace of `src/RimMandrake/LeaningScrub/` (no game, no bridge run). Repros below are traced, not executed.
- Tally: **15 VERIFIED, 6 PLAUSIBLE, 7 REFUTED** (28 numbered findings). IDs are slice letter + GPT's number (A5 = slice A finding 5).

## Question used

Same text for A, B, C except the final slice name on line 1.

```
SUBJECT: LeaningScrub (RimWorld 1.6 mod, C# + XML defs). Restate this subject on the first line of your answer so we can detect crossed answers. This is slice "LeaningScrub_A".

You are a hostile, senior RimWorld modder and Harmony expert reviewing this mod. Find UNUSUAL bugs and edge cases, not style. Probe in particular: save/load round trips (ExposeData, Scribe_Collections, null lists after load, fields not saved, PostLoadInit ordering, loading a save that has the mod's data but the mod now disabled, savegame removal safety); tick-rate/pause/speed-3/ultrafast behaviour (Tick vs TickRare vs TickLong, intervals skipping, catch-up after map load); multiple maps and caravans, temporary/pocket/space maps, world-map tiles and biome changes mid-game; pawns arriving/leaving/spawning/despawning mid-effect; death/despawn/destroy/discard during effects (stale references, Thing.Destroyed vs Spawned, map == null, Position invalid); null and out-of-bounds cells (InBounds, CellIndices, edge-of-map, off-by-one in grids, negative or overflow indices, integer overflow, float NaN/Inf, division by zero); mod-setting toggles mid-game (turning a feature off while state exists, on again); Harmony patch ordering and conflicts with vanilla and the DLCs (Biotech, Anomaly, Odyssey, Royalty, Ideology) and other common mods (prefix returning false skipping other mods, __result misuse, transpiler fragility, patching generic/overloaded methods); performance spikes and long ticks (per-tick allocations, O(N^2) scans, LINQ in hot paths, whole-map scans, unbounded caches/dictionaries, static state leaking across games/maps); determinism and RNG (Rand without seeding, Rand.PushState misuse, order-dependent dictionary/hashset iteration, thread-unsafe statics); minified/strange defs (missing fields, MayRequire, ThingDefs without comps, defs with odd stack/size, def names referenced from C# that may not exist, XML patch xpaths that silently match nothing); static caches not cleared on game load / new game; GameComponent/MapComponent lifetime. 

Output format: RANKED findings, most severe first. For EACH finding give: (1) a short title, (2) severity (crash / data loss / wrong behaviour / perf / cosmetic), (3) the exact file path and line number (or method name) it implicates, quoting the 1-3 offending lines, (4) a concrete step-by-step repro a tester could follow in-game or with a script, (5) your confidence (high/medium/low) and why. Do not pad: skip anything you cannot tie to code you can SEE in the files below. Review ONLY against the code you can see; when a claim depends on code not in this slice, put it under a final heading "Outside this slice" rather than guessing. Give at least 10 findings if that many real ones exist, but never invent one to reach a count.
```

Inlined files (inferred from what each answer could cite; the file lists are not in the question files): A got the Source/*.cs for GenStep_SweetlineTrees, VenomvineFourForms, Ripple, ScrubInjections, VenomvineRooms, SmotherCraft, CallingPyre, RunwayBloom, SweetlineScratching, TheLean, FireStamp plus Kernel/RM_BlazeKernel and RM_FormsKernel. B got RM_VenomvineForms.cs and RM_SweetlineGuardians.cs (kernels for Forms/Guardian/Lean absent). C got XML only (biome, Salvessa, VenomvineFourForms, VenomvineForms, FuzzFlora) and a validation doc, no C#.

## Verified

All are low or moderate impact; none is a crash or save-corruption bug. Ordered by player-visible reach.

### V1. Crown mob cap is exceeded (A5) - wrong behaviour, moderate
- `Source/RM_VenomvineRooms.cs:128-151` (`RM_MapComponent_CrownMob.MapComponentTick`), also `IsIdle`/`HeadingTo` 154-166.
- Repro: Stall on, a crown stand (`maxMobbers=30`, `drawRadius=40`, `MobInterval=250`) with 60 idle wild Dustflutters inside 40 cells. Pass 1 sends 30 (`held` hits 30). Pass 2, 250 ticks later: the 30 in flight are on a `Goto` job, so `!IsIdle` skips them before `HeadingTo` and they are never counted; `held` restarts at 0 and 30 more are sent. Result: 60 mobbers against a cap of 30. Also, `held < maxMobbers` ends the loop before later residents are counted, so order matters.
- Evidence: counting happens only in the `distSq <= settleSq` and `TrySendToStand` branches; in-transit pawns hit `continue` at the `!IsIdle(p)` test first.
- Fix (offline-provable via a pawn-list unit test of a Verse-free helper, or bridge): count heading pawns, `if (HeadingTo(p, stand, settleSq)) { held++; continue; }` placed right after the `settleSq` branch and before the `drawSq/IsIdle` test; ideally a first loop that counts residents and in-flight pawns before any dispatch.

### V2. Guardian release prunes before it releases (B5) - wrong behaviour, low-moderate
- `Source/RM_SweetlineGuardians.cs:480-505` (`ReleaseAll`, `PostDestroy`), `Prune` 194-205.
- Evidence: `ThingWithComps.Destroy` runs `DeSpawn` first, then `PostDestroy(mode, previousMap)`. By then `parent.MapHeld` is null while every warden's `MapHeld` is the map, so `Prune`'s `p.MapHeld != parent.MapHeld` removes all of them. `ReleaseAll`'s loop (clear `homeTree`, `WakeUp`) and the "lost their tree" message (`guardians.Count > 0`) therefore never run. Wake-up then depends on each warden's own `CompTick` (every 250 ticks, `RM_CompRoostGuardian` 662-667) noticing `homeTree.Destroyed`.
- Repro (bridge): spawn a tree with wardens, destroy the tree, observe no "bark-wardens ... have lost their tree" message. Save within 250 ticks and reload: `homeTree` resolves to null, so the `homeTree != null` guard skips `WakeUp` and the sleepers stay dormant unless a roost within 60 cells has a vacancy (GPT's save claim; plausible, window is narrow).
- Fix (2 lines): in `ReleaseAll`, `if (parent.MapHeld != null) Prune();`, and in `RM_CompRoostGuardian.CompTick`'s null-home branch also `WakeUp` a dormant pawn that has no home (`dormant != null && !dormant.Awake`).

### V3. A tamed lead warden silences trunk-watching (B8) - wrong behaviour, low
- `Source/RM_SweetlineGuardians.cs:322-332` (`IsLead`).
- Evidence: `IsLead` takes the first spawned, living pawn in `guardians` with no `Faction` or `homeTree` test. A tamed lead clears its own `homeTree` in `CompTick` (655-659) but stays listed until `Prune` (only `CompTickLong` every 2000 ticks, `LiveCount`, `HasVacancy`). The other wardens get `IsLead == false`, so `WatchTheTrunk` is skipped for up to 2000 ticks.
- Repro (bridge): tree with 3 wardens, tame `Guardians[0]`, have a colonist cut/harvest the tree; disturbance does not rise until the next prune.
- Fix (1 line): `if (p != null && p.Spawned && !p.Dead && p.Faction == null)` in `IsLead`.

### V4. Master switch freezes the Gale latch (B9) - wrong behaviour, low
- `Source/RM_VenomvineForms.cs:576-601` (`MapComponentTick`).
- Evidence: the early `return` on `!modEnabled` sits above the `wasGale = gale` update, so the latch is stale while off. Off during a Gale, back on mid-Gale: `gale && !wasGale` fires a spurious `GaleOnset` (Walk and Shed) with no weather change. Off before a Gale that begins and ends while off, back on during a second one: its onset is missed.
- Fix (3-4 lines): update `wasGale` before the `modEnabled` return, or reset it to the current state on the first enabled tick.

### V5. Disabled contact venom still spends the scratch cooldown (B11) - wrong behaviour, low
- `Source/RM_VenomvineForms.cs:627-631`, `651-654`, `Scratch` 692-700.
- Evidence: `nextThornTick[p]` / `nextLitterTick[p]` are written before `Scratch` returns early on `!contactVenomEnabled` or a zero amount. Re-enable and the pawn is protected for one `contactIntervalTicks` (2500 on the forms XML) for hits that never landed.
- Fix (about 6 lines): make `Scratch` return bool and commit the clock only when damage was dealt, or skip the whole thorn/litter branch when `contactVenomEnabled` is false.

### V6. Erupt animals already fleeing never take off (A9) - wrong behaviour, low
- `Source/RM_RunwayBloom.cs:206-216` (`Answer`), `FleeFrom` 301-304.
- Evidence: `FleeFrom` returns null when `CurJob.def == JobDefOf.Flee`; `Answer` then returns before `RM_Flight.TryLaunch`. A second bloom during a flee leaves a flyer grounded.
- Fix (3 lines): `if (flee == null) { if (ext.response == RM_RunwayBloomResponse.Erupt && a.CurJob?.def == JobDefOf.Flee) RM_Flight.TryLaunch(a); return; }` (TryLaunch after the job exists is the documented order).

### V7. Smother job ignores the setting once under way (A6) - wrong behaviour, low
- `Source/RM_SmotherCraft.cs:183-203` (finish `initAction`), `MakeNewToils` 160-180; setting text `RM_LeaningScrubMod.cs:345` ("Off: no new claims").
- Evidence: gating is only in `RM_FloatMenuOptionProvider_Smother` and `PassRuns`. A job already queued when the player switches the feature off consumes the blanket and calls `StartSmother()`.
- Fix (2 lines): `this.FailOn(() => !RM_WindCalendar.On(RM_LeaningScrubSettings.smotherCraftEnabled));` at the top of `MakeNewToils`.

### V8. Sweetline tree registry keeps empty entries per Map (A12) - memory, low
- `Source/RM_SweetlineScratching.cs:82-89` (`Deregister`); registry cleared only by `CheckGame` on game change.
- Evidence: `list.Remove(tree)` leaves `trees[map]` with an empty list; the static dictionary holds a strong reference to every Map that ever had a tree until the next game load, including discarded temporary maps. Both callers (GenStep `Fits`, `Scratching` line 126) already handle a null or empty `TreesOn`, so removing the entry is safe.
- Fix (1 line): in `Deregister`, `if (list.Count == 0) trees.Remove(map);` after the decrement.

### V9. Bloom orders override manhunting wild animals (A8) - wrong behaviour, low
- `Source/RM_RunwayBloom.cs:150-178` (`Bloom`, `Answer`), `StartSway` 248-254.
- Evidence: neither `Bloom` nor `Answer` tests `a.InMentalState`; `StartJob(..., InterruptForced)` replaces the mental-state job with Flee or `Wait_MaintainPosture`. (`RM_Ripple.ShouldHide` explicitly excludes mental states, so the convention exists.)
- Fix (1 line each): add `|| a.InMentalState` to the filters in `Bloom` and `Answer`.

### V10. Pyre "too little caught" warning tests the wrong thing (A7) - cosmetic, low
- `Source/RM_CallingPyre.cs:130-134`, `209`.
- Evidence: the warning compares total fires `lit` with `MinOpenFires` (5), but `RM_BlazeKernel.FindBlaze` needs 5 fires within `ClusterRadius` 6 of one fire. The default `callingPyreRadius` is 14 (slider 4-30), and `Ignite` takes nearest plants but nothing guarantees clustering, so scattered fires pass the message test yet draw nobody.
- Fix: after `Ignite`, call `map.GetComponent<RM_MapComponent_FireStamp>().FindBlaze().IsValid` and use that for `thin`; a few lines, offline-provable via the kernel.

### V11. Tree gen step destroys items/plants then aborts (A1) - data loss in a narrow case
- `Source/RM_GenStep_SweetlineTrees.cs:127-141` (`Plant`), `Fits` 94-122.
- Evidence: `Plant` destroys plants/items/filth on the cell, then returns false if anything else (pawn, blueprint, non-edifice thing) remains. `Fits` does not reject occupied cells. In real map generation this is nearly harmless (nothing else stands there); the live reach is `ProofMapStep` on a played map.
- Fix (3 lines): reject in `Fits` when any non-(plant/item/filth) thing is in `c.GetThingList(map)`, or test occupancy before destroying.

### V12. Proof hooks destroy bystanders and act map-wide (A10, B1, B2, B3) - diagnostic side effects, low
- `RM_CallingPyre.cs:277-281` (`ProofPyre`), `RM_FireStamp.cs:363` (`ProofStamp` finally): destroy every fire within 30 cells, not only fixture fires.
- `RM_VenomvineForms.cs:994` (`Stand`: `c.GetPlant(map)?.Destroy()` on a spot where `FindSpot` allows plants) and `1099-1112` + `1212` (hoard case adds every steel stack within 4 cells to `made`, destroyed in `finally`, also in `off` mode).
- `ProofForm` sworn/thorn cases call `comp.SweepThorns` with `contactVenomEnabled = true`, which scratches any real pawn standing in marked thorns on the map.
- Repro: run the proofs on a played map with an unrelated fire, plant, steel stack, or a pawn on thorns inside the radii.
- Fix: track fires/steel by thing ID created or present-before (snapshot ids before, destroy only new); have `FindSpot` also reject cells with plants/items. Proofs only run from the bridge on throwaway maps, so rank last.

## Plausible

- **A3 Ripple cleanup misses arrivals (`RM_Ripple.cs:89-93`)**: the `!on && !anyHidden` early return is real, and a hidden wild pawn arriving from another map keeps `RM_RippleHidden` (no expiry in `RM_LeaningScrub_Ripple.xml`). Needs a wild animal that changes maps with the hediff, which vanilla rarely does. Cheap fix: drop the early return, or scan only when `mapPawns` count changed.
- **A4 Captured campers keep free food/rest (`RM_ScrubInjections.cs:407-416`)**: no prisoner/lord check, so a prisoner of a non-hostile camp faction is refilled every 2500 ticks. Hinges on `Pawn.HostileTo` for arrested pawns, which I did not trace. Fix would be `|| p.IsPrisoner || p.IsSlave`.
- **A11 `FindBlaze` is O(n^2) before the stamper check (`RM_BlazeKernel.cs:25-33`, `RM_FireStamp.cs:121-141`)**: true as written, every 600 ticks; costs about 16M distance tests at 4000 fires, so only a vast wildfire. Cheap guard: bail out of `ConvergePass` when no stamper is `Available` before calling `FindBlaze`.
- **A13 `Applies` cached for component lifetime (`RM_TheLean.cs:50-60`)**: stale only if a map's biome changes in place or the extension is edited at runtime, neither of which vanilla does.
- **B4 Hoarded items are never ticked (`RM_VenomvineForms.cs:260-290`)**: `RM_CompHoard` holds items in a `ThingOwner` and never forwards `ThingOwnerTick`, so absorbed meat/apparel does not rot or deteriorate while held, then returns fresh on cut. True of the code; whether that is intended (a "treasure chest" per the pitch) is an owner call, and engine ticking of a non-ticking holder's contents was not checked.
- **B12 `SweepQuench` is Q x F (`RM_VenomvineForms.cs:785-810`)**: early-outs on no fires and only ready stands scan; needs thousands of both to matter.

## Refuted

- **A2 strangler hits a building on another map**: needs a wall or tree to be despawned and respawned on another map at the same coordinates; walls and trees are not minifiable or transferable, so it is unreachable without a script.
- **A14 `LashReady` int overflow**: `int.MaxValue` ticks is about 596 in-game years; unreachable.
- **B6 transferred pawn scratched by the old map**: requires a foreign damage callback to move a pawn between maps during the same synchronous sweep; no such path in this mod.
- **B7 nearby-roost exclusion bypassed**: true in code (`PostSpawnSetup` and `TryRehome` skip `OtherRoostTooClose`), but the map step spaces trees 40 cells apart and `watchRadius` is 9, so shipped content never has two roosts within range; only dev spawns do.
- **B10 contact clocks not saved**: acknowledged tradeoff in the field comment (`RM_VenomvineForms.cs:520-522`) and in `MapComponent_ContactVenom`; by design.
- **C1 Strangler/Weeper/Lure missing from `wildPlants`**: known and already in front of the owner, `design/RimMandrake/venomvine_design_2026-10-16.md` ("Three forms never grow wild", recommended option A). Not a new finding.
- **C2 duplicate `sowTags` in Salvessa**: the empty `Inherit="False"` node plus a populated one is the shipped pattern (copied 1:1 from the canon plant); the last list wins, and the latest `Player.log` shows Salvessa loading with no duplicate-field or XML error.

## Outside this slice (leftovers worth a look, not findings)

- Weeper description says "It is not dangerous to pass" but `RM_VenomvineFourForms.xml:112-118` gives it `CompProperties_ContactVenom` (3 damage per 2500 ticks) and a body-size barrier. Text or comp is wrong; owner call. Plausible.
- Dripping venomvine has no explicit `harvestTag`; `PlantProperties.harvestTag` defaults to "Standard", so this is probably fine (not traced in the engine).
- Whipfuzz sets `harvestYield` 1 but no `harvestedThingDef` (`RM_LeaningScrubFuzzFlora.xml:55-57`, parent `PlantBase` has none). Probably harvest-inert; check `measure` / live def for a config-error line.
- Not judgeable here: Harmony patches and vanilla/DLC compat, `RM_CompGuardianDormant` wake semantics, `RM_MentalState_ScopedAggression`, mod-removal safety.
