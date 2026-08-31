## spec
Full specs, both ruled by the owner 2026-08-30: `design/Jawa/covered_pit_traps_spec.md`
(the pit mechanics themselves) and `design/Jawa/trap_renaissance_spec.md` §4b (the
audit item this grew out of; its §2 trap-sense ruling — "Option C, gene + Ishko
layer" — is campaign-layer content, not in scope for this core-framework build).
Risk spikes proving the three hardest API shapes already compiled clean before
this item was filed: `src/RimMandrake/Spikes/` (Spike1 terrain-mimic print,
Spike2 holding-platform pattern, Spike3 — unrelated, Salvation engine).

Built: a new mod, **`RimMandrake Pits`**
(`src/RimMandrake/RimMandrake_Pits/`, packageId `mandrake.rimmandrakepits`),
species-agnostic core framework only — no theology, no species dig bonus, no
droid-labor wiring, no art (per spec §9, those are the campaign layer).

- **Dig-stage lifecycle** — `Building_PitDigSite` + `CompPitDigStage`. Placed
  via the normal Blueprint→Frame path (ConstructionSpeed) — placement is
  stage 1. Shallow tier (1 required stage) is done at placement; Deep (2) and
  Chasm (3, +shoring cost) need further "Dig Deeper" passes worked by
  `JobDriver_DigPitDeeper` (MiningSpeed-scaled, modeled on vanilla
  `JobDriver_RemoveBuilding`/`WorkGiver_FillIn`). Final stage transforms the
  site into its `openPitDef`.
- **Terrain-mimic covers** — `Building_OpenPit.Print()` samples
  `Position.GetTerrain(Map).graphic.MatSingle` and prints a plane with it
  (the exact verified trick from `Spikes/Spike1_TerrainMimic.cs`), only while
  the pit is covered/armed.
- **Mass-sum triggers** — `CompPitCoverTrigger` sums `Pawn.GetStatValue(StatDefOf.Mass)`
  (confirmed in RimWorld source to include body mass + gear/inventory) across
  every pawn on the pit's occupied cells, every 30 ticks, and springs the pit
  once the sum crosses the armed cover tier's rating (woven scrap 40kg /
  plank & lattice 120kg / reinforced frame 400kg — the spec's own §3 numbers,
  unranked-tuned, player-chosen via 3 "Arm Cover" gizmos on the open pit).
- **Struggle escape** — `PitEscapeUtility.EscapeChance` scores
  (bodySize − depthTier), health %, and manipulation into a clamped
  [0.02, 0.95] chance rolled every in-game hour
  (`Building_OpenPit.Tick()`/`RunStruggleInterval`); a failed attempt costs a
  small `RM_PinnedInPit` severity bump, a success ejects the pawn to an
  adjacent cell and clears it.
- **Fitting family** ("one framework, five faces", spec §5 title) —
  `CompPitFitting` + `PitFittingType` (Bare/Spiked/Oiled/Poison/Water/Oubliette)
  as DATA on one shared `Building_OpenPit` class, not five subclasses. Spiked
  = lethal damage on capture; Oiled = soaks + an Ignite gizmo
  (`FireUtility.TryStartFireIn`); Poison = `HediffDefOf.ToxicBuildup` accrual;
  Water = blocks the escape roll entirely + `RM_PitDrowning` (custom hediff —
  no vanilla "aquatic"/drowning hediff was found in source to reuse); Oubliette
  = `DamageDefOf.EMP` on mechanoid capture.
- **Holding-platform pit cell** — `Building_PitCell : Building_OpenPit`,
  modeled on the verified `Building_HoldingPlatform`/Spike2 pattern
  (`IThingHolderWithDrawnPawn`/`IThingHolder`, `ThingOwner`). No mass trigger
  (manually gated); `covered` is repurposed as GATE CLOSED per the owner's
  severity ruling ("the cover is the mercy... uncovered = actively harsh") —
  `RM_PitExposure` accrues while open, recedes while closed. 1x2 (holds one)
  and 2x2 (holds two) per spec §6 footprint capacity.

## Quicktest matrix — RAN 2026-08-30, on the 4-mod `pits` tier

Driven from the bridge on throwaway `start_debug_game_ready` maps (NOT the
campaign). Every verdict below is a raw field value the mod itself
`Log.Message`'d and the call returned in its own `effects.logs` — no bridge
`success:true` was accepted as evidence. The test hooks are real code and
shipped: `Source/Debug/PitDebugActions.cs`, eleven `DebugActionType.ToolMap`
leaves under `Actions\T: …`, reachable by x/z (arm each tier, uncover, set
depth, force scan, force struggle, advance dig stage, dump raw state).

### Five defects found and fixed, each proved by an A/B

1. 🔴 **Nothing loaded at all.** The three abstract parents carried
   `<defName>` instead of `Name=`, so no child resolved its parent — 74
   config errors, every `thingClass` null, and `start_debug_game_ready`
   itself crashed in `ReadingPolicyDatabase.GenerateStartingPolicies` on
   the null classes. **After:** 0 config/XML errors on load.
2. 🔴 **Nothing ticked.** `BuildingBase` never sets `tickerType`, so it
   defaults to `TickerType.Never` — `CompPitCoverTrigger.CompTick` and
   `Building_OpenPit.Tick` never ran, which is the entire mass trigger and
   the whole struggle clock. Measured: an *immobilised* 62.75 kg pawn sat on
   an armed 40 kg cover for 200 ticks and the trap did not spring. **After
   `<tickerType>Normal</tickerType>`:** same setup springs within 60 ticks
   with no debug help.
3. 🔴 **Shallow pits never opened.** `RequiredStages == 1` means nothing ever
   calls `CompleteToOpenPit`, so a Shallow dig site sat as a dig site
   forever — stranding all six Shallow fittings, i.e. the entire fitting
   family. Completed on first tick now (not in `PostSpawnSetup`, which would
   Destroy the parent inside its own spawn). Deep/Chasm correctly still wait
   for dig work.
4. 🔴 **The terrain-mimic never appeared.** `DirtyMapMesh` dirtied
   `MapMeshFlagDefOf.Buildings`; a Thing's own `Print()` output lives in the
   section dirtied by `Things` (`Verse/Thing.cs`), so the pre-arm print stayed
   on screen. **Before:** five pits, three armed, all five drawing the same
   sprite. **After:** only the two uncovered controls are visible; the three
   armed ones vanish into the soil with no seam at `rootSize 7` — closer than
   the closest normal play zoom. That is criterion 3, met by looking.
5. **Water drowned instantly.** `AdjustSeverity(…, 1f)` against
   `lethalSeverity 1.0` killed the occupant on the first interval and left a
   corpse in the pit; the hediff's own second stage (`minSeverity 0.6`) was
   unreachable. Now `drowningSeverityPerInterval = 0.15` — measured
   0.15→0.30→0.45→0.60→0.75→0.90→dead, a ~7-hour clock.

### What the matrix proved (21/21, then 7/7 on the fixes)

Measured `StatDefOf.Mass`, exactly as the trigger reads it — squirrel/rat
**12**, human **50.8–64.5**, Scyther **60**, Lancer **68**, Boomalope **120**,
Muffalo **144**, Centipede **202**, elephant/megasloth/thrumbo **240**.

- Woven scrap 40 kg: squirrel does not spring it, human does.
- Plank lattice 120 kg: one human (62.8) does not; a thrumbo (240) does.
- **Load sums** — three humans at 62.75 + 50.80 + 64.50 = **178.05** spring a
  120 kg cover that none of them springs alone. Three thrumbos = 720 spring a
  400 kg frame. This is spec §4's "a tight raider knot can overload a plank
  cover together", proved.
- An unarmed pit reads `threshold = float.MaxValue` and never springs under
  188 kg of standing pawns.
- Dig lifecycle: Deep 1/2 → open pit at `depthTier=Deep`; Chasm 1/3 → 2/3 →
  open pit at `depthTier=Chasm`; blueprint places through the ordinary
  Architect path.
- Escape curve falls monotonically with depth on the same three pawns —
  Shallow `[0.702, 0.661, 0.687]`, Deep `[0.518, 0.478, 0.503]`, Chasm
  `[0.427, 0.423, 0.412]` — and a struggle roll really ejects (a healthy
  thrumbo left a shallow pit on its first roll, matching the spec's "out in
  seconds and ANGRY"). A wounded pawn scores lower at the same depth (spiked
  capture, healthPct 0.697 → 0.609 against ~0.70 unwounded).
- Fittings: comps resolve one-each with no duplication, Spiked takes the
  captive from ~0.93 to 0.697 health, Poison accrues ToxicBuildup 0.020 →
  0.040 per interval, Water blocks the escape roll across four intervals
  while the drowning clock runs.
- Pit Cell: `Building_PitCell` resolves, carries **no** trigger comp (correct
  — manually gated), and reads `maxOccupants` 1 for 1x2 and 2 for 2x2 off its
  footprint, which is spec §6's whole capacity rule.

### Tuning findings (numbers, not verdicts)

- 🔑 **The 400 kg reinforced-frame tier was unreachable by any single vanilla
  creature.** The heaviest thing in Core is 240 kg (elephant, megasloth,
  thrumbo). Spec §3 wants that tier to mean "only monsters and vehicles
  fall"; as built it meant "only crowds fall". **Owner ruled 2026-08-30:
  drop to 220 kg** (within reach of the 240 kg single-creature ceiling,
  still excludes humans/heavies) — changed in `PitCoverTier.cs`,
  `PitDebugActions.cs`, and `covered_pit_traps_spec.md` §3. Same ruling also
  flagged the 240 kg ceiling itself as suspiciously low for a "big game"
  category — filed `BEAST_MASS_REALISM_AUDIT_1` to check our authored
  creatures' bodySize/mass values against realism.
- `PitDepthTier.MaxBodySize` is dead code — nothing reads it, so the spec's
  "Shallow holds bodysize <= 1" is not enforced anywhere.

## Open questions — flagged, not guessed
- **Oubliette does not switch a mechanoid off.** The EMP lands as damage
  (`Crack:13.67` on a captured Centipede) but the pawn reads
  `stunned=False` — the stun is what "mechanoids and droids that fall in
  switch off" means, and a de-spawned pawn inside a `ThingOwner` does not
  appear to receive it. The capture works; the signature effect does not.
- **`def.passability` cannot be toggled per-instance** (it's a per-`ThingDef`
  field, `Verse/BuildableDef.cs`). All pit defs are `Standable`, so there is
  no accidental-fall-while-uncovered hazard in this build — only a SPRUNG
  covered trap captures anyone. A "walk into an obvious hole" mechanic would
  need a second swapped ThingDef or a Tick-based check; not built.
- **Multi-occupant DRAWING is unsolved.** `IThingHolderWithDrawnPawn` (the
  only verified precedent) draws exactly one pawn. A 2x2 Pit Cell holding two
  per spec §6 draws only the first; the second is held/saved/escapes but
  invisible until the first vacates. No vanilla multi-pawn-holder precedent
  was found to build against.
- **Prisoner intake and feeding are player-gizmo stand-ins, not real jobs** —
  `RM_PlaceInPitCell` teleports the assigned prisoner in; `RM_FeedCaptive`
  refills food instantly. Both are exactly the points
  `Spikes/Spike2_PitCellHolding.cs`'s own README already flagged "unproven
  until runtime" (a real carry-to-holder JobDriver and a feed-through-the-gate
  job). Inherited, not newly guessed.
- **"Spoil hauled out" (§2) and cover-material cost (§3) are not modeled.**
  The spec names neither a spoil resource defName nor an arm-cover recipe;
  inventing either would be exactly the kind of defName guess CLAUDE.md
  forbids. Dig-deeper work costs time only; arming a cover is a free/instant
  gizmo. Flagged for the campaign/balance layer.
- **Terrain-driven dig speed and weather ambience (spec §7 — sand digs fast
  and silts, rock never silts, sandstorms re-arm covers)** are out of scope
  for this pass; not one of the six mechanics the item title names.
- **CanSwim (Water fitting) is a defName-string heuristic**
  (`RaceProps.body.defName` contains "aquatic"), because no vanilla aquatic
  RaceProperties flag exists in source. Silently does nothing for any race
  that doesn't opt in.
- **"Ground only, never on ship substructure" (spec §2)** has no enforcement
  mechanism here — no verified field/PlaceWorker for "not on hull floor" was
  found; not guessed, not built.

## verify
- [x] Build clean: `RimMandrakePits.dll`, 0 errors / 0 warnings
  (`"%USERPROFILE%\.dotnet\dotnet.exe" build
  D:\Luke\dev\Rimworld\src\RimMandrake\RimMandrake_Pits\Source\RimMandrake_Pits.csproj -c Release`).
- [x] All Defs XML well-formed; every `openPitDef`/`Class`/`thingClass`/
  `driverClass`/`giverClass` string cross-checked by hand against the
  compiled types and the defNames actually declared (no live-dump check
  available for a brand-new, undeployed-to-ModsConfig mod).
- [x] `deploy_custom_mods.py --mod RimMandrake_Pits --apply` — files deployed
  to the game Mods folder; mod NOT added to `ModsConfig.xml` (not enabled),
  per this item's own scope line — activation is a separate step.
- [x] **Spawn-mass quicktest matrix** on the 4-mod `pits` tier
  (`modset_builder.py --tier pits`) — ran 2026-08-30, see the section above.
  21/21 on the matrix and 7/7 on the defect fixes, all read back as raw
  fields. Cover tiers gate by measured mass, mass sums across grouped pawns,
  fall/spike/poison/water effects fire, the escape curve behaves, and the
  terrain-mimic camouflage was proved by an A/B screenshot pair.
- [x] Mod loads clean on a real mod list: `mandrake.rimmandrakepits` active,
  **0 config errors, 0 XML errors** in `Player.log`. Five load-blocking or
  mechanic-killing defects were found and fixed to get there.
- [ ] Pit Cell prisoner assignment/gate/feed gizmos exercised live. The class,
  the missing trigger comp and the footprint capacity are proved; the gizmo
  bodies (`RM_PlaceInPitCell`, `RM_FeedCaptive`, gate open/close, the
  `RM_PitExposure` clock) are not — they are gizmo-only and have no
  bridge-reachable hook yet, unlike arming, which now does.
- [ ] Oiled fitting's Ignite gizmo — same reason: gizmo-only, unexercised.

## criteria
- [x] Quicktest matrix confirms the cover-tier ratings sort creatures the way
  §3 describes — 40 kg takes humans and up but not squirrels, 120 kg takes
  big game but not one human, and sums stack. ⚠️ **400 kg does NOT sort as
  §3 describes** and needs an owner call (see Tuning findings): no single
  vanilla creature reaches it.
- [x] Escape-chance curve reads as intended — thrumbo out of a shallow pit on
  its first roll at 0.950, humans 0.70 → 0.50 → 0.42 across Shallow/Deep/Chasm,
  and a wound lowers it at fixed depth.
- [x] Terrain-mimic seam is acceptably subtle — invisible, actually, at
  `rootSize 7`. A/B: `pits_A_all_open.png` vs `pits_B_alternating_armed.png`
  in `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots`.
- [x] No Player.log errors on load with the mod in ModsConfig.

## Watch out
🔶 **Still `doing`, but for a much smaller reason than before.** The matrix has
run and the core framework is proved end to end. What is left is (a) the
owner's call on the 400 kg tier, and (b) the gizmo-only surfaces — Pit Cell
intake/gate/feed and the Oiled ignite — which no bridge hook reaches. Neither
is a core-mechanics question.

🔑 **The mod is deployed but NOT in the owner's 585-mod list.** It was proved
on its own 4-mod tier; adding it to his live list is a content decision, left
to him. `python3 src/RimMandrake/Utils/modset_builder.py --tier pits --apply`
rebuilds the test list at any time (game must be closed).

🔑 **`Source/Debug/PitDebugActions.cs` ships with the mod on purpose.** Arming
a cover, setting depth and rolling a struggle are gizmo actions, and a gizmo
is unreachable from anything but a human clicking it — without those eleven
ToolMap leaves none of this could have been proved from outside, and none of
it could be re-proved after a change.

🔑 **Fitting × depth-tier is deliberately NOT a full cross product.** Only
Shallow gets all six fittings; Deep and Chasm ship Bare-only in this pass, to
prove the staged-digging path without generating 18 near-duplicate defs for
no mechanical gain. Extending the matrix is cheap (one more `ThingDef` per
combination) once the base mechanic is quicktest-proven.

🔑 **`RM_PlaceInPitCell`/`RM_FeedCaptive` are stand-ins, not the real
mechanic.** Do not report prisoner intake or feeding as "done" — they are
placeholders that make the holder testable, explicitly flagged above.

## 2026-08-31 (FOUNDRY) — the gizmo-only gap closed, still owed a live proof

Added five debug actions closing exactly the gap the "Watch out" section
above named (`Source/Debug/PitDebugActions.cs`, category `RMPits`):
`PitCell: assign nearest prisoner`, `PitCell: place assigned in cell`,
`PitCell: toggle gate`, `PitCell: feed held captive`, and
`Oiled: ignite (bypasses soaked/Sprung gate)`. Two methods on
`Building_PitCell` (`PlaceAssignedInCell`, `FeedHeldPawn`) went from
`private` to `internal` so the debug-action class can reach them —
`covered`/`soaked` were already `public`. Builds clean (0 errors, 0
warnings), deployed.

**Still not live-proven.** `mandrake.rm.pits` is deliberately not in the
owner's active `ModsConfig.xml` (his own content-tier decision, unchanged
by this pass) and the `pits` test tier needs the game closed to swap to —
both paths need a restart this session doesn't have. The next window that
loads either the pits tier or the main list with this mod active should
run these five actions once each and confirm: prisoner assigned, teleported
into the cell, gate toggles (and `RM_PitExposure` moves the right
direction per §-cited rate), food need refills, and an Oiled+Sprung pit
actually ignites. Nothing here changes the core criteria, already all
met.
