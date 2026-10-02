# GREENTIDE_THURROCK_HERD_BUILD_1 — the thurrock: the tree-felling herd, the Greentide's living giant

Caused by `GREENTIDE_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.greentide`. Design:
`design/Jawa/worldbuilding/biomes/greentide_bedazzle_review_2026-10-02.md` §3 (the thurrock), §4 row 1,
§8. Rulings (decisions taken by question card 2026-10-02 07:43 PDT): **build first: base fixes plus the
giant**; **the giant is the tree-felling herd**: *huge copper-teal browsers that knock trees down to eat
the crowns, cross, and fight in season; a passing herd is crash after crash, opening sun gaps and dropping
wood across the roads; provoke one and it shoulders walls like trees.* ⛔ **No moult.** The varkhoss moult
(§5 idea 2) and "only the moulting giant" were not chosen: one body state, no moult behaviour, no shed
plates.

Mark 5 (GIANT beast), and the sheet's missing sort: the **Shatterers**, the jungle's third tree-feller
(`design/Jawa/worldbuilding/biomes/the_greentide.md` §4). Name **thurrock** (invented, Greentide accent):
collision-checked 2026-10-02 by a python sweep of `src/`, `design/` and `infrastructure/` (defName, label
and description text): 1 hit, the review itself; Wookieepedia search 0 results (probe `wyyyschokk` 50);
artpipe `find thurrock` 0 hits (probe `korrum` 12).

## spec

1. **The creature, `RM_Thurrock`** (race ThingDef + PawnKindDef, free tier): a towering slab-shouldered
   browser, body size about 8, drawn huge on an ordinary footprint (no new rig; `drawSize` carries the
   scale), hide a wet copper-teal sheened with mineral bloom, a short trunk-like upper lip for stripping
   canopy. Herd animal (`wildGroupSize` about 3 to 6), wild, never a mount, not tameable (`trainability`
   none / `wildness` 1, first values). Diet: browses tree crowns (`foodType` Tree/Plant; it eats felled
   trees' leaves, not grass first). Description in the biome's voice: the reason the canopy has holes.
2. **It fells trees as a way of life: reuse the built Shatterer aura.** A `HediffDef` `RM_ThurrockShatter`
   carrying `HediffCompProperties_PeriodicAreaAttack` (`src/RimMandrake/EnvironmentalHazards/Source/`)
   with `fellsTreesBelowHealthFraction` set, `plantMultiplier` high, `pawnMultiplier` and
   `buildingMultiplier` 0 at rest, `requiresAwake` true, `sparesCarrier` true, a small radius. The fall goes
   through `RM_TreeFallUtility` / `RM_FellableTreeExtension` (the same path the krannock's gnaw and the crack
   fall use): a felled tree lands as a fallen trunk and drops its wood. The thurrock then browses the felled
   crown.
3. **The one new piece: "always has this hediff from spawn".** No such wiring exists (the krannock pass
   checked: `hediffGiverSets` is a probabilistic roll, no innate-hediff comp exists;
   `src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_Krannock.xml` l.45-60). Add a small generic
   `RM_CompProperties_InnateHediff` / `RM_CompInnateHediff` in `mandrake.rm.creaturebehaviors`: on
   `PostSpawnSetup` (and on load), if the pawn lacks the listed hediff, add it. Generic, names no biome.
   S size. 🔴 If it lands in `RM_CreatureBehaviors.csproj`, add the `<Compile Include>` line
   (`EnableDefaultCompileItems` is false; a missing line compiles to nothing, with no error).
4. **A passing herd is a weather event.** While a herd moves along a treeline the aura fires again and
   again: crash after crash, fallen trunks open sun gaps (the canopy is gone where they fell) and drop wood
   across root causeways (`GREENTIDE_BASE_PORT_BUILD_1`). No new mechanism: this is the aura on a herd.
   Tune the aura interval so a herd fells a handful of trees per in-game hour, not a forest (Mod Settings).
5. **In season they fight.** Rut brawls between males: use the vanilla `fightsInRut`-style behaviour if the
   race fields allow it (🔴 UNMEASURED: read the 1.6 race/rut fields in RimSage before naming one); during
   a brawl the aura's `plantMultiplier` already fells what they crash into. If vanilla has no rut fight,
   drop this clause rather than writing new AI, and say so on the item.
6. **Provoked, it shoulders walls like trees.** When the thurrock is in a hostile mental state (manhunter,
   revenge) the aura's `buildingMultiplier` applies: a second stage of `RM_ThurrockShatter`, entered while
   the pawn is in a hostile mental state (a stage keyed by a tiny comp or the existing severity path), with
   `buildingMultiplier` > 0, so it batters walls and doors as it does trees. Natural rock is spared
   (`sparedNaturalRock` true). At rest it never damages buildings.
7. **Silence.** A thurrock is not a hunter, so it does not carry `RM_SilenceAuraExtension`; the jungle's
   crashes stop when a herd stops, which is its own sign.
8. **Roster row:** `RM_Thurrock` in `RM_Greentide`'s `<wildAnimals>` at about 0.08 (first value; one herd
   on many maps, none on some), added by `GREENTIDE_FREE_ROSTER_OWNED_1`'s list.
9. **Mod Settings:** on/off for the felling aura (off = a big browser that fells nothing); trees felled
   per hour (aura interval); provoked wall damage on/off.
10. **Readable signs:** the crashes, the fallen trunks with stripped crowns, sun-gaps in the canopy, wood
   across causeways, the herd itself (huge, copper-teal), cracked walls after a provoked one.

Reuses: `HediffComp_PeriodicAreaAttack` + `fellsTreesBelowHealthFraction`, `RM_TreeFallUtility`,
`RM_FellableTreeExtension`. New code: `RM_CompInnateHediff` (S), and possibly the hostile-state stage key.

Depends on: nothing open to build. Criteria that read causeways need `GREENTIDE_BASE_PORT_BUILD_1`. Art:
`infrastructure/artpipe/art_lists/greentide_turn1_2026-10-02.csv` (`RM_Thurrock` row).

## criteria

Deterministic state reads through `jawa/get_defs` and debug `[Tool]`s, recorded in the Greentide functional
script:
- `ThingDef/RM_Thurrock`, `PawnKindDef/RM_Thurrock`, `HediffDef/RM_ThurrockShatter` resolve on the free
  tier alone; `RM_ThurrockShatter`'s `HediffCompProperties_PeriodicAreaAttack.fellsTreesBelowHealthFraction`
  > 0; `RM_Thurrock`'s race body size ≥ 6.
- A spawned `RM_Thurrock` holds `RM_ThurrockShatter` on the first tick after spawn; after a save/load round
  trip it still holds exactly one. A spawned vanilla Muffalo does not (the comp is per-def).
- On a test map with 10 grown trees within the aura radius of one awake `RM_Thurrock` and the aura enabled:
  after N ticks at least one tree is gone and a fallen trunk / wood stack exists at or beside its cell; with
  the aura toggle off, after the same N ticks all 10 trees remain.
- At rest beside a wall for N ticks: the wall's hit points are unchanged. Forced into manhunter beside the
  same wall: hit points fall. Natural rock beside it is unchanged in both cases.
- `RM_Greentide`'s `<wildAnimals>` (parsed as elements) contains `RM_Thurrock`.
- No hediff, stat or comp named "moult" or "shed" exists on any `RM_Thurrock` def (the moult is not built).
- Each Mod Settings toggle off removes exactly its effect.
