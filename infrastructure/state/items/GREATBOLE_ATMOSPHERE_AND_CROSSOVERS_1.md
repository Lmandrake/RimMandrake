# GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1 — the greatbole's song, thermal sanctuary, pilgrims, and the two opt-in crossovers

**Spec: `design/Jawa/worldbuilding/biomes/kits/greatbole_harvest_spec.md`** §5, §7, §8, §8a, §8b.
Filed on close of `GREATBOLE_HARVEST_LADDER_1`, which shipped the threshold ladder, the three
events, the fruit's three products and the grubs — see that item's closed prose
(`infrastructure/state/items/closed/GREATBOLE_HARVEST_LADDER_1.md`) for exactly what is already
built and reusable.

## What this item owes

1. **The song (§5)** — the greatbole's own hum as a diegetic progress bar. `RM_MapComponent_
   ProximitySoundscape` + `RM_ProximitySoundscapeExtension` (`mandrake.rm.creaturebehaviors`,
   built 2026-09-23) already do the layered-SoundDef/hysteresis half; owed is generalising their
   driver to accept an external 0–1 scalar (this item's own `RM_MapComponent_LivingRegrowth.
   GetRemovedFraction` is exactly that scalar) instead of only a nearby-Thing count, plus the
   greatbole's own authored hum layers. ⚠️ UNMEASURED: whether a true beat frequency is
   achievable from two live sustainers, or must be baked into one authored file (spec's own
   caveat).
2. **Thermal sanctuary (§7)** — chambers hold deep-ground temperature. ⚠️ UNMEASURED: whether
   that value is readable and whether a room's temperature can be pinned to it rather than merely
   insulated toward it (spec §10.9). Needs Desktop/RimSage engine reading before authoring.
3. **The pilgrims (§8a)** — a visiting group whose disposition is read off the tree's own body
   (sealed rooms don't count against the player, open regrowing cuts are wounds, witnessing a
   Great Shaking triggers an attack). `RM_` tier with a campaign skin (generic pilgrims outside
   Utinni). ⚠️ UNMEASURED: how a visiting group's disposition is set from a map-state reading at
   arrival, and how "witnessing an event" is detected while present (spec §10.10) — do not name a
   mechanism for either from reasoning.
4. **Two opt-in crossovers (§8b)**, Mod Settings toggles, DEFAULT OFF, Utinni ships both off:
   anima focus (fixed-strength first; harmony-tracking needs a runtime-variable focus strength,
   UNMEASURED) and arboreal servants (objection raised and dissolved in the spec's own §8b-ii —
   it holds only when the *design* chooses for the player, not when the player opts in).
5. **The seed's planting/growth mechanic (§3c)** — BUILT OFFLINE 2026-10-06 (see "Built" below); live proof owed.
6. **Gorbeleth toxin as the sealant's reagent (spec §11)** — `RM_Gorbeleth` now exists (tree roster,
   `src/RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_TreeRoster.xml`), so this is no longer
   blocked on the roster; the reagent wiring itself is not built.
7. **Royal Rind's Contagion/Miasma stat wiring** — `RM_Apparel_RindCoat` ships today with the
   vanilla-stat portion (`ArmorRating_Heat`, `Insulation_Heat`, `Insulation_Cold`, ruled numbers).
   The Scald portion is done: Scald protection is `ArmorRating_Heat` (`SCALD_FOLD_INTO_HEAT_1`).
   The Contagion/Miasma custom-stat portion is blocked on those biomes' own StatDef work — do not
   invent that StatDef family here.

## Watch out

- 🔴 Everything in `GREATBOLE_HARVEST_LADDER_1` that this item's work touches: `RUT_GreatboleCore`
  now carries TWO comps (`CompProperties_LivingBoleMarker` and `RUT_CompProperties_
  GreatboleHarvestLadder`) plus `RUT_Jawa_WildsteamClan` goodwill wiring on the catastrophe. Read
  `src/RimUtinni/UtinniPatches/Source/RUT_CompGreatboleHarvestLadder.cs`'s own header before
  extending it further.
- The three thresholds are Mod Settings sliders (`UtinniPatchesSettings.greatboleShakingThreshold`
  /`greatboleHealingThreshold`/`greatboleCatastropheThreshold`) — the healing one only moves this
  item's own ANNOUNCEMENT timing; the actual accelerated-regrow threshold baked into
  `RUT_GreatboleCore.xml`'s `CompProperties_LivingBoleMarker.acceleratedRegrowThreshold` is fixed
  at load (0.6) and does not move live with the slider. Fixing that (reading the setting live
  from `RM_MapComponent_LivingRegrowth` instead of a value frozen at `RegisterBole` time) is a
  small owed polish, not attempted here for time.
- ⛔ Do not build any of §5/§7/§8a's UNMEASURED mechanisms from reasoning — each needs a
  Desktop/RimSage read first, same posture the harvest spec itself already insists on for its
  own §10.

## Engine check — does the Gauranlen system accept a non-plant host? (FOUNDRY, 2026-10-04, RimSage, decompiled 1.6)

**Yes, structurally — with two hard-coded gates that need a small C# workaround.** MEASURED-SRC:

- `CompTreeConnection : ThingComp` — no `Plant` cast anywhere in it. It works in `CompTick()` (Normal ticker;
  `Plant_TreeGauranlen` sets `tickerType Normal`), so a Building host **must set `tickerType Normal`**
  (`BuildingBase` does not; `RUT_GreatboleCore` sets none today).
- `ThingRequestGroup.DryadSpawner` = "def has `CompProperties_TreeConnection`" (`ThingListGroupHelper.cs:170`),
  def-category agnostic — so pruning (`WorkGiver_PruneGauranlenTree.PotentialWorkThingsGlobal`), mode change,
  both Gauranlen alerts and the building-overlay all find a Building host unchanged.
- `PostSpawnSetup` destroys the host unless Ideology is active — moot (all DLC assumed).
- **Building penalty off is XML-only:** the loss is `connectionLossDailyPerBuildingDistanceCurve` over
  `listerArtificialBuildingsForMeditation` within `radiusToBuildingForConnectionStrengthLoss`; give our
  `CompProperties_TreeConnection` a flat-zero curve (or radius 0). The host itself never counts: a natural
  thing has `faction == null` and `CountsAsArtificialBuilding` requires a faction.
- 🔴 **Gate 1 — the connection ritual never offers our host.** `RitualObligationTargetWorker_UnconnectedGauranlenTree.GetTargets`
  is `listerThings.ThingsOfDef(ThingDefOf.Plant_TreeGauranlen)`. Fix: a filter subclass (or postfix) that
  enumerates `ThingRequestGroup.DryadSpawner` instead. `RitualOutcomeEffectWorker_ConnectToTree` itself is
  host-agnostic (`TryGetComp<CompTreeConnection>`).
- 🔴 **Gate 2 — `RitualPosition_BesideTree.ThingDef => ThingDefOf.Plant_TreeGauranlen`**: ritual positions key
  on the vanilla def. Same fix shape (subclass or postfix).
- Cosmetic only: `GauranlenUtility.CocoonAndPodCellValidator` excludes Gauranlen-def cells (our host is
  Impassable anyway); `Pawn_ConnectionsTracker` gizmo icon is the Gauranlen icon.

⇒ The owner's ruled option (vanilla Gauranlen, building penalty OFF) is **buildable**: XML comp + ticker on the
host, plus ~2 small C# classes for the two ritual gates. No need to go back to him.
NEXT: build it in the free Greentide mod (where the 2026-10-03 ruling moves heartwood/core) when its DLL is not
frozen for a live run; default OFF Mod Settings toggle per §8b.

## Built offline 2026-10-06 (FOUNDRY) — game down, nothing deployed, nothing live-proven

All in `src/RimMandrake/Greentide`; DLL rebuilt clean (`winbuild.py Greentide`, 0 warnings).

- **Seed planting (§3c).** `RM_GreatboleSeed` gets vanilla `CompProperties_Plantable` → `RM_Greatbole`
  (gated patch `Patches/RM_Greatbole_Crossovers.xml`, setting "Greatbole seeds can be planted", default ON).
  `RM_Greatbole` now uses `RM_Plant_Greatbole` (`Source/RM_Plant_Greatbole.cs`): for **sown** trees only,
  `GrowthRate` is 0 without open water within 1.5 cells and ×20 with it (INVENTED, 220 → 11 days), with an
  inspect line saying which. Wild greatboles are unchanged. Dry cells are not refused at targeting time
  (`CompPlantable.CanPlantAt` is not virtual); the sapling just doesn't grow and says why.
- **Servant crossover (§8b-ii).** Same patch file, setting "Opt-in: greatbole servants", DEFAULT OFF:
  `CompProperties_TreeConnection` on `RM_GreatboleCore` (vanilla numbers, building radius 0 + flat-zero
  curve), `ritualFocus`, and the two ritual gates swapped for `RM_RitualObligationTargetWorker_UnconnectedDryadSpawner`
  / `RM_RitualPosition_BesideDryadSpawner` (`Source/RM_GreatboleServants.cs`), which read
  `ThingRequestGroup.DryadSpawner` and so keep vanilla Gauranlen trees working.
- **Pre-existing defect fixed:** `RM_GreatboleCore` had no `tickerType`, so it defaulted to Never and
  `RM_CompGreatboleHarvestLadder.CompTick` never ran — the whole harvest ladder could not fire. Now `Normal`.
- **Not built:** the song (needs AtmosphericBase / the soundscape scalar driver, unbuilt), thermal pull,
  pilgrims, anima crossover, Wildsteam goodwill-for-planting (campaign tier), Royal Rind stats.

NEXT: live-verify on a quicktest: plant a seed beside water and on dry ground and read growth/inspect;
with servants ON, start the connection ritual on a core whose west cell is mined open and check dryads spawn
and connection strength takes no building loss.
