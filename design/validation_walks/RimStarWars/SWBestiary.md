# SWBestiary — validation walk
subject: src/RimStarWars/SWBestiary  (packageId mandrake.rsw.swbestiary)
feature: absorbed-creature-roster
deps: none (Ludeon.RimWorld only) — content-only, no assemblies, no patches
list: minimal
status-hint: absorbed-content salvage bin — 10 creature ThingDef/PawnKindDef pairs (bantha, jerba, 8 ex-Jurassic-Rimworld dinosaurs), their egg/wool/milk/leather/meat/horn items, one ThoughtDef, and 589 SoundDefs absorbed wholesale from three retired mods so retiring them cost the campaign nothing.

## must be true
- RSW_Bantha (ThingDef+PawnKindDef) exists as a herd/pack animal with CompProperties_Shearable (RSW_WoolBantha) and CompProperties_Milkable (RSW_BlueMilk), and its 5 product ThingDefs (RSW_WoolBantha, RSW_BlueMilk, RSW_Leather_Bantha, RSW_Bantha_Meat, RSW_BanthaHorn) all resolve.
- RSW_Jerba (new content, not a port) exists as a pack/milk animal reusing the bantha's unwooled sprite (swanimals/Bantha/Bantha) at a smaller drawSize, banded for desert biomes (Desert/ExtremeDesert/AridShrubland in wildBiomes).
- The 8 absorbed ex-Jurassic creatures (RSW_Baseopsis, RSW_Diplocaulus, RSW_Holcorobeus, RSW_Platyhystrix, RSW_Protosolpuga, RSW_Protovermes, RSW_Segnosaurus, RSW_Termitotron) all resolve to vanilla ParentName="AnimalThingBase" with no donor-only comp classes (ExtraButcheringProducts.CompProperties_SpecialButcherChance was stripped) and no donor-only sounds (Segnosaurus's Carnotaurus sounds were repointed to vanilla Pawn_Thrumbo_*).
- Each of the 8 has its own egg pair in RSW_Absorbed_Eggs.xml (16 ThingDefs total) feeding a working CompProperties_EggLayer breeding loop.
- The 589 absorbed SoundDefs load cleanly and are referenced by defName from the creature lifeStageAges blocks that use them (e.g. RSW_Bantha's soundWounded/soundDeath/soundCall/soundAngry all point at RSW_Pawn_Bantha_* names present in SoundDefs_SWBestiary.xml), so retiring the donor mods did not silently orphan a sound reference.
- RSW_DrankBlueMilk ThoughtDef exists and is wired as RSW_BlueMilk's ingestible/tasteThought.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.swbestiary" and no XML error naming RSW_Bantha.xml, RSW_Jerba.xml, RSW_Absorbed_*.xml or SoundDefs_SWBestiary.xml   # load-time
2. [D] def read-back: ThingDef RSW_Bantha exists; race/body=QuadrupedAnimalWithHoovesAndHorn, race/packAnimal=true, race/leatherDef=RSW_Leather_Bantha, race/specificMeatDef=RSW_Bantha_Meat, comps contains CompProperties_Shearable(woolDef=RSW_WoolBantha) and CompProperties_Milkable(milkDef=RSW_BlueMilk)
3. [D] def read-back: PawnKindDef RSW_Bantha exists; race=RSW_Bantha, combatPower=375, lifeStages[2]/butcherBodyPart/thing=RSW_BanthaHorn
4. [D] def read-back: ThingDef RSW_Jerba exists; race/wildBiomes contains Desert=0.4, ExtremeDesert=0.22, AridShrubland=0.35; statBases/MeatAmount=196; comps contains CompProperties_Milkable(milkDef=Milk)
5. [D] def read-back: each of RSW_Baseopsis, RSW_Diplocaulus, RSW_Holcorobeus, RSW_Platyhystrix, RSW_Protosolpuga, RSW_Protovermes, RSW_Segnosaurus, RSW_Termitotron resolves as a ThingDef (ParentName=AnimalThingBase, no ConfigErrors) and its matching PawnKindDef exists with race pointing back at it
6. [D] def read-back: RSW_BaseopsisEggFertilized and RSW_BaseopsisEggUnFertilized exist (ParentName=EggFertBase/EggUnfertBase); RSW_Baseopsis's CompProperties_EggLayer/eggFertilizedDef=RSW_BaseopsisEggFertilized, eggUnfertilizedDef=RSW_BaseopsisEggUnFertilized — repeat the defName-pair check for the other 7 species by pattern
7. [D] def read-back: SoundDef RSW_Pawn_Bantha_Angry exists; subSounds[0]/grains[0]/clipPath=SWanimals/Pawn_Bantha_Angry — confirms the absorbed sound library actually resolves clips, not just defNames
8. [D] def read-back: ThoughtDef RSW_DrankBlueMilk exists; stages[0]/baseMoodEffect=3; ThingDef RSW_BlueMilk's ingestible/tasteThought=RSW_DrankBlueMilk
9. [B] jawa/spawn_pawn {kindDef: "RSW_Bantha", faction: "none"} → returns success, one bantha pawn spawned
10. [B] jawa/spawn_pawn {kindDef: "RSW_Jerba", faction: "none"} → returns success, one jerba pawn spawned
11. [B] jawa/spawn_pawn {kindDef: "RSW_Baseopsis", faction: "none"} → returns success, one Baseopsis pawn spawned (spot-checks the absorbed-dinosaur wave loads and generates, not just parses)
12. [B] jawa/list_pawns {} on the quicktest map after steps 9-11 → 3 pawns present, races RSW_Bantha/RSW_Jerba/RSW_Baseopsis
X. [S] (human pass) the 589-clip SoundDefs library and the extracted-AssetBundle dinosaur sprites — audio timbre/mix and whether the recovered art still reads clean at game scale are both a listen/look, not a script

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**The absorbed beasts on the map**
- [ ] `bestiary_beasts_render_whole` — each absorbed creature (`RSW_Bantha`,
      `RSW_Jerba`, the eight ex-Jurassic animals such as `RSW_Segnosaurus` and
      `RSW_Termitotron`) is drawn as a whole animal at play zoom, at every life stage.
- [ ] `bestiary_beasts_hold_across_facings` — each beast reads as the same animal
      walking north, east and south, with no facing swapping to a different
      creature or vanishing.
- [ ] `bestiary_jerba_smaller_than_bantha` — a jerba beside a bantha is plainly the
      smaller animal (it reuses the bantha's unwooled sprite at a smaller drawSize).

**Products**
- [ ] `bestiary_blue_milk_reads_blue` — `RSW_BlueMilk` in a stockpile reads as blue
      milk, distinct from vanilla milk at a glance. (guess)
- [ ] `bestiary_eggs_read_as_eggs` — the absorbed creatures' eggs read as eggs in a
      stockpile, not as generic chunks or a magenta square. (guess)

### cannot show

- [ ] `bestiary_never_magenta` — a magenta or missing-texture square where one of
      these beasts or its products should be.
- [ ] `bestiary_jerba_reads_as_shrunk_bantha` — the jerba reading as nothing but a
      scaled-down bantha rather than its own animal. (guess: the reused sprite may
      be accepted as-is; his call)
