# Tree size census (2026-10-18)

Item: `TREE_SIZE_ASK_GIANTS_WANTED`. Proposal: `design/RimMandrake/tree_size_proposal_2026-10-18.md`.

**Method (MEASURED, bench clone, 2026-10-18).** Every `ThingDef` under `src/**/Defs/` whose defName starts `RM_`/`RSW_`/`RUT_`
and that is a plant (own or inherited `<plant>` / `category Plant`), parsed as XML elements, with `ParentName` resolved
through abstract defs in `src/` AND the installed game's `Data/*/Defs` (so `TreeBase`'s `1.5~2.0` is inherited where a def
sets nothing). Patches under `src/**/Patches/` that set `visualSizeRange`/`drawSize` were applied (one hit, on a non-tree).
**Tree** = the ruled test (`design/RimMandrake/tree_burst_design_2026-10-17.md` §2): `visualSizeRange` max ≥ 3.0, not in
the ExplosiveGrowth roster's `<fungi>`, not `RM_Greatbole`. Biomes = `BiomeDef/wildPlants` children plus patch-added
`wildPlants` (`UtinniPatches`). Texture widths read from the PNG headers under each mod's `Textures/` for the def's
`texPath` (file or `Graphic_Random` folder). "Drawn side" = `drawSize.x × visualSizeRange.max` (the engine's quad side,
`RimWorld/Plant.cs` `Print`, decompiled 1.6 via RimSage). The census scripts were session scratch (derived, not committed).

**Result: 340 plant defs of ours; 44 trees** (MEASURED). Size spread of `visualSizeRange` max: min 3.0 · median 4.4 ·
max 10.0. Bins: exactly 3.0: 11 · (3, 5]: 18 · (5, 8]: 10 · > 8: 5. Against the owner's size bins
(`design/Jawa/worldbuilding/flora_commission_template.md:177`, small <1 · medium 1–2.2 (person = 1.5) · large 2.2–5 ·
TITAN 5+): **24 trees are "large", 20 are "TITAN"** (≥ 5.0). For scale, `RM_Greatbole` (excluded) is 12~16.
- **Every one of the 44 is a 1×1 plant** (`size` unset). None opts into HugeThings' ground footprint
  (`RM_HugePlantExtension` is used only by `src/RimMandrake/TheRot/Patches/RotGiants_HugeFootprint.xml`, Rot fungi).
- **Only `RM_VaultRoot` sets `drawSize` (2)**: it draws 10.4 cells wide while the tree test reads it as 5.2.
- Greentide holds 20 of the 44. `RM_SweetlineTree` is in no `wildPlants` list (hand-placed landmark, by design).
- Texture px per drawn cell at full growth: 25 (`RM_VaultRoot`) to 186 (`RM_Ollim`); 11 trees below 64, 26 below 128.

## Our trees (44), largest first

| # | defName | label | mod | biome(s) | visualSizeRange | drawSize | drawn side at full growth (cells) | footprint (`size`) | tex px (widths) | px per cell at full | description size words |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `RSW_Plant_HydenockTree_Wild` | wild hydenock tree | SWBestiary | RM_FeverWood | 5~10 | 1 (default) | 10 | 1,1 (default) | 256,512 | 51 | large |
| 2 | `RM_SweetlineTree` | sweetline tree | LeaningScrub | — (none found) | 7.7~10.0 | 1 (default) | 10 | 1,1 (default) | 1280 | 128 | giant, trunk |
| 3 | `RM_CorriskTree` | wild corrisk tree | FeverWood | RM_FeverWood | 5~10 | 1 (default) | 10 | 1,1 (default) | 512 | 51 | crown, tall, trunk |
| 4 | `RM_Veluthar` | veluthar | Greentide | RM_Greentide | 7.5~10.0 | 1 (default) | 10 | 1,1 (default) | 256 | 26 | canopy, crown, enormous |
| 5 | `RM_Kaddrath` | kaddrath | Greentide | RM_Greentide | 6.5~9.0 | 1 (default) | 9 | 1,1 (default) | 1152 | 128 | crown, taller, trunk |
| 6 | `RSW_Plant_JoganTree_Wild` | wild jogan tree | SWBestiary | RM_FeverWood | 5~8 | 1 (default) | 8 | 1,1 (default) | 512 | 64 | — |
| 7 | `RM_LumbrelTree` | wild lumbrel tree | FeverWood | RM_FeverWood | 5~8 | 1 (default) | 8 | 1,1 (default) | 512 | 64 | broad |
| 8 | `RM_Mourvel` | mourvel | Greentide | RM_Greentide | 6.0~8.0 | 1 (default) | 8 | 1,1 (default) | 1024 | 128 | canopy, low |
| 9 | `RM_Sarnstilt` | sarnstilt | Greentide | RM_Greentide | 5.0~7.0 | 1 (default) | 7 | 1,1 (default) | 896 | 128 | crown, huge, trunk |
| 10 | `RM_Illurin` | illurin | Greentide | RM_Greentide | 4.0~7.0 | 1 (default) | 7 | 1,1 (default) | 256 | 37 | broad, canopy, small |
| 11 | `RM_Brunnock` | brunnock | Greentide | RM_Greentide | 4.0~6.0 | 1 (default) | 6 | 1,1 (default) | 768 | 128 | low, trunk |
| 12 | `RM_Ghemmel` | ghemmel | Greentide | RM_Greentide | 4.0~6.0 | 1 (default) | 6 | 1,1 (default) | 256 | 43 | crown, storey, trunk |
| 13 | `RM_Ollim` | ollim | Stillsand | RM_Stillsand, RUT_ExtremeDesert | 3.5~5.5 | 1 (default) | 5.5 | 1,1 (default) | 1024 | 186 | trunk, vast |
| 14 | `RM_Dulloth` | dulloth | Webwork | RM_Webwork | 4.0~5.2 | 1 (default) | 5.2 | 1,1 (default) | 256 | 49 | broad, canopy |
| 15 | `RM_VaultRoot` | vault-root tree | Wasteland | RM_Wasteland, RUT_Wasteland | 2.4~5.2 | 2 | 10.4 | 1,1 (default) | 256 | 25 | squat, trunk |
| 16 | `RM_Nemmer` | nemmer | Greentide | RM_Greentide | 3.5~5.0 | 1 (default) | 5 | 1,1 (default) | 256 | 51 | crown, large, low, trunk |
| 17 | `RM_Vurmeloth` | vurmeloth | Greentide | RM_Greentide | 3.5~5.0 | 1 (default) | 5 | 1,1 (default) | 640 | 128 | crown, small |
| 18 | `RM_Zhorrel` | zhorrel | Greentide | RM_Greentide | 3.5~5.0 | 1 (default) | 5 | 1,1 (default) | 256 | 51 | crown, low |
| 19 | `RM_Tumbel` | tumbel | Greentide | RM_Greentide | 3.0~5.0 | 1 (default) | 5 | 1,1 (default) | 256,640 | 128 | — |
| 20 | `RM_GiantFibreStalk` | giant fibre stalk | Abyss | RM_Abyss, RUT_Abyss | 2.6~5.0 | 1 (default) | 5 | 1,1 (default) | 512 | 102 | enormous, tall |
| 21 | `RM_Kollavane` | kollavane | Webwork | RM_Webwork | 3.3~4.8 | 1 (default) | 4.8 | 1,1 (default) | 256 | 53 | crown, trunk |
| 22 | `RM_Rockfinger` | rockfinger | WeepingStones | RM_WeepingStones | 2.25~4.8 | 1 (default) | 4.8 | 1,1 (default) | 256 | 53 | high, low, tall |
| 23 | `RM_Mirrelbole` | mirrelbole | Greentide | RM_Greentide | 3.0~4.0 | 1 (default) | 4 | 1,1 (default) | 512 | 128 | trunk |
| 24 | `RM_Quathis` | quathis | Greentide | RM_Greentide | 2.5~4.0 | 1 (default) | 4 | 1,1 (default) | 512 | 128 | — |
| 25 | `RM_Thalquith` | thalquith | Greentide | RM_Greentide | 2.5~4.0 | 1 (default) | 4 | 1,1 (default) | 256,512 | 128 | crown, trunk |
| 26 | `RM_Brakkel` | brakkel | Greentide | RM_Greentide | 2.5~4.0 | 1 (default) | 4 | 1,1 (default) | 512 | 128 | enormous, taller |
| 27 | `RM_Sarquin` | sarquin | Greentide | RM_Greentide | 2.5~4.0 | 1 (default) | 4 | 1,1 (default) | 512 | 128 | — |
| 28 | `RM_Wollick` | wollick | Greentide | RM_Greentide | 2.5~4.0 | 1 (default) | 4 | 1,1 (default) | 512 | 128 | huge, small, taller |
| 29 | `RM_Ollamane` | ollamane | Miasma | RM_Miasma | 2.0~3.6 | 1 (default) | 3.6 | 1,1 (default) | 256 | 71 | vast |
| 30 | `RM_Wickwood` | wickwood tree | Abyss | RM_Abyss | 2.6~3.6 | 1 (default) | 3.6 | 1,1 (default) | 256 | 71 | crown |
| 31 | `RM_Thulvane` | thulvane | FeverWood | RM_FeverWood | 2.6~3.5 | 1 (default) | 3.5 | 1,1 (default) | 256 | 73 | broad, colossal, crown |
| 32 | `RM_Thessamor` | thessamor | Miasma | RM_Miasma | 1.8~3.4 | 1 (default) | 3.4 | 1,1 (default) | 256 | 75 | broad, crown, low, metre, trunk |
| 33 | `RM_Eyebark` | eyebark | Contagion | RM_Contagion | 2.6~3.4 | 1 (default) | 3.4 | 1,1 (default) | 256 | 75 | canopy, trunk |
| 34 | `RM_CrackedThornwood` | twisting thornwood | FloodedCanyon | RM_FloodedCanyon, RUT_CrackedLands | 1.3~3.0 | 1 (default) | 3 | 1,1 (default) | 256 | 85 | large |
| 35 | `RM_Shadespire` | shadespire | LongShade | RM_LongShade | 2.0~3.0 | 1 (default) | 3 | 1,1 (default) | 512 | 171 | metres, small, tall |
| 36 | `RM_HalfmadeTree` | halfmade tree | Contagion | RM_Contagion | 2.3~3.0 | 1 (default) | 3 | 1,1 (default) | 256 | 85 | — |
| 37 | `RM_KneelOllim` | kneel ollim | Stillsand | RM_Stillsand | 1.6~3.0 | 1 (default) | 3 | 1,1 (default) | 256 | 85 | low, small, tall, tower |
| 38 | `RM_TwistingThornwood` | twisting thornwood | Cauldron | RM_Cauldron, RUT_Cauldron | 1.3~3.0 | 1 (default) | 3 | 1,1 (default) | 256 | 85 | trunk |
| 39 | `RM_TreeMartyr` | sarrowan | Cauldron | RM_Cauldron, RUT_Cauldron | 1.3~3.0 | 1 (default) | 3 | 1,1 (default) | 256 | 85 | crown, small, tall, trunk |
| 40 | `RM_KeeningCordax` | keening cordax | Cauldron | RM_Cauldron | 2.0~3.0 | 1 (default) | 3 | 1,1 (default) | 256 | 85 | tall |
| 41 | `RM_Gorbeleth` | gorbeleth | Greentide | RM_Greentide | 2.0~3.0 | 1 (default) | 3 | 1,1 (default) | 384 | 128 | low, trunk |
| 42 | `RM_Phorrik` | phorrik | Greentide | RM_Greentide | 2.0~3.0 | 1 (default) | 3 | 1,1 (default) | 384 | 128 | — |
| 43 | `RM_Maddrick` | maddrick | Greentide | RM_Greentide | 2.0~3.0 | 1 (default) | 3 | 1,1 (default) | 384 | 128 | high |
| 44 | `RM_GlowGlobe` | glow globe | Abyss | RM_Abyss, RUT_Abyss | 0.6~3.0 | 1 (default) | 3 | 1,1 (default) | 256 | 85 | low |

### Description vs size (a selection, quoted from the def `description`)

| defName | visual max | the def says |
|---|---|---|
| `RM_Thulvane` | 3.5 | "A colossal fused column of a tree ... rising past sight so its crown is simply a permanent green ceiling." (cast proposal: "the 16-cell fused tower", `design/Jawa/worldbuilding/biomes/fever_wood_rm_cast_proposal_2026-09-24.md:66`) |
| `RM_Ollamane` | 3.6 | "Three or four vast fan-leaves on separate stalks, rising far above everything around them" |
| `RM_Shadespire` | 3.0 | "a slow, hard, banded column three or four metres tall" |
| `RM_CrackedThornwood` | 3.0 | "A large species of tree" |
| `RM_GiantFibreStalk` | 5.0 | "a column of ridged segments as thick as a man and twice as tall" |
| `RM_Veluthar` | 10.0 | "The dominant canopy tree, and the biggest ordinary fall in the whole Greentide" |
| `RM_SweetlineTree` | 10.0 | "A single ancient giant, centuries old" |
| `RM_Maddrick` | 3.0 | "A ring of inward-curling leaf blades standing shoulder-high" (ruled a tree 2026-10-18) |
| `RM_GlowGlobe` | 3.0 | "A low plant that grows a single round glowing globe the size of a melon" (ruled a tree 2026-10-18) |
| `RM_KeeningCordax` | 3.0 | "A tall alien reed with a hollow, ribbed stalk" (ruled a tree 2026-10-18) |
| `RM_Gorbeleth` | 3.0 | "A low mottled purple-brown barrel of a trunk" |

## Vanilla trees and woody plants (installed 1.6 `Data/*/Defs`, MEASURED; stumps omitted)

Inherited from `TreeBase` (`Data/Core/Defs/ThingDefs_Plants/Plants_Bases.xml`): `visualSizeRange 1.5~2.0`, `size` 1×1,
`passability PassThroughOnly`, `pathCost 42`, `fillPercent 0.25`, `blockWind true`, `altitudeLayer Building`.
Note: vanilla pine, gray pine, witchwood, rat palm and snagroot reach **3.0** and would pass our tree test; oak, maple,
poplar, birch, palm, cecropia, drago, bamboo stop at 2.0. Vanilla tree texture sizes: UNMEASURED (they live in
`resources.assets`, not loose files).

| defName | DLC | visualSizeRange | drawSize | harvestTag |
|---|---|---|---|---|
| `Plant_TreeGrayPine` | Biotech | 1.3~3.0 | 1 (default) | Wood |
| `Plant_Witchwood` | Biotech | 1.3~3.0 | 1 (default) | Wood |
| `Plant_RatPalm` | Biotech | 1.3~3.0 | 1 (default) | Wood |
| `Plant_TreePine` | Core | 1.5~3.0 | 1 (default) | Wood |
| `Plant_TreeSnagroot` | Odyssey | 1.5~3.0 | 1 (default) | Wood |
| `Plant_TreeArchean` | Odyssey | 2~2.5 | 1 (default) | Wood |
| `Plant_TreeAnima` | Royalty | 1.8~2.5 | 1 (default) | Wood |
| `Plant_TreeTeak` | Core | 1.3~2.4 | 1 (default) | Wood |
| `Plant_TreeCypress` | Core | 1.5~2.3 | 1 (default) | Wood |
| `Plant_TreeHarbinger` | Anomaly | 1.5~2.1 | 1 (default) | Wood |
| `Plant_TreePolux` | Biotech | 1.5~2.1 | 1 (default) | Wood |
| `Plant_TreeGauranlen` | Ideology | 1.5~2.1 | 1 (default) | Wood |
| `Plant_TreeCocoa` | Core | 1~2 | 1 (default) | Standard |
| `Plant_Timbershroom` | Core | 1.5~2.0 | 1 (default) | Wood |
| `Plant_SaguaroCactus` | Core | 1.5~2.0 | 1 (default) | Wood |
| `Plant_TreeDrago` | Core | 1.5~2.0 | 1 (default) | Wood |
| `Plant_TreeMaple` | Core | 1.5~2.0 | 1 (default) | Wood |
| `Plant_TreeOak` | Core | 1.5~2.0 | 1 (default) | Wood |
| `Plant_TreePoplar` | Core | 1.5~2.0 | 1 (default) | Wood |
| `Plant_TreeBirch` | Core | 1.5~2.0 | 1 (default) | Wood |
| `Plant_TreeCecropia` | Core | 1.5~2.0 | 1 (default) | Wood |
| `Plant_TreePalm` | Core | 1.5~2.0 | 1 (default) | Wood |
| `Plant_TreeBamboo` | Core | 1.5~2.0 | 1 (default) | Wood |
| `Plant_Willowgill` | Odyssey | 1~2 | 0.8 | None |
| `Plant_TreeCocoa_Wild` | Odyssey | 1~2 | 1 (default) | Standard |
| `Plant_TreeWillow` | Core | 1.1~1.8 | 1 (default) | Wood |
| `Plant_PebbleCactus` | Biotech | 0.8~1.5 | 1 (default) | Wood |
| `Plant_TreeBonsai` | Ideology | 0.3~1.05 | 1 (default) | Wood |
| `Plant_Fibercorn` | Ideology | 0.3~0.65 | 1.5 | Wood |
| `Plant_Fibercorn_Wild` | Odyssey | 0.3~0.65 | 1.5 | Wood |
