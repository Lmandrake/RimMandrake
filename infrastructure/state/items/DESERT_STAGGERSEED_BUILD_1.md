# DESERT_STAGGERSEED_BUILD_1 — author the staggerseed cycle plant

## state (2026-09-20) — BUILT, waiting on the name card

**Both mechanisms and both ThingDefs are landed and building clean. This item
stays OPEN**, per its own `## verify`: the plant may not ship under the working
name, and the owner card `STAGGERSEED_SHIPPING_NAME_1` is still `proposed`.
What is left on this item is the rename, and nothing else.

Landed:

- `src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_Staggerseed.xml` — the
  bush. `fertilityMin` 0.45 confines it to the "protected water pockets", the
  tightest of the three desert plants' niches (ultracactus 0.05, surra grass
  0.30). Its **own** `ingestible.outcomeDoers` carries the brood as well as the
  harvested fruit's, because `Verse/Thing.cs Ingested` runs the outcome doers of
  whatever is eaten and a grazing animal eats the PLANT, never the item — on the
  fruit alone the whole dispersal cycle would never once fire in a wild biome.
- `.../Defs/ThingDefs_Items/RUT_Staggerseed_Items.xml` — `RUT_StaggerseedFruit`
  (raw, lethal) and `RUT_StaggerseedSeedDish` (prepared, euphoric).
- `.../Defs/HediffDefs/RUT_Staggerseed_Hediffs.xml` — `RUT_StaggerseedBrood`
  (untendable, `lethalSeverity` 1, ~7 h from the dose) and
  `RUT_StaggerseedEuphoria`.
- `.../Defs/ThoughtDefs/` and `.../Defs/RecipeDefs/` — the situational mood
  thought and the Cooking-8 preparation.
- `src/RimMandrake/CreatureBehaviors/Source/RM_HediffComp_ShadeStagger.cs` (+ its
  properties class) — both halves of the dispersal. Past severity 0.6 it forces a
  Goto toward the nearest strictly-better-shaded reachable cell that
  `RM_MapComponent_ShadeGrid` knows of, and on `Notify_PawnDied` it germinates the
  plant at the corpse, at a chance running 0.15 in full sun to 1.0 in full shade —
  the "it aims at shade" ruling expressed as the asymmetry itself, not as flavour
  text over a flat chance. Mod Settings entry 24 in `RM_CreatureBehaviorsMod.cs`.
- `RUT_Desert.xml` wildPlants at 0.1; `AshkarrFlora/About/About.xml` gains
  `loadAfter mandrake.rm.creaturebehaviors`.

Checked and clean: assembly builds 0 warnings / 0 errors; every new XML parses;
`run_selftests.py` 67/67.

⚠️ **Art is queued, not landed** — jobs `rutstaggerseed_v1` and
`rutstaggerseeddish_v1` in `infrastructure/artpipe/pending/`, filed after
searching `done/`, `_artsrc/`, `registry.jsonl` and `art_status.json` for
"staggerseed"/"cycle plant" and finding nothing. Until the daemon reaches them
`validate_patch.py` reports the three texPaths as missing; that is expected, and
is the same state `RSW_Ultracactus` shipped in.

⚠️ **Not deployed.** Nothing has been copied to the game's `Mods` folder and no
live check has been run — the whole pass is offline.

## what is wrong

desert.md §4b/§7 names the desert's third signature plant — the cycle plant,
working name **staggerseed** (owner's name still owed, unlike the ultracactus,
which the owner already named) — and it has no def, no C#, and no card asking
the owner for a shipping name. `DESERT_SIGNATURE_FLORA_1` authored the
ultracactus and filed this item and `DESERT_SHADE_PLANTS_DESIGN_1` as its
correctly-scoped successors rather than building all three at once.

## why it matters

Per §4b/§7 the staggerseed is not scenery — it is "an active participant in
the patch economy," the desert's only seed-disperser, and its prepared dish is
named a target for the Star Wars cuisine track (§4b: "a controlled near-miss
with a lethal parasite... producing euphoria").

## the work — two mechanisms, both needing C#

- **Corpse-dispersal.** The fruit, eaten raw, "hatches its seeds inside your
  belly," kills the eater, and the dying animal "staggers toward the next
  shade — and dies in it," where the seeds then germinate. This is a
  post-death dispersal mechanic (a lethal ingestion hediff that also biases
  the dying pawn/animal's movement toward the nearest shade before death, then
  spawns the plant near the corpse) — no vanilla CompProperties covers
  "dying creature seeks shade then seeds germinate at its corpse."
- **Euphoric prepared-seed dish.** "Prepared correctly, the preparation lets
  them begin to grow and then perish before they can hurt you — producing
  euphoria." A cooked/prepared meal item with its own ingestible outcome
  (Hediff, euphoria-flavoured) distinct from the raw fruit's lethal one — the
  same plant's two harvested products (raw = deadly, prepared = a delicacy)
  need two different ingestible outcomes on two different ThingDefs.

## gated on a name card

Unlike the ultracactus (owner's name already stands), desert.md marks this
plant's name as "owner's pick. Working: staggerseed." — §7 and §4b both use
the working name only. **File the card before building**: a short,
Star-Wars-flavoured name ask for this one plant, kept separate from the
`EXTREME_DESERT_UNRULED_VERMIN_1` / `SURRA_GRASS_FERTILITYMIN_1` cards per
`DESERT_SIGNATURE_FLORA_1`'s own "Watch out" note — this is a smaller, single-item
ask and should not be bundled with theirs.

## verify

A staggerseed ThingDef (raw fruit, lethal-ingestion + shade-seeking + corpse-seed
mechanic) and a prepared-dish ThingDef (euphoric hediff) both exist, wired into
`RUT_Desert`, under whatever shipping name the owner's card returns — or, if
the name card is still outstanding, this item stays open rather than shipping
under the working name.

## criteria

The staggerseed ships as two ThingDefs plus the C# behind both mechanisms,
under an owner-given name.
