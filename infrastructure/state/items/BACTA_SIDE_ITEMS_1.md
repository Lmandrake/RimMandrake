# BACTA_SIDE_ITEMS_1 — bacta full-kit satellites: medical droid, field consumables, trader wiring

Filed by BENCH 2026-09-14, reassigned to FOUNDRY 2026-09-21 (owner, at the bench, verbatim:
*"Shipping implementation items to FOUNDRY is a good idea. Let's enable that as much as
possible."*). No spec/verify existed on the item before this pass — FOUNDRY wrote them here
per the CHARTER's own build-and-prove posture, citing `BACTA_TANK_CORE_1`'s "V1 scope (card
4): FULL KIT" line as the scope authority: *"tank + fluid here; 2-1B-style medical droid
facility + bacta patches/spray in BACTA_SIDE_ITEMS_1; art in BACTA_TANK_ART_1."*

Extends the already-built, already live-tested `mandrake.rsw.bacta` mod
(`src/RimStarWars/Bacta/`) — not a new mod. Reuses its ruled mechanism
(`CompBactaImmersion.cs`, BACTA_TANK_CORE_1 card 2) rather than reinventing healing.

## What "KR pattern" turned out to mean

No "KR" droid, mechanism or doc exists anywhere in this repo or in
`design/RimStarWars/canon_references/DROIDS_INDEX.md` (checked; zero hits). Read literally,
the phrase names the pattern `RSW_BactaTank.xml` had ALREADY wired for `VitalsMonitor` before
this item existed — `CompProperties_AffectedByFacilities` / vanilla `CompFacility` — with an
explicit comment: *"The facility hook BACTA_SIDE_ITEMS_1 needs: the 2-1B-style medical droid
will be added to this list."* Treated "KR pattern" as that vanilla linkable-facility pattern,
not a proper-noun droid line, and built the droid on it.

## Spec (written this pass)

1. **`RSW_MedicalDroid`** (`Defs/ThingDefs_Buildings/RSW_MedicalDroid.xml`) — a 1x1 powered
   facility building using vanilla `CompProperties_Facility` (verified against
   `RimWorld/CompFacility.cs`, `CompProperties_Facility.cs` in the decompiled source, and
   Core's own `VitalsMonitor` ThingDef as template). Added to `RSW_BactaTank`'s
   `linkableFacilities`. Research-gated on the existing `RSW_BactaImmersion` project (no new
   research tree — full-kit scope, not a new tech branch).

   Deliberately NOT wired through `CompProperties_Facility.statOffsets` + a `StatDef`
   (VitalsMonitor's own route, e.g. `MedicalTendQualityOffset`): the tank's healing never runs
   through vanilla `TendUtility`, so there is no natural StatDef consumer. Instead
   `CompBactaImmersion.DroidAssisting` reads the link directly off
   `CompAffectedByFacilities.LinkedFacilitiesListForReading` + `IsFacilityActive` (both public
   vanilla API, verified in the decompiled source) and multiplies the tank's wound/scar/
   immunity rates by `BactaSettings.medicalDroidHealMultiplier` (default 1.5x) while a
   powered, active droid is linked.

2. **`RSW_BactaPatch` / `RSW_BactaSpray`** (`Defs/ThingDefs_Items/RSW_BactaFieldItems.xml`) —
   field-usable consumables. Wired the vanilla way: `CompProperties_Usable` (the "Use"
   float-menu/gizmo, `JobDef UseItem`) plus `CompProperties_UseEffectPlaySound` and
   `CompProperties_UseEffectDestroySelf`, all reused unmodified — verified against Core's own
   `MechSerumHealer` ("healer mech serum",
   `Data/Core/Defs/ThingDefs_Items/Items_Exotic.xml`), the closest vanilla precedent for a
   self-use field heal item.

   The healing comp itself, `CompUseEffect_BactaHeal`, is ours and is NOT
   `CompUseEffect_FixWorstHealthCondition` (Core's own comp on `MechSerumHealer`) — read that
   comp's target, `Verse.HealthUtility.FixWorstHealthCondition`/`TryGetWorstHealthCondition`,
   in the decompiled source and confirmed it explicitly calls `FindBiggestMissingBodyPart` and
   `Cure(part, pawn)` (regrows the missing part) and can select a permanent brain injury as
   the worst condition — exactly the two things BACTA_TANK_CORE_1 card 2 rules bacta must
   never do. Reusing it unmodified would have broken the mod's own central law.

   Instead, `CompBactaImmersion.TryHealPawn`'s guarded pass (never regrow a missing part,
   never touch the brain/mind) was extracted verbatim into a new shared static class,
   `BactaHealingUtility.ApplyHealingDose`, and both the tank and `CompUseEffect_BactaHeal`
   now call it — one mechanism, two doses (continuous vs. one burst). The tank's own call site
   passes exactly the values it always did, so this refactor changes nothing about the tank's
   already live-tested behaviour (BACTA_TANK_CORE_1, live test v2, same day).

   Patch: small wound-only dose (6 severity, tend quality 0.65), no scar erasure, no infection
   assist. Spray: bigger dose (10 severity, tend quality 0.80) plus a small infection-assist
   nudge (`infectionAssistEnabled=true`, `immunityGainAmount=0.05`). Both gated on a new
   `BactaSettings.fieldItemsEnabled` toggle and scaled by `BactaSettings.fieldItemPotency`.
   Both are also wired onto `ThingDef Human` and the animal-base abstract's `<recipes>` list
   (`Patches/RSW_Bacta_RecipeWiring.xml`, mirroring exactly how Core wires
   `AdministerMechSerumHealer`) so a doctor can administer either to someone else via a bill,
   not just self-use.

   `thingCategories` is `Drugs`, not a Medicine category — same precedent `MechSerumHealer`
   sets, so an ordinary doctor's Tend job never auto-burns one on a random patient.

3. **Trader-tag wiring for all bacta goods** — `Patches/RSW_Bacta_TraderStock.xml` extended
   with explicit `StockGenerator_SingleDef` rows for `RSW_BactaPatch`, `RSW_BactaSpray` and
   `RSW_MedicalDroid` (the last via `<minifiedDef>MinifiedThing</minifiedDef>`, same as
   vanilla `VitalsMonitor`, at a much smaller countRange — a whole-unit purchase, not a stack
   good) on the same three trader kinds (`Orbital_Exotic`, `Caravan_Outlander_Exotic`,
   `Base_Outlander_Standard`) already carrying `RSW_Bacta`'s own rows.

4. **Mod Settings** (per the 2026-09-12 standing rule): `medicalDroidEnabled` +
   `medicalDroidHealMultiplier` (1.0x-3.0x slider, default 1.5x), `fieldItemsEnabled` +
   `fieldItemPotency` (0.25x-3.0x slider, default 1.0x). Defaults = shipped behaviour, both
   toggles independently all-off-degrades-gracefully (droid off = link exists, does nothing;
   field items off = item builds/trades but Use is disabled with a stated reason).

## verify

Offline (this pass, no bridge):
- All new/edited XML well-formed (`xml.etree.ElementTree`, 6 files).
- `validate_patch.py --defs` against the live 621-mod load set: both patch files
  `OK - 0 errors` (`RSW_Bacta_TraderStock.xml`: 3 warnings, same pre-existing
  not-wrapped-in-Conditional style note BACTA_TANK_CORE_1 already accepted;
  `RSW_Bacta_RecipeWiring.xml`: 2 warnings, same style note). Both new xpaths confirmed
  exactly 1 live match each in Core (`Races_Humanlike.xml`, `Races_Animal_Base.xml`).
  **Caught a real bug this way**: `[defName="AnimalBase"]` was wrong — the animal abstract
  has no `defName` at all, it is `Name="AnimalThingBase"` (an XML attribute, not a def
  child) — validator reported a genuine 0-match xpath before this ever reached the game;
  fixed to `[@Name="AnimalThingBase"]`, re-ran, confirmed 1 match.
  All 4 new/edited Defs files: `OK - 0 errors` (two informational notes on
  `CompProperties_UseEffect_BactaHeal` not being a known vanilla class — expected, it's our
  own compiled class, confirmed by the successful build below).
- `.csproj` wired: both new `.cs` files (`BactaHealingUtility.cs`,
  `CompUseEffect_BactaHeal.cs`) added to `<Compile Include>` — the `EnableDefaultCompileItems
  false` trap checked and avoided.
- **C# build succeeded** (`dotnet build ... -c Release`, 0 warnings, 0 errors) — the game
  was NOT holding the DLL locked at the time this pass ran, so this is a real, not merely
  attempted, build.
- Deploy: plan showed exactly the 10 expected files (6 new, 4 edited), nothing from another
  window. `--apply`: 9/10 written; `Assemblies/RimMandrake.StarWars.Bacta.dll` failed with
  `[Errno 22]` (OS file lock — the game was running by the time deploy ran, after the build
  above). This is the documented, expected outcome, not a defect; a re-run of
  `deploy_custom_mods.py --mod Bacta --apply` once the game is down will pick it up.

**Owed, for the bridge holder** (none of this attempted here — no bridge this pass):
- Deploy the DLL once the game is down, then a quicktest: droid linked+powered speeds a
  known wound's closure rate relative to an unlinked control (read `jawa/pawn_get` severity
  over a fixed tick window with and without the droid, same shape BACTA_TANK_CORE_1's own
  live test already used for the tank alone); a bacta patch closes one fresh wound instantly
  on use and is consumed; a bacta spray closes multiple fresh wounds plus nudges a treatable
  infection's immunity, and is consumed; both refuse to fire with a stated reason when
  nothing is healable, and when `fieldItemsEnabled` is off; a missing part/brain hediff is
  confirmed untouched by either item (**not** a full live test — a single-hediff probe per
  BACTA_TANK_CORE_1's own trap notes, `jawa/pawn_health` adding `WoundInfection` is
  immediately lethal, so test infection-assist very carefully or skip it and rely on the
  shared code path already being source-verified against the tank's own guard).
- Settings screen render check (all 4 new controls appear, same
  `topLevelSettingCount: 0`-for-statics caveat BACTA_TANK_CORE_1 already documented applies).
- Art acceptance (droid, patch, spray textures) is `BACTA_TANK_ART_1`, not this item —
  all three new textures are explicitly marked placeholder
  (`Textures/Things/Building/Bacta/PLACEHOLDER.md`,
  `Textures/Things/Item/Bacta/PLACEHOLDER.md`, both updated this pass).

## status (FOUNDRY, 2026-09-24 game-down window)

**DLL now deployed — 10/10 files in sync.** Game was confirmed genuinely down
(`./game` → `NOT RUNNING`) before touching anything. Rebuilt
`RimMandrake.StarWars.Bacta.dll` (`dotnet build -c Release`, 0 warnings/0 errors) and
`deploy_custom_mods.py --mod Bacta --apply` → `VERIFIED in sync`; md5 of the repo copy
and the deployed copy match byte-for-byte. A full `--mod Bacta` re-plan afterward reports
`in sync (22 files)` / `Everything in sync`.

Re-ran `validate_patch.py --live --defs` against the live 621-mod dump
(`DefDump/captures/2026-09-24T22-19-22Z`) and `ModsConfig.FULL.LATEST.xml`: both patches
`OK - 0 errors` (5 pre-existing advisory warnings, unchanged from the prior pass, not
regressions). `run_selftests.py`: **75/75 passed, 0 failed.**

Left `doing` — game stayed down the whole pass, so no bridge was taken and the live
quicktest in `## verify` (droid healing rate, patch/spray consumption, settings render)
is still owed. Whoever next holds a live game: take the bridge, run that quicktest, then
close or note accordingly.

## status (FOUNDRY, resumed 2026-09-25)

Offline state re-checked and unchanged: `deploy_custom_mods.py --mod Bacta` plan reports
`in sync (22 files)` / `Everything in sync` — nothing drifted since the prior pass.
`bridge who` reports it held by another live FOUNDRY window ("FireHawk flight live
verify", idle 9 min at check time — provably alive, not stale). Per this item's own
brief, not force-taking a live-held bridge. Blocked rather than closed
(`rimflow block BACTA_SIDE_ITEMS_1`); the owed live quicktest (droid heal-rate delta,
patch/spray consume-and-heal, settings render) is unchanged and still gates the close.
