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

## Open questions — flagged, not guessed
- **Spawn-mass quicktest matrix has not run.** This is the item's own stated
  first step and needs the bridge (occupied this pass). All mass thresholds
  (cover tiers), escape-chance curve, fall/spike/poison/EMP damage numbers,
  and struggle interval are spec-derived placeholders, not tuned values.
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
- [ ] **Spawn-mass quicktest matrix** (squirrel/human/thrumbo/centipede ×
  woven-scrap/plank-lattice/reinforced-frame cover tiers) on the 22s minimal
  list — THE NEXT STEP, needs the bridge free. Proves: cover tiers actually
  gate the right creature sizes, mass-sum "load stacks" for grouped pawns,
  fall damage/fitting effects fire correctly, struggle-escape odds feel like
  the spec's target ("a healthy thrumbo in a shallow pit is out in seconds
  and ANGRY; a wounded raider in a deep pit is yours"), and the terrain-mimic
  cover actually reads as camouflaged at play zoom (LOOK at it, per
  `worldview.py`/screenshot convention — this is explicitly an eyeball check,
  not a number).
- [ ] Mod enabled in `ModsConfig.xml` and a load-round smoke test (does it
  load at all on the minimal list, any red Player.log lines) — not attempted
  this pass; deploying files only was the explicit instruction.
- [ ] Pit Cell prisoner assignment/gate/feed gizmos exercised live (the
  stand-in jobs above need eyes-on before anyone calls them "working").

## criteria
- [ ] Quicktest matrix confirms the three cover-tier mass ratings sort
  creatures the way §3's table describes, or gets retuned until they do.
- [ ] Escape-chance curve reads as intended in play (thrumbo-shallow escapes
  fast, raider-deep does not) — not just internally consistent math.
- [ ] Terrain-mimic seam is acceptably subtle at normal play zoom (the whole
  point of the mechanic).
- [ ] No Player.log errors on load once the mod is added to ModsConfig.

## Watch out
🔶 **Do not close this item.** The quicktest matrix is this item's own stated
first step and has not run — that is offline-unreachable (bridge occupied,
and a quicktest is inherently a live-testing step). Leave `doing`.

🔑 **Fitting × depth-tier is deliberately NOT a full cross product.** Only
Shallow gets all six fittings; Deep and Chasm ship Bare-only in this pass, to
prove the staged-digging path without generating 18 near-duplicate defs for
no mechanical gain. Extending the matrix is cheap (one more `ThingDef` per
combination) once the base mechanic is quicktest-proven.

🔑 **`RM_PlaceInPitCell`/`RM_FeedCaptive` are stand-ins, not the real
mechanic.** Do not report prisoner intake or feeding as "done" — they are
placeholders that make the holder testable, explicitly flagged above.
