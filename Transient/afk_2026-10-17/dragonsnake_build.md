# DRAGONSNAKE_PAIR_BUILD_ONE_PALE_ONE_PROPER — progress (BENCH AFK 2026-10-17)

## Status
defs + roster + validation committed; C# toggle written, waiting on the taozin agent's uncommitted edits to the same settings file/DLL

## Item + rulings
Owner 2026-10-17 split ruling (verbatim in both canon entries): JFO four variants = canon Dragonsnake (dark olive-slate crocodilian QUADRUPED);
the two pale Mandalorian-and-Grogu images = Dragonsnake_albino (pale LIMBLESS serpent). No ruling retires existing art, so none is retired.

## Existing RSW_Dragonsnake (def, art, roster placements)
- Def `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Dragonsnake.xml`; BodyDef `RSW_Dragonsnake` in `Defs/Bodies/RSW_MlieWaveC_Bodies.xml`.
- FINDING: the item's "Watch out" called that BodyDef a quadruped. It is NOT: it is a limbless SnakeBody serpent (tail club, hood, no legs).
- FINDING: the INSTALLED body art `Textures/RimStarWars/SWBestiary/Dragonsnake/Dragonsnake_{east,south,north}.png` is the PALE serpent
  (artpipe `regen_gt_canon_dragonsnake_v1`, owner note 2026-10-08 "follow the middle white canon") — i.e. it already passes the ALBINO Must show,
  and fails the canon Dragonsnake's. The swimming art `swanimals/Dragonsnake/Dragonsnake_Swimming_*` is the tan donor (fails colour).
- Rosters: `RUT_Greentide` BiomeDef inline 0.12 + `WildAnimals_Greentide.xml` patch onto `RM_Greentide` 0.12; race.wildBiomes TropicalSwamp 0.8,
  TemperateSwamp 0.6, TropicalRainforest 0.2, ColdBog 0.2. (SeasWaterline Lane1 rows target the donor `Dragonsnake`, not ours.)

## Albino: where it lives (design call + reasoning)
Rare pale variant in EXACTLY the parent's swamps — no new biome, no eviction, no new home. Reasons: canon gives the pale
film creature no separate habitat (a Nal Hutta swamp dragonsnake the Hutts keep in a pit); the brief prefers same-biome
rare variant; "one biome per animal" is satisfied by following the parent rather than founding a second home.
- Greentide (`RUT_Greentide` + `RM_Greentide`): 0.02 vs parent 0.12 — patch-added in `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml`,
  guarded on `ThingDef[defName="RSW_DragonsnakeAlbino"]` (the def is deploy-held, so the guard keeps rows from naming a missing def).
- race.wildBiomes: parent's vanilla swamp rows at 1/6 (TropicalSwamp 0.13, TemperateSwamp 0.1, TropicalRainforest 0.03, ColdBog 0.03).
- Breeds: lays the dragonsnake's own eggs, which hatch ordinary dragonsnakes (albinism recessive; stays rare).

## Defs built
- `RSW_Dragonsnake` BodyDef rebuilt as the canon quadruped (4 Legs + clawed feet, dorsal spine ridge, long eel tail with spined tip);
  tool "bodily constriction" relabelled "tail lash". Header note in `RSW_Dragonsnake.xml`.
- NEW `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_DragonsnakeAlbino.xml`: BodyDef (limbless, no hood, "vestigial eye pit"s),
  ThingDef (body 5.0, ToxicBite needle fangs, constriction, wildness 0.9), PawnKindDef (combatPower 360; texPaths
  `RimStarWars/SWBestiary/DragonsnakeAlbino/DragonsnakeAlbino[_Swimming]`; dessicated reuses the parent's).
- HELD in `src/DEPLOY_HOLD.txt` until its art is installed.
- Mod Settings: `RSW_BeastMechanicsSettings.albinoDragonsnakeEnabled` + `Source/BeastMechanics/RSW_DragonsnakeAlbinoToggle.cs`
  (startup roster strip, Scarlands precedent) — NOT YET WIRED/BUILT: the taozin AFK agent has the same settings .cs, csproj and DLL
  modified and uncommitted; wiring now would sweep its work into my commit or mine into its build.
- Item prose corrected: its "Watch out" called the donor BodyDef a quadruped; it was a limbless serpent.

## Art queued (artpipe)
List: `Transient/afk_2026-10-17/dragonsnake_art/art_list.json`; 9 jobs filed to `D:\Luke\dev\_artpipe\pending\`, priority 5, item-tagged:
- `dragonsnake_jfo_v1_{east,south,north}` — canon body, JFO concept sheet as canon_reference, target `RimStarWars/SWBestiary/Dragonsnake/Dragonsnake`
- `dragonsnake_jfo_v1_swim_{east,south,north}` — canon swimming, target `swanimals/Dragonsnake/Dragonsnake_Swimming` (replaces the tan donor)
- `dragonsnake_albino_v1_swim_{east,south,north}` — derive_from the finished `regen_gt_canon_dragonsnake_v1_east` (same individual)
- Albino BODY: NOT re-queued. Existing done render `regen_gt_canon_dragonsnake_v1_{east,south,north}` (the pale serpent now installed
  on RSW_Dragonsnake's path) already shows every albino Must show line; install it to `RimStarWars/SWBestiary/DragonsnakeAlbino/DragonsnakeAlbino_*` (owed).
- Nothing retired: the 2026-10-17 ruling deletes canon images, not installed art. The pale art stays on RSW_Dragonsnake until the JFO render is picked.
East/south/north per rimworld-sprite-facings (west mirrors east); north/south derive from the east master.

## Validation / selftests / script row
(pending)

## Owed (deploys, live rows)
(pending)
