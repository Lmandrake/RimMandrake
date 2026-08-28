# machinewreck — mangled metal, dead machinery, crash debris

**Condition palette, material-agnostic.** What you scatter to say *something broke
here and nobody came back*. Slag and chunks for the small litter, dead machines for
the silhouettes, and the ground treatments that stop wreckage sitting on clean soil.

⚠️ **These are CANDIDATES, not a curated set.** Every def below is present in the
current build and checked, and every one has now been *looked at* —
`Palettes/machinewreck_contact.png`, 33 of 33 real sprites, no missing textures.
See "What the sheet showed" below. The taste calls are still the owner's; only the
broken art has been acted on.

## How a wreck palette differs from a floor palette

A floor palette is a *field* — you cover an area and the ratios do the work. Wreckage
is **punctuation**. Three principles, none of them measured yet, all of them things
we already know from looking at generated ruins:

- **Silhouettes, then litter.** One dead machine anchors a scene; the slag chunks and
  rubble around it are what make the machine look fallen rather than placed. Scatter
  litter *outward* from the big piece, densest at the base.
- **One accident, one cause.** Mixing mech wreckage, crashed shuttle and industrial
  scrap in one heap reads as a junkyard, which is a different palette. Pick a cause.
- **The ground must be disturbed.** Intact machinery on broken asphalt reads wrong,
  and so does wreckage on clean sand. Terrain and things go down together.

## Colour

This palette declares no colours of its own — corroded metal is corroded metal.
Take the ramps from `Palettes/flooring_rusted.md`: `wall_rust` for the saturated
end, `wall_brown_hot` where the wreck should read old rather than freshly burst.

```palette
# ------------------------------------------------------ the ground it sits on
role  ASPHALT_BROKEN   BrokenAsphalt          @mod=Core | cracked roadway
role  ASPHALT_WASTE    WastelandAsphalt       @mod=Advanced Biomes (Continued) | same idea, wasteland variant
role  SUBSTRUCTURE_BAD BrokenSubstructure     @mod=Gravship Crashes | broken gravship substructure - the ship's own floor, failed
role  GARBAGE          SWCPTerrain_junkyardgarbage       @mod=Star Wars KotOR Resources and Materials | trash-covered soil
role  GARBAGE_WET      SWCPTerrain_junkyardgarbage_soggy @mod=Star Wars KotOR Resources and Materials | trash sediment
role  BURNT            VEE_BurntForestSoil    @mod=Vanilla Landmarks Expanded | burnt ground

# ------------------------------------------------------------- small litter
thing SLAG_STEEL       ChunkSlagSteel         @mod=Core | steel slag chunk - the default litter
thing SLAG_MECH        ChunkMechanoidSlag     @mod=Core | mechanoid slag chunk
thing SLAG_SCATTER     AB_SlagRubble          @mod=Alpha Biomes | scattered slag, thinner than a chunk
# 🔴 OFF - not a taste call. All three declare texPath `raw_resources/slag_blank`,
# one shared file, and on the contact sheet it is a blank white shape: placeholder
# art the mod never finished. Three "different materials" that are one blank sprite.
# Re-enable only if that texture is replaced.
# thing SLAG_PLASTEEL    KotORChunk_plasteel    @mod=Star Wars KotOR Resources and Materials | plasteel slag chunk
# thing SLAG_DURASTEEL   KotORChunk_durasteel   @mod=Star Wars KotOR Resources and Materials | durasteel slag chunk
# thing SLAG_BRONZIUM    KotORChunk_bronzium    @mod=Star Wars KotOR Resources and Materials | bronzium slag chunk
thing RUBBLE_BUILDING  Filth_RubbleBuilding   @mod=Core | building rubble (filth layer, sits under things)
thing RUBBLE_ROCK      Filth_RubbleRock       @mod=Core | rock rubble (filth layer)
thing ROCKS_COLLAPSED  CollapsedRocks         @mod=Core | collapsed rocks - blocks movement, reads as a cave-in
thing JUNK_PILE        KOTOR_MineableJunk     @mod=Star Wars KotOR Resources and Materials | piled junk, mineable

# ---------------------------------------------------------- crates and scrap
thing SCRAP_BOX        AncientBox_SteelSlag   @mod=Odyssey | steel scrap box
thing SCRAP_PALLET     AncientPallet_SteelSlag @mod=Odyssey | steel scrap pallet
thing SHELVES_DEAD     AM_DamagedEmptyShelves @mod=Ancient urban ruins | collapsed shelves
thing STORAGE_DEAD     BrokenStorageUnitLGE   @mod=Go Explore! | broken storage container

# --------------------------------------------- the silhouettes: dead machines
thing CONSOLE_DEAD     AncientDestroyedConsole      @mod=Odyssey | ancient destroyed console
thing CONSOLE_DEAD_LG  AncientDestroyedConsoleLarge @mod=Odyssey | the large version
thing TURRET_DEAD      AncientAutocannonTurret      @mod=Odyssey | broken autocannon turret
thing TURRET_DEAD_LG   AncientUraniumSlugTurret     @mod=Odyssey | broken uranium slug turret
thing LAMP_DEAD        AG_AncientLamp               @mod=Alpha Genes | ancient broken lamp
thing ENGINE_DEAD      BrokenGravEngine             @mod=Gravship Crashes | broken grav engine - the centrepiece of a downed ship
thing CEREBREX_DEAD    CerebrexCore_Destroyed       @mod=Odyssey | destroyed cerebrex core

# --------------------------------------------------------- mechanoid failure
# Keep these together or not at all - a ruined mech turret beside industrial
# scrap reads as two unrelated accidents in one place.
thing MECH_RELAY_DEAD     MechRelay_Crashed          @mod=Odyssey | crashed mechanoid relay
thing MECH_TURRET_DEAD    AB_Mech_RuinedTurret_Full  @mod=Alpha Biomes | ruined mech turret
thing MECH_ASSEMBLER_DEAD AB_Mech_RuinedAssembler    @mod=Alpha Biomes | ruined mech assembler
thing MECH_CAPSULE_DEAD   AB_Mech_RuinedCapsule      @mod=Alpha Biomes | ruined mech capsule
thing MECH_MORTAR_DEAD    AB_Mech_RuinedMortar_Full  @mod=Alpha Biomes | ruined mech mortar
thing MECH_SHIELD_DEAD    AB_Mech_RuinedShield       @mod=Alpha Biomes | ruined mech shield

# -------------------------------------------------------------------- rules
rule Wreckage is punctuation, not a field. One big silhouette anchors a scene; the litter around its base is what makes it read as fallen.
rule Pick ONE cause per heap. Mech wreckage plus crashed shuttle plus industrial scrap is a junkyard, which is a different palette.
rule The ground goes down with the things. Intact soil under a wreck reads as placed; broken asphalt or garbage soil reads as an accident.
rule Filth_Rubble* are FILTH - they sit under things and are swept away by colonists. Use them for texture, never as the structure of a scene.
rule Colours come from flooring_rusted. This palette deliberately declares none of its own.

# -------------------------------------------------------------------- used
used Nothing yet. First consumer will be the ruined Gravship Cradle's surroundings.
```

## What the sheet showed

`D:\Luke\dev\Rimworld\Palettes\machinewreck_contact.png` — 33 cells, grouped by
the sections in the block above, captioned with defName and supplying mod.

**Acted on — a fact, not taste.** `KotORChunk_plasteel`, `_durasteel` and `_bronzium`
all declare `texPath: raw_resources/slag_blank`. One file, three defs, and the sprite
is a blank white shape. They are commented out in the block above with the reason
attached, not deleted.

**Flagged for the owner — my read, overrule freely:**

| | |
|---|---|
| `AncientBox_SteelSlag`, `AncientPallet_SteelSlag` | **teal painted crates.** They read as intact containers someone left behind, not as scrap. Wrong colour story for a rusted desert site — they would need restuffing or cutting |
| `CerebrexCore_Destroyed` | pale green, organic, unmistakably **archotech**. That is a different palette; it does not belong in an industrial accident |
| `BrokenAsphalt` vs `WastelandAsphalt` | near-identical grey-brown speckle. Keeping both buys nothing |
| `AB_SlagRubble` | tiny scattered specks; nearly invisible at map zoom. Texture only, never structure |
| `AG_AncientLamp` | dark gourd silhouette that reads organic rather than mechanical |

**Reads well, no action:** the six mechanoid pieces are visually one family — pale
bone-white shells that clearly came off the same machine — which is exactly the
"one cause per heap" rule paying off. `BrokenGravEngine` is the best centrepiece on
the sheet.

## Owed before this is trustworthy

1. A contact sheet of every sprite above, at map zoom, so the ones that do not read
   as wreckage get cut.
2. Ratios. `flooring_rusted` has none either — the Cradle drove its wear from a noise
   field rather than proportions — and wreckage probably wants scatter *rules*
   (density falling off from an anchor) rather than flat percentages.
